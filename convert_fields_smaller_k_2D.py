import netCDF4 as nc
import argparse
import json as simplejson
import os
import numpy as np
import sys

# merge files from 2D simulations (2D means very narrox y-dimension)


def main():

    # Parse information from the command line
    parser = argparse.ArgumentParser(prog='PyCLES')
    parser.add_argument("casename")
    parser.add_argument("path")
    parser.add_argument("--kmin")
    parser.add_argument("--kmax")
    parser.add_argument("--tmin")
    parser.add_argument("--tmax")
    parser.add_argument("--k0")
    args = parser.parse_args()


    # case_name = args.casename
    path_root = args.path
    # nml = simplejson.loads(open(os.path.join(path_in, case_name + '.in')).read())

    path_fields = os.path.join(path_root, 'fields')
    if args.kmax:
        k_max = np.int(args.kmax)
    else:
        k_max = 120     # leads to about 20% reduction of size for fields of original size 200x200x150
    if args.kmin:
        k_min = np.int(args.kmin)
    else:
        k_min = k_max
    if args.k0:
        k0 = np.int(args.k0)
    else:
        k0 = 0

    print('')
    print('path: ', path_root)
    print('')
    print('k0', k0)
    print('kmin', k_min)
    print('kmax', k_max)
    print('')

    i0_center, i0_coll, j0 = define_geometry(path_root, args)

    # (1) for each time/file in path_fields do...
    # (2) read in original fields file
    #       >> field_keys
    #       >> how to access dimensions of variables?
    #       >> data
    # (3) create new fields file, e.g. 100_k_kmax.nc
    # (4) save data[:,:,:k_max] in new variable of new fields file

    if args.tmin:
        tmin = np.int(args.tmin)
    else:
        tmin = 100
    if args.tmax:
        tmax = np.int(args.tmax)
    else:
        tmax = 100
    times = [np.int(name[:-3]) for name in os.listdir(path_fields) if name[-2:] == 'nc'
             and tmin <= np.int(name[:-3]) <= tmax]
    times.sort()
    nt = len(times)
    print('times: ' + str(times))
    print('nt:', nt)
    files = [str(t) + '.nc' for t in times]
    print(files)
    print('')

    # path_fields = os.path.join(path_root, 'fields_k120')
    # print os.listdir(path_fields)
    # times = [np.int(name[:-8]) for name in os.listdir(path_fields) if name[-2:] == 'nc'
    #          and tmin <= np.int(name[:-8]) <= tmax]
    # times.sort()
    # nt = len(times)
    # print('times: '+str(times))
    # print('nt:', nt)
    # files = [str(t) + '_k120.nc' for t in times]
    # print(files)
    # print('')

    ''' output vertical crosssections for all times and k=0..k_max for all variables given in var_list '''
    var_list = ['u', 'v', 'w', 's', 'temperature', 'phi']
    var_list = ['u', 'v', 'w', 's', 'temperature']

    path_out = os.path.join(path_root, 'fields_merged')
    if not os.path.exists(path_out):
        os.mkdir(path_out)
    print''
    convert_file_for_varlist_vertsection_xz_transposed(var_list, times, files, k_max, path_fields, path_out, j0)
    # convert_file_for_varlist_vertsection_xz(var_list, times, files, path_fields, path_out, j0)
    print''

    return





def convert_file_for_varlist_vertsection_xz(var_list, times, files, path_fields, path_out, location):

    # read in test fields file
    fullpath_in = os.path.join(path_fields, files[0])
    rootgrp_in = nc.Dataset(fullpath_in, 'r')
    # field_keys = rootgrp_in.groups['fields'].variables.keys()
    # dims_keys = rootgrp_in.groups['fields'].dimensions.keys()
    dims = rootgrp_in.groups['fields'].dimensions
    nx_ = dims['nx'].size
    nz_ = dims['nz'].size
    rootgrp_in.close()

    jc = location
    file_name = 'fields_allt_xz_j' + str(np.int(jc)) + '.nc'
    fullpath_out = os.path.join(path_out, file_name)
    print('filename', file_name)

    if os.path.exists(fullpath_out):
        print('')
        print('file ' + fullpath_out + ' already exists! ')
        print('')
    else:
        rootgrp_out = nc.Dataset(fullpath_out, 'w', format='NETCDF4')
        rootgrp_out.createDimension('time', None)
        rootgrp_out.createDimension('nx', nx_)
        rootgrp_out.createDimension('nz', nz_)
        descr_grp = rootgrp_out.createGroup('description')
        var = descr_grp.createVariable('jc', 'f8', )
        var[:] = jc

        time_out = rootgrp_out.createVariable('time', 'f8', ('time',))
        time_out.long_name = 'Time'
        time_out.units = 's'
        time_out[:] = times

        # create variables
        var_list_all = np.append(var_list, 'theta')
        for var in var_list_all:
            rootgrp_out.createVariable(var, 'f8', ('time', 'nx', 'nz'))

        # fill variables
        for it, file in enumerate(files):
            print('file: ', file)
            fullpath_in = os.path.join(path_fields, file)
            rootgrp_in = nc.Dataset(fullpath_in, 'r')
            for var in var_list:
                print('var', var)
                var_out = rootgrp_out.variables[var]
                data = rootgrp_in.groups['fields'].variables[var][:, jc, :]
                var_out[it, :, :] = data[:, :]
            var = 'theta'
            data = rootgrp_in.groups['fields'].variables['s'][:, jc, :]
            data_th = theta_s(data)
            del data
            var_out = rootgrp_out.variables[var]
            var_out[it, :,:] = data_th

        rootgrp_out.close()
    return




