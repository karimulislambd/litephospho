"""Statistics for the follow-up (reviewer-response) experiments.

Pools the two independent executions of notebooks/litephospho_reviewer_experiments.ipynb
(results/reviewer_experiments/run1, run2; three seeds each -> six runs per configuration)
and prints every number reported in the paper's follow-up sections: leakage inflation with
Welch's t-tests, the pooling ablation, the protein-language-model comparison and the
released MusiteDeep 2020 models, including per-residue PR-AUC.

Usage (from the repository root):  python analysis/reviewer_stats.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import average_precision_score as ap

ROOT = Path(__file__).resolve().parents[1] / 'results' / 'reviewer_experiments'
RUNS = [ROOT / 'run1', ROOT / 'run2']
RES = [json.load(open(r / 'results.json')) for r in RUNS]
y = np.load(ROOT / 'y_test_homology.npy').astype(int)
residue = pd.read_csv(ROOT / 'test_windows_homology.csv')['residue'].values


def vals(prefix, metric, runs=(0, 1)):
    return np.array([v[metric] for i in runs for k, v in RES[i].items() if k.startswith(prefix)])


def distinct_runs(prefix):
    """Frozen-encoder entries were carried over unchanged into run2; count them once."""
    a = {k: v['PR_AUC'] for k, v in RES[0].items() if k.startswith(prefix)}
    b = {k: v['PR_AUC'] for k, v in RES[1].items() if k.startswith(prefix)}
    return (0,) if a == b else (0, 1)


def scores(prefix, runs=(0, 1)):
    files = [f for i in runs for f in sorted((RUNS[i] / 'scores').glob(prefix.replace('|', '__') + '*.npy'))]
    return np.mean([np.load(f).astype(np.float32) for f in files], 0)


def boot(a, b, n_boot=1000, seed=0):
    """Paired bootstrap of PR-AUC(a) - PR-AUC(b): mean, 95% CI, one-sided p (a not better)."""
    rng = np.random.default_rng(seed); n = len(y); d = np.empty(n_boot)
    for i in range(n_boot):
        j = rng.integers(0, n, n); d[i] = ap(y[j], a[j]) - ap(y[j], b[j])
    return d.mean(), np.percentile(d, 2.5), np.percentile(d, 97.5), np.mean(d <= 0)


def ms(v):
    return f'{v.mean():.3f} +- {v.std(ddof=1):.3f}' if len(v) > 1 else f'{v[0]:.3f}'


def ci95(v):
    h = stats.t.ppf(0.975, len(v) - 1) * v.std(ddof=1) / np.sqrt(len(v))
    return v.mean() - h, v.mean() + h


print('=== E1: leakage inflation (random - homology ROC-AUC), six runs ===')
infl = {}
for m in ('LitePhospho', 'DeepPhos', 'MusiteDeep'):
    infl[m] = np.array([RES[i][f'E1|{m}|random|seed{s}']['ROC_AUC'] - RES[i][f'E1|{m}|homology|seed{s}']['ROC_AUC']
                        for i in (0, 1) for s in (1, 2, 3)])
    lo, hi = ci95(infl[m])
    print(f'{m:12s} homology ROC {ms(vals(f"E1|{m}|homology", "ROC_AUC"))}  PR {ms(vals(f"E1|{m}|homology", "PR_AUC"))}  '
          f'random ROC {ms(vals(f"E1|{m}|random", "ROC_AUC"))}  inflation {ms(infl[m])} [{lo:.3f}, {hi:.3f}]')
for a, b in (('DeepPhos', 'LitePhospho'), ('MusiteDeep', 'LitePhospho'), ('MusiteDeep', 'DeepPhos')):
    t, p = stats.ttest_ind(infl[a], infl[b], equal_var=False)
    print(f'  Welch {a} - {b}: {infl[a].mean() - infl[b].mean():+.4f}  t={t:.2f}  p={p:.2g}')
lp = scores('E1|LitePhospho|homology|')
for m in ('DeepPhos', 'MusiteDeep'):
    d, lo, hi, p = boot(lp, scores(f'E1|{m}|homology|'))
    print(f'  paired bootstrap LitePhospho - {m}: {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  p={p:.3f}')

print('\n=== E2: pooling ablation (homology split), six runs ===')
print(f'flatten (LitePhospho)  PR {ms(vals("E1|LitePhospho|homology", "PR_AUC"))}  ROC {ms(vals("E1|LitePhospho|homology", "ROC_AUC"))}')
for v in ('gap', 'gmp', 'gap_wide'):
    d, lo, hi, p = boot(lp, scores(f'E2|LP-{v}|'))
    print(f'{v:22s} PR {ms(vals(f"E2|LP-{v}|", "PR_AUC"))}  ROC {ms(vals(f"E2|LP-{v}|", "ROC_AUC"))}  '
          f'LitePhospho - this {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  p={p:.3f}')

print('\n=== E3: protein language models ===')
for name in ('esm2_t12_35M_UR50D-finetuned-window', 'esm2_t12_35M_UR50D-frozen-fullctx',
             'esm2_t33_650M_UR50D-frozen-fullctx'):
    pre = f'E3|{name}|'; rr = distinct_runs(pre)
    d, lo, hi, p = boot(lp, scores(pre, rr))
    print(f'{name:38s} n={len(vals(pre, "PR_AUC", rr))}  PR {ms(vals(pre, "PR_AUC", rr))}  ROC {ms(vals(pre, "ROC_AUC", rr))}  '
          f'ECE {ms(vals(pre, "ECE", rr))}  LitePhospho - this {d:+.4f} [{lo:+.4f}, {hi:+.4f}]')

print('\n=== E4: MusiteDeep 2020 released models (run2) vs LitePhospho ===')
md = np.load(RUNS[1] / 'scores' / 'E4__MusiteDeep2020-released__homology__na.npy').astype(np.float32)
r = RES[1]['E4|MusiteDeep2020-released|homology|na']
d, lo, hi, p = boot(lp, md)
print(f'MusiteDeep 2020: ROC {r["ROC_AUC"]:.3f}  PR {r["PR_AUC"]:.3f}  ECE {r["ECE"]:.2f}  coverage {r["coverage"]:.0%}')
print(f'LitePhospho - MusiteDeep 2020: {d:+.4f} [{lo:+.4f}, {hi:+.4f}]  p={p:.3f}')
for aa in 'STY':
    k = residue == aa
    print(f'  {aa}: n={k.sum():,}  PR MusiteDeep 2020 {ap(y[k], md[k]):.3f}  LitePhospho {ap(y[k], lp[k]):.3f}')
