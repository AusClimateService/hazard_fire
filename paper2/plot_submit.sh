#!/bin/bash
task=$1

jobfile="pjob_0.pbs"

# Create PBS job script
  cat > $jobfile <<EOF
#!/bin/bash -l
##PBS -P xv83 
#PBS -P v19 
#PBS -l walltime=24:00:00
## normal
#PBS -q normalbw
#PBS -l ncpus=14
#PBS -l mem=63GB
#PBS -l wd
#PBS -l storage=scratch/xv83+gdata/ia39+gdata/xv83+gdata/dk92+gdata/v14+gdata/v19+gdata/fp2+gdata/hh5+gdata/ik11+gdata/cj50+gdata/e14+gdata/ua8
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
#conda activate analysis3-23.10
#conda env list
# list available kernels
jupyter kernelspec list

# Plot figures for SA papern

#papermill plot_ffdi-change.ipynb output/out_plot0.ipynb -p dirstore 'sa_2090'

for year in 'sa_obs' 'sa_2020' 'sa_2050' 'sa_2090'; do
#for year in 'sa_obs' ; do
  echo "Running script for \$year"
  papermill plot_ffdi.ipynb output/out_plot1_\${year}.ipynb -p dirstore \${year}
  papermill plot_SA.ipynb  output/out_plot2_\${year}.ipynb -p dirstore \${year}
done

EOF

# Submit the job
 qsub $jobfile

