"""
optimizer.py — Simulated Annealing with parallel independent restarts.

Algorithm:
  1. Start from a random (or seeded) layout
  2. Propose a swap of two random keys
  3. If delta_score < 0: always accept (improvement)
     If delta_score >= 0: accept with probability exp(-delta/T)
  4. Lower temperature T slowly over time
  5. Track best layout seen across all steps

Parallelism:
  - Each worker runs a full independent SA from a different random seed
  - Workers share no state during optimization (embarrassingly parallel)
  - Best result across all workers is taken at the end / each checkpoint
  - On R5 3600 (6C/12T): run 10-12 workers simultaneously

For weeks-long runs:
  - Checkpoints saved every N steps (configurable)
  - Resume from checkpoint on restart
  - Periodic logging of best score across all workers

Usage:
    python main.py optimize                  # Run optimizer
    python main.py optimize --resume         # Resume from latest checkpoint
    python main.py analyze LAYOUT_STRING     # Analyze a specific layout
"""

import os
import math
import time
import random
import pickle
import signal
import multiprocessing as mp
from datetime import datetime
from typing import List, Tuple, Optional

from config import CHARS, NUM_KEYS, SA, PATHS

N_CHARS = len(CHARS)


def random_layout() -> List[int]:
    """Generate a random layout (permutation of char indices)."""
    layout = list(range(N_CHARS))
    random.shuffle(layout)
    return layout


def qwerty_layout() -> List[int]:
    """Return the QWERTY layout as char indices."""
    # Standard QWERTY positions for our 30 chars
    # Top row: q w e r t y u i o p
    # Home:    a s d f g h j k l ;
    # Bottom:  z x c v b n m , . '  (adjusted)
    qwerty_str = "qwertyuiopasdfghjkl;zxcvbnm,.'"
    char_to_idx = {c: i for i, c in enumerate(CHARS)}
    layout = [0] * NUM_KEYS
    for pos, char in enumerate(qwerty_str):
        if char in char_to_idx:
            layout[pos] = char_to_idx[char]
        else:
            # placeholder for chars not in our set
            layout[pos] = pos % N_CHARS
    return layout


def colemak_dh_layout() -> List[int]:
    """Colemak-DH as a starting point (already much better than QWERTY)."""
    colemak_dh = "qwfpbjluy;arstgmneio'zxcdvkh,./"
    colemak_dh = colemak_dh[:30]
    char_to_idx = {c: i for i, c in enumerate(CHARS)}
    layout = list(range(N_CHARS))
    for pos, char in enumerate(colemak_dh):
        if char in char_to_idx:
            layout[pos] = char_to_idx[char]
    return layout


def layout_to_string(layout: List[int]) -> str:
    """Convert layout list to display string."""
    chars = [CHARS[layout[i]] for i in range(NUM_KEYS)]
    rows = [
        ' '.join(chars[0:5])  + '  |  ' + ' '.join(chars[5:10]),
        ' '.join(chars[10:15]) + '  |  ' + ' '.join(chars[15:20]),
        ' '.join(chars[20:25]) + '  |  ' + ' '.join(chars[25:30]),
    ]
    return '\n'.join(rows)


def layout_to_flat(layout: List[int]) -> str:
    """Return layout as a flat 30-char string for storage."""
    return ''.join(CHARS[layout[i]] for i in range(NUM_KEYS))


def flat_to_layout(s: str) -> List[int]:
    """Inverse of layout_to_flat."""
    char_to_idx = {c: i for i, c in enumerate(CHARS)}
    return [char_to_idx[c] for c in s]


def temperature_schedule(step: int, max_steps: int, T_start: float, T_end: float,
                          mode: str = 'exponential') -> float:
    """Return temperature at given step."""
    t = step / max_steps
    if mode == 'exponential':
        return T_start * (T_end / T_start) ** t
    elif mode == 'linear':
        return T_start + (T_end - T_start) * t
    elif mode == 'cosine':
        return T_end + 0.5 * (T_start - T_end) * (1 + math.cos(math.pi * t))
    return T_start


