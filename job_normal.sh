#!/bin/bash -l
 
#PBS -P xv83 
#PBS -l walltime=18:00:00
## normal
#PBS -q hugemem
#PBS -l ncpus=48
#PBS -l mem=1470GB
##PBS -l jobfs=1300GB  
##PBS -q normal
##PBS -l ncpus=48
##PBS -l mem=190GB
##PBS -l jobfs=130GB  
#PBS -l wd
#PBS -l storage=gdata/ia39+gdata/xv83+gdata/dk92+gdata/v14+gdata/v19+gdata/fp2+gdata/hh5+gdata/ik11+gdata/cj50+gdata/e14+gdata/ua8
#PBS -j oe
#PBS -m abe
 
module list
module load conda/analysis3-24.04
module load dask-optimiser
module load ferret
conda activate analysis3-23.01
conda env list

# compute the FFDI then
# compute the Thresholds from the FFDI
jupytext ffdi_batch.ipynb --to py
##python -u ./ffdi_batch.py raw ST-05 0 51 1 > ./$PBS_JOBID-job.log1 2>&1
##python -u ./ffdi_batch.py adjust QME-BARRAR2 0 50 1 > ./$PBS_JOBID-job.log1 2>&1
##python -u ./ffdi_batch.py adjust NSW-G 24 50 1 > ./$PBS_JOBID-job.log1 2>&1

jupytext ffdi_threshold_batch.ipynb --to py
jupytext ffdi_threshold_time_batch.ipynb --to py
##python -u ./ffdi_threshold_batch.py raw ST-05 > ./$PBS_JOBID-job.log2 2>&1
##python -u ./ffdi_threshold_batch.py adjust QME-BARRAR2 > ./$PBS_JOBID-job.log2 2>&1
##python -u ./ffdi_threshold_batch.py adjust BOM_ACCESS-ESM1-5_ssp370_r6i1p1f1_BARPA-R_v1-r1-ACS-QME-BARRAR2 > ./$PBS_JOBID-job.log2 2>&1
##python -u ./ffdi_threshold_batch.py adjust NSW-G > ./$PBS_JOBID-job.log2 2>&1
python -u ./ffdi_threshold_time_batch.py adjust QME-BARRAR2 > ./$PBS_JOBID-job.log2 2>&1
 
 
 
 
