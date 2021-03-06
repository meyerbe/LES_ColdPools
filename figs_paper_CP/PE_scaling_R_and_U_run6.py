import numpy as np
import argparse
import os
import json as simplejson
from scipy import optimize
# from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

execfile('settings.py')
plt.rcParams['xtick.direction']='out'
plt.rcParams['ytick.direction']='out'


def main():
    parser = argparse.ArgumentParser(prog='LES_CP')
    parser.add_argument('--rparams', nargs='+', type=int)
    parser.add_argument("--tmin")
    parser.add_argument("--tmax")
    args = parser.parse_args()

    case_name = 'ColdPoolDry_single_3D'
    path_root = '/nbi/ac/conv4/rawdata/ColdPools_PyCLES/3D_sfc_fluxes_off/single_3D/run6_PE_scaling_dx50m'
    path_out_figs = '/nbi/home/meyerbe/paper_CP'
    global dt_fields
    dt_fields = 100
    print('path figures: ' + path_out_figs)
    print('')

    # reference case: dTh3_z1000_r1000
    dTh_ref = 3
    rstar_ref = 1000
    zstar_ref = 1000
    ID_ref = 'dTh3_z' + str(zstar_ref) + '_r' + str(rstar_ref)
    path_ref = '/nbi/ac/conv4/rawdata/ColdPools_PyCLES/3D_sfc_fluxes_off/single_3D/run3b_dx50m/' + ID_ref

    dTh, z_params, r_params = set_input_parameters(args, path_root, dTh_ref, path_ref, case_name)

    # --------------------------------------
    ''' (A) read in data from tracer output (text-file)'''
    cp_id = 1  # circle ID that is used for statistics

    r_av = np.zeros((n_params, nt))
    r_var = np.zeros((n_params, nt))
    r_sigma = np.zeros((n_params, nt))
    U_rad_av = np.zeros((n_params, nt))
    for istar in range(n_params):
        zstar = z_params[0]
        rstar = r_params[istar]
        if rstar == 1000:
            ID = ID_ref
            fullpath_in = os.path.join(path_ref, 'tracer_k0', 'output')
        else:
            ID = 'dTh'+str(dTh)+'_z'+str(zstar)+'_r'+str(rstar)
            run_id = 'dz2000_run2'
            fullpath_in = os.path.join(path_root, ID+'_'+run_id, 'tracer_k0', 'output')
        print('------- ' + str(istar) + ') ' + ID)
        print(fullpath_in)
        n_tracers = get_number_tracers(fullpath_in)
        n_cps = get_number_cps(fullpath_in)
        print('number of CPs: ', n_cps)
        print('number of tracers per CP: ', n_tracers)
        print('')
        for it,t0 in enumerate(times):
            dist_av, dist_var, U_rad_av[istar, it] = get_radius_vel(fullpath_in, it, cp_id, n_tracers, n_cps)
            r_av[istar,it] = dist_av*dx[0]
            r_var[istar,it] = dist_var*dx[0]**2
            r_sigma[istar,it] = np.sqrt(dist_var*dx[0]**2)
        print('')




    ''' (B) FITTING '''
    global it0
    it0 = 6
    t0 = times[it0]
    itsplit = np.int(1600./dt_fields)

    # # plot timeseries without fitting
    # fig_name = 'R_scaling_no_fits'
    # plot_timeseries(times, r_av, r_sigma, r_params, itsplit, path_out_figs, fig_name)

    # R0 = r_av[istar,it0]
    # print('it0', it0, R0)
    # x = np.log(times[1:]*1./t0)
    # y = np.log(r_av[istar,1:]/R0)
    # [a,m], pcov = optimize.curve_fit(linear_fit, x, y)
    # print('a, m', a, m)
    # # plt.figure()
    # # plt.plot(x, y, '-o')
    # # plt.plot(x, a+m*x, 'k')
    # # plt.show()
    #
    # plt.figure()
    # x1 = np.log(times[1:itsplit] * 1. / t0)
    # y1 = np.log(r_av[istar, 1:itsplit] / R0)
    # [a1, m1], pcov = optimize.curve_fit(linear_fit, x1, y1)
    # print('a1, m1', a1, m1)
    # plt.plot(x1, y1, '-o')
    # plt.plot(x1, a1 + m1 * x1, 'k')
    #
    # x2 = np.log(times[itsplit:] / t0)
    # y2 = np.log(r_av[istar, itsplit:] / R0)
    # [a2, m2], pcov = optimize.curve_fit(linear_fit, x2, y2)
    # print('a2, m2', a2, m2)
    # plt.plot(x2, y2, '-o')
    # plt.plot(x2, a2 + m2 * x2, 'k')
    #
    # x = np.log(times[1:]/t0)
    # plt.plot(x, a2 + m2 * x, 'r')
    # plt.savefig(os.path.join(path_out_figs, 'R_scaling_pow_log_knick_a.png'))



    ''' Plotting '''
    # for istar, rstar in enumerate(r_params):
    #     R0 = r_av[istar,it0]
    #     fig_name = 'R_scaling_pow_log_knick_r' + str(rstar)
    #     print(fig_name)
    #     plot_R_twofits_variance(times, r_av[istar,:], r_var[istar,:], r_sigma[istar,:],
    #                             itsplit, rstar, path_out_figs, fig_name)


    fig_name = 'R_scaling_pow_log_run6'
    plot_run6_fits(times, r_av, r_sigma,
                   r_params, itsplit,
                   path_out_figs, fig_name)


    return

