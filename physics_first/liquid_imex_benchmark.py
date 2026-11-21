"""Run the bounded ambient-water benchmark or remeasure its archived fields."""
import argparse
import json
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from .liquid_imex import Liquid, LENGTH, P0, T0, step

LD = np.longdouble
EPS = np.finfo(float).eps


def flash(w, U):
    """Independent absolute (D,U) flash and Simpson dp integral on that path."""
    s = CP.AbstractState("HEOS", "Water")
    dr, m, H = U
    rho = w.rho + dr
    de = H / rho - 0.5 * (m / rho)**2
    out = np.empty((4, len(m)))
    for i in range(len(m)):
        total = 0.
        for fraction, weight in ((0., 1.), (0.5, 4.), (1., 1.)):
            s.update(CP.DmassUmass_INPUTS, w.rho + fraction * dr[i], w.e + fraction * de[i])
            total += weight * (dr[i] * s.first_partial_deriv(CP.iP, CP.iDmass, CP.iUmass)
                               + de[i] * s.first_partial_deriv(CP.iP, CP.iUmass, CP.iDmass))
        if s.phase() != CP.iphase_liquid:
            raise ValueError("checkpoint outside liquid branch")
        out[:, i] = [s.p() - P0, total / 6, s.T(), s.speed_sound()]
    return out


