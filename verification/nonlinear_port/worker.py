"""Held Poiseuille worker. FEM imports occur only after supervisor release.

This is source for a future admitted scope, not a standalone launch command.
The worker-scope backend remains unadmitted for whole-task execution; attempts zero.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from .fixture_driver import run_poiseuille
from .handshake import held, completed
from .manifest import validate as validate_manifest
from .prototype import Refusal
from .source_binding import verify_source


def _read_json(path):
    with open(path, encoding='utf-8') as stream:
        return json.load(stream)


def _cgroup_path():
    lines = Path('/proc/self/cgroup').read_text().splitlines()
    if len(lines) != 1 or not lines[0].startswith('0::'):
        raise Refusal('unresolved unified worker cgroup')
    return lines[0][3:]


def load_pinned_modules(versions):
    """Import inside the verified scope and refuse any different FEM pin."""
    import numpy as np
    import dolfinx
    from dolfinx import fem, mesh
    from dolfinx.fem import petsc as fem_petsc
    import basix
    import basix.ufl as basix_ufl
    import ufl
    import ffcx
    import petsc4py
    from petsc4py import PETSc
    import mpi4py
    from mpi4py import MPI

    actual = dict(python='.'.join(map(str, sys.version_info[:3])),
                  dolfinx=dolfinx.__version__, basix=basix.__version__,
                  ufl=ufl.__version__, ffcx=ffcx.__version__,
                  petsc4py=petsc4py.__version__, mpi4py=mpi4py.__version__)
    if any(actual[k] != versions[k] for k in actual):
        raise Refusal(f'pinned Python/FEM version mismatch: {actual}')
    petsc_version = '.'.join(map(str, PETSc.Sys.getVersion()[:3]))
    if petsc_version != versions['petsc']:
        raise Refusal('PETSc library version mismatch')
    mpi_library = MPI.Get_library_version()
    if 'MPICH' not in mpi_library or versions['mpich'] not in mpi_library:
        raise Refusal('MPI library version mismatch')
    if MPI.COMM_WORLD.size != 1:
        raise Refusal('one MPI rank required')
    actual.update(petsc=petsc_version, mpich=versions['mpich'],
                  mpi_library=mpi_library.strip())
    return dict(np=np, mesh=mesh, fem=fem, fem_petsc=fem_petsc,
                basix_ufl=basix_ufl, basix=basix, ufl=ufl,
                PETSc=PETSc, comm=MPI.COMM_WORLD), actual


def main(args=None):
    args = sys.argv[1:] if args is None else args
    if len(args) != 2:
        raise Refusal('worker requires one reserved directory and manifest')
    directory, manifest_path = Path(args[0]), Path(args[1])
    reservation = _read_json(directory/'reservation.json')
    admission = _read_json(directory/'admission.json')
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    validate_manifest(manifest)
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    if (reservation.get('status') != 'RESERVED' or reservation.get('fixture') != 'poiseuille'
            or reservation.get('manifest_sha256') != digest
            or reservation.get('interpreter') != sys.executable
            or admission.get('approved') is not True
            or admission.get('fixture') != 'poiseuille'
            or admission.get('run_directory') != str(directory.resolve())
            or admission.get('source_commit') != reservation.get('source_commit')
            or admission.get('manifest_sha256') != digest
            or admission.get('attempts_granted') != 1):
        raise Refusal('worker reservation/admission mismatch')
    actual_cgroup = _cgroup_path()
    binding = verify_source(reservation)
    held(directory, reservation, actual_cgroup, binding)
    if any(os.environ.get(name) != '1' for name in
           ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS')):
        raise Refusal('one numerical thread per library required before imports')
    t0 = time.monotonic()
    modules, actual_versions = load_pinned_modules(manifest['versions'])
    t1 = time.monotonic()
    numerical = run_poiseuille(modules, manifest)
    t2 = time.monotonic()
    numerical['actual_versions'] = actual_versions
    numerical['worker_intervals'] = dict(import_seconds=t1-t0,
                                          fixture_setup_jit_and_solve_seconds=t2-t1)
    with open(directory/'numerical.json', 'x', encoding='utf-8') as stream:
        json.dump(numerical, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    completed(directory, reservation)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        raise SystemExit(1)
