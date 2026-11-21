"""Release budgets on normal sections, Stokes/shape checks, and one-factor controls."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

from . import ring_strain as rs
from .ring_thresholds import ORIGINAL, placement, write_csv

ARCS = (0, 11.25, 45, 90, 180)
RADII = (0, .25, .5, .75, 1., 1.5, 2.)
CANDIDATE = dict(gap=.008, core=.002, gamma=.0036, tilt=np.pi/6)


def frame(arc, gap, tilt):
    # Left ring. Tangent x outward radial gives the second in-plane basis.
    pos, tan = rs.ring(-1, rs.SAMPLES, **placement(gap, tilt))
    idx = round(arc*rs.SAMPLES/360)
    radial = (pos[idx]+placement(gap, tilt)['half_spacing']*rs.AXES[0])/rs.RADIUS
    return pos[idx], tan[idx], np.stack((radial, np.cross(tan[idx], radial)))


def samples(arc, gap, core, gamma, tilt, count, fd_divisors):
    radii, angles = np.array([(r, phi) for r in RADII for phi in
                              (range(0, 360, 15) if r else [0])]).T
    center, tangent, basis = frame(arc, gap, tilt)
    angles_rad = np.deg2rad(angles)
    offsets = (core*radii)[:, None]*np.column_stack((np.cos(angles_rad), np.sin(angles_rad)))
    points = center + offsets @ basis
    # On the intersection x=y=0 the two mirror symmetries force omega and
    # its Laplacian to vanish. There is no axis on which to project a rate.
    null = np.linalg.norm(points[:,:2],axis=1) < 1e-14
    v, checks = rs.measure(-1, count, **placement(gap, tilt), core=core, gamma=gamma,
                           targets=(points[~null], np.tile(tangent, (sum(~null), 1))), fd_divisors=fd_divisors)
    rows = []
    regular_index = 0
    scalars = ('omega_s_inv','angle_deg','s','visc','net','stretch_abs','visc_abs','net_abs',
               'iso_s','iso_visc','iso_net','iso_omega_s_inv')
    for i, (r, angle) in enumerate(zip(radii, angles)):
        if null[i]:
            # Retain the ill-conditioned raw projection for the convergence audit.
            def local_field(side):
                source, unit = rs.ring(side,count,**placement(gap,tilt))
                return rs.field(points[i:i+1],source,unit*(2*np.pi*rs.RADIUS/count),
                                core=core,gamma=gamma)
            own, partner = local_field(-1), local_field(1)
            omega = own[2]+partner[2]
            magnitude = np.linalg.norm(omega)
            checks['null_raw_omega'] = magnitude
            checks['null_raw_net'] = None
            if magnitude > 0:
                axis = omega / magnitude
                checks['null_raw_net'] = (rs.project(own[1]+partner[1],axis)[0]
                                          + rs.NU*rs.dot(own[3]+partner[3],axis)[0]/magnitude)
            iso_mag = np.linalg.norm(own[2])
            iso_axis = own[2]/iso_mag
            iso_s = rs.project(own[1],iso_axis)[0]
            iso_visc = rs.NU*rs.dot(own[3],iso_axis)[0]/iso_mag
            vals = dict.fromkeys(scalars)
            vals.update(iso_s=iso_s,iso_visc=iso_visc,iso_net=iso_s+iso_visc,iso_omega_s_inv=iso_mag)
            vals.update(omega_s_inv=0., net_abs=0.)
            axis = (None,)*3
        else:
            vals = {k:v[k][regular_index] for k in scalars}
            axis = v['omega_hat'][regular_index]
            regular_index += 1
        rows.append(dict(arc_deg=arc, r_a=r, phi_deg=angle, symmetry_null=bool(null[i]),
                         line_fraction=vals['omega_s_inv']/v['iso_omega_s_inv'][0],
                         **dict(zip(('x_m','y_m','z_m'), points[i])),
                         **dict(zip(('hat_x','hat_y','hat_z'), axis)), **vals))
    return rows, checks


def section_shape(arc, opts, nrad, nphi, nsource, *, sides=(-1, 1)):
    gap, tilt, a, gamma = (opts[k] for k in ('gap','tilt','core','gamma'))
    center, tangent, basis = frame(arc, gap, tilt)
    # Disk of radius 2a. Legendre radial weights include the polar Jacobian.
    roots, weights = np.polynomial.legendre.leggauss(nrad)
    radii = a*(1+roots)
    phi = 2*np.pi*np.arange(nphi)/nphi
    polar = np.column_stack((np.cos(phi), np.sin(phi)))
    xy = (radii[:,None,None]*polar).reshape(-1, 2)
    area = np.repeat(weights*a*radii*(2*np.pi/nphi), nphi)
    points = center + xy @ basis
    edge = center + 2*a*polar @ basis
    edge_dl = 2*a*2*np.pi/nphi*np.column_stack((-np.sin(phi), np.cos(phi))) @ basis
    axial = np.zeros(len(points))
    loop = 0.
    for side in sides:
        source, unit = rs.ring(side, nsource, **placement(gap, tilt))
        dl = unit*(2*np.pi*rs.RADIUS/nsource)
        for start in range(0, len(points), 128):
            sl = slice(start, start+128)
            omega = rs.field(points[sl], source, dl, core=a, gamma=gamma)[2]
            axial[sl] += omega @ tangent
        u = rs.field(edge, source, dl, velocity_only=True, core=a, gamma=gamma)
        loop += (u*edge_dl).sum()
    signed = area*axial
    w = np.maximum(signed, 0)
    centroid = np.average(xy, weights=w, axis=0)
    delta = xy-centroid
    covariance = (delta.T*w) @ delta / w.sum()
    widths = np.sqrt(2*np.linalg.eigvalsh(covariance))*1000
    return dict(flux_m2_s=signed.sum(), loop_m2_s=loop, flux_over_gamma=signed.sum()/gamma,
                stokes_rel=abs(loop-signed.sum())/gamma, negative_flux_over_gamma=-signed[signed<0].sum()/gamma,
                centroid_radial_mm=1000*centroid[0], centroid_second_mm=1000*centroid[1],
                minor_mm=widths[0], major_mm=widths[1])


def facing_peak(opts):
    # Local |omega| maximum in the half-radius disk neighbourhood (square bounds).
    gap, tilt, a = (opts[k] for k in ('gap','tilt','core'))
    center, tangent, basis = frame(0, gap, tilt)
    def evaluate(xy):
        pt = (center + a*np.asarray(xy) @ basis)[None,:]
        return rs.measure(-1, 512, core=a, gamma=opts['gamma'], **placement(gap, tilt),
                          targets=(pt, tangent[None,:]), fd_divisors=())[0]
    def loss(xy):
        return -evaluate(xy)['omega_s_inv'][0]
    opt = minimize(loss, [0.,0.], method='Nelder-Mead', bounds=[(-.5,.5)]*2,
                   options=dict(xatol=1e-8, fatol=1e-10))
    if not opt.success or max(abs(opt.x)) > .49:
        raise ValueError('unresolved facing section peak')
    v = evaluate(opt.x)
    return dict(peak_radial_a=opt.x[0], peak_second_a=opt.x[1],
                peak_omega=v['omega_s_inv'][0], peak_net=v['net'][0], peak_abs=v['net_abs'][0])


def sensitivity():
    rows = []
    for factor, value in [('gamma', .0036), ('gamma', .00324), ('gamma', .00396),
                          ('core', .0018), ('core', .0022), ('gap', .007), ('gap', .009),
                          ('tilt', np.deg2rad(25)), ('tilt', np.deg2rad(35))]:
        case = dict(CANDIDATE)
        case[factor] = value
        opts = dict(**placement(case['gap'],case['tilt']), core=case['core'], gamma=case['gamma'])
        v, _ = rs.measure(-1, 512, **opts, fd_divisors=())
        center, tangent, basis = frame(0,case['gap'],case['tilt'])
        points = center + case['core']*np.array([-.75,-.5,.5,.75])[:,None]*basis[0]
        radial, _ = rs.measure(-1,512, **opts, fd_divisors=(),
                               targets=(points,np.tile(tangent,(4,1))))
        rows.append(dict(varied='nominal' if case == CANDIDATE else factor, **case,
                         line_s=v['s'][0], line_visc=v['visc'][0], line_net=v['net'][0],
                         line_abs=v['net_abs'][0], positive_line_count=int(sum(v['net']>0)),
                         left_facing_ux=v['u_m_s'][0,0], **dict(zip(('in75_net','in50_net','out50_net','out75_net'),radial['net'])),
                         **facing_peak(case)))
    return rows


def study(folder):
    folder.mkdir(parents=True, exist_ok=True)
    points, shapes, checks = [], [], []
    for label, gap, gamma in [('original', ORIGINAL, rs.GAMMA), ('closer', .008, rs.GAMMA),
                              ('candidate', .008, .0036)]:
        opts = dict(CANDIDATE, gap=gap, gamma=gamma)
        line, _ = rs.measure(-1,512, **placement(gap), gamma=gamma, fd_divisors=())
        for arc in ARCS:
            previous = None
            for n in rs.LEVELS:
                rows, diag = samples(arc, **opts, count=n, fd_divisors=(8,16,32,64) if n==512 else ())
                entry = dict(case=label, arc=arc, count=n)
                entry.update({k:v for k,v in diag.items() if k.startswith('null_')})
                if previous:
                    for k in ('s','visc','net','net_abs','omega_s_inv','hat_x','hat_y','hat_z'):
                        entry['change_'+k] = max(abs(x[k]-y[k]) for x,y in zip(rows,previous)
                                                     if not x['symmetry_null'])
                if n==512:
                    entry.update({k:v for k,v in diag.items() if k.startswith('fd_') or
                                  k in ('div_u','curl_minus_omega')})
                    entry['centerline_error'] = abs(rows[0]['net'] - line['net'][round(arc*rs.SAMPLES/360)])
                checks.append(entry)
                previous = rows
            points.extend(dict(case=label, **r) for r in rows)
            for nr, nphi, nsource in ((8,24,256),(16,48,512)):
                shapes.append(dict(case=label, arc_deg=arc,nrad=nr,nphi=nphi,source=nsource,
                                   **section_shape(arc,opts,nr,nphi,nsource)))
    write_csv(folder/'sections.csv', points)
    write_csv(folder/'section_shape.csv', shapes)
    write_csv(folder/'sensitivity.csv', sensitivity())
    (folder/'section_checks.json').write_text(json.dumps(checks,indent=2,allow_nan=False)+'\n')
    return (all(max(c['change_net'],c['change_visc'],c['change_s']) < rs.TOL and
                max(c['div_u'],c['curl_minus_omega']) < 1e-9 and c['fd_a64_pair_s'] < rs.TOL and
                c['fd_a64_pair_directional_s'] < rs.TOL and c['centerline_error'] < 1e-10
                for c in checks if c['count']==512) and
            all(s['stokes_rel'] < 1e-6 for s in shapes if s['nrad']==16))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    raise SystemExit(0 if study(parser.parse_args().directory) else 1)
