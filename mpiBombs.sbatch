#!/bin/bash

#SBATCH --partition=piv
#SBATCH --job-name=mpiPyhonBombs
#SBATCH --time=03:00
#SBATCH --output=bombsOutput.out
#SBATCH --ntask=4

echo "Setting enviroment"
module purge
module load prun gnu7/7.3.0 openmpi3/3.0.0 py2-mpi4py/3.0.0

echo "Launching process"
prun ./mpiPyhonBombs.py sample_input.txt
echo "Python process finished"
