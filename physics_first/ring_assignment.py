"""Static facing-section assignment control using the analytic Gaussian ring fields."""
import argparse
import csv
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from .axis_ring import CORE, GAMMA, release
from .ring_concentration import polar_rule
from .ring_sections import CANDIDATE, frame
from .ring_thresholds import placement


def study():
    tilt = CANDIDATE['tilt']
    for gap in (.008,.004,.002):
        origin,tangent,basis=frame(0,gap,tilt)
        spacing=placement(gap,tilt)['half_spacing']
        def section(radius,order):
            offsets,weight=polar_rule(order)
            points=origin+np.moveaxis(radius*offsets,0,-1)@basis
            components=[]
            for sign in (-1,1):
                displacement=points-[sign*spacing,0,0]
                axis=np.array([-sign*np.sin(tilt),0,np.cos(tilt)])
                z=displacement@axis
                radial=displacement-z[:,:,None]*axis
                w=release(np.linalg.norm(radial,axis=2),z)*(np.cross(axis,radial)@tangent)
                components.append(w)
            w=sum(components)
            area=weight*radius**2
            signed=np.sum(area*w)
            return dict(flux_over_gamma=signed/GAMMA,own_over_gamma=np.sum(area*components[0])/GAMMA,
                        partner_over_gamma=np.sum(area*components[1])/GAMMA,
                        negative_over_gamma=np.sum(area*np.minimum(w,0))/GAMMA,
                        effective_mm2=1e6*signed**2/np.sum(area*w*w))
        for order in (16,32):
            stop=gap/2
            max_flux=section(stop,order)['flux_over_gamma']
            crossings = {}
            for percent in (25,50,75):
                def residual(x):
                    return section(x,order)['flux_over_gamma']-percent/100
                # The disk inside the midplane lies in the left-sign lobe.
                crossings[f'r{percent}_inside_midplane_mm']=(
                    1000*brentq(residual,1e-8,stop,xtol=1e-13) if max_flux>=percent/100 else None)
            for radius in sorted({stop,2*CORE,3*CORE,4*CORE}):
                yield dict(gap_mm=gap*1000,order=order,radius_mm=1000*radius,
                           **section(radius,order),**crossings)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('destination',type=Path)
    a=p.parse_args()
    rows=list(study())
    with a.destination.open('w') as f:
        writer=csv.DictWriter(f,fieldnames=rows[0],lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
