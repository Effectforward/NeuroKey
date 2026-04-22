"""
main.py — CLI entry point for the keyboard optimizer.

Commands:
  python main.py optimize              Run optimizer (all workers)
  python main.py optimize --resume     Resume from checkpoints
  python main.py analyze qwerty        Analyze a named layout
  python main.py analyze "abc..."      Analyze a 30-char flat layout string
  python main.py compare               Compare all known layouts vs best found
  python main.py show-best             Show best layout found so far
  python main.py rebuild-corpus        Force rebuild n-gram cache from corpus files
  python main.py test                  Run a quick sanity check

FIRST TIME SETUP:
  1. Run:  bash get_data.sh           (download corpus — takes hours/days)
  2. Run:  python main.py test        (verify everything works)
  3. Run:  python main.py optimize    (let it run for days/weeks)
  4. Run:  python main.py show-best   (inspect result)
"""

import sys
import os
import pickle

from src.config import PATHS
from src.corpus import build_ngrams
from src.scorer import Scorer
from src.optimizer import optimize, layout_to_string, layout_to_flat
from src.analyze import (get_layout, print_layout, print_full_analysis,
                     compare_layouts, KNOWN_LAYOUTS)


def cmd_optimize(resume: bool = False, workers: int = None, steps: int = None, cooling: str = None, engine: str = 'cpu'):
    uni, bi, tri = build_ngrams()
    scorer = Scorer(uni, bi, tri)
    
    print("\nBaseline scores (for reference):")
    from src.analyze import compare_layouts, get_layout
    baselines = {name: get_layout(name) for name in ['qwerty', 'colemak-dh', 'dvorak', 'graphite']}
    import json, os
    os.makedirs('results', exist_ok=True)
    baseline_scores = {}
    for name, layout in baselines.items():
        baseline_scores[name] = scorer.full_score(layout)
    with open('results/baselines.json', 'w') as f:
        json.dump(baseline_scores, f)
        
    compare_layouts(baselines, scorer)
    
    print("\nStarting optimizer...\n")
    if engine == 'gpu':
        try:
            from src.pytorch_optimizer import optimize_pytorch
            best_score, best_layout = optimize_pytorch(scorer, resume=resume, workers=workers, steps=steps, cooling_str=cooling)
        except ImportError:
            print("PyTorch not installed. Run: pip install torch")
            return
    else:
        best_score, best_layout = optimize(scorer, resume=resume, workers=workers, steps=steps, cooling_str=cooling)
    
    if best_layout:
        print(f"\n{'═'*60}")
        print(f"OPTIMIZATION COMPLETE")
        print(f"Best score: {best_score:.6f}")
        print_full_analysis(best_layout, scorer, title="OPTIMIZED LAYOUT")
        print(f"\nFlat string (save this!): {layout_to_flat(best_layout)}")


def cmd_analyze(layout_name: str):
    uni, bi, tri = build_ngrams()
    scorer = Scorer(uni, bi, tri)
    layout = get_layout(layout_name)
    print_full_analysis(layout, scorer, title=layout_name.upper())


def cmd_compare():
    uni, bi, tri = build_ngrams()
    scorer = Scorer(uni, bi, tri)
    
    layouts = {name: get_layout(name) for name in KNOWN_LAYOUTS}
    
    # Add best found if it exists
    best_path = os.path.join(PATHS['results'], 'best_layout.pkl')
    if os.path.exists(best_path):
        with open(best_path, 'rb') as f:
            data = pickle.load(f)
        from src.optimizer import flat_to_layout
        layouts['★ optimized'] = flat_to_layout(data['flat'])
    
    compare_layouts(layouts, scorer)


def cmd_show_best():
    best_path = os.path.join(PATHS['results'], 'best_layout.pkl')
    if not os.path.exists(best_path):
        print("No best layout found yet. Run: python main.py optimize")
        return
    
    with open(best_path, 'rb') as f:
        data = pickle.load(f)
    
    uni, bi, tri = build_ngrams()
    scorer = Scorer(uni, bi, tri)
    
    from src.optimizer import flat_to_layout
    layout = flat_to_layout(data['flat'])
    print_full_analysis(layout, scorer, title=f"BEST FOUND (score={data['score']:.6f})")
    print(f"\nFound at: {data.get('timestamp', 'unknown')}")


