#!/bin/bash

#PBS -l wd
#PBS -l ncpus=4
#PBS -l mem=32GB
#PBS -l walltime=01:30:00
#PBS -q normal
#PBS -P w35
#PBS -m ae
#PBS -M mdekauwe@gmail.com
#PBS -l storage=gdata/w35+gdata/wd9




source activate sci
module add netcdf/4.7.1
python ./run_comparison.py --qsub

