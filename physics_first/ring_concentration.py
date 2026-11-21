"""Reconstruct native sections and reconcile them with the 41 archived R290 samples."""
import argparse
import csv
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.interpolate import RectBivariateSpline
from scipy.optimize import brentq

from .axis_ring import CORE, GAMMA, NU, RADIUS, Grid, release
from .axis_ring_measure import locate

PRIMARY = 'n16_L80_s4'
FRACTIONS = (.25,.50,.75)


@lru_cache(maxsize=None)
def polar_rule(order):
    nodes, weights = np.polynomial.legendre.leggauss(order)
    angle = np.arange(4*order)*(2*np.pi/(4*order))
    unit = np.array([np.cos(angle),np.sin(angle)])
    offsets = unit[:,None,:]*((nodes+1)/2)[None,:,None]
    return offsets, weights[:,None]*(nodes[:,None]+1)*np.pi/(8*order)


def radii(field, center, order=16):
    offsets, weights = polar_rule(order)
    def fraction(radius):
        r,z = center[:,None,None]+radius*offsets
        return np.sum(field(r,z)*weights)*(radius**2/GAMMA)
    return {f'r{round(100*f)}_m':brentq(lambda x:fraction(x)-f,0,2*CORE,xtol=2e-14) for f in FRACTIONS}


def moments(r,z,w,weights):
    signed = w*weights
    positive = np.maximum(w,0)*weights
    mass = np.sum(positive)
    center = np.array([np.sum(positive*x)/mass for x in (r,z)])
    x,y = r-center[0], z-center[1]
    xx,xy,yy = (np.sum(positive*v)/mass for v in (x*x,x*y,y*y))
    widths = np.sqrt(2*np.linalg.eigvalsh([[xx,xy],[xy,yy]]))
    gamma = signed.sum()
    return center, dict(gamma=gamma, negative_gamma=np.sum(np.minimum(w,0)*weights),
                        aeff_m2=gamma**2/np.sum(w*signed),
                        minor_m=widths[0],major_m=widths[1],ellipse_m2=np.pi*np.prod(widths))


def series(archive, name):
    heat = name == 'diffusion'
    data = np.genfromtxt(archive/((PRIMARY if heat else name)+'.csv'),delimiter=',',names=True)
    n,length,sub = (PRIMARY if heat else name).split('_')[:3]
    g = Grid(int(n[1:]),int(length[1:])/1000)
    steps = int(sub[1:])
    shift = g.h/2 if name.endswith('shift') else 0.
    nu = 0 if name.endswith('inviscid') else NU
    eta = release(g.R,g.Z-shift)
    marker = np.array([[RADIUS,shift]])
    sampled = None
    if name == PRIMARY:
        sampled = np.load(archive/(PRIMARY+'_fields.npz'))
        rs,zs = sampled['r_m'],sampled['z_m']
        sampled_grid = SimpleNamespace(r=rs,z=zs,h=rs[1]-rs[0])
    for j,row in enumerate(data):
        if heat:
            eta = release(g.R,g.Z,np.sqrt(CORE**2+4*NU*row['t_s']))
        w = g.R*eta
        ridge, quad = locate(g,w)
        centroid, metrics = moments(g.R,g.Z,w,g.weights)
        field = g.interpolate(w)
        metrics.update(radii(field,ridge))
        if not heat:
            np.testing.assert_allclose([*ridge,*marker[0],metrics['r50_m'],metrics['gamma']],
                                       [row['ridge_r'],row['ridge_z'],row['m0_r'],row['m0_z'],
                                        row['half_radius'],row['box_gamma']],atol=4e-10,rtol=0)
            metrics.update(marker_length_m=2*np.pi*row['m0_r'],marker_omega=row['m0_omega'],
                           peak_omega=row['ridge_peak'],rim_gamma=row['ridge_flux'])
        yield name,j,'whole',metrics
        if sampled is not None:
            for label, center, order in [('quadratic',quad,16),('centroid',centroid,16),
                                         ('marker',marker[0],16),('polar32',ridge,32)]:
                yield name,j,label,radii(field,center,order)
            sampled_w = sampled['fields'][j,2].astype(float)
            fit = RectBivariateSpline(rs,zs,sampled_w)
            sample_center = locate(sampled_grid,sampled_w)[0]
            yield name,j,'archived_field',radii(fit.ev,sample_center)
            yield name,j,'ridge_checks',dict(fit_delta_m=np.linalg.norm(quad-ridge),
                    sample_fit_delta_m=np.linalg.norm(sample_center-ridge),
                    field_archive_error_s_inv=np.max(abs(sampled_w-field(rs[:,None],zs[None,:]))))
            for scale in (1.8,2,2.2,3,4,5):
                offsets, weight = polar_rule(32)
                radius = CORE*scale
                r,z = ridge[:,None,None]+radius*offsets
                _, section = moments(r,z,field(r,z),weight*radius**2)
                yield name,j,f'disk_{scale}a',section
        if j+1 < len(data) and not heat:
            for _ in range(steps):
                eta,marker = g.step(eta,marker,.0005/steps,nu)
    if sampled is not None:
        sampled.close()


def write(archive, directory):
    for name in [p.stem for p in sorted(archive.glob('n*.csv'))]+['diffusion']:
        with (directory/(name+'.csv')).open('w') as f:
            writer = csv.writer(f,lineterminator='\n')
            writer.writerow(('frame','time_s','definition','metric','value_SI'))
            for _,j,label,metrics in series(archive,name):
                writer.writerows((j,.0005*j,label,k,v) for k,v in metrics.items())


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('archive',type=Path)
    p.add_argument('destination',type=Path)
    a=p.parse_args()
    a.destination.mkdir(parents=True,exist_ok=False)
    write(a.archive,a.destination)
