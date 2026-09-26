"""R234 finite caller for one new repaired-source Poiseuille allocation.

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
RUN = Path('/tmp/navier-poiseuille-r234-once')
PYTHON = '/tmp/navier-fenicsx-r229/bin/python'
PYTHON_SHA256 = '5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3'
MANIFEST = ROOT/'verification/nonlinear_port/future_fem.json'
INVENTORY = ROOT/'docs/realizability/evidence/r233/checks.json'
EXPECTED_MANIFEST = '7a8bda917e6b46994ad24c68e0b6c6013b7d6776f90c86a6de763f31f52fa558'
LIMIT = 180


def load_components():
    # Include project imports in the outer timer and make direct path execution work.
    from verification.nonlinear_port.supervision import supervise_once
    from verification.nonlinear_port.systemd_backend import SystemdBackend
    from verification.nonlinear_port.systemd_bus import Bus
    return supervise_once, SystemdBackend, Bus


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if (git('rev-parse', 'HEAD') != expected_commit or
            git('status', '--porcelain', '--untracked-files=all') or
            git('rev-parse', '--show-toplevel') != str(ROOT)):
        raise RuntimeError('launch checkout is not the expected clean commit')
    inventory = json.loads(INVENTORY.read_text())['source_sha256']
    differences = [name for name, expected in inventory.items()
                   if digest(ROOT/name) != expected]
    if differences or digest(MANIFEST) != EXPECTED_MANIFEST:
        raise RuntimeError('reviewed source or frozen manifest changed: ' + repr(differences))
    resolved = Path(PYTHON).resolve(strict=True)
    if digest(resolved) != PYTHON_SHA256:
        raise RuntimeError('R229 interpreter hash changed')
    if RUN.exists() or RUN.is_symlink():
        raise RuntimeError('one-use output directory already exists')
    available_kib = next(int(line.split()[1]) for line in
                         Path('/proc/meminfo').read_text().splitlines()
                         if line.startswith('MemAvailable:'))
    if available_kib < 1536*1024:
        raise RuntimeError('less than 1536 MiB host memory available')
    if not Path('/sys/fs/cgroup/cgroup.controllers').is_file():
        raise RuntimeError('unified cgroup unavailable')
    bus = bus_type()
    try:
        version = bus.property(bus.path, 'Manager', 'Version', 's')
    finally:
        bus.close()
    return dict(source_commit=expected_commit, source_files=len(inventory),
                manifest_sha256=EXPECTED_MANIFEST, interpreter=PYTHON,
                executable=str(resolved), executable_sha256=PYTHON_SHA256,
                host_mem_available_kib=available_kib, manager_version=version,
                run_directory=str(RUN))


def expired(signum, frame):
    raise TimeoutError('180-second outer caller timer expired')


def main():
    if len(sys.argv) != 2 or len(sys.argv[1]) != 40:
        raise SystemExit('usage: run_once.py EXACT_LAUNCH_COMMIT')
    expected_commit = sys.argv[1]
    started = time.monotonic()
    signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, LIMIT)
    preflight_facts = None
    result = None
    reason = None
    try:
        supervise_once, SystemdBackend, Bus = load_components()
        preflight_facts = preflight(expected_commit, Bus)
        admission = dict(approved=True, fixture='poiseuille', attempts_granted=1,
                         run_directory=str(RUN), source_commit=expected_commit,
                         manifest_sha256=EXPECTED_MANIFEST)
        result = supervise_once(RUN, MANIFEST, admission,
                                SystemdBackend(ROOT, runtime_seconds=149),
                                source_commit=expected_commit, interpreter=PYTHON,
                                owner='PC/WSL daisy / R234')
    except Exception as exc:
        reason = f'{type(exc).__name__}: {exc}'
    elapsed_before_save = time.monotonic()-started
    status = ('PASS' if result is not None and result.get('status') == 'PASS'
              and reason is None and elapsed_before_save <= LIMIT else 'INCOMPLETE')
    outer = dict(status=status, preflight=preflight_facts,
                 inner_status=None if result is None else result.get('status'),
                 reason=reason, elapsed_before_caller_save=elapsed_before_save,
                 outer_limit_seconds=LIMIT, final_save_tail_observed=False)
    if RUN.is_dir():
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
