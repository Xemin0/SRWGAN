#!/bin/bash

# Job Name
#SBATCH -J SRWGAN

# Time Requested (Not tested yet)
#SBATCH -t 5:00:00

# Number of Cores (max 4)
#SBATCH -c 4

# Single Node (Not yet optmized for Distributed Computing)
#SBATCH -N 1

# Request GPU partition and Access (max 2)
#SBATCH -p gpu --gres=gpu:2

# Request Memory (Not tested yet)
#SBATCH --mem=20G

# Outputs
#SBATCH -e ./scratch/SRWGAN.err
#SBATCH -o ./scratch/SRWGAN.out

############## END OF SLURM COMMANDS #############

# Show CPU infos
lscpu

# Show GPU infos
nvidia-smi

# Force Printing Out `stdout`
export PYTHONUNBUFFERED=TRUE

# Load modules 
#module load openssl/3.0.0 cuda/11.7.1 cudnn/8.6.0

# Activate Conda Env
#conda activate /anaconda3/envs/srwgan

# Run the Python file with arguments
python3 train_SRWGAN.py --trainnum 600 --epochs 200 --batchsz 4 --gpweight 16.0 --cweight 4 --savemodel True
