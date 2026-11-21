"""Sample the actual spatial operator at saved disk endpoints with a steady residual evaluation."""
import argparse
from pathlib import Path
import shutil

import numpy as np

from .disk_balance_trials import BINARIES, execute, require_hash
from .disk_step_trial import INPUT_HASHES
from .disk_mass_balance import residual
from .rotating_disk import dual_geometry, mesh
from .disk_step_evidence import conservative
from .su2_acoustic import read_restart, write_restart, FIELDS

FINAL_STEPS = {'reference': 4, 'full': 1, 'half': 2, 'tight': 1}


def probe(root, binary):
    require_hash(binary, BINARIES[0])
    release = root/'release'
    skip = {'TIME_DOMAIN','TIME_MARCHING','TIME_ITER','TIME_STEP','UNST_CFL_NUMBER','INNER_ITER',
            'RESTART_ITER','SCREEN_OUTPUT','SCREEN_WRT_FREQ_TIME','SOLUTION_FILENAME','RESTART_FILENAME'}
    config = [s for s in (release/'wave.cfg').read_text().splitlines() if s.split('=',1)[0] not in skip]
    config += ['TIME_DOMAIN= NO', 'ITER= 1', 'CFL_NUMBER= 1e-15', 'SOLUTION_FILENAME= input',
               'RESTART_FILENAME= sampled', 'SCREEN_OUTPUT= (INNER_ITER, RMS_DENSITY, RMS_ENERGY)']
    cfg = '\n'.join(config)+'\n'
    xy, cells, wall = mesh(32, True)
    vol, _ = dual_geometry(xy, cells, wall)
    for case, step in {'release': 0, **FINAL_STEPS}.items():
        dest = root/('spatial_'+case)
        state = read_restart(root/case/f'state_{step:05d}.dat')
        if not dest.exists():
            dest.mkdir()
            shutil.copyfile(release/'line.su2', dest/'line.su2')
            write_restart(dest, np.column_stack([state[k] for k in FIELDS]))
            (dest/'state_00000.dat').rename(dest/'input.dat')
            (dest/'wave.cfg').write_text(cfg)
            execute(dest, binary, 180)
        if (dest/'wave.cfg').read_text() != cfg or 'Exit status: 0' not in (dest/'resources.txt').read_text():
            raise ValueError(f'Unverified steady sample in {dest}')
        require_hash(dest/'line.su2', INPUT_HASHES['line.su2'])
        binding = read_restart(dest/'input.dat')
        for key in FIELDS:
            np.testing.assert_array_equal(binding[key], state[key])
        sampled = read_restart(dest/'sampled.dat')
        values = np.column_stack([sampled['Residual_'+k] for k in FIELDS[2:]])
        # Forward Euler outputs its *input* residual and a pseudo-updated
        # solution. Bound that update by a full diameter CFL transit time.
        q = conservative(state)
        dt_max = 1e-15*.2/1400.
        bound = dt_max*abs(values)/vol[:, None]+abs(np.spacing(q))
        if np.any(abs(conservative(sampled)-q)>bound):
            raise ValueError('Steady pseudo-update exceeds CFL and storage allowance')
        if case == 'release':
            np.testing.assert_array_equal(values, residual(release))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('binary', type=Path)
    probe(**vars(p.parse_args()))
