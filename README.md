# Lagrangian simulation with SYMPHONIE hydrodynamic model

This package contains scripts for creating the 'notebook_drifter' required for Lagrangian runs with SYMPHONIE and few simple post-processing scripts.


## construction of the notebook_drifter:

* first I run the script 'coord_plume_release.py'
   	 * allow to choose the release period,
   	 * the release position,
   	 * the particle sinking or rising velocities

I converted the grid into polygons (.shp) to verify if the release positions are in the sea mask with the script 'coord_plume_release.py'

* then I run the script 'notebook_drifter.py' to create the SYMPHONIE notebook from the txt file 'coord_plume_release_with_ws_450_2000-08-01_2000-08-01.txt' created by the previous script

* in the 'notebook_drifter' you can choose the output format - the best is '.nc' instead of 'txt'

* you can also choose the timestep to save the output (trajectory timestep)

* if you have a vertical turbulent component (like TKE or vertical diffusion) in your offlines you can activate one of the vertical turbulent diffusion scheme, if not deactivate it

* to save computation time you can increase the Time steps ratio


## SYMPHONIE Lagrangian simulations

* upload the notebook_drifter in the 'SYMPHONIE/CONFIG/NOTEBOOK' directory

* upload offlines in the 'SYMPHONIE/CONFIG/OFLLINE' directory (for ROMS offlines instead of SYMPHONIE, the format date needs to be modify according to Patrick FORTRAN routine)

* the grid of the configuration is needed with the good directory path and features in 'notebook_grid'

* in the 'notebook_offline' : activate the offline mode (ioffline = 2) and indicate the offlines storage path

* in the 'notebook_time' : the start time of the simulation should be at least one timestep before the first drifter release (if 1 average offline per day : at least 1 day before the first particle release)
    
* all the forcing (wave, tide, air-sea, ...) notebooks are in the deactivated mode


## DRIFTERS trajectories output

* the output files will be saved in the '/RDIR/CONFIG/tmp/' directory
    
* if you choose the '.nc' format, one file is obtain per output timestep (one per day for example)

* you can find some output examples in ... directory

* then you can run the post-processing python script to visualize the drifters positions like 'drifter_density.py' 'drifter_proba.py' 'drifter_traj.py'

