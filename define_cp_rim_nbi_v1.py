import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
import netCDF4 as nc
import argparse
import json as simplejson
import os


plt.rcParams['lines.linewidth'] = 1.

# (a) vertical velocity is zero from divergence to convergence zone (behind front)
#       >> velocity should be zero when averaged over a larger area
# (b) radially average


def main():
    parser = argparse.ArgumentParser(prog='LES_CP')
    parser.add_argument("--casename")
    parser.add_argument("--path")
    parser.add_argument("--tmin")
    parser.add_argument("--tmax")
    parser.add_argument("--k0")
    args = parser.parse_args()

    global path_fields, path_out
    if args.path:
        path = args.path
    else:
        # path = '/Users/bettinameyer/polybox/ClimatePhysics/Copenhagen/Projects/LES_ColdPool/' \
        #        'triple_3D_noise/Out_CPDry_triple_dTh2K/'
        path = '/nbi/ac/cond1/meyerbe/ColdPools/triple_3D_noise/Out_CPDry_triple_Th3K/'
    if os.path.exists(os.path.join(path, 'fields')):
        path_fields = os.path.join(path, 'fields')
    elif os.path.exists(os.path.join(path, 'fields_k120')):
        path_fields = os.path.join(path, 'fields_k120')
    path_out = os.path.join(path, 'figs_cp_rim')
    if not os.path.exists(path_out):
        os.mkdir(path_out)

    global case_name
    if args.casename:
        case_name = args.casename
    else:
        case_name = 'ColdPoolDry_triple_3D'

    if args.tmin:
        tmin = np.int(args.tmin)
    else:
        tmin = 100
    if args.tmax:
        tmax = np.int(args.tmax)
    else:
        tmax = tmin + 100
    timerange = np.arange(tmin,tmax,100)
    nt = len(timerange)

    nml = simplejson.loads(open(os.path.join(path, case_name + '.in')).read())
    global nx, ny, nz, dx, dy, dz
    nx = nml['grid']['nx']
    ny = nml['grid']['ny']
    nz = nml['grid']['nz']
    dx = nml['grid']['dx']
    dy = nml['grid']['dy']
    dz = nml['grid']['dz']
    gw = nml['grid']['gw']

    global cm_bwr, cm_grey, cm_vir
    cm_bwr = plt.cm.get_cmap('bwr')
    cm_vir = plt.cm.get_cmap('jet')
    cm_grey = plt.cm.get_cmap('gist_gray_r')

    # define subdomain to scan
    # --- for triple coldpool ---
    d = np.int(np.round(ny / 2))
    a = np.int(np.round(d * np.sin(60.0 / 360.0 * 2 * np.pi)))  # sin(60 degree) = np.sqrt(3)/2
    rstar = 5000.0  # half of the width of initial cold-pools [m]
    irstar = np.int(np.round(rstar / dx))
    ic = np.int(np.round(a / 2))
    jc = np.int(np.round(d / 2))
    shift = 20
    id = irstar + shift
    jd = irstar + shift
    ishift = np.max(id - ic, 0)
    jshift = np.max(jd - jc, 0)
    nx_ = 2 * id
    ny_ = 2 * jd

    print('ic,jc,id,jc,nx_,ny_', ic, jc, id, jd, nx_, ny_)

    # (A) read in w-field
    #       - shift field (roll) and define partial domain where to look for cold pool
    # (B) mask 2D field and turn mask from boolean (True: w>w_c) into integer (1: w>w_c)
    # (C) Define rim of cold pool as the outline of the mask; based on number of neighbours

    # define general arrays
    if args.k0:
        k0 = np.int(args.k0)
    else:
        k0 = 5      # level
    dphi = 6        # angular resolution for averaging of radius
    n_phi = 360 / dphi
    # - rim_intp_all = (phi(t,i_phi)[deg], phi(t,i_phi)[rad], r(t,i_phi))
    # - rim_vel = (phi(t,i_phi)[deg], phi(t,i_phi)[rad], r(t,i_phi), U(t,i_phi), dU(t, i_phi))
    # - rim_vel_av = (r_av(t), U_av(t), dU_av/dt(t))
    rim_intp_all = np.zeros(shape=(3, nt, n_phi), dtype=np.double)
    rim_vel = np.zeros(shape=(5, nt, n_phi), dtype=np.double)
    rim_vel_av = np.zeros(shape=(3, nt))

    for it,t0 in enumerate(timerange):
        if it > 0:
            dt = t0-timerange[it-1]
        else:
            dt = t0
        print('time: '+ str(t0), '(dt='+str(dt)+')')

        '''(A) read in w-field, shift domain and define partial domain '''
        w = read_in_netcdf_fields('w', os.path.join(path_fields, str(t0) + '.nc'))
        w_roll = np.roll(np.roll(w[:, :, k0], ishift, axis=0), jshift, axis=1)
        w_ = w_roll[ic - id + ishift:ic + id + ishift, jc - jd + jshift:jc + jd + jshift]
        icshift = id
        jcshift = jd
        print('ishift', ishift, ic-id + ishift, ic+ id + ishift, icshift, jcshift)

        plot_yz_crosssection(w, ic, path_out, t0)


        ''' (B) mask 2D field and turn mask from boolean (True: w>w_c) into integer (1: w>w_c)'''
        perc = 90
        w_c = np.percentile(w_, perc)
        w_mask = np.ma.masked_less(w_, w_c)
        # if w_mask.mask.any():
        #     w_bin = np.asarray(
        #         [np.int(w_mask.mask.reshape(nx_ * ny_)[i]) for i in range(nx_ * ny_)]).reshape(nx_, ny_)
        w_mask_r = np.ma.masked_where(w_ > w_c, w_)
        if not w_mask_r.mask.any():
            print('STOP (t='+str(t0)+')' )
            continue
        else:
            w_bin_r = np.asarray(
                [np.int(w_mask_r.mask.reshape(nx_ * ny_)[i]) for i in range(nx_ * ny_)]).reshape(nx_, ny_)

        # plot_s(w, w_c, t0, k0, path_fields, path_out)
        plot_w_field(w_c, perc, w, w_roll, w_, w_mask,
                     ishift, jshift, id, jd, ic, jc, icshift, jcshift,
                     k0, t0, gw, nx_, ny_)
        del w, w_roll

        ''' (C) define outline of cold pool '''
        ''' Rim based on outline '''
        rim_test = np.zeros((nx_, ny_), dtype=np.int)
        rim_test1 = np.zeros((nx_, ny_), dtype=np.int)
        rim_test2 = np.zeros((nx_, ny_), dtype=np.int)
        j = 0
        while(j<ny_-1):
            i = 0
            while (w_mask.mask[i,j] and i<nx_-1):
                i += 1
            if i <= ic:
                rim_test1[i,j] = 1
                rim_test[i, j] = 1
            i = nx_-1
            while (w_mask.mask[i,j] and i>=0):
                i -= 1
            if i >= ic:
                rim_test1[i, j] = 1
                rim_test[i, j] = 1
            j += 1

        i = 0
        while (i<nx_-1):
            j = 0
            while (w_mask.mask[i,j] and j<ny_-1):
                j+=1
            if j <= jc:
                rim_test[i,j] = 1
                rim_test2[i,j] = 1
            j = ny_-1
            while (w_mask.mask[i,j] and j>=0):
                j-=1
            if j >= jc:
                rim_test[i, j] = 1
                rim_test2[i,j] = 1
            i+=1



        ''' Rim based on number of neighbours '''
        # w_mask = True, if w<w_c
        # w_mask_r = True, if w>w_c
        rim2 = np.zeros((nx_,ny_),dtype=np.int)
        for i in range(nx_):
            for j in range(ny_):
                if w_mask_r.mask[i,j]:
                    a = np.count_nonzero(w_bin_r[i-1:i+2,j-1:j+2])
                    if a > 5 and a < 9:
                        rim2[i,j] = 1
        rim = np.zeros((nx_,ny_),dtype=np.int)
        rim_list = []
        rim_list_backup = []
        count = 0
        for i in range(nx_):
            for j in range(jcshift+1):
                if w_mask_r.mask[i,j]:
                    a = np.count_nonzero(w_bin_r[i-1:i+2,j-1:j+2])
                    if a > 5 and a < 9:
                        rim[i,j] = 1
                        rim_list.append((i,j))
                        rim_list_backup.append((i,j))
                        count += 1
                        a = np.count_nonzero(w_bin_r[i-1:i+2, j:j+3])
                        if a<=5 or a>=9:
                            break
            for j in range(ny_-1,jcshift,-1):
                if w_mask_r.mask[i,j]:
                    a = np.count_nonzero(w_bin_r[i-1:i+2,j-1:j+2])
                    if a > 5 and a < 9:
                        rim[i,j] = 1
                        rim_list.append((i, j))
                        rim_list_backup.append((i, j))
                        a = np.count_nonzero(w_bin_r[i-1:i+2, j-2:j+1])
                        if a <= 5 or a >= 9:
                            break

        plot_outlines(perc, w_mask_r, rim, rim2, rim_test, rim_test1, rim_test2,
                      jcshift, nx_, ny_, t0)

        del rim_test, rim_test1, rim_test2


        ''' (D) Polar Coordinates & sort according to angle '''
        # (1) find/define center of mass (here = (ic/jc))
        # (2)
        # Once you create a tuple, you cannot edit it, it is immutable. Lists on the other hand are mutable,
        #   you can edit them, they work like the array object in JavaScript or PHP. You can add items,
        #   delete items from a list; but you can't do that to a tuple, tuples have a fixed size.
        nrim = len(rim_list)
        for i, coord in enumerate(rim_list):
            rim_list[i] = (coord, (polar(coord[0]-icshift, coord[1]-jcshift)))
            # if rim already very close to subdomain (nx_,ny_), make domain larger
            if coord[0] >= nx_ - 3 or coord[1] >= ny_ - 3:
                print('!!! changing domain size', nx_, nx_+4)
                shift += 5
                id = irstar + shift
                jd = irstar + shift
                ishift = np.max(id - ic, 0)
                jshift = np.max(jd - jc, 0)
                nx_ = 2 * id
                ny_ = 2 * jd
        # sort list according to angle
        rim_list.sort(key=lambda tup: tup[1][1])
        plot_rim_mask(w_, rim, rim_list, rim_list_backup, icshift, jcshift, nx_, ny_, t0)
        del rim_list_backup
        del w_mask


        # average and interpolate for bins of 6 degrees
        # rim_intp = (phi[deg], phi[rad], r(phi))
        # rim_intp_all = (phi[t,deg], phi[t,rad], r(t,phi))
        angular_range = np.arange(0,361,dphi)
        rim_intp_all[0,it,:] = angular_range[:-1]
        rim_intp_all[1,it,:] = np.pi*rim_intp_all[0,it,:]/180
        # print('')
        i = 0
        for n,phi in enumerate(rim_intp_all[0,it,:]):
            phi_ = rim_list[i][1][1]
            r_aux = 0.0
            count = 0
            while (phi_ >= phi and phi_ < angular_range[n+1]):
                r_aux += rim_list[i][1][0]
                count += 1
                i += 1
                if i < nrim:
                    phi_ = rim_list[i][1][1]
                else:
                    # phi_ = angular_range[n+1]
                    i = 0   # causes the rest of n-, phi-loop to run through without entering the while-loop
                    # >> could probably be done more efficiently
                    break
            if count > 0:
                rim_intp_all[2,it,n] = r_aux / count
        print('')


        # plot outline in polar coordinates r(theta)
        plot_angles(rim_list, rim_intp_all[:,it,:], t0)
        plot_cp_outline_alltimes(rim_intp_all[:,0:it+1,:], timerange)


        ''' Compute radial velocity of rim '''
        rim_vel[0:3, it, :] = rim_intp_all[0:3, it, :]  # copy phi [deg + rad], r(phi)
        if it == 0:
            rim_vel_av[0, it] = np.average(np.ma.masked_less(rim_intp_all[2, it, :], 1.))
            rim_vel_av[1, it] = 0.0
        elif it > 0:
            # for n, phi in enumerate(rim_intp_all[0,it,:]):
            rim_vel[3, it, :] = (rim_intp_all[2, it, :] - rim_intp_all[2, it-1, :]) / dt
            rim_vel_av[0, it] = np.average(np.ma.masked_less(rim_intp_all[2,it,:],1.))
            # rim_vel_av[0, it] = np.average(np.ma.masked_greater(rim_intp_all[2,it,:],1.))
            rim_vel_av[1, it] = np.average(np.ma.masked_where(rim_intp_all[2,it,:]>1., rim_vel[3,it,:]).data)

            plot_cp_rim_averages(rim_vel[:, 0:it+1, :], rim_vel_av[:, :it+1], timerange[:it+1])
            plot_cp_rim_velocity(rim_vel[:, 0:it + 1, :], rim_vel_av, timerange)

    return



