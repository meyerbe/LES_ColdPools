import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import netCDF4 as nc
import argparse
import json as simplejson
import os
import sys


label_size = 12
plt.rcParams['xtick.labelsize'] = label_size
plt.rcParams['ytick.labelsize'] = label_size
plt.rcParams['axes.labelsize'] = 15
# plt.rcParams['xtick.direction']='out'
# plt.rcParams['ytick.direction']='out'
plt.rcParams['legend.fontsize'] = 8
# plt.rcParams['lines.linewidth'] = 3
# plt.rcParams['grid.linewidth'] = 20
# plt.rcParams['xtick.major.size'] = 8.5
# plt.rcParams['xtick.minor.size'] = 5
# plt.rcParams['ytick.major.size'] = 8.5
# plt.rcParams['ytick.minor.size'] = 5
# plt.rcParams['xtick.major.width'] = 2
# plt.rcParams['xtick.minor.width'] = 1.5
# plt.rcParams['ytick.major.width'] = 2
# plt.rcParams['ytick.minor.width'] = 1.5
# plt.rcParams['pdf.fonttype'] = 42         # Output Type 3 (Type3) or Type 42 (TrueType)

def main():

    ''' set paths & parameters '''
    # Parse information from the command line
    parser = argparse.ArgumentParser(prog='LES_CP')
    parser.add_argument("casename")
    parser.add_argument("path_root")
    parser.add_argument("path1")
    parser.add_argument("path2")
    parser.add_argument("path_out")
    parser.add_argument("--tmin")
    parser.add_argument("--tmax")
    parser.add_argument("--kmax")
    parser.add_argument("--everysecond")
    args = parser.parse_args()

    set_input_parameters(args)
    # ic_arr, jc_arr = define_geometry(nml)
    if args.everysecond:
        every_second = args.everysecond
    else:
        every_second = True
    print('every_second', every_second)

    file_name = 'stats_radial_averaged.nc'
    file1 = nc.Dataset(os.path.join(path1, 'data_analysis', file_name))
    file2 = nc.Dataset(os.path.join(path2, 'data_analysis', file_name))

    dx1 = file1.groups['dimensions'].dimensions['dx'].size
    dx2 = file2.groups['dimensions'].dimensions['dx'].size
    dz1 = file1.groups['dimensions'].dimensions['dz'].size
    dz2 = file2.groups['dimensions'].dimensions['dz'].size
    if dx1 < dx2:   # want to have file2 higher resolution
        file_aux = file2
        file2 = file1
        file1 = file_aux
        del file_aux
    print('dx: ', dx1_nml[0], dx2_nml[0], dx1)
    print('dz: ', dx1_nml[2], dx2_nml[2], dz1)
    print('nx: ', nx1[0], nx2[0])
    print('nz: ', nx1[2], nx2[2])

    grp_stats1 = file1.groups['stats'].variables
    grp_stats2 = file2.groups['stats'].variables

    time1 = file1.groups['timeseries'].variables['time'][:]
    time2 = file2.groups['timeseries'].variables['time'][:]
    print('times: ')
    print time1
    print time2
    nt = np.minimum(len(time1), len(time2))
    time1 = time1[:nt]
    time2 = time2[:nt]
    if len(time1) != len(time2):
        time1 = time1[:nt]
        time2 = time2[:nt]
    if time1.any() != time2.any():
        print'problem with times'
        sys.exit()

    r1 = file1.groups['stats'].variables['r'][:]
    r2 = file2.groups['stats'].variables['r'][:]
    ri1 = file1.groups['stats'].variables['ri'][:]
    ri2 = file2.groups['stats'].variables['ri'][:]

    try:
        krange1 = file1.groups['dimensions'].variables['krange'][:]
        krange2 = file2.groups['dimensions'].variables['krange'][:]
    except:
        krange1 = np.arange(kmax)
        krange2 = np.arange(kmax)
    print ''
    print 'kranges:'
    print krange1
    print krange2

    if dz1 > dz2:
        print 'dz1 > dz2'
        dz12 = np.double(dz1) / dz2
        kmax_ = np.int(np.minimum(np.int(np.round(kmax / dz12)), len(krange2)/dz12))
        krange1 = krange1[:kmax_]
        krange2 = krange2[0::np.int(dz12)]
    elif dz1 < dz2:
        print 'dz1 < dz2'
        dz12 = np.double(dz2) / dz1
        kmax_ = np.int(np.round(kmax / dz12))
        krange1 = krange1[0::2]
        krange2 = krange2[:kmax_]
    else:
        dz12 = 1.
        kmax_ = kmax

    print('')
    print 'dz: ', dz1, dz2, dz12
    print 'kmax: ', kmax, kmax_
    print krange1
    print krange2
    print 'zranges:'
    print krange1*dz1
    print krange2*dz2

    var_list = ['w', 'v_rad', 's']
    ncol = len(var_list)
    rmax = 8e3
    irmax1 = np.where(r1 == rmax)[0]
    irmax2 = np.where(r2 == rmax)[0]
    # irmax1 = -1
    # irmax2 = -1
    print ''
    print r1[-1], r2[-1]
    print 'irmax: ', irmax1, irmax2
    print 'rmax', r1[irmax1], r2[irmax2]
    print ''



    for k0 in range(kmax_):
        k1 = krange1[k0]
        k2 = krange2[k0]
        print('z1, z2: ', k1*dz1, k2*dz2)
        fig_name = 'radial_average_z' + str(k1*dz1) + '.png'
        fig, axes = plt.subplots(1, ncol, sharey='none', figsize=(7 * ncol, 5))
        for i, ax in enumerate(axes):
            var1 = grp_stats1[var_list[i]][:, :, :]
            var2 = grp_stats2[var_list[i]][:, :, :]
            if var_list[i] == 'w':
               ax.set_ylim(-6,np.maximum(np.amax(var1[:,:,k0]),np.amax(var2[:,:,k0])))

            if every_second == True:
                for it, t0 in enumerate(time1[1::2]):
                    # print('- t='+str(t0))
                    count_color = 2 * np.double(it) / len(time1)
                    if it == 0:
                        ax.plot(r1[:irmax1], var1[2*it+1, :irmax1, k1], color=cm.copper(count_color), linewidth=3,
                                label='t=' + str(t0)+', dx='+str(dx1))
                    else:
                        ax.plot(r1[:irmax1], var1[2*it+1, :irmax1, k1], color=cm.copper(count_color), linewidth=3,
                                label='t=' + str(t0))
                for it, t0 in enumerate(time1[1::2]):
                    #print('t=' + str(t0))
                    count_color = 2 * np.double(it) / len(time1)
                    if it == 0:
                        ax.plot(r2[:irmax2], var2[2*it+1, :irmax2, k2], '-', color=cm.jet(count_color), linewidth=3,
                                label='dx='+str(dx2))
                    else:
                        # ax.plot(r2[:irmax2], )
                        ax.plot(r2[:irmax2], var2[2*it+1, :irmax2, k2], '-', color=cm.jet(count_color), linewidth=2,
                                label='dx='+str(dx2))
            else:
                for it, t0 in enumerate(time1):
                    print('t=' + str(t0))
                    count_color = np.double(it) / len(time1)
                    if it == 0:
                        ax.plot(r1[:irmax1], var1[it, :irmax1, k1], color=cm.copper(count_color), linewidth=3,
                                label='t=' + str(t0) + ', dx=' + str(dx1))
                    else:
                        ax.plot(r1[:irmax1], var1[it, :irmax1, k1], color=cm.copper(count_color), linewidth=3,
                                label='t=' + str(t0))
                for it, t0 in enumerate(time1):
                    print('t=' + str(t0))
                    count_color = np.double(it) / len(time1)
                    if it == 0:
                        ax.plot(r2[:irmax2], var2[it, :irmax2, k2], '-', color=cm.jet(count_color), linewidth=2,
                                label='dx=' + str(dx2))
                    else:
                        ax.plot(r2[:irmax2], var2[it, :irmax2, k2], '-', color=cm.jet(count_color), linewidth=2,
                                label='dx=' + str(dx2))
            ax.set_title(var_list[i])
            ax.set_xlabel('radius r  [m]')
            ax.set_ylabel(var_list[i])
        axes[2].legend(loc='upper center', bbox_to_anchor=(1.15, 0.8),
                       fancybox=True, ncol=2, fontsize=8)
        # plt.tight_layout()
        plt.subplots_adjust(bottom=0.12, right=.9, left=0.04, top=0.9, wspace=0.15)
        fig.suptitle('Radially averaged variables   (k='+str(k0)+')')
        fig.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)

    file1.close()
    file2.close()

    return


