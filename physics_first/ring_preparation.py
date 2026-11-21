"""Mechanical and free-space energy scales of the three sampled releases (SI)."""
import argparse
from pathlib import Path

import numpy as np
from scipy.special import erf

from . import ring_strain as rs
from .ring_thresholds import ORIGINAL, placement, write_csv

RHO = 998.
DIAMETER = .025
STROKE = .050


def energy_term(first, second, a, gamma):
    # 1/2 rho integral(A.omega). Both line densities carry a Gaussian.
    x, dl = first
    y, dm = second
    r = np.linalg.norm(x[:,None,:]-y, axis=-1)
    potential = np.full_like(r,np.sqrt(2/np.pi)/a)
    np.divide(erf(r/(np.sqrt(2)*a)), r, where=r>0, out=potential)
    return RHO*gamma**2/(8*np.pi)*np.sum(potential*(dl @ dm.T))


def scales(gap, gamma, n):
    a = rs.CORE
    loops = []
    opts = placement(gap)
    for side in (-1,1):
        p,t = rs.ring(side,n,**opts)
        loops.append((p,t*(2*np.pi*rs.RADIUS/n)))
    single = energy_term(loops[0],loops[0],a,gamma)
    mutual = 2*energy_term(*loops,a,gamma)
    v,_ = rs.measure(-1,n,**opts,gamma=gamma,fd_divisors=())
    prop = np.linalg.norm(v['iso_u_m_s'][0])
    close = 2*v['u_m_s'][0,0]
    exit_u = 2*gamma/STROKE
    volume = np.pi*(DIAMETER/2)**2*STROKE
    swirl = gamma*(1-np.exp(-1.121**2))/(2*np.pi*1.121*a)
    return dict(gap_mm=1000*gap,gamma=gamma,n=n,exit_m_s=exit_u,stroke_s=STROKE/exit_u,
                nozzle_Re=DIAMETER*exit_u/rs.NU,volume_m3=volume,slug_J=.5*RHO*volume*exit_u**2,
                isolated_J=single,mutual_J=mutual,pair_J=2*single+mutual,isolated_m_s=prop,
                gap_closing_m_s=close,ballistic_s=gap/(2*.5*prop),release_tangent_s=gap/close,
                swirl_m_s=swirl,swirl_Mach=swirl/1482,axis_deficit_Pa=RHO*np.log(2)*(gamma/(2*np.pi*a))**2)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    folder = parser.parse_args().directory
    folder.mkdir(parents=True,exist_ok=True)
    write_csv(folder/'preparation.csv',[scales(g,gamma,n) for g,gamma in
              ((ORIGINAL,rs.GAMMA),(.008,rs.GAMMA),(.008,.0036)) for n in (256,512)])
