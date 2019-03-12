#!/bin/bash

#PBS -l wd
#PBS -l ncpus=2
#PBS -l mem=32GB
#PBS -l walltime=00:30:00
#PBS -q normal
#PBS -P w35
#PBS -m ae
#PBS -M mdekauwe@gmail.com
set -e

ulimit -s unlimited

umask 022

python run_comparison.py --qsub