# ----------------------------------
def plot_cp_rim_averages(rim_vel, rim_vel_av, timerange):
    nt = rim_vel.shape[1]
    plt.figure(figsize=(12, 5))
    plt.subplot(121)
    plt.plot(timerange[:nt], rim_vel_av[0,:nt],'-o')
    plt.xlabel('t  [s]')
    plt.ylabel('r  [m]')
    plt.title('average radius')

    plt.subplot(122)
    plt.plot(timerange[:], rim_vel_av[1,:],'-o')
    plt.xlabel('t  [s]')
    plt.ylabel('U  [m/s]')
    plt.grid()
    plt.title('average rim velocity')

    plt.savefig(os.path.join(path_out, 'rim_velocity_av.png'))
    plt.close()
    return


def plot_cp_rim_velocity(rim_vel, rim_vel_av, timerange):
    nt = rim_vel.shape[1]
    plt.figure(figsize=(12,5))
    ax = plt.subplot(122)
    for it, t0 in enumerate(timerange[0:nt]):
        ax.plot(rim_vel[0, it, :], rim_vel[2, it, :],
                label='t=' + str(t0) + 's', color=cm_vir(np.double(it) / nt))
    # plt.legend()
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.0), ncol=3, fontsize=12)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
                   # fancybox=True, shadow=True, ncol=5)
    plt.xlabel('phi  [deg]')
    plt.ylabel('U(phi)  [m/s]')
    plt.ylim([20,np.amax(rim_vel[2,:nt,:])+2])

    ax = plt.subplot(121, projection='polar')
    for it, t0 in enumerate(timerange[0:nt]):
        ax.plot(rim_vel[1, it, :], rim_vel[2, it, :],
                label='t=' + str(t0) + 's', color=cm_vir(np.double(it) / nt))
    ax.set_rmax(45.0)
    plt.suptitle('radial velocity of CP expansion (dr/dt)')
    plt.savefig(os.path.join(path_out, 'rim_velocity.png'))
    plt.close()
    return


