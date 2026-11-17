#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --job-name=q025-full-context
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact/slurm-%j.err
set -euo pipefail
umask 022
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/source-context-v3-compact
PYTHON=/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python
"$PYTHON" ../source-index-v2/smoke_check.py
"$PYTHON" build_full_pack.py --downloads /n/holylabs/randall_lab/Everyone/swampland/graph-extraction/atlas-20261104/snapshots/20261104T205600Z/downloads --units ../source-index-v2/inputs/units-metadata.json --ledger ../round4/inputs/current-relation-ledger.json --old-pack ../compact-source-context/pack --out pack
