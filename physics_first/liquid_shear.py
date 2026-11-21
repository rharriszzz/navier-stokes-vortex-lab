"""R294 staggered shear validation. SI units, unit depth for inventories."""
import argparse
import json
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from .liquid_imex import Liquid, P0
from .liquid_imex_2d import kinetic, primitive, step
from .measure_shear import fit_decay
from .su2_shear import AMPLITUDE, HEIGHT, LENGTH

LD = np.longdouble
EPS = np.finfo(float).eps
STANDARD = 2e-11


def checkerboard(w):
    """Axis and diagonal Nyquist standing waves. Compare with midpoint acoustics."""
    ny, nx = 4, 32
    dx, dy = LENGTH/nx, HEIGHT/ny
    dt = 0.25*dx/w.c
    amplitude = 1e-4
    j, i = np.indices((ny, nx))
    rows = []
    for inviscid in (True, False):
        material = Liquid() if inviscid else w
        if inviscid:
            material.mu = material.k = 0.
        for ax, ay in ((1, 0), (0, 1), (1, 1)):
            mode = (-1.)**(ax*i+ay*j)
            r = amplitude*mode/w.c**2
            U = np.array([r, 0*r, 0*r, (w.rho+r)*r*P0/w.rho**2])
            freq = 2*w.c*np.hypot(ax/dx, ay/dy)
            angle = 2*np.arctan(dt*freq/2)
            history, momentum, theory = [], [], []
            for n in range(1, 17):
                U, p, _, _ = step(material, U, dt, dx, dy, 2e-14)
                history.append(float(np.mean(mode*p)/amplitude))
                # Linear continuity predicts face momentum in phase with mode.
                momentum.append([float(np.mean(mode*m)*w.c/amplitude) for m in U[1:3]])
                theory.append(np.cos(n*angle))
            error = float(np.max(np.abs(np.array(history)-theory)))
            normal = np.array([ax/dx, ay/dy])/np.hypot(ax/dx, ay/dy)
            m_err = float(np.max(np.abs(momentum-np.outer(np.sin(np.arange(1,17)*angle), normal))))
            # Finite viscosity changes mode amplitude on this short window.
            limit = 1e-8 if inviscid else .10
            rows.append(dict(axes=[ax, ay], inviscid=inviscid, dt_s=dt,
                             pressure_over_initial=history, face_momentum_scaled=momentum,
                             max_pressure_error_vs_inviscid=error, max_momentum_error_vs_inviscid=m_err,
                             **{"pass": bool(error < limit and m_err < limit and min(history) < -.8
                                and max(abs(np.array(history))) <= 1+1e-8)}))
    return rows