def plot_cp_outline_alltimes(rim_intp_all, timerange):
    nt = rim_intp_all.shape[1]
    plt.figure(figsize=(12,10))
    ax = plt.subplot(111, projection='polar')
    for it, t0 in enumerate(timerange[0:nt]):
        ax.plot(rim_intp_all[1,it,:], rim_intp_all[2,it,:],'-o', label='t='+str(t0)+'s',
                color = cm_vir(np.double(it)/nt))
    # plt.legend()
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    plt.suptitle('outline CP (all times)', fontsize=28)
    plt.savefig(os.path.join(path_out, 'rim_cp1_alltimes.png'))
    plt.close()

    return




def plot_angles(rim_list, rim_intp, t0):
    plt.figure(figsize=(20,5))
    nx_plots = 4
    plt.subplot(1, nx_plots, 1)
    for i in range(len(rim_list)):
        plt.plot(rim_list[i][1][1], rim_list[i][1][0], 'x', color=cm_vir(float(i) / len(rim_list)))
    plt.xlabel('th')
    plt.ylabel('r')
    plt.title('rim list')
    plt.subplot(1, nx_plots, 2)
    for i in range(len(rim_list)):
        plt.plot(rim_list[i][1][1], rim_list[i][0][0], 'x', color=cm_vir(float(i) / len(rim_list)))
    plt.xlabel('th')
    plt.ylabel('x')
    plt.title('rim list')
    plt.subplot(1, nx_plots, 3)
    plt.plot(rim_intp[0,:], rim_intp[2,:], '-o')
    plt.title('rim interpolated')
    plt.xlabel('th')
    plt.ylabel('r')

    plt.subplot(144, projection='polar')
    plt.plot(rim_intp[1, :], rim_intp[2, :], '-o')

    plt.suptitle('t='+str(t0)+'s', fontsize=28)
    plt.savefig(os.path.join(path_out, 'angles_t'+str(t0)+'s.png'))
    plt.close()
    return



