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
import sys

def main():
    print('COMPUTING MIN MAX')
    # (A) domain maximum
    #
    # (B) maximum in cross-sections
    #   determine max v in yz-crosssections
    #   determine max u in xz-crosssections


    ''' set paths & parameters '''
    # Parse information from the command line
    parser = argparse.ArgumentParser(prog='LES_CP')
    parser.add_argument("casename")
    parser.add_argument("path")
    parser.add_argument("--tmin")
    parser.add_argument("--tmax")
    parser.add_argument("--kmin")
    parser.add_argument("--kmax")
    args = parser.parse_args()

    files, times, nml, ic_arr, jc_arr, kmax = set_input_parameters(args)

    ID = os.path.split(path_in)[1]
    print('id: ', ID)

    ''' (A) plot and output domain min/max '''
    var_list = ['w', 's', 'temperature', 'theta']
    # var_list = ['w']
    data_minmax_domain = plot_minmax_domain(var_list, ID, kmax, times)
    minmax_file_name = 'minmax_domain.nc'
    dump_minmax_file(data_minmax_domain, var_list, times, kmax,
                     ID, minmax_file_name, path_in)



    ''' (B) plot min/max from  azimuthally averaged fields '''
    minmax_xz = plot_xz_minmax(ID, jc_arr, times)


    return



# ----------------------------------
# ----------------------------------


def plot_xz_minmax(ID, jc_arr, times):
    print('')
    print('computing min/max xz')
    var_list = ['u', 'w', 's', 'temperature']
    minmax = {}
    minmax['time'] = times
    for var_name in var_list:
        minmax[var_name] = {}
        minmax[var_name]['max'] = np.zeros(len(times), dtype=np.double)
        minmax[var_name]['min'] = np.zeros(len(times), dtype=np.double)

    for var_name in var_list:
        print('')
        print('xz: variable: ' + var_name)
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all', figsize=(5, 12))
        for it, t0 in enumerate(times):
            var = read_in_netcdf_fields(var_name, os.path.join(path_fields, str(t0) + '.nc'))
            minmax[var_name]['max'][it] = np.amax(var[:,jc_arr[0],:])
            minmax[var_name]['min'][it] = np.amin(var[:,jc_arr[0],:])
            del var
        maxx = ax1.plot(times, minmax[var_name]['max'][:], 'o-', label=ID)
        minn = ax2.plot(times, minmax[var_name]['min'][:], 'o-', label=ID)
        ax1.legend(loc='best', fontsize=10)
        ax2.legend(loc='best', fontsize=10)
        ax1.set_title('max(' + var_name + ')')
        ax1.set_ylabel('max(' + var_name + ')')
        ax2.set_title('min(' + var_name + ')')
        ax2.set_ylabel('min(' + var_name + ')')
        ax2.set_xlabel('time [s]')
        fig.suptitle(ID)
        fig.savefig(os.path.join(path_out_figs, var_name + '_' + ID + '_minmax_xz.png'))
        plt.close(fig)

    return minmax



# compute domain minimum and maximum of variables (s, temperature, w) for each timestep
def plot_minmax_domain(var_list, ID, kmax, times):
    print('computing min/max domain')

    minmax = {}
    minmax['time'] = times
    for var_name in var_list:
        minmax[var_name] = {}
        minmax[var_name]['max'] = np.zeros(len(times), dtype=np.double)
        minmax[var_name]['min'] = np.zeros(len(times), dtype=np.double)
    # # # minmax['w'] = {}
    # # # minmax['s'] = {}
    # # # minmax['temp'] = {}

    for var_name in var_list:
        print('')
        print('variable: ' + var_name)
        fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all', figsize=(5,12))
        for it, t0 in enumerate(times):
            if var_name == 'theta':
                s_var = read_in_netcdf_fields('s', os.path.join(path_fields, str(t0)+'.nc'))
                var = theta_s(s_var)
            else:
                var = read_in_netcdf_fields(var_name, os.path.join(path_fields, str(t0)+'.nc'))
            minmax[var_name]['max'][it] = np.amax(var[:,:,:])
            minmax[var_name]['min'][it] = np.amin(var[:,:,:])
            del var
        maxx = ax1.plot(times, minmax[var_name]['max'][:], 'o-', label=ID)
        minn = ax2.plot(times, minmax[var_name]['min'][:], 'o-', label=ID)
        ax1.legend(loc='best', fontsize=10)
        ax2.legend(loc='best', fontsize=10)
        ax1.set_title('max(' + var_name + ')')
        ax1.set_ylabel('max(' + var_name + ')')
        ax2.set_title('min(' + var_name + ')')
        ax2.set_ylabel('min(' + var_name + ')')
        ax2.set_xlabel('time [s]')
        fig.suptitle(ID)
        fig_name = var_name+'_'+str(ID)+'_minmax.png'
        print('saving: ' + os.path.join(path_out_figs, var_name + '_' + fig_name))
        fig.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)
        print('')

    return minmax



# ----------------------------------
def theta_s(s):
    # parameters from pycles
    T_tilde = 298.15
    sd_tilde = 6864.8
    cpd = 1004.0
    th_s = T_tilde * np.exp( (s - sd_tilde)/cpd )
    return th_s

