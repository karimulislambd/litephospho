# LitePhospho reviewer experiments — summary

Seeds: [1, 2, 3] | AMP: True | total runtime 6.43 h | split: released litephospho_split.csv

Homology test set: 172,682 windows (50.4% positive)

## E1 — multi-seed benchmark and leakage inflation

| Model | Homology ROC | Homology PR | Random ROC | Inflation (ROC) mean ± sd | 95% CI | n |
|---|---|---|---|---|---|---|
| LitePhospho | 0.7676 ± 0.0011 | 0.7620 ± 0.0014 | 0.7997 ± 0.0008 | 0.0321 ± 0.0012 | [+0.0290, +0.0351] | 3 |
| DeepPhos | 0.7617 ± 0.0015 | 0.7572 ± 0.0016 | 0.8124 ± 0.0023 | 0.0507 ± 0.0037 | [+0.0415, +0.0600] | 3 |
| MusiteDeep | 0.7603 ± 0.0007 | 0.7548 ± 0.0009 | 0.8095 ± 0.0005 | 0.0492 ± 0.0007 | [+0.0474, +0.0510] | 3 |

Welch t-tests on inflation (does architecture change inflation beyond seed noise?):
- DeepPhos − LitePhospho: Δinflation +0.0187, t = 8.24, p = 0.007767
- MusiteDeep − LitePhospho: Δinflation +0.0172, t = 20.65, p = 0.0001491
- MusiteDeep − DeepPhos: Δinflation -0.0015, t = -0.69, p = 0.5569

Paired bootstrap on seed-averaged homology scores (ΔPR-AUC, LitePhospho − other, B = 1000):
- vs DeepPhos: +0.0037 [+0.0031, +0.0045], one-sided p = 0.0000
- vs MusiteDeep: +0.0041 [+0.0033, +0.0049], one-sided p = 0.0000

## E2 — flatten vs global pooling (homology split, same trainer and seeds)

| Variant | Params | ROC-AUC | PR-AUC | n |
|---|---|---|---|---|
| LitePhospho (flatten) | 436,577 | 0.7676 ± 0.0011 | 0.7620 ± 0.0014 | 3 |
| LP-gap | 190,817 | 0.7526 ± 0.0006 | 0.7433 ± 0.0004 | 3 |
| LP-gmp | 190,817 | 0.7456 ± 0.0013 | 0.7363 ± 0.0019 | 3 |
| LP-gap_wide | 500,897 | 0.7513 ± 0.0016 | 0.7420 ± 0.0017 | 3 |

## E3 — protein language models / E4 — published tool as released

| Model | ROC-AUC | PR-AUC | ECE | n | note |
|---|---|---|---|---|---|
| esm2_t12_35M_UR50D-frozen-fullctx | 0.7809 ± 0.0005 | 0.7894 ± 0.0005 | 0.0114 ± 0.0008 | 3 |  |
| esm2_t33_650M_UR50D-frozen-fullctx | 0.7833 ± 0.0012 | 0.7910 ± 0.0010 | 0.0065 ± 0.0021 | 3 |  |
| esm2_t12_35M_UR50D-finetuned-window | 0.7708 | 0.7672 | 0.0334 | 1 |  |
| MusiteDeep2020-released | 0.7218 | 0.7246 | 0.2195 | 1 | coverage 100.0% |