# LitePhospho

**A homology-controlled benchmark and a compact, calibrated reference model for phosphorylation-site prediction.**

LitePhospho predicts serine/threonine/tyrosine (S/T/Y) phosphorylation sites from protein sequence. The repository serves two purposes: (1) a **homology-controlled benchmark** on which a spectrum of models is re-evaluated under one identical protocol, and (2) **LitePhospho**, a compact (0.44M-parameter), calibrated, explainable, CPU-deployable reference model evaluated within it.

## Highlights
- **Homology-controlled evaluation:** proteins are clustered at 30% sequence identity (MMseqs2) and whole clusters are assigned to train/validation/test, so no test protein shares more than 30% identity with any training protein. 19,625 phosphoproteins form 9,870 clusters, giving 807,583 / 175,019 / 172,614 windows.
- **Verified data:** EPSD site coordinates are checked against the reviewed UniProt (Swiss-Prot) sequence. Of the 664,562 sites that can be placed on a sequence, 86,954 (13.1%) are coordinate mismatches (wrong isoform or release) that land on non-phosphoacceptor residues; they are discarded, because retaining them creates a trivial shortcut that inflates measured performance.
- **Leakage inflation depends on architecture, not size:** over six runs with one identical training procedure, removing homology control costs LitePhospho 0.031 ± 0.002 ROC-AUC, versus 0.050 ± 0.003 for DeepPhos\* and 0.048 ± 0.002 for MusiteDeep\* (both *p* < 10⁻⁵), although DeepPhos\* has *fewer* parameters than LitePhospho.
- **Where protein language models gain:** on the same 31-residue window, an ESM2-35M fine-tuned end to end is no better than LitePhospho; frozen ESM2 given the whole protein leads by about 0.026 PR-AUC, and scaling from 35M to 650M parameters adds almost nothing. The advantage comes from context, not scale.
- **Position preservation matters:** replacing LitePhospho's flatten step with global pooling costs 0.019–0.028 PR-AUC, even for a pooled variant with more parameters.
- **Deployable:** 1.67 MB, ~0.96 ms/site on CPU via ONNX; well calibrated (ECE 0.015), and ECE 0.010 at realistic prevalence after a closed-form prior-shift correction.

## Main benchmark (homology-controlled test set, n = 172,614)
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
| ESM2-35M (window pooling, ±64 context) | 0.779 | 0.775 | 0.702 |

Paired bootstrap (B = 1000) against LitePhospho: XGBoost −0.047, DeepPhos\* −0.007, MusiteDeep\* −0.010 PR-AUC (all *p* < 0.001); the 35M ESM2 reference leads by 0.014 PR-AUC.

At realistic class prevalence (0.315) LitePhospho reaches PR-AUC 0.612 (about 1.9× the random baseline). On disease-associated PTMD 2.0 sites from held-out protein clusters (n = 56,017, <30% identity to all training proteins) it recovers 81.7% at the default threshold and 57.2% at a 10% false-positive rate (test-set recall at that rate: 40.1%).

\* Our reimplementations, trained on the benchmark; the original training code depends on obsolete framework versions. The released MusiteDeep 2020 prediction models are evaluated separately below.

## Follow-up experiments (reviewer response)
Run on the released split with one identical training procedure for all deep models, three seeds, executed twice (six runs per configuration unless stated otherwise).

| Experiment | Result |
|---|---|
| Leakage inflation (ROC-AUC) | LitePhospho 0.031 ± 0.002; DeepPhos\* 0.050 ± 0.003; MusiteDeep\* 0.048 ± 0.002 |
| LitePhospho vs reimplementations (PR-AUC) | +0.005 over DeepPhos\*, +0.006 over MusiteDeep\* (both *p* < 0.001) |
| Pooling ablation (PR-AUC) | flatten 0.762; global avg. 0.743; global max 0.734; capacity-matched avg. (500,897 params) 0.741 |
| ESM2-35M fine-tuned on the 31-residue window | 0.767 (= LitePhospho; Δ −0.0005, n.s.) |
| ESM2-35M / ESM2-650M frozen, whole protein | 0.789 / 0.791 |
| MusiteDeep 2020, released models as published | 0.725 (LitePhospho +0.042; ahead for S, T and Y) |

