import numpy as np
import matplotlib.pyplot as plt
import netCDF4 as nc
import argparse
import json as simplejson
import os
import matplotlib.patches as mpatches

execfile('settings.py')

label_size = 15
plt.rcParams['xtick.labelsize'] = label_size
plt.rcParams['ytick.labelsize'] = label_size
plt.rcParams['lines.markersize'] = 2
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['legend.fontsize'] = 8
# plt.rcParams["legend.edgecolor"] = 'w'
plt.rcParams['axes.labelsize'] = 18
# plt.rcParams['xtick.direction']='out'
# plt.rcParams['ytick.direction']='out'
# plt.rcParams['figure.titlesize'] = 35
plt.rcParams['text.usetex'] = 'true'



def main():
    path_single = '/nbi/ac/conv4/rawdata/ColdPools_PyCLES/3D_sfc_fluxes_off/single_3D/run5_PE_scaling_dx100m'
    path_single_dx50 = '/nbi/ac/conv4/rawdata/ColdPools_PyCLES/3D_sfc_fluxes_off/single_3D/run6_PE_scaling_dx50m'
    path_double = '/nbi/ac/coag/rawdata/ColdPools_PyCLES/3D_sfc_fluxes_off/double_3D'
    path_triple = '/nbi/ac/cond2/meyerbe/ColdPools/3D_sfc_fluxes_off/triple_3D/'
    case_name_single = 'ColdPoolDry_single_3D'
    case_name_double = 'ColdPoolDry_double_3D'
    case_name_triple = 'ColdPoolDry_triple_3D'

    # path_out_figs = '/nbi/ac/cond1/meyerbe/paper_CP_single/'
    path_out_figs = '/nbi/ac/cond1/meyerbe/paper_CP/'
    # path_out_figs = '/nbi/home/meyerbe/paper_CP/'
    if not os.path.exists(path_out_figs):
        os.mkdir(path_out_figs)
    print('path figs: ' + path_out_figs)
    print('')

    dTh = 5
    zstar = 1000
    rstar = 1100
    print('zstar: ' + str(zstar))
    print('rstar: ' + str(rstar))
    print('')
    if rstar == 1100:
        d_range = [10, 12, 15]
        t_ini = [600, 600, 600]
        t_2CP = [1100, 1500, 2400]
        t_3CP = [1500, 2200, 3300]
        t_final = [2400, 3100, 4200]
    elif rstar == 2000:
        d_range = [10, 15, 20]
        t_ini = [400, 400, 400]
        t_2CP = [600, 800, 2200]
        t_3CP = [800, 1100, 3200]
        t_final = [1800, 2500, 3500]
    id_list_s = ['dTh' + str(dTh) + '_z' + str(zstar) + '_r' + str(rstar)]
    id_list_d = []
    id_list_t = []
    for dstar in d_range:
        # id_list_d.append('dTh'+str(dTh)+'_z'+str(zstar)+'_r'+str(rstar)+'_d'+str(dstar) + 'km' + '_nx480')
        id_list_d.append('dTh'+str(dTh)+'_z'+str(zstar)+'_r'+str(rstar)+'_d'+str(dstar) + 'km')
        id_list_t.append('dTh'+str(dTh)+'_z'+str(zstar)+'_r'+str(rstar)+'_d'+str(dstar) + 'km')
    print('ID-list: ', id_list_t)
    print('')

    define_geometry(case_name_single, case_name_double, case_name_triple,
                    path_single, path_double, path_triple,
                    id_list_s, id_list_d, id_list_t)

    ''' determine max. height '''
    zmax = 5000.
    kmax = np.int(zmax / dx[2])
    print('zmax: ' + str(zmax))
    print('kmax: ' + str(kmax))
    print('')

    ''' determine time range '''
    global tmin, tmax
    tmin = np.int(0)
    tmax = np.int(np.amax(t_final))  # bcs. of tracer statistics
    times = np.arange(tmin, tmax + dt_fields, dt_fields)
    nt = len(times)
    print('d=' + str(d_range[0]) + ': ' + str(t_ini[0]) + ', ' + str(t_2CP[0]) + ', ' + str(t_3CP[0]) + ', ' + str(
        t_final[0]))
    print('d=' + str(d_range[1]) + ': ' + str(t_ini[1]) + ', ' + str(t_2CP[1]) + ', ' + str(t_3CP[1]) + ', ' + str(
        t_final[1]))
    print('d=' + str(d_range[2]) + ': ' + str(t_ini[2]) + ', ' + str(t_2CP[2]) + ', ' + str(t_3CP[2]) + ', ' + str(
        t_final[2]))
    print('tmin: ' + str(tmin))
    print('tmax: ' + str(tmax))
    print('times: ' + str(times))
    print('nt  : ' + str(nt))
    print('')


    ''' determine sampling subdomain '''
    print('define sampling domain')
    # for single CP: search maximum within circle of radius CP has at 2-CP / 3-CP collision time
    # single: from tracer statistics
    k0 = 0
    fullpath_in = os.path.join(path_single, id_list_s[0], 'tracer_k' + str(k0), 'output')
    n_tracers = get_number_tracers(fullpath_in)
    n_cps = get_number_cps(fullpath_in)
    dist_av = np.zeros((nt))
    for it, t0 in enumerate(times):
        cp_id = 2
        dist_av[it] = get_radius(fullpath_in, it, cp_id, n_tracers, n_cps)
    r_av = dist_av * dx[0]
    rad_1CP_ini = np.empty(3)
    rad_2CP_ini = np.empty(3)
    rad_3CP_ini = np.empty(3)
    rad_3CP_end = np.empty(3)
    delta_s = 6.e2
    for d in range(len(d_range)):
        rad_1CP_ini[d] = r_av[np.int(t_ini[d] / dt_fields)]
        rad_2CP_ini[d] = r_av[np.int(t_2CP[d] / dt_fields)]
        rad_3CP_ini[d] = r_av[np.int(t_3CP[d] / dt_fields)]
        rad_3CP_end[d] = r_av[np.int(t_final[d] / dt_fields)]
    [xs, ys] = nx_s[:2] * .5
    # double
    delta_d = np.asarray([1.e3, 8.e3] / dx[0])
    # triple
    delta_t = np.int(2.e3 / dx[0])

    # plotting limits
    if rstar == 1100:
        lim_single = [50, 50, 20]
        # # for large domains
        # lim_double = [[100, 200], [100, 250], [100, 220]]
        # for small domains
        lim_double = [[60, 120], [80, 100], [80, 100]]
        lim_triple = [100, 200, 280]
    elif rstar == 2000:
        lim_single = [80, 30, 60]
        lim_double = [[100, 280], [80, 280], [80, 220]]
        lim_triple = [200, 250, 250]

    # plot_CPs_at_times(xs, ys, delta_s, delta_d, delta_t, lim_single, lim_double, lim_triple,
    #                   d_range, t_ini, t_2CP, t_3CP, t_final,
    #                   rad_1CP_ini, rad_2CP_ini, rad_3CP_ini, rad_3CP_end,
    #                   id_list_s, id_list_d, id_list_t,
    #                   path_single, path_double, path_triple, path_out_figs)
    print('')





    ''' (A) plot from local (unaveraged) min / max in subdomains'''
    ''' compute min/max values in subdomains '''
    # Subdomains:
    # - single CP: circle
    # - double CP collision: rectangles along collision line
    # - triple CP collision: square around collision point

    path_out = os.path.join(path_single, id_list_s[0], 'data_analysis')
    filename = 'minmax_subdomains_noaverage.nc'
    # w_min, w_max, th_min, th_max, s_min, s_max, z, z_half = \
    #    compute_subdomains_max_single(path_single, id_list_s[0], case_name_single,
    #                                   delta_s,
    #                                   kmax, times, nt,
    #                                   t_ini[0], t_2CP, t_3CP, t_final, r_av, d_range, path_out_figs)
    # dump_minmax_file(w_min, w_max, th_min, th_max, s_min, s_max,
    #                 z, z_half, kmax, times, filename, path_out)
    # for d, dstar in enumerate(d_range):
    #     w_min_d, w_max_d, th_min_d, th_max_d, s_min_d, s_max_d, z, z_half \
    #         = compute_subdomains_max_double(path_double, id_list_d[d], case_name_double,
    #                                         d, dstar, rstar,
    #                                         r_av, delta_d,
    #                                         times, nt, t_2CP[d], t_3CP[d],
    #                                         kmax, path_out_figs)
    #     path_out = os.path.join(path_double, id_list_d[d], 'data_analysis')
    #     if not os.path.exists(path_out):
    #         os.mkdir(path_out)
    #     dump_minmax_file(w_min_d, w_max_d, th_min_d, th_max_d, s_min_d, s_max_d,
    #                      z, z_half, kmax, times, filename, path_out)
    #
    #     w_min_t, w_max_t, th_min_t, th_max_t, s_min_t, s_max_t, z, z_half \
    #         = compute_subdomains_max_triple(path_triple, id_list_t[d], case_name_triple,
    #                                         d, dstar,
    #                                         times, nt, t_3CP[d], t_final[d], delta_t,
    #                                         kmax, path_out_figs)
    #     path_out = os.path.join(path_triple, id_list_t[d], 'data_analysis')
    #     if not os.path.exists(path_out):
    #         os.mkdir(path_out)
    #     dump_minmax_file(w_min_t, w_max_t, th_min_t, th_max_t, s_min_t, s_max_t, z, z_half, kmax, times, filename, path_out)

    # # plot min/max in each subdomain for all times
    # #     fig_name = 'collisions_minmax_alltimes_subdomain_unaveraged_rstar' + str(rstar) + '_d' + str(dstar) + 'km.png'
    # plot_minmax_timeseries_subdomains(rstar, d_range, id_list_s, id_list_d, id_list_t,
    #                                   t_2CP, t_3CP, t_final,
    #                                   path_single, path_double, path_triple,
    #                                   filename, path_out_figs)

    # print(path_double)
    # # plot min/max in each subdomain for time windows
    # #     fig_name = 'collisions_minmax_profiles_subdomain_unaveraged_rstar' + str(rstar) + '.png'
    # plot_minmax_timewindows_subdomain(rstar, d_range, id_list_s, id_list_d, id_list_t,
    #                             t_ini, t_2CP, t_3CP, t_final,
    #                             path_single, path_double, path_triple,
    #                             filename, path_out_figs)



    ''' (B) plot from local (unaveraged) min / max in total domain'''
    filename = 'minmax_domain_noaverage.nc'
    ''' compute domain min/max values '''
    # w_min_s, w_max_s, th_min_s, th_max_s, s_min_s, s_max_s, z, z_half \
    #     = compute_domain_max(path_single, id_list_s[0], case_name_single, kmax, times, nt)
    # path_out = os.path.join(path_single, id_list_s[0], 'data_analysis')
    # dump_minmax_file(w_min_s, w_max_s, th_min_s, th_max_s, s_min_s, s_max_s, z, z_half, kmax, times, filename, path_out)
    # # w_min_s, w_max_s, th_min_s, th_max_s, z, z_half \
    # #         = compute_domain_max(path_single_dx50, id_list_s[0], case_name_single, kmax, times, nt)
    # # path_out = os.path.join(path_single_dx50, id_list_s[0], 'data_analysis')
    # # dump_minmax_file(w_min_s, w_max_s, th_min_s, th_max_s, z, z_half, kmax, times, filename, path_out)
    # for d, dstar in enumerate(d_range):
    #     w_min_d, w_max_d, th_min_d, th_max_d, s_min_d, s_max_d, z, z_half \
    #         = compute_domain_max(path_double, id_list_d[d], case_name_double, kmax, times, nt)
    #     path_out = os.path.join(path_double, id_list_d[d], 'data_analysis')
    #     if not os.path.exists(path_out):
    #         os.mkdir(path_out)
    #     dump_minmax_file(w_min_d, w_max_d, th_min_d, th_max_d, s_min_d, s_max_d, z, z_half, kmax, times, filename, path_out)
    #     path_out = os.path.join(path_triple, id_list_t[d], 'data_analysis')
    #     if not os.path.exists(path_out):
    #         os.mkdir(path_out)
    #     w_min_t, w_max_t, th_min_t, th_max_t, s_min_t, s_max_t, z, z_half \
    #         = compute_domain_max(path_triple, id_list_t[d], case_name_triple, kmax, times, nt)
    #     dump_minmax_file(w_min_t, w_max_t, th_min_t, th_max_t, s_min_t, s_max_t, z, z_half, kmax, times, filename, path_out)

    # path = os.path.join(path_single, id_list_s[0])
    # compute_CP_height(zstar, path, filename)
    # for d, dstar in enumerate(d_range):
    #     path = os.path.join(path_double, id_list_d[d])
    #     compute_CP_height(zstar, path, filename)
    #     path = os.path.join(path_triple, id_list_t[d])
    #     compute_CP_height(zstar, path, filename)

    # plot_minmax_timeseries_domain(rstar, d_range, id_list_s, id_list_d, id_list_t,
    #                               t_ini, t_2CP, t_3CP, t_final,
    #                               path_single, path_double, path_triple,
    #                               filename, path_out_figs)

    # plot min/max in each domain for time windows
    plot_minmax_timewindows_domain(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                t_ini, t_2CP, t_3CP, t_final,
                                path_single, path_double, path_triple,
                                filename, path_out_figs)
    plot_minmax_timewindows_domain_ts(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                   t_ini, t_2CP, t_3CP, t_final,
                                   path_single, path_double, path_triple,
                                   filename, path_out_figs)

    # plot separately for all three simulations
    # # fig_name = 'collisions_minmax_timewindows_domain_unaveraged_rstar' + str(rstar) + '_d' + str(dstar) + 'km_w.png'
    # plot_minmax_alltimes_separate(rstar, d_range, id_list_s, id_list_d, id_list_t,
    #                               t_ini, t_2CP, t_3CP, t_final,
    #                               path_single, path_double, path_triple,
    #                               filename, path_out_figs)






    ''' (C) plot from averaged min / max'''
    # - single - azimuthal average
    # - double - average along collision line
    # - triple - average about a few grid points at center

    # fig_name = 'collisions_minmax_profiles_domain.png'
    # zrange = np.arange(nz) * dx[2]
    # fig, axis = plt.subplots(1, 3, figsize=(14, 5))
    # ax0 = axis[0]
    # ax1 = axis[1]
    # for i_id, ID in enumerate(id_list):
    #     al = np.double(i_id + 1) / (ncases + 1)
    #     ax0.plot(ts_max_w[i_id, :nz], zrange, color='b', alpha=al, label='single, ' + ID)
    #     ax1.plot(ts_min_th[i_id, :nz], zrange, color='b', alpha=al, label='single, ' + ID)
    # ax0.legend(loc='upper left', bbox_to_anchor=(-0.1, -0.1),
    #            fancybox=False, shadow=False, ncol=3, fontsize=9)
    # # ax1.legend(loc='upper left', bbox_to_anchor=(0.1, -0.1),
    # #            fancybox=False, shadow=False, ncol=1, fontsize=9)
    # ax0.set_ylabel('height [km]')
    # ax0.set_xlabel('max(w) [m/s]')
    # ax1.set_xlabel(r'min(potential temperature  ) [K]')
    # for ax in axis.flatten():
    #     y_ticks = [np.int(ti * 1e-3) for ti in ax.get_yticks()]
    #     ax.set_yticklabels(y_ticks)
    # plt.subplots_adjust(bottom=0.18, right=.95, left=0.1, top=0.9, hspace=0.4)
    # plt.savefig(os.path.join(path_out_figs, fig_name))
    # plt.close()
    #
    # time_bins = np.ndarray((ncases,3), dtype=np.double)
    # time_bins[0,:] = [1000, 1400, times[-1]]
    # time_bins[1,:] = [4500, 5900, times[-1]]
    # # time_bins[1,:] = [2300, 3200, times[-1]]
    # # time_bins[2,:] = [4500, 5900, times[-1]]
    # time_bins_ = {}
    # time_bins_['d10km'] = [1000, 1400, times[-1]]
    # time_bins_['d15km'] = [2300, 3200, times[-1]]
    # time_bins_['d20km'] = [4500, 5900, times[-1]]
    #
    # fig_name = 'collisions_minmax_profiles.png'
    # zrange = np.arange(nz) * dx[2]
    # fig, axis = plt.subplots(1, 3, figsize=(14, 5))
    # ax0 = axis[0]
    # ax1 = axis[1]
    # for i_id, ID in enumerate(id_list):
    #     print(ID[-5:])
    #     # it_s = np.int(times_array_w[i_id, 0]/dt_fields)
    #     # it_d = np.int(times_array_w[i_id, 1]/dt_fields)
    #     # it_s = np.int(time_bins[i_id, 0]/dt_fields)
    #     # it_d = np.int(time_bins[i_id, 1]/dt_fields)
    #     it_s = np.int(time_bins_[ID[-5:]][0]/dt_fields)
    #     it_d = np.int(time_bins_[ID[-5:]][1]/dt_fields)
    #     # it_t = times_array_w[i_id, 2]
    #     print('it single, double: ', it_s, it_d)
    #     al = np.double(i_id + 1) / (ncases + 1)
    #     aux = np.amax(prof_max_w[i_id, :it_s, :nz], axis=0)
    #     print('', prof_max_w.shape, aux.shape, nz, zrange.shape)
    #     ax0.plot(np.amax(prof_max_w[i_id, :it_s, :nz], axis=0), zrange, color='b', alpha=al, label='single, ' + ID)
    #     # ax0.plot(prof_max_w[i_id, :nz], zrange, '-', color='g', alpha=al, label='double')
    #     # ax0.plot(prof_max_w[i_id, :nz], zrange, '-', color='r', alpha=al, label='triple')
    # #     ax1.plot(prof_min_th[i_id, :nz], zrange, color='b', alpha=al, label='single, ' + ID)
    # #     # ax1.plot(prof_min_th[i_id, :nz], zrange, '-', color='g', alpha=al, label='double')
    # #     # ax1.plot(prof_min_th[i_id, :nz], zrange, '-', color='r', alpha=al, label='triple')
    # # ax0.legend(loc='upper left', bbox_to_anchor=(-0.1, -0.1),
    # #            fancybox=False, shadow=False, ncol=3, fontsize=9)
    # # # ax1.legend(loc='upper left', bbox_to_anchor=(0.1, -0.1),
    # # #            fancybox=False, shadow=False, ncol=1, fontsize=9)
    # ax0.set_ylabel('height [km]')
    # ax0.set_xlabel('max(w) [m/s]')
    # ax1.set_xlabel(r'min(potential temperature  ) [K]')
    # # ax1.set_xlim(250,350)
    # for ax in axis.flatten():
    #     y_ticks = [np.int(ti * 1e-3) for ti in ax.get_yticks()]
    #     ax.set_yticklabels(y_ticks)
    # plt.subplots_adjust(bottom=0.18, right=.95, left=0.1, top=0.9, hspace=0.4)
    # plt.savefig(os.path.join(path_out_figs, fig_name))
    # plt.close()

    return


