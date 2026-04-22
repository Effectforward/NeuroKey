"""
analyze.py — Layout analysis and comparison tools.

Usage:
    python main.py analyze qwerty
    python main.py analyze "bdfkxjlouy,nrstgpheai;qzcwmv.'"   # flat string
    python main.py compare qwerty colemak-dh
    python main.py show-best
"""

from typing import List, Dict
from src.config import CHARS, NUM_KEYS, EFFORT, FINGER, HAND, COL
from src.optimizer import (layout_to_string, layout_to_flat, flat_to_layout,
                       qwerty_layout, colemak_dh_layout, random_layout)

N_CHARS = len(CHARS)

KNOWN_LAYOUTS = {
    'qwerty':     "qwertyuiopasdfghjkl;zxcvbnm,.'",
    'dvorak':     "',.pyfgcrlaoeuidhtns;qjkxbmwvz",
    'colemak':    "qwfpgjluy;arstdhneiozxcvbkm,.'",
    'colemak-dh': "qwfpbjluy;arstgmneiozxcdvkh,.'",
    'workman':    "qdrwbjfup;ashtgyneoizxmcvkl,.'",
    'graphite':   "bldwzjfou,nrtsgyhaei;qxmcvkp.'",
}

FINGER_NAMES = ['LP', 'LR', 'LM', 'LI', 'RI', 'RM', 'RR', 'RP']


def get_layout(name_or_flat: str) -> List[int]:
    """Resolve a layout name or flat string to a layout list."""
    char_to_idx = {c: i for i, c in enumerate(CHARS)}
    
    if name_or_flat in KNOWN_LAYOUTS:
        s = KNOWN_LAYOUTS[name_or_flat]
        # Pad or trim to 30 chars
        s = s[:30].ljust(30, CHARS[-1])
        layout = [char_to_idx.get(c, 0) for c in s]
        return layout
    
    if name_or_flat == 'qwerty':
        return qwerty_layout()
    if name_or_flat in ('colemak-dh', 'colemak_dh'):
        return colemak_dh_layout()
    if name_or_flat == 'random':
        return random_layout()
    
    if len(name_or_flat) == 30:
        return flat_to_layout(name_or_flat)
    
    raise ValueError(f"Unknown layout: '{name_or_flat}'. "
                     f"Use a known name {list(KNOWN_LAYOUTS.keys())} "
                     f"or a 30-char flat string.")


def print_layout(layout: List[int], title: str = "Layout"):
    """Pretty-print a layout with finger color hints (ANSI)."""
    COLORS = {
        0: '\033[91m',   # LP — red
        1: '\033[93m',   # LR — yellow
        2: '\033[92m',   # LM — green
        3: '\033[96m',   # LI — cyan
        4: '\033[94m',   # RI — blue
        5: '\033[95m',   # RM — magenta
        6: '\033[33m',   # RR — orange
        7: '\033[37m',   # RP — white
    }
    RESET = '\033[0m'
    HOME_ROW_BOLD = '\033[1m'
    
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print(f"{'─'*50}")
    
    row_labels = ['TOP ', 'HOME', 'BOT ']
    for row in range(3):
        print(f"  {row_labels[row]}  ", end='')
        for col in range(10):
            pos = row * 10 + col
            char = CHARS[layout[pos]]
            finger = FINGER[pos]
            color = COLORS[finger]
            bold = HOME_ROW_BOLD if row == 1 else ''
            print(f"{color}{bold}{char}{RESET}", end=' ')
            if col == 4:
                print(' ', end='')
        print()
    
    print(f"\n  Flat: {layout_to_flat(layout)}")
    print(f"{'─'*50}")


def print_full_analysis(layout: List[int], scorer, title: str = "Analysis"):
    """Print full metric breakdown for a layout."""
    print_layout(layout, title)
    
    metrics = scorer.breakdown(layout)
    total_score = scorer.full_score(layout)
    
    print(f"\n  SCORE: {total_score:.6f}  (lower = better)\n")
    
    print(f"  {'METRIC':<22} {'VALUE':>10}  {'WEIGHTED':>10}")
    print(f"  {'─'*22}  {'─'*10}  {'─'*10}")
    
    w = scorer.weights
    
    def row(name, key, fmt='.4f', negate=False):
        val = metrics.get(key, 0)
        if isinstance(val, str):
            print(f"  {name:<22} {val:>22}")
            return
        weighted = val * w.get(key, 1.0)
        sign = '-' if negate else ''
        print(f"  {name:<22} {val:>10.4f}   {weighted:>+10.4f}")
    
    row('Effort',          'effort')
    row('SFB rate',        'sfb')
    row('SFS rate',        'sfs')
    row('Inward rolls',    'inward_roll')
    row('Outward rolls',   'outward_roll')
    row('Redirects',       'redirect')
    row('Lat. stretches',  'lsb')
    
    print(f"\n  Hand balance: {metrics['hand_balance']}")
    print(f"\n  Finger usage:")
    for finger, usage in metrics['finger_usage'].items():
        bar_len = int(float(usage.replace('%','')) * 1.5)
        bar = '█' * bar_len
        print(f"    {finger}  {bar:<30} {usage}")
    
    print(f"\n  Position effort heatmap:")
    _print_heatmap(layout, scorer)


def _print_heatmap(layout: List[int], scorer):
    """Print a heatmap of key usage (unigram freq × effort contribution)."""
    SHADES = [' ', '░', '▒', '▓', '█']
    
    usage = [scorer.uni[layout[p]] for p in range(NUM_KEYS)]
    max_usage = max(usage) if usage else 1
    
    row_labels = ['TOP ', 'HOME', 'BOT ']
    for row in range(3):
        print(f"    {row_labels[row]}  ", end='')
        for col in range(10):
            pos = row * 10 + col
            level = int(usage[pos] / max_usage * (len(SHADES) - 1))
            shade = SHADES[level]
            char = CHARS[layout[pos]]
            print(f"{char}{shade}", end=' ')
            if col == 4:
                print(' ', end='')
        print()


def compare_layouts(layouts_dict: Dict[str, List[int]], scorer):
    """Compare multiple layouts side by side."""
    print(f"\n{'═'*70}")
    print(f"  LAYOUT COMPARISON")
    print(f"{'═'*70}")
    
    results = []
    for name, layout in layouts_dict.items():
        score = scorer.full_score(layout)
        metrics = scorer.breakdown(layout)
        results.append((name, score, layout, metrics))
    
    # Sort by score
    results.sort(key=lambda x: x[1])
    
    header = f"  {'LAYOUT':<18} {'SCORE':>8} {'SFB':>6} {'SFS':>6} {'INROLL':>7} {'REDIR':>7} {'HAND':>10}"
    print(header)
    print(f"  {'─'*18} {'─'*8} {'─'*6} {'─'*6} {'─'*7} {'─'*7} {'─'*10}")
    
    for name, score, layout, m in results:
        rank = '★ ' if results.index((name, score, layout, m)) == 0 else '  '
        sfb    = m['sfb'] * 100
        sfs    = m['sfs'] * 100
        inroll = m['inward_roll'] * 100
        redir  = m['redirect'] * 100
        hand   = m['hand_balance']
        print(f"{rank}{name:<18} {score:>8.4f} {sfb:>5.2f}% {sfs:>5.2f}% {inroll:>6.2f}% {redir:>6.2f}% {hand:>10}")
    
    print(f"\n  Best: {results[0][0]} (score: {results[0][1]:.4f})")
    print(f"  vs QWERTY improvement: "
          f"{(results[-1][1] - results[0][1]) / results[-1][1] * 100:.1f}%")
