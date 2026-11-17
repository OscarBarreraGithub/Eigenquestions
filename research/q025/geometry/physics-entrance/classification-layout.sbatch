#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=00:10:00
#SBATCH --job-name=q025-classify-layout
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/physics-entrance/layout-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/physics-entrance/layout-%j.err
set -euo pipefail
umask 022
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/geometry/physics-entrance
/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python layout_graph_distance.py --baseline results --out layout-v2
