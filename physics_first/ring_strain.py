"""Free-space, time-zero Gaussian ring quadrature. All internal quantities are SI."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.special import gammainc

RADIUS = 0.015
HALF_SPACING = 0.019
CORE = 0.002
GAMMA = 0.0018
NU = 1.0034e-6
SAMPLES = 128
LEVELS = (128, 256, 512)
TOL = 0.02  # s^-1, for the projected rates
AXES = np.eye(3)


def ring(sign, count):
    """Positions and oriented unit tangents. Basis e1 x e_y points along flight."""
    theta = np.arange(count) * (2 * np.pi / count)
    e1 = np.array([np.cos(np.pi / 6), 0, sign * np.sin(np.pi / 6)])
    radial = np.outer(np.cos(theta), e1) + np.outer(np.sin(theta), AXES[1])
    tangent = np.outer(-np.sin(theta), e1) + np.outer(np.cos(theta), AXES[1])
    return sign * HALF_SPACING * AXES[0] + RADIUS * radial, tangent


def radial_factor(q2, order):
    """Dimensionless K a^3 or (K'/r) a^5 with finite coincident limits."""
    power, scale, limit = ((1.5, 1, 4/3) if order == 0 else (2.5, -3, -8/5))
    result = np.full_like(q2, limit / np.sqrt(np.pi))
    return np.divide(scale * gammainc(power, q2), q2**power, out=result, where=q2 > 0)


def field(targets, source, dl, velocity_only=False):
    """Integrate u, J_ij = du_i/dx_j, omega and its vector Laplacian for one loop."""
    r = targets[:, None, :] - source
    q2 = np.einsum('...i,...i->...', r, r) / CORE**2
    weights = GAMMA / (4 * np.pi) * dl
    cross = np.cross(weights, r)
    k = radial_factor(q2, 0) / CORE**3
    velocity = np.einsum('ts,tsi->ti', k, cross)
    if velocity_only:
        return velocity
    derivative = radial_factor(q2, 1) / CORE**5
    gradient = np.stack([k @ np.cross(weights, axis) for axis in AXES], axis=-1)
    gradient += np.einsum('ts,tsi,tsj->tij', derivative, cross, r)
    gaussian = np.exp(-q2) / (np.pi**1.5 * CORE**3)
    omega = GAMMA * gaussian @ dl
    laplacian = GAMMA * (gaussian * (4*q2 - 6) / CORE**2) @ dl
    return velocity, gradient, omega, laplacian


def dot(x, y):
    return np.einsum('...i,...i->...', x, y)


def project(gradient, axis):
    # The antisymmetric part vanishes in the quadratic form.
    return np.einsum('ti,tij,tj->t', axis, gradient, axis)


def maximum(x):
    return float(np.max(np.abs(x)))


def measure(sign, count):
    points, tangent = ring(sign, SAMPLES)
    sources = []
    for side in (sign, -sign):
        source, unit = ring(side, count)
        sources.append((source, unit * (2 * np.pi * RADIUS / count)))
    own, other = (field(points, *source) for source in sources)
    u, jac, omega, lap = (a+b for a, b in zip(own, other))
    mag = np.linalg.norm(omega, axis=1)
    axis = omega / mag[:, None]
    own_mag = np.linalg.norm(own[2], axis=1)
    iso_axis = own[2] / own_mag[:, None]
    s = project(jac, axis)
    visc = NU * dot(lap, axis) / mag
    iso_visc = NU * dot(own[3], iso_axis) / own_mag
    curl = np.stack([jac[:, k, j] - jac[:, j, k]
                     for j, k in ((1, 2), (2, 0), (0, 1))], axis=1)
    values = dict(position_m=points, tangent=tangent, omega_hat=axis,
                  angle_deg=np.rad2deg(np.arctan2(np.linalg.norm(np.cross(axis, tangent), axis=1),
                                                   dot(axis, tangent))),
                  omega_s_inv=mag, u_m_s=u, J_s_inv=jac,
                  partner_u_m_s=other[0], partner_J_s_inv=other[1],
                  iso_u_m_s=own[0], iso_J_s_inv=own[1], iso_omega_s_inv=own_mag,
                  s=s, self_s=project(own[1], axis), partner_s=project(other[1], axis),
                  tangent_self_s=project(own[1], tangent), tangent_partner_s=project(other[1], tangent),
                  self_visc=NU * dot(own[3], axis) / mag,
                  partner_visc=NU * dot(other[3], axis) / mag, visc=visc, net=s+visc,
                  stretch_abs=mag*s, visc_abs=mag*visc, net_abs=mag*(s+visc),
                  iso_s=project(own[1], iso_axis), iso_visc=iso_visc,
                  iso_net=project(own[1], iso_axis)+iso_visc)
    checks = dict(div_u=maximum(np.trace(jac, axis1=1, axis2=2)), curl_minus_omega=maximum(curl-omega),
                  iso_speed_spread=np.ptp(np.linalg.norm(own[0], axis=1)), iso_s=maximum(values['iso_s']),
                  iso_visc_spread=np.ptp(iso_visc), iso_omega_spread=np.ptp(own_mag),
                  split_s=maximum(s-values['self_s']-values['partner_s']),
                  split_visc=maximum(visc-values['self_visc']-values['partner_visc']))
    for divisor in (8, 16):
        h = CORE / divisor
        fd = []
        for source in sources:
            def centered(direction):
                plus = field(points+h*direction, *source, velocity_only=True)
                minus = field(points-h*direction, *source, velocity_only=True)
                return (plus-minus) / (2*h)
            # Also difference along omega_hat directly, holding each target's axis fixed.
            fd.append((np.stack([centered(e) for e in AXES], axis=-1), centered(axis)))
        for name, grad, fd_j, directional in (
                ('partner', other[1], *fd[1]),
                ('pair', jac, fd[0][0]+fd[1][0], fd[0][1]+fd[1][1])):
            prefix = f'fd_a{divisor}_{name}'
            checks[prefix+'_J'] = maximum(fd_j-grad)
            checks[prefix+'_s'] = maximum(project(fd_j-grad, axis))
            checks[prefix+'_directional_s'] = maximum(dot(directional, axis)-project(grad, axis))
    return values, checks


def analyze():
    summary = {'tolerance_s_inv': TOL, 'levels': {}, 'changes': {}}
    previous = None
    for n in LEVELS:
        (left, lc), (right, rc) = (measure(sign, n) for sign in (-1, 1))
        checks = {key: max(lc[key], rc[key]) for key in lc}
        idx = np.arange(SAMPLES)
        for name, lookup, mirror, target in (
                ('x', (SAMPLES//2-idx) % SAMPLES, np.array([-1, 1, 1]), right),
                ('y', (-idx) % SAMPLES, np.array([1, -1, 1]), left)):
            checks['mirror_'+name+'_rates'] = max(maximum(left[k]-target[k][lookup])
                                                  for k in ('s', 'visc', 'net'))
            checks['mirror_'+name+'_u'] = maximum(left['u_m_s']*mirror-target['u_m_s'][lookup])
            checks['mirror_'+name+'_J'] = maximum(left['J_s_inv']*np.outer(mirror, mirror)
                                                  -target['J_s_inv'][lookup])
            # Vorticity is an axial vector under a reflection.
            checks['mirror_'+name+'_axis'] = maximum(-left['omega_hat']*mirror-target['omega_hat'][lookup])
        fields = {key: np.concatenate((v, right[key])) for key, v in left.items()}
        ranges = {key: [float(fields[key].min()), float(fields[key].max())] for key in
                  ('s', 'self_s', 'partner_s', 'visc', 'net', 'net_abs', 'angle_deg', 'omega_s_inv')}
        summary['levels'][n] = dict(ranges=ranges, max_errors=checks)
        if previous is not None:
            summary['changes'][n] = {key: maximum(fields[key]-previous[key]) for key in
                                     ('s', 'partner_s', 'visc', 'net', 'iso_s', 'iso_visc', 'u_m_s', 'J_s_inv')}
        previous = fields
    # The design specifies convergence of projected rates and an independent partner strain.
    checks = summary['levels'][LEVELS[-1]]['max_errors']
    fine = summary['changes'][LEVELS[-1]]
    agreement = {'fine_'+k: fine[k] < TOL for k in ('s', 'partner_s', 'visc', 'iso_s', 'iso_visc')}
    for divisor in (8, 16):
        for suffix in ('partner_s', 'pair_s', 'partner_directional_s', 'pair_directional_s'):
            key = f'fd_a{divisor}_{suffix}'
            agreement[key] = checks[key] < TOL
    symmetry = ('div_u', 'curl_minus_omega', 'iso_s', 'iso_visc_spread', 'iso_speed_spread',
                'iso_omega_spread', 'split_s', 'split_visc', *(k for k in checks if k.startswith('mirror_')))
    agreement.update({k: bool(checks[k] < 1e-9) for k in symmetry})
    summary['gates'] = agreement
    summary['passed'] = all(agreement.values())
    return summary, fields


def write_samples(path, fields):
    columns = dict(ring=np.repeat(['left', 'right'], SAMPLES),
                   azimuth_deg=np.tile(np.arange(SAMPLES)*360/SAMPLES, 2))
    for name, values in fields.items():
        for index in np.ndindex(values.shape[1:]):
            suffix = ''.join('xyz'[i] for i in index)
            columns[name + ('_'+suffix if suffix else '')] = values[(slice(None), *index)]
    with path.open('w', newline='') as out:
        writer = csv.writer(out, lineterminator='\n')
        writer.writerow(columns)
        writer.writerows(zip(*columns.values(), strict=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='output directory for JSON checks and finest CSV')
    destination = parser.parse_args().directory
    destination.mkdir(parents=True, exist_ok=True)
    summary, fields = analyze()
    (destination / 'ring_strain.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    write_samples(destination / 'ring_strain.csv', fields)
    raise SystemExit(0 if summary['passed'] else 1)
