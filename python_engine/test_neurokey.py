"""
test_neurokey.py — Comprehensive test suite for NeuroKey.

Run with:
    pytest test_neurokey.py -v
"""

import os
import sys
import pytest
import collections

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import CHARS, NUM_KEYS, EFFORT, FINGER, HAND, COL, WEIGHTS, SA, PATHS
from src.scorer import Scorer, CHAR_TO_IDX, N_CHARS
from src.optimizer import (
    random_layout, qwerty_layout, colemak_dh_layout,
    layout_to_string, layout_to_flat, flat_to_layout,
    temperature_schedule
)
from src.analyze import get_layout, KNOWN_LAYOUTS


# ──────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────

@pytest.fixture
def fake_scorer():
    """Build a scorer from a small synthetic corpus for fast testing."""
    uni = {c: 1.0 / 26.0 for c in 'abcdefghijklmnopqrstuvwxyz'}
    bi = {}
    tri = {}
    for c1 in 'etaoins':
        for c2 in 'etaoins':
            bi[c1 + c2] = 0.01
            for c3 in 'etao':
                tri[c1 + c2 + c3] = 0.001
    return Scorer(uni, bi, tri)


@pytest.fixture
def real_scorer():
    """Build a scorer from real corpus data if available, skip otherwise."""
    cache = PATHS['ngram_cache']
    if not os.path.exists(cache):
        pytest.skip("No corpus cache found — run 'bash get_data.sh' first")
    from src.corpus import build_ngrams
    uni, bi, tri = build_ngrams()
    return Scorer(uni, bi, tri)


# ──────────────────────────────────────────────────────────────
# Config Tests
# ──────────────────────────────────────────────────────────────

class TestConfig:
    def test_chars_length(self):
        assert len(CHARS) == 30, f"Expected 30 chars, got {len(CHARS)}"

    def test_effort_length(self):
        assert len(EFFORT) == NUM_KEYS

    def test_finger_length(self):
        assert len(FINGER) == NUM_KEYS

    def test_hand_length(self):
        assert len(HAND) == NUM_KEYS

    def test_col_length(self):
        assert len(COL) == NUM_KEYS

    def test_effort_home_row_easier(self):
        """Home row (positions 10-19) should generally have lower effort than top/bottom."""
        home_avg = sum(EFFORT[10:20]) / 10
        top_avg = sum(EFFORT[0:10]) / 10
        bottom_avg = sum(EFFORT[20:30]) / 10
        assert home_avg < top_avg, "Home row should be easier than top row"
        assert home_avg < bottom_avg, "Home row should be easier than bottom row"

    def test_corpus_weights_sum_to_one(self):
        from src.config import CORPUS_WEIGHTS
        total = sum(CORPUS_WEIGHTS.values())
        assert abs(total - 1.0) < 0.01, f"Corpus weights should sum to ~1.0, got {total}"

    def test_sa_params_valid(self):
        assert SA['T_start'] > SA['T_end'] > 0
        assert SA['steps_per_run'] > 0
        assert SA['n_workers'] >= 1


# ──────────────────────────────────────────────────────────────
# Layout Tests
# ──────────────────────────────────────────────────────────────

class TestLayouts:
    def test_random_layout_is_permutation(self):
        layout = random_layout()
        assert sorted(layout) == list(range(N_CHARS))

    def test_qwerty_is_valid_permutation(self):
        layout = qwerty_layout()
        assert sorted(layout) == list(range(N_CHARS))

    def test_colemak_dh_is_valid_permutation(self):
        layout = colemak_dh_layout()
        assert sorted(layout) == list(range(N_CHARS))

    def test_layout_to_flat_roundtrip(self):
        layout = qwerty_layout()
        flat = layout_to_flat(layout)
        assert len(flat) == 30
        reconstructed = flat_to_layout(flat)
        assert reconstructed == layout

    def test_layout_to_string_format(self):
        layout = qwerty_layout()
        s = layout_to_string(layout)
        assert '|' in s
        assert len(s.split('\n')) == 3

    def test_known_layouts_valid(self):
        for name, flat_str in KNOWN_LAYOUTS.items():
            layout = get_layout(name)
            assert sorted(layout) == list(range(N_CHARS)), f"{name} is not a valid permutation"

    def test_get_layout_unknown_raises(self):
        with pytest.raises(ValueError):
            get_layout("nonexistent_layout_xyz")


# ──────────────────────────────────────────────────────────────
# Scorer Tests
# ──────────────────────────────────────────────────────────────

