#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:05:00
#SBATCH --job-name=q025-dated-HC
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/final-release-v1/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/final-release-v1/slurm-%j.err
set -euo pipefail
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/final-release-v1
/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python update_flow.py --input accepted-geometry-input.json --previous-input ../final-overview-v1/attempt-1/accepted-geometry-input.json --previous-flow ../final-overview-v1/attempt-1/results/complete-F.npz --schematic schematic-preholdout.json --out results
