#!/bin/bash -l
 
#PBS -P xv83
#PBS -q megamem
#PBS -l walltime=48:00:00
#PBS -l ncpus=48
#PBS -l mem=2990GB
#PBS -l jobfs=1400GB
#PBS -l wd
#PBS -l storage=gdata/xv83+gdata  mmore
#PBS -j oe
#PBS -m abe
 
conda activate pangeo_bran2020_demo

for it in 0 1  # mse and abs fits
do 
time python  ../rechunk.py ${it} > ./$PBS_JOBID_rechunker.log 2>&1
done 
 

# script to run the gev code to compute the desire output
conda activate tf_xarray  # curl-hf
#   time python gev1.py 0 >& l0 | tee l0 &
   time python gev1.py 0 >& l0 &
   time python gev1.py 10 >& l10 &
   time python gev1.py 15 >& l15 &
   time python gev1.py 20 >& l20 &
   time python gev1.py 25 >! l25 &

time python ifit.py >& lfit1  &