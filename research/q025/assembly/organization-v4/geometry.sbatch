#!/bin/bash
#SBATCH --account=randall_lab
#SBATCH --partition=test
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --job-name=q025-approved-homes
#SBATCH --output=slurm-%j.log
set -euo pipefail
export OPENBLAS_NUM_THREADS=4
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
trap 'touch FAILED' ERR
/n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/env/bin/python measure-approved-overview.py --input accepted-geometry-input.json --support positive-support.json --reference-root /n/netscratch/randall_lab/Everyone/obarrera/physics-atlas-encoders/20261104-v1/results --out results
touch COMPLETE