## Installation

    pip install -r requirements.txt

## Reproducing the results
- **Full pipeline (needs a GPU):** `notebooks/litephospho_pipeline.ipynb` preprocesses the data, builds the 30%-identity split, trains LitePhospho and all baselines, and writes every table and figure. `notebooks/litephospho_canonical_run_executed.ipynb` is the canonical run with all outputs preserved.
- **Original cross-architecture leakage experiment:** `notebooks/litephospho_leakage_experiment.ipynb` (single run; superseded by the follow-up experiments).
- **Follow-up experiments (Kaggle, GPU):** `notebooks/litephospho_reviewer_experiments.ipynb` runs E1 (multi-seed leakage), E2 (pooling ablation), E3 (ESM2 35M/650M and fine-tuning) and E4 (released MusiteDeep 2020). `notebooks/litephospho_E4_musitedeep_CPU.ipynb` runs E4 alone on CPU. Outputs of both executions are in `results/reviewer_experiments/run1` and `run2`.
- **Statistics and figures only (CPU, no training):**
  - `python analysis/reviewer_stats.py` — every number in the follow-up sections (pooled runs, Welch's tests, paired bootstraps, per-residue results).
  - `python analysis/calibration_prevalence.py` — calibration at realistic prevalence, raw and prior-shift corrected.
  - `python analysis/ptmd_recall_fpr.py --ptmd Total.txt --uniprot uniprotkb.fasta` — PTMD 2.0 recall at matched false-positive rates (needs the external data files).
  - `python analysis/make_fig_leakage_multiseed.py` — the multi-run leakage figure.
  - `results/FINAL_scores.npz` holds the frozen per-model test scores and labels of the main benchmark.

## Repository structure

    litephospho/
    |-- notebooks/    pipeline, executed canonical run, leakage experiment, follow-up experiments
    |-- analysis/     scripts that recompute the reported statistics and figures
    |-- data/         litephospho_split.csv (homology-controlled benchmark split)
    |-- models/       trained LitePhospho (.pt) and ONNX export
    |-- results/      FINAL_metrics.csv, FINAL_scores.npz, figures/,
    |                 reviewer_experiments/ (run1, run2: results, summaries, per-window scores)
    |-- requirements.txt
    |-- LICENSE

## The benchmark split
`data/litephospho_split.csv` lists all **19,625 phosphoproteins** with their 30%-identity cluster (**9,870 clusters**) and train/validation/test assignment (13,941 / 2,889 / 2,795 proteins). Use it to evaluate other methods on exactly the same partition.

> **Reproducibility notes:** MMseqs2 clustering is not bit-for-bit deterministic across runs; regenerating the partition with the same code changes cluster and window counts by under 0.1% and held-out ROC-AUC by under 0.001. The file shipped here is the authoritative partition (regenerate with `notebooks/litephospho_export_split.ipynb` if needed). Rebuilding the windows on this split with negatives sampled in sorted protein order, as the follow-up notebook does, gives 807,454 / 175,080 / 172,682 windows. GPU training is not bit-for-bit deterministic either, which is why the follow-up experiments were executed twice and pooled.

## Data sources
The raw databases are not redistributed; download them from their providers:
- **EPSD** (phosphosites): https://epsd.biocuckoo.cn/
- **UniProt** (reviewed human sequences): https://www.uniprot.org/
- **PTMD 2.0** (disease-associated sites): https://ptmd.biocuckoo.cn/

## Citation
[Author list]. *Homology-controlled benchmarking of phosphorylation-site prediction: architecture-dependent leakage inflation and a compact, calibrated reference model.* [Journal], [year]. (To be updated on acceptance.)

## License
Code is released under the MIT License (see `LICENSE`).
