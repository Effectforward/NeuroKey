"""
scorer.py — The fitness function. This is the heart of the optimizer.

Every metric here has been chosen based on:
  - Empirical typing speed research
  - Community consensus (alt-keyboard Discord, keyboard-design.com)
  - The Engram, Graphite, and MTGAP layout analyses

Lower score = better layout.

TWO modes:
  full_score(layout)         — O(all_bigrams), used for analysis/verification
  delta_score(layout, a, b)  — O(bigrams containing a or b), used during SA

Layout representation:
  layout: list[int] of length 30 — layout[i] = index into CHARS for key at position i
  Inverse: pos_of[char_idx] = position
"""

import math
from typing import Dict, List, Tuple
from src.config import (
    CHARS, NUM_KEYS, EFFORT, FINGER, HAND, COL,
    FINGER_STRENGTH, FINGER_USAGE_LIMIT, WEIGHTS
)

# Pre-index for fast lookup
CHAR_TO_IDX = {c: i for i, c in enumerate(CHARS)}
N_CHARS = len(CHARS)
N_FINGERS = 8


class Scorer:
    """
    Precomputes all lookup tables from n-gram data, then scores layouts rapidly.
    
    Usage:
        scorer = Scorer(unigrams, bigrams, trigrams)
        score = scorer.full_score(layout)
        delta = scorer.delta_score(layout, pos_a, pos_b)
    """
    
    def __init__(self, unigrams: Dict, bigrams: Dict, trigrams: Dict):
        """
        Precompute n-gram arrays indexed by char index for O(1) lookup.
        
        unigrams[char] = frequency (float, sums to 1)
        bigrams['ab']  = frequency of char 'a' followed by 'b'
        trigrams['abc']= frequency of trigram abc
        """
        # Unigram array: uni[char_idx] = frequency
        self.uni = [0.0] * N_CHARS
        for c, freq in unigrams.items():
            if c in CHAR_TO_IDX:
                self.uni[CHAR_TO_IDX[c]] = freq
        
        # Bigram matrix: bi[i][j] = freq of char_i followed by char_j
        self.bi = [[0.0] * N_CHARS for _ in range(N_CHARS)]
        for gram, freq in bigrams.items():
            if len(gram) == 2 and gram[0] in CHAR_TO_IDX and gram[1] in CHAR_TO_IDX:
                i, j = CHAR_TO_IDX[gram[0]], CHAR_TO_IDX[gram[1]]
                self.bi[i][j] = freq
        
        # Trigram: tri[i][j][k] stored as flat dict for memory efficiency
        self.tri = {}
        for gram, freq in trigrams.items():
            if len(gram) == 3 and all(c in CHAR_TO_IDX for c in gram):
                key = (CHAR_TO_IDX[gram[0]], CHAR_TO_IDX[gram[1]], CHAR_TO_IDX[gram[2]])
                self.tri[key] = freq
        
        # For delta scoring: precompute which trigrams involve each char
        # tri_by_char[idx] = list of (i,j,k, freq) trigrams involving char idx
        self.tri_by_char = [[] for _ in range(N_CHARS)]
        for (i,j,k), freq in self.tri.items():
            self.tri_by_char[i].append((i,j,k,freq))
            if j != i:
                self.tri_by_char[j].append((i,j,k,freq))
            if k != i and k != j:
                self.tri_by_char[k].append((i,j,k,freq))
        
        self.weights = WEIGHTS
        print(f"Scorer initialized: {sum(v>0 for v in self.uni)} chars, "
              f"{sum(self.bi[i][j]>0 for i in range(N_CHARS) for j in range(N_CHARS))} bigrams, "
              f"{len(self.tri)} trigrams")
    
    # ─────────────────────────────────────────────
    # Layout helpers
    # ─────────────────────────────────────────────
    
    @staticmethod
    def pos_of_all(layout: List[int]) -> List[int]:
        """Return pos_of[char_idx] = position, inverse of layout."""
        pos = [0] * N_CHARS
        for p, c in enumerate(layout):
            pos[c] = p
        return pos
    
    # ─────────────────────────────────────────────
    # Key relationship predicates
    # ─────────────────────────────────────────────
    
    @staticmethod
    def same_finger(p1: int, p2: int) -> bool:
        return FINGER[p1] == FINGER[p2]
    
    @staticmethod
    def same_hand(p1: int, p2: int) -> bool:
        return HAND[p1] == HAND[p2]
    
    @staticmethod
    def is_inward_roll(p1: int, p2: int) -> bool:
        """True if p1→p2 is an inward roll (toward index finger)."""
        if HAND[p1] != HAND[p2]:
            return False
        if FINGER[p1] == FINGER[p2]:
            return False
        c1, c2 = COL[p1], COL[p2]
        hand = HAND[p1]
        if hand == 0:  # Left hand: inward = moving right (increasing col)
            return c2 > c1
        else:           # Right hand: inward = moving left (decreasing col)
            return c2 < c1
    
    @staticmethod
    def is_outward_roll(p1: int, p2: int) -> bool:
        """True if p1→p2 is an outward roll (away from index finger)."""
        if HAND[p1] != HAND[p2]:
            return False
        if FINGER[p1] == FINGER[p2]:
            return False
        return not Scorer.is_inward_roll(p1, p2)
    
    @staticmethod
    def is_redirect(p1: int, p2: int, p3: int) -> bool:
        """True if p1→p2→p3 is a redirect (direction reversal on same hand, no SFB)."""
        if HAND[p1] != HAND[p2] or HAND[p2] != HAND[p3]:
            return False
        if FINGER[p1]==FINGER[p2] or FINGER[p2]==FINGER[p3]:
            return False
        c1, c2, c3 = COL[p1], COL[p2], COL[p3]
        d12 = c2 - c1
        d23 = c3 - c2
        return (d12 > 0 and d23 < 0) or (d12 < 0 and d23 > 0)
    
    @staticmethod
    def is_lsb(p1: int, p2: int) -> bool:
        """
        Lateral Stretch Bigram: index finger crossing into the other index column,
        or index+middle spanning two rows while stretching laterally.
        """
        f1, f2 = FINGER[p1], FINGER[p2]
        # Index reaching into center column (col 4 or 5) while other key is far
        # Also: index+ring/pinky combos that stretch the hand
        if HAND[p1] != HAND[p2]:
            # Cross-center-column index stretch
            if (f1 in (3,4) and abs(COL[p1] - COL[p2]) >= 2 and
                    not (HAND[p1] == 0 and COL[p1] == 4) and
                    not (HAND[p1] == 1 and COL[p1] == 5)):
                return False  # not lsb
        # Same hand: index reaching across to the inner column (col 4 left, col 5 right)
        if HAND[p1] == HAND[p2]:
            hand = HAND[p1]
            if hand == 0 and (COL[p1] == 4 or COL[p2] == 4):
                # Left index inner column combined with a non-adjacent finger
                if abs(f1 - f2) >= 2:
                    return True
            if hand == 1 and (COL[p1] == 5 or COL[p2] == 5):
                if abs(f1 - f2) >= 2:
                    return True
        return False
    
    # ─────────────────────────────────────────────
    # Full scoring
    # ─────────────────────────────────────────────
    
    def full_score(self, layout: List[int]) -> float:
        """
        Score a full layout. Lower is better.
        This is O(N²) in bigrams — use for analysis, not inner SA loop.
        """
        pos = self.pos_of_all(layout)
        w = self.weights
        score = 0.0
        
        # ── 1. Effort (unigrams × position effort) ─────────────────
        effort_score = sum(self.uni[c] * EFFORT[pos[c]] for c in range(N_CHARS))
        score += w['effort'] * effort_score
        
        # ── 2. Bigram metrics ───────────────────────────────────────
        sfb_score = 0.0
        inroll_score = 0.0
        outroll_score = 0.0
        lsb_score = 0.0
        
        for i in range(N_CHARS):
            pi = pos[i]
            for j in range(N_CHARS):
                freq = self.bi[i][j]
                if freq == 0:
                    continue
                pj = pos[j]
                
                if self.same_finger(pi, pj):
                    if i != j:  # actual SFB (not same char twice)
                        sfb_score += freq / FINGER_STRENGTH[FINGER[pi]]
                elif self.same_hand(pi, pj):
                    if self.is_inward_roll(pi, pj):
                        inroll_score += freq
                    elif self.is_outward_roll(pi, pj):
                        outroll_score += freq
                
                if self.is_lsb(pi, pj):
                    lsb_score += freq
        
        score += w['sfb'] * sfb_score
        score += w['inward_roll'] * inroll_score   # negative weight = reward
        score += w['outward_roll'] * outroll_score
        score += w['lsb'] * lsb_score
        
        # ── 3. Trigram metrics ──────────────────────────────────────
        sfs_score = 0.0
        redirect_score = 0.0
        
        for (i,j,k), freq in self.tri.items():
            pi, pj, pk = pos[i], pos[j], pos[k]
            
            # SFS: same finger on positions i and k, with j in between
            if FINGER[pi] == FINGER[pk] and i != k:
                sfs_score += freq / FINGER_STRENGTH[FINGER[pi]]
            
            # Redirect
            if self.is_redirect(pi, pj, pk):
                redirect_score += freq
        
        score += w['sfs'] * sfs_score
        score += w['redirect'] * redirect_score
        
        # ── 4. Hand balance ─────────────────────────────────────────
        left_usage  = sum(self.uni[c] for c in range(N_CHARS) if HAND[pos[c]] == 0)
        right_usage = sum(self.uni[c] for c in range(N_CHARS) if HAND[pos[c]] == 1)
        total = left_usage + right_usage
        if total > 0:
            imbalance = abs(left_usage - right_usage) / total
            score += w['hand_imbalance'] * imbalance
        
        # ── 5. Finger overload ──────────────────────────────────────
        for f in range(N_FINGERS):
            usage = sum(self.uni[c] for c in range(N_CHARS) if FINGER[pos[c]] == f)
            limit = FINGER_USAGE_LIMIT[f]
            if usage > limit:
                score += w['finger_overload'] * (usage - limit)
        
        return score
    
    # ─────────────────────────────────────────────
    # Delta scoring for SA inner loop
    # ─────────────────────────────────────────────
    
    def _char_contribution(self, char_idx: int, pos: List[int]) -> float:
        """
        Score contribution of a single character — all bigrams/trigrams involving it.
        Used in delta scoring: compute old contribution, swap, compute new contribution.
        The difference is the delta score.
        """
        ci = char_idx
        pi = pos[ci]
        w = self.weights
        score = 0.0
        
        # Effort
        score += w['effort'] * self.uni[ci] * EFFORT[pi]
        
        # Bigrams where ci is first char
        for j in range(N_CHARS):
            freq = self.bi[ci][j]
            if freq > 0:
                pj = pos[j]
                if self.same_finger(pi, pj) and ci != j:
                    score += w['sfb'] * freq / FINGER_STRENGTH[FINGER[pi]]
                elif self.same_hand(pi, pj):
                    if self.is_inward_roll(pi, pj):
                        score += w['inward_roll'] * freq
                    elif self.is_outward_roll(pi, pj):
                        score += w['outward_roll'] * freq
                if self.is_lsb(pi, pj):
                    score += w['lsb'] * freq
        
        # Bigrams where ci is second char (reverse direction)
        for j in range(N_CHARS):
            freq = self.bi[j][ci]
            if freq > 0:
                pj = pos[j]
                if self.same_finger(pj, pi) and j != ci:
                    score += w['sfb'] * freq / FINGER_STRENGTH[FINGER[pi]]
                elif self.same_hand(pj, pi):
                    if self.is_inward_roll(pj, pi):
                        score += w['inward_roll'] * freq
                    elif self.is_outward_roll(pj, pi):
                        score += w['outward_roll'] * freq
                if self.is_lsb(pj, pi):
                    score += w['lsb'] * freq
        
        # Trigrams involving ci
        seen = set()
        for (i,j,k,freq) in self.tri_by_char[ci]:
            tkey = (i,j,k)
            if tkey in seen:
                continue
            seen.add(tkey)
            pi2, pj2, pk2 = pos[i], pos[j], pos[k]
            if FINGER[pi2] == FINGER[pk2] and i != k:
                score += w['sfs'] * freq / FINGER_STRENGTH[FINGER[pi2]]
            if self.is_redirect(pi2, pj2, pk2):
                score += w['redirect'] * freq
        
        return score
    
    def delta_score(self, layout: List[int], pos_a: int, pos_b: int) -> float:
        """
        Compute score change from swapping keys at positions pos_a and pos_b.
        Returns new_score - old_score (negative = improvement).
        
        IMPORTANT: Does NOT include hand_imbalance and finger_overload terms
        (these are recomputed cheaply in the SA loop separately).
        """
        pos = self.pos_of_all(layout)
        ca = layout[pos_a]  # char currently at pos_a
        cb = layout[pos_b]  # char currently at pos_b
        
        # Score contribution of both chars before swap
        old_a = self._char_contribution(ca, pos)
        old_b = self._char_contribution(cb, pos)
        # Subtract interaction between ca and cb (counted twice above)
        old_ab = self._interaction(ca, cb, pos)
        
        # Perform the swap
        pos[ca] = pos_b
        pos[cb] = pos_a
        
        # Score after swap
        new_a = self._char_contribution(ca, pos)
        new_b = self._char_contribution(cb, pos)
        new_ab = self._interaction(ca, cb, pos)
        
        # Restore pos
        pos[ca] = pos_a
        pos[cb] = pos_b
        
        return (new_a + new_b - new_ab) - (old_a + old_b - old_ab)
    
    def _interaction(self, ci: int, cj: int, pos: List[int]) -> float:
        """Score of the direct interaction between chars ci and cj (to avoid double-counting)."""
        pi, pj = pos[ci], pos[cj]
        score = 0.0
        w = self.weights
        
        for freq, p1, p2 in [(self.bi[ci][cj], pi, pj), (self.bi[cj][ci], pj, pi)]:
            if freq > 0:
                if self.same_finger(p1, p2):
                    score += w['sfb'] * freq / FINGER_STRENGTH[FINGER[p1]]
                elif self.same_hand(p1, p2):
                    if self.is_inward_roll(p1, p2):
                        score += w['inward_roll'] * freq
                    elif self.is_outward_roll(p1, p2):
                        score += w['outward_roll'] * freq
                if self.is_lsb(p1, p2):
                    score += w['lsb'] * freq
        return score
    
    # ─────────────────────────────────────────────
    # Detailed breakdown for analysis
    # ─────────────────────────────────────────────
    
    def breakdown(self, layout: List[int]) -> Dict:
        """Return per-metric scores for analysis and weight tuning."""
        pos = self.pos_of_all(layout)
        metrics = {}
        
        metrics['effort'] = sum(self.uni[c] * EFFORT[pos[c]] for c in range(N_CHARS))
        
        sfb = sfs = inroll = outroll = lsb = redirect = 0.0
        for i in range(N_CHARS):
            pi = pos[i]
            for j in range(N_CHARS):
                freq = self.bi[i][j]
                if freq == 0: continue
                pj = pos[j]
                if self.same_finger(pi, pj) and i != j:
                    sfb += freq
                elif self.same_hand(pi, pj):
                    if self.is_inward_roll(pi, pj): inroll += freq
                    elif self.is_outward_roll(pi, pj): outroll += freq
                if self.is_lsb(pi, pj): lsb += freq
        
        for (i,j,k), freq in self.tri.items():
            pi, pj, pk = pos[i], pos[j], pos[k]
            if FINGER[pi] == FINGER[pk] and i != k: sfs += freq
            if self.is_redirect(pi, pj, pk): redirect += freq
        
        metrics['sfb']          = sfb
        metrics['sfs']          = sfs
        metrics['inward_roll']  = inroll
        metrics['outward_roll'] = outroll
        metrics['lsb']          = lsb
        metrics['redirect']     = redirect
        
        left_usage  = sum(self.uni[c] for c in range(N_CHARS) if HAND[pos[c]] == 0)
        right_usage = sum(self.uni[c] for c in range(N_CHARS) if HAND[pos[c]] == 1)
        total = left_usage + right_usage
        metrics['hand_balance'] = f"{left_usage/total*100:.1f}L / {right_usage/total*100:.1f}R" if total else "N/A"
        
        finger_usage = [0.0] * N_FINGERS
        for c in range(N_CHARS):
            finger_usage[FINGER[pos[c]]] += self.uni[c]
        metrics['finger_usage'] = {
            ['LP','LR','LM','LI','RI','RM','RR','RP'][f]: f"{v*100:.1f}%"
            for f, v in enumerate(finger_usage)
        }
        
        return metrics
