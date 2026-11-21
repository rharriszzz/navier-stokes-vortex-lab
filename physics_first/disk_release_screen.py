"""Physical release screen using the reassembled SU2 operator and packed liquid state."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator

from .acoustic_initial_state import background
from .disk_mass_balance import regions, residual, rms
from .disk_pilot import flash
from .disk_step_evidence import conservative
from .measure_disk import measure
from .rotating_disk import mesh, dual_geometry, INNER
from .su2_acoustic import read_restart
from .vortex_equilibrium import initial_state


def shear(xy, cells, u, mu):
    vertices = xy[cells]
    edges = np.roll(vertices, -1, axis=1)-vertices
    normals = np.stack((edges[:, :, 1], -edges[:, :, 0]), axis=-1)
    area = .5*((vertices-vertices.mean(axis=1)[:, None, :])*normals).sum(axis=(1, 2))
    face = .5*(u[cells]+np.roll(u[cells], -1, axis=1))
    grad = np.einsum('cei,cej->cij', face, normals)/area[:, None, None]
    tau = mu*(grad+grad.transpose(0, 2, 1)
              -2/3*np.trace(grad, axis1=1, axis2=2)[:, None, None]*np.eye(2))
    return (area @ (grad*tau).sum(axis=(1, 2)),
            np.sqrt(area @ (tau*tau).sum(axis=(1, 2))/area.sum()))


def loop(xy, u, halfwidth):
    gamma = 0.
    for axis in (0, 1):
        for sign in (-1, 1):
            side = (np.isclose(xy[:, axis], sign*halfwidth, atol=1e-15, rtol=0) &
                    (abs(xy[:, 1-axis])<=halfwidth+1e-15))
            s = xy[side, 1-axis]
            order = np.argsort(s)
            gamma += sign*(1-2*axis)*np.trapezoid(u[side, 1-axis][order], s[order])
    return gamma


def screen(source, release):
    props = background()
    xy, cells, wall = mesh(32, True)
    r = np.linalg.norm(xy, axis=1)
    vol, _ = dual_geometry(xy, cells, wall)
    old, q = (conservative(read_restart(d/'state_00000.dat')) for d in (source, release))
    rho = q[:, 0]
    u, u0 = q[:, 1:3]/rho[:, None], old[:, 1:3]/old[:, :1]
    change = u-u0
    arm = np.column_stack((-xy[:, 1], xy[:, 0]))
    angular = (arm*change).sum(axis=1)
    speed = np.linalg.norm(change, axis=1)
    core = regions(xy)['core']
    circulation = {}
    for width in (.005, .010, .020, .030):
        gamma0 = loop(xy, u0, width)
        circulation[str(width)] = loop(xy, change, width)/gamma0
    p, t = flash(q)
    profile = initial_state(128)
    prescribed = PchipInterpolator(profile.r, profile.p)(np.round(r, 15))
    ring = np.isclose(r, INNER, rtol=0, atol=1e-15)
    thermo = dict(pressure_range_Pa=[min(p), max(p)], max_recovery_error_Pa=max(abs(p-prescribed)),
                  max_T_error_K=max(abs(t-props['temperature_K'])), T_range_K=[min(t), max(t)],
                  density_range_kg_m3=[min(rho), max(rho)], density_change_max=max(abs(rho-old[:, 0])),
                  inner_rise_Pa=p[ring].mean()-p[r.argmin()], liquid_nodes=len(r))
    # Supply only the metadata actually used by the native Euler identity check.
    historical = json.loads((source/'initial.json').read_text())
    audit = {k:historical[k] for k in ('n', 'wide', 'nodes', 'dt_s')}
    audit.update(thermo)
    metadata = release/'initial.json'
    if metadata.exists():
        if json.loads(metadata.read_text()) != audit:
            raise ValueError('Release metadata differs from the projected-state audit')
    else:
        with metadata.open('x') as out:
            out.write(json.dumps(audit, indent=2)+'\n')
    check = measure(release)
    old_rate = residual(source)[:, 0]/vol
    reduction = rms(old_rate[core], vol[core])/check['regions']['inner']['density_rate_rms']
    correction_energy = rho*(change*(u0+.5*change)).sum(axis=1)
    power, stress = shear(xy, cells, u, props['mu_Pa_s'])
    mu_power0, stress0 = shear(xy, cells, u0, props['mu_Pa_s'])
    ref = .0001670970848767434
    gates = dict(velocity=speed.max()<.001, circulation=max(map(abs, circulation.values()))<.001,
                 mass_reduction=reduction>=10, wall=np.all(u[wall]==0),
                 liquid_density=np.array_equal(rho, old[:, 0]),
                 pressure=thermo['max_recovery_error_Pa']<.05 and abs(thermo['inner_rise_Pa']-15.90531581)<.05,
                 temperature=thermo['max_T_error_K']<1e-8,
                 radial=check['regions']['inner']['radial_rms']<.001,
                 viscous_power=abs(power/ref-1)<.05, kinetic_rate=abs(-check['kinetic_rate_W_m']/ref-1)<.05)
    return dict(thermodynamics=thermo, max_change_m_s=speed.max(), peak_xy_m=xy[speed.argmax()].tolist(),
                integrated_conservative_change_per_m=(vol@(q-old)).tolist(),
                kinetic_change_J_m=vol@correction_energy,
                packing_energy_error_max_J_m3=max(abs(q[:, 3]-old[:, 3]-correction_energy)),
                velocity_regions={name:dict(max_m_s=max(speed[m]), rms_m_s=rms(speed[m], vol[m]))
                                  for name, m in regions(xy).items()},
                core_angular_speed_change_max_s=max(abs(angular[core]/r[core]**2)),
                core_angular_speed_relative_max=max(abs(angular[core]/(arm[core]*u0[core]).sum(axis=1))),
                angular_momentum_relative_change=(vol*rho)@angular/((vol*rho)@(arm*u0).sum(axis=1)),
                circulation_fractional_changes=circulation, core_mass_norm_reduction=reduction,
                stress_norm_rms_Pa=[stress0, stress], stress_power_W_m=[mu_power0, power],
                solver_release=check, gates={k:bool(v) for k, v in gates.items()},
                passed=bool(all(gates.values())))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('release', type=Path)
    a = ap.parse_args()
    print(json.dumps(screen(a.source, a.release), indent=2, allow_nan=False))
