"""Held manufactured pilot worker; numerical modules load only after release."""
import hashlib
import os
from pathlib import Path
import sys
import time

from .handshake import held, completed
from .linear_evidence import LatestSystem
from .manufactured_driver import (run_manufactured, validate_reservation)
from .manufactured_manifest import contract_digest, validate as validate_manifest
from .prototype import Refusal
from .rotation_driver import read_limited, strict_json_bytes, write_limited_new
from .source_binding import verify_source
from .worker import _cgroup_path, load_pinned_modules


def main(args=None, *, monotonic=time.monotonic):
    args = sys.argv[1:] if args is None else args
    if len(args) != 2:
        raise Refusal('manufactured worker requires one reserved directory and manifest')
    directory, manifest_path = Path(args[0]).resolve(), Path(args[1])
    reservation = read_limited(directory/'reservation.json')
    admission = read_limited(directory/'admission.json')
    manifest_bytes = manifest_path.read_bytes()
    manifest = strict_json_bytes(manifest_bytes)
    validate_manifest(manifest)
    validate_reservation(reservation, admission, manifest_bytes, manifest,
                         directory, sys.executable, reservation.get('owner'))
    binding = verify_source(reservation)
    held(directory, reservation, _cgroup_path(), binding)
    if any(os.environ.get(name) != '1' for name in
           ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS')):
        raise Refusal('one numerical thread per library required before imports')
    imported_at = monotonic()
    modules, versions, artifact = load_pinned_modules(manifest['versions'])
    assembled_at = monotonic()
    numerical = run_manufactured(modules, manifest, clock=monotonic,
        linear_evidence=LatestSystem(directory, binding, fixture='manufactured'))
    finished_at = monotonic()
    numerical.update(worker_schema=1, fixture='manufactured',
        kind='manufactured_spatial_pilot', mode='single_be_spatial_pilot',
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        contract_sha256=contract_digest(manifest), source_binding=binding,
        worker_intervals=dict(import_seconds=assembled_at-imported_at,
            fixture_setup_jit_and_solve_seconds=finished_at-assembled_at),
        actual_versions=versions, ffcx_artifact=artifact)
    # A complete finite numerical refusal remains on disk for independent replay.
    write_limited_new(directory/'numerical.json', numerical)
    completed(directory, reservation)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        raise SystemExit(1)
