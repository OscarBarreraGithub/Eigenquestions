#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --job-name=q025-compact-context
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/compact-source-context/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/compact-source-context/slurm-%j.err
set -euo pipefail
umask 022
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/compact-source-context
/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python compact_source_context.py --pack ../source-context/pack --units ../round3-v2/results/source-rows.jsonl --evidence /n/holylabs/randall_lab/Everyone/swampland/graph-extraction/atlas-20261104/snapshots/20261104T205600Z/downloads/evidence.jsonl.gz --out pack
