# LitePhospho

A homology-controlled benchmark and a lightweight, explainable model for
serine/threonine/tyrosine **phosphosite prediction**.

Under a strict 30%-identity (leakage-free) split, LitePhospho — a 0.44M-parameter
position-preserving CNN — is significantly better than classical baselines and on par
with reimplemented DeepPhos/MusiteDeep, while a pooled ESM2 classifier is the accuracy
ceiling. We also show that larger models inflate ~2× more under evaluation leakage.

## Key results (leakage-free, PR-AUC)
| Model | PR-AUC | ROC-AUC |
|---|---|---|
| XGBoost | 0.772 | 0.765 |
| DeepPhos* / MusiteDeep* (reimpl.) | 0.800 / 0.794 | 0.795 / 0.790 |
| **LitePhospho (ours)** | **0.805** | **0.800** |
| ESM2 (pooled, ceiling) | 0.813 | 0.804 |

## Repository structure
- `notebooks/` — full pipeline (data → split → train → evaluate → explain)
- `data/litephospho_split.csv` — the homology-controlled benchmark split (accession, cluster, split)
- `models/` — trained LitePhospho (`.pt`) and ONNX export
- `results/` — final metrics and per-model prediction scores

## Reproduce
```bash
pip install -r requirements.txt