# --------------------------------------------------------------------
def compute_subdomains_max_triple(path, ID, casename,
                                  d, dstar,
                                  times, nt, t_ini, t_fi, delta_t,
                                  kmax, path_out_figs):
    print('triple: compute max in subdomain')
    # times = [0, ..., t_final+2*dt_fields], len(times)=nt
    w_min = np.zeros((nt, kmax), dtype=np.double)
    w_max = np.zeros((nt, kmax), dtype=np.double)
    th_min = np.ones((nt, kmax), dtype=np.double)
    th_max = np.ones((nt, kmax), dtype=np.double)
    s_min = np.ones((nt, kmax), dtype=np.double)
    s_max = np.ones((nt, kmax), dtype=np.double)

    root = nc.Dataset(os.path.join(path, ID, 'stats', 'Stats.' + casename + '.nc'))
    zrange = root.groups['profiles'].variables['z'][:kmax]
    zrange_half = root.groups['profiles'].variables['z_half'][:kmax]
    root.close()

    if not os.path.exists(os.path.join(path_out_figs, 'figs_collision_test')):
        os.mkdir(os.path.join(path_out_figs, 'figs_collision_test'))

    # it_ini = np.int(t_ini / dt_fields)
    # it_fi = np.int(t_fi / dt_fields)
    # ic = np.int(nx_t[d][0] * .5)
    # jc = np.int(nx_t[d][1] * .5)
    for it, t0 in enumerate(times):
        print('--- t: ', it, t0)
        fullpath_in = os.path.join(path, ID, 'fields', str(t0) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, :kmax]
        s = root.groups['fields'].variables['s'][:, :, :kmax]
        root.close()

        xt = np.int(nx_t[d][0] * .5 - delta_t * .5)
        yt = np.int(nx_t[d][1] * .5 - delta_t * .5)
        # print('triple: ', xt, yt, delta_t)
        w_min[it, :] = np.amin(np.amin(w[xt:xt + delta_t, yt:yt + delta_t, :], axis=0), axis=0)
        w_max[it, :] = np.amax(np.amax(w[xt:xt + delta_t, yt:yt + delta_t, :], axis=0), axis=0)
        s_min[it, :] = np.amin(np.amin(s[xt:xt + delta_t, yt:yt + delta_t, :], axis=0), axis=0)
        s_max[it, :] = np.amax(np.amax(s[xt:xt + delta_t, yt:yt + delta_t, :], axis=0), axis=0)
        th_min[it, :] = thetas_c(s_min[it, :], 0)
        th_max[it, :] = thetas_c(s_max[it, :], 0)
    return w_min, w_max, th_min, th_max, s_min, s_max, zrange, zrange_half



def compute_subdomains_max_double(path, ID, casename, d, dstar, rstar,
                                  r_av, delta_d,
                                  times, nt, t_ini, t_fi,
                                  kmax, path_out_figs):
    print('double: compute max in subdomain')
    w_min = np.zeros((nt, kmax), dtype=np.double)
    w_max = np.zeros((nt, kmax), dtype=np.double)
    th_min = np.zeros((nt, kmax), dtype=np.double)
    th_max = np.zeros((nt, kmax), dtype=np.double)
    s_min = np.zeros((nt, kmax), dtype=np.double)
    s_max = np.zeros((nt, kmax), dtype=np.double)

    root = nc.Dataset(os.path.join(path, ID, 'stats', 'Stats.' + casename + '.nc'))
    zrange = root.groups['profiles'].variables['z'][:kmax]
    zrange_half = root.groups['profiles'].variables['z_half'][:kmax]
    root.close()

    if not os.path.exists(os.path.join(path_out_figs, 'figs_collision_test')):
        os.mkdir(os.path.join(path_out_figs, 'figs_collision_test'))

    # it_ini = np.int(t_ini / dt_fields)
    # it_fi = np.int(t_fi / dt_fields)
    ic = np.int(nx_d[d][0] * .5)
    jc = np.int(nx_d[d][1] * .5)
    for it, t0 in enumerate(times):
        # it = it_+it_ini
        print('--- t: ', it, t0)
        fullpath_in = os.path.join(path, ID, 'fields', str(t0) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, :kmax]
        s = root.groups['fields'].variables['s'][:, :, :kmax]
        root.close()
        # rad = (delta_s + r_av[np.int(t0 / dt_fields)]) / dx[0]
        # mask = np.ma.masked_less(r_field, rad)
        # w_masked = r_mask.mask[:, :, np.newaxis] * w
        # s_masked = r_mask.mask[:, :, np.newaxis] * s
        rad2 = r_av[it] ** 2
        d2 = (dstar * 1.e3 / 2) ** 2
        # print('double: ', rad2, d2)
        if rad2 >= d2:
            delta_d[1] = np.floor(2.e3 / dx[0]) + 2. / dx[0] * np.sqrt(rad2 - d2)
            [xd, yd] = [ic, jc] - delta_d * .5
            w_min[it, :] = np.amin(np.amin(w[xd:xd + delta_d[0], yd:yd + delta_d[1], :], axis=0), axis=0)
            w_max[it, :] = np.amax(np.amax(w[xd:xd + delta_d[0], yd:yd + delta_d[1], :], axis=0), axis=0)
            s_min[it, :] = np.amin(np.amin(s[xd:xd + delta_d[0], yd:yd + delta_d[1], :], axis=0), axis=0)
            s_max[it, :] = np.amax(np.amax(s[xd:xd + delta_d[0], yd:yd + delta_d[1], :], axis=0), axis=0)
            th_min[it, :] = thetas_c(s_min[it, :], 0)
            th_max[it, :] = thetas_c(s_max[it, :], 0)
        else:
            [xd, yd] = [ic, jc]
            delta_d[1] = 1
            w_min[it, :] = 0
            w_max[it, :] = 0
            s_min[it, :] = np.amin(np.amin(s, axis=0), axis=0)
            s_max[it, :] = np.amax(np.amax(s, axis=0), axis=0)
            th_min[it, :] = thetas_c(s_min[it, :], 0)
            th_max[it, :] = thetas_c(s_max[it, :], 0)
        # print('double: ', ic,jc, xd, yd, delta_d)
        # print('...', np.amax(w_max[it,:]), np.amin(s_min[it,:]), np.amin(th_min[it,:]))

    return w_min, w_max, th_min, th_max, s_min, s_max, zrange, zrange_half


