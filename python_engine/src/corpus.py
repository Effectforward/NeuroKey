"""
corpus.py — Load source files and build n-gram frequency tables.

Handles:
  - Raw source code files (any language)
  - Synthetic vim/helix normal-mode motion sequences
  - Weighted merging of multiple corpora
  - Caching to disk so you only process once

Usage:
    from corpus import build_ngrams
    unigrams, bigrams, trigrams = build_ngrams()
"""

import os
import re
import math
import pickle
import collections
from pathlib import Path
from typing import Dict, Tuple

from src.config import CHARS, CORPUS_WEIGHTS, PATHS

CHAR_SET = set(CHARS)


def _normalize(text: str) -> str:
    """Lowercase, strip control chars, keep only chars in our set."""
    text = text.lower()
    # Replace common code constructs with their char-level representation
    # Keep only characters in our optimization set + spaces (space is structural)
    return ''.join(c for c in text if c in CHAR_SET or c == ' ')


def _count_ngrams(text: str, n: int) -> collections.Counter:
    """Count n-grams, skipping spaces (spaces don't count as chars to type)."""
    # Split by spaces — only count n-grams within words/tokens
    counter = collections.Counter()
    # Use a sliding window that doesn't cross spaces
    tokens = text.split()
    for token in tokens:
        for i in range(len(token) - n + 1):
            gram = token[i:i+n]
            if all(c in CHAR_SET for c in gram):
                counter[gram] += 1
    return counter


def _load_directory(directory: str, weight: float, max_bytes: int = 500_000_000) -> Tuple:
    """Load all text files from a directory, return weighted n-gram counts."""
    uni = collections.Counter()
    bi  = collections.Counter()
    tri = collections.Counter()
    
    path = Path(directory)
    if not path.exists():
        print(f"  [warn] Directory not found: {directory}, skipping.")
        return uni, bi, tri
    
    total_bytes = 0
    file_count = 0
    
    for fpath in path.rglob('*'):
        if not fpath.is_file():
            continue
        if total_bytes >= max_bytes:
            break
        try:
            raw = fpath.read_bytes()
            total_bytes += len(raw)
            text = raw.decode('utf-8', errors='ignore')
            text = _normalize(text)
            uni.update(list(text.replace(' ', '')))
            bi.update(_count_ngrams(text, 2))
            tri.update(_count_ngrams(text, 3))
            file_count += 1
        except Exception:
            continue
    
    print(f"  Loaded {file_count} files ({total_bytes/1e6:.1f} MB) from {directory}")
    
    # Apply weight
    uni_w = {k: v * weight for k, v in uni.items() if k in CHAR_SET}
    bi_w  = {k: v * weight for k, v in bi.items()  if all(c in CHAR_SET for c in k)}
    tri_w = {k: v * weight for k, v in tri.items() if all(c in CHAR_SET for c in k)}
    
    return uni_w, bi_w, tri_w





def _merge(*freq_dicts) -> Dict:
    """Merge multiple frequency dicts by summing values."""
    merged = collections.defaultdict(float)
    for d in freq_dicts:
        for k, v in d.items():
            merged[k] += v
    return dict(merged)


def _normalize_frequencies(freq: Dict) -> Dict:
    """Normalize so all values sum to 1.0."""
    total = sum(freq.values())
    if total == 0:
        return freq
    return {k: v / total for k, v in freq.items()}


def build_ngrams(force_rebuild: bool = False) -> Tuple[Dict, Dict, Dict]:
    """
    Build unigram, bigram, trigram frequency tables from all corpora.
    Results are cached to disk.
    
    Returns:
        unigrams: Dict[char, float]         — normalized frequencies
        bigrams:  Dict[str (len 2), float]  — normalized frequencies
        trigrams: Dict[str (len 3), float]  — normalized frequencies
    """
    cache_path = PATHS['ngram_cache']
    
    if not force_rebuild and os.path.exists(cache_path):
        print(f"Loading n-gram cache from {cache_path}...")
        with open(cache_path, 'rb') as f:
            return pickle.load(f)
    
    print("Building n-gram tables from corpus...")
    
    all_uni, all_bi, all_tri = {}, {}, {}
    
    corpus_dir = PATHS['corpus_dir']
    
    for lang, weight in CORPUS_WEIGHTS.items():
        lang_dir = os.path.join(corpus_dir, lang)
        print(f"  Processing {lang} corpus (weight={weight})...")
        u, b, t = _load_directory(lang_dir, weight)
        
        all_uni = _merge(all_uni, u)
        all_bi  = _merge(all_bi,  b)
        all_tri = _merge(all_tri, t)
    
    # Normalize
    uni = _normalize_frequencies(all_uni)
    bi  = _normalize_frequencies(all_bi)
    tri = _normalize_frequencies(all_tri)
    
    # Filter to only chars in our set
    uni = {k: v for k, v in uni.items() if k in CHAR_SET}
    bi  = {k: v for k, v in bi.items()  if len(k)==2 and all(c in CHAR_SET for c in k)}
    tri = {k: v for k, v in tri.items() if len(k)==3 and all(c in CHAR_SET for c in k)}
    
    # Re-normalize after filtering
    uni = _normalize_frequencies(uni)
    bi  = _normalize_frequencies(bi)
    tri = _normalize_frequencies(tri) if tri else {}
    
    result = (uni, bi, tri)
    
    # Cache to disk
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, 'wb') as f:
        pickle.dump(result, f)
    print(f"Cached n-grams to {cache_path}")
    
    _print_stats(uni, bi, tri)
    return result


def _print_stats(uni, bi, tri):
    print(f"\nCorpus stats:")
    print(f"  Unique unigrams: {len(uni)}")
    print(f"  Unique bigrams:  {len(bi)}")
    print(f"  Unique trigrams: {len(tri)}")
    top_bi = sorted(bi.items(), key=lambda x: -x[1])[:10]
    print(f"  Top 10 bigrams: {top_bi}")