def convert_file_for_varlist_vertsection_xz_transposed(var_list, times, files, kmax, path_fields, path_out, location):

    # read in test fields file
    fullpath_in = os.path.join(path_fields, files[0])
    rootgrp_in = nc.Dataset(fullpath_in, 'r')
    # field_keys = rootgrp_in.groups['fields'].variables.keys()
    # dims_keys = rootgrp_in.groups['fields'].dimensions.keys()
    dims = rootgrp_in.groups['fields'].dimensions
    nx_ = dims['nx'].size
    nz_ = np.minimum(kmax, dims['nz'].size)
    rootgrp_in.close()

    jc = location
    file_name = 'fields_allt_xz_transp.nc'
    fullpath_out = os.path.join(path_out, file_name)
    print('filename', file_name)

    if os.path.exists(fullpath_out):
        print('')
        print('file ' + fullpath_out + ' already exists! ')
        print('')
    else:
        rootgrp_out = nc.Dataset(fullpath_out, 'w', format='NETCDF4')
        rootgrp_out.createDimension('time', None)
        rootgrp_out.createDimension('nx', nz_)
        rootgrp_out.createDimension('nz', nx_)
        # descr_grp = rootgrp_out.createGroup('description')

        time_out = rootgrp_out.createVariable('time', 'f8', ('time',))
        time_out.long_name = 'Time'
        time_out.units = 's'
        time_out[:] = times

        # create variables
        var_list_all = np.append(var_list, 'theta')
        for var in var_list_all:
            rootgrp_out.createVariable(var, 'f8', ('time', 'nx', 'nz'))

        # fill variables
        for it, file in enumerate(files):
            print('file: ', file)
            fullpath_in = os.path.join(path_fields, file)
            rootgrp_in = nc.Dataset(fullpath_in, 'r')
            for var in var_list:
                print('var', var)
                var_out = rootgrp_out.variables[var]
                data = rootgrp_in.groups['fields'].variables[var][:, jc, :kmax]
                var_out[it, :, :] = data[:, :].T
            var = 'theta'
            data = rootgrp_in.groups['fields'].variables['s'][:, jc, :kmax]
            data_th = theta_s(data)
            del data
            var_out = rootgrp_out.variables[var]
            var_out[it, :,:] = data_th.T

        rootgrp_out.close()
    return




# _______________________________________________________
# _______________________________________________________

def define_geometry(path_root, args):
    print('--- define geometry ---')

    case_name = args.casename
    nml = simplejson.loads(open(os.path.join(path_root, case_name + '.in')).read())
    global nx, ny, nz, dx, dV, gw
    nx = nml['grid']['nx']
    ny = nml['grid']['ny']
    nz = nml['grid']['nz']
    dx = np.zeros(3, dtype=np.int)
    dx[0] = nml['grid']['dx']
    dx[1] = nml['grid']['dy']
    dx[2] = nml['grid']['dz']
    gw = nml['grid']['gw']
    dV = dx[0] * dx[1] * dx[2]
    print('nml: ', dx, nx)

    # set coordinates for plots
    if case_name == 'ColdPoolDry_single_2D':
        # try:
        #     rstar = nml['init']['r']
        # except:
        #     rstar = 5000.0  # half of the width of initial cold-pools [m]
        # zstar = nml['init']['h']
        try:
            ic = nml['init']['ic']
        except:
            ic = np.int(nx/2)
        ic_arr = np.zeros(1)
        ic_arr[0] = ic
    elif case_name == 'ColdPoolDry_double_2D':
        try:
            rstar = nml['init']['r']
        except:
            rstar = 5000.0  # half of the width of initial cold-pools [m]
        irstar = np.int(np.round(rstar / dx[0]))
        # zstar = nml['init']['h']
        isep = 4 * irstar
        ic1 = np.int(nx / 3)  # np.int(Gr.dims.ng[0] / 3)
        ic2 = ic1 + isep
        ic_arr = [ic1, ic2]



    ''' plotting parameters '''
    # at center of CP: (i0_center)
    # at collision point: (i0_coll)
    if case_name == 'ColdPoolDry_single_2D':
        i0_coll = ic_arr[0]
        i0_center = ic_arr[0]
    elif case_name == 'ColdPoolDry_double_2D':
        i0_center = ic_arr[0]
        i0_coll = 0.5 * (ic_arr[0] + ic_arr[1])

    j0 = np.int(ny / 2)

    print''
    print('CP center: ', i0_center)
    print('CP collision: ', i0_coll)
    print''

    return i0_center, i0_coll, j0

# _______________________________________________________

def create_file(fname, nx, ny, nz):
    rootgrp = nc.Dataset(fname, 'w', format='NETCDF4')
    rootgrp.createDimension('time', None)
    fieldgrp = rootgrp.createGroup('fields')
    fieldgrp.createDimension('nx', nx)
    fieldgrp.createDimension('ny', ny)
    fieldgrp.createDimension('nz', nz)

    rootgrp.close()
    return


def write_field(fname, f, data):
    rootgrp = nc.Dataset(fname, 'r+')
    fields = rootgrp.groups['fields']
    var = fields.createVariable(f, 'f8', ('nx', 'ny', 'nz'))
    var[:, :, :] = data
    rootgrp.close()

# _______________________________________________________
# _______________________________________________________
def theta_s(s):
    T_tilde = 298.15
    sd_tilde = 6864.8
    cpd = 1004.0
    th_s = T_tilde * np.exp( (s - sd_tilde)/cpd )
    return th_s
# _______________________________________________________

if __name__ == '__main__':
    main()
