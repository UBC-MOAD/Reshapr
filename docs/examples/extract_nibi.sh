#!/bin/bash

#SBATCH --job-name=test-reshapr
#SBATCH --ntasks=16
# force all cores to be on the same node
#SBATCH --ntasks-per-node=16
#SBATCH --mem-per-cpu=8000M
#SBATCH --time=1:30:00
#SBATCH --mail-user=dlatorne@eoas.ubc.ca
#SBATCH --mail-type=ALL
#SBATCH --account=def-allen
# stdout and stderr file paths/names
#SBATCH --output=/scratch/dlatorne/test-reshapr/stdout
#SBATCH --error=/scratch/dlatorne/test-reshapr/stderr

WORK_DIR=$HOME/MOAD/reshapr-expts/

pixi run -m $HOME/MOAD/Reshapr reshapr -v debug extract $WORK_DIR/extract_nibi.yaml --start-date 2007-01-01 --end-date 2007-12-31