# ----------------------------------------------------------------------
''' (B) FITTING '''
''' (a) fit power law '''
def linear_fit(x, a, m):
    return a+m*x
def powlaw_fit(x, a, m):
    return np.exp(a) * x**m

def powlaw_fit_two(x, a1, m1, a2, m2):
    x0 = 1600./(it0*dt_fields)
    y = np.zeros(shape=x.shape[0])
    for i,xi in enumerate(x):
        if xi<x0:
            y[i] = np.exp(a1) * xi**m1
        else:
            y[i] = np.exp(a2) * xi**m2
    return y
''' (b) logarithmic fit by Romps '''
def log_fit_romps(t, a, b, c):
    return a + b*np.log(1+c*t)
''' compute mean square error '''
def sq_error(y_obs, y_model):
    n = np.shape(y_obs)[0]
    S = 0
    for i,yi in enumerate(y_obs):
        S += (yi-y_model[i])**2
    return S
# ----------------------------------------------------------------------
def plot_run6_fits(times, r_av, r_std,
                            r_params, itsplit,
                            path_out_figs, fig_name):
    t0 = it0 * dt_fields
    t_split = itsplit * dt_fields

    x = times[it0:] / t0
    # x_log = np.log(x)
    x1 = times[it0:itsplit] / t0
    # x1_log = np.log(x1)
    x2 = times[itsplit:] / t0
    # x2_log = np.log(x2)
    n = len(x)
    n1 = len(x1)
    n2 = len(x2)


    n_params = len(r_params)
    o1 = np.zeros(n_params, dtype=np.double)
    o2 = np.zeros(n_params, dtype=np.double)
    m1 = np.zeros(n_params, dtype=np.double)
    m2 = np.zeros(n_params, dtype=np.double)
    l1 = np.zeros(n_params, dtype=np.double)
    l2 = np.zeros(n_params, dtype=np.double)
    k1 = np.zeros(n_params, dtype=np.double)
    k2 = np.zeros(n_params, dtype=np.double)
    a = np.zeros(n_params, dtype=np.double)
    b = np.zeros(n_params, dtype=np.double)
    c = np.zeros(n_params, dtype=np.double)
    err_log = np.zeros(n_params, dtype=np.double)
    eps_log = np.zeros(n_params, dtype=np.double)
    err_pow = np.zeros(n_params, dtype=np.double)
    err_pow_normed = np.zeros(n_params, dtype=np.double)
    eps_pow = np.zeros(n_params, dtype=np.double)

    for istar, rstar in enumerate(r_params):
        R0 = r_av[istar,it0]
        print('')
        print('FITTING: rstar='+str(rstar), '(it0='+str(it0)+', R0='+str(R0)+')', 'isplit='+str(itsplit))

        ''' Section 1 '''
        y1 = r_av[istar, it0:itsplit] / R0
        [o1[istar], m1[istar]], pcov = optimize.curve_fit(powlaw_fit, x1, y1)
        err_pow1 = sq_error(y1, powlaw_fit(x1, o1[istar], m1[istar]))        # multiply by R0
        err_pow1_normed = sq_error(R0*y1, R0*powlaw_fit(x1, o1[istar], m1[istar]))        # multiply by R0

        # y1_log = np.log(y1)
        # [o1_log, m1_log], pcov = optimize.curve_fit(linear_fit, x1_log, y1_log)
        # perr1 = np.sqrt(np.diag(pcov))
        # err_lin1 = np.round(sq_error(y1_log, linear_fit(x1_log, o1_log, m1_log)), 3)
        # err_lin1_normed = sq_error(R0*np.exp(y1_log), R0*np.exp(linear_fit(x1_log, o1_log, m1_log)))

        ''' Section 2 '''
        y2 = r_av[istar, itsplit:] / R0
        [o2[istar], m2[istar]], pcov = optimize.curve_fit(powlaw_fit, x2, y2)
        err_pow2 = np.round(sq_error(y2, powlaw_fit(x2, o2[istar], m2[istar])), 3)
        err_pow2_normed = sq_error(R0*y2, R0*powlaw_fit(x2, o2[istar], m2[istar]))

        # y2_log = np.log(y2)
        # [o2_log, m2_log], pcov = optimize.curve_fit(linear_fit, x2_log, y2_log)
        # perr2 = np.sqrt(np.diag(pcov))
        # err_lin2 = np.round(sq_error(y2_log, linear_fit(x2_log, o2_log, m2_log)), 3)
        # err_lin2_normed = sq_error(R0*np.exp(y2_log), R0*np.exp(linear_fit(x2_log, o2_log, m2_log)))

        ''' Section 1 + 2 '''
        y = r_av[istar, it0:] / R0
        [l1[istar], k1[istar], l2[istar], k2[istar]], pcov = optimize.curve_fit(powlaw_fit_two, x, y)
        err_pow[istar] = sq_error(y, powlaw_fit_two(x, l1[istar], k1[istar], l2[istar], k2[istar]))
        err_pow_normed[istar] = sq_error(y*R0, R0*powlaw_fit_two(x, l1[istar], k1[istar], l2[istar], k2[istar]))
        eps_pow[istar] = 1./n*np.sqrt(err_pow_normed[istar])

        p0 = [0., 1., .5]
        [a[istar], b[istar], c[istar]], pcov = optimize.curve_fit(log_fit_romps, t0*x, R0*y, p0[:])
        # perr = np.sqrt(np.diag(pcov))
        err_log1 = np.round(sq_error(y1*R0, log_fit_romps(t0*x1, a[istar], b[istar], c[istar])), 3)
        err_log2 = np.round(sq_error(y2*R0, log_fit_romps(t0*x2, a[istar], b[istar], c[istar])), 3)
        err_log[istar] = np.round(sq_error(y*R0, log_fit_romps(t0*x, a[istar], b[istar], c[istar])), 3)
        eps_log[istar] = 1./n*np.sqrt(err_log[istar])

        print('')
        print('Section 1:')
        print('power law fit: (a,m)=' + str(np.round(o1[istar], 3)) + ', ' + str(np.round(m1[istar], 3)))
        # print('linear fit:    ' + str(np.round(o1_log, 3)) + ', ' + str(np.round(m1_log, 3)))
        print('Error power law: e(R/R0)=' + str(np.round(err_pow1, 2)) + ', e(R)=' + str(np.round(err_pow1_normed, 2)))
        print('    mean(e) (sqrt, normed)   ', np.round(1./n1 * np.sqrt(err_pow1), 3),
              np.round(1. / n1 * np.sqrt(err_pow1_normed), 2))
        # print('Error linear fit:', np.round(err_lin1, 3), np.round(err_lin1_normed, 3))
        # print('(sqrt, normed)   ', np.round(np.sqrt(1. / n1 * err_lin1), 3),
        #       np.round(np.sqrt(1. / n1 * err_lin1_normed), 2))
        print('Error log-fit:', np.round(err_log1, 3))
        print('    mean(e) (sqrt, normed)   ', np.round(1./n1 * np.sqrt(err_log1), 3))
        print('')
        print('Section 2:')
        print('power law fit: (a,m)=' + str(np.round(o2[istar], 3)) + ', ' + str(np.round(m2[istar], 3)))
        # print('linear fit:    ' + str(np.round(o2_log, 3)) + ', ' + str(np.round(m2_log, 3)))
        print('Error power law: e(R/R0)=' + str(np.round(err_pow2, 2)) + ', e(R)=' + str(np.round(err_pow2_normed, 2)))
        print('    mean(e) (sqrt, normed)   ', np.round(1./n2 * np.sqrt(err_pow2), 3), np.round(1./n2 * np.sqrt(err_pow2_normed), 2))
        # print('Error linear fit:', np.round(err_lin2, 3), np.round(err_lin2_normed, 3))
        # print('(sqrt, normed)   ', np.round(np.sqrt(1./n2 * err_lin1), 3), np.round(np.sqrt(1./n2 * err_lin2_normed), 2))
        print('Error log-fit:', np.round(err_log2, 3))
        print('(sqrt, normed)   ', np.round(1./n2 * np.sqrt(err_log2), 3))
        print('')
        print('Section 1+2:')
        print('power law fit (y=a_i*x^m_i): ')
        print('a1, m1, a2, m2 = ' + str(np.round(l1[istar],3))+', '+str(np.round(k1[istar],3))+
                ', '+str(np.round(l2[istar], 3))+', '+str(np.round(k2[istar],3)))
        print('Error power law: ', np.round(err_pow[istar], 4))
        print('    mean(e) (sqrt normed)   ', np.round(eps_pow[istar], 4))
        print('Log-fit: (a,b,c)=', a[istar], b[istar], c[istar])
        print('Error log-fit:', np.round(err_log[istar], 3))
        print('    mean(e) (sqrt, normed)   ', np.round(eps_log[istar], 3))
        print('')
        print('')


    fig, axes = plt.subplots(1, 3, sharex='none', figsize=(20, 6))
    lblsize = 24
    ticksize = 15
    ax00 = axes[0]
    ax01 = axes[1]
    ax10 = axes[2]

    itplot0 = it0-2
    itplot0 = 1

    x = times[itplot0:] / t0
    x_log = np.log(times[itplot0:] / t0)

    ax00.plot([t0, t0], [0, 12e3], '.5', linewidth=.5)
    ax00.plot([t_split, t_split], [0, 14e3], '--', color='.5', linewidth=.5)
    ax01.plot([np.log(t0 / t0), np.log(t0 / t0)], [-2, 2], '.5', linewidth=.5)
    ax01.plot([np.log(t_split / t0), np.log(t_split / t0)], [-2, 2], '--', color='.5', linewidth=.5)
    ax10.plot([t0, t0], [0, np.amax(r_std)], '.5', linewidth=.5)
    ax10.plot([t_split, t_split], [0, np.amax(r_std)], '--', color='.5', linewidth=.5)
    for istar in range(n_params):
        R0 = r_av[istar, it0]

        ax00.plot(times[itplot0:], r_av[istar, itplot0:], 'x', color=colorlist5[istar])
        lbl = r'R=a+b$\,$log(1+c$\,$t), (S$^2$='+str(np.round(err_log[istar],1))\
              +', $\epsilon$='+str(np.round(eps_log[istar],1))+')'
        ax00.plot(times[itplot0:], a[istar] + b[istar] * np.log(1 + c[istar] * times[itplot0:]), '-', color=colorlist5[istar], label=lbl)

        ax01.plot(x_log, np.log(r_av[istar, itplot0:] / R0), 'x', color=colorlist5[istar])
        lbl = 'R=R0+a*(t/t0)**m, (S$^2$=' + str(np.round(err_pow_normed[istar], 1)) \
              + ', $\epsilon$=' + str(np.round(eps_pow[istar], 1)) + ')'
        ax01.plot(x_log, np.log(powlaw_fit_two(x, l1[istar], k1[istar], l2[istar], k2[istar])),
                  '-', color=colorlist5[istar], label=lbl)

        lbl = 'r*=' + str(r_params[istar])
        ax10.plot(times[itplot0:], r_std[istar, itplot0:], '-x', color=colorlist5[istar], linewidth=1, label=lbl)
        # ax2_ = ax2.twinx()
        # ax2_.plot(times[itplot0:], r_var[itplot0:], 'o-', color='.8', markeredgecolor='w')

        residual_pow = r_av[istar, itplot0:] - R0*powlaw_fit_two(x, l1[istar], k1[istar], l2[istar], k2[istar])
        residual_log = r_av[istar, itplot0:] - log_fit_romps(t0 * x, a[istar], b[istar], c[istar])
        axins_y = 0.2
        axins_width = .13
        axins_height = .15
        axins1 = plt.axes([0.17, axins_y, axins_width, axins_height])
        axins1.plot(t0*x, residual_log, color=colorlist5[istar])
        axins2 = plt.axes([0.51, axins_y, axins_width, axins_height])
        axins2.plot(t0*x, residual_pow, color=colorlist5[istar])
        axins1.set_ylim(-500, 500)
        axins2.set_ylim(-500, 500)
        for label in axins1.yaxis.get_ticklabels()[0::2]:
            label.set_visible(False)
        for label in axins2.yaxis.get_ticklabels()[1::2]:
            label.set_visible(False)
        for axins in [axins1, axins2]:
            # axins.set_aspect('equal')
            axins.set_xlim(dt_fields, tmax)
            axins.set_xlabel('t [min]', fontsize=12)
            axins.set_ylabel('residual', fontsize=12)
            axins.set_xticks(np.arange(0, tmax, step=600))
            axins.set_xticklabels([np.int(n / 60) for n in axins.get_xticks()])
            axins.set_yticklabels([np.int(n) for n in axins.get_yticks()])

    ax00.set_xticks(np.arange(0, tmax, step=600))
    ax00.set_xticklabels([np.int(n / 60) for n in ax00.get_xticks()], fontsize=ticksize)
    ax00.set_yticklabels([np.int(n * 1e-3) for n in ax00.get_yticks()], fontsize=ticksize)
    ax01.set_xticklabels([n for n in ax01.get_xticks()], fontsize=ticksize)
    ax01.set_yticklabels([n for n in ax01.get_yticks()], fontsize=ticksize)
    ax10.set_xticks(np.arange(0, tmax, step=600))
    ax10.set_xticklabels([np.int(n / 60) for n in ax10.get_xticks()], fontsize=ticksize)
    ax10.set_yticklabels([np.round(n * 1e-3, 2) for n in ax10.get_yticks()], fontsize=ticksize)
    # # ax2_.set_yticklabels([np.int(n) for n in ax2_.get_yticks()])

    ax00.legend(loc=2, fontsize=12)
    ax10.legend(loc='best', fontsize=12)
    ax01.legend(loc=2, fontsize=12)
    ax00.set_ylim(0, np.amax(r_av) * 1.1)
    ax01.set_ylim(-1.5, 2.)
    ax00.set_xlabel('t  [min]', fontsize=lblsize)
    ax00.set_ylabel('R  [km]', fontsize=lblsize)
    ax01.set_xlabel('log(t/t0)  [-]', fontsize=lblsize)
    ax01.set_ylabel('log(R/R0)  [-]', fontsize=lblsize)
    ax10.set_xlabel('t  [min]', fontsize=lblsize)
    ax10.set_ylabel(r'std(R)  [km]', fontsize=lblsize)

    textprops = dict(facecolor='white', alpha=0.9, linewidth=0.)
    txt_x = 1.08
    ftsize = 21
    ax00.text(0., txt_x, 'a) Logarithmic fit', transform=ax00.transAxes, fontsize=ftsize, verticalalignment='top',
              bbox=textprops)
    ax01.text(0., txt_x, 'b) Power law fit', transform=ax01.transAxes, fontsize=ftsize, verticalalignment='top',
              bbox=textprops)
    ax10.text(0., txt_x, 'c) Standard deviation of the radius', transform=ax10.transAxes, fontsize=ftsize,
              verticalalignment='top', bbox=textprops)

    plt.subplots_adjust(bottom=0.12, right=.97, left=0.05, top=0.92, wspace=0.25, hspace=0.2)
    print('saving: ' + str(os.path.join(path_out_figs, fig_name)))
    fig.savefig(os.path.join(path_out_figs, fig_name + '.png'))
    fig.savefig(os.path.join(path_out_figs, fig_name + '.pdf'))
    plt.close(fig)
    return


