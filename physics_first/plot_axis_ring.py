"""Render the measured isolated-ring histories. Run with NumPy and Matplotlib."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot(directory):
    def read(filename):
        return np.genfromtxt(directory/filename, delimiter=',', names=True, encoding=None)
    a = read('n16_L80_s4.csv')
    translation = read('translation.csv')
    inviscid = read('n16_L80_s4_inviscid.csv')
    t = a['t_s']*1000
    fig, axes = plt.subplots(2, 3, figsize=(13, 7), layout='constrained')
    colors = ['#176072','#bc502c','#775688']
    def lines(ax, title, units, series):
        for (label,y),color in zip(series,colors):
            ax.plot(t,y,label=label,c=color,lw=2)
        ax.set(title=title, xlabel='Time (ms)', ylabel=units)
        ax.grid(alpha=.18)
        ax.legend(fontsize=8, frameon=False)
    lines(axes[0,0], 'Axial travel', 'Displacement (mm)',
          [('Ridge',a['ridge_z']*1000),('Marker released on ridge',a['m1_z']*1000),
           ('Section centroid',translation['section_centroid_z_m']*1000)])
    lines(axes[0,1], 'Ridge-centered section', 'Width or radius (mm)',
          [('Major width',a['ridge_major']*1000),('Minor width',a['ridge_minor']*1000),
           ('Half-circulation radius',a['half_radius']*1000)])
    lines(axes[0,2], 'Vorticity', 'Magnitude (s⁻¹)',
          [('Viscous ridge',a['ridge_peak']),('Marker released on ridge',a['m1_omega']),
           ('Inviscid ridge',inviscid['ridge_peak'])])
    power = a['box_diss_W']
    loss = np.r_[0,np.cumsum((power[:-1]+power[1:])*.00025)]
    lines(axes[1,0], 'Kinetic energy lost in the box', 'Energy (µJ)',
          [('Measured loss',1e6*(a['box_energy_J'][0]-a['box_energy_J'])),
           ('Integrated dissipation',1e6*loss)])
    axes[1,0].lines[1].set_linestyle('--')
    lines(axes[1,1], 'Aperture dependence', 'Area change from release (%)',
          [(label,100*(a[f'{tag}_area']/a[f'{tag}_area'][0]-1))
           for label,tag in [('Radius 1.8a','small'),('Radius 2a','ridge'),('Radius 2.2a','large')]])
    lines(axes[1,2], 'Stretching along vorticity', 'Material stretching rate (s⁻¹)',
          [('Front marker (+a/2)',a['m2_stretch']),('Rear marker (−a/2)',a['m3_stretch']),
           ('Geometric line marker',a['m0_stretch'])])
    fig.suptitle('One freely evolving viscous ring at 20 °C', fontsize=16)
    fig.savefig(directory/'history.png',dpi=145)
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    plot(parser.parse_args().directory)
