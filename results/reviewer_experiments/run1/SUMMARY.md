# LitePhospho reviewer experiments — summary

Seeds: [1, 2, 3] | AMP: True | total runtime 5.10 h | split: released litephospho_split.csv

Homology test set: 172,682 windows (50.4% positive)

## E1 — multi-seed benchmark and leakage inflation

| Model | Homology ROC | Homology PR | Random ROC | Inflation (ROC) mean ± sd | 95% CI | n |
|---|---|---|---|---|---|---|
| LitePhospho | 0.7678 ± 0.0007 | 0.7629 ± 0.0009 | 0.7984 ± 0.0024 | 0.0306 ± 0.0019 | [+0.0258, +0.0355] | 3 |
| DeepPhos | 0.7615 ± 0.0004 | 0.7567 ± 0.0002 | 0.8113 ± 0.0028 | 0.0498 ± 0.0028 | [+0.0428, +0.0568] | 3 |
| MusiteDeep | 0.7600 ± 0.0014 | 0.7531 ± 0.0026 | 0.8070 ± 0.0022 | 0.0470 ± 0.0028 | [+0.0400, +0.0540] | 3 |

Welch t-tests on inflation (does architecture change inflation beyond seed noise?):
- DeepPhos − LitePhospho: Δinflation +0.0192, t = 9.72, p = 0.001085
- MusiteDeep − LitePhospho: Δinflation +0.0164, t = 8.27, p = 0.001912
- MusiteDeep − DeepPhos: Δinflation -0.0028, t = -1.22, p = 0.288

Paired bootstrap on seed-averaged homology scores (ΔPR-AUC, LitePhospho − other, B = 1000):
- vs DeepPhos: +0.0059 [+0.0051, +0.0066], one-sided p = 0.0000
- vs MusiteDeep: +0.0071 [+0.0062, +0.0080], one-sided p = 0.0000

## E2 — flatten vs global pooling (homology split, same trainer and seeds)

| Variant | Params | ROC-AUC | PR-AUC | n |
|---|---|---|---|---|
| LitePhospho (flatten) | 436,577 | 0.7678 ± 0.0007 | 0.7629 ± 0.0009 | 3 |
| LP-gap | 190,817 | 0.7530 ± 0.0009 | 0.7434 ± 0.0009 | 3 |
| LP-gmp | 190,817 | 0.7423 ± 0.0046 | 0.7317 ± 0.0060 | 3 |
| LP-gap_wide | 500,897 | 0.7504 ± 0.0011 | 0.7403 ± 0.0014 | 3 |

## E3 — protein language models / E4 — published tool as released

| Model | ROC-AUC | PR-AUC | ECE | n | note |
|---|---|---|---|---|---|
| esm2_t12_35M_UR50D-frozen-fullctx | 0.7809 ± 0.0005 | 0.7894 ± 0.0005 | 0.0114 ± 0.0008 | 3 |  |
| esm2_t33_650M_UR50D-frozen-fullctx | 0.7833 ± 0.0012 | 0.7910 ± 0.0010 | 0.0065 ± 0.0021 | 3 |  |
| esm2_t12_35M_UR50D-finetuned-window | 0.7704 | 0.7672 | 0.0341 | 1 |  |

E4 error: {'error': 'RuntimeError(\'failed: cd /tmp/musite/MusiteDeep_web/MusiteDeep && CUDA_VISIBLE_DEVICES="" /tmp/musite/\')'}