"""Fixed-gap centerline budgets and circulation thresholds. SI internally."""
import argparse
import csv
import json
from pathlib import Path

import numpy as np

from . import ring_strain as rs

ORIGINAL = 2*(rs.HALF_SPACING - rs.RADIUS*np.cos(np.pi/6))
GAPS = (ORIGINAL, .010, .008)
CORES = (.0015, rs.CORE, .0025)


def placement(gap, tilt=np.pi/6):
    return dict(half_spacing=gap/2 + rs.RADIUS*np.cos(tilt), tilt=tilt)


def write_csv(path, rows):
    with path.open('w', newline='') as out:
        w = csv.DictWriter(out, fieldnames=rows[0], lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def centerlines(folder):
    rows = []
    validation = {}
    for gap in GAPS:
        key = f'{gap*1000:.6f}'
        check, values = rs.analyze(**placement(gap))
        validation[key] = check
        for i in range(2*rs.SAMPLES):
            rows.append(dict(gap_mm=gap*1000, side=(-1, 1)[i//rs.SAMPLES],
                             theta_deg=(i % rs.SAMPLES)*360/rs.SAMPLES,
                             **{k: values[k][i] for k in
                                ('omega_s_inv', 's', 'visc', 'net', 'net_abs', 'iso_net')}))
    write_csv(folder/'centerlines.csv', rows)
    (folder/'gap_checks.json').write_text(json.dumps(validation, indent=2, allow_nan=False)+'\n')
    return all(v['passed'] for v in validation.values())


def critical(gap, core):
    # Reflection maps the right ring onto the left. Search all targets on the left.
    opts = dict(**placement(gap), core=core)
    def at(gamma, n=512):
        return rs.measure(-1, n, **opts, gamma=gamma, fd_divisors=())[0]

    base = at(rs.GAMMA)
    ratios = np.where(base['s'] > 0, -base['visc']/base['s'], np.inf)
    i = np.argmin(ratios)
    gamma = rs.GAMMA*ratios[i]
    rates = [at(f*gamma)['net'].max() for f in (.99, 1., 1.01)]
    direct, checks = rs.measure(-1,512,**opts,gamma=gamma,fd_divisors=(8,16,32))
    middle = at(gamma, 256)
    coarse = at(gamma, 128)
    swirl = gamma*(1-np.exp(-1.121**2))/(2*np.pi*1.121*core)
    # Integral rho * integral(v_theta^2/r dr), straight Gaussian from axis to infinity.
    deficit = 998*(gamma/(2*np.pi*core))**2*np.log(2)
    return dict(gap_mm=gap*1000, a_mm=core*1000, gamma_m2_s=gamma,
                left_theta_deg=i*360/rs.SAMPLES, Re_gamma=gamma/rs.NU,
                swirl_m_s=swirl, isolated_line_m_s=np.linalg.norm(direct['iso_u_m_s'][i]),
                swirl_Mach=swirl/1482, straight_deficit_Pa=deficit,
                single_tail_midpoint=np.exp(-(gap/(2*core))**2),
                max_net_99=rates[0], max_net_100=rates[1], max_net_101=rates[2],
                coarse_change=max(rs.maximum(middle[k]-coarse[k]) for k in ('s','visc','net')),
                fine_change=max(rs.maximum(direct[k]-middle[k]) for k in ('s','visc','net')),
                **{f'fd_a{d}': max(checks[f'fd_a{d}_{kind}'] for kind in
                                   ('pair_s','partner_s','pair_directional_s','partner_directional_s'))
                   for d in (8,16,32)})


def main(folder):
    folder.mkdir(parents=True, exist_ok=True)
    passed = centerlines(folder)
    rows = [critical(gap, core) for gap in GAPS for core in CORES]
    write_csv(folder/'critical.csv', rows)
    return passed and all(r['max_net_99'] < 0 < r['max_net_101'] and
                          abs(r['max_net_100']) < 1e-9 and max(r[k] for k in ('coarse_change','fine_change','fd_a8','fd_a16','fd_a32')) < rs.TOL
                          for r in rows)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    raise SystemExit(0 if main(parser.parse_args().directory) else 1)