# ----------------------------------------------------------------------

def plot_R_twofits_variance(times, r_av, r_var, r_std, itsplit, rstar,
                            path_out_figs, fig_name):
    t0 = it0*dt_fields
    t_split = itsplit*dt_fields
    R0 = r_av[it0]
    rmax = np.amax(r_av)
    rvarmax = np.amax(r_var)
    # print('it0', it0, R0)

    print('FITTING 2x: (it0='+str(it0)+', R0='+str(R0)+')')
    ''' Section 1 '''
    x1 = times[it0:itsplit] / t0
    y1 = r_av[it0:itsplit] / R0
    n1 = len(x1)
    # [a1_, m1_], pcov = optimize.curve_fit(powlaw_fit, x1, r_av[1:t_split])
    # p0 = [1, .5]
    # print('.....', p0)
    # [a1_, m1_], pcov = optimize.curve_fit(powlaw_fit, x1, r_av[1:t_split], p0=[r_av[0], .5])
    # # err_pow1_ = sq_error(y1, powlaw_fit(x1, a1_, m1_))
    [o1, m1], pcov = optimize.curve_fit(powlaw_fit, x1, y1)
    err_pow1 = sq_error(y1, powlaw_fit(x1, o1, m1))        # multiply by R0
    err_pow1_normed = sq_error(R0*y1, R0*powlaw_fit(x1, o1, m1))        # multiply by R0

    x1_log = np.log(x1)
    y1_log = np.log(y1)
    [o1_log, m1_log], pcov = optimize.curve_fit(linear_fit, x1_log, y1_log)
    perr1 = np.sqrt(np.diag(pcov))
    err_lin1 = np.round(sq_error(y1_log, linear_fit(x1_log, o1_log, m1_log)), 3)
    err_lin1_normed = sq_error(R0*np.exp(y1_log), R0*np.exp(linear_fit(x1_log, o1_log, m1_log)))

    ''' Section 2 '''
    x2 = times[itsplit:] / t0
    y2 = r_av[itsplit:] / R0
    n2 = len(x2)
    [o2_, m2_], pcov = optimize.curve_fit(powlaw_fit, x2, r_av[itsplit:])
    err_pow2_ = np.round(sq_error(y1, powlaw_fit(x1, o2_, m2_)), 3)
    [o2, m2], pcov = optimize.curve_fit(powlaw_fit, x2, y2)
    err_pow2 = np.round(sq_error(y2, powlaw_fit(x2, o2, m2)), 3)
    err_pow2_normed = sq_error(R0*y2, R0*powlaw_fit(x2, o2, m2))

    x2_log = np.log(x2)
    y2_log = np.log(y2)
    [o2_log, m2_log], pcov = optimize.curve_fit(linear_fit, x2_log, y2_log)
    perr2 = np.sqrt(np.diag(pcov))
    err_lin2 = np.round(sq_error(y2_log, linear_fit(x2_log, o2_log, m2_log)), 3)
    err_lin2_normed = sq_error(R0*np.exp(y2_log), R0*np.exp(linear_fit(x2_log, o2_log, m2_log)))

    ''' Section 1 + 2 '''
    x = times[it0:] / t0
    y = r_av[it0:] / R0
    n = len(x)
    [l1, k1, l2, k2], pcov = optimize.curve_fit(powlaw_fit_two, x, y)
    print('-----', l1, k1, l2, k2)
    err_pow = sq_error(y, powlaw_fit_two(x, l1, k1, l2, k2))
    err_pow_normed = sq_error(y*R0, R0*powlaw_fit_two(x, l1, k1, l2, k2))

    p0 = [0., 1., .5]
    [a, b, c], pcov = optimize.curve_fit(log_fit_romps, t0*x, R0*y, p0[:])
    # [a, b, c], pcov = optimize.curve_fit(log_fit_romps, t0*x, y, p0=p0[:])
    perr = np.sqrt(np.diag(pcov))
    err_log1 = np.round(sq_error(y1*R0, log_fit_romps(t0*x1, a, b, c)), 3)
    err_log2 = np.round(sq_error(y2*R0, log_fit_romps(t0*x2, a, b, c)), 3)
    err_log = np.round(sq_error(y*R0, log_fit_romps(t0*x, a, b, c)), 3)

    print('')
    print('Section 1:')
    print('power law fit: ' + str(np.round(o1, 3)) + ', ' + str(np.round(m1, 3)))
    print('linear fit:    ' + str(np.round(o1_log, 3)) + ', ' + str(np.round(m1_log, 3)))
    print('Error power law: ', np.round(err_pow1, 2), np.round(err_pow1_normed, 2))
    print('(sqrt, normed)   ', np.round(np.sqrt(1. / n1 * err_pow1), 3),
          np.round(np.sqrt(1. / n1 * err_pow1_normed), 2))
    print('Error linear fit:', np.round(err_lin1, 3), np.round(err_lin1_normed, 3))
    print('(sqrt, normed)   ', np.round(np.sqrt(1. / n1 * err_lin1), 3),
          np.round(np.sqrt(1. / n1 * err_lin1_normed), 2))
    print('Error log-fit:', np.round(err_log1, 3))
    print('(sqrt, normed)   ', np.round(np.sqrt(1./n1*err_log1), 3))
    print('')
    print('Section 2:')
    print('power law fit: ' + str(np.round(o2, 3)) + ', ' + str(np.round(m2, 3)))
    print('linear fit:    ' + str(np.round(o2_log, 3)) + ', ' + str(np.round(m2_log, 3)))
    print('Error power law: ', np.round(err_pow2, 2), np.round(err_pow2_normed, 2))
    print('(sqrt, normed)   ', np.round(np.sqrt(1./n2 * err_pow2), 3), np.round(np.sqrt(1./n2 * err_pow2_normed), 2))
    print('Error linear fit:', np.round(err_lin2, 3), np.round(err_lin2_normed, 3))
    print('(sqrt, normed)   ', np.round(np.sqrt(1./n2 * err_lin1), 3), np.round(np.sqrt(1./n2 * err_lin2_normed), 2))
    print('Error log-fit:', np.round(err_log2, 3))
    print('(sqrt, normed)   ', np.round(np.sqrt(1. / n2 * err_log2), 3))
    print('')
    print('Section 1+2:')
    print('power law fit: ' + str(np.round(l1,3))+', '+str(np.round(k1,3))+', '+str(np.round(l2, 3))+', '+str(np.round(k2,3)))
    print('Error power law: ', np.round(err_pow, 2))
    print('(sqrt, normed)   ', np.round(np.sqrt(1./n * err_pow_normed), 3))
    # print('linear fit:    ' + str(np.round(o2_log, 3)) + ', ' + str(np.round(m2_log, 3)))
    # print('(sqrt, normed)   ', np.round(np.sqrt(1. / n2 * err_pow2), 3),
    #       np.round(np.sqrt(1. / n2 * err_pow2_normed), 2))
    # print('Error linear fit:', np.round(err_lin2, 3), np.round(err_lin2_normed, 3))
    # print('(sqrt, normed)   ', np.round(np.sqrt(1. / n2 * err_lin1), 3),
    #       np.round(np.sqrt(1. / n2 * err_lin2_normed), 2))
    print('Log-fit: (a,b,c)=', a, b, c)
    print('Error log-fit:', np.round(err_log, 3))
    print('(sqrt, normed)   ', np.round(np.sqrt(1./n * err_log), 3))
    print('')
    print('')





    fig, axes = plt.subplots(1, 3, sharex='none', figsize=(20, 5))
    ax0 = axes[0]
    ax1 = axes[1]
    ax2 = axes[2]
    # ax3 = axes[3]
    itplot0 = 1
    x = times[itplot0:] / t0
    x_log = np.log(times[itplot0:] / t0)

    ax0.plot([t0, t0], [0, 12e3], '.5', linewidth=.5)
    ax0.plot([t_split, t_split], [0, 14e3], '--', color='.5', linewidth=.5)
    ax0.plot(times[itplot0:], r_av[itplot0:], '-o', color='k', markeredgecolor='w')
    lbl = r'R=a+b$\,$log(1+c$\,$t), (S$^2$='+str(np.round(err_log,1))+', $\epsilon$='+str(np.round(np.sqrt(err_log)/n,1))+')'
    ax0.plot(times[itplot0:], a + b * np.log(1 + c * times[itplot0:]), 'r-', label=lbl)
    lbl = 'R=R0+a*(t/t0)**m, (S$^2$='+str(np.round(err_pow_normed,1))+', $\epsilon$='+str(np.round(np.sqrt(err_pow_normed)/n,1))+')'
    ax0.plot(times[itplot0:], R0*powlaw_fit_two(x, l1, k1, l2, k2), 'b-', label=lbl)
    textprops = dict(facecolor='white', alpha=0.5, linewidth=0.)
    txt_x = .04
    txt_y = .95
    ftsize = 15
    text_str = 'Log-fit: a='+str(np.round(a,2)) + ', b='+str(np.round(b,2))+ ', c='+str(np.round(c,4))
    ax0.text(txt_x, txt_y, text_str, transform=ax0.transAxes, fontsize=ftsize, verticalalignment='top', bbox=textprops)

    ax1.plot([np.log(t0/t0), np.log(t0/t0)], [-2,2], '.5', linewidth=.5)
    ax1.plot([np.log(t_split/t0), np.log(t_split/t0)], [-2,2], '--', color='.5', linewidth=.5)

    ax1.plot(x_log, np.log(r_av[itplot0:]/R0), '-o', color='k', markeredgecolor='w')
    lbl = 'y=a+m*x, a=' + str(np.round(o1, 1)) + ', m=' + str(np.round(m1, 1)) + ' (' + str(np.round(perr1, 3)) + ')'
    ax1.plot(x_log, o1 + m1*x_log, '-', color='.3', linewidth=1, label=lbl)
    lbl = 'y=a+m*x, a=' + str(np.round(o2, 1)) + ', m=' + str(np.round(m2, 1)) + ' (' + str(np.round(perr2, 3)) + ')'
    ax1.plot(x_log, o2 + m2*x_log, 'k-', linewidth=1, label=lbl)
    lbl = 'log(R/R0)=a+m*log(t/t0)'
    ax1.plot(x_log, np.log(powlaw_fit_two(x, l1, k1, l2, k2)), 'b-', label=lbl)

    ax2.plot([t0, t0], [0, np.sqrt(rvarmax)], '.5', linewidth=.5)
    ax2.plot([t_split, t_split], [0, np.sqrt(rvarmax)], '--', color='.5', linewidth=.5)
    ax2.plot(times[itplot0:], r_std[itplot0:], 'o-', color='k', markeredgecolor='w')
    # ax2_ = ax2.twinx()
    # ax2_.plot(times[itplot0:], r_var[itplot0:], 'o-', color='.8', markeredgecolor='w')

    ax0.set_xticks(np.arange(0, tmax, step=600))
    ax0.set_xticklabels([np.int(n / 60) for n in ax0.get_xticks()])
    ax0.set_yticklabels([np.int(n * 1e-3) for n in ax0.get_yticks()])
    ax2.set_xticks(np.arange(0, tmax, step=600))
    ax2.set_xticklabels([np.int(n / 60) for n in ax2.get_xticks()])
    ax2.set_yticklabels([np.round(n*1e-3,2) for n in ax2.get_yticks()])
    # ax2_.set_yticklabels([np.int(n) for n in ax2_.get_yticks()])

    ax0.legend(loc='best')
    ax1.legend(loc='best')
    ax0.set_ylim(0, rmax*1.1)
    ax1.set_ylim(-1.5, 2.)
    ax0.set_xlabel('t  [min]')
    ax0.set_ylabel('R  [km]')
    ax1.set_xlabel('log(t/t0)  [-]')
    ax1.set_ylabel('log(R/R0)  [-]')
    ax2.set_xlabel('t  [min]')
    ax2.set_ylabel(r'std(R)  [km]')

    plt.suptitle('r*='+str(rstar)+'m')
    plt.subplots_adjust(bottom=0.12, right=.97, left=0.05, top=0.87, wspace=0.25, hspace=0.2)
    print('saving: ' + str(os.path.join(path_out_figs, fig_name)))
    fig.savefig(os.path.join(path_out_figs, fig_name + '.png'))
    # fig.savefig(os.path.join(path_out_figs, fig_name + '.pdf'))
    plt.close(fig)
    print('')
    return

