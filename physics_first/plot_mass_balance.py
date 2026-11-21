"""Render measured release mass sources and the local 12 ns rate discrepancy."""
import argparse
from pathlib import Path

import numpy as np


def extract(source, root, dest):
    from .disk_mass_balance import residual
    from .disk_step_evidence import conservative
    from .rotating_disk import dual_geometry, mesh, INITIAL
    from .su2_acoustic import read_restart

    xy, cells, wall = mesh(32, True)
    area, _ = dual_geometry(xy, cells, wall)
    q0, ref, full = [conservative(read_restart(path)) for path in
                     (root/'release/state_00000.dat', root/'reference/state_00004.dat', root/'full/state_00001.dat')]
    old = conservative(read_restart(source/'state_00000.dat'))
    velocity = q0[:, 1:3]/q0[:, :1]
    change = np.linalg.norm(velocity-old[:, 1:3]/old[:, :1], axis=1)
    # Same release and elapsed time. Difference the conservative increments
    # before forming tiny velocity slopes, as in the endpoint gate.
    def increment(q):
        dq = q-q0
        return (dq[:, 1:3]-velocity*dq[:, :1])/q[:, :1]
    n = 225
    squares = cells[:(n-1)**2]
    edges = np.roll(xy[squares], -1, axis=1)-xy[squares]
    def line_integral(v):
        values = v[squares]
        return (.5*(values+np.roll(values, -1, axis=1))*edges).sum(axis=(1, 2))
    center = xy[squares].mean(axis=1)
    strong = np.exp(-(center**2).sum(axis=1)/INITIAL.gaussian_width_m**2)
    strong = strong>.25*strong.max()
    rate = np.full(len(squares), np.nan)
    rate[strong] = (line_integral(increment(full)-increment(ref))[strong] /
                    (12e-9*line_integral(velocity)[strong]))
    np.savez_compressed(dest, xy=xy, density_rate=-residual(source)[:, 0]/area, correction=change,
                        rate=rate.reshape(n-1,n-1))


def plot(data, dest):
    import matplotlib.pyplot as plt
    with np.load(data) as fields:
        xy = fields['xy']*1e3
        fig, axes = plt.subplots(1, 3, figsize=(11, 3.9), layout='constrained')
        for ax, values, limit, cmap, title, units in [
                (axes[0], fields['density_rate'], (-3, 3), 'RdBu_r', 'Original release', 'Density rate (kg m⁻³ s⁻¹)'),
                (axes[1], fields['correction']*1e6, (0, 5.6), 'viridis', 'Initial velocity correction', 'Magnitude (µm/s)')]:
            dots = ax.scatter(xy[:, 0], xy[:, 1], c=values, s=.6, linewidths=0, cmap=cmap,
                              vmin=limit[0], vmax=limit[1], rasterized=True)
            ax.set(title=title, xlim=(-82, 82), ylim=(-82, 82), xlabel='x (mm)', aspect='equal')
            fig.colorbar(dots, ax=ax, location='bottom', shrink=.91, label=units)
        axes[0].set_ylabel('y (mm)')
        img = axes[2].imshow(fields['rate'], origin='lower', extent=(-35, 35, -35, 35), cmap='RdBu_r',
                             vmin=-.1, vmax=.1, interpolation='nearest')
        axes[2].set(title='Implicit minus explicit at 12 ns', xlabel='x (mm)', xlim=(-12, 12), ylim=(-12, 12))
        fig.colorbar(img, ax=axes[2], location='bottom', shrink=.91, label='Strong-core fractional rate difference (s⁻¹)')
        fig.savefig(dest, dpi=160)
        plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    modes = p.add_subparsers(dest='mode', required=True)
    for mode, names in [('extract', ('source', 'root', 'dest')), ('plot', ('data', 'dest'))]:
        cmd = modes.add_parser(mode)
        for name in names:
            cmd.add_argument(name, type=Path)
    args = vars(p.parse_args())
    fn = extract if args.pop('mode')=='extract' else plot
    fn(**args)
