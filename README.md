# LitePhospho

**A homology-controlled benchmark and a lightweight, explainable model for phosphorylation-site prediction.**

LitePhospho predicts serine/threonine/tyrosine (S/T/Y) phosphorylation sites from protein sequence. Its purpose is twofold: (1) to provide a strictly **homology-controlled (leakage-free) benchmark** on which a spectrum of models is re-evaluated under one identical protocol, and (2) to deliver **LitePhospho**, a compact (0.44M-parameter), calibrated, explainable, CPU-deployable model that stays competitive under that benchmark.

## Highlights
- **Leakage-free evaluation:** proteins are clustered at 30% sequence identity (MMseqs2) and whole clusters assigned to train/validation/test, so no test protein resembles any training protein. 19,625 phosphoproteins form 9,870 clusters, giving 807,583 / 175,019 / 172,614 windows.
- **Verified data:** EPSD site coordinates are checked against the UniProt residue. About 13% of raw candidate positives are coordinate mismatches (wrong isoform or release) that land on non-phosphoacceptor residues; these are discarded. Retaining them creates a trivial shortcut that inflates measured performance.
- **Honest benchmark:** classical baselines, faithful reimplementations of DeepPhos and MusiteDeep, and frozen ESM2 protein-language-model references, all on the same test set.
- **Key finding:** leakage inflation is **architecture-dependent, not size-dependent**. Removing homology control costs LitePhospho only −0.030 ROC-AUC, versus −0.043 for DeepPhos\* and −0.047 for MusiteDeep\* — even though DeepPhos\* has *fewer* parameters than LitePhospho.
- **Deployable:** 1.67 MB, ~0.96 ms/site on CPU, exported to ONNX; well calibrated (ECE 0.015) without post-hoc recalibration.
- **Reproducible:** fixed seeds and deterministic cuDNN; five retrainings vary by less than 0.001 in ROC-AUC and PR-AUC.

## Results (leakage-free 30%-identity split, same test set, n = 172,614)
| Model | PR-AUC | ROC-AUC | F1 |
|---|---|---|---|
| Random forest | 0.702 | 0.712 | 0.651 |
| Logistic regression | 0.706 | 0.725 | 0.666 |
| Linear SVM | 0.706 | 0.724 | 0.657 |
| XGBoost (best classical) | 0.718 | 0.728 | 0.667 |
| PlainCNN | 0.730 | 0.740 | 0.681 |
| MusiteDeep\* (reimplemented) | 0.755 | 0.761 | 0.699 |
| DeepPhos\* (reimplemented) | 0.758 | 0.764 | 0.696 |
| **LitePhospho (ours)** | **0.765** | **0.769** | **0.697** |
| ESM2-8M (centre residue) | 0.767 | 0.761 | 0.686 |
| ESM2-35M (pooled; accuracy ceiling) | 0.779 | 0.775 | 0.702 |

Paired bootstrap (B = 1000) against LitePhospho: XGBoost −0.047, DeepPhos\* −0.007, MusiteDeep\* −0.010 PR-AUC (all *p* < 0.001); the 35M ESM2 reference leads by 0.014 PR-AUC. LitePhospho therefore reaches **98% of the strongest reference's PR-AUC using about 1.2% of its parameters**.

At realistic class prevalence (0.315) LitePhospho reaches PR-AUC 0.612 (1.9× the random baseline), and it recovers **81.7%** of disease phosphosites on previously unseen proteins (PTMD 2.0; 83.2% across all mapped sites).

\* Reimplementations, not the original software — the original releases depend on obsolete framework versions. Under a leaky random split they reach ROC-AUC 0.809 and 0.808, the regime described by their authors.

## Installation

    pip install -r requirements.txt

## Reproducing the results
- **Full pipeline (needs a GPU):** run `notebooks/litephospho_pipeline.ipynb` top to bottom. It preprocesses the data, builds the 30%-identity split, trains LitePhospho and all baselines, and writes every table and figure.
- **Cross-architecture leakage experiment:** `notebooks/litephospho_leakage_experiment.ipynb` trains each architecture under a random and a homology-controlled split.
- **Executed record:** `notebooks/litephospho_canonical_run_executed.ipynb` is the canonical run with all outputs preserved.
- **Tables and figures only (CPU, no training):** load `results/FINAL_scores.npz` (frozen per-model prediction scores and labels) and recompute any metric, confidence interval, or plot.

## Repository structure

    litephospho/
    |-- notebooks/    pipeline, leakage experiment, and the executed canonical run
    |-- data/         litephospho_split.csv (homology-controlled benchmark split)
    |-- models/       trained LitePhospho (.pt) and ONNX export
    |-- results/      FINAL_metrics.csv, FINAL_scores.npz, leakage_crossmethod.json, figures/
    |-- requirements.txt
    |-- LICENSE

## The benchmark split
`data/litephospho_split.csv` lists all **19,625 phosphoproteins** with their 30%-identity cluster (**9,870 clusters**) and train/validation/test assignment (13,941 / 2,889 / 2,795 proteins). Use it to evaluate other methods on the exact same leakage-free partition.

> **Reproducibility note:** MMseqs2 clustering is not bit-for-bit deterministic across runs. Regenerating the partition with the same code yields cluster and window counts differing by under 0.1%, and reproduces held-out ROC-AUC to within 0.001. The file shipped here is the authoritative partition; regenerate it with `notebooks/litephospho_export_split.ipynb` if needed.

## Data sources
The raw databases are not redistributed here; download them from their providers and run the preprocessing in the notebook:
- **EPSD** (phosphosites): https://epsd.biocuckoo.cn/
- **UniProt** (sequences): https://www.uniprot.org/
- **PTMD 2.0** (disease-associated sites): https://ptmd.biocuckoo.cn/

## Citation
[Author list]. *Homology-controlled benchmarking of phosphorylation-site prediction: architecture-dependent leakage inflation and a compact, calibrated model.* [Journal], [year]. (To be updated on acceptance.)

## License
Code is released under the MIT License (see `LICENSE`).
