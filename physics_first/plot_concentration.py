"""Plot fixed-flux and enstrophy measurements from the published tables."""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from .ring_concentration_summary import read, PRIMARY


def plot(directory, output):
    tables={case:read(directory/(case+'.csv')) for case in (PRIMARY,PRIMARY+'_inviscid','diffusion')}
    t=np.arange(41)*.5
    fig,axes=plt.subplots(1,3,figsize=(11,3.5),layout='constrained')
    def line(ax,case,definition,metric,label):
        y=tables[case][definition,metric]
        ax.plot(t,100*(y/y[0]-1),label=label,lw=2)
    for fraction in (25,50,75):
        line(axes[0],PRIMARY,'whole',f'r{fraction}_m',f'{fraction}% of release Γ')
    for case,label in zip(tables,('Water','Inviscid','Diffusion only'),strict=True):
        line(axes[1],case,'whole','aeff_m2',label)
    for label,description in [('disk_2a','2a disk'),('disk_3a','3a disk'),('whole','Full section')]:
        line(axes[2],PRIMARY,label,'aeff_m2',description)
    for ax,title in zip(axes,['Fixed-circulation radii','Effective area','Aperture sensitivity'],strict=True):
        ax.set(title=title,xlabel='Time (ms)',xlim=(0,20))
        ax.axhline(0,color='0.55',lw=.7)
        ax.legend(frameon=False,fontsize=8)
    axes[0].set_ylabel('Change from release (%)')
    fig.savefig(output,dpi=155)
    plt.close(fig)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args()
    plot(a.directory,a.output)
