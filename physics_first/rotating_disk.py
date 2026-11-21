"""Generate a median-dual SU2 disk and measure the assembled release residual (SI)."""

import argparse
import json
from pathlib import Path

import CoolProp.CoolProp as CP
import numpy as np
from scipy.interpolate import PchipInterpolator

from physics_first.acoustic_initial_state import background
from physics_first.cylinder_spreading import INITIAL, INNER, WALL, initial_swirl
from physics_first.shear_qualification import COEFFICIENT
from physics_first.su2_acoustic import write_configuration, write_restart
from physics_first.vortex_equilibrium import initial_state, liquid_at_pt

PEAK = INITIAL.peak_radius_m


def mesh(n, wide=False):
    """Cartesian core square, four conforming blocks to 30 mm, then annular quads."""
    square_n = 7*n//2 if wide else n
    circle = .065 if wide else INNER
    grid = np.arange((2*square_n+1)**2).reshape(2*square_n+1, 2*square_n+1)
    axis = np.arange(-square_n, square_n+1) * (PEAK/n)
    x, y = np.meshgrid(axis, axis)
    nodes = [np.column_stack((x.ravel(), y.ravel()))]
    rings = np.r_[grid[0, :-1], grid[:-1, -1], grid[-1, :0:-1], grid[:0:-1, 0]]
    inner = nodes[0][rings]
    direction = inner / np.linalg.norm(inner, axis=1)[:, None]
    quads = [np.stack((grid[:-1, :-1], grid[:-1, 1:], grid[1:, 1:], grid[1:, :-1]), axis=-1).reshape(-1, 4)]
    count = len(nodes[0])
    for i in range(1, 4*n+1):
        if i <= 2*n:
            f = i/(2*n)
            layer = (1-f)*inner + f*circle*direction
        else:
            f = (i-2*n)/(2*n)
            layer = circle * (WALL/circle)**f * direction
        ids = np.arange(count, count + len(layer))
        quads.append(np.column_stack((rings, ids, np.roll(ids, -1), np.roll(rings, -1))))
        nodes.append(layer)
        rings, count = ids, count + len(layer)
    return np.vstack(nodes), np.vstack(quads), rings


def dual_geometry(xy, quads, wall):
    """Barycentric dual area and an upper bound on dual perimeter for the CFL."""
    xyq = xy[quads]
    center = xyq.mean(axis=1)
    mid = (xyq + np.roll(xyq, -1, axis=1)) / 2
    vol, perimeter = np.zeros((2, len(xy)))
    for i in range(4):
        edge = mid[:, i] - xyq[:, i]
        spoke = center - mid[:, i]
        area = (edge[:, 0]*spoke[:, 1] - edge[:, 1]*spoke[:, 0]) / 2
        if np.min(area) <= 0:
            raise ValueError("inverted quadrilateral sector")
        for ids in (quads[:, i], quads[:, (i+1) % 4]):
            np.add.at(vol, ids, area)
            np.add.at(perimeter, ids, np.linalg.norm(spoke, axis=1))
    half_lengths = np.linalg.norm(xy[wall] - np.roll(xy[wall], -1, axis=0), axis=1)/2
    perimeter[wall] += half_lengths + np.roll(half_lengths, 1)
    return vol, perimeter


def generate(directory, n, wide=False):
    if n not in (16, 32, 64):
        raise ValueError("use 16, 32 or 64 cells per peak radius")
    xy, quads, wall = mesh(n, wide)
    r = np.linalg.norm(xy, axis=1)
    # Sample at SU2 solution points on the median dual. Preserve common radii
    # to 1e-15 m for the repeated symmetric pressure/temperature flashes.
    profile = initial_state(128)
    radii, indices = np.unique(np.round(r, 15), return_inverse=True)
    prescribed = PchipInterpolator(profile.r, profile.p)(radii)
    eos = CP.AbstractState("HEOS", "Water")
    density, internal = np.empty((2, len(radii)))
    for i, pressure in enumerate(prescribed):
        liquid_at_pt(eos, pressure)
        density[i], internal[i] = eos.rhomass(), eos.umass()
    rho = density[indices]
    u = initial_swirl(r)
    speed_over_r = np.divide(u, r, where=r>0, out=np.zeros_like(r))
    uv = np.column_stack((-xy[:, 1], xy[:, 0])) * speed_over_r[:, None]
    energy = rho * (internal[indices] + .5*(uv**2).sum(axis=1))
    data = np.column_stack((xy, rho, rho[:, None]*uv, energy))
    # Recover every distinct conservative (rho,e) pair after Cartesian packing.
    e = energy/rho - .5*((data[:, 3:5]/rho[:, None])**2).sum(axis=1)
    pairs, index = np.unique(np.column_stack((rho, e)), axis=0, return_inverse=True)
    recovered, temperature = np.empty((2, len(pairs)))
    for i, (density_i, e_i) in enumerate(pairs):
        eos.update(CP.DmassUmass_INPUTS, density_i, e_i)
        if eos.phase() != CP.iphase_liquid:
            raise ValueError("non-liquid conservative state")
        recovered[i], temperature[i] = eos.p(), eos.T()
    p = recovered[index]
    base = background()
    vol, perimeter = dual_geometry(xy, quads, wall)
    dt = float(.2*np.min(vol/perimeter)/(base['sound_speed_m_s'] + .1))
    directory.mkdir(parents=True, exist_ok=False)
    write_restart(directory, data)
    lines = ["NDIME= 2", f"NELEM= {len(quads)}"]
    lines.extend("9 %d %d %d %d" % tuple(q) for q in quads)
    lines += [f"NPOIN= {len(xy)}"]
    lines.extend(f"{x:.17g} {y:.17g} {i}" for i, (x, y) in enumerate(xy))
    lines.extend(["NMARK= 1", "MARKER_TAG= wall", f"MARKER_ELEMS= {len(wall)}"])
    lines.extend(f"3 {i} {j}" for i, j in zip(wall, np.roll(wall, -1)))
    (directory / "line.su2").write_text("\n".join(lines) + "\n")
    write_configuration(directory, base, dt, 1, .1/base["sound_speed_m_s"], WALL, 1,
                        boundaries="MARKER_HEATFLUX= (wall, 0.0)", time_scheme="EULER_EXPLICIT")
    with (directory / "wave.cfg").open("a") as f:
        f.write(COEFFICIENT + "\n")
    ring = np.isclose(r, INNER, rtol=0, atol=1e-15)
    audit = dict(n=n, nodes=len(r), quads=len(quads), wall_faces=len(wall),
                 polygon_area_m2=vol.sum(), min_dual_area_m2=vol.min(), dt_s=dt,
                 liquid_nodes=len(r), conservative_flash_pairs=len(pairs),
                 max_recovery_error_Pa=max(abs(p-prescribed[indices])),
                 max_T_error_K=max(abs(temperature-base['temperature_K'])),
                 pressure_range_Pa=[p.min(), p.max()], inner_rise_Pa=p[ring].mean()-p[r.argmin()],
                 max_wall_speed_m_s=max(u[wall]), radial_momentum_max=abs((data[:, 3:5]*xy).sum(axis=1)
                 / np.where(r>0, r, 1)).max())
    if wide:
        audit["wide"] = True
    (directory / "initial.json").write_text(json.dumps(audit, indent=2)+"\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("directory", type=Path)
    ap.add_argument("n", type=int)
    ap.add_argument("--wide", action="store_true", help="matched spacing with a 35 mm Cartesian half-width")
    args = ap.parse_args()
    generate(args.directory, args.n, args.wide)
