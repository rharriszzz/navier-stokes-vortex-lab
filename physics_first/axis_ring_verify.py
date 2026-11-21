"""Pre-evolution convergence and release gates. Exit nonzero and retain all measurements on failure."""
import argparse
import json
from pathlib import Path

import numpy as np
from .axis_ring import CORE, GAMMA, NU, RADIUS, Grid, release, rk3
from .ring_strain import field, ring


def probes():
    angles = np.arange(24)*np.pi/12
    dr = np.r_[0., *(f*CORE*np.cos(angles) for f in (.25, .5, .75, 1.))]
    z = np.r_[0., *(f*CORE*np.sin(angles) for f in (.25, .5, .75, 1.))]
    return np.column_stack([RADIUS + dr, z])


def reference(points):
    src, tangent = ring(-1, 512, half_spacing=0, tilt=0)
    xyz = np.column_stack((points[:, 0], np.zeros(len(points)), points[:, 1]))
    u, jac, w, lap = field(xyz, src, tangent * (2*np.pi*RADIUS/512), gamma=GAMMA)
    return u[:, [0, 2]], w[:, 1], jac[:, 1, 1] + NU*lap[:, 1]/w[:, 1]


def verify(n, length):
    g = Grid(n, length)
    # Ground truth for a smooth regular field crossing the axis on the actual mesh.
    width = .012
    s = (g.R**2 + g.Z**2)/width**2
    exact = np.exp(-s)
    phi = g.invert((10-4*s)*exact/width**2, exact)
    ur, uz = g.velocity(phi)
    div = (g.dr @ (g.R*ur) + g.axial(g.R*uz))[1:] / g.R[1:]
    axis_error = np.max(abs(uz[0] - 2*exact[0]))
    potential_error = np.max(abs(phi-exact))
    # Independent 5D heat kernel at the axis, with negligible outer trace.
    hot = np.exp(-(g.R**2+g.Z**2)/CORE**2)
    initial = hot.copy()
    dt = .00025
    for _ in range(20):
        hot, = rk3((hot,), dt, lambda y: (g.tendency(y, 0, 0, NU),))
    ratio = 1+4*NU*20*dt/CORE**2
    analytic = ratio**-2.5 * np.exp(-(g.R**2+g.Z**2)/(CORE**2*ratio))
    heat_error = np.max(abs(hot-analytic)) / np.max(abs(analytic-initial))
    points = probes()
    exact_u, exact_w, exact_rate = reference(points)
    strong = exact_w >= exact_w[0]/2
    eta = release(g.R, g.Z)
    phi = g.invert(eta)
    ur, uz = g.velocity(phi)
    rate = -g.axial(phi)*g.R*eta + NU*g.R*g.diffusion(eta)
    interp = lambda y: g.interpolate(y)(*points.T)
    sampled_u = np.column_stack([interp(ur), interp(uz)])
    w = interp(g.R*eta)
    rates = interp(rate)/w
    # Coupled 0.5 ms pilot at three step sizes; compare terminal eta at fixed h.
    endpoints = []
    early_rates = []
    for steps in (2, 4, 8):
        dt = .0005/steps
        state, markers = eta.copy(), points.copy()
        for i in range(steps):
            state, markers = g.step(state, markers, dt)
            if i == 0:
                moved = g.interpolate(g.R*state)(*markers.T)
                early_rates.append(np.log(moved/w)/dt)
        endpoints.append(state)
    differences = [np.max(abs(a-b)) for a,b in zip(endpoints, endpoints[1:])]
    initial_rate = 2*early_rates[-1]-early_rates[-2]
    return dict(nodes=g.shape, potential_Linf=potential_error, axis_uz_Linf=axis_error,
                div_Linf=float(np.max(abs(div))), heat_change_rel=heat_error,
                min_initial_omega=float(w.min()), orientation=bool(np.all(w>0)),
                circulation_rel=abs(np.sum(g.weights*g.R*eta)/GAMMA-1),
                impulse_rel=abs(np.sum(g.weights*g.R**3*eta)/(GAMMA*RADIUS**2)-1),
                line_speed_m_s=sampled_u[0,1], velocity_Linf_m_s=np.max(abs(sampled_u-exact_u)),
                strong_rate_Linf_s=np.max(abs((rates-exact_rate)[strong])),
                strong_material_extrap_Linf_s=np.max(abs((initial_rate-exact_rate)[strong])),
                release_omega_Linf_s=np.max(abs(w-exact_w)), strong_count=int(sum(strong)),
                temporal_eta_differences=differences, temporal_order=np.log2(differences[0]/differences[1]),
                rates=rates[strong].tolist())


def qualification():
    output = {}
    for n, length in ((8,.08),(12,.08),(16,.08),(12,.16)):
        key = f'n{n}_L{int(1000*length)}'
        output[key] = verify(n, length)
        print(key, {k:v for k,v in output[key].items() if k!='rates'}, flush=True)
    coarse, mid, fine, big = output.values()
    gates = dict(manufactured=coarse['potential_Linf']>mid['potential_Linf']>fine['potential_Linf'],
                 axis=coarse['axis_uz_Linf']>mid['axis_uz_Linf']>fine['axis_uz_Linf'],
                 heat=coarse['heat_change_rel']>mid['heat_change_rel']>fine['heat_change_rel']
                      and fine['heat_change_rel']<.001,
                 divergence=max(v['div_Linf'] for v in output.values())<1e-8,
                 temporal=min(v['temporal_order'] for v in output.values())>2.7,
                 invariants=all(v['orientation'] and max(v['circulation_rel'],v['impulse_rel'])<1e-6
                                for v in output.values()),
                 velocity=coarse['velocity_Linf_m_s']>mid['velocity_Linf_m_s']>fine['velocity_Linf_m_s']
                          and fine['velocity_Linf_m_s']<.000646,
                 strong_rates=max(v[k] for v in (mid,fine,big) for k in
                                  ('strong_rate_Linf_s','strong_material_extrap_Linf_s'))<.02,
                 outer=(abs(big['line_speed_m_s']-mid['line_speed_m_s'])<.000646 and
                        np.max(abs(np.subtract(big['rates'],mid['rates'])))<.01))
    return dict(levels=output, gates={k:bool(v) for k,v in gates.items()}, passed=all(gates.values()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = qualification()
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    raise SystemExit(0 if result['passed'] else 1)
