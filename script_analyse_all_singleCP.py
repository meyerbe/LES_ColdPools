import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cm as cm
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
import netCDF4 as nc
import argparse
import json as simplejson
import os

import compute_minmax_all
from compute_minmax_all import compute_minmax


''' set paths & parameters '''
# Parse information from the command line
parser = argparse.ArgumentParser(prog='LES_CP')
parser.add_argument("casename")
parser.add_argument("root_path")
parser.add_argument("--tmin")
parser.add_argument("--tmax")
parser.add_argument("--kmin")
parser.add_argument("--kmax")
args = parser.parse_args()

print '''setting parameters '''
case_name = args.casename
global path_root, path_out_data, path_out_figs
path_root = args.root_path
path_out_data = os.path.join(path_root, 'data_analysis')
if not os.path.exists(path_out_data):
    os.mkdir(path_out_data)
path_out_figs = os.path.join(path_root, 'figs_minmax')
if not os.path.exists(path_out_figs):
    os.mkdir(path_out_figs)
print('paths:')
print path_root
print path_out_data
print path_out_figs

dTh_range = [3]
zstar_range = [4000, 2000, 2000, 1500, 1000, 1000, 670, 2000, 500, 250 ]
zstar_range = [4000, 1500, 670, 250]
rstar_range = [250, 670, 1500, 4000]
n_thermo = len(dTh_range)
n_geom = len(zstar_range)
thermo_parameters = np.asarray(dTh_range)
geom_parameters = np.zeros((n_thermo, 2, n_geom), dtype=np.int)
geom_parameters[0,0,:] = zstar_range
geom_parameters[0,1,:] = rstar_range
# geom_parameters[0, :] = [4000, 2000, 2000, 1500, 1000, 1000, 670, 2000, 500, 250 ]


# thermo_parameters
test_arr = np.zeros((3, 2))
test_arr[0,0] = 3
# test_arr[0,1] = [1 2]
print('...', test_arr)
# test_list = {}
# test_list

if args.kmin:
    kmin = np.int(args.kmin)
else:
    kmin = 1
if args.kmax:
    kmax = np.int(args.kmax)
else:
    kmax = 1

if args.tmin:
    tmin = np.int(args.tmin)
else:
    tmin = 100
if args.tmax:
    tmax = np.int(args.tmax)
else:
    tmax = 100
dt = 100
times = np.arange(tmin, tmax + dt, dt)



# compute_minmax(dTh_range, zstar_range, rstar_range,
#                 kmin, kmax, times, path_root, case_name)
compute_minmax(thermo_parameters, geom_parameters, kmin, kmax, times,
               case_name, path_root, path_out_figs, path_out_data)
