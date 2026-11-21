"""Read SU2's assembled residual for the single-stage rotating release probe."""

import argparse
import json
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np

from physics_first.acoustic_initial_state import background
from physics_first.cylinder_spreading import INITIAL, INNER
from physics_first.rotating_disk import dual_geometry, mesh, PEAK
from physics_first.su2_acoustic import FIELDS, read_restart


def measure(directory):
    audit = json.loads((directory / "initial.json").read_text())
    initial = read_restart(directory / "state_00000.dat")
    final = read_restart(directory / "state_00001.dat")
    xy, quads, wall = mesh(audit["n"], audit.get("wide", False))
    for state in (initial, final):
        np.testing.assert_allclose(xy, np.column_stack((state["x"], state["y"])), rtol=0, atol=1e-16)
    vol, _ = dual_geometry(xy, quads, wall)
    q = np.column_stack([initial[k] for k in FIELDS[2:]])
    end = np.column_stack([final[k] for k in FIELDS[2:]])
    residual = np.column_stack([final["Residual_"+k] for k in FIELDS[2:]])
    rate = -residual/vol[:, None]
    dt = audit["dt_s"]
    err = end - q - rate*dt
    # The old and new conservative states are independently rounded doubles.
    rounding = np.spacing(np.maximum(abs(end), abs(q)))
    ulps = np.max(abs(err)/rounding, axis=0)
    # Reconstructed dual areas also incur geometric floating-point error.
    allowance = 2*rounding + 2e-12*abs(rate*dt)
    if np.any(abs(err) > allowance):
        raise ValueError(f"release residual disagrees with Euler update (ulps {ulps})")
    rho = q[:, 0]
    u = q[:, 1:3]/rho[:, None]
    acc = (rate[:, 1:3] - u*rate[:, :1])/rho[:, None]
    r = np.linalg.norm(xy, axis=1)
    radial = xy/np.where(r>0, r, 1)[:, None]
    ar = (acc*radial).sum(axis=1)
    at = acc[:, 1]*radial[:, 0] - acc[:, 0]*radial[:, 1]
    props = background()
    nu = props["mu_Pa_s"]/props["rho_kg_m3"]
    width = INITIAL.gaussian_width_m
    physical = -2*nu*INITIAL.circulation_m2_s*r*np.exp(-(r/width)**2)/(np.pi*width**4)
    ring = np.isclose(r, INNER, atol=1e-15, rtol=0)
    # Linearize p(rho,e) at the wall state over a 17 Pa background variation.
    eos = CP.AbstractState("HEOS", "Water")
    eos.update(CP.PT_INPUTS, props["pressure_pa"], props["temperature_K"])
    dp_drho = eos.first_partial_deriv(CP.iP, CP.iDmass, CP.iUmass)
    dp_de = eos.first_partial_deriv(CP.iP, CP.iUmass, CP.iDmass)
    e = q[:, 3]/rho - .5*(u**2).sum(axis=1)
    de = (rate[:, 3] - (u*rate[:, 1:3]).sum(axis=1)
          + (.5*(u**2).sum(axis=1)-e)*rate[:, 0])/rho
    dpdt = dp_drho*rate[:, 0] + dp_de*de
    square_radius = .035 if audit.get("wide", False) else PEAK
    sections = {}
    for name, mask in (("peak_region", r <= PEAK+1e-15), ("inner", r <= INNER+1e-15),
                       ("square_boundary", np.isclose(abs(xy).max(axis=1), square_radius, rtol=0, atol=1e-15)),
                       ("square_interior", abs(xy).max(axis=1) < square_radius-1e-15),
                       ("outer_motionless", r > .082)):
        mask = mask & (r>0)
        def rms(field):
            return np.sqrt(np.average(field[mask]**2, weights=vol[mask]))
        peak = np.flatnonzero(mask)[np.argmax(abs(ar[mask]))]
        sections[name] = dict(nodes=int(mask.sum()), radial_rms=rms(ar), radial_max=abs(ar[peak]),
                              peak_xy_m=xy[peak].tolist(), density_rate_rms=rms(rate[:, 0]),
                              pressure_rate_rms_Pa_s=rms(dpdt), pressure_rate_max_Pa_s=max(abs(dpdt[mask])),
                              tangential_rms=rms(at),
                              physical_tangential_rms=rms(physical) if name != "outer_motionless" else 0.,
                              tangential_error_rms=rms(at-physical) if name != "outer_motionless" else rms(at))
    # Separate the global conservative rates and the rate of kinetic energy.
    kinetic_rate = (u*rate[:, 1:3]).sum(axis=1) - .5*(u**2).sum(axis=1)*rate[:, 0]
    integrated = (vol[:, None]*rate).sum(axis=0)
    radii = np.arange(1, 31)*.001
    bins = []
    for upper in radii:
        mask = (r>upper-.001+1e-15) & (r<=upper+1e-15)
        if mask.any():
            bins.append([upper, int(mask.sum()), np.average(ar[mask], weights=vol[mask]),
                         np.sqrt(np.average(ar[mask]**2, weights=vol[mask])),
                         np.average(at[mask], weights=vol[mask]), np.average(physical[mask], weights=vol[mask])])
    return dict(initial=audit, regions=sections, max_update_error_ulps=ulps.tolist(),
                max_update_abs_error=abs(err).max(axis=0).tolist(),
                solver_primitive_rise_Pa=final["Pressure"][ring].mean()-final["Pressure"][r.argmin()],
                axis_acceleration_norm_m_s2=np.linalg.norm(acc[r.argmin()]),
                inventory_release=(vol[:, None]*q).sum(axis=0).tolist(),
                inventory_rate=integrated.tolist(), kinetic_rate_W_m=vol @ kinetic_rate,
                radial_bins_columns=["outer_m", "nodes", "mean_ar", "rms_ar", "mean_at", "mean_ref_at"],
                radial_bins=bins)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    row = measure(parser.parse_args().directory)
    print(json.dumps(row, indent=2, allow_nan=False))
