"""Measure and project the centered SU2 mass flux on the relocated 2D disk."""
import argparse
import json
from pathlib import Path
import shutil

import CoolProp.CoolProp as CP
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import lsqr

from .acoustic_initial_state import background
from .disk_pilot import flash
from .disk_step_evidence import conservative
from .rotating_disk import INNER, dual_geometry, mesh
from .su2_acoustic import FIELDS, read_restart, write_restart


def mass_matrix(xy, cells, rho):
    """Map nodal Cartesian velocities to integrated outflux using SU2 primitive means."""
    i = cells.ravel()
    j = np.roll(cells, -1, axis=1).ravel()
    spoke = np.repeat(xy[cells].mean(axis=1), 4, axis=0) - (xy[i] + xy[j])/2
    # Each cell contributes one half-face, directed from i's dual cell to j's.
    normal = np.column_stack((spoke[:, 1], -spoke[:, 0]))
    weight = (rho[i] + rho[j])[:, None] * normal / 4
    rows = np.repeat(np.concatenate((i, i, j, j)), 2)
    cols = (2*np.concatenate((i, j, i, j))[:, None] + np.arange(2)).ravel()
    values = np.concatenate((weight, weight, -weight, -weight)).ravel()
    return sparse.coo_matrix((values, (rows, cols)), shape=(len(xy), 2*len(xy))).tocsr()


def residual(directory):
    state = read_restart(directory/'state_00001.dat')
    return np.column_stack([state['Residual_'+name] for name in FIELDS[2:]])


def eos_rates(q, rates):
    """Chain rule for p(rho,e), including conservative momentum and energy work."""
    fluid = CP.AbstractState('HEOS', 'Water')
    props = background()
    fluid.update(CP.PT_INPUTS, props['pressure_pa'], props['temperature_K'])
    chi = fluid.first_partial_deriv(CP.iP, CP.iDmass, CP.iUmass)
    kappa = fluid.first_partial_deriv(CP.iP, CP.iUmass, CP.iDmass)
    u = q[:, 1:3]/q[:, :1]
    ke = .5*(u*u).sum(axis=1)
    e = q[:, 3]/q[:, 0]-ke
    de = (rates[:, 3] - (u*rates[:, 1:3]).sum(axis=1) + (ke-e)*rates[:, 0])/q[:, 0]
    return chi*rates[:, 0] + kappa*de, fluid.speed_sound()**2*rates[:, 0]


def rms(values, weights):
    return np.sqrt(np.average(values**2, weights=weights))


def regions(xy):
    r = np.linalg.norm(xy, axis=1)
    box = np.max(abs(xy), axis=1)
    return {'disk': np.ones(len(r), bool), 'core': (r>0) & (r<=INNER+1e-15),
            'square_seam': np.isclose(box, .035, atol=1e-15, rtol=0),
            'circle_seam': np.isclose(r, .065, atol=1e-15, rtol=0),
            'taper': (r>=.060) & (r<=.080), 'quiet': r>.082}


def baseline(source, centered, endpoint):
    xy, cells, wall = mesh(32, True)
    vol, _ = dual_geometry(xy, cells, wall)
    q = conservative(read_restart(source/'state_00000.dat'))
    u = q[:, 1:3]/q[:, :1]
    total = residual(source)
    central = residual(centered)[:, 0]
    matrix = mass_matrix(xy, cells, q[:, 0])
    flat = mass_matrix(xy, cells, np.full(len(xy), q[0, 0])) @ u.ravel()
    dp, acoustic = eos_rates(q, -total/vol[:, None])
    p0, _ = flash(q)
    p12, _ = flash(conservative(read_restart(endpoint)))
    observed = p12-p0
    report = {}
    reconstruction = matrix@u.ravel()
    rate = -total[:, 0]/vol
    for name, m in regions(xy).items():
        idx = np.flatnonzero(m)[np.argmax(abs(rate[m]))]
        def norm(v):
            return rms(v[m], vol[m])
        report[name] = dict(nodes=int(m.sum()), density_rate_rms=norm(rate),
            max_abs_density_rate=abs(rate[idx]), peak_xy_m=xy[idx].tolist(),
            mass_rate_norm2_fraction=np.sum(vol[m]*rate[m]**2)/np.sum(vol*rate**2),
            jst_rate_rms=norm((total[:, 0]-central)/vol),
            constant_density_difference_rms=norm((flat-central)/vol),
            centered_reconstruction_max=float(np.max(abs((reconstruction-central)[m]))),
            pressure_rate_rms_Pa_s=norm(dp), pressure_rate_max_Pa_s=max(abs(dp[m])),
            pressure_rate_acoustic_difference_rms_Pa_s=norm(dp-acoustic),
            predicted_peak_Pa=max(abs(dp[m]))*12e-9, observed_peak_Pa=max(abs(observed[m])),
            observed_rms_Pa=norm(observed), error_rms_Pa=norm(observed-dp*12e-9),
            acoustic_error_rms_Pa=norm(observed-acoustic*12e-9))
    report['signed_outflux_kg_m_s'] = total[:, 0].sum()
    report['absolute_outflux_sum_kg_m_s'] = abs(total[:, 0]).sum()
    report['wall_max_speed_m_s'] = np.linalg.norm(u[wall], axis=1).max()
    return report


