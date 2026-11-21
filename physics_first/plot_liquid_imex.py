"""Plot the saved pressure fields and the independent pressure-recovery audit."""
import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot(directory, output):
    results = json.loads((directory / 'results.json').read_text())
    oracle = json.loads((directory / 'decimal.json').read_text())
    fig, (wave, eos) = plt.subplots(1, 2, figsize=(9, 3.6), layout='constrained')
    x = (np.arange(128) + 0.5) * 100/128
    with np.load(directory/'fields.npz') as fields:
        for steps, color in [(4, '#a23b20'), (16, '#31785d'), (512, '#275384')]:
            pressure = fields[f'n128_m{steps}_A10_s1_tol2e-11'][-1, 3]
            wave.plot(x, pressure, color=color, label=f'{steps} steps')
    wave.plot(x[::6], 10*np.sin(2*np.pi*x[::6]/100), 'k.', label='Analytic', ms=3)
    wave.set(xlabel='Position (mm)', ylabel='Pressure perturbation (Pa)',
             title='After one acoustic crossing')
    wave.legend(frameon=False, ncol=2, fontsize=9)
    points = results['precision']['steps']
    for key, label, color in [('implicit_vs_abs_flash_Pa', 'Absolute flash', '#a23b20'),
                              ('implicit_vs_integral_Pa', 'Derivative integral', '#275384')]:
        eos.loglog([p['peak_input_Pa'] for p in points], [p[key] for p in points],
                   'o-', label=label, color=color, ms=3)
    rows = oracle['samples']
    amps = sorted({r['amplitude_Pa'] for r in rows})
    eos.loglog(amps, [max(abs(r['difference_Pa']) for r in rows if r['amplitude_Pa']==a)
                      for a in amps], 'kx', label='48-digit spot check')
    eos.set(xlabel='Initial wave amplitude (Pa)', ylabel='Pressure discrepancy (Pa)',
            title='Recovery from conservative variables')
    eos.legend(frameon=False, fontsize=9)
    for ax in (wave, eos):
        ax.spines[['top','right']].set_visible(False)
    fig.savefig(output, dpi=170)
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    plot(args.directory, args.output)
