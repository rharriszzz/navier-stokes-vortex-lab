"""Compare conservative disk endpoints, including EOS recovery, to viscous swirl."""

import argparse
import json
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np
from scipy.spatial import cKDTree

from physics_first.acoustic_initial_state import background, T0
from physics_first.cylinder_spreading import INITIAL, INNER
from physics_first.disk_time_cases import CASES
from physics_first.rotating_disk import dual_geometry, mesh
from physics_first.su2_acoustic import FIELDS, read_restart


def flash(q):
    rho = q[:, 0]
    u = q[:, 1:3]/rho[:, None]
    pairs, idx = np.unique(np.column_stack((rho, q[:, 3]/rho-.5*(u*u).sum(axis=1))),
                           axis=0, return_inverse=True)
    p, t = np.empty((2, len(pairs)))
    eos = CP.AbstractState("HEOS", "Water")
    for j, (d, e) in enumerate(pairs):
        eos.update(CP.DmassUmass_INPUTS, d, e)
        if eos.phase() != CP.iphase_liquid:
            raise ValueError("non-liquid endpoint")
        p[j], t[j] = eos.p(), eos.T()
    return p[idx], t[idx]


def peak_fit(r, ut, selected):
    ids = np.flatnonzero(selected & (r < .02))
    ids = ids[np.argsort(r[ids])]
    im = np.argmax(ut[ids])
    if not 0 < im < len(ids)-1:
        raise ValueError("unbracketed peak")
    center = r[ids[im]]
    ix = ids[im-1:im+2]
    a, b, c = np.polyfit(r[ix]-center, ut[ix], 2)
    return np.array([center-b/(2*a), c-b*b/(4*a)])


def compare(directory, name):
    n, _, dt, steps, _ = CASES[name]
    wide = name == "wide32"
    xy, quads, wall = mesh(n, wide)
    r = np.linalg.norm(xy, axis=1)
    radial = xy / np.where(r>0, r, 1)[:, None]
    tangent = np.column_stack((-radial[:, 1], radial[:, 0]))
    vol, _ = dual_geometry(xy, quads, wall)
    edges = np.roll(xy[quads], -1, axis=1) - xy[quads]
    centers = xy[quads].mean(axis=1)
    rc = np.linalg.norm(centers, axis=1)
    area = .5*np.sum((xy[quads, 0]-centers[:, None, 0])*edges[:, :, 1]
                     - (xy[quads, 1]-centers[:, None, 1])*edges[:, :, 0], axis=1)
    core = (r>0) & (r<=INNER+1e-15)
    inner_cells = rc<INNER
    xaxis = (xy[:, 0]>0) & (abs(xy[:, 1])<1e-14)
    diagonal = (xy[:, 0]>0) & (abs(xy[:, 0]-xy[:, 1])<1e-14)
    dist, rotated = cKDTree(xy).query(np.column_stack((-xy[:, 1], xy[:, 0])))
    if max(dist)>1e-14:
        raise ValueError("quarter-turn geometry differs")
    props = background()
    nu = props["mu_Pa_s"]/props["rho_kg_m3"]
    records = []
    for step in sorted({0, max(steps//2, 1), steps}):
        state = read_restart(directory / f"state_{step:05d}.dat")
        np.testing.assert_allclose(xy, np.column_stack((state["x"], state["y"])), rtol=0, atol=1e-16)
        q = np.column_stack([state[k] for k in FIELDS[2:]])
        p, t = flash(q)
        uv = q[:, 1:3]/q[:, :1]
        ut = (uv*tangent).sum(axis=1)
        ur = (uv*radial).sum(axis=1)
        uc = uv[quads]
        omega = (.5*(uc + np.roll(uc, -1, axis=1))*edges).sum(axis=(1, 2))/area
        width2 = INITIAL.gaussian_width_m**2+4*nu*step*dt
        ref_ut = -INITIAL.circulation_m2_s*np.expm1(-r[core]**2/width2)/(2*np.pi*r[core])
        ref_omega = INITIAL.circulation_m2_s*np.exp(-rc[inner_cells]**2/width2)/(np.pi*width2)
        fits = np.stack([peak_fit(r, ut, line) for line in (xaxis, diagonal)])
        if step == 0:
            q0, u0, p0, omega0, fits0 = q, uv, p, omega, fits
            ref0, ut0 = ref_omega, ut
        dq = q-q0
        # Exact finite kinetic change, expressed in small conservative differences.
        dk = .5*((uv+u0)*dq[:, 1:3]).sum(axis=1) - .5*(uv*u0).sum(axis=1)*dq[:, 0]
        dp = p-p0
        peaks = fits-fits0
        core_peak = np.flatnonzero(core)[np.argmax(abs(dp[core]))]
        square_edge = core & np.isclose(abs(xy).max(axis=1), .035 if wide else .010, atol=1e-15, rtol=0)
        pressure_variance = vol[core] @ dp[core]**2
        edge_fraction = (vol[square_edge] @ dp[square_edge]**2)/pressure_variance if pressure_variance else None
        bins = []
        for upper in (.005,.010,.015,.020,.025,.030):
            points = (r>upper-.005+1e-15) & (r<=upper+1e-15)
            cells = (rc>upper-.005) & (rc<=upper)
            bins.append([upper, np.average(ut[points], weights=vol[points]),
                         np.average(ut[points]-ut0[points], weights=vol[points]),
                         np.average(omega[cells], weights=area[cells]),
                         np.average((omega-omega0)[cells], weights=area[cells])])
        records.append(dict(step=step, t_s=dt*step, liquid_nodes=len(p), pressure_min_Pa=min(p),
                            max_T_error_K=max(abs(t-T0)), inner_rise_Pa=p[np.isclose(r, INNER, atol=1e-15,
                            rtol=0)].mean()-p[r.argmin()], max_pressure_change_Pa=max(abs(dp)),
                            global_peak_xy_m=xy[np.argmax(abs(dp))].tolist(),
                            core_peak_pressure_change_Pa=dp[core_peak], core_peak_xy_m=xy[core_peak].tolist(),
                            square_edge_fraction_core_dp2=edge_fraction,
                            pressure_change_core_rms_Pa=np.sqrt(np.average(dp[core]**2, weights=vol[core])),
                            max_quarter_turn_pressure_Pa=max(abs(p-p[rotated])),
                            max_quarter_turn_speed_m_s=max(abs(ut-ut[rotated])),
                            radial_core_rms_m_s=np.sqrt(np.average(ur[core]**2, weights=vol[core])),
                            inner_ut_error_rms_m_s=np.sqrt(np.average((ut[core]-ref_ut)**2, weights=vol[core])),
                            inner_omega_error_rms_s=np.sqrt(np.average((omega[inner_cells]-ref_omega)**2,
                                                               weights=area[inner_cells])),
                            omega_change_error_rms_s=np.sqrt(np.average(((omega-omega0)[inner_cells]
                                -(ref_omega-ref0))**2, weights=area[inner_cells])),
                            peak_radius_speed_axes_diag=fits.tolist(), peak_changes=peaks.tolist(),
                            inventory_change=(vol[:, None]*dq).sum(axis=0).tolist(),
                            kinetic_change_J_m=vol@dk, internal_change_J_m=vol@(dq[:, 3]-dk),
                            profiles=bins))
    return dict(case=name, profile_columns=["outer_m","mean_ut","change_ut","mean_omega","change_omega"],
                endpoints=records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("case", choices=CASES)
    args = parser.parse_args()
    print(json.dumps(compare(args.root / args.case, args.case), indent=2, allow_nan=False))
