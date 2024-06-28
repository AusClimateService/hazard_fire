# hazard_fire
Code and descriptions for fire weather indices and metrics

The initial code was developed to compute FFDI from the bias_input_data of the ACS regional climate simulations

FFDI is based on XCLIM implementation 

The code has been setup to process the data in bias-input-data for ssp370

To apply the code, one needs to
1. rechunk the simulations to store the data with all the time points in one chunk and save it into a Zarr store.  The chunking process required an initial time chunk of 1 because some of the files chunk only one-time point!  In future, it is recommended to chunk the netcdf files with smaller dimensions (e.g. time =-1, lat=33, lon=43) to facilitate the building of a dataset with one chunk in time.

The resulting Zarr store only has the 4 variables used in the FFDI calculation, which should be fixed. (add dswr and rhusmax),  
The Zarr store should also speed up other diagnostics done along the time dimension (e.g. EHF)

2. run the ffdi_v0 to compute the ffdi from the Zarr stores from 1.
Note the XCLIM ffdi code cannot have chunking across the time dimension, hence the need for rechunking

The final step would be to create a script with the appropriate queue setup to process the entire dataset, like

PBS commands

for model 0 to 12 do 
	python rechunk,py model
	python ffdi_v0 model
done


Data locations: 
 - /g/data/ia39/ncra/bushfire/ffdi - multi-model
 - /g/data/ia39/ncra/fire
