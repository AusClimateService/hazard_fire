#!/bin/bash

task=$1

case "$task" in
  0)
    echo "Period 0 observations ..."
	store="'sa_obs'"
	ts="'2000-01-01'"
	te="'2020-12-31'"
    ;;
  1)
    echo "Period 1 ..."
	store="'sa_2020'"
	ts="'2015-01-01'"
	te="'2035-01-01'"
    ;;
  2)
    echo "period 2..."
	store="'sa_2050'"
	ts="'2040-01-01'"
	te="'2060-01-01'"
    ;;
  3)
    echo "Period 3..."
	store="'sa_2090'"
	ts="'2080-01-01'"
	te="'2100-01-01'"
    ;;
  *)
    echo "Unknown task: $task"
    echo "Usage: $0 {1|2|3}"
    exit 1
    ;;
esac

for ((j1=0; j1<=0; j1+=4)); do
##for ((j1=1; j1<=44; j1+=4)); do
  j2=$((j1 + 3))
#  j2=$((j1 + 2))
#  j2=$((j1 + 1))
#  j2=$((j1 + 0))
  jobfile="cjob_${j1}_${j2}.pbs"

  # Create PBS job script
  cat > $jobfile <<EOF
#!/bin/bash -l
#PBS -P xv83 
#PBS -l walltime=24:00:00
## normal
#PBS -q normalbw
#PBS -l ncpus=28
#PBS -l mem=256GB
#PBS -l wd
#PBS -l storage=gdata/ia39+gdata/xv83+gdata/dk92+gdata/v14+gdata/v19+gdata/fp2+gdata/xp65+gdata/ik11+gdata/cj50+gdata/e14+gdata/ua8
#PBS -j oe
#PBS -m abe
 
module list
#module unload conda/analysis3-24.04
#module load conda/analysis3-23.10
#module load dask-optimiser
module load ferret
module use /g/data/xp65/public/modules
module load conda/analysis3
module list
conda env list
conda activate analysis3-23.10

conda env list
# list available kernels
jupyter kernelspec list

# compute SOBOL information

echo "Time from $ts to $te "
echo "Processing from $j1 to $j2"
for ((i=$j1; i<=$j2; i+=1)); do
#papermill xr_correl.ipynb output/outcor_\${i}.ipynb -k python3 -p mindex \${i} -p lat1 -45 -p lat2 -10 -p lon1 110 -p lon2 155 -p p_ext 0.99 -p t1 $ts -p t2 $te -p dirstore $store
papermill xr_permutation.ipynb output/outper_\${i}.ipynb -k python3 -p mindex \${i} -p lat1 -45 -p lat2 -10 -p lon1 110 -p lon2 155 -p p_ext 0.99 -p t1 $ts -p t2 $te -p dirstore $store
papermill xr_fit_pdf.ipynb output/outfit_\${i}.ipynb -k python3 -p mindex \${i} -p lat1 -45 -p lat2 -10 -p lon1 110 -p lon2 155 -p p_ext 0.99 -p t1 $ts -p t2 $te -p dirstore $store
papermill xr_sobol-v1.ipynb output/outsobol_\${i}.ipynb -k python3 -p mindex \${i} -p lat1 -45 -p lat2 -10 -p lon1 110 -p lon2 155 -p p_ext 0.99 -p t1 $ts -p t2 $te -p dirstore $store
done

EOF

# Submit the job
 qsub $jobfile
done