def integrate(w, n, steps, amplitude, direction, tol=2e-11):
    dx, dt = LENGTH / n, LENGTH / (w.c * steps)
    U = w.initialize(n, amplitude, direction)
    history = [np.vstack((U, w.primitive(U)[2]))]
    residuals = np.zeros(3)
    # Accumulate actual local update roundoff and a floating-point absolute bound.
    bounds, observed = np.zeros(3, dtype=LD), np.zeros(3, dtype=LD)
    peak_pressure = 0.
    for j in range(steps):
        V, p, flux, res = step(w, U, dt, dx, tol)
        residuals = np.maximum(residuals, res)
        f = flux.astype(LD)
        left = np.roll(f, 1, axis=1)
        defect = V.astype(LD) - U + (dt / dx) * (f - left)
        observed += dx * np.sum(abs(defect), axis=1)
        bounds += 4 * EPS * dx * np.sum(abs(U) + (dt / dx) * (abs(left) + abs(f)), axis=1)
        peak_pressure = max(peak_pressure, np.max(abs(p)))
        U = V
        if (j + 1) % (steps // 4) == 0:
            history.append(np.vstack((U, p)))
    return np.array(history), dict(max_nonlinear_Pa=residuals[0], max_linear_Pa=residuals[1],
                                   max_corrections=int(residuals[2]), peak_pressure_Pa=peak_pressure,
                                   summed_local_error=np.asarray(observed, float).tolist(),
                                   roundoff_budget=np.asarray(bounds, float).tolist())


def measure(w, history, steps, amplitude, direction):
    n = history.shape[-1]
    dx = LENGTH / n
    modes, snapshots = [], []
    basis = np.exp(-2j * np.pi * (np.arange(n) + 0.5) / n)
    for U0, U1 in zip([history[0], *history[:-1]], history):
        U, p = U1[:3], U1[3]
        raw, recovered, temperature, sound = flash(w, U)
        modes.append(2 * np.mean(recovered * basis))
        raw_mode = 2 * np.mean(raw * basis)
        rho = w.rho + U[0]
        velocity = U[1] / rho
        # Difference the small conservative variables before volume integration.
        delta = U.astype(LD) - U0[:3].astype(LD)
        inventories = dx * np.sum(delta, axis=1)
        absolute = dx * np.sum(delta[2] + LD(w.e) * delta[0])
        packed = (U[2] + w.e * rho) - (U0[2] + w.e * (w.rho + U0[0]))
        wave = dx * np.sum(0.5 * (recovered**2 / (w.rho * w.c**2) + w.rho * velocity**2))
        snapshots.append(dict(d_inventory=np.array(inventories, float).tolist(),
                              d_absolute_J_m2=float(absolute), d_repacked_J_m2=float(dx*np.sum(packed)),
                              wave_J_m2=wave, pressure_mode_Pa=[modes[-1].real, modes[-1].imag],
                              pimplicit_vs_integral_Pa=max(abs(p - recovered)),
                              pimplicit_vs_flash_Pa=max(abs(p - raw)),
                              raw_mode_Pa=[raw_mode.real, raw_mode.imag],
                              p_abs_Pa=[min(raw)+P0, max(raw)+P0],
                              rho_kg_m3=[min(rho), max(rho)], T_K=[min(temperature), max(temperature)],
                              c_m_s=[min(sound), max(sound)]))
    raw_modes = [complex(*q['raw_mode_Pa']) for q in snapshots]
    raw_phase = np.unwrap(np.angle(raw_modes))
    raw_speed = -(raw_phase[-1] - raw_phase[0]) * w.c / (2 * np.pi)
    phase = np.unwrap(np.angle(modes))
    speed = -(phase[-1] - phase[0]) * w.c / (2 * np.pi)
    return dict(n=n, steps=steps, amplitude_Pa=amplitude, direction=direction, cfl=n/steps,
                speed_m_s=speed, speed_error=speed/(direction*w.c)-1,
                raw_speed_error=raw_speed/(direction*w.c)-1,
                raw_amplitude_error=abs(raw_modes[-1])/amplitude-1,
                final_amplitude_Pa=abs(modes[-1]), amplitude_error=abs(modes[-1])/amplitude-1,
                quarters=snapshots)


def qualify(rows):
    """All resolved runs, both independent refinements and every checkpoint."""
    checks = {}
    checks['phase_amplitude'] = all(abs(r[key]) < 0.01 for r in rows
                                    for key in ('speed_error', 'amplitude_error',
                                                'raw_speed_error', 'raw_amplitude_error'))
    checks['EOS'] = all(q['pimplicit_vs_integral_Pa'] < 1e-9 and q['pimplicit_vs_flash_Pa'] < 1e-3
                        for r in rows for q in r['quarters'])
    checks['pressure_solve'] = all(r['max_linear_Pa'] < 2e-11 and r['max_nonlinear_Pa'] <= 2e-11
                                   for r in rows)
    checks['inventories'] = True
    for r in rows:
        budget = np.array(r['roundoff_budget'])
        for q in r['quarters']:
            absolute_budget = budget[2] + r['e_ref'] * budget[0]
            if (abs(q['d_absolute_J_m2']) > absolute_budget or
                    np.any(abs(np.array(q['d_inventory'])) > budget)):
                checks['inventories'] = False
        checks['inventories'] &= bool(np.all(r['summed_local_error'] <= budget))
    orders = {}
    for amp in (10, 100):
        for sign in (-1, 1):
            subset = {(r['n'], r['steps']): r for r in rows
                      if r['amplitude_Pa'] == amp and r['direction'] == sign}
            for axis, triplet in [('space', [(32, 512), (64, 512), (128, 512)]),
                                  ('time', [(128, 128), (128, 256), (128, 512)])]:
                for quantity in ('speed_m_s', 'final_amplitude_Pa'):
                    a, b, c = [subset[x][quantity] for x in triplet]
                    orders[f'{axis}_{quantity}_{amp}_{sign}'] = np.log2((a-b)/(b-c))
    checks['independent_orders'] = all(1.8 < order < 2.2 for order in orders.values())
    return checks, orders


def precision(w):
    s = CP.AbstractState("HEOS", "Water")
    rows = []
    for a in (100., 10., 1., .01, .001, .0001, .00001, .000001):
        U = w.initialize(16, a, 1)
        V, p, _, res = step(w, U, LENGTH/(w.c*64), LENGTH/16, tol=max(1e-17, 2e-13*a))
        raw, integrated, _, _ = flash(w, V)
        internal = V[2]/(w.rho + V[0]) - 0.5*(V[1]/(w.rho+V[0]))**2
        rows.append(dict(peak_input_Pa=a, implicit_vs_integral_Pa=max(abs(p-integrated)),
                         implicit_vs_abs_flash_Pa=max(abs(p-raw)), nonlinear_Pa=res[0], linear_Pa=res[1],
                         rho_repack_error_kg_m3=max(abs((w.rho + V[0]) - w.rho - V[0])),
                         e_repack_error_J_kg=max(abs((w.e + internal) - w.e - internal)),
                         shifted_energy_ulp_J_m3=np.spacing(max(abs(V[2])))))
    gradients = []
    for var, delta in ((CP.iDmass, .001), (CP.iUmass, .5)):
        other = CP.iUmass if var == CP.iDmass else CP.iDmass
        pressures = []
        for sign in (-1, 1):
            s.update(CP.DmassUmass_INPUTS, w.rho + (var == CP.iDmass)*sign*delta,
                     w.e + (var == CP.iUmass)*sign*delta)
            pressures.append(s.p())
        s.update(CP.DmassT_INPUTS, w.rho, T0)
        gradients.append([s.first_partial_deriv(CP.iP,var,other),
                          (pressures[1]-pressures[0])/(2*delta)])
    return dict(reference=dict(rho=w.rho, e=w.e, c=w.c, mu=w.mu, k=w.k,
                               absolute_energy_ulp_J_m3=np.spacing(w.e*w.rho)),
                derivatives_analytic_and_secant=gradients, steps=rows)


def run(out, replay):
    w = Liquid()
    out.mkdir(parents=True, exist_ok=True)
    cache = np.load(out / 'fields.npz') if replay else {}
    saved = json.loads((out / 'solves.json').read_text()) if replay else {}
    def case(n, steps, a, sign, tol=2e-11, inviscid=False):
        key = f'n{n}_m{steps}_A{a}_s{sign}_tol{tol:g}'
        fluid = w
        if inviscid:
            key += '_inviscid'
            fluid = Liquid()
            fluid.mu = fluid.k = 0.
        if replay:
            history = cache[key]
        else:
            history, saved[key] = integrate(fluid, n, steps, a, sign, tol)
            cache[key] = history
        return dict(**measure(w, history, steps, a, sign), **saved[key], e_ref=w.e, inviscid=inviscid)
    resolved = [case(n, m, a, s) for a in (10, 100) for s in (1, -1)
                for n in (32, 64, 128) for m in (128, 256, 512)]
    checks, orders = qualify(resolved)
    extra = []
    if all(checks.values()):
        extra = [case(128, m, 10, 1) for m in (16, 4)]
        extra.append(case(128, 256, 10, 1, 2e-12))
        extra.extend(case(128, m, 10, 1, inviscid=True) for m in (16, 4))
    results = dict(precision=precision(w), resolved=resolved, checks=checks, orders=orders, controls=extra)
    if not replay:
        np.savez_compressed(out / 'fields.npz', **cache)
        (out / 'solves.json').write_text(json.dumps(saved, indent=1) + '\n')
    return json.dumps(results, indent=1, allow_nan=False) + '\n', all(checks.values())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--replay', action='store_true')
    args = parser.parse_args()
    report, passed = run(args.directory, args.replay)
    if args.replay:
        if report != (args.directory / 'results.json').read_text():
            raise SystemExit('replay differs from archived measurements')
    else:
        (args.directory / 'results.json').write_text(report)
    raise SystemExit(0 if passed else 1)
