"""Figure: leakage inflation under a random vs the homology-controlled split, mean +- s.d. over six
runs (two executions x three seeds) of the reviewer experiment E1.

Usage (from the repository root):  python analysis/make_fig_leakage_multiseed.py
Writes results/figures/fig_leakage_multiseed.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1] / 'results'
RUNS = [json.load(open(ROOT / 'reviewer_experiments' / r / 'results.json')) for r in ('run1', 'run2')]
models = [('LitePhospho', 'LitePhospho\n(0.44M)'), ('DeepPhos', 'DeepPhos$^{*}$\n(0.39M)'),
          ('MusiteDeep', 'MusiteDeep$^{*}$\n(0.67M)')]

fig, ax = plt.subplots(figsize=(7.6, 5.0)); w = 0.36
for i, (m, label) in enumerate(models):
    rnd = [R[f'E1|{m}|random|seed{s}']['ROC_AUC'] for R in RUNS for s in (1, 2, 3)]
    hom = [R[f'E1|{m}|homology|seed{s}']['ROC_AUC'] for R in RUNS for s in (1, 2, 3)]
    infl = np.array(rnd) - np.array(hom)
    for off, v, col, name in ((-w / 2, rnd, '#95a5a6', 'Random split (leaky)'),
                              (w / 2, hom, '#e74c3c', 'Homology 30% (controlled)')):
        ax.bar(i + off, np.mean(v), w, yerr=np.std(v, ddof=1), capsize=4, color=col,
               label=name if i == 0 else None, error_kw=dict(lw=1))
        ax.scatter([i + off] * len(v), v, s=10, color='black', zorder=3)
        ax.text(i + off, np.mean(v) + 0.007, f'{np.mean(v):.3f}', ha='center', fontsize=10)
    ax.text(i, 0.735, f'$-${infl.mean():.3f}\n$\\pm${infl.std(ddof=1):.3f}', ha='center',
            fontsize=12, fontweight='bold', color='white')
ax.set_xticks(range(len(models))); ax.set_xticklabels([l for _, l in models], fontsize=11)
ax.set_ylim(0.6, 0.85); ax.set_ylabel('ROC-AUC', fontsize=11)
ax.set_title('Leakage inflation: random vs homology-controlled split (6 runs)', fontsize=12)
ax.legend(loc='lower left', fontsize=10); ax.grid(axis='y', alpha=.3)
fig.tight_layout()
out = ROOT / 'figures' / 'fig_leakage_multiseed.png'
fig.savefig(out, dpi=300, bbox_inches='tight'); print('saved', out)