# ----------------------------------
def set_input_parameters(args):
    ''' setting parameters '''
    global path_in, path_out_data, path_out_figs, path_fields
    path_in = args.path
    if os.path.exists(os.path.join(path_in, 'fields')):
        path_fields = os.path.join(path_in, 'fields')
    elif os.path.exists(os.path.join(path_in, 'fields_k120')):
        path_fields = os.path.join(path_in, 'fields_k120')
    path_out_data = os.path.join(path_in, 'data_analysis')
    if not os.path.exists(path_out_data):
        os.mkdir(path_out_data)
    path_out_figs = os.path.join(path_in, 'figs_minmax')
    if not os.path.exists(path_out_figs):
        os.mkdir(path_out_figs)
    print('')
    print('paths: ')
    print('path data in: ' + path_in)
    print('path data out: ' + path_out_data)
    print('path figures:  ' + path_out_figs)
    print('')

    global case_name
    case_name = args.casename
    nml = simplejson.loads(open(os.path.join(path_in, case_name + '.in')).read())
    global nx, ny, nz, dx
    dx = np.ndarray(3, dtype=np.int)
    nx = nml['grid']['nx']
    ny = nml['grid']['ny']
    nz = nml['grid']['nz']
    dx[0] = nml['grid']['dx']
    dx[1] = nml['grid']['dy']
    dx[2] = nml['grid']['dz']
    # gw = nml['grid']['gw']


    try:
        print('(ic,jc) from nml')
        ic = nml['init']['ic']
        jc = nml['init']['jc']
        ic_arr = np.zeros(1)
        jc_arr = np.zeros(1)
        ic_arr[0] = ic
        jc_arr[0] = jc
    except:
        print('(ic,jc) NOT from nml')
        if case_name == 'ColdPoolDry_single_3D':
            ic = np.int(nx/2)
            jc = np.int(ny/2)
            ic_arr = np.zeros(1)
            jc_arr = np.zeros(1)
            ic_arr[0] = ic
            jc_arr[0] = jc
        else:
            print('ic, jc not defined')
    # try:
    #     marg = nml['init']['marg']
    #     print('marg from nml')
    # except:
    #     marg = 500.
    #     print('marg NOT from nml')


    # global krange
    # if args.kmin:
    #     kmin = np.int(args.kmin)
    # else:
    #     kmin = 1
    if args.kmax:
        kmax = np.int(args.kmax)
    else:
        kmax = np.int(10e3*1./dx[2])
    # krange = np.arange(kmin, kmax + 1)

    if args.tmin:
        tmin = np.int(args.tmin)
    else:
        tmin = 100
    if args.tmax:
        tmax = np.int(args.tmax)
    else:
        tmax = 100

    ''' file range '''
    files = [name for name in os.listdir(path_fields) if name[-2:] == 'nc']
    if len(files[0]) <= 7:  # 100.nc
        files = [name for name in os.listdir(path_fields) if name[-2:] == 'nc'
                 and np.int(name[:-3]) >= tmin and np.int(name[:-3]) <= tmax]
        times = [np.int(name[:-3]) for name in files]
        times.sort()
        for it, t0 in enumerate(times):
            files[it] = str(t0) + '.nc'
    else:  # 100_k120.nc
        files = [name for name in os.listdir(path_fields) if name[-2:] == 'nc'
                 and np.int(name[:-8]) >= tmin and np.int(name[:-8]) <= tmax]
        times = [np.int(name[:-8]) for name in files]
        times = times.sort()
        for it, t0 in enumerate(times):
            files[it] = str(t0) + files[0][3:]

    print('')
    print('files', files)
    print('len', len(files))
    print('')
    print('times', times)
    print('')
    return files, times, nml, ic_arr, jc_arr, kmax


# --------------------------------------------------------------------

def dump_minmax_file(data, var_list, times, kmax,
                     ID, file_name, path_in):
    print(' ')
    print('-------- dump minmax data -------- ')
    # print(os.path.join(path_out_data, file_name))

    nt = len(times)

    path_out_data = os.path.join(path_in, 'data_analysis')
    print(os.path.join(path_out_data, file_name))

    rootgrp = nc.Dataset(os.path.join(path_out_data, file_name), 'w', format='NETCDF4')

    dims_grp = rootgrp.createGroup('dimensions')
    # dims_grp.createDimension('dx', dx[0])
    dims_grp.createDimension('nz', kmax)

    ts_grp = rootgrp.createGroup('timeseries')
    ts_grp.createDimension('nt', nt)
    var = ts_grp.createVariable('time', 'f8', ('nt'))
    var.unit = "s"
    var[:] = times

    for var_name in var_list:
        var = ts_grp.createVariable(var_name+'_max', 'f8', ('nt'))
        var[:] = data[var_name]['max'][:]
        var = ts_grp.createVariable(var_name + '_min', 'f8', ('nt'))
        var[:] = data[var_name]['min'][:]

    rootgrp.close()
    print('')
    return
# ----------------------------------


def read_in_netcdf_fields(variable_name, fullpath_in):
    # print(fullpath_in)
    rootgrp = nc.Dataset(fullpath_in, 'r')
    var = rootgrp.groups['fields'].variables[variable_name]
    data = var[:,:,:]
    rootgrp.close()
    return data

if __name__ == '__main__':
    main()