# _______________________________
# _______________________________
def set_input_parameters(args):
    print ''' setting parameters '''
    global path1, path2
    # global path_fields1, path_fields2
    global path_out_data, path_out_figs
    path_root = args.path_root
    path1 = os.path.join(path_root, args.path1)
    path2 = os.path.join(path_root, args.path2)
    # path_fields1 = os.path.join(path1, 'fields')
    # path_fields2 = os.path.join(path1, 'fields')

    path_out_data = os.path.join(path_root, args.path_out)
    if not os.path.exists(path_out_data):
        os.mkdir(path_out_data)
    path_out_figs = os.path.join(path_root, args.path_out)
    if not os.path.exists(path_out_figs):
        os.mkdir(path_out_figs)
    print ''
    print 'paths:'
    print 'path 1: ' + path1
    print 'path 2: ' + path2
    print ''
    print 'path figs: ' + path_out_figs
    print ''

    global case_name
    case_name = args.casename
    nml1 = simplejson.loads(open(os.path.join(path1, case_name + '.in')).read())
    nml2 = simplejson.loads(open(os.path.join(path2, case_name + '.in')).read())
    global nx1, nx2, dx1_nml, dx2_nml
    nx1 = np.ndarray(3, dtype=np.int)
    nx2 = np.ndarray(3, dtype=np.int)
    dx1_nml = np.ndarray(3, dtype=np.int)
    dx2_nml = np.ndarray(3, dtype=np.int)
    nx1[0] = nml1['grid']['nx']
    nx1[1] = nml1['grid']['ny']
    nx1[2] = nml1['grid']['nz']
    nx2[0] = nml2['grid']['nx']
    nx2[1] = nml2['grid']['ny']
    nx2[2] = nml2['grid']['nz']
    dx1_nml[0] = nml1['grid']['dx']
    dx1_nml[1] = nml1['grid']['dy']
    dx1_nml[2] = nml1['grid']['dz']
    dx2_nml[0] = nml2['grid']['dx']
    dx2_nml[1] = nml2['grid']['dy']
    dx2_nml[2] = nml2['grid']['dz']
    gw = nml1['grid']['gw']


    global ic_arr1, jc_arr1, ic_arr2, jc_arr2
    try:
        print('(ic,jc) from nml')
        ic1 = nml1['init']['ic']
        jc1 = nml1['init']['jc']
        ic2 = nml2['init']['ic']
        jc2 = nml2['init']['jc']
        if ic1 != ic2 or jc1 != jc2:
            print('Problem: different geometries')
            sys.exit()
        else:
            ic = ic1
            jc = jc1
            ic_arr = [ic]
            jc_arr = [jc]
    except:
        print('(ic,jc) NOT from nml')
        if case_name == 'ColdPoolDry_single_3D':
            ic = np.int(nx1/2)
            jc = np.int(ny1/2)
            ic_arr1 = [ic]
            jc_arr1 = [jc]
            ic = np.int(nx2/2)
            jc = np.int(ny2/2)
            ic_arr2 = [ic]
            jc_arr2 = [jc]
        else:
            print('ic, jc not defined')
    global kmax
    if args.kmax:
        kmax = np.int(args.kmax)
    else:
        kmax = nx1[2]

    global tmin, tmax
    if args.tmin:
        tmin = np.int(args.tmin)
    else:
        tmin = 100
    if args.tmax:
        tmax = np.int(args.tmax)
    else:
        tmax = 100

    print('')
    print('kmax ', kmax, 'nz1 ', nx1[2])
    print('')

    return

