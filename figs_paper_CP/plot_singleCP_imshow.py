import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
#from matplotlib import cm
# from matplotlib.widgets import TextBox
import netCDF4 as nc
import argparse
import json as simplejson
import os

execfile('settings.py')
label_size = 13
plt.rcParams['xtick.labelsize'] = label_size
plt.rcParams['ytick.labelsize'] = label_size
plt.rcParams['lines.linewidth'] = 2
plt.rcParams['lines.markersize'] = 6
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['text.usetex'] = 'true'
plt.rcParams['legend.numpoints'] = 1

# tracer file:
# - col=0:      timestep of simulation
# - col=1:      age of CP (timestep since beginning of first CP)
# - col=2:      tracer id
# - col=3:      CP id
# - col=4,5:    tracer position (coordinates)
# - col=6,7:    tracer position (coordinates), rounded
# - col=8,9:    tracer radius & angle
# - col=10,11:  u, v wind components
# - col=12,13:  radial & tangential wind components
# - col=14,15:  x-, y-distance of tracer to center
# - col=16,17:  CP center (xc,yc) (COM)

from thermodynamic_functions import thetas_c

def main():
    parser = argparse.ArgumentParser(prog='LES_CP')
    # parser.add_argument("--tmin")
    # parser.add_argument("--tmax")
    # parser.add_argument("--dx")
    # parser.add_argument("--shift")
    # parser.add_argument("--irmax")
    # parser.add_argument("--nsub")
    args = parser.parse_args()

    res = 25
    run = 'run4'
    dTh = 3
    rstar = 1000
    zstar = 1000
    case = 'dTh' + str(dTh) + '_z' + str(zstar) + '_r' + str(rstar)
    # case_name = args.casename
    case_name = 'ColdPoolDry_single_3D'

    # time_range = [600, 900, 1200, 1500]
    time_range = [600, 1200, 1800, 2400]
    nt = len(time_range)
    imin = 40
    k0 = 0

    path_root = '/nbi/ac/cond1/meyerbe/ColdPools/3D_sfc_fluxes_off/single_3D_noise/'
    path = os.path.join(path_root, run + '_dx' + str(res) + 'm', case)
    print(path)
    path_fields = os.path.join(path, 'fields')
    path_out_figs = '/nbi/home/meyerbe/paper_CP/figs_run4'
    if not os.path.exists(path_out_figs):
        os.mkdir(path_out_figs)

    nml = simplejson.loads(open(os.path.join(path, case_name + '.in')).read())
    ic = nml['init']['ic']
    jc = nml['init']['jc']
    nx = nml['grid']['nx']
    ny = nml['grid']['ny']
    dx = np.ndarray(3, dtype=np.int)
    dx[0] = nml['grid']['dx']
    dx[1] = nml['grid']['dy']
    dx[2] = nml['grid']['dz']
    # kmax = np.int(1.0e3 / dx[2])
    dt_fields = nml['fields_io']['frequency']
    print('res: ' + str(dx))
    print('CP centre: ' + str(ic) + ', ' + str(jc))
    print('')

    ''' radial velocity '''
    root_vrad_2D = nc.Dataset(os.path.join(path, 'fields_v_rad/v_rad.nc'))
    # time_rad = root_vrad_2D.variables['time'][:]
    vrad_2D_ = root_vrad_2D.variables['v_rad'][:, :, :, k0]  # v_rad[nt,nx,ny,nz]
    root_vrad_2D.close()
    # root_vrad = nc.Dataset(os.path.join(path, 'data_analysis/stats_radial_averaged.nc'))
    # time_rad = root_vrad.groups['timeseries'].variables['time'][:]
    # vrad = root_vrad.groups['stats'].variables['v_rad'][:, :, k0]         # v_rad[nt,nr,nz]
    # root_vrad.close()

    # ''' vorticity '''
    # root_vort = nc.Dataset(os.path.join(path, 'fields_vorticity/field_vort_yz.nc'))
    # time_vort = root_vort.groups['fields'].variables['time'][:]
    # vorticity_ = root_vort.groups['fields'].variables['vort_yz'][:, :, :kmax]     # vort_yz[t,y,z]
    # root_vort.close()


    ''' Figure with potential temperature, vertical velocity, radial velocity ? '''
    # zoom in to see clefts

    fig_name = 'CP_crosssection_dx' + str(res) + '_' + case + '_imshow.png'
    # nlev = 2e2
    nlev = 2e1
    ncol = len(time_range)
    nrow = 3
    axins_x = .594
    axins_width = .13
    textprops = dict(facecolor='white', alpha=0.9, linewidth=0.)
    t_pos_x = 85.
    t_pos_y = 85.




    fig, axes_ = plt.subplots(nrow, ncol, figsize=(4.9 * ncol, 5 * nrow), sharex='all', sharey='all')

    lvls_th = np.linspace(298, 300, nlev)
    lvls_w = np.linspace(-3, 3, nlev)
    lvls_vrad = np.linspace(-3, 3, nlev)
    norm_th = matplotlib.cm.colors.Normalize(vmax=300, vmin=298)
    norm_w = matplotlib.cm.colors.Normalize(vmax=3, vmin=-3)
    norm_vrad = matplotlib.cm.colors.Normalize(vmax=3, vmin=-3)

    for i, t0 in enumerate(time_range):
        #if i < 2:
        #    continue
        it = np.int(t0/dt_fields)
        print('time: ', t0)

        fullpath_in = os.path.join(path_fields, str(t0) + '.nc')
        root_field = nc.Dataset(fullpath_in)
        grp = root_field.groups['fields']
        s = grp.variables['s'][:, :, k0]
        w = grp.variables['w'][:, :, k0]
        # v = grp.variables['v'][:,:,k0]
        # u = grp.variables['u'][:, :, k0]
        root_field.close()
        theta = thetas_c(s, 0.0)#[ic - nx / 2:ic + nx / 2, :]
        # vorticity = vorticity_[it, :, :]
        vrad_2D = vrad_2D_[it, :, :]

        axs = axes_[0, :]
        cf = axs[i].imshow(theta[:, :].T, cmap=cm_bw_r, norm=norm_th)
        if t0 == time_range[-2]:
            axins = plt.axes([axins_x, 0.815, axins_width, axins_width])
            axins.imshow(theta[ic+48:, jc+48:].T, cmap=cm_bw_r, norm=norm_th)
            axins.set_aspect('equal')
            axins.set_xlim(0, 280)
            axins.set_ylim(0, 280)
            axins.set_xticklabels('')
            axins.set_yticklabels('')
        if t0 == time_range[-1]:
            cax = plt.axes([0.95, 0.7, 0.012, 0.22])
            plt.colorbar(cf, cax=cax, ticks=np.arange(298,300.1,1))

        axs = axes_[1, :]
        cf = axs[i].imshow(w[:, :].T, cmap=cm_bwr, norm=norm_w)
        if t0 == time_range[-2]:
            axins = plt.axes([axins_x, 0.495,axins_width, axins_width])
            axins.imshow(w[ic+48:, jc+48:].T, cmap=cm_bwr, norm=norm_w)
            axins.set_aspect('equal')
            axins.set_xlim(0,280)
            axins.set_ylim(0,280)
            axins.set_xticklabels('')
            axins.set_yticklabels('')
        if t0 == time_range[-1]:
            cax = plt.axes([0.95, 0.38, 0.012, 0.22])
            cbar = plt.colorbar(cf, cax=cax, ticks=np.arange(-3, 3+0.02, 1.))

        axs = axes_[2, :]
        cf = axs[i].imshow(vrad_2D[:, :].T, cmap=cm_bwr, norm=norm_vrad)
        if t0 == time_range[-2]:
            axins = plt.axes([axins_x, 0.175, axins_width, axins_width])
            axins.imshow(vrad_2D[ic+48:, jc+48:].T, cmap=cm_bwr, norm=norm_vrad)
            axins.set_aspect('equal')
            axins.set_xlim(0, 280)
            axins.set_ylim(0, 280)
            axins.set_xticklabels('')
            axins.set_yticklabels('')
        if t0 == time_range[-1]:
            cax = plt.axes([0.95, 0.06, 0.012, 0.22])
            cbar = plt.colorbar(cf, cax=cax, ticks=np.arange(0, 3.1, 1))

        for ax in axes_[:,i].flat:
            ax.text(t_pos_x, t_pos_y, 't='+str(np.int(t0/60))+'min', fontsize=16, horizontalalignment='left', bbox=textprops)

    #for ax in axes_[:,2].flat:
    #    ax.plot(ic,jc, 'ko', markersize=10)


    for ax in axes_.flat:
        ax.set_xlim(imin, nx-imin)
        ax.set_ylim(imin, ny-imin)
        ax.set_aspect('equal')
        x_ticks = [np.int(n*dx[0]*1e-3) for n in ax.get_xticks()]
        x_ticks = [np.int((n-imin)*dx[0]*1e-3) for n in ax.get_xticks()]
        # x_ticks = [np.int((n-imin)) for n in ax.get_xticks()]
        #x_ticks = [np.int(n) for n in ax.get_xticks()]
        ax.set_xticklabels(x_ticks)
        y_ticks = [np.int(n*dx[1]*1e-3) for n in ax.get_yticks()]
        y_ticks = [np.int((n-imin)*dx[0]*1e-3) for n in ax.get_yticks()]
        # y_ticks = [np.int((n)) for n in ax.get_yticks()]
        #y_ticks = [np.int(n) for n in ax.get_yticks()]

        #ax.set_xticks(np.arange(0, (nx-2*imin)*dx[0], step=1.e3))
        # ax.set_xticks(np.arange(0, (nx-2*imin)))
        for label in ax.xaxis.get_ticklabels()[0::2]:
            label.set_visible(False)
        for label in ax.yaxis.get_ticklabels()[0::2]:
            label.set_visible(False)
        ax.set_yticklabels(y_ticks)
    for ax in axes_[2,:].flat:
        ax.set_xlabel('x  [km]')
    for ax in axes_[:,0].flat:
        ax.set_ylabel('y  [km]')

    textprops = dict(facecolor='white', alpha=0.9, linewidth=0.)
    title_pos_x = imin + - 120
    title_pos_y = ny - imin + 25
    title_font = 21
    txt = 'a) potential temperature'
    axes_[0,0].text(title_pos_x, title_pos_y, txt, fontsize=title_font, horizontalalignment='left', bbox=textprops)
    txt = 'b) vertical velocity'
    axes_[1,0].text(title_pos_x, title_pos_y, txt, fontsize=title_font, horizontalalignment='left', bbox=textprops)
    txt = 'c) radial velocity'
    axes_[2,0].text(title_pos_x, title_pos_y, txt, fontsize=title_font, horizontalalignment='left', bbox=textprops)



    # axes_[-1].legend(loc='upper center', bbox_to_anchor=(1.2, 1.),
    #                 fancybox=True, shadow=True, ncol=1, fontsize=10)
    plt.subplots_adjust(bottom=0.04, right=.94, left=0.05, top=0.95, wspace=0.08, hspace=0.18)
    #fig.tight_layout()
    print('saving: ', os.path.join(path_out_figs, fig_name))
    fig.savefig(os.path.join(path_out_figs, fig_name))
    plt.close(fig)

    return


# ----------------------------------------------------------------------

if __name__ == '__main__':
    main()