# ----------------------------------------------------------------------
def plot_timeseries(times, r_av, r_std, r_params, itsplit,
                    path_out_figs, fig_name):
    t0 = it0 * dt_fields
    t_split = itsplit * dt_fields




    fig, axes = plt.subplots(1, 3, sharex='none', figsize=(20, 6))
    lblsize = 24
    ticksize= 15
    ax00 = axes[0]
    ax01 = axes[1]
    ax10 = axes[2]

    itplot0 = 1

    x_log = np.log(times[itplot0:] / t0)

    for istar in range(n_params):
        R0 = r_av[istar, it0]

        ax00.plot([t0, t0], [0, 12e3], '.5', linewidth=.5)
        ax00.plot([t_split, t_split], [0, 14e3], '--', color='.5', linewidth=.5)
        ax00.plot(times[itplot0:], r_av[istar, itplot0:], 'x', color=colorlist5[istar])

        ax01.plot([np.log(t0/t0), np.log(t0/t0)], [-2,2], '.5', linewidth=.5)
        ax01.plot([np.log(t_split/t0), np.log(t_split/t0)], [-2,2], '--', color='.5', linewidth=.5)
        ax01.plot(x_log, np.log(r_av[istar, itplot0:]/R0), 'x', color=colorlist5[istar])

        ax10.plot([t0, t0], [0, np.sqrt(np.amax(r_std))], '.5', linewidth=.5)
        ax10.plot([t_split, t_split], [0, np.sqrt(np.amax(r_std))], '--', color='.5', linewidth=.5)
        lbl = 'r*='+str(r_params[istar])
        ax10.plot(times[itplot0:], r_std[istar,itplot0:], '-x', color=colorlist5[istar], linewidth=1, label=lbl)
        # ax2_ = ax2.twinx()
        # ax2_.plot(times[itplot0:], r_var[itplot0:], 'o-', color='.8', markeredgecolor='w')

    ax00.set_xticks(np.arange(0, tmax, step=600))
    ax00.set_xticklabels([np.int(n / 60) for n in ax00.get_xticks()], fontsize=ticksize)
    ax00.set_yticklabels([np.int(n * 1e-3) for n in ax00.get_yticks()], fontsize=ticksize)
    ax01.set_xticklabels([n for n in ax01.get_xticks()], fontsize=ticksize)
    ax01.set_yticklabels([n for n in ax01.get_yticks()], fontsize=ticksize)
    ax10.set_xticks(np.arange(0, tmax, step=600))
    ax10.set_xticklabels([np.int(n / 60) for n in ax10.get_xticks()], fontsize=ticksize)
    ax10.set_yticklabels([np.round(n*1e-3,2) for n in ax10.get_yticks()], fontsize=ticksize)
    # # ax2_.set_yticklabels([np.int(n) for n in ax2_.get_yticks()])

    ax00.legend(loc=2, fontsize=12)
    ax10.legend(loc='best', fontsize=12)
    ax01.legend(loc=2, fontsize=12)
    ax00.set_ylim(0, np.amax(r_av)*1.1)
    ax01.set_ylim(-1.5, 2.)
    ax00.set_xlabel('t  [min]', fontsize=lblsize)
    ax00.set_ylabel('R  [km]', fontsize=lblsize)
    ax01.set_xlabel('log(t/t0)  [-]', fontsize=lblsize)
    ax01.set_ylabel('log(R/R0)  [-]', fontsize=lblsize)
    ax10.set_xlabel('t  [min]', fontsize=lblsize)
    ax10.set_ylabel(r'std(R)  [km]', fontsize=lblsize)

    textprops = dict(facecolor='white', alpha=0.9, linewidth=0.)
    txt_x = 1.08
    ftsize = 21
    ax00.text(0., txt_x, 'a) Logarithmic fit', transform=ax00.transAxes, fontsize=ftsize, verticalalignment='top', bbox=textprops)
    ax10.text(0., txt_x, 'b) Power law fit', transform=ax10.transAxes, fontsize=ftsize, verticalalignment='top', bbox=textprops)
    ax01.text(0., txt_x, 'c) Standard deviation of the radius', transform=ax01.transAxes, fontsize=ftsize, verticalalignment='top', bbox=textprops)

    plt.subplots_adjust(bottom=0.12, right=.97, left=0.05, top=0.92, wspace=0.25, hspace=0.2)
    print('saving: ' + str(os.path.join(path_out_figs, fig_name)))
    fig.savefig(os.path.join(path_out_figs, fig_name + '.png'))
    fig.savefig(os.path.join(path_out_figs, fig_name + '.pdf'))
    plt.close(fig)

    return

