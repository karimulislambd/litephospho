"""Calibration of LitePhospho at the realistic test prevalence (0.315).

The balanced test negatives are a random subsample of all non-site S/T/Y windows on the test
proteins, so re-weighting them recovers the full-prevalence test set (sanity check: the
re-weighted PR-AUC reproduces the directly measured 0.612). Reports ECE of the raw scores and
after the standard prior-shift correction (Saerens et al., Neural Computation 2002).

Usage (from the repository root):  python analysis/calibration_prevalence.py
"""
from pathlib import Path

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

z = np.load(Path(__file__).resolve().parents[1] / 'results' / 'FINAL_scores.npz')
y = z['y_true'].astype(int)
s = z['LitePhospho'].astype(float)
P, N = y.sum(), (1 - y).sum()
PI_TEST = 87018 / 275929   # prevalence of all S/T/Y residues on the test proteins
PI_TRAIN = 0.497           # positive fraction of the balanced training split
w = np.where(y == 1, 1.0, P * (1 - PI_TEST) / (PI_TEST * N))


def ece(scores, labels, weights, bins=10):
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(scores, edges[1:-1]), 0, bins - 1)
    e, tot = 0.0, weights.sum()
    for b in range(bins):
        m = idx == b
        if m.any():
            e += weights[m].sum() / tot * abs(np.average(scores[m], weights=weights[m]) -
                                              np.average(labels[m], weights=weights[m]))
    return e


def prior_shift(p, pi_from, pi_to):
    r = (pi_to / (1 - pi_to)) / (pi_from / (1 - pi_from))
    return p * r / (p * r + (1 - p))


print(f'balanced   ECE {ece(s, y, np.ones_like(s)):.4f}  PR-AUC {average_precision_score(y, s):.4f}')
print(f'reweighted PR-AUC {average_precision_score(y, s, sample_weight=w):.4f}  '
      f'ROC-AUC {roc_auc_score(y, s, sample_weight=w):.4f}  (prevalence {np.average(y, weights=w):.3f})')
adj = prior_shift(s, PI_TRAIN, PI_TEST)
print(f'at prevalence {PI_TEST:.3f}: raw ECE {ece(s, y, w):.4f} -> prior-shift corrected ECE {ece(adj, y, w):.4f}')
rng = np.random.default_rng(0)
bs = [ece(adj[i], y[i], w[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(1000))]
print(f'corrected ECE 95% CI [{np.percentile(bs, 2.5):.4f}, {np.percentile(bs, 97.5):.4f}]')
