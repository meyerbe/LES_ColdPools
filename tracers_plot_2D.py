import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import netCDF4 as nc
import argparse
import json as simplejson
import os

label_size = 10
plt.rcParams['xtick.labelsize'] = label_size
plt.rcParams['ytick.labelsize'] = label_size
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['axes.labelsize'] = 15

def main():
    parser = argparse.ArgumentParser(prog='LES_CP')
    parser.add_argument("casename")
    parser.add_argument("path")
    parser.add_argument("--k0")
    parser.add_argument("--tmin")
    parser.add_argument("--tmax")
    parser.add_argument("--path_tracers")
    parser.add_argument("--shift")
    args = parser.parse_args()
    set_input_parameters(args)

    global cm_bwr, cm_grey, cm_vir, cm_hsv
    cm_bwr = plt.cm.get_cmap('bwr')
    cm_grey = plt.cm.get_cmap('gist_gray_r')
    cm_hsv = plt.cm.get_cmap('hsv')

    dt_fields = 100

    if args.k0:
        k0 = np.int(args.k0)
    else:
        k0 = 0

    if args.shift:
        shift = np.int(args.shift)
    else:
        shift = -1


    path_out_figs = os.path.join(path, 'figs_tracers')
    if not os.path.exists(path_out_figs):
        os.mkdir(path_out_figs)

    if args.path_tracers:
        path_tracers = os.path.join(path, args.path_tracers)
        path_tracer_file = os.path.join(path, args.path_tracers, 'output')
    else:
        k_tracers = 0
        path_tracers = os.path.join(path, 'tracer_k' + str(k_tracers))
        path_tracer_file = os.path.join(path, 'tracer_k' + str(k_tracers), 'output')

    print('')
    print('path figs:    ' + path_out_figs)
    print('path tracers: ' + path_tracer_file)
    print('')

    cp_id = 1
    n_cps = get_number_cps(path_tracer_file)
    n_tracers = get_number_tracers(path_tracer_file)
    print('number of CPs: ' + str(n_cps))
    print('CP ID: ' + str(cp_id))
    coordinates = get_tracer_coords(cp_id, n_cps, n_tracers, times, dt_fields, path_tracer_file)
    print('')

    '''' plot input fields '''
    plot_input_fields(coordinates, n_tracers, shift, path_tracers, path_out_figs)


    var_list = ['s', 'w']
    for it,t0 in enumerate(times):
        print('-plot time: '+str(t0))
        fig_name = 's_w' + '_t' + str(t0) + '_tracers.png'
        fig, axis = plt.subplots(1, 2, figsize=(11, 6), sharey='all')
        rootgrp = nc.Dataset(os.path.join(path_fields, str(t0)+'.nc'))
        for j, var_name in enumerate(var_list):
            print var_name, j
            var = rootgrp.groups['fields'].variables[var_name][:,:,k0]
            max = np.amax(var)
            if var_name in ['w', 'v_rad', 'v_tan']:
                min = -max
                cm_ = cm_bwr
            else:
                min = np.amin(var)
                cm_ = cm_hsv
            # axis[j].contourf(var.T, levels=np.linspace(min, max, 1e2), cmap=cm_)
            axis[j].imshow(var.T, vmin=min, vmax=max, cmap=cm_, origin='lower')
            axis[j].set_title(var_name)
            axis[j].set_aspect('equal')
        rootgrp.close()
        for i in range(n_tracers):
            for j in range(len(var_list)):
                axis[j].plot(coordinates[it,i,0]+shift, coordinates[it,i,1]+shift, 'ok', markersize=2)
        plt.tight_layout()
        fig.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)


    var_list = ['v_rad', 'v_tan']
    rootgrp = nc.Dataset(os.path.join(path, 'fields_v_rad', 'v_rad.nc'))
    for it, t0 in enumerate(times):
        print('-plot time: ' + str(t0))
        fig_name = 'v_rad_tan' + '_t' + str(t0) + '_tracers.png'
        fig, axis = plt.subplots(1, 2, figsize=(11, 6), sharey='all')
        for j, var_name in enumerate(var_list):
            print var_name, j
            var = rootgrp.variables[var_name][it, :, :, k0]
            max = np.amax(var)
            if var_name in ['w', 'v_rad', 'v_tan']:
                min = -max
            else:
                min = np.amin(var)
            axis[j].contourf(var.T, levels=np.linspace(min, max, 1e2), cmap=cm_bwr)
            axis[j].contourf(var.T, levels=np.linspace(min, max, 1e2), cmap=cm_bwr)
            axis[j].set_title(var_name)
            axis[j].set_aspect('equal')
        for i in range(n_tracers):
            for j in range(len(var_list)):
                axis[j].plot(coordinates[it,i,0]+shift, coordinates[it,i,1]+shift, 'ok', markersize=2)
        plt.tight_layout()
        fig.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)
    rootgrp.close()



    var_list = ['u', 'v']
    rootgrp = nc.Dataset(os.path.join(path_tracers, 'input', 'uv_alltimes.nc'))
    for it, t0 in enumerate(times):
        print('-plot time: ' + str(t0))
        fig_name = 'uv_alltimes' + '_t' + str(t0) + '_tracers.png'
        fig, axis = plt.subplots(1, 2, figsize=(11, 6), sharey='all')
        for j, var_name in enumerate(var_list):
            print var_name, j
            var = rootgrp.variables[var_name][it, :, :]
            max = np.amax(var)
            if var_name in ['w', 'v_rad', 'v_tan']:
                min = -max
            else:
                min = np.amin(var)
            axis[j].contourf(var.T, levels=np.linspace(min, max, 1e2), cmap=cm_bwr)
            axis[j].contourf(var.T, levels=np.linspace(min, max, 1e2), cmap=cm_bwr)
            axis[j].set_title(var_name)
            axis[j].set_aspect('equal')
        for i in range(n_tracers):
            for j in range(len(var_list)):
                axis[j].plot(coordinates[it,i,0]+shift, coordinates[it,i,1]+shift, 'ok', markersize=2)
        plt.tight_layout()
        fig.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)
    rootgrp.close()


    return
