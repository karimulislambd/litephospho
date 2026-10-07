"""PTMD 2.0 sensitivity check at matched false-positive rates, by homology status.

Scores every mapped PTMD 2.0 phosphorylation site with the released ONNX model and reports
recall at thresholds fixed by the FPR they produce on the negatives of the homology-controlled
test set. Sites on validation/test-cluster proteins (<30% identity to every training protein)
form the reported external set.

PTMD and UniProt are not redistributed; pass their paths:
    python analysis/ptmd_recall_fpr.py --ptmd Total.txt --uniprot uniprotkb.fasta
(UniProt: reviewed human proteome in FASTA; PTMD 2.0: 'Total.txt' from https://ptmd.biocuckoo.cn/)
"""
import argparse
import re
from pathlib import Path

import numpy as np
import onnxruntime as ort
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
ap_ = argparse.ArgumentParser(); ap_.add_argument('--ptmd', required=True); ap_.add_argument('--uniprot', required=True)
args = ap_.parse_args()

WINDOW, HALF = 31, 15
VOCAB = {a: i for i, a in enumerate('ACDEFGHIKLMNPQRSTVWYX')}

seq, acc, buf = {}, None, []
for line in open(args.uniprot):
    line = line.strip()
    if line.startswith('>'):
        if acc: seq[acc] = ''.join(buf)
        p = line[1:].split('|'); acc = p[1] if len(p) >= 2 else p[0].split()[0]; buf = []
    else:
        buf.append(line)
if acc: seq[acc] = ''.join(buf)
split = pd.read_csv(ROOT / 'data' / 'litephospho_split.csv').set_index('accession')['split'].to_dict()

ptmd = pd.read_csv(args.ptmd, sep=None, engine='python')
ptmd = ptmd[ptmd['Type'].astype(str).str.contains('phospho', case=False, na=False)]
wins, groups = [], []
for a_raw, pos in zip(ptmd['UniProt'], ptmd['Position']):
    a = str(a_raw).split('-')[0].strip(); m = re.match(r'^([A-Za-z])?(\d+)', str(pos).strip())
    if a not in seq or not m:
        continue
    i = int(m.group(2)) - 1; s = seq[a]
    if not (0 <= i < len(s)) or s[i] not in 'STY':
        continue
    wins.append(('X' * HALF + s + 'X' * HALF)[i:i + WINDOW])
    sp = split.get(a)
    groups.append('train' if sp == 'train' else 'held-out' if sp in ('val', 'test') else 'unclustered')
groups = np.array(groups)
print(f'PTMD phosphorylation rows {len(ptmd):,}; mapped S/T/Y sites {len(wins):,}; '
      + ', '.join(f'{g} {np.sum(groups == g):,}' for g in ('train', 'held-out', 'unclustered')))

sess = ort.InferenceSession(str(ROOT / 'models' / 'litephospho_v4.onnx'), providers=['CPUExecutionProvider'])
name = sess.get_inputs()[0].name
X = np.array([[VOCAB.get(c, VOCAB['X']) for c in w.upper()] for w in wins], dtype=np.int64)
logit = np.concatenate([sess.run(None, {name: X[k:k + 4096]})[0].reshape(-1) for k in range(0, len(X), 4096)])
prob = 1 / (1 + np.exp(-logit))

z = np.load(ROOT / 'results' / 'FINAL_scores.npz')
y, s = z['y_true'].astype(int), z['LitePhospho'].astype(float)
neg = s[y == 0]
print('\noperating   threshold  test FPR  test recall  PTMD recall (held-out clusters)')
for label, t in [('default', 0.5)] + [(f'FPR {int(f * 100)}%', float(np.quantile(neg, 1 - f))) for f in (0.20, 0.10, 0.05)]:
    print(f'{label:10s}  {t:9.3f}  {np.mean(neg >= t):8.3f}  {np.mean(s[y == 1] >= t):11.3f}  '
          f'{np.mean(prob[groups == "held-out"] >= t):.3f}')