def projection(matrix, vol, rho, wall, mass):
    """Minimum kinetic-norm correction, subject to a small weighted residual.

    The damped least-squares solution also minimizes the kinetic norm on
    its achieved residual-norm sublevel set. Row weights give the dual-area
    integral of squared density rate; fixed wall columns are excluded.
    """
    free = np.ones(2*len(vol), dtype=bool)
    free[(2*wall[:, None]+np.arange(2)).ravel()] = False
    inv_weight = np.repeat(1/np.sqrt(vol*rho), 2)[free]
    op = matrix[:, free].multiply(inv_weight).multiply((1/np.sqrt(vol))[:, None]).tocsr()
    scale = np.max(np.asarray(abs(op).sum(axis=1)))
    op /= scale
    rhs = -mass/(np.sqrt(vol)*scale)
    damping = 1e-4
    sol = lsqr(op, rhs, damp=damping, atol=1e-12, btol=1e-12, iter_lim=3000)
    x, stop, iterations = sol[:3]
    change = np.zeros(2*len(vol))
    change[free] = x*inv_weight
    defect = op@x-rhs
    gradient = op.T@defect+damping**2*x
    audit = dict(lsqr_stop=stop, iterations=iterations, damping=damping,
                 scale=float(scale), estimated_augmented_condition=sol[6],
                 relative_normal_defect=float(np.linalg.norm(gradient)/np.linalg.norm(op.T@rhs)),
                 weighted_residual_ratio=float(np.linalg.norm(defect)/np.linalg.norm(rhs)),
                 correction_kinetic_norm2=float(x@x))
    if audit['relative_normal_defect'] > 1e-7:
        raise ValueError(f'Unconverged projection: {audit}')
    return change.reshape(-1, 2), audit


def prepare(source, dest):
    xy, cells, wall = mesh(32, True)
    state = read_restart(source/'state_00000.dat')
    np.testing.assert_array_equal(xy, np.column_stack((state['x'], state['y'])))
    q = conservative(state)
    rho = q[:, 0].copy()
    vol, _ = dual_geometry(xy, cells, wall)
    u = q[:, 1:3]/rho[:, None]
    change, audit = projection(mass_matrix(xy, cells, rho), vol, rho, wall, residual(source)[:, 0])
    q[:, 1:3] = rho[:, None]*(u+change)
    # Add only the kinetic increment to retain the historical liquid internal energy.
    q[:, 3] += rho*(change*(u+.5*change)).sum(axis=1)
    dest.mkdir(exist_ok=False)
    for name in ('wave.cfg', 'line.su2'):
        shutil.copyfile(source/name, dest/name)
    write_restart(dest, np.column_stack((xy, q)))
    return audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    for mode, names in [('baseline', ('source', 'centered', 'endpoint')),
                        ('project', ('source', 'dest'))]:
        command = sub.add_parser(mode)
        for name in names:
            command.add_argument(name, type=Path)
    args = vars(parser.parse_args())
    func = baseline if args.pop('mode') == 'baseline' else prepare
    print(json.dumps(func(**args), indent=2, allow_nan=False))