def _sa_worker(worker_id: int, scorer_data: bytes, seed: int,
               max_steps: int, T_start: float, T_end: float, cooling: str,
               checkpoint_dir: str, checkpoint_every: int,
               result_queue: mp.Queue, stop_event: mp.Event,
               start_layout: Optional[List[int]] = None):
    """
    Single SA worker. Runs in a separate process.
    Sends best layout to result_queue at each checkpoint.
    """
    # Reconstruct scorer in this process
    import pickle as pkl
    scorer = pkl.loads(scorer_data)
    
    rng = random.Random(seed)
    
    # Initialize layout
    if start_layout is not None:
        layout = list(start_layout)
    else:
        layout = random_layout()
        rng.shuffle(layout)
    
    # Compute initial score
    current_score = scorer.full_score(layout)
    best_layout = list(layout)
    best_score = current_score
    
    char_indices = list(range(N_CHARS))
    accepts = 0
    rejects = 0
    improvements = 0
    
    checkpoint_path = os.path.join(checkpoint_dir, f'worker_{worker_id}.pkl')
    
    # Load existing checkpoint if present
    if os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, 'rb') as f:
                ckpt = pkl.load(f)
            layout = ckpt['layout']
            best_layout = ckpt['best_layout']
            best_score = ckpt['best_score']
            current_score = ckpt['current_score']
            start_step = ckpt['step']
            print(f"[Worker {worker_id}] Resumed from checkpoint at step {start_step}, best_score={best_score:.6f}")
        except Exception as e:
            print(f"[Worker {worker_id}] Could not load checkpoint: {e}, starting fresh")
            start_step = 0
    else:
        start_step = 0
    
    t0 = time.time()
    
    for step in range(start_step, max_steps):
        if stop_event.is_set():
            break
        
        T = temperature_schedule(step, max_steps, T_start, T_end, cooling)
        
        # Pick two random distinct positions to swap
        pos_a = rng.randint(0, NUM_KEYS - 1)
        pos_b = rng.randint(0, NUM_KEYS - 1)
        while pos_b == pos_a:
            pos_b = rng.randint(0, NUM_KEYS - 1)
        
        # Compute delta score (fast, O(bigrams for these two chars))
        delta = scorer.delta_score(layout, pos_a, pos_b)
        
        # Accept/reject
        if delta < 0:
            # Always accept improvements
            layout[pos_a], layout[pos_b] = layout[pos_b], layout[pos_a]
            current_score += delta
            improvements += 1
            if current_score < best_score:
                best_score = current_score
                best_layout = list(layout)
        elif T > 0 and rng.random() < math.exp(-delta / T):
            # Accept worse with Boltzmann probability
            layout[pos_a], layout[pos_b] = layout[pos_b], layout[pos_a]
            current_score += delta
            accepts += 1
        else:
            rejects += 1
        
        # Checkpoint
        if step % checkpoint_every == 0 and step > start_step:
            elapsed = time.time() - t0
            steps_per_sec = (step - start_step) / max(elapsed, 1)
            eta_hours = (max_steps - step) / max(steps_per_sec, 1) / 3600
            
            print(f"[Worker {worker_id}] Step {step:,}/{max_steps:,} | "
                  f"Best: {best_score:.6f} | T={T:.6f} | "
                  f"{steps_per_sec/1000:.0f}k steps/s | ETA: {eta_hours:.1f}h | "
                  f"Impr: {improvements:,} Accept: {accepts:,}")
            
            # Save checkpoint
            os.makedirs(checkpoint_dir, exist_ok=True)
            ckpt = {
                'layout': layout,
                'best_layout': best_layout,
                'best_score': best_score,
                'current_score': current_score,
                'step': step,
                'timestamp': datetime.now().isoformat(),
            }
            with open(checkpoint_path, 'wb') as f:
                pkl.dump(ckpt, f)
            
            # Send best to main process
            result_queue.put((worker_id, best_score, list(best_layout), step))
            
            accepts = rejects = improvements = 0  # reset counters
    
    # Final result
    # Recompute full score for accuracy (delta accumulation has floating point drift)
    final_score = scorer.full_score(best_layout)
    result_queue.put((worker_id, final_score, best_layout, max_steps))
    print(f"[Worker {worker_id}] DONE. Final best score: {final_score:.6f}")
    print(f"[Worker {worker_id}] Best layout:\n{layout_to_string(best_layout)}")