# _______________________________

# def define_geometry(nml):
#     a = nml['grid']['nx']
#     '''--- define geometry ---'''
#     global rstar
#     if case_name == 'ColdPoolDry_double_2D':
#         rstar = 5000.0  # half of the width of initial cold-pools [m]
#         irstar = np.int(np.round(rstar / dx))
#         # zstar = nml['init']['h']
#         isep = 4 * irstar
#         ic1 = np.int(nx / 3)
#         ic2 = ic1 + isep
#         jc1 = np.int(ny / 2)
#         jc2 = jc1
#         ic_arr = [ic1, ic2]
#         jc_arr = [jc1, jc2]
#     elif case_name == 'ColdPoolDry_single_3D':
#         rstar = nml['init']['r']
#         # irstar = np.int(np.round(rstar / dx))
#         # zstar = nml['init']['h']
#         dTh = nml['init']['dTh']
#         ic = np.int(nx / 2)
#         jc = np.int(ny / 2)
#         # xc = Gr.x_half[ic + Gr.dims.gw]  # center of cold-pool
#         # yc = Gr.y_half[jc + Gr.dims.gw]  # center of cold-pool
#         ic_arr = [ic]
#         jc_arr = [jc]
#     elif case_name == 'ColdPoolDry_double_3D':
#         try:
#             rstar = nml['init']['r']
#         except:
#             rstar = 5000.0  # half of the width of initial cold-pools [m]
#         irstar = np.int(np.round(rstar / dx))
#         # zstar = nml['init']['h']
#         isep = 4 * irstar
#         jsep = 0
#         ic1 = np.int(np.round((nx + 2 * gw) / 3)) - gw
#         jc1 = np.int(np.round((ny + 2 * gw) / 2)) - gw
#         ic2 = ic1 + isep
#         jc2 = jc1 + jsep
#         ic_arr = [ic1, ic2]
#         jc_arr = [jc1, jc2]
#     elif case_name == 'ColdPoolDry_triple_3D':
#         try:
#             rstar = nml['init']['r']
#         except:
#             rstar = 5000.0  # half of the width of initial cold-pools [m]
#         irstar = np.int(np.round(rstar / dx))
#         d = np.int(np.round(ny / 2))
#         dhalf = np.int(np.round(ny / 4))
#         a = np.int(np.round(d * np.sin(60.0 / 360.0 * 2 * np.pi)))  # sin(60 degree) = np.sqrt(3)/2
#         ic1 = np.int(np.round(a / 2))  # + gw
#         ic2 = ic1
#         ic3 = ic1 + np.int(np.round(a))
#         jc1 = np.int(np.round(d / 2))  # + gw
#         jc2 = jc1 + d
#         jc3 = jc1 + np.int(np.round(d / 2))
#         ic_arr = [ic1, ic2, ic3]
#         jc_arr = [jc1, jc2, jc3]
#
#         isep = dhalf
#
#     return ic_arr, jc_arr

# _______________________________

if __name__ == '__main__':
    main()
