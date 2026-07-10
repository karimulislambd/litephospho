# LitePhospho

**A homology-controlled benchmark and a lightweight, explainable model for phosphorylation-site prediction.**

LitePhospho predicts serine/threonine/tyrosine (S/T/Y) phosphorylation sites from protein sequence. Its purpose is twofold: (1) to provide a strictly **homology-controlled (leakage-free) benchmark** on which a spectrum of models is re-evaluated under one identical protocol, and (2) to deliver **LitePhospho**, a compact (0.44M-parameter), calibrated, explainable, CPU-deployable model that stays competitive under that benchmark.

## Highlights
- **Leakage-free evaluation:** proteins are clustered at 30% sequence identity (MMseqs2) and whole clusters assigned to train/validation/test, so no test protein resembles any training protein.
- **Honest benchmark:** classical baselines, faithful reimplementations of DeepPhos and MusiteDeep, and ESM2 protein-language-model classifiers, all on the same test set.
- **Key finding:** larger models inflate ~2x more than the compact model when homology control is removed (LitePhospho -0.020 vs DeepPhos -0.049, MusiteDeep -0.042 ROC-AUC).
- **Deployable:** 1.67 MB, ~1.1 ms/site on CPU, exported to ONNX; well calibrated (ECE 0.014).

## Results (leakage-free 30%-identity split, same test set)
| Model | PR-AUC | ROC-AUC | F1 |
|---|---|---|---|
| XGBoost (best classical) | 0.772 | 0.765 | 0.673 |
| MusiteDeep* (reimplemented) | 0.794 | 0.790 | 0.706 |
| DeepPhos* (reimplemented) | 0.800 | 0.795 | 0.707 |
| **LitePhospho (ours)** | **0.805** | **0.800** | **0.706** |
| ESM2 (pooled; accuracy ceiling) | 0.813 | 0.804 | 0.706 |

At realistic class prevalence (0.330) LitePhospho reaches PR-AUC 0.704 (2.1x the random baseline), and it recovers 79.0% of disease phosphosites on unseen proteins (PTMD 2.0). *Reimplementations were validated to reproduce published-regime performance under a random split.*

## Installation

    pip install -r requirements.txt

## Reproducing the results
- **Full pipeline (needs a GPU for training):** open the notebook in `notebooks/` and run it top to bottom. It downloads/preprocesses the data, builds the 30%-identity split, trains LitePhospho and all baselines, and produces every table and figure.
- **Tables and figures only (CPU, no training):** load `results/FINAL_scores.npz` (the frozen per-model prediction scores and labels) and recompute any metric, confidence interval, or plot directly.

## Repository structure

    litephospho/
    |-- notebooks/    full pipeline: data -> split -> train -> evaluate -> explain
    |-- data/         litephospho_split.csv (homology-controlled benchmark split)
    |-- models/       trained LitePhospho (.pt) and ONNX export
    |-- results/      FINAL_metrics.csv and per-model prediction scores (FINAL_scores.npz)
    |-- requirements.txt
    |-- LICENSE

## The benchmark split
`data/litephospho_split.csv` lists every phosphoprotein with its 30%-identity cluster and its train/validation/test assignment. Use it to evaluate other methods on the exact same leakage-free partition.

## Data sources
The raw databases are not redistributed here; download them from their providers and run the preprocessing in the notebook:
- **EPSD** (phosphosites): https://epsd.biocuckoo.cn/
- **UniProt** (sequences): https://www.uniprot.org/
- **PTMD 2.0** (disease-associated sites): https://ptmd.biocuckoo.cn/

## Citation
[Author list]. *Homology-controlled benchmarking of phosphorylation-site prediction: capacity-dependent leakage inflation and a competitive lightweight model.* [Journal], [year]. (To be updated on acceptance.)

## License
Code is released under the MIT License (see `LICENSE`).