def optimize(scorer, resume: bool = False, workers: int = None, steps: int = None, cooling_str: str = None) -> Tuple[float, List[int]]:
    """
    Run parallel SA optimization.
    
    Args:
        scorer: Scorer instance
        resume:  If True, load existing checkpoints and continue
        workers: Override config n_workers
        steps: Override config steps_per_run
        cooling_str: Override config cooling schedule
    
    Returns:
        (best_score, best_layout) across all workers
    """
    n_workers   = workers if workers is not None else SA['n_workers']
    max_steps   = steps if steps is not None else SA['steps_per_run']
    T_start     = SA['T_start']
    T_end       = SA['T_end']
    cooling     = cooling_str if cooling_str is not None else SA['cooling']
    ckpt_every  = SA['checkpoint_every']
    ckpt_dir    = PATHS['checkpoint']
    results_dir = PATHS['results']
    
    os.makedirs(ckpt_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Starting optimization: {n_workers} workers × {max_steps:,} steps")
    print(f"Temperature: {T_start} → {T_end} ({cooling})")
    print(f"Estimated time: depends on hardware; R5 3600 ~24h per 50M steps")
    print(f"{'='*60}\n")
    
    # Serialize scorer for pickling to worker processes
    import pickle as pkl
    scorer_data = pkl.dumps(scorer)
    
    # Shared state
    result_queue = mp.Queue()
    stop_event   = mp.Event()
    
    # Different starting points for diversity
    start_layouts = [None] * n_workers
    start_layouts[0] = qwerty_layout()       # One starts from QWERTY
    start_layouts[1] = colemak_dh_layout()   # One from Colemak-DH
    # Rest start random
    
    workers = []
    for wid in range(n_workers):
        seed = 42 + wid * 1337
        p = mp.Process(
            target=_sa_worker,
            args=(wid, scorer_data, seed, max_steps, T_start, T_end, cooling,
                  ckpt_dir, ckpt_every, result_queue, stop_event, start_layouts[wid]),
            daemon=True
        )
        p.start()
        workers.append(p)
    
    # Handle Ctrl+C gracefully
    global_best_score = float('inf')
    global_best_layout = None
    
    def handle_sigterm(sig, frame):
        print("\n[Main] Terminate/Interrupt received. Stopping workers gracefully...")
        stop_event.set()
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)
    
    # Collect results as they come in
    finished = 0
    try:
        while finished < n_workers and not stop_event.is_set():
            try:
                wid, score, layout, step = result_queue.get(timeout=5.0)
                if score < global_best_score:
                    global_best_score = score
                    global_best_layout = list(layout)
                    print(f"\n★ NEW GLOBAL BEST from worker {wid}: {score:.6f}")
                    print(layout_to_string(layout))
                    print(f"  Flat: {layout_to_flat(layout)}\n")
                    
                    # Save global best
                    best_path = os.path.join(results_dir, 'best_layout.pkl')
                    with open(best_path, 'wb') as f:
                        pkl.dump({
                            'layout': layout,
                            'score': score,
                            'flat': layout_to_flat(layout),
                            'timestamp': datetime.now().isoformat(),
                        }, f)
                
                if step >= max_steps:
                    finished += 1
            except Exception:
                # Queue timeout — just check if workers are still alive
                alive = sum(1 for p in workers if p.is_alive())
                if alive == 0:
                    break
    except KeyboardInterrupt:
        stop_event.set()
    
    # Wait for workers
    for p in workers:
        p.join(timeout=30)
        if p.is_alive():
            p.terminate()
    
    return global_best_score, global_best_layout
