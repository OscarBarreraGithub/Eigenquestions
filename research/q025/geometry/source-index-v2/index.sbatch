#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --job-name=q025-method-index
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-index-v2/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-index-v2/slurm-%j.err
set -euo pipefail
umask 022
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-index-v2
PYTHON=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
"$PYTHON" smoke_check.py
"$PYTHON" export_index.py --pack ../compact-source-context/pack --units inputs/units-metadata.json --ledger ../round4/inputs/current-relation-ledger.json --full-edges /n/holylabs/randall_lab/Everyone/swampland/graph-extraction/atlas-20261104/snapshots/20261104T205600Z/downloads/edges.jsonl.gz --out pack
