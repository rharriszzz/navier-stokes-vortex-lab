"""Plot the release map and signed material budget from the finest ring CSV."""
import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import numpy as np


def plot(source, destination):
    with source.open() as data:
        rows = list(csv.DictReader(data))
    fig, (plan, rates) = plt.subplots(1, 2, figsize=(10, 4.6), layout='constrained',
                                      gridspec_kw={'width_ratios': [1.25, 1]})
    norm = Normalize(0, .28)
    for side in ('left', 'right'):
        selected = [r for r in rows if r['ring'] == side]
        xy = 1000*np.array([[float(r['position_m_'+axis]) for axis in 'xy'] for r in selected])
        s = np.array([float(r['s']) for r in selected])
        lines = LineCollection(np.stack((xy, np.roll(xy, -1, axis=0)), axis=1),
                               cmap='viridis', norm=norm, linewidth=5, capstyle='round')
        lines.set_array((s+np.roll(s, -1))/2)
        plan.add_collection(lines)
    plan.set(xlim=(-36, 36), ylim=(-22, 22), aspect='equal',
             xlabel='x (mm)', ylabel='y (mm)', title='Release geometry viewed along z')
    plan.annotate('Facing', xy=(6, 0), xytext=(0, 7), ha='center',
                  arrowprops={'arrowstyle': '->'})
    plan.annotate('Far', xy=(32, 0), xytext=(32, -12), ha='center',
                  arrowprops={'arrowstyle': '->'})
    fig.colorbar(lines, ax=plan, location='bottom', shrink=.80, pad=.10,
                 label='Axial extension rate (s⁻¹)')
    profile = [r for r in rows if r['ring'] == 'left' and float(r['azimuth_deg']) <= 180]
    angle = [float(r['azimuth_deg']) for r in profile]
    for key, name, color, style in [('s', 'Stretching', '#176456', '-'),
                                    ('visc', 'Viscosity', '#963d1c', '--'),
                                    ('net', 'Net', '#253a5c', '-')]:
        rates.plot(angle, [float(r[key]) for r in profile], label=name,
                   color=color, ls=style, lw=2.5)
    rates.axhline(0, color='0.55', lw=.8)
    rates.set(xlim=(0, 180), ylim=(-1.1, .36), xticks=[0, 45, 90, 135, 180],
              xlabel='Angle from facing point (degrees)', ylabel='Fractional rate (s⁻¹)',
              title='Vorticity budget along either ring')
    rates.legend(loc='center right', frameon=False)
    for axis in (plan, rates):
        axis.spines[['top', 'right']].set_visible(False)
    fig.savefig(destination, dpi=160)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    plot(args.source, args.destination)
