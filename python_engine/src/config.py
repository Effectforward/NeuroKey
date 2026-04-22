"""
config.py — All tunable parameters for the keyboard optimizer.

TUNING GUIDE:
  - SFB weight is the most impactful; keep it high (8-15)
  - Increase VIM_PENALTY if you use Neovim/Helix heavily
  - INWARD_ROLL_BONUS is negative (reward), increase magnitude for more rolliness
  - Run the optimizer, feel the result, adjust weights, repeat
"""

# ─────────────────────────────────────────────────────────────
# CHARACTER SET — 30 keys on the alpha zone
# Letters a-z plus 4 critical punctuation marks
# ─────────────────────────────────────────────────────────────
CHARS = list("abcdefghijklmnopqrstuvwxyz.,';")  # 30 characters

# ─────────────────────────────────────────────────────────────
# KEY POSITIONS  (0–29, left→right, top→bottom)
#
#   0  1  2  3  4  |  5  6  7  8  9      ← top row
#  10 11 12 13 14  | 15 16 17 18 19      ← home row
#  20 21 22 23 24  | 25 26 27 28 29      ← bottom row
# ─────────────────────────────────────────────────────────────
NUM_KEYS = 30

# ─────────────────────────────────────────────────────────────
# EFFORT MAP — lower = easier/faster to reach
# Based on empirical finger strength & reach data from ergonomics research
# (Engram paper, Carpalx, community consensus)
# ─────────────────────────────────────────────────────────────
EFFORT = [
    # Top row — harder to reach
    3.0, 2.4, 2.0, 1.8, 2.2,   2.2, 1.8, 2.0, 2.4, 3.0,
    # Home row — easiest
    1.5, 1.1, 1.0, 1.0, 1.3,   1.3, 1.0, 1.0, 1.1, 1.5,
    # Bottom row — hardest (curling fingers down)
    3.5, 2.8, 2.5, 1.9, 3.0,   3.0, 1.9, 2.5, 2.8, 3.5,
]

# ─────────────────────────────────────────────────────────────
# FINGER ASSIGNMENTS
# 0=LP (Left Pinky)  1=LR  2=LM  3=LI
# 4=RI (Right Index) 5=RM  6=RR  7=RP (Right Pinky)
# ─────────────────────────────────────────────────────────────
_FINGER_ROW = [0, 1, 2, 3, 3,   4, 4, 5, 6, 7]
FINGER = _FINGER_ROW * 3  # same pattern for all 3 rows

HAND = [0 if f < 4 else 1 for f in FINGER]  # 0=Left, 1=Right

# Column within-hand (for roll direction calculation)
# Left hand: col 0(LP) 1(LR) 2(LM) 3(LI) 4(LI-inner)   → higher col = closer to center
# Right hand: col 5(RI-inner) 6(RI) 7(RM) 8(RR) 9(RP)  → lower col = closer to center
COL = list(range(10)) * 3  # col 0-9 for each key

# ─────────────────────────────────────────────────────────────
# FINGER STRENGTH WEIGHTS (affects SFB penalty per finger)
# Stronger fingers tolerate SFBs slightly better
# ─────────────────────────────────────────────────────────────
FINGER_STRENGTH = [0.5, 0.7, 1.0, 1.0,   1.0, 1.0, 0.7, 0.5]  # LP…RP

# ─────────────────────────────────────────────────────────────
# MAX ACCEPTABLE FINGER USAGE (fraction of all keypresses)
# Pinky should not exceed ~8%, ring ~15%, middle/index ~30%
# ─────────────────────────────────────────────────────────────
FINGER_USAGE_LIMIT = [0.09, 0.16, 0.22, 0.25,   0.25, 0.22, 0.16, 0.09]

# ─────────────────────────────────────────────────────────────
# SCORING WEIGHTS  (positive = penalty, negative = reward)
# ─────────────────────────────────────────────────────────────
WEIGHTS = {
    # Core ergonomic metrics
    'effort':           1.0,    # Weighted key effort × frequency
    'sfb':             10.0,    # Same-Finger Bigrams — THE most important metric
    'sfs':              3.5,    # Same-Finger Skipgrams (double SFB with key in between)
    'inward_roll':     -3.5,    # REWARD: consecutive keys rolling toward index finger
    'outward_roll':     0.5,    # Small penalty for rolling away from index
    'redirect':         4.0,    # Direction change on same hand in a trigram (disruptive)
    'lsb':              2.5,    # Lateral Stretch Bigrams (index reaching across center)
    'hand_imbalance':   2.0,    # Deviation from 50/50 hand usage
    'finger_overload':  5.0,    # Penalty when finger exceeds usage limit

    # Programming-specific — symbols that appear constantly in code
    'prog_sfb_bonus':   3.0,    # Extra SFB penalty for programming bigrams
}

# ─────────────────────────────────────────────────────────────
# CORPUS WEIGHTS — how much each corpus type contributes
# Balanced for general programming
# ─────────────────────────────────────────────────────────────
CORPUS_WEIGHTS = {
    'python':       0.15,
    'javascript':   0.15,
    'rust':         0.10,
    'cpp':          0.10,
    'go':           0.10,
    'java':         0.10,
    'typescript':   0.10,
    'c':            0.08,
    'ruby':         0.05,
    'shell':        0.02,
    'english':      0.05,   # Comments, docs (Markdown)
}

# ─────────────────────────────────────────────────────────────
# SIMULATED ANNEALING PARAMETERS
# ─────────────────────────────────────────────────────────────
SA = {
    'T_start':      2.0,        # Initial temperature
    'T_end':        0.001,      # Final temperature
    'steps_per_run': 50_000_000, # Steps per parallel worker
    'checkpoint_every': 1_000_000,
    'n_workers':    10,          # Parallel independent restarts
    'cooling':      'exponential',  # 'exponential' or 'linear'
}

# ─────────────────────────────────────────────────────────────
# FILE PATHS
# ─────────────────────────────────────────────────────────────
PATHS = {
    'corpus_dir':   'data/corpus/',
    'ngram_cache':  'data/ngrams_cache.pkl',
    'checkpoint':   'checkpoints/',
    'results':      'results/',
}
