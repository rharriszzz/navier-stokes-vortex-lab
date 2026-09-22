"""Analytical R194 oracles only. No solver, mesh, field input or dependencies."""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from itertools import product
import json
import math
from pathlib import Path


def close(a: float, b: float, scale: float = 1.0) -> None:
    assert abs(a-b) <= 2e-12*max(abs(a), abs(b), scale), (a, b)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def crossz(a, b):
    return a[0]*b[1]-a[1]*b[0]


def main() -> dict:
    passed = []
    # Circular area average uses t=s² uniformly on [0,1]. Exact rational moments.
    moments = [sum(F(2**k * math.comb(k,j)*(-1)**j, j+1)
                   for j in range(k+1)) for k in (1,2,3)]
    assert moments == [F(1),F(4,3),F(2)]
    passed.append('exact circular profile moments')
    rho, mu, nu, rv, d, dr = 1000., 1e-3, 1e-6, .1, .004, .006
    qb = 2e-3/60
    qj = qb/32
    area = math.pi*d*d/4
    ubar = qj/area
    ur = (2*qb/32)/(math.pi*dr*dr/4)
    close(ubar*area*32, qb, qb)
    close(ur*math.pi*dr*dr/4*32, 2*qb, qb)
    close(2*ubar, .16578639905405765, .001)
    passed.append('inlet and balanced return normalizations')
    # Both cap groups and bank totals remain compatible for the whole ramp.
    for xi in (0, .1, .25, .5, .8, 1):
        ramp = 3*xi**2-2*xi**3
        close(-64*qj*ramp+32*(2*qb/32)*ramp, 0, qb)
        assert 0 <= ramp <= 1
    assert all(6*x-6*x*x == 0 for x in (0,1))
    passed.append('instantaneous flux-compatible smooth preparation')
    # Simple nominal spacing screens; actual bore union remains unmeshed.
    return_spacing = 2*.035*math.sin(math.pi/16)
    assert return_spacing > dr
    assert .055-d/2 > .045 and .065+d/2 < .075
    assert .010 > d
    passed.append('nominal row band and return separation')
    ej = (-1/math.sqrt(2), 1/math.sqrt(2), 0)
    for length in (0,.02,.04):
        x = tuple(v-length*w for v,w in zip((rv,0,0),ej))
        close(crossz(x,ej),rv/math.sqrt(2),rv)
    passed.append('straight oblique bore angular lever arm')
    torque_uniform = rho*qb*ubar*rv/math.sqrt(2)
    torque_parabolic = torque_uniform*float(moments[1])
    # Independent circular midpoint integration of actual velocity moments.
    n = 20000
    beta_num = math.fsum((2*(1-(j+.5)/n))**2 for j in range(n))/n
    assert abs(beta_num-4/3) < 1e-8
    close(torque_parabolic/torque_uniform,4/3)
    passed.append('angular flux and independent profile quadrature')
    power_uniform = rho*qb*ubar**2
    power_parabolic = power_uniform*float(moments[2])
    close(power_parabolic/power_uniform,2)
    passed.append('kinetic flux distinct from pressure work')
    f, normal, tangential = .125, .3, .2
    actual = f*normal*tangential
    mean_product = f*f*normal*tangential
    covariance = f*(normal-f*normal)*(tangential-f*tangential)+(1-f)*(-f*normal)*(-f*tangential)
    close(actual,mean_product+covariance)
    close(mean_product/actual,f)
    passed.append('finite footprint averaging covariance counterexample')
    theta = 2*math.pi/16
    for m in (0,16,32): close(math.cos(m*theta),1)
    close(math.cos(4*theta),0)
    close(math.sin(4*theta),1)
    close(math.cos(4*math.pi/2),1)
    for phase in (0,.3,math.pi/2):
        close(sum(math.cos(4*j*theta+phase) for j in range(16)),0)
    passed.append('C16 base restriction and m4 phase compatibility')
    # Exact Poiseuille velocity/dissipation/pressure-drop identity.
    bore_r, length = d/2,.5
    dp = 8*mu*length*ubar/(bore_r*bore_r)
    diss = 8*math.pi*mu*length*ubar**2
    close(dp*qj,diss,diss)
    close(dp,32*mu*length*ubar/d**2,dp)
    passed.append('independent Poiseuille power and pressure oracle')
    # Tensor Gauss-3 exactly integrates these degree <= 4 polynomial budgets.
    nodes = (-math.sqrt(3/5),0.,math.sqrt(3/5))
    weights = (5/9,8/9,5/9)
    sides = (1.,2.,3.)
    def quadrature(axes):
        for indices in product(range(3),repeat=len(axes)):
            coords = [0.,0.,0.]
            weight = 1.
            for axis,j in zip(axes,indices):
                coords[axis] = sides[axis]*(1+nodes[j])/2
                weight *= weights[j]*sides[axis]/2
            yield coords,weight
    # u=(x,2y,-3z); p=-rho*(x²+4y²+9z²)/2: exact steady f=0.
    rates = (1.,2.,-3.)
    flux = angular = torque = kinetic = work = gauge_work = gauge_torque = 0.
    for axis in range(3):
        for sign in (-1,1):
            normal_vec = [0.,0.,0.];normal_vec[axis]=sign
            for x,w in quadrature([k for k in range(3) if k!=axis]):
                x[axis] = 0 if sign==-1 else sides[axis]
                u = [a*b for a,b in zip(rates,x)]
                p = -rho*sum(a*a*b*b for a,b in zip(rates,x))/2
                tr = [(-p+2*mu*rates[k])*normal_vec[k] for k in range(3)]
                un = dot(u,normal_vec)
                flux += w*un
                angular += w*rho*crossz(x,u)*un
                torque += w*crossz(x,tr)
                kinetic += w*rho*dot(u,u)*un/2
                work += w*dot(u,tr)
                gauge_work += w*dot(u,[-7*n for n in normal_vec])
                gauge_torque += w*crossz(x,[-7*n for n in normal_vec])
    volume = math.prod(sides)
    diss_affine = 2*mu*sum(a*a for a in rates)*volume
    close(flux,0,volume)
    close(angular,torque)
    assert abs(angular)>1  # Nonzero torque; not a vacuous zero/zero check.
    close(kinetic,work-diss_affine)
    passed.append('nonzero independent affine momentum and energy surface budgets')
    close(gauge_work,0,100)
    close(gauge_torque,0,100)
    passed.append('pressure gauge leaves closed budgets invariant')
    return dict(checks_passed=len(passed),groups=passed,
                interpretation='Analytical proposal checks only; no tank or discretization validation.',
                values=dict(inlet_mean_m_s=ubar,inlet_peak_m_s=2*ubar,
                inlet_reynolds=ubar*d/nu,equal_split_return_mean_m_s=ur,
                return_neighbour_spacing_m=return_spacing,
                torque_uniform_micro_N_m=torque_uniform*1e6,
                torque_parabolic_micro_N_m=torque_parabolic*1e6,
                profile_torque_difference_micro_N_m=(torque_parabolic-torque_uniform)*1e6,
                profile_difference_over_confound=(torque_parabolic-torque_uniform)/(.1309e-6),
                inlet_kinetic_uniform_mW=power_uniform*1e3,
                inlet_kinetic_parabolic_mW=power_parabolic*1e3,
                tank_turnover_s=math.pi*rv**2*.2/(2*qb),
                one_percent_inlet_torque_micro_N_m=.01*torque_parabolic*1e6),
                affine_oracle=dict(mass_out=flux,angular_out=angular,torque=torque,
                kinetic_out=kinetic,traction_work=work,dissipation=diss_affine))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    payload = json.dumps(main(),indent=2,allow_nan=False)+'\n'
    if args.output:
        args.output.write_text(payload)
    else:
        print(payload,end='')
