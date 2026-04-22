import os
import time
import torch
import json
import pickle
from datetime import datetime
from typing import Tuple, List

from src.config import CHARS, NUM_KEYS, EFFORT, FINGER, WEIGHTS, HAND, COL
from src.optimizer import layout_to_flat
from src.logger import log_performance

class PytorchGA:
    """
    Vectorized Genetic Algorithm for Keyboard Layout Optimization.
    Operates on a population of layouts as a single (PopulationSize, 30) tensor.
    """
    def __init__(self, scorer, population_size=10000, device='cuda'):
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.pop_size = population_size
        self.n_keys = 30
        
        # 1. Precompute N-gram Tensors
        self.uni = torch.tensor(scorer.uni, dtype=torch.float32, device=self.device)
        self.bi = torch.tensor(scorer.bi, dtype=torch.float32, device=self.device)
        
        # 2. Precompute Position Property Tensors
        self.effort = torch.tensor(EFFORT, dtype=torch.float32, device=self.device)
        self.finger = torch.tensor(FINGER, dtype=torch.long, device=self.device)
        self.hand = torch.tensor(HAND, dtype=torch.long, device=self.device)
        self.col = torch.tensor(COL, dtype=torch.long, device=self.device)
        
        # 3. Precompute Penalty Matrix (QAP Matrix)
        # P[p1][p2] = penalty between position p1 and p2
        self.penalty_matrix = torch.zeros((30, 30), device=self.device)
        for p1 in range(30):
            for p2 in range(30):
                if p1 == p2: continue
                p = 0.0
                # SFB
                if FINGER[p1] == FINGER[p2] and HAND[p1] == HAND[p2]:
                    p += WEIGHTS['sfb']
                # Rolls
                if HAND[p1] == HAND[p2] and FINGER[p1] != FINGER[p2]:
                    # Simple inward roll check for matrix
                    c1, c2 = COL[p1], COL[p2]
                    inward = (c2 > c1) if HAND[p1] == 0 else (c2 < c1)
                    p += WEIGHTS['inward_roll'] if inward else WEIGHTS['outward_roll']
                self.penalty_matrix[p1, p2] = p

    def fitness(self, layouts: torch.Tensor) -> torch.Tensor:
        """
        Compute fitness for a batch of layouts.
        layouts: (Batch, 30)
        """
        batch_size = layouts.shape[0]
        
        # 1. Unigram Effort: Sum(uni[char] * effort[pos])
        # char_at_pos[b, p] = layouts[b, p]
        unigram_scores = torch.sum(self.uni[layouts] * self.effort.unsqueeze(0), dim=1)
        
        # 2. Bigram Score (QAP formulation)
        # Score_b = sum_{p1, p2} Bi[L_b[p1], L_b[p2]] * Penalty[p1, p2]
        # This can be computed by indexing into the Bigram matrix
        
        # Construct batch bigram matrices: Bi_batch[b, p1, p2] = Bi[L_b[p1], L_b[p2]]
        # We use advanced indexing to avoid loops
        p1_idx = torch.arange(30, device=self.device).view(1, 30, 1).expand(batch_size, 30, 30)
        p2_idx = torch.arange(30, device=self.device).view(1, 1, 30).expand(batch_size, 30, 30)
        
        chars_p1 = layouts.gather(1, p1_idx.view(batch_size, -1)).view(batch_size, 30, 30)
        chars_p2 = layouts.gather(1, p2_idx.view(batch_size, -1)).view(batch_size, 30, 30)
        
        # Bigram frequencies for each pair of positions in the layout
        # Using a flattened view for efficient indexing
        batch_bi = self.bi[chars_p1, chars_p2]
        
        bigram_scores = torch.sum(batch_bi * self.penalty_matrix.unsqueeze(0), dim=(1, 2))
        
        return unigram_scores + bigram_scores

    def crossover_pmx(self, p1: torch.Tensor, p2: torch.Tensor) -> torch.Tensor:
        """Partially Mapped Crossover (PMX) - simplified for tensors."""
        # For efficiency on GPU, we use a simple 'swap mutation' approach as crossover
        # but for a true GA we'll do random selection of genes.
        mask = torch.rand(p1.shape, device=self.device) > 0.5
        child = p1.clone()
        child[mask] = p2[mask]
        
        # Fix duplicates (crucial for layout validity)
        # This is the 'repair' step
        for b in range(child.shape[0]):
            unique, counts = torch.unique(child[b], return_counts=True)
            if len(unique) < 30:
                # Find missing and duplicates
                all_chars = torch.arange(30, device=self.device)
                missing = all_chars[~torch.isin(all_chars, unique)]
                # Replace duplicates with missing
                # (A more robust PMX would be better, but this is a fast approximation)
                pass # TODO: Full PMX implementation if needed
        return child

    def mutate(self, layouts: torch.Tensor, rate=0.05) -> torch.Tensor:
        """Randomly swap two keys in a percentage of the population."""
        mask = torch.rand(layouts.shape[0], device=self.device) < rate
        if not mask.any(): return layouts
        
        idx1 = torch.randint(0, 30, (mask.sum(),), device=self.device)
        idx2 = torch.randint(0, 30, (mask.sum(),), device=self.device)
        
        affected = layouts[mask]
        temp = affected[torch.arange(affected.shape[0]), idx1]
        affected[torch.arange(affected.shape[0]), idx1] = affected[torch.arange(affected.shape[0]), idx2]
        affected[torch.arange(affected.shape[0]), idx2] = temp
        layouts[mask] = affected
        return layouts

def optimize_pytorch(scorer, resume: bool = False, workers: int = None, steps: int = None, cooling_str: str = None):
    ga = PytorchGA(scorer, population_size=(workers or 10) * 500)
    
    # Initialize random population
    pop = torch.stack([torch.randperm(30, device=ga.device) for _ in range(ga.pop_size)])
    
    best_score = float('inf')
    best_layout = None
    t0 = time.time()
    
    max_gen = steps or 1000
    print(f"Starting Vectorized GA on {ga.device}...")
    
    for gen in range(max_gen):
        scores = ga.fitness(pop)
        
        # Selection
        val, idx = torch.sort(scores)
        if val[0] < best_score:
            best_score = val[0].item()
            best_layout = pop[idx[0]].cpu().tolist()
            print(f"Gen {gen} | Best: {best_score:.6f} | Flat: {layout_to_flat(best_layout)}")
            
            # Save
            os.makedirs('results', exist_ok=True)
            with open('results/best_layout.pkl', 'wb') as f:
                pickle.dump({'layout': best_layout, 'score': best_score, 'timestamp': datetime.now().isoformat()}, f)
        
        # Keep top 20%
        top_k = int(ga.pop_size * 0.2)
        next_pop = pop[idx[:top_k]].repeat(5, 1)[:ga.pop_size]
        
        # Mutate the rest
        next_pop[top_k:] = ga.mutate(next_pop[top_k:], rate=0.2)
        pop = next_pop
        
        if gen % 10 == 0:
            elapsed = time.time() - t0
            eps = (gen * ga.pop_size) / max(elapsed, 1.0)
            log_performance('gpu', eps, best_score)

    return best_score, best_layout
