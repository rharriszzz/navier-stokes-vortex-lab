"""Draw the measured signed radial transect and facing-section sample classifications."""
import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot(folder, destination):
    with (folder/'sections.csv').open() as source:
        rows = [r for r in csv.DictReader(source) if float(r['arc_deg'])==0]
    fig, axes = plt.subplots(1,2,figsize=(10,4.35),layout='constrained')
    ax = axes[0]
    for case, label in [('original','12.019 mm, original Γ'),('closer','8 mm, original Γ'),
                        ('candidate','8 mm, doubled Γ')]:
        vals = sorted(((1 if float(r['phi_deg'])==0 else -1)*float(r['r_a']),
                       float(r['net']),float(r['iso_net']))
                      for r in rows if r['case']==case and
                      float(r['phi_deg']) in (0,180) and float(r['r_a'])<=1)
        x, y, isolated = zip(*vals)
        ax.plot(x,y,'o-',label=label,markersize=3)
    ax.plot(x,isolated,'k--',label='Isolated, either Γ')
    ax.axhline(0,color='0.5',linewidth=.8)
    ax.set(xlabel='Radial offset from facing centerline / a',ylabel='Material rate of |ω| / |ω| (s⁻¹)',
           title='Facing radial transect')
    ax.legend(fontsize=8)
    ax=axes[1]
    labels=('Pair loses','Pair and isolated grow','Only pair grows')
    colors=('#b1b7bf','#24736a','#c35714')
    for group in range(3):
        xy=[]
        for r in rows:
            if r['case']!='candidate' or float(r['line_fraction'])<.5:
                continue
            positive = float(r['net'])>0
            actual = 0 if not positive else (1 if float(r['iso_net'])>0 else 2)
            if actual==group:
                phi=np.deg2rad(float(r['phi_deg']))
                xy.append(float(r['r_a'])*np.array([np.cos(phi),np.sin(phi)]))
        x,y=np.array(xy).T
        ax.scatter(x,y,s=22,c=colors[group],label=labels[group])
    ax.set(aspect='equal',xlabel='Outward radial offset / a',ylabel='Offset opposite flight / a',
           title='Doubled Γ, strong facing-core samples',xlim=(-.88,.88),ylim=(-1.15,.86))
    ax.legend(loc='lower center',fontsize=7,ncol=2)
    fig.savefig(destination,dpi=155)
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    plot(args.directory,args.output)