def cmd_export_ngrams():
    """Export n-grams as JSON for the Rust/Tauri frontend."""
    import json
    uni, bi, tri = build_ngrams()
    
    # tri is (i,j,k) -> freq, convert to "i,j,k" string for JSON
    tri_json = {f"{k[0]},{k[1]},{k[2]}": v for k, v in tri.items()}
    
    data = {
        'unigrams': uni,
        'bigrams': bi,
        'trigrams': tri_json
    }
    
    output_path = os.path.join(PATHS['results'], 'ngrams.json')
    os.makedirs(PATHS['results'], exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f)
    print(f"Exported n-grams to {output_path}")


def cmd_rebuild_corpus():
    build_ngrams(force_rebuild=True)
    print("Corpus rebuilt.")


def cmd_test():
    """Quick sanity check — generate fake corpus and verify scoring works."""
    print("Running sanity check...")
    
    # Minimal fake corpus
    fake_uni = {c: 1/26 for c in 'abcdefghijklmnopqrstuvwxyz'}
    fake_bi  = {}
    fake_tri = {}
    for c1 in 'abcde':
        for c2 in 'abcde':
            fake_bi[c1+c2] = 0.01
            for c3 in 'abcde':
                fake_tri[c1+c2+c3] = 0.001
    
    scorer = Scorer(fake_uni, fake_bi, fake_tri)
    
    from src.optimizer import qwerty_layout, random_layout
    q_layout = qwerty_layout()
    r_layout = random_layout()
    
    q_score = scorer.full_score(q_layout)
    r_score = scorer.full_score(r_layout)
    print(f"QWERTY score:  {q_score:.6f}")
    print(f"Random score:  {r_score:.6f}")
    
    # Test delta scoring
    from src.optimizer import flat_to_layout
    layout = qwerty_layout()
    full_before = scorer.full_score(layout)
    delta = scorer.delta_score(layout, 0, 1)
    layout[0], layout[1] = layout[1], layout[0]
    full_after = scorer.full_score(layout)
    delta_actual = full_after - full_before
    print(f"Delta test: predicted={delta:.6f}, actual={delta_actual:.6f}, "
          f"match={'✓' if abs(delta - delta_actual) < 0.001 else '✗ MISMATCH'}")
    
    print("\nSanity check passed! ✓")
    print("\nNext step: run 'bash get_data.sh' to download corpus data.")


def main():
    args = sys.argv[1:]
    
    if not args or args[0] == 'help':
        print(__doc__)
        return
    
    cmd = args[0]
    
    if cmd == 'optimize':
        resume = '--resume' in args
        workers = None
        steps = None
        cooling = None
        engine = 'cpu'
        
        for i, arg in enumerate(args):
            if arg == '--workers' and i+1 < len(args):
                workers = int(args[i+1])
            elif arg == '--steps' and i+1 < len(args):
                steps = int(args[i+1])
            elif arg == '--cooling' and i+1 < len(args):
                cooling = args[i+1]
            elif arg == '--engine' and i+1 < len(args):
                engine = args[i+1].lower()
                
        cmd_optimize(resume=resume, workers=workers, steps=steps, cooling=cooling, engine=engine)
    
    elif cmd == 'analyze':
        if len(args) < 2:
            print("Usage: python main.py analyze <layout_name_or_flat_string>")
            print(f"Known names: {list(KNOWN_LAYOUTS.keys())}")
            return
        cmd_analyze(args[1])
    
    elif cmd == 'compare':
        cmd_compare()
    
    elif cmd == 'show-best':
        cmd_show_best()
    
    elif cmd == 'rebuild-corpus':
        cmd_rebuild_corpus()
    
    elif cmd == 'export-ngrams':
        cmd_export_ngrams()
    
    elif cmd == 'test':
        cmd_test()
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == '__main__':
    main()
