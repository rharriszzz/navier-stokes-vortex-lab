"""Held exact-field rotation worker; no numerical imports before release."""
import hashlib
import os
from pathlib import Path
import sys
import time

from .handshake import held, completed
from .prototype import Refusal
from .rotation_driver import (assemble_rotation, read_limited,
                              strict_json_bytes, validate_reservation,
                              write_limited_new)
from .rotation_manifest import contract_digest, validate as validate_manifest
from .source_binding import verify_source
from .worker import _cgroup_path, load_pinned_modules


def main(args=None, *, monotonic=time.monotonic):
    args = sys.argv[1:] if args is None else args
    if len(args) != 2:
        raise Refusal('rotation worker requires one reserved directory and manifest')
    directory, manifest_path = Path(args[0]).resolve(), Path(args[1])
    reservation = read_limited(directory/'reservation.json')
    admission = read_limited(directory/'admission.json')
    manifest_bytes = manifest_path.read_bytes()
    manifest = strict_json_bytes(manifest_bytes)
    validate_manifest(manifest)
    validate_reservation(reservation, admission, manifest_bytes, manifest,
                         directory, sys.executable, reservation.get('owner'))
    actual_cgroup = _cgroup_path()
    binding = verify_source(reservation)
    held(directory, reservation, actual_cgroup, binding)
    if any(os.environ.get(name) != '1' for name in
           ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
            'NUMEXPR_NUM_THREADS')):
        raise Refusal('one numerical thread per library required before imports')
    imported_at = monotonic()
    modules, actual_versions, artifact = load_pinned_modules(manifest['versions'])
    assembled_at = monotonic()
    geometry, oracle, receipts, phases = assemble_rotation(modules, manifest,
                                                           monotonic=monotonic)
    finished_at = monotonic()
    payload = dict(worker_schema=1, kind='rotation_assembly', fixture='rotation',
                   mode='exact_field_assembly',
                   manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                   contract_sha256=contract_digest(manifest['contract']),
                   source_binding=binding, geometry=geometry, oracle=oracle,
                   assembly_receipts=receipts, phase_seconds=phases,
                   worker_intervals=dict(import_seconds=assembled_at-imported_at,
                                         fixture_setup_jit_and_assembly_seconds=
                                         finished_at-assembled_at),
                   actual_versions=actual_versions, ffcx_artifact=artifact)
    # Save a complete finite assembly even when an exact-target gate fails.
    # The controller recomputes and refuses the saved numerical decision.
    write_limited_new(directory/'numerical.json', payload)
    completed(directory, reservation)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'{type(exc).__name__}: {exc}', file=sys.stderr, flush=True)
        raise SystemExit(1)
