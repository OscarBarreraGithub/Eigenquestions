#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH --time=00:10:00
#SBATCH --job-name=q025-broad-display
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/final-overview-v1/attempt-1/display-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/final-overview-v1/attempt-1/display-%j.err
set -euo pipefail
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/final-overview-v1/attempt-1
/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python correct_display.py --previous results --out corrected-display
