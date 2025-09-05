# FFDI extremes paper from RCMs

## Code and workflow for multi-model analysis of FFDI and atmospheric variables from RCMs

Foundation of a draft paper on FFDI extremes using RCMs. 

A suite of notebooks were created for the analysis. The workflow uses papermill to run the notebooks in batch model.  There are two script files for doing this.

submit.sh  - runs the required notebooks to produce all the data required.  The script created multiple batch jobs to run the analysis on three RCM at a time.  The script creates files for subsquent analysis and plotting.  By commenting out papermill commands one can choose what notebook to run.  The directory output stores the notebook run.

plot_submit.sh  - run notebooks to produce figures.  The resulting figures are saved to figs directory with a copy of the notebook used saved to output.
