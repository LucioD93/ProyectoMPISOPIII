#!/bin/bash

#SBATCH --partition=piv
#SBATCH --job-name=mpiPyhonBombs
#SBATCH --time=10:00
#SBATCH --output=bombsOutput.out
#SBATCH --ntask=12

echo "Setting enviroment"
module purge
module load prun gnu7/7.3.0 openmpi3/3 py3-mpi4py/3.0.0

echo "Launching process"
prun ./mpiPythonBombs.py caso2.txt
echo "Python process finished"