def plot_rim_mask(w_mask, rim, rim_list, rim_list_backup,
                  icshift, jcshift, nx_, ny_, t0):
    max = np.amax(w_mask)
    nx_plots = 4
    ny_plots = 2
    plt.figure(figsize=(5*nx_plots, 6*ny_plots))
    plt.subplot(ny_plots, nx_plots, 1)
    plt.imshow(w_mask.T, cmap=cm_bwr, origin='lower', vmin=-max, vmax=max)
    plt.title('w')
    plt.subplot(ny_plots, nx_plots, 2)
    plt.imshow(rim.T, origin='lower', cmap=cm_vir)
    plt.title('rim')
    plt.subplot(ny_plots, nx_plots, 3)
    plt.imshow(rim.T, origin='lower')
    for i in range(len(rim_list)):
        plt.plot(rim_list_backup[i][0], rim_list_backup[i][1], 'yx', markersize=2)
    plt.title('rim + rim_list')
    plt.xlim([0, nx_ - 1])
    plt.ylim([0, ny_ - 1])
    plt.subplot(ny_plots, nx_plots, 4)
    plt.plot(rim_list_backup)
    plt.title('orange=y, blue=x')
    plt.subplot(ny_plots, nx_plots, 5)
    for i in range(len(rim_list_backup)):
        plt.plot(rim_list_backup[i][0],rim_list_backup[i][1], 'x', color=cm_vir(float(i)/len(rim_list)))
    plt.plot(rim_list_backup[0][0], rim_list_backup[0][1], 'ko')
    plt.title('before sort')
    plt.subplot(ny_plots, nx_plots, 6)
    for i in range(len(rim_list_backup)):
        plt.plot(rim_list_backup[i][0]-icshift,rim_list_backup[i][1]-jcshift,
                 'x', color=cm_vir(float(i)/len(rim_list)))
    plt.plot(rim_list_backup[0][0]-icshift, rim_list_backup[0][1]-jcshift, 'ko')
    plt.title('shifted, before sort')
    plt.subplot(ny_plots, nx_plots, 7)
    for i in range(len(rim_list)):
        plt.plot(rim_list[i][0][0], rim_list[i][0][1], 'x', color=cm_vir(float(i)/len(rim_list)))
    plt.title('after sort (c=order)')
    plt.subplot(ny_plots, nx_plots, 8)
    for i in range(len(rim_list)):
        plt.plot(rim_list[i][0][0], rim_list[i][0][1],
                 'x', color=cm_vir(rim_list[i][1][1]/360))
    plt.title('after sort (c=angle)')
    plt.suptitle('cold pool outline - t='+str(t0)+'s',fontsize=28)
    plt.savefig(os.path.join(path_out,'rim_mask_t'+str(t0)+'s.png'))
    plt.close()

    return