def compute_subdomains_max_single(path, ID, casename,
                                  delta_s, kmax, times, nt,
                                  t_ini, t_2CP, t_3CP, t_final,
                                  r_av, d_range, path_out_figs):
    print('single: compute max in subdomain')
    w_min = np.zeros((nt, kmax), dtype=np.double)
    w_max = np.zeros((nt, kmax), dtype=np.double)
    th_min = np.zeros((nt, kmax), dtype=np.double)
    th_max = np.zeros((nt, kmax), dtype=np.double)
    s_min = np.zeros((nt, kmax), dtype=np.double)
    s_max = np.zeros((nt, kmax), dtype=np.double)

    root = nc.Dataset(os.path.join(path, ID, 'stats', 'Stats.' + casename + '.nc'))
    zrange = root.groups['profiles'].variables['z'][:kmax]
    zrange_half = root.groups['profiles'].variables['z_half'][:kmax]
    root.close()

    if not os.path.exists(os.path.join(path_out_figs, 'figs_collision_test')):
        os.mkdir(os.path.join(path_out_figs, 'figs_collision_test'))

    root = nc.Dataset(os.path.join(path, ID, 'fields_v_rad', 'v_rad.nc'), 'r')
    r_field = root.variables['r_field'][:, :]
    root.close()

    # it_ini = np.int(t_ini/dt_fields)
    for it, t0 in enumerate(times):
        print('--- t: ', it, t0)
        fullpath_in = os.path.join(path, ID, 'fields', str(t0) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, :kmax]
        s = root.groups['fields'].variables['s'][:, :, :kmax]
        root.close()
        rad = (delta_s + r_av[np.int(t0 / dt_fields)]) / dx[0]
        r_mask_l = np.ma.masked_less(r_field, rad)
        r_mask_g = np.ma.masked_greater_equal(r_field, rad)
        w_masked = r_mask_l.mask[:, :, np.newaxis] * w
        s_masked = (1 + 9 * r_mask_g.mask[:, :, np.newaxis]) * s
        w_min[it, :] = np.amin(np.amin(w_masked, axis=0), axis=0)
        w_max[it, :] = np.amax(np.amax(w_masked, axis=0), axis=0)
        s_min[it, :] = np.amin(np.amin(s_masked, axis=0), axis=0)
        s_max[it, :] = np.amax(np.amax(s_masked, axis=0), axis=0)
        th_min[it, :] = thetas_c(s_min[it, :], 0)
        # print('single: smin', s_min.shape, s_min[it,:], th_min[it,5])
        th_max[it, :] = thetas_c(s_max[it, :], 0)

        if it < 100:
            for k0 in [0, 5, 10, 15, 20]:
                w_max_loc_all = np.unravel_index(np.argmax(w[:, :, k0], axis=None), nx_s[:2])
                w_max_loc = np.unravel_index(np.argmax(w_masked[:, :, k0], axis=None), nx_s[:2])
                s_min_loc_all = np.unravel_index(np.argmin(s[:, :, k0], axis=None), nx_s[:2])
                s_min_loc = np.unravel_index(np.argmin(s_masked[:, :, k0], axis=None), nx_s[:2])
                # print('loc: ', w_max_loc, w_max_loc_all, s_min_loc, s_min_loc_all)
                fig_name = 'w_masked_single_t' + str(t0) + '_k' + str(k0) + '.png'
                fig, axis = plt.subplots(2, 5, figsize=(16, 7))
                ax0 = axis[0, 0]
                ax1 = axis[0, 1]
                ax2 = axis[0, 2]
                ax3 = axis[0, 3]
                ax4 = axis[0, 4]
                ax0.set_title('radius')
                cf = ax0.imshow(r_field)
                plt.colorbar(cf, ax=ax0, shrink=0.7)
                ax1.set_title('radius masked (r>=r_av[t])')
                cf = ax1.imshow(r_mask_l)
                plt.colorbar(cf, ax=ax1, shrink=0.7)
                ax2.set_title('mask')
                cf = ax2.imshow(r_mask_l.mask)
                plt.colorbar(cf, ax=ax2, shrink=0.7)
                ax3.set_title('w')
                cf = ax3.imshow(w[:, :, k0])
                plt.colorbar(cf, ax=ax3, shrink=0.7)
                ax3.plot(w_max_loc_all[0], w_max_loc_all[1], 'x', color='k', markersize=10)
                ax3.plot(w_max_loc[0], w_max_loc[1], 'ok', markersize=5)
                ax4.set_title('w*mask')
                cf = ax4.imshow(w_masked[:, :, k0])
                plt.colorbar(cf, ax=ax4, shrink=0.7)

                ax2 = axis[1, 2]
                ax3 = axis[1, 3]
                ax4 = axis[1, 4]
                ax2.set_title('mask g')
                cf = ax2.imshow(r_mask_g.mask)
                plt.colorbar(cf, ax=ax2, shrink=0.7)
                ax3.set_title('s')
                cf = ax3.imshow(s[:, :, k0], vmin=np.amin(s[:, :, k0]), vmax=np.amax(s[:, :, k0]))
                plt.colorbar(cf, ax=ax3, shrink=0.7)
                ax3.plot(s_min_loc_all[0], s_min_loc_all[1], 'kx', markersize=10)
                ax3.plot(s_min_loc[0], s_min_loc[1], 'ok', markersize=5)
                ax4.set_title('s*mask')
                cf = ax4.imshow(s_masked[:, :, k0], vmin=6864, vmax=np.amax(s[:, :, k0]))
                plt.colorbar(cf, ax=ax4, shrink=0.7, extend='max')

                for ax in axis.flat:
                    ax.set_xlim(nx_s[0] * .5 - rad - 10, nx_s[0] * .5 + rad + 10)
                    ax.set_ylim(nx_s[0] * .5 - rad - 10, nx_s[0] * .5 + rad + 10)
                plt.subplots_adjust(bottom=0.1, right=.95, left=0.05, top=0.9, hspace=0.4, wspace=0.2)
                plt.savefig(os.path.join(path_out_figs, 'figs_collision_test', fig_name))
                plt.close()

        del w_masked, s_masked
        del w, s
        # del s_min, s_max

    fig, axis = plt.subplots(1, 3)
    for it, t0 in enumerate(times):
        if t0 > t_ini:
            if t0 <= t_2CP[0]:
                axis[0].plot(w_max[it, :], zrange)
                axis[0].set_title('t=' + str(t_ini) + '-' + str(t_2CP[0]))
            if t0 <= t_2CP[1]:
                axis[1].plot(w_max[it, :], zrange)
                axis[1].set_title('t=' + str(t_ini) + '-' + str(t_2CP[1]))
            if t0 <= t_2CP[2]:
                axis[2].plot(w_max[it, :], zrange)
                axis[2].set_title('t=' + str(t_ini) + '-' + str(t_2CP[2]))
    for ax in axis:
        ax.set_xlim(0, 4)
    plt.savefig(os.path.join(path_out_figs, 'figs_collision_test', 'w_max_test.png'))

    return w_min, w_max, th_min, th_max, s_min, s_max, zrange, zrange_half


# --------------------------------------------------------------------
def compute_domain_max(path, ID, casename, kmax, times, nt):
    w_min = np.ones((nt, kmax), dtype=np.double)
    w_max = np.ones((nt, kmax), dtype=np.double)
    th_min = np.ones((nt, kmax), dtype=np.double)
    th_max = np.ones((nt, kmax), dtype=np.double)
    s_min = np.ones((nt, kmax), dtype=np.double)
    s_max = np.ones((nt, kmax), dtype=np.double)

    root = nc.Dataset(os.path.join(path, ID, 'stats', 'Stats.' + casename + '.nc'))
    zrange = root.groups['profiles'].variables['z'][:kmax]
    zrange_half = root.groups['profiles'].variables['z_half'][:kmax]
    root.close()

    for it, t0 in enumerate(times):
        fullpath_in = os.path.join(path, ID, 'fields', str(t0) + '.nc')
        # print(fullpath_in)
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, :kmax]
        w_min[it, :] = np.amin(np.amin(w, axis=0), axis=0)
        w_max[it, :] = np.amax(np.amax(w, axis=0), axis=0)
        del w
        s = root.groups['fields'].variables['s'][:, :, :kmax]
        s_min[it, :] = np.amin(np.amin(s, axis=0), axis=0)
        s_max[it, :] = np.amax(np.amax(s, axis=0), axis=0)
        del s
        th_min[it, :] = thetas_c(s_min[it, :], 0)
        th_max[it, :] = thetas_c(s_max[it, :], 0)
        root.close()
        # del s_min, s_max
    return w_min, w_max, th_min, th_max, s_min, s_max, zrange, zrange_half


def dump_minmax_file(w_min, w_max, th_min, th_max, s_min, s_max,
                     z, z_half, kmax, times, filename, path_out):
    print('dumping: ', filename, path_out)
    # output for each CP:
    # - min, max (timeseries)
    # - CP height (field; max=timeseries)
    # - (ok) CP rim (field)
    nt = len(times)
    print('create output file: ', os.path.join(path_out, filename))
    # print('time output: ', times)

    rootgrp = nc.Dataset(os.path.join(path_out, filename), 'w', format='NETCDF4')

    ts_grp = rootgrp.createGroup('timeseries')
    ts_grp.createDimension('nt', nt)
    var = ts_grp.createVariable('time', 'f8', ('nt'))
    var.units = "s"
    var[:] = times
    ts_grp.createDimension('nz', kmax)
    var = ts_grp.createVariable('z', 'f8', ('nz'))
    var.units = "m"
    var[:] = z
    var = ts_grp.createVariable('z_half', 'f8', ('nz'))
    var.units = "m"
    var[:] = z_half
    #
    var = ts_grp.createVariable('th_max', 'f8', ('nt', 'nz'))
    var.long_name = 'max potential temperature'
    var.units = "K"
    var[:, :] = th_max[:, :]
    var = ts_grp.createVariable('th_min', 'f8', ('nt', 'nz'))
    var.long_name = 'min potential temperature'
    var.units = "K"
    var[:, :] = th_min[:, :]

    var = ts_grp.createVariable('s_max', 'f8', ('nt', 'nz'))
    var.long_name = 'max entropy'
    var.units = "K"
    var[:, :] = s_max[:, :]
    var = ts_grp.createVariable('s_min', 'f8', ('nt', 'nz'))
    var.long_name = 'min entropy'
    var.units = "K"
    var[:, :] = s_min[:, :]

    var = ts_grp.createVariable('w_max', 'f8', ('nt', 'nz'))
    var.long_name = 'domain max vertical velocity'
    var.units = "m/s"
    var[:, :] = w_max[:, :]
    var = ts_grp.createVariable('w_min', 'f8', ('nt', 'nz'))
    var.long_name = 'domain min vertical velocity'
    var.units = "m/s"
    var[:, :] = w_min[:, :]

    rootgrp.close()
    print('')
    return


def read_in_minmax(kmax, path_out, filename):
    root = nc.Dataset(os.path.join(path_out, filename), 'r')
    time = root.groups['timeseries'].variables['time'][:]
    z = root.groups['timeseries'].variables['z'][:kmax]
    z_half = root.groups['timeseries'].variables['z_half'][:kmax]
    w_max = root.groups['timeseries'].variables['w_max'][:, :kmax]
    th_min = root.groups['timeseries'].variables['th_min'][:, :kmax]
    s_min = root.groups['timeseries'].variables['s_min'][:, :kmax]
    root.close()
    return w_max, th_min, s_min, z, z_half, time