# ----------------------------------------------------------------------
def get_radius_vel(fullpath_in, t0, cp_id, n_tracers, n_cps):
    f = open(fullpath_in + '/coldpool_tracer_out.txt', 'r')
    lines = f.readlines()
    dist = []
    vel = []

    count = t0 * n_cps * n_tracers + (cp_id - 1) * n_tracers
    # while CP age is 0 and CP ID is cp_id
    timestep = int(lines[count].split()[0])
    cp_ID = int(lines[count].split()[3])
    # print(timestep, cp_ID)
    while (timestep - 1 == t0 and int(lines[count].split()[3]) == cp_id):
        columns = lines[count].split()
        dist.append(float(columns[8]))
        # vel.append(np.sqrt(float(columns[10])**2 + float(columns[11])**2))
        vel.append(float(columns[12]))
        count += 1
        timestep = int(lines[count].split()[0])
    f.close()
    r_av = np.average(dist)
    r_var = np.var(dist)
    vel_av = np.average(vel)
    vel_var = np.var(vel)

    f.close()
    return r_av, r_var, vel_av

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
# ----------------------------------------------------------------------
def set_input_parameters(args, path_root, dTh_ref, path_ref, case_name):
    print('--- set input parameters ---')

    global n_params
    dTh = 5
    z_params = [1000]  # run5, 6
    if args.rparams:
        r_params = args.rparams
    else:
        r_params = [500, 1000, 1100, 1600, 2300] # run5, 6
        # r_params = [500, 1100, 2300] # run5, 6
    n_params = len(r_params)
    print('dTh: ', dTh)
    print('z*: ', z_params)
    print('r*: ', r_params)
    print('n_params: ', n_params)


    global times, tmin, tmax, nt, k0
    if args.tmin:
        tmin = np.double(args.tmin)
    else:
        tmin = np.double(100)
    if args.tmax:
        tmax = np.double(args.tmax)
    else:
        tmax = np.double(3600)
    times = np.arange(tmin, tmax + 100., 100.)
    times.sort()
    nt = len(times)
    print('tmin: ' + str(tmin) +', tmax: '+str(tmax))
    print('nt: ' + str(nt))
    print('')

    try:
        id0 = 'dTh' + str(dTh) + '_z' + str(z_params[0]) + '_r' + str(r_params[0])
        nml = simplejson.loads(open(os.path.join(path_root, id0, case_name + '.in')).read())
    except:
        # id0 = 'dTh' + str(dTh_ref) + '_z' + str(z_params[0]) + '_r' + str(r_params[0])
        nml = simplejson.loads(open(os.path.join(path_ref, case_name + '.in')).read())
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

    return dTh, z_params, r_params
# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()