def plot_outlines(perc, w_mask, rim, rim2, rim_test, rim_test1, rim_test2,
                  jcshift, nx_, ny_, t0):
    max = np.amax(w_mask)
    nx_plots = 4
    ny_plots = 2
    plt.figure(figsize=(24,8))
    plt.subplot(ny_plots,nx_plots,1)
    plt.imshow(w_mask.T, cmap=cm_bwr, origin='lower', vmin=-max, vmax=max)
    plt.plot([nx_-1,nx_-1],[0,ny_-1],'r')
    plt.plot([0, nx_ - 1], [ny_-1, ny_ - 1], 'r')
    plt.title('w masked')
    plt.xlim([0, nx_-1])
    plt.ylim([0, ny_-1])

    plt.subplot(ny_plots,nx_plots,2)
    plt.imshow(w_mask.mask.T, origin='lower', cmap=cm_grey)
    plt.title('mask')
    # plt.colorbar(shrink=0.5)
    plt.subplot(ny_plots,nx_plots,3)
    plt.title('rim2 - #neighbours')
    plt.imshow(rim2.T, origin='lower', cmap=cm_grey)
    plt.plot([0, nx_ - 1], [jcshift, jcshift], 'w')
    plt.xlim([0, nx_ - 1])
    plt.ylim([0, ny_ - 1])

    plt.subplot(ny_plots,nx_plots,4)
    plt.title('rim - #neighbours')
    plt.imshow(rim.T, origin='lower', cmap=cm_grey)
    plt.plot([0,nx_-1],[jcshift, jcshift],'w')
    plt.xlim([0, nx_ - 1])
    plt.ylim([0, ny_ - 1])

    plt.subplot(ny_plots,nx_plots,5)
    plt.title('rim x')
    plt.imshow(rim_test1.T, origin='lower', cmap=cm_grey)
    ax = plt.gca()
    # ax.set_xticks(np.arange(-0.5, imax - imin - 0.5, 1), minor=True)
    # ax.set_yticks(np.arange(-0.5, imax - imin - 0.5, 1), minor=True)
    # ax.grid(which='minor', color='w', linewidth=0.2)#, linestyle='-', linewidth=2)
    plt.subplot(ny_plots,nx_plots,6)
    plt.title('rim y')
    plt.imshow(rim_test2.T, origin='lower', cmap=cm_grey)
    plt.subplot(ny_plots,nx_plots,7)
    plt.title('rim - outermost')
    plt.imshow(rim_test.T, origin='lower', cmap=cm_grey)

    plt.subplot(ny_plots,nx_plots,8)
    plt.title('rim - outermost vs #neighbours')
    plt.imshow(rim_test.T, origin='lower', cmap=plt.cm.get_cmap('gist_gray_r'))
    plt.imshow(rim.T, origin='lower',alpha =0.5)
    plt.plot([0, nx_ - 1], [jcshift, jcshift], 'w')
    plt.xlim([0, nx_ - 1])
    plt.ylim([0, ny_ - 1])

    plt.savefig(os.path.join(path_out, 'rim_searching_perc'+str(perc)+'_t' + str(t0) + '.png'))
    plt.close()
    return