class TestScorer:
    def test_scorer_init(self, fake_scorer):
        assert len(fake_scorer.uni) == N_CHARS
        assert len(fake_scorer.bi) == N_CHARS
        assert len(fake_scorer.bi[0]) == N_CHARS

    def test_full_score_is_positive(self, fake_scorer):
        layout = qwerty_layout()
        score = fake_scorer.full_score(layout)
        assert score > 0, "Score should be positive for any real layout"

    def test_full_score_deterministic(self, fake_scorer):
        layout = qwerty_layout()
        s1 = fake_scorer.full_score(layout)
        s2 = fake_scorer.full_score(layout)
        assert s1 == s2, "Same layout should always produce same score"

    def test_different_layouts_different_scores(self, fake_scorer):
        q = qwerty_layout()
        c = colemak_dh_layout()
        sq = fake_scorer.full_score(q)
        sc = fake_scorer.full_score(c)
        assert sq != sc, "QWERTY and Colemak-DH should have different scores"

    def test_delta_score_matches_full(self, fake_scorer):
        """Delta scoring should match the difference between two full scores."""
        layout = qwerty_layout()
        full_before = fake_scorer.full_score(layout)
        delta = fake_scorer.delta_score(layout, 0, 1)
        
        # Actually swap
        layout[0], layout[1] = layout[1], layout[0]
        full_after = fake_scorer.full_score(layout)
        actual_delta = full_after - full_before
        
        # Delta scoring doesn't include hand_imbalance/finger_overload,
        # so allow a small margin
        assert abs(delta - actual_delta) < 0.1, \
            f"Delta mismatch: predicted={delta:.6f}, actual={actual_delta:.6f}"

    def test_breakdown_returns_all_metrics(self, fake_scorer):
        layout = qwerty_layout()
        metrics = fake_scorer.breakdown(layout)
        expected_keys = ['effort', 'sfb', 'sfs', 'inward_roll', 'outward_roll',
                        'lsb', 'redirect', 'hand_balance', 'finger_usage']
        for key in expected_keys:
            assert key in metrics, f"Missing metric: {key}"

    def test_pos_of_all_inverse(self, fake_scorer):
        layout = qwerty_layout()
        pos = fake_scorer.pos_of_all(layout)
        for p, char_idx in enumerate(layout):
            assert pos[char_idx] == p


# ──────────────────────────────────────────────────────────────
# Temperature Schedule Tests
# ──────────────────────────────────────────────────────────────

class TestTemperatureSchedule:
    def test_exponential_start(self):
        T = temperature_schedule(0, 1000, 2.0, 0.001, 'exponential')
        assert abs(T - 2.0) < 0.001

    def test_exponential_end(self):
        T = temperature_schedule(1000, 1000, 2.0, 0.001, 'exponential')
        assert abs(T - 0.001) < 0.001

    def test_linear_monotonic(self):
        temps = [temperature_schedule(s, 100, 2.0, 0.001, 'linear') for s in range(101)]
        for i in range(len(temps) - 1):
            assert temps[i] >= temps[i + 1], "Linear schedule should be monotonically decreasing"

    def test_cosine_monotonic(self):
        temps = [temperature_schedule(s, 100, 2.0, 0.001, 'cosine') for s in range(101)]
        # Cosine is not strictly monotonic but should start high and end low
        assert temps[0] > temps[-1]


# ──────────────────────────────────────────────────────────────
# Ergonomic Predicate Tests
# ──────────────────────────────────────────────────────────────

class TestErgonomics:
    def test_same_finger_self(self):
        """Position should be same-finger with itself."""
        assert Scorer.same_finger(0, 0)

    def test_same_finger_same_column(self):
        """Positions in the same column (same finger) across rows."""
        # Position 0 (top-left) and 10 (home-left) are both left pinky
        assert Scorer.same_finger(0, 10)
        assert Scorer.same_finger(0, 20)

    def test_different_finger(self):
        assert not Scorer.same_finger(0, 1)

    def test_same_hand_left(self):
        assert Scorer.same_hand(0, 1)
        assert Scorer.same_hand(0, 10)

    def test_different_hand(self):
        assert not Scorer.same_hand(0, 5)

    def test_inward_roll_left(self):
        """Left hand: inward = increasing column (toward index)."""
        assert Scorer.is_inward_roll(0, 1)  # pinky to ring
        assert not Scorer.is_inward_roll(1, 0)  # ring to pinky = outward

    def test_inward_roll_right(self):
        """Right hand: inward = decreasing column (toward index)."""
        assert Scorer.is_inward_roll(9, 8)  # pinky to ring
        assert not Scorer.is_inward_roll(8, 9)  # ring to pinky = outward

    def test_inward_roll_cross_hand(self):
        """Cross-hand should never be a roll."""
        assert not Scorer.is_inward_roll(0, 9)


# ──────────────────────────────────────────────────────────────
# Logger Tests
# ──────────────────────────────────────────────────────────────

class TestLogger:
    def test_log_performance_creates_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr('src.logger.PERF_LOG_PATH', str(tmp_path / 'perf.json'))
        from src.logger import log_performance
        log_performance('cpu', 50000.0, 1.234)
        assert (tmp_path / 'perf.json').exists()

    def test_log_performance_updates(self, tmp_path, monkeypatch):
        import json
        monkeypatch.setattr('src.logger.PERF_LOG_PATH', str(tmp_path / 'perf.json'))
        from src.logger import log_performance
        log_performance('cpu', 50000.0, 1.234)
        log_performance('gpu', 200000.0, 1.100)
        
        with open(tmp_path / 'perf.json') as f:
            data = json.load(f)
        assert data['cpu_evals_per_sec'] == 50000.0
        assert data['gpu_evals_per_sec'] == 200000.0
        assert len(data['history']) == 2


# ──────────────────────────────────────────────────────────────
# Integration: Real corpus tests (skipped if no data)
# ──────────────────────────────────────────────────────────────

class TestIntegration:
    def test_qwerty_worse_than_colemak(self, real_scorer):
        """On real programming data, Colemak-DH should beat QWERTY."""
        q = get_layout('qwerty')
        c = get_layout('colemak-dh')
        sq = real_scorer.full_score(q)
        sc = real_scorer.full_score(c)
        assert sc < sq, f"Colemak-DH ({sc:.4f}) should beat QWERTY ({sq:.4f})"

    def test_all_known_layouts_score(self, real_scorer):
        """All known layouts should produce finite scores."""
        for name in KNOWN_LAYOUTS:
            layout = get_layout(name)
            score = real_scorer.full_score(layout)
            assert score > 0 and score < 100, f"{name} score out of range: {score}"
