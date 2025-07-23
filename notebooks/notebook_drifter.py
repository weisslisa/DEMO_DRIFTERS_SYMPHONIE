# -------LIB------------------
import pandas as pd
from datetime import datetime
# -----------------------------

path = '/home/weissli/Documents/SYMPHONIE/MODULE_DRIFTER/v3_plume/'

# river = 'Indus' # Indus GBM Zambezi
zone = '3zones'
period = '2017-01-01'

### open drifters information file with positions, sinking or rising velocity, time of release
f = path + f'release_plume_4320_{period}_v3.txt' # '_2016-12-01.txt'
# f_in = path + 'coord_plume_release_with_ws_450_2011-01-12_2011-01-14.txt'

df = pd.read_table(f, delim_whitespace=True) # header=0

# period of release

### open destination file in writing mode
destination = open(path + f'notebook_drifter_{zone}_{len(df)}_{period}_v3', "w")

### write in destination file
# write header (parameters can be modified)
destination.write('1        ! 1=Lagragian drifters routine is on (=0 otherwise)                                             ! DRIFTER_ONOFF\n'
                  'notebook ! initial mode: "notebook" or "fortran"                                                         ! DRIFTER_INITIAL_MODE\n' 
                  '3600.    ! sampling (seconds) of the outputs (<0 if no ascii output)                                     ! DRIFTER_OUT_SAMPLING\n' 
                  '2        ! Output files format: 0= one file per drifter, 1= one file with all drifters per mpi rank, 2= a single netcdf file per sampling  ! drifter_output_files\n'
                  '2        ! Runge-Kutta order (RK1, RK2 or RK4) for drifters time stepping. RK2 is recommended.           ! rungekutta_order\n'
                  '3        ! Time steps ratio: drifters time step over momentum equations time step (i.e. dt_drf/dti_fw)   ! dt_drf_over_dti_fw\n' 
                  '1 6      ! 1/0 (on/off) and storage index in drifter_l array for individual buoyancy / vertical velocity ! flag_buo_w,id_wdrifter\n'
                  '0        ! 1 = add tke-dependent random vertical velocity, 2 = KH-dependent random w, 0 = no random w     ! drifter_random_w\n'
                  '1        ! flag_stay_in_water=1 to prevent particles from settling on the bottom (0 otherwise)\n'
                  '-- if "notebook" mode: give now the drifter list --- check that nbomax is big enough in parameter ----\n')

# write drifter positions, sinking or rising velocity, time of release
for i in range(len(df)):
    destination.write("%10.6f %10.6f %6.1f   0        !---- arg4=1: i j k, arg4=0: lat lon z of the drifter\n"
                      "%1.3f                                   ! vertical_buoyancy_velocity\n"
                      "%i %i %i %i %i %i                          ! year, month, day, hour, minute, second\n"
                      % (df.lat[i], df.lon[i], df.z[i],
                         df.ws[i],
                         df.year[i], df.month[i], df.day[i], df.h[i], df.m[i], df.s[i])) # , int(uniform(0, 24))))

destination.close()