# --------------------------------------------------------------------
def compute_CP_height(zstar, path, filename):
    threshold = 299.5
    kmax = np.int((zstar + 500.) / dx[2])

    fullpath = os.path.join(path, 'data_analysis')
    w_max, th_min, s_min, z, z_half, time = read_in_minmax(kmax, fullpath, filename)
    del w_max, s_min, time
    nt = time.shape[0]
    CP_height = np.zeros((nt), dtype=np.int)
    for it,t0 in enumerate(time):
        k = kmax
        th = th_min[it,k]
        while k>0 and th>threshold:
            k = k-1
        CP_height[it] = k*dx[2]
    rootgrp = nc.Dataset(os.path.join(fullpath, filename), 'r+', format='NETCDF4')
    ts_grp = rootgrp.groups['timeseries']
    var = ts_grp.createVariable('CP_height', 'f8', ('nt'))
    var.long_name = 'cold pool height (theta < 299.5K)'
    var.units = "m"
    var[:] = CP_height[:]
    rootgrp.close()

    return

# ---------------------------- TRACER STATISTICS -----------------------

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


def get_number_cps(fullpath_in):
    # get number of tracers in each CP
    f = open(fullpath_in + '/coldpool_tracer_out.txt', 'r')
    lines = f.readlines()
    cp_number = int(lines[-1].split()[3])
    f.close()

    return cp_number


def get_radius(fullpath_in, t0, cp_id, n_tracers, n_cps):
    f = open(fullpath_in + '/coldpool_tracer_out.txt', 'r')
    # f = open(DIR+EXPID+'/'+child+'/output/irt_tracks_output_pure_sort.txt', 'r')
    lines = f.readlines()
    dist = []

    count = t0 * n_cps * n_tracers + (cp_id - 1) * n_tracers
    # while CP age is 0 and CP ID is cp_id
    timestep = int(lines[count].split()[0])
    cp_ID = int(lines[count].split()[3])
    # print(timestep, cp_ID)
    while (timestep - 1 == t0 and int(lines[count].split()[3]) == cp_id):
        columns = lines[count].split()
        dist.append(float(columns[8]))
        count += 1
        timestep = int(lines[count].split()[0])
    f.close()
    r_av = np.average(dist)

    return r_av


# ----------------------------------------------------------------------
def define_geometry(case_name_single, case_name_double, case_name_triple,
                    path_single, path_double, path_triple, id_list_s, id_list_d, id_list_t):
    print('define geometry')

    global nx_s, nx_d, nx_t
    nx_s = np.empty(3, dtype=np.int)
    nx_d = []
    nx_t = []
    dx_s = np.empty(3, dtype=np.int)
    dx_d = []
    dx_t = []

    nml = simplejson.loads(open(os.path.join(path_single, id_list_s[0], case_name_single + '.in')).read())
    nx_s[0] = nml['grid']['nx']
    nx_s[1] = nml['grid']['ny']
    nx_s[2] = nml['grid']['nz']
    dx_s[0] = nml['grid']['dx']
    dx_s[1] = nml['grid']['dy']
    dx_s[2] = nml['grid']['dz']
    dt_fields_s = np.int(nml['fields_io']['frequency'])
    for d, ID in enumerate(id_list_d):
        nml = simplejson.loads(open(os.path.join(path_double, ID, case_name_double + '.in')).read())
        nx_d.append(np.empty(3, dtype=np.int))
        nx_d[d][0] = nml['grid']['nx']
        nx_d[d][1] = nml['grid']['ny']
        nx_d[d][2] = nml['grid']['nz']
        dx_d.append(np.empty(3, dtype=np.int))
        dx_d[d][0] = nml['grid']['dx']
        dx_d[d][1] = nml['grid']['dy']
        dx_d[d][2] = nml['grid']['dz']
    dt_fields_d = np.int(nml['fields_io']['frequency'])
    for d, ID in enumerate(id_list_t):
        nml = simplejson.loads(open(os.path.join(path_triple, ID, case_name_triple + '.in')).read())
        nx_t.append(np.empty(3, dtype=np.int))
        nx_t[d][0] = nml['grid']['nx']
        nx_t[d][1] = nml['grid']['ny']
        nx_t[d][2] = nml['grid']['nz']
        dx_t.append(np.empty(3, dtype=np.int))
        dx_t[d][0] = nml['grid']['dx']
        dx_t[d][1] = nml['grid']['dy']
        dx_t[d][2] = nml['grid']['dz']
    dt_fields_t = np.int(nml['fields_io']['frequency'])
    print('')
    print('nx single: ' + str(nx_s))
    print('nx double: ' + str(nx_d))
    print('nx triple: ' + str(nx_t))
    print('dx single: ' + str(dx_s))
    print('dx double: ' + str(dx_d))
    print('dx triple: ' + str(dx_t))
    print('dt fields single: ' + str(dt_fields_s))
    print('dt fields double: ' + str(dt_fields_d))
    print('dt fields triple: ' + str(dt_fields_t))
    print('')

    global nx, ny, nz, dx
    nx = nml['grid']['nx']
    ny = nml['grid']['ny']
    nz = nml['grid']['nz']
    dx = np.ndarray(3, dtype=np.int)
    dx[0] = nml['grid']['dx']
    dx[1] = nml['grid']['dy']
    dx[2] = nml['grid']['dz']
    global dt_fields
    dt_fields = np.maximum(dt_fields_d, dt_fields_t)

    return


# ----------------------------------------------------------------------
def plot_CPs_at_times(xs, ys, delta_s, delta_d, delta_t, lim_single, lim_double, lim_triple,
                      d_range, t_ini, t_2CP, t_3CP, t_final,
                      rad_1CP_ini, rad_2CP_ini, rad_3CP_ini, rad_3CP_end,
                      id_list_s, id_list_d, id_list_t,
                      path_single, path_double, path_triple, path_out_figs):
    ''' testing '''
    k0 = 0
    if k0 == 0:
        w_max = 3.
    elif k0 == 10:
        w_max = 1.
    lvls = np.arange(-w_max, w_max, .25)
    # lvls = np.arange(-w_max, w_max, .5)
    # lvls = np.linspace(-4, 4, 10)
    for d, dstar in enumerate(d_range):
        print('plotting CPs: d=' + str(dstar), d)
        print('times: ', t_ini[d], t_2CP[d], t_3CP[d], t_final[d])
        fig_name = 'collisions_subdomains_k' + str(k0) + '_' + id_list_s[0] + '_d' + str(dstar) + 'km.png'
        fig, axis = plt.subplots(3, 4, figsize=(20, 15))
        fullpath_in = os.path.join(path_single, id_list_s[0], 'fields', str(t_ini[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[0, 0].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[0, 0], shrink=0.8)
        fullpath_in = os.path.join(path_single, id_list_s[0], 'fields', str(t_2CP[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[0, 1].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[0, 1], shrink=0.8)
        fullpath_in = os.path.join(path_single, id_list_s[0], 'fields', str(t_3CP[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[0, 2].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[0, 2], shrink=0.8)
        fullpath_in = os.path.join(path_single, id_list_s[0], 'fields', str(t_final[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[0, 3].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[0, 3], shrink=0.8)

        fullpath_in = os.path.join(path_double, id_list_d[d], 'fields', str(t_ini[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[1, 0].contourf(w, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[1, 0], shrink=0.8)
        fullpath_in = os.path.join(path_double, id_list_d[d], 'fields', str(t_2CP[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[1, 1].contourf(w, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[1, 1], shrink=0.8)
        fullpath_in = os.path.join(path_double, id_list_d[d], 'fields', str(t_3CP[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[1, 2].contourf(w, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[1, 2], shrink=0.8)
        fullpath_in = os.path.join(path_double, id_list_d[d], 'fields', str(t_final[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[1, 3].contourf(w, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[1, 3], shrink=0.8)

        fullpath_in = os.path.join(path_triple, id_list_t[d], 'fields', str(t_ini[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[2, 0].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[2, 0], shrink=0.8)
        fullpath_in = os.path.join(path_triple, id_list_t[d], 'fields', str(t_2CP[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[2, 1].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[2, 1], shrink=0.8)
        fullpath_in = os.path.join(path_triple, id_list_t[d], 'fields', str(t_3CP[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[2, 2].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[2, 2], shrink=0.8)
        fullpath_in = os.path.join(path_triple, id_list_t[d], 'fields', str(t_final[d]) + '.nc')
        root = nc.Dataset(fullpath_in, 'r')
        w = root.groups['fields'].variables['w'][:, :, k0]
        root.close()
        cf = axis[2, 3].contourf(w.T, levels=lvls, cmap=cm_bwr, extend='both')
        plt.colorbar(cf, ax=axis[2, 3], shrink=0.8)

        circle0 = plt.Circle((xs, ys), (rad_1CP_ini[d] + delta_s) / dx[0], fill=False, color='k', linewidth=1)
        circle1 = plt.Circle((xs, ys), (rad_2CP_ini[d] + delta_s) / dx[0], fill=False, color='k', linewidth=1)
        circle2 = plt.Circle((xs, ys), (rad_3CP_ini[d] + delta_s) / dx[0], fill=False, color='k', linewidth=1)
        circle3 = plt.Circle((xs, ys), (rad_3CP_end[d] + delta_s) / dx[0], fill=False, color='k', linewidth=1)
        axis[0, 0].add_artist(circle0)
        axis[0, 1].add_artist(circle1)
        axis[0, 2].add_artist(circle2)
        axis[0, 3].add_artist(circle3)
        ic = np.int(nx_d[d][0] * .5)
        jc = np.int(nx_d[d][1] * .5)
        # delta_d[1] = np.floor(1.e3/dx[0]) + 2./dx[0]*np.sqrt(rad_1CP_ini[d]**2 - (dstar*1.e3)**2/4)
        # print('delta_d', rad_1CP_ini[d], (dstar*1.e3)/2, rad_1CP_ini[d]**2, (dstar*1.e3)**2/4, rad_1CP_ini[d]**2 - (dstar*1.e3)**2/4)
        # [xd, yd] = [ic,jc] - delta_d*.5
        # rect_double0 = mpatches.Rectangle((yd, xd), delta_d[1], delta_d[0], linewidth=2, edgecolor='k', facecolor='none')
        rad2 = rad_2CP_ini[d] ** 2
        d2 = (dstar * 1.e3 / 2) ** 2
        if rad2 >= d2:
            delta_d[1] = np.floor(2.e3 / dx[0]) + 2. / dx[0] * np.sqrt(rad_2CP_ini[d] ** 2 - (dstar * 1.e3) ** 2 / 4)
            [xd, yd] = [ic, jc] - delta_d * .5
            rect_double1 = mpatches.Rectangle((yd, xd), delta_d[1], delta_d[0], linewidth=2, edgecolor='k',
                                              facecolor='none')
            axis[1, 1].add_patch(rect_double1)
        delta_d[1] = np.floor(2.e3 / dx[0]) + 2. / dx[0] * np.sqrt(rad_3CP_ini[d] ** 2 - (dstar * 1.e3 / 2) ** 2)
        [xd, yd] = [ic, jc] - delta_d * .5
        rect_double2 = mpatches.Rectangle((yd, xd), delta_d[1], delta_d[0], linewidth=2, edgecolor='k', facecolor='none')
        delta_d[1] = np.floor(2.e3/dx[0]) + 2./dx[0] * np.sqrt(rad_3CP_end[d]**2 - (dstar*1.e3/2)**2)
        [xd, yd] = [ic, jc] - delta_d * .5
        rect_double3 = mpatches.Rectangle((yd, xd), delta_d[1], delta_d[0], linewidth=2, edgecolor='k', facecolor='none')
        axis[1, 2].add_patch(rect_double2)
        axis[1, 3].add_patch(rect_double3)

        [xt, yt] = nx_t[d][:2] * .5 - delta_t * .5
        rect_triple0 = mpatches.Rectangle((xt, yt), delta_t, delta_t, linewidth=1, edgecolor='k', facecolor='none')
        rect_triple1 = mpatches.Rectangle((xt, yt), delta_t, delta_t, linewidth=1, edgecolor='k', facecolor='none')
        rect_triple2 = mpatches.Rectangle((xt, yt), delta_t, delta_t, linewidth=1, edgecolor='k', facecolor='none')
        rect_triple3 = mpatches.Rectangle((xt, yt), delta_t, delta_t, linewidth=1, edgecolor='k', facecolor='none')
        axis[2, 0].add_patch(rect_triple0)
        axis[2, 1].add_patch(rect_triple1)
        axis[2, 2].add_patch(rect_triple2)
        axis[2, 3].add_patch(rect_triple3)

        axis[0, 0].set_title('t=' + str(t_ini[d]) + 's')
        axis[0, 1].set_title('t=' + str(t_2CP[d]) + 's')
        axis[0, 2].set_title('t=' + str(t_3CP[d]) + 's')
        axis[0, 3].set_title('t=' + str(t_final[d]) + 's')
        for ax in axis[0, :].flat:
            ax.set_xlim(lim_single[d], nx_s[0] - lim_single[d])
            ax.set_ylim(lim_single[0], nx_s[1] - lim_single[d])
        for ax in axis[1, :].flat:
            ax.set_xlim(lim_double[d][0], nx_d[d][1] - lim_double[d][0])
            ax.set_ylim(lim_double[d][1], nx_d[d][0] - lim_double[d][1])
        for ax in axis[2, :].flat:
            ax.set_xlim(lim_triple[d], nx_t[d][0] - lim_triple[d])
            ax.set_ylim(lim_triple[d], nx_t[d][1] - lim_triple[d])
        for ax in axis.flat:
            ax.set_aspect('equal')
        plt.subplots_adjust(bottom=0.05, right=.95, left=0.05, top=0.95, hspace=0.1, wspace=0.1)
        print('saving: ', fig_name)
        plt.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)

    return


# ----------------------------------------------------------------------
def plot_minmax_timeseries_domain(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                  t_ini, t_2CP, t_3CP, t_final,
                                  path_single, path_double, path_triple,
                                  filename, path_out_figs):
    print('plot minmax timeseries alltimes domain')
    zmax_plot = 3000.
    kmax_plot = np.int(zmax_plot / dx[2])

    path = os.path.join(path_single, id_list_s[0], 'data_analysis')
    w_max_s, th_min_s, s_min_s, z, z_half, t_s = read_in_minmax(kmax_plot, path, filename)
    for d, dstar in enumerate(d_range):
        # t0 = 0
        # it0 = 0
        t0 = t_ini[d]
        it0 = np.int(t0 / dt_fields)
        # t1 = t_final[d]
        t1 = t_2CP[d]
        it1 = np.int(t1 / dt_fields)

        fig_name = 'collisions_minmax_alltimes_domain_unaveraged_rstar' + str(rstar) + '_d' + str(dstar) + 'km.png'
        print(fig_name)
        # print(path_out_figs)

        path = os.path.join(path_double, id_list_d[d], 'data_analysis')
        # print(path)
        w_max_d, th_min_d, s_min_d, z, z_half, t_d = read_in_minmax(kmax_plot, path, filename)
        path = os.path.join(path_triple, id_list_t[d], 'data_analysis')
        w_max_t, th_min_t, s_min_t, z, z_half, t_t = read_in_minmax(kmax_plot, path, filename)

        fig, axis = plt.subplots(2, 4, figsize=(14, 12), sharey='none')
        # maxw = np.amax(w_max_s)+.1
        # maxw = np.maximum(np.maximum(np.amax(w_max_s), np.amax(w_max_d)), np.amax(w_max_t)) + .1
        maxw = 4.
        # print('time single: ', t_s, w_max_s.shape)
        axis[0, 0].plot(t_s[it0:it1+1], np.amax(w_max_s[it0:it1+1, :], axis=1), 'o-', color=colorlist3[0], label='single CP gust front')
        axis[0, 0].plot(t_d[it0:it1+1], np.amax(w_max_d[it0:it1+1, :], axis=1), 'o-', color=colorlist3[1], label='double CP collision')
        axis[0, 0].plot(t_t[it0:it1+1], np.amax(w_max_t[it0:it1+1, :], axis=1), 'o-', color=colorlist3[2], label='triple CP collision')
        axis[1, 0].plot(t_s[it0:it1+1], np.amin(th_min_s[it0:it1+1, :], axis=1), 'o-', color=colorlist3[0], label='single CP gust front')
        axis[1, 0].plot(t_d[it0:it1+1], np.amin(th_min_d[it0:it1+1, :], axis=1), 'o-', color=colorlist3[1], label='double CP collision')
        axis[1, 0].plot(t_t[it0:it1+1], np.amin(th_min_t[it0:it1+1, :], axis=1), 'o-', color=colorlist3[2], label='triple CP collision')
        for ax in axis[0, 1:].flat:
            ax.plot([0., maxw], [1000, 1000], 'k-', linewidth=0.5)
        for ax in axis[1, 1:].flat:
            ax.plot([298, 300.1], [1000, 1000], 'k-', linewidth=0.5)
        for it_, t0_ in enumerate(range(t0, t_final[d] + dt_fields, dt_fields)):
            it = it_ + it0
            lbl = 't=' + str(t0_) + 's'
            cl = t0_* 1. / t_final[d]

            axis[0, 1].plot(w_max_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 2].plot(w_max_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 3].plot(w_max_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)

            axis[1, 1].plot(th_min_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[1, 2].plot(th_min_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[1, 3].plot(th_min_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)

        axis[0, 1].set_title('single CP')
        axis[0, 2].set_title('double CP, collision line')
        axis[0, 3].set_title('triple CP, collision point')
        for ax in axis[:, 1].flat:
            ax.set_ylabel('Height z  [m]')
            ax.set_yticklabels([np.round(ti * 1e-3, 1) for ti in ax.get_yticks()])
        for ax in axis[0, 1:].flat:
            ax.set_xlabel('max(w)')
            ax.set_xlim(-0.1, maxw)
            ax.set_xticklabels([np.round(ti,1) for ti in ax.get_xticks()])
        for ax in axis[1, 1:].flat:
            ax.set_xlim(298, 300.1)
            ax.set_xlabel('min(theta)')
        axis[0, 0].set_xlabel('time [s]')
        axis[1, 0].set_xlabel('time [s]')
        axis[0, 0].set_ylabel('max(w)')
        axis[1, 0].set_ylabel('min(theta)')
        axis[1, 0].set_ylim(295, 300)

        # for ax in axis[:, 2].flat:
        #     ax.axis('off')

        axis[0, 0].legend(loc=3, fontsize=12)
        axis[0, 3].legend(loc='upper left', bbox_to_anchor=(1, 1.),
                          fancybox=False, shadow=False, ncol=1, fontsize=12)
        plt.subplots_adjust(bottom=0.1, right=.9, left=0.05, top=0.95, hspace=0.2, wspace=0.1)
        plt.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)
    return



def plot_minmax_timeseries_subdomains(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                      t_2CP, t_3CP, t_final,
                                      path_single, path_double, path_triple,
                                      filename, path_out_figs):
    path = os.path.join(path_single, id_list_s[0], 'data_analysis')
    w_max_s, th_min_s, s_min_s, z, z_half, t_s = read_in_minmax(kmax_plot, path, filename)
    for d, dstar in enumerate(d_range):
        fig_name = 'collisions_minmax_alltimes_subdomain_unaveraged_rstar' + str(rstar) + '_d' + str(dstar) + 'km.png'
        zmax_plot = 3000.
        kmax_plot = np.int(zmax_plot / dx[2])

        path = os.path.join(path_double, id_list_d[d], 'data_analysis')
        w_max_d, th_min_d, s_min_d, z, z_half, t_d = read_in_minmax(kmax_plot, path, filename)
        path = os.path.join(path_triple, id_list_t[d], 'data_analysis')
        w_max_t, th_min_t, s_min_t, z, z_half, t_t = read_in_minmax(kmax_plot, path, filename)

        fig, axis = plt.subplots(2, 4, figsize=(14, 12), sharey='none')
        # maxw = np.amax(w_max_s) + .1
        maxw = np.maximum(np.maximum(np.amax(w_max_s), np.amax(w_max_d)), np.amax(w_max_t))+.1
        axis[0, 0].plot(t_s, np.amax(w_max_s[:, :], axis=1), 'o-', color=colorlist3[0], label='single CP')
        axis[0, 0].plot(t_d, np.amax(w_max_d[:, :], axis=1), 'o-', color=colorlist3[1], label='double CP')
        axis[0, 0].plot(t_t, np.amax(w_max_t[:, :], axis=1), 'o-', color=colorlist3[2], label='triple CP')
        axis[1, 0].plot(t_s, np.amin(th_min_s[:, :], axis=1), 'o-', color=colorlist3[0], label='single CP')
        axis[1, 0].plot(t_d, np.amin(th_min_d[:, :], axis=1), 'o-', color=colorlist3[1], label='double CP')
        axis[1, 0].plot(t_t, np.amin(th_min_t[:, :], axis=1), 'o-', color=colorlist3[2], label='triple CP')
        for ax in axis[0, 1:].flat:
            ax.plot([0., maxw], [1000, 1000], 'k-', linewidth=0.5)
        for ax in axis[1, 1:].flat:
            ax.plot([298, 300.1], [1000, 1000], 'k-', linewidth=0.5)
        for it, t0 in enumerate(range(0, t_final[d] + dt_fields, dt_fields)):
            lbl = 't=' + str(t0) + 's'
            cl = t0 * 1. / t_final[d]

            axis[0, 1].plot(w_max_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 2].plot(w_max_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 3].plot(w_max_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)

            axis[1, 1].plot(th_min_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[1, 2].plot(th_min_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[1, 3].plot(th_min_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)

        axis[0, 1].set_title('single CP')
        axis[0, 2].set_title('double CP, collision line')
        axis[0, 3].set_title('triple CP, collision point')
        for ax in axis[:, 1].flat:
            ax.set_ylabel('height z  [m]')
        for ax in axis[0, 1:].flat:
            ax.set_xlabel('max(w)')
            ax.set_xlim(-0.1, maxw)
        for ax in axis[1, 1:].flat:
            ax.set_xlim(298, 300.1)
            ax.set_xlabel('min(theta)')
        axis[0, 0].set_xlabel('time [s]')
        axis[1, 0].set_xlabel('time [s]')
        axis[0, 0].set_ylabel('max(w)')
        axis[1, 0].set_ylabel('min(theta)')
        th_min = np.minimum(np.amin(th_min_s), np.amin(th_min_t))
        th_max = 300.1#np.maximum(np.amin(th_min_s), np.amin(th_min_t))
        axis[1, 0].set_ylim(th_min - .5, th_max)
        axis[1, 0].set_xlim(0, t_final[d])

        # for ax in axis[:, 2].flat:
        #     ax.axis('off')

        axis[0, 0].legend(loc=1, fontsize=12)
        axis[0, 3].legend(loc='upper left', bbox_to_anchor=(1, 1.),
                          fancybox=False, shadow=False, ncol=1, fontsize=12)
        plt.subplots_adjust(bottom=0.1, right=.9, left=0.05, top=0.95, hspace=0.2, wspace=0.1)
        plt.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)
    return



def plot_minmax_timewindows_domain(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                t_ini, t_2CP, t_3CP, t_final,
                                path_single, path_double, path_triple,
                                filename, path_out_figs):
    ''' read in min/max values '''
    print('plotting min / max in domain')
    fig_name = 'collisions_minmax_profiles_domain_unaveraged_rstar' + str(rstar) + '.png'
    zmax_plot = 3000.
    kmax_plot = np.int(zmax_plot / dx[2])
    alpha_list = [1, .5, .2]

    fig, axis = plt.subplots(2, 4, figsize=(14, 10), sharey='all')

    maxw = 4.
    for ax in axis[0, :].flat:
        ax.plot([0., maxw], [1000, 1000], 'k-', linewidth=0.5)
    for ax in axis[1, :].flat:
        ax.plot([290, 310], [1000, 1000], 'k-', linewidth=0.5)
        ax.plot([300, 300], [0, kmax_plot * dx[2]], 'k-', linewidth=0.5)

    path = os.path.join(path_single, id_list_s[0], 'data_analysis')
    w_max_s, th_min_s, s_min_s, z, z_half, t_s = read_in_minmax(kmax_plot, path, filename)
    it_ini = np.int(t_ini[0] / dt_fields)
    lbl_s = 'single CP gust front'

    for d, dstar in enumerate(d_range):
        # al = 1. - d * 1. / (len(d_range))
        al = alpha_list[d]
        al = 1.
        lst = linestyle_list[d]
        if d > 0:
            lbl_s = ''
        else:
            lbl_s = 'single CP gust front'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)
        axis[0, 0].plot(np.amax(w_max_s[it_ini:, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst, label=lbl_s)
        axis[0, 1].plot(np.amax(w_max_s[it_ini:it_2CP, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst, label=lbl_s)
        axis[0, 2].plot(np.amax(w_max_s[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        axis[0, 3].plot(np.amax(w_max_s[it_3CP:it_final, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)

        axis[1, 0].plot(np.amin(th_min_s[it_ini:, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        axis[1, 1].plot(np.amin(th_min_s[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        axis[1, 2].plot(np.amin(th_min_s[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        axis[1, 3].plot(np.amin(th_min_s[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)

    # double
    for d, dstar in enumerate(d_range):
        path = os.path.join(path_double, id_list_d[d], 'data_analysis')
        w_max_d, th_min_d, s_min_d, z, z_half, t_d = read_in_minmax(kmax_plot, path, filename)
        # al = 1. - d * 1. / (len(d_range) + 1)
        al = alpha_list[d]
        al = 1.
        lst = linestyle_list[d]
        if d > 0:
            # lbl_d = '                   ,  d='+str(dstar)+'km'
            lbl_d = 'd='+str(dstar)+'km'
        else:
            lbl_d = 'double CP collision,  d='+str(dstar)+'km'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)

        axis[0, 0].plot(np.amax(w_max_d[it_ini:, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        axis[0, 1].plot(np.amax(w_max_d[it_ini:it_2CP, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        axis[0, 2].plot(np.amax(w_max_d[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        axis[0, 3].plot(np.amax(w_max_d[it_3CP:it_final, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)

        axis[1, 0].plot(np.amin(th_min_d[it_ini:, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        axis[1, 1].plot(np.amin(th_min_d[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        axis[1, 2].plot(np.amin(th_min_d[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        axis[1, 3].plot(np.amin(th_min_d[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)

    # triple
    for d, dstar in enumerate(d_range):
        path = os.path.join(path_triple, id_list_t[d], 'data_analysis')
        w_max_t, th_min_t, s_min_t, z, z_half, t_t = read_in_minmax(kmax_plot, path, filename)
        # al = 1. - d * 1. / (len(d_range) + 1)
        al = alpha_list[d]
        al = 1.
        lst = linestyle_list[d]
        if d > 0:
            # lbl_t = '                   ,  d='+str(dstar)+'km'
            lbl_t = 'd=' + str(dstar) + 'km'
        else:
            lbl_t = 'triple CP collision,  d=' + str(dstar) + 'km'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)

        axis[0, 0].plot(np.amax(w_max_t[it_ini:, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        axis[0, 1].plot(np.amax(w_max_t[it_ini:it_2CP, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        axis[0, 2].plot(np.amax(w_max_t[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        axis[0, 3].plot(np.amax(w_max_t[it_3CP:it_final, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)

        axis[1, 0].plot(np.amin(th_min_t[it_ini:, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        axis[1, 1].plot(np.amin(th_min_t[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        axis[1, 2].plot(np.amin(th_min_t[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        axis[1, 3].plot(np.amin(th_min_t[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)

    for ax in axis[0, :].flat:
        ax.set_xlim(0, maxw)
        ax.set_xticklabels([np.int(i) for i in ax.get_xticks()])
        ax.set_xlabel('max. w  [m/s]')
        for label in ax.xaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
    for ax in axis[1, :].flat:
        ax.set_xlim(298., 300.1)
        ax.set_xticklabels([np.int(i) for i in ax.get_xticks()])
        ax.set_xlabel(r'min. $\theta$ [K]')
        for label in ax.xaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
    for ax in axis[:, 0].flat:
        ax.set_ylabel('Height z  [km]')
        ax.set_yticklabels([np.int(i*1e-3) for i in ax.get_yticks()])
        for label in ax.yaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
    # # axis[0, 0].set_title(r't $>$' + str(t_ini[d]))
    # # axis[0, 1].set_title(str(t_ini[d]) + r'$\leq$ t $<$' + str(t_2CP[d]))
    # # axis[0, 2].set_title(str(t_2CP[d]) + r'$\leq$ t $<$' + str(t_3CP[d]))
    # # axis[0, 3].set_title(str(t_3CP[d]) + r'$\leq$ t $<$' + str(t_final[d]))
    #
    #
    # axis[0, 0].set_title(r't $>$' + str(np.int(t_ini[0] / 60)) + 'min')
    # axis[0, 1].set_title(str(np.int(t_ini[0] / 60)) + 'min' + r'$\leq$ t $<$ t(2CP)')
    # axis[0, 2].set_title(r't(2CP) $\leq$ t $<$ t(3CP)')
    # axis[0, 3].set_title(r't(3CP) $\leq$ t $<$ t(3CP)+15min')
    txt_a = r't $>$' + str(np.int(t_ini[0] / 60)) + 'min'
    txt_b = str(np.int(t_ini[0] / 60)) + 'min ' + r'$\leq$ t $<$ t$_{2CP}$'
    txt_c = r't$_{2CP}$ $\leq$ t $<$ t$_{3CP}$'
    txt_d = r't$_{3CP}$ $\leq$ t $<$ t$_{3CP}$ + 15min'
    txt_a = r't$>$' + str(np.int(t_ini[0] / 60)) + 'min'
    txt_b = str(np.int(t_ini[0] / 60)) + 'min' + r'$\leq$t$<$t$_{2CP}$'
    txt_c = r't$_{2CP}\leq$t$<$t$_{3CP}$'
    txt_d = r't$_{3CP}\leq$t$<$t$_{3CP}$+15min'


    textprops = dict(facecolor='white', alpha=0.9, linewidth=0.)
    txt_x0 = 0.25
    txt_x1 = 298.1
    txt_y = 2700
    ftsize = 18
    axis[0, 0].text(txt_x0, txt_y, 'a) ' + txt_a, fontsize=ftsize, bbox=textprops)
    axis[0, 1].text(txt_x0, txt_y, 'b) ' + txt_b, fontsize=ftsize, bbox=textprops)
    axis[0, 2].text(txt_x0, txt_y, 'c) ' + txt_c, fontsize=ftsize, bbox=textprops)
    axis[0, 3].text(txt_x0, txt_y, 'd) ' + txt_d, fontsize=ftsize, bbox=textprops)
    axis[1, 0].text(txt_x1, txt_y, 'e) ' + txt_a, fontsize=ftsize, bbox=textprops)
    axis[1, 1].text(txt_x1, txt_y, 'f) ' + txt_b, fontsize=ftsize, bbox=textprops)
    axis[1, 2].text(txt_x1, txt_y, 'g) ' + txt_c, fontsize=ftsize, bbox=textprops)
    axis[1, 3].text(txt_x1, txt_y, 'h) ' + txt_d, fontsize=ftsize, bbox=textprops)


    axis[0, -1].legend(loc='upper left', bbox_to_anchor=(0.4, .85),
                      fancybox=False, shadow=False, ncol=1, fontsize=12)
    # # # ax2.legend(loc='upper left', bbox_to_anchor=(0.1, -0.1),
    # # #            fancybox=False, shadow=False, ncol=1, fontsize=9)
    # # # plt.suptitle('min/max for ' + var_name, fontsize=21)
    plt.subplots_adjust(bottom=0.06, right=.9, left=0.05, top=0.95, hspace=0.2, wspace=0.1)
    print('saving: '+ os.path.join(path_out_figs, fig_name))
    plt.savefig(os.path.join(path_out_figs, fig_name))
    plt.savefig(os.path.join(path_out_figs, fig_name[:-4]+'.pdf'))
    plt.close(fig)
    print('')

    return


def plot_minmax_timewindows_domain_ts(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                t_ini, t_2CP, t_3CP, t_final,
                                path_single, path_double, path_triple,
                                filename, path_out_figs):
    ''' read in min/max values '''
    print('plotting min / max in domain')
    print('t_ini', t_ini)
    print('t_2CP', t_2CP)
    print('t_3CP', t_3CP)

    fig_name = 'collisions_minmax_profiles_domain_unaveraged_rstar' + str(rstar) + '_ts.png'
    zmax_plot = 3000.
    kmax_plot = np.int(zmax_plot / dx[2])
    alpha_list = [1, .5, .2]

    fig, axis_ = plt.subplots(2, 4, figsize=(15, 10), sharey='none')
    axx = [.055,.4,.6,.8]
    axy0 = 0.55
    axy1 = 0.05
    axh = .42
    axw = .19
    for ax in axis_.flat:
        ax.axis('off')
    ax00 = fig.add_axes([axx[0],axy0,.28,axh])  # [left, bottom, width, height]
    ax01 = fig.add_axes([axx[1],axy0,axw,axh])  # [left, bottom, width, height]
    ax02 = fig.add_axes([axx[2],axy0,axw,axh])  # [left, bottom, width, height]
    ax03 = fig.add_axes([axx[3],axy0,axw,axh])  # [left, bottom, width, height]
    ax10 = fig.add_axes([axx[0],axy1,.28,axh])  # [left, bottom, width, height]
    ax11 = fig.add_axes([axx[1],axy1,axw,axh])  # [left, bottom, width, height]
    ax12 = fig.add_axes([axx[2],axy1,axw,axh])  # [left, bottom, width, height]
    ax13 = fig.add_axes([axx[3],axy1,axw,axh])  # [left, bottom, width, height]
    for ax in [ax02, ax03, ax12, ax13]:
        for label in ax.yaxis.get_ticklabels()[:]:
            label.set_visible(False)

    maxw = 4.
    for ax in [ax01, ax02, ax03]:
        ax.plot([0., maxw], [1000, 1000], 'k-', linewidth=0.5)
        ax.set_xlim(0, maxw)
        ax.set_xticklabels([np.int(i) for i in ax.get_xticks()])
        ax.set_xlabel('max. w  [m/s]')
        for label in ax.xaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
    for ax in [ax11, ax12, ax13]:
        ax.plot([290, 310], [1000, 1000], 'k-', linewidth=0.5)
        ax.plot([300, 300], [0, kmax_plot * dx[2]], 'k-', linewidth=0.5)
        ax.set_xlim(298., 300.1)
        ax.set_xticklabels([np.int(i) for i in ax.get_xticks()])
        ax.set_xlabel(r'min. $\theta$ [K]')
        for label in ax.xaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
    for ax in [ax12, ax13]:
        ax.xaxis.get_ticklabels()[0].set_visible(False)

    for d, dstar in enumerate(d_range[:1]):
        lst = linestyle_list[d]
        ax00.plot([t_2CP[d],t_2CP[d]],[.5,4.], 'k', linestyle=lst, linewidth=0.5)
        ax00.plot([t_3CP[d],t_3CP[d]],[.5,4.], 'k', linestyle=lst, linewidth=0.5)
        ax10.plot([t_2CP[d],t_2CP[d]],[298,300], 'k', linestyle=lst, linewidth=0.5)
        ax10.plot([t_3CP[d],t_3CP[d]],[298,300], 'k', linestyle=lst, linewidth=0.5)

    # single
    path = os.path.join(path_single, id_list_s[0], 'data_analysis')
    w_max_s, th_min_s, s_min_s, z, z_half, t_s = read_in_minmax(kmax_plot, path, filename)
    it_ini = np.int(t_ini[0] / dt_fields)
    it_final_max = np.int(np.amax(t_final) / dt_fields)
    for d, dstar in enumerate(d_range):
        # al = 1. - d * 1. / (len(d_range))
        al = alpha_list[d]
        al = 1.
        lst = linestyle_list[d]
        if d > 0:
            lbl_s = ''
        else:
            lbl_s = 'single CP gust front'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)
        # axis[0, 0].plot(np.amax(w_max_s[it_ini:, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst, label=lbl_s)
        ax00.plot(t_s[it_ini:it_final_max], np.amax(w_max_s[it_ini:it_final_max,:], axis=1), color=colorlist3[0], alpha=al, linestyle=lst, label=lbl_s)
        ax01.plot(np.amax(w_max_s[it_ini:it_2CP, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst, label=lbl_s)
        ax02.plot(np.amax(w_max_s[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        ax03.plot(np.amax(w_max_s[it_3CP:it_final, :], axis=0), z, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)

        # axis[1, 0].plot(np.amin(th_min_s[it_ini:, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        ax10.plot(t_s[it_ini:it_final_max], np.amin(th_min_s[it_ini:it_final_max,:], axis=1), color=colorlist3[0], alpha=al, linestyle=lst, label=lbl_s)
        ax11.plot(np.amin(th_min_s[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        ax12.plot(np.amin(th_min_s[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)
        ax13.plot(np.amin(th_min_s[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[0], alpha=al, linestyle=lst,label=lbl_s)

    # double
    for d, dstar in enumerate(d_range):
        path = os.path.join(path_double, id_list_d[d], 'data_analysis')
        w_max_d, th_min_d, s_min_d, z, z_half, t_d = read_in_minmax(kmax_plot, path, filename)
        # al = 1. - d * 1. / (len(d_range) + 1)
        al = alpha_list[d]
        al = 1.
        lst = linestyle_list[d]
        if d > 0:
            # lbl_d = '                   ,  d='+str(dstar)+'km'
            lbl_d = 'd='+str(dstar)+'km'
        else:
            lbl_d = 'double CP collision,  d='+str(dstar)+'km'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)

        # axis[0, 0].plot(np.amax(w_max_d[it_ini:, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        ax00.plot(t_d[it_ini:it_final_max], np.amax(w_max_d[it_ini:it_final_max,:], axis=1), color=colorlist3[1], alpha=al, linestyle=lst, label=lbl_d)
        ax01.plot(np.amax(w_max_d[it_ini:it_2CP, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        ax02.plot(np.amax(w_max_d[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        ax03.plot(np.amax(w_max_d[it_3CP:it_final, :], axis=0), z, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)

        # axis[1, 0].plot(np.amin(th_min_d[it_ini:, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        ax10.plot(t_d[it_ini:it_final_max], np.amin(th_min_d[it_ini:it_final_max,:], axis=1), color=colorlist3[1], alpha=al, linestyle=lst, label=lbl_d)
        ax11.plot(np.amin(th_min_d[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        ax12.plot(np.amin(th_min_d[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)
        ax13.plot(np.amin(th_min_d[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[1], linestyle=lst, alpha=al, label=lbl_d)

    # triple
    for d, dstar in enumerate(d_range):
        path = os.path.join(path_triple, id_list_t[d], 'data_analysis')
        w_max_t, th_min_t, s_min_t, z, z_half, t_t = read_in_minmax(kmax_plot, path, filename)
        print('d='+str(d)+', t='+str(t_t), it_ini)
        # al = 1. - d * 1. / (len(d_range) + 1)
        al = alpha_list[d]
        al = 1.
        lst = linestyle_list[d]
        if d > 0:
            # lbl_t = '                   ,  d='+str(dstar)+'km'
            lbl_t = 'd=' + str(dstar) + 'km'
        else:
            lbl_t = 'triple CP collision,  d=' + str(dstar) + 'km'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)

        # axis[0, 0].plot(np.amax(w_max_t[it_ini:, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax00.plot(t_t[it_ini:it_final_max], np.amax(w_max_t[it_ini:it_final_max,:], axis=1), color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax01.plot(np.amax(w_max_t[it_ini:it_2CP, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax02.plot(np.amax(w_max_t[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax03.plot(np.amax(w_max_t[it_3CP:it_final, :], axis=0), z, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)

        # axis[1, 0].plot(np.amin(th_min_t[it_ini:, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax10.plot(t_t[it_ini:it_final_max], np.amin(th_min_t[it_ini:it_final_max,:], axis=1), color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax11.plot(np.amin(th_min_t[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax12.plot(np.amin(th_min_t[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)
        ax13.plot(np.amin(th_min_t[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[2], alpha=al, linestyle=lst, label=lbl_t)

    ax00.set_ylabel('max. w  [m/s]')
    ax00.set_yticklabels([np.int(i) for i in ax00.get_yticks()])
    for label in ax00.yaxis.get_ticklabels()[0::2]:
        label.set_visible(False)
    ax10.set_ylabel(r'min. $\theta$ [K]')
    ax10.set_yticklabels([np.int(i) for i in ax10.get_yticks()])
    for label in ax10.yaxis.get_ticklabels()[1::2]:
        label.set_visible(False)
    for ax in [ax00, ax10]:
        locs = ax.get_xticks()
        locs_ = np.arange(600, np.amax(t_final)+10, 600)
        print('---', locs, locs_)
        ax.set_xticks(locs_)
        ax.set_xticklabels([np.int(i) for i in ax.get_xticks()])
        for label in ax.xaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
    for ax in [ax01, ax11]:
        ax.set_ylabel('Height z  [km]')
        ax.set_yticklabels([np.int(i*1e-3) for i in ax.get_yticks()])
        for label in ax.yaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
        print('limits: ', np.amin(t_ini), np.amax(t_final))
    for ax in [ax00, ax10]:
        ax.set_xlim(np.amin(t_ini), np.amax(t_final))
    ax10.set_xlabel('time [s]')


    # # axis[0, 0].set_title(r't $>$' + str(t_ini[d]))
    # # axis[0, 1].set_title(str(t_ini[d]) + r'$\leq$ t $<$' + str(t_2CP[d]))
    # # axis[0, 2].set_title(str(t_2CP[d]) + r'$\leq$ t $<$' + str(t_3CP[d]))
    # # axis[0, 3].set_title(str(t_3CP[d]) + r'$\leq$ t $<$' + str(t_final[d]))
    # #
    # axis[0, 0].set_title(r't $>$' + str(np.int(t_ini[0] / 60)) + 'min')
    # axis[0, 1].set_title(str(np.int(t_ini[0] / 60)) + 'min' + r'$\leq$ t $<$ t(2CP)')
    # axis[0, 2].set_title(r't(2CP) $\leq$ t $<$ t(3CP)')
    # axis[0, 3].set_title(r't(3CP) $\leq$ t $<$ t(3CP)+15min')
    txt_a = r't$>$' + str(np.int(t_ini[0] / 60)) + 'min'
    txt_b = str(np.int(t_ini[0] / 60)) + 'min' + r'$\leq$t$<$t$_{2CP}$'
    txt_c = r't$_{2CP}\leq$t$<$t$_{3CP}$'
    txt_d = r't$_{3CP}\leq$t$<$t$_{3CP}$+15min'

    textprops = dict(facecolor='white', alpha=0.9, linewidth=0.)
    txt_x0 = 0.25
    txt_x1 = 298.1
    txt_y = 2700
    ftsize = 18
    print('label a', np.amin(t_ini))
    ax00.text(np.amin(t_ini)+dt_fields, 3.8, 'a) ' + txt_a, fontsize=ftsize, bbox=textprops)
    ax01.text(txt_x0, txt_y, 'b) ' + txt_b, fontsize=ftsize, bbox=textprops)
    ax02.text(txt_x0, txt_y, 'c) ' + txt_c, fontsize=ftsize, bbox=textprops)
    ax03.text(txt_x0, txt_y, 'd) ' + txt_d, fontsize=ftsize, bbox=textprops)
    ax10.text(np.amin(t_ini)+dt_fields, 299.8, 'e) ' + txt_a, fontsize=ftsize, bbox=textprops)
    ax11.text(txt_x1, txt_y, 'f) ' + txt_b, fontsize=ftsize, bbox=textprops)
    ax12.text(txt_x1, txt_y, 'g) ' + txt_c, fontsize=ftsize, bbox=textprops)
    ax13.text(txt_x1, txt_y, 'h) ' + txt_d, fontsize=ftsize, bbox=textprops)

    # ax03.legend(loc='upper left', bbox_to_anchor=(0.3, .85), fancybox=False, shadow=False, ncol=1, fontsize=12)
    print('')
    print('', t_3CP[0]*1./(t_final[-1]-t_ini[0]), t_3CP[0], t_final[-1], t_ini[0])
    print('')
    ax10.legend(loc='upper left', bbox_to_anchor=(.25, .5), fancybox=False, shadow=False, ncol=1, fontsize=13)
    # ax00.legend(loc='upper left', bbox_to_anchor=(1.05, .5), fancybox=False, shadow=False, ncol=1, fontsize=12)
    plt.subplots_adjust(bottom=0.06, right=.9, left=0.05, top=0.95, hspace=0.2, wspace=0.1)
    print('saving: ' + os.path.join(path_out_figs, fig_name))
    plt.savefig(os.path.join(path_out_figs, fig_name))
    plt.savefig(os.path.join(path_out_figs, fig_name[:-4]+'.pdf'))
    plt.close(fig)
    print('')
    return



def plot_minmax_timewindows_subdomain(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                t_ini, t_2CP, t_3CP, t_final,
                                path_single, path_double, path_triple,
                                filename, path_out_figs):
    ''' read in min/max values '''
    print('plotting min / max in subdomain')
    fig_name = 'collisions_minmax_profiles_subdomain_unaveraged_rstar' + str(rstar) + '.png'
    zmax_plot = 3000.
    kmax_plot = np.int(zmax_plot / dx[2])
    alpha_list = [1, .5, .2]

    fig, axis = plt.subplots(2, 4, figsize=(14, 12), sharey='all')
    maxw = 4.
    for ax in axis[0, :].flat:
        ax.plot([0., maxw], [1000, 1000], 'k-', linewidth=0.5)
    for ax in axis[1, :].flat:
        ax.plot([290, 310], [1000, 1000], 'k-', linewidth=0.5)
        ax.plot([300, 300], [0, kmax_plot * dx[2]], 'k-', linewidth=0.5)


    path = os.path.join(path_single, id_list_s[0], 'data_analysis')
    w_max_s, th_min_s, s_min_s, z, z_half, t_s = read_in_minmax(kmax_plot, path, filename)
    it_ini = np.int(t_ini[0] / dt_fields)
    it_final = np.int(t_final[0] / dt_fields)
    lbl_s = 'single CP gust front'
    # axis[0, 0].plot(np.amax(w_max_s[it_ini:, :], axis=0), z, color=colorlist3[0], label=lbl_s)
    axis[0, 0].plot(t_s[it_ini:it_final + 1], np.amax(w_max_s[it_ini:it_final + 1, :], axis=1), 'o-', color=colorlist3[0], label=lbl_s)
    axis[1, 0].plot(t_s[it_ini:it_final + 1], np.amin(th_min_s[it_ini:it_final + 1, :], axis=1), 'o-', color=colorlist3[0], label=lbl_s)

    for d, dstar in enumerate(d_range):
        print('.... d: ' + str(dstar))
        # al = 1. - d * 1. / (len(d_range) + 1)
        al = alpha_list[d]
        if d > 0:
            lbl_s = ''
        else:
            lbl_s = 'single CP gust front'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)
        axis[0, 1].plot(np.amax(w_max_s[it_ini:it_2CP, :], axis=0), z, color=colorlist3[0], alpha=al, label=lbl_s)
        axis[0, 2].plot(np.amax(w_max_s[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[0], alpha=al, label=lbl_s)
        axis[0, 3].plot(np.amax(w_max_s[it_3CP:it_final, :], axis=0), z, color=colorlist3[0], alpha=al, label=lbl_s)

        axis[1, 0].plot(np.amin(th_min_s[it_ini:, :], axis=0), z_half, color=colorlist3[0], alpha=al, label=lbl_s)
        axis[1, 1].plot(np.amin(th_min_s[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[0], alpha=al, label=lbl_s)
        axis[1, 2].plot(np.amin(th_min_s[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[0], alpha=al, label=lbl_s)
        axis[1, 3].plot(np.amin(th_min_s[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[0], alpha=al, label=lbl_s)

    # double
    for d, dstar in enumerate(d_range):
        print('.... d: ' + str(dstar))
        path = os.path.join(path_double, id_list_d[d], 'data_analysis')
        print(os.path.join(path, filename))
        w_max_d, th_min_d, s_min_d, z, z_half, t_d = read_in_minmax(kmax_plot, path, filename)
        # al = 1. - d * 1. / (len(d_range) + 1)
        al = alpha_list[d]
        if d > 0:
            # lbl_d = '                   ,  d='+str(dstar)+'km'
            lbl_d = 'd='+str(dstar)+'km'
        else:
            lbl_d = 'double CP collision,  d='+str(dstar)+'km'
        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)

        # axis[0, 0].plot(np.amax(w_max_d[it_ini:, :], axis=0), z, color=colorlist3[1], alpha=al, label=lbl_d)
        axis[0, 0].plot(t_d[it_ini:it_final + 1], np.amax(w_max_d[it_ini:it_final + 1, :], axis=1), 'o-', color=colorlist3[1], label=lbl_d)
        axis[0, 1].plot(np.amax(w_max_d[it_ini:it_2CP, :], axis=0), z, color=colorlist3[1], alpha=al, label=lbl_d)
        axis[0, 2].plot(np.amax(w_max_d[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[1], alpha=al, label=lbl_d)
        axis[0, 3].plot(np.amax(w_max_d[it_3CP:it_final, :], axis=0), z, color=colorlist3[1], alpha=al, label=lbl_d)

        # axis[1, 0].plot(np.amin(th_min_d[it_ini:, :], axis=0), z_half, color=colorlist3[1], alpha=al, label=lbl_d)
        axis[1, 0].plot(t_d[it_ini:it_final + 1], np.amin(th_min_d[it_ini:it_final + 1, :], axis=1), 'o-', color=colorlist3[1], label=lbl_d)
        axis[1, 1].plot(np.amin(th_min_d[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[1], alpha=al, label=lbl_d)
        axis[1, 2].plot(np.amin(th_min_d[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[1], alpha=al, label=lbl_d)
        axis[1, 3].plot(np.amin(th_min_d[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[1], alpha=al, label=lbl_d)


    # triple
    for d, dstar in enumerate(d_range):
        print('.... d: ' + str(dstar))
        path = os.path.join(path_triple, id_list_t[d], 'data_analysis')
        w_max_t, th_min_t, s_min_t, z, z_half, t_t = read_in_minmax(kmax_plot, path, filename)

        # al = 1. - d * 1. / (len(d_range) + 1)
        al = alpha_list[d]
        if d > 0:
            # lbl_t = '                   ,  d='+str(dstar)+'km'
            lbl_t = 'd='+str(dstar)+'km'
        else:
            lbl_t = 'triple CP collision,  d='+str(dstar)+'km'

        it_ini = np.int(t_ini[d] / dt_fields)
        it_2CP = np.int(t_2CP[d] / dt_fields)
        it_3CP = np.int(t_3CP[d] / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)

        # axis[0, 0].plot(np.amax(w_max_t[it_ini:, :], axis=0), z, color=colorlist3[2], alpha=al, label=lbl_t)
        axis[0, 0].plot(t_t[it_ini:it_final + 1], np.amax(w_max_t[it_ini:it_final + 1, :], axis=1), 'o-', color=colorlist3[2], label=lbl_t)
        axis[0, 1].plot(np.amax(w_max_t[it_ini:it_2CP, :], axis=0), z, color=colorlist3[2], alpha=al, label=lbl_t)
        axis[0, 2].plot(np.amax(w_max_t[it_2CP:it_3CP, :], axis=0), z, color=colorlist3[2], alpha=al, label=lbl_t)
        axis[0, 3].plot(np.amax(w_max_t[it_3CP:it_final, :], axis=0), z, color=colorlist3[2], alpha=al, label=lbl_t)

        # axis[1, 0].plot(np.amin(th_min_t[it_ini:, :], axis=0), z_half, color=colorlist3[2], alpha=al, label=lbl_t)
        axis[1, 0].plot(t_t[it_ini:it_final + 1], np.amin(th_min_t[it_ini:it_final + 1, :], axis=1), 'o-', color=colorlist3[2], label=lbl_t)
        axis[1, 1].plot(np.amin(th_min_t[it_ini:it_2CP, :], axis=0), z_half, color=colorlist3[2], alpha=al, label=lbl_t)
        axis[1, 2].plot(np.amin(th_min_t[it_2CP:it_3CP, :], axis=0), z_half, color=colorlist3[2], alpha=al, label=lbl_t)
        axis[1, 3].plot(np.amin(th_min_t[it_3CP:it_final, :], axis=0), z_half, color=colorlist3[2], alpha=al, label=lbl_t)


    for ax in axis[0, :].flat:
        ax.set_xlim(0, 4)
        ax.set_xlabel('max. w  [m/s]')
    for ax in axis[1, :].flat:
        ax.set_xlim(298., 300.1)
        ax.set_xlabel(r'min. $\theta$ [K]')
    for ax in axis[:, 0].flat:
        ax.set_ylabel('Height z  [m]')
        ax.set_yticklabels([np.round(i*1e-3,1) for i in ax.get_yticks()])
    # axis[0, 0].set_title(r't $>$' + str(t_ini[d]))
    # axis[0, 1].set_title(str(t_ini[d]) + r'$\leq$ t $<$' + str(t_2CP[d]))
    # axis[0, 2].set_title(str(t_2CP[d]) + r'$\leq$ t $<$' + str(t_3CP[d]))
    # axis[0, 3].set_title(str(t_3CP[d]) + r'$\leq$ t $<$' + str(t_final[d]))
    axis[0, 0].set_title(r't $>$' + str(np.int(t_ini[0]/60))+'min')
    axis[0, 1].set_title(str(np.int(t_ini[0] / 60)) + 'min' + r'$\leq$ t $<$ t(2CP)')
    axis[0, 2].set_title(r't(2CP) $\leq$ t $<$ t(3CP)')
    axis[0, 3].set_title(r't(3CP) $\leq$ t $<$ t(3CP)+15min')

    axis[0, 0].legend(loc='upper left', bbox_to_anchor=(0.15, .99),
                      fancybox=False, shadow=False, ncol=1, fontsize=12)
    # # # ax2.legend(loc='upper left', bbox_to_anchor=(0.1, -0.1),
    # # #            fancybox=False, shadow=False, ncol=1, fontsize=9)
    # # # plt.suptitle('min/max for ' + var_name, fontsize=21)
    plt.subplots_adjust(bottom=0.1, right=.95, left=0.05, top=0.95, hspace=0.2)
    plt.savefig(os.path.join(path_out_figs, fig_name))
    plt.close(fig)
    return

# ----------------------------------------------------------------------

def plot_minmax_alltimes_separate(rstar, d_range, id_list_s, id_list_d, id_list_t,
                                  t_ini, t_2CP, t_3CP, t_final,
                                  path_single, path_double, path_triple,
                                  filename, path_out_figs):
    print('plot minmax timeseries alltimes domain')
    zmax_plot = 3000.
    kmax_plot = np.int(zmax_plot / dx[2])

    path = os.path.join(path_single, id_list_s[0], 'data_analysis')
    w_max_s, th_min_s, s_min_s, z, z_half, t_s = read_in_minmax(kmax_plot, path, filename)
    # maxw = np.amax(w_max_s)+.1
    # maxw = np.maximum(np.maximum(np.amax(w_max_s), np.amax(w_max_d)), np.amax(w_max_t)) + .1
    maxw = 4.

    for d, dstar in enumerate(d_range):
        t0 = t_ini[d]
        it0 = np.int(t0 / dt_fields)
        it_final = np.int(t_final[d] / dt_fields)

        path = os.path.join(path_double, id_list_d[d], 'data_analysis')
        w_max_d, th_min_d, s_min_d, z, z_half, t_d = read_in_minmax(kmax_plot, path, filename)
        path = os.path.join(path_triple, id_list_t[d], 'data_analysis')
        w_max_t, th_min_t, s_min_t, z, z_half, t_t = read_in_minmax(kmax_plot, path, filename)

        fig_name = 'collisions_minmax_timewindows_domain_unaveraged_rstar' + str(rstar) + '_d' + str(dstar) + 'km_w.png'
        print(fig_name)
        fig, axis = plt.subplots(4, 3, figsize=(11, 14), sharey='row')

        for it_, t0_ in enumerate(range(t0, t_final[d] + dt_fields, dt_fields)):
            it = it_ + it0
            lbl = 't=' + str(t0_) + 's'
            cl = it_ * 1. / (it_final-it0)
            # cl2 = t0_ * 1. / (t_2CP[d]-t0)

            axis[0, 0].plot(w_max_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 1].plot(w_max_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 2].plot(w_max_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)

            if t0_ < t_2CP[d]:
                axis[1, 0].plot(w_max_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[1, 1].plot(w_max_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[1, 2].plot(w_max_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            elif t0_ < t_3CP[d]:
                axis[2, 0].plot(w_max_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[2, 1].plot(w_max_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[2, 2].plot(w_max_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            else:
                axis[3, 0].plot(w_max_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[3, 1].plot(w_max_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[3, 2].plot(w_max_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)

        for ax in axis[:,0].flat:
            ax.set_ylabel('height z  [m]')
        for ax in axis[3,:].flat:
            ax.set_xlabel('max(w) [m/s]')
        plt.suptitle('rstar=' + str(rstar) + ', d=' + str(dstar) + 'km')
        axis[0,0].set_title('single CP')
        axis[0,1].set_title('double CP')
        axis[0,2].set_title('triple CP')
        # axis[0, 0].legend(loc=3, fontsize=12)
        # axis[0, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.), fancybox=False, shadow=False, ncol=1, fontsize=12)
        axis[1, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.5), fancybox=False, shadow=False, ncol=1, fontsize=12)
        axis[2, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.), fancybox=False, shadow=False, ncol=1, fontsize=12)
        axis[3, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.), fancybox=False, shadow=False, ncol=1, fontsize=12)
        plt.subplots_adjust(bottom=0.1, right=.85, left=0.06, top=0.95, hspace=0.2, wspace=0.1)
        plt.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)



        fig_name = 'collisions_minmax_timewindows_domain_unaveraged_rstar' + str(rstar) + '_d' + str(dstar) + 'km_theta.png'
        print(fig_name)
        fig, axis = plt.subplots(4, 3, figsize=(11, 14), sharey='row')

        for it_, t0_ in enumerate(range(t0, t_final[d] + dt_fields, dt_fields)):
            it = it_ + it0
            lbl = 't=' + str(t0_) + 's'
            cl = it_ * 1. / (it_final - it0)
            # cl = t0 * 1. / (t_final[d] - t0)
            # cl2 = t0 * 1. / (t_2CP[d]-t0)

            axis[0, 0].plot(th_min_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 1].plot(th_min_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            axis[0, 2].plot(th_min_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)

            if t0_ < t_2CP[d]:
                axis[1, 0].plot(th_min_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[1, 1].plot(th_min_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[1, 2].plot(th_min_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            elif t0_ < t_3CP[d]:
                axis[2, 0].plot(th_min_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[2, 1].plot(th_min_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[2, 2].plot(th_min_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
            else:
                axis[3, 0].plot(th_min_s[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[3, 1].plot(th_min_d[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
                axis[3, 2].plot(th_min_t[it, :kmax_plot], z[:kmax_plot], color=cm(cl), label=lbl)
        for ax in axis[:,0].flat:
            ax.set_ylabel('height z  [m]')
        for ax in axis[3,:].flat:
            ax.set_xlabel('min(theta) [K]')
        for ax in axis.flat:
            ax.set_xlim(298,300.1)
        plt.suptitle('rstar='+str(rstar)+', d='+str(dstar)+'km')
        axis[0, 0].set_title('single CP')
        axis[0, 1].set_title('double CP')
        axis[0, 2].set_title('triple CP')
        # axis[0, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.), fancybox=False, shadow=False, ncol=1, fontsize=12)
        axis[1, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.5), fancybox=False, shadow=False, ncol=1, fontsize=12)
        axis[2, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.), fancybox=False, shadow=False, ncol=1, fontsize=12)
        axis[3, 2].legend(loc='upper left', bbox_to_anchor=(1, 1.), fancybox=False, shadow=False, ncol=1, fontsize=12)
        plt.subplots_adjust(bottom=0.1, right=.85, left=0.06, top=0.95, hspace=0.2, wspace=0.1)
        plt.savefig(os.path.join(path_out_figs, fig_name))
        plt.close(fig)


    return
# ----------------------------------------------------------------------
def cpm_c(qt):
    cpd = 1004.0
    cpv = 1859.0
    return (1.0 - qt) * cpd + qt * cpv

def thetas_c(s, qt):
    T_tilde = 298.15
    sd_tilde = 6864.8
    sv_tilde = 10513.6
    return T_tilde * np.exp((s - (1.0 - qt) * sd_tilde - qt * sv_tilde) / cpm_c(qt))

# ----------------------------------




if __name__ == '__main__':
    print('')
    main()
