"""Run the three bounded R291 disk comparisons in fresh directories."""
import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path

TRIALS = {'full': (1, -5, '1e-8'), 'half': (2, -5, '1e-8'), 'tight': (1, -6, '1e-9')}
INPUT_HASHES = {'line.su2': '7b5a9f74a912e7202db5c52c27ba8080b6f7dd94bb6a9c0d765bbba332328b59',
                'state_00000.dat': 'ea9447f1681de1906de7f36be8d777f3ee46846ba89f4fd535ffec7b83ab836c',
                'wave.cfg': '67f2ce5489cc1c6627f4dbca14efc1fb05472013d02c9c17c6be1b646dda2a43'}


def run(source, binary, dest, case):
    for name, digest in INPUT_HASHES.items():
        if hashlib.sha256((source/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Unexpected wide-disk input '+name)
    dest.mkdir(parents=True, exist_ok=False)
    for name in ('line.su2','state_00000.dat','initial.json'):
        shutil.copy(source/name,dest/name)
    steps, target, linear = TRIALS[case]
    settings = dict(s.split('= ',1) for s in (source/'wave.cfg').read_text().splitlines())
    settings.update(TIME_STEP=str(12e-9/steps), TIME_ITER=str(1+steps), INNER_ITER='10',
                    TIME_MARCHING='DUAL_TIME_STEPPING-1ST_ORDER', TIME_DISCRE_FLOW='EULER_IMPLICIT',
                    CFL_NUMBER='10', LINEAR_SOLVER_ERROR=linear, LINEAR_SOLVER_ITER='50',
                    CONV_FIELD='(RMS_DENSITY, RMS_MOMENTUM-X, RMS_MOMENTUM-Y, RMS_ENERGY)',
                    CONV_STARTITER='1', CONV_RESIDUAL_MINVAL=str(target),
                    SCREEN_OUTPUT='(TIME_ITER, INNER_ITER, RMS_DENSITY, RMS_MOMENTUM-X, RMS_ENERGY, LINSOL_ITER)',
                    HISTORY_WRT_FREQ_INNER='1', OUTPUT_WRT_FREQ='1', WRT_PERFORMANCE='YES')
    (dest/'wave.cfg').write_text(''.join(f'{k}= {v}\n' for k,v in settings.items()))
    with (dest/'solver.log').open('w') as log:
        subprocess.run(['/usr/bin/time','-v','-o','resources.txt','timeout','420',
                        'prlimit','--as=2684354560',str(binary),'wave.cfg'],
                       cwd=dest,stdout=log,stderr=subprocess.STDOUT,check=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for key in ('source','binary','root'):
        p.add_argument(key,type=Path)
    p.add_argument('case',choices=TRIALS)
    a=p.parse_args()
    run(a.source,a.binary.resolve(),a.root/a.case,a.case)