# ----------------------------------------------------------------------

def plot_input_fields(coordinates, n_tracers, shift, path_tracers, path_out_figs):
    print(os.path.join(path_tracers, 'input', 'uv_alltimes.nc'))
    rootgrp = nc.Dataset(os.path.join(path_tracers, 'input', 'uv_alltimes.nc'))
    for it, t0 in enumerate(times):
        if it > 0:
            print('-plot time: ' + str(t0))
            fig_name = 'uv_input_fields' + '_t' + str(t0) + '_tracers.png'
            fig, ax = plt.subplots(1, 1, figsize=(7, 6), sharey='all')
            var1 = rootgrp.variables['u'][it, :, :]
            var2 = rootgrp.variables['v'][it, :, :]
            max = np.amax(var1)
            min = -max
            # min = np.amin(var)
            ax.contourf(var1.T, levels=np.linspace(min, max, 1e2), cmap=cm_bwr)
            # ax.contour(var2.T, levels=np.linspace(min, max, 2e1), colors='k', linewidth=0.5)
            ax.contour(var2.T, colors='k', linewidths=0.5)
            ax.set_title('u and v')
            ax.set_aspect('equal')
            # for i in range(n_tracers):
            #     ax.plot(coordinates[it, i, 0] + shift, coordinates[it, i, 1] + shift, 'ok', markersize=2)
            plt.tight_layout()
            fig.savefig(os.path.join(path_out_figs, fig_name))
            plt.close(fig)
    rootgrp.close()

    return



# ----------------------------------------------------------------------


def get_tracer_coords(cp_id, n_cps, n_tracers, times, dt_fields, fullpath_in):
    print('get tracer coordinates')
    f = open(fullpath_in + '/coldpool_tracer_out.txt', 'r')
    lines = f.readlines()
    column = lines[0].split()

    nt = len(times)
    coords = np.zeros((nt, n_tracers, 2))

    for it, t0 in enumerate(times):
        print('----t0='+str(t0), it, '----')
        i = 0
        # count = t0 * n_cps * n_tracers + (cp_id - 1) * n_tracers
        # count = it * n_cps * n_tracers + (cp_id - 1) * n_tracers
        count = t0/dt_fields * n_cps * n_tracers + (cp_id - 1) * n_tracers
        # while CP age is 0 and CP ID is cp_id
        timestep = int(lines[count].split()[0])
        cp_ID = int(lines[count].split()[3])
        # while (timestep - 1 == it and cp_ID == cp_id):
        while (timestep - 1 == t0/dt_fields and cp_ID == cp_id):
            columns = lines[count].split()
            coords[it,i,0] = float(columns[4])
            coords[it,i,1] = float(columns[5])
            i += 1
            count += 1
            cp_ID = int(lines[count].split()[3])
            timestep = int(lines[count].split()[0])

    f.close()
    # print ''
    return coords


def get_number_cps(fullpath_in):
    # get number of tracers in each CP
    f = open(fullpath_in + '/coldpool_tracer_out.txt', 'r')
    lines = f.readlines()
    # count = 0
    # # while CP age is 0 and CP ID is 1
    # while (int(lines[count].split()[0]) == 1):
    #     count += 1
    # cp_number = int(lines[count-1].split()[3])
    cp_number = int(lines[-1].split()[3])

    f.close()

    return cp_number


def get_number_tracers(fullpath_in):
    # get number of tracers in each CP
    f = open(fullpath_in + '/coldpool_tracer_out.txt', 'r')
    lines = f.readlines()
    count = 0
    # while CP age is 0 and CP ID is 1
    cp_age = int(lines[count].split()[0])
    cp_ID = int(lines[count].split()[3])
    print('cp_age', cp_age)
    while (cp_age == 1 and cp_ID == 1):
        count += 1
        cp_age = int(lines[count].split()[0])
        cp_ID = int(lines[count].split()[3])
    n_tracers = count
    f.close()

    return n_tracers
# ----------------------------------------------------------------------

def set_input_parameters(args):
    print('--- set input parameters ---')
    global path, path_fields, case_name
    path = args.path
    path_fields = os.path.join(path, 'fields')
    case_name = args.casename

    nml = simplejson.loads(open(os.path.join(path, case_name + '.in')).read())
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

    global tmin, tmax
    if args.tmin:
        tmin = np.int(args.tmin)
    else:
        tmin = 100
    if args.tmax:
        tmax = np.int(args.tmax)
    else:
        tmax = 100

    ''' time range '''
    global times, files
    times = [np.int(name[:-3]) for name in os.listdir(path_fields) if name[-2:] == 'nc'
             and tmin <= np.int(name[:-3]) <= tmax]
    times.sort()
    files = [str(t) + '.nc' for t in times]
    print('tmin, tmax: ', tmin, tmax)
    print('times: ', times)
    print('')

    return

# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