def initial(w, nx, ny, shifted):
    U = np.zeros((4, ny, nx))
    x = (np.arange(nx) - (nx//4 if shifted else 0)) % nx
    U[2] = w.rho*AMPLITUDE*np.sin(2*np.pi*x/nx)
    U[3] = kinetic(w, U)[2]
    return U


def checkpoint(w, U, U0, p, elapsed, audit):
    area = LENGTH*HEIGHT
    # Independent dual-volume KE in extended precision, using adjacent masses.
    def energy(q):
        r, mx, my, _ = q.astype(LD)
        return (mx**2/(2*w.rho+r+np.roll(r,-1,axis=1))
                + my**2/(2*w.rho+r+np.roll(r,-1,axis=0))).mean()
    ke, ke0 = energy(U), energy(U0)
    u, v, _, de, recovered, temp = primitive(w, U)
    rho = w.rho+U[0]
    # Verify the phase in an absolute Helmholtz flash, and recover pressure
    # independently by Simpson integration with native (rho,e) derivatives.
    exact = np.empty_like(de)
    pairs, indices = np.unique(np.stack([U[0].ravel(), de.ravel()]), axis=1, return_inverse=True)
    independent = []
    for dr, delta_e in pairs.T:
        dp = 0.
        for a, b in ((0., 1.), (.5, 4.), (1., 1.)):
            s = w.state
            s.update(CP.DmassUmass_INPUTS, w.rho+a*dr, w.e+a*delta_e)
            if s.phase() != CP.iphase_liquid:
                raise ValueError("checkpoint outside liquid branch")
            dp += b*(dr*s.first_partial_deriv(CP.iP, CP.iDmass, CP.iUmass)
                     + delta_e*s.first_partial_deriv(CP.iP, CP.iUmass, CP.iDmass))/6
        independent.append(dp)
    exact.flat[:] = np.array(independent)[indices]
    wave = 2*np.mean(v*np.exp(-2j*np.pi*np.arange(p.shape[1])/p.shape[1]))
    drift = (U.astype(LD)-U0).mean(axis=(1,2))*area
    loss = float((ke0-ke)*area)
    internal = float((de.astype(LD)*rho).mean()*area)
    # Initial internal increment is zero by construction. Endpoint KE storage
    # and subtraction bound plus accumulated H update budget.
    thermal_precision = audit["allowance"][3] + 16*EPS*float((abs(U[3]).mean()+ke0+ke)*area)
    return dict(time_s=elapsed, amplitude_m_s=float(abs(wave)), phase_rad=float(np.angle(wave)),
                kinetic_J_m=float(ke*area), kinetic_loss_J_m=loss, internal_gain_J_m=internal,
                conversion_precision_J_m=thermal_precision,
                stress_integral_J_m=audit["stress"], pressure_dilatation_J_m=audit["pdil"],
                internal_minus_stress_plus_pdil_J_m=internal-audit["stress"]+audit["pdil"],
                inventory_drift=drift.astype(float).tolist(), roundoff_bound=audit["allowance"].tolist(),
                absolute_local_defects=audit["defect"].tolist(), max_pressure_residual_Pa=audit["res"],
                max_corrections=audit["iters"], max_abs_u_m_s=float(abs(u).max()),
                dp_min_mean_max_Pa=[float(f(recovered)) for f in (np.min, np.mean, np.max)],
                max_strip_range_Pa=float(np.ptp(exact, axis=0).max()),
                trial_strip_max_Pa=float(np.ptp(p, axis=0).max()),
                strip_range_by_x_Pa=np.ptp(exact, axis=0).tolist(),
                independent_minus_trial_max_Pa=float(abs(exact-p).max()),
                max_abs_dr_kg_m3=float(abs(U[0]).max()),
                dT_min_mean_max_K=[float(f(temp)) for f in (np.min, np.mean, np.max)]), exact


def integrate(w, nx, ny, steps, shifted, tol):
    dx, dy = LENGTH/nx, HEIGHT/ny
    dt = 8*LENGTH/(steps*w.c)
    U0 = initial(w,nx,ny,shifted)
    U = U0.copy()
    audit = dict(allowance=np.zeros(4), defect=np.zeros(4), stress=0., pdil=0., res=0., iters=0)
    snapshots, fields = [], []
    p = primitive(w,U)[4]
    for n in range(steps+1):
        if n % (steps//4) == 0:
            row, exact = checkpoint(w,U,U0,p,n*dt,audit)
            snapshots.append(row)
            fields.append(np.concatenate([U, p[None], exact[None]]))
        if n == steps:
            break
        V, p, flux, (res, iters, power, pdil) = step(w,U,dt,dx,dy,tol)
        # Whole-trajectory liquid neighborhood guard. Independent phase
        # classification is also performed on each saved conservative field.
        if not (np.isfinite(V).all() and np.max(abs(p)) < 1 and np.max(abs(V[0])) < 1e-5
                and np.max(abs(V[3])) < 1 and np.max(abs(V[1:3])) < 20):
            raise ArithmeticError("state outside near-ambient shear envelope")
        fx, fy = (a.astype(LD) for a in flux)
        ex, ey = np.roll(fx,1,axis=2), np.roll(fy,1,axis=1)
        predicted = dt*((fx-ex)/dx + (fy-ey)/dy)
        audit["defect"] += np.sum(abs(V.astype(LD)-U+predicted),axis=(1,2))*dx*dy
        scale = abs(U) + dt*((abs(fx)+abs(ex))/dx + (abs(fy)+abs(ey))/dy)
        audit["allowance"] += 8*EPS*np.sum(scale,axis=(1,2))*dx*dy
        audit["stress"] += dt*power*LENGTH*HEIGHT
        audit["pdil"] += dt*pdil*LENGTH*HEIGHT
        audit["res"] = max(audit["res"],res)
        audit["iters"] = max(audit["iters"],iters)
        U = V
    times = np.array([s["time_s"] for s in snapshots])
    amps = np.array([s["amplitude_m_s"] for s in snapshots])
    energies = np.array([s["kinetic_J_m"] for s in snapshots])
    nu, intervals = fit_decay(times, amps)
    nu_ke, kinetic_intervals = fit_decay(times, np.sqrt(energies))
    for index, row in enumerate(snapshots[1:]):
        row.update(interval_nu_m2_s=intervals[index], interval_kinetic_nu_m2_s=kinetic_intervals[index])
    return dict(nx=nx, ny=ny, steps=steps, shifted=shifted, tol_Pa=tol, dt_s=dt,
                nu_m2_s=nu, kinetic_nu_m2_s=nu_ke, checkpoints=snapshots), np.asarray(fields)


def gates(row, material_nu):
    checks = []
    for s in row["checkpoints"]:
        allowance = np.array(s["roundoff_bound"])
        checks.extend([max(s["trial_strip_max_Pa"], s["max_strip_range_Pa"]) <= .001, s["independent_minus_trial_max_Pa"] <= .001,
                       np.all(abs(np.array(s["inventory_drift"])) <= allowance),
                       np.all(s["absolute_local_defects"] <= allowance),
                       s["max_pressure_residual_Pa"] <= row["tol_Pa"]])
        if s["time_s"] > 0 and material_nu:
            checks.extend([abs(s[key]/material_nu-1)<.05 for key in
                           ("interval_nu_m2_s", "interval_kinetic_nu_m2_s")])
            checks.append(abs(s["internal_gain_J_m"]-s["kinetic_loss_J_m"]) <= s["conversion_precision_J_m"])
            checks.append(abs(s["internal_minus_stress_plus_pdil_J_m"]) < .05*s["kinetic_loss_J_m"])
    return bool(all(checks))


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False)+"\n")


def run(directory, pilot):
    directory.mkdir(exist_ok=True, parents=True)
    w = Liquid()
    physical = w.mu/w.rho
    modes = checkerboard(w)
    write_json(directory/"pressure_modes.json", modes)
    if not all(row["pass"] for row in modes):
        raise SystemExit("alternating pressure gate failed")
    # Same historical physical steps at each resolution. Additional controls
    # isolate strip height resolution, nonlinear tolerance and temporal order.
    cases = [(32,4,256,False,STANDARD)]
    if not pilot:
        pilot_result = json.loads((directory/"pilot.json").read_text())
        if not pilot_result["pass"]:
            raise SystemExit("pilot gate failed")
        cases = [(nx,4,n,s,STANDARD) for nx in (32,64,128) for n in (2048,4096)
                 for s in (False,True)]
        cases += [(64,8,2048,False,STANDARD), (64,4,2048,False,STANDARD/10),
                  (32,4,512,False,STANDARD), (32,4,1024,False,STANDARD),
                  (64,4,2048,False,2e-16)]
    rows, fields, pairs = {}, {}, {}
    name = "pilot" if pilot else "matrix"
    def save(passed):
        write_json(directory/(name+".json"),dict(physical_nu_m2_s=physical, cases=rows,
                                                   aligned_max_Pa=pairs, **{"pass": bool(passed)}))
        np.savez_compressed(directory/(name+".npz"), **fields)
    for nx, ny, n, shifted, tol in cases:
        key = f"{nx}x{ny}_{n}_{int(shifted)}_{tol:g}"
        row, raw = integrate(w,nx,ny,n,shifted,tol)
        fields[key], rows[key] = raw, row
        good = gates(row,physical)
        if shifted:
            ref = fields[f"{nx}x{ny}_{n}_0_{tol:g}"]
            aligned = np.roll(raw, -(nx//4), axis=-1)
            pairs[key] = np.max(abs(aligned[:,4:]-ref[:,4:]),axis=(1,2,3)).tolist()
            good &= np.array_equal(aligned[0],ref[0]) and max(pairs[key]) <= .001
        for prev in list(rows.values())[:-1]:
            # All cases share the same physical viscosity and rate targets.
            good &= abs(row["nu_m2_s"]-prev["nu_m2_s"]) < .05*physical
        save(False)  # A partial matrix has yet to pass its combined gates.
        print(key, "pass" if good else "FAIL", flush=True)
        if not good:
            raise SystemExit(1)
    if pilot:
        save(True)
    else:
        def nu(nx,n):
            return rows[f"{nx}x4_{n}_0_{STANDARD:g}"]["nu_m2_s"]
        space_ratio = (nu(32,2048)-nu(64,2048))/(nu(64,2048)-nu(128,2048))
        time_ratio = (pilot_result["cases"]["32x4_256_0_2e-11"]["nu_m2_s"]-nu(32,512))/(nu(32,512)-nu(32,1024))
        passed = 3 < space_ratio < 5 and 3 < time_ratio < 5
        write_json(directory/"refinement.json",dict(spatial_ratio=space_ratio, temporal_ratio=time_ratio,
                                                    **{"pass":bool(passed)}))
        save(passed)
        if not passed:
            raise SystemExit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    run(args.directory,args.pilot)
