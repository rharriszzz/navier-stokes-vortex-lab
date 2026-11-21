"""Repeat the historical disk configurations from one screened R292 restart."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from zipfile import ZipFile

from .disk_step_trial import INPUT_HASHES, TRIALS

EVIDENCE = Path(__file__).resolve().parents[1]/'docs/physics-first'
BINARIES = ('0941113d648fbd79bd745ef68f050f982225c479e3ca0f59ad28d582c28d84aa',
            'e8d2d6bf2e1f1c15e9c8788e9cfdd233dcd4aa1cba85bd4659d1a6ff08d60806')
RESTART = '693b762dca36f6275190fd03d77cb37d4a2352287ac5db3779cb76e8b991301f'


def require_hash(file, expected):
    if hashlib.sha256(file.read_bytes()).hexdigest() != expected:
        raise ValueError(f'Unexpected input: {file}')


def execute(directory, binary, seconds=420):
    with (directory/'solver.log').open('x') as log:
        subprocess.run(['/usr/bin/time', '-v', '-o', 'resources.txt', 'timeout', str(seconds),
                        'prlimit', '--as=2684354560', str(binary.resolve()), 'wave.cfg'],
                       cwd=directory, stdout=log, stderr=subprocess.STDOUT, check=True)


def run(root, installed, experimental):
    release = root/'release'
    require_hash(release/'line.su2', INPUT_HASHES['line.su2'])
    require_hash(release/'state_00000.dat', RESTART)
    require_hash(installed, BINARIES[0])
    require_hash(experimental, BINARIES[1])
    if not json.loads((EVIDENCE/'r292/release.json').read_text())['passed']:
        raise ValueError('Release screening failed')
    for case in ('reference', *TRIALS):
        dest = root/case
        dest.mkdir(exist_ok=False)
        for name in ('line.su2', 'state_00000.dat'):
            shutil.copyfile(release/name, dest/name)
        if case == 'reference':
            archive, member, binary = 'rotating-disk/fields.zip', 'wide32', installed
        else:
            archive, member, binary = 'r291/disk.zip', case, experimental
        with ZipFile(EVIDENCE/archive) as inputs:
            (dest/'wave.cfg').write_bytes(inputs.read(member+'/wave.cfg'))
        execute(dest, binary)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('root', 'installed', 'experimental'):
        p.add_argument(arg, type=Path)
    run(**vars(p.parse_args()))
