#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --job-name=q025-assembly-smoke
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/assembly/smoke-v1/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/assembly/smoke-v1/slurm-%j.err
set -euo pipefail
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/assembly/smoke-v1
/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python overview_smoke.py
