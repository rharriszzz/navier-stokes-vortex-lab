"""R269 finite caller for one new manufactured spatial BE allocation.

Run only after a later Continue and clean publication of the allocation and caller. The caller uses the
existing reviewed controller/backend; it does not import numerical packages.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
RUN = Path('/tmp/navier-manufactured-r269-once')
PYTHON = '/tmp/navier-fenicsx-r229/bin/python'
PYTHON_SHA256 = '5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3'
MANIFEST = ROOT/'verification/nonlinear_port/future_manufactured.json'
INVENTORY = ROOT/'docs/realizability/evidence/r269/source_inventory.json'
ALLOCATION = Path(__file__).with_name('allocation.json')
ARTIFACTS = Path(__file__).with_name('artifacts.json')
LIMIT = 180
ANGULAR_POLICY = dict(file='angular_audit.json', schema=1, bytes_max=262144,
    required=True, cross_check_numerical=True, consistency_required_for_pass=True,
    physical_acceptance_unchanged=True)


def load_components():
    # Include project imports in the outer timer and make direct path execution work.
    from verification.nonlinear_port.supervision import supervise_manufactured_once
    from verification.nonlinear_port.systemd_backend import SystemdBackend
    from verification.nonlinear_port.systemd_bus import Bus
    return supervise_manufactured_once, SystemdBackend, Bus


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def git(*args):
    proc = subprocess.run(['/usr/bin/git', '-C', str(ROOT), *args],
                          capture_output=True, text=True, timeout=3, check=True)
    return proc.stdout.strip()


def save_new(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def preflight(expected_commit, bus_type):
    # All source/artifact/host checks precede manager access and reservation.
    from verification.nonlinear_port.manufactured_driver import expected_admission, read_limited
    from verification.nonlinear_port.manufactured_manifest import canonical, contract_digest, validate
    if (len(expected_commit) != 40 or any(c not in '0123456789abcdef' for c in expected_commit)
            or git('rev-parse', 'HEAD') != expected_commit
            or git('status', '--porcelain', '--untracked-files=all')
            or git('rev-parse', '--show-toplevel') != str(ROOT)):
        raise RuntimeError('launch checkout is not the expected clean commit')
    allocation = read_limited(ALLOCATION)
    if (allocation['request'] != 'R269' or type(allocation['attempts_granted']) is not int or allocation['attempts_granted'] != 1
            or allocation['run_directory'] != str(RUN)
            or allocation['caller_sha256'] != digest(Path(__file__))
            or allocation['source_inventory_sha256'] != digest(INVENTORY)
            or allocation['artifact_inventory_sha256'] != digest(ARTIFACTS)
            or json.dumps(allocation.get('angular_evidence'), sort_keys=True) !=
               json.dumps(ANGULAR_POLICY, sort_keys=True)):
        raise RuntimeError('published manufactured allocation or caller binding changed')
    inventory = read_limited(INVENTORY)['source_sha256']
    differences = [name for name, expected in inventory.items()
                   if digest(ROOT/name) != expected]
    if differences or digest(MANIFEST) != allocation['manifest_sha256']:
        raise RuntimeError('reviewed source or frozen manifest changed: ' + repr(differences))
    manifest = read_limited(MANIFEST)
    validate(manifest)
    contract_hash = contract_digest(manifest)
    if (contract_hash != allocation['contract_sha256']
            or canonical(allocation['contract']) != canonical(manifest)):
        raise RuntimeError('reviewed manufactured contract changed')
    resolved = Path(PYTHON).resolve(strict=True)
    if (sys.executable != PYTHON or digest(resolved) != PYTHON_SHA256
            or allocation['interpreter'] != PYTHON
            or allocation['executable_sha256'] != PYTHON_SHA256):
        raise RuntimeError('R229 caller/worker interpreter changed')
    artifacts = read_limited(ARTIFACTS)
    if any(digest(Path(name)) != expected for name, expected in
           artifacts['runtime_files_sha256'].items()):
        raise RuntimeError('reviewed runtime artifact changed')
    if any(str(Path(name).resolve(strict=True)) != expected for name, expected in
           artifacts['library_resolutions'].items()):
        raise RuntimeError('reviewed library resolution changed')
    if digest(Path(artifacts['cached_archive'])) != artifacts['package']['sha256']:
        raise RuntimeError('reviewed cached archive changed')
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError('one-use output directory already exists')
    available_kib = next(int(line.split()[1]) for line in
                         Path('/proc/meminfo').read_text().splitlines()
                         if line.startswith('MemAvailable:'))
    if available_kib < 1536*1024:
        raise RuntimeError('less than 1536 MiB host memory available')
    controllers = Path('/sys/fs/cgroup/cgroup.controllers')
    if not controllers.is_file() or not {'memory', 'pids'} <= set(controllers.read_text().split()):
        raise RuntimeError('unified memory/PID controllers unavailable')
    admission = dict(approved=True, fixture='manufactured', mode='single_be_spatial_pilot',
                     kind='manufactured_spatial_pilot', worker_schema=1, attempts_granted=1,
                     run_directory=str(RUN), source_commit=expected_commit,
                     manifest_sha256=allocation['manifest_sha256'],
                     contract_sha256=contract_hash, interpreter=PYTHON,
                     executable=str(resolved), executable_sha256=PYTHON_SHA256,
                     artifact_inventory_sha256=digest(ARTIFACTS))
    expected_admission(admission, MANIFEST.read_bytes(), manifest, RUN,
                       expected_commit, PYTHON, 'PC/WSL daisy / R269')
    bus = bus_type()
    try:
        version = bus.property(bus.path, 'Manager', 'Version', 's')
        if version != allocation['reviewed_manager_version']:
            raise RuntimeError('reviewed manager version changed')
    finally:
        bus.close()
    return dict(admission=admission, source_commit=expected_commit,
                source_files=len(inventory), manifest_sha256=admission['manifest_sha256'],
                contract_sha256=contract_hash, worker_schema=1, interpreter=PYTHON,
                executable=str(resolved), executable_sha256=PYTHON_SHA256,
                host_mem_available_kib=available_kib, manager_version=version,
                run_directory=str(RUN), artifact_inventory_sha256=digest(ARTIFACTS),
                runtime_artifacts_verified=len(artifacts['runtime_files_sha256']))


def expired(signum, frame):
    raise TimeoutError('180-second outer caller timer expired')


def check_angular(directory, source_commit):
    # Read even after the unchanged physical validator refuses the old budget.
    # This can only restrict outer acceptance; it cannot promote INCOMPLETE.
    from verification.nonlinear_port.manufactured_angular import (
        MAX_BYTES, strict_json, validate_numerical_aliases)
    from verification.nonlinear_port.manufactured_driver import read_limited
    from verification.nonlinear_port.source_binding import expected_binding
    with (directory/'angular_audit.json').open('rb') as stream:
        blob = stream.read(MAX_BYTES+1)
    record = strict_json(blob)
    binding = expected_binding(ROOT, dict(source_commit=source_commit,
        interpreter=PYTHON), PYTHON)
    numerical = read_limited(directory/'numerical.json')
    validate_numerical_aliases(record, numerical, binding)
    comparisons = {degree: {name: value['accepted'] for name, value in
        entry['comparisons'].items()} for degree, entry in record['degrees'].items()}
    consistent = all(value for checks in comparisons.values() for value in checks.values())
    return dict(file='angular_audit.json', bytes=len(blob),
        sha256=hashlib.sha256(blob).hexdigest(), valid=True,
        consistent=consistent, comparisons=comparisons)


def main():
    if (len(sys.argv) != 2 or len(sys.argv[1]) != 40
            or any(c not in '0123456789abcdef' for c in sys.argv[1])):
        raise SystemExit('usage: run_once.py EXACT_LAUNCH_COMMIT')
    expected_commit = sys.argv[1]
    started = time.monotonic()
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, LIMIT)
    preflight_facts = None
    result = None
    reason = None
    angular = None
    invoked_supervisor = False
    try:
        supervise_manufactured_once, SystemdBackend, Bus = load_components()
        preflight_facts = preflight(expected_commit, Bus)
        admission = preflight_facts['admission']
        invoked_supervisor = True
        result = supervise_manufactured_once(RUN, MANIFEST, admission,
                                SystemdBackend(ROOT, runtime_seconds=149),
                                source_commit=expected_commit, interpreter=PYTHON,
                                owner='PC/WSL daisy / R269')
        angular = check_angular(RUN, expected_commit)
    except Exception as exc:
        reason = f'{type(exc).__name__}: {exc}'
    elapsed_before_save = time.monotonic()-started
    status = ('PASS' if result is not None and result.get('status') == 'PASS'
              and angular is not None and angular['consistent']
              and reason is None and elapsed_before_save <= LIMIT else 'INCOMPLETE')
    outer = dict(status=status, preflight=preflight_facts, angular_evidence=angular,
                 inner_status=None if result is None else result.get('status'),
                 reason=reason, elapsed_before_caller_save=elapsed_before_save,
                 outer_limit_seconds=LIMIT, final_save_tail_observed=False)
    # A preflight refusal must never append to an existing spent directory.
    if invoked_supervisor and RUN.is_dir():
        save_new(RUN/'caller.json', outer)
        elapsed_after_save = time.monotonic()-started
        if elapsed_after_save > LIMIT:
            status = 'INCOMPLETE'
        save_new(RUN/'caller_completion.json',
                 dict(status=status, elapsed_after_caller_save=elapsed_after_save,
                      final_completion_save_tail_observed=False))
    else:
        elapsed_after_save = time.monotonic()-started
    signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps(dict(status=status, reason=reason,
                          elapsed_after_caller_save=elapsed_after_save,
                          run_directory=str(RUN), inner_status=outer['inner_status'])),
          flush=True)
    return 0 if status == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