def plot_s(w,w_c,t0,k0):
    s = read_in_netcdf_fields('s', os.path.join(path_fields, str(t0) + '.nc'))
    # s_roll = np.roll(w[:, :, k0], [ishift, jshift], [0, 1])
    s_mask = np.ma.masked_where(w[:,:,k0] <= w_c, s[:,:,k0])
    plt.figure()
    ax1 = plt.subplot(1,2,1)
    ax2 = plt.subplot(1,2,2)
    ax1.imshow(s[:,:,k0].T, origin='lower')
    ax2.imshow(s_mask.T, origin='lower')
    # plt.colorbar(ax2)
    plt.suptitle('s masked on w='+str(w_c)+'m/s (z='+str(k0*dz)+')')
    plt.savefig(os.path.join(path_out, 's_masked_k'+str(k0)+'_thresh'+str(w_c)+'_t'+str(t0)+'.png'))
    plt.close()
    del s
    return



def plot_w_field(w_c, perc, w, w_roll, w_, w_mask,
                 ishift, jshift, id, jd, ic, jc, icshift, jcshift,
                 k0, t0, gw, nx_ , ny_):
    max = np.amax(w)
    plt.figure(figsize=(20, 6))
    ax1 = plt.subplot(1, 5, 1)
    ax1.set_title('w')
    # plt.contourf(w[:, :, k0].T, cmap=cm_bwr, aspect=1.)
    # plt.colorbar()
    ax2 = plt.subplot(1, 5, 2)
    ax2.set_title('np.roll(w)')
    ax3 = plt.subplot(1, 5, 3)
    ax3.set_title('w_')
    ax4 = plt.subplot(1, 5, 4)
    ax4.set_title('masked array')
    ax5 = plt.subplot(1, 5, 5)
    ax5.set_title('mask')
    cax = ax1.imshow(w[:, :, k0].T, cmap=cm_bwr, origin='lower', vmin=-max, vmax=max)
    cbar = plt.colorbar(cax, ticks=np.arange(-np.floor(max), np.floor(max) + 1), shrink=0.5)
    ax1.plot([ic, ic], [0, ny - 1], 'b')
    ax1.plot([ic + gw, ic + gw], [0, ny - 1], 'b--')
    ax1.plot([0, nx - 1], [jc, jc], 'r')
    ax1.plot([0, nx - 1], [jc + gw, jc + gw], 'r--')
    ax2.imshow(w_roll.T, cmap=cm_bwr, origin='lower', vmin=-max, vmax=max)
    ax2.plot([ic + ishift, ic + ishift], [0, ny - 1])
    ax2.plot([ic - id + ishift, ic - id + ishift], [0, ny - 1], '--')
    ax2.plot([ic + id + ishift, ic + id + ishift], [0, ny - 1], '--')
    ax2.plot([0, nx - 1], [jc + jshift, jc + jshift])
    ax2.plot([0, nx - 1], [jc + jshift - jd, jc + jshift - jd], 'k--')
    ax2.plot([0, nx - 1], [jc + jshift + jd, jc + jshift + jd], 'k--')
    ax3.imshow(w_.T, cmap=cm_bwr, origin='lower', vmin=-max, vmax=max)
    ax3.plot([icshift, icshift], [0, ny_ - 1])
    ax3.plot([0, nx_ - 1], [jcshift, jcshift])
    ax4.imshow(w_mask.T, cmap=cm_bwr, origin='lower', vmin=-max, vmax=max)
    ax5.imshow(w_mask.mask.T, origin='lower', vmin=-max, vmax=max)

    plt.suptitle(
        'w masked on ' + str(perc) + 'th percentile: w=' + str(np.round(w_c, 2)) + 'm/s (z=' + str(k0 * dz) + ')')
    plt.savefig(os.path.join(path_out, 'w_masked_k' + str(k0) + '_perc' + str(perc) + '_t' + str(t0) + '.png'))
    plt.close()
    return



def plot_yz_crosssection(w,ic,path_out,t0):
    max = np.amax(w)
    plt.figure()
    cax = plt.imshow(w[ic, :, :100].T, cmap=cm_bwr, origin='lower', vmin=-max, vmax=max)
    plt.colorbar(cax, ticks=np.arange(-np.floor(max), np.floor(max) + 1))
    plt.savefig(os.path.join(path_out, 'w_crosssection_t' + str(t0) + '.png'))
    plt.close()

    return


# ----------------------------------
import math
def polar(x, y):
    """returns r, theta(degrees)
    """
    r = (x ** 2 + y ** 2) ** .5
    if y == 0:
        theta = 180 if x < 0 else 0
    elif x == 0:
        theta = 90 if y > 0 else 270
    elif x > 0:
        theta = math.degrees(math.atan(float(y) / x)) if y > 0 \
            else 360 + math.degrees(math.atan(float(y) / x))
    elif x < 0:
        theta = 180 + math.degrees(math.atan(float(y) / x))
    return r, theta
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