import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from datetime import datetime
import xarray as xr
from cmcrameri import cm
import sys

###############################################################################
###                           PATH and PARAMETERS
###############################################################################
### Grid and offlines SYMPHONIE (normal version of SYMPHONIE)
path = '../example_files/'
path_fig = '../example_fig/'
grid = '../example_files/grid/grid_full_60_regular12.nc'

###############################################################################
### release period
# here indicates the period of release 'DJF', 'JJA', 'other' if you want to choose manually the oeriod in the script. You can add other options here after
period = 'other'
# here indicates the timestep between each release, i.e. every days, hours, minutes, seconds
step = 'hours'
# here indicates the number of particles to be release at each timestep
particles_per_timestep = 2

### release area, whether a zone or a geographical dropping position
release_area = 'zones' # release_area = 'zones' or 'points'
tot_areas = 3

# if you want to release particles around the barycentre of the geographical zone, chose the following option:
zones = {
    'GLOBINDOC' : {'lon_min': 16, 'lon_max': 139, 'lat_min': -45, 'lat_max': 31}, # global indian ocean
    'ArS' : {'lon_min': 60, 'lon_max': 70, 'lat_min': 7, 'lat_max': 17},  # Arabian Sea
    'BoB' : {'lon_min': 83, 'lon_max': 93, 'lat_min': 7, 'lat_max': 17}, # Bay of Bengal
    'MoC' : {'lon_min': 34, 'lon_max': 44, 'lat_min': -27, 'lat_max': -17} # Mozambique Channel
}

# if you want to determine release positions (lon, lat) around a specific GEOGRAPHICAL DROPPING POINT, chose the following option:
# the corresponding i,j grid cell is needed
points = {
    'Indus' : {'i': 2325, 'j': 592},
    'GBM' : {'i': 2469, 'j': 2874},
    'Zambezi' : {'i': 53, 'j': 2251}
}

###############################################################################
###                           RELEASE PERIOD
###############################################################################
### release period
if period == 'DJF':
    start_date = datetime(2016, 12, 1, 0, 0, 0) # start of release
    stop_date = datetime(2017, 3, 1, 0, 0, 0) # enf of release
elif period == 'JJA':
    start_date = datetime(2017, 6, 1, 0, 0, 0) # start of release
    stop_date = datetime(2017, 8, 30, 0, 0, 0) # enf of release
elif period == 'other':
    start_date = datetime(2017, 1, 1, 0, 0, 0)  # start of release
    stop_date = datetime(2017, 1, 3, 0, 0, 0)  # end of release

print("start_date: " + str(start_date))
print("stop_date: " + str(stop_date))

# chose frequency
freq_map = {
    'days': 'D',
    'hours': 'H',
    'minutes': 'T',  # T = minute
    'seconds': 'S'
}

if step not in freq_map:
    raise ValueError(f"Unsupported step: {step}")

freq = freq_map[step]

### release dates
gradual_dates = pd.date_range(start=start_date, end=stop_date - pd.to_timedelta(1, unit=step), freq=freq) #, periods=int(timestep)).round('s')
print("number of release timesteps: " + str(len(gradual_dates)))

### total number of particles released over the entire simulation
P_tot = len(gradual_dates) * particles_per_timestep * tot_areas
print("number of particles to be release over the whole period: " + str(P_tot))
repeated_dates = gradual_dates.repeat(particles_per_timestep)

area_release_dates = pd.DataFrame({
    'y': repeated_dates.year,
    'm': repeated_dates.month,
    'd': repeated_dates.day,
    'h': repeated_dates.hour,
    'min': repeated_dates.minute,
    's': repeated_dates.second})

total_release_dates = pd.concat([area_release_dates] * tot_areas, ignore_index=True)

print("number of dates saved : ", len(total_release_dates))

###############################################################################
###                      RELEASE HORIZONTAL POSITIONS
###############################################################################
if release_area == 'zones':
    lat1,lon1 = (zones[list(zones.keys())[1]]['lat_min']+(zones[list(zones.keys())[1]]['lat_max']-zones[list(zones.keys())[1]]['lat_min'])/2,
                 zones[list(zones.keys())[1]]['lon_min']+(zones[list(zones.keys())[1]]['lon_max']-zones[list(zones.keys())[1]]['lon_min'])/2)
    lat2,lon2 = (zones[list(zones.keys())[2]]['lat_min']+(zones[list(zones.keys())[2]]['lat_max']-zones[list(zones.keys())[2]]['lat_min'])/2,
                 zones[list(zones.keys())[2]]['lon_min']+(zones[list(zones.keys())[2]]['lon_max']-zones[list(zones.keys())[2]]['lon_min'])/2)
    lat3,lon3 = (zones[list(zones.keys())[3]]['lat_min']+(zones[list(zones.keys())[3]]['lat_max']-zones[list(zones.keys())[3]]['lat_min'])/2,
                 zones[list(zones.keys())[3]]['lon_min']+(zones[list(zones.keys())[3]]['lon_max']-zones[list(zones.keys())[3]]['lon_min'])/2)

elif release_area == 'points':
    lat1, lon1 = (float(g.latitude_t[points[list(points.keys())[0]]['i'], points[list(points.keys())[0]]['j']]),
                  float(g.longitude_t[points[list(points.keys())[0]]['i'], points[list(points.keys())[0]]['j']]))
    lat2, lon2 = (float(g.latitude_t[points[list(points.keys())[1]]['i'], points[list(points.keys())[1]]['j']]),
                  float(g.longitude_t[points[list(points.keys())[1]]['i'], points[list(points.keys())[1]]['j']]))
    lat3, lon3 = (float(g.latitude_t[points[list(points.keys())[2]]['i'], points[list(points.keys())[2]]['j']]),
                  float(g.longitude_t[points[list(points.keys())[2]]['i'], points[list(points.keys())[2]]['j']]))

# choose the radius in degree of the circular plume around the grid point
R = 1

# random draw of the positions in the circular plume
P_per_zone = int(P_tot / tot_areas)

lon_x = []
lat_y = []

# Function to generate random points within a circular plume
def generate_points(lon, lat, R, num_points):
    r = R * np.sqrt(np.random.rand(num_points, 1))  # Random radii
    theta = 2 * np.pi * np.random.rand(num_points, 1)  # Random angles
    lon_points = lon + (r / np.cos(np.radians(lat))) * np.cos(theta)
    lat_points = lat + r * np.sin(theta)
    return lon_points.flatten(), lat_points.flatten()

# Generate points for each zone
for center_lon, center_lat in [(lon1, lat1), (lon2, lat2), (lon3, lat3)]:
    lon_tmp, lat_tmp = generate_points(center_lon, center_lat, R, P_per_zone)
    lon_x.extend(lon_tmp)
    lat_y.extend(lat_tmp)

# Ensure all points are accounted for (if P_tot is not divisible by tot_areas)
remaining_points = P_tot - len(lon_x)
if remaining_points > 0:
    lon_tmp, lat_tmp = generate_points(lon3, lat3, R, remaining_points)
    lon_x.extend(lon_tmp)
    lat_y.extend(lat_tmp)

# Convert to numpy arrays for consistency
lon_x = np.array(lon_x)
lat_y = np.array(lat_y)

print(f"Number of release positions saved: {len(lon_x)}, {len(lat_y)}")

###############################################################################
###                      RELEASE VERTICAL POSITIONS
###############################################################################

# random draw of the particle release depth z
top_depth = -1 # in m
bottom_depth = -5 # in m
z_rd = np.around(np.random.uniform(bottom_depth, top_depth, int(P_tot)), 1)
print("number of release positions saved : " + str(len(lon_x)), len(lat_y), len(z_rd))

###############################################################################
###                          PLUME VERIFICATION
###############################################################################

# verification 1
plt.plot(lon_x, lat_y, 'o')
plt.show()

### store all release data in M
M_tmp = pd.DataFrame([np.ravel(lon_x), np.ravel(lat_y), z_rd]).transpose()
M = pd.concat([M_tmp], axis=0, ignore_index=True)

# verification 2
plt.plot(M[0].to_numpy(), M[1].to_numpy(), 'o')
# plt.show()

###############################################################################
###                        VERTICAL VELOCITIES
###############################################################################

### sinking or rising velocities associated with particles (if not determined before thank to observations
# ws = pd.DataFrame({'ws': int(P_tot/3) * ( [0] + [0.01] + [-0.001] )})
ws = pd.DataFrame({'ws': int(P_tot) * ( [0] )})

###############################################################################
###                        TOTAL RELEASE PARAMETERS
###############################################################################

### saving all the release parameters
Id_P = pd.DataFrame(np.arange(1, len(M)+1))
final = pd.concat([Id_P, M, total_release_dates, ws], axis=1)  # np.matrix().T
print(len(total_release_dates), len(M), len(Id_P), len(ws), len(final))

np.savetxt(path + 'preprocessing/release_plume_' + str(len(final)) + '_drifters_' + str(start_date.strftime("%Y-%m-%d")) + '_to_' + str(stop_date.strftime("%Y-%m-%d")) + '.txt',
           final,
           fmt=('%4i', '%9.5f', '%9.5f', '%4.1f', '%4i', '%2i', '%2i', '%2i', '%2i', '%2i', '%5.3f'),
           header='Id_P lon lat z year month day h m s ws')

###############################################################################
#                         MASK VERIFICATION                                   #
###############################################################################
### inputs upstream grid cell (65,230)
g = xr.open_dataset(grid)
msk_u = g['mask_u'][:, :]   # extracting mask terre/mer + contour
msk_v = g['mask_v'][:, :]   # extracting mask terre/mer + contour
msk_t = g['mask_t'][:, :]   # extracting mask terre/mer + contour
lon_t = g['longitude_t'][:, :]  # extracting lon data
lat_t = g['latitude_t'][:, :]   # extracting lat data
g.close()         # closing netcdf file

# plot grid mask
g.mask_t.plot.contourf(x='longitude_t', y='latitude_t', cmap = cm.nuuk, levels=3)
# g12.mask_t.plot.contour(x='longitude_t', y='latitude_t', color='k')
# plot drifters initial positions
plt.plot(M[0].to_numpy(), M[1].to_numpy(), '.', color='indianred')
plt.xlim(np.nanmin(g.longitude_t), np.nanmax(g.longitude_t))
plt.ylim(np.nanmin(g.latitude_t), np.nanmax(g.latitude_t))
plt.savefig(path_fig + 'release_plumes.png', dpi=300, bbox_inches='tight')
plt.show()

