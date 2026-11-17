#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --job-name=q025-organization-compare
#SBATCH --output=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/organization-comparison-v1/attempt-1/slurm-%j.out
#SBATCH --error=/n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/organization-comparison-v1/attempt-1/slurm-%j.err
set -euo pipefail
export PYTHONUNBUFFERED=1 PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4
cd /n/netscratch/randall_lab/Everyone/obarrera/eigenquestions-q025/organization-comparison-v1/attempt-1
/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python compare.py --input accepted-geometry-input.json --support support-and-access.local.json --routes source-method-routes.json --reference-root /n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/results --out results
