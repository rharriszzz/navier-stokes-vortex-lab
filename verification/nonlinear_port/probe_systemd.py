"""Explicit benign host probe, never a FEM admission or numerical fixture.

Two cases only: held/released clean completion and independent expiry with a
child. A new exclusive output directory retains evidence. Stop on unexpected
failure; there is no automatic retry. Run externally on the owning Linux host.
"""
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

from .handshake import held, completed, publish, read
from .supervision import CAPS, verify_held_scope
from .prototype import Refusal
from .systemd_backend import SystemdBackend
from .worker import _cgroup_path


def worker(directory, mode):
    reservation = read(directory/'reservation.json')
    held(directory, reservation, _cgroup_path())
    if mode == 'clean':
        completed(directory, reservation)
        return
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    child = subprocess.Popen([sys.executable, '-c',
        'import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(30)'])
    publish(directory/'child.json', dict(pid=child.pid))
    time.sleep(30)
    raise Refusal('independent expiry did not terminate probe')


def probe(directory):
    start = time.monotonic()
    directory.mkdir(exist_ok=False)
    results = []
    for mode, runtime in [('clean', 6), ('expiry', 2)]:
        run = directory/mode
        run.mkdir()
        publish(run/'reservation.json', dict(release_nonce=mode))
        backend = SystemdBackend(Path(__file__).resolve().parents[2], runtime_seconds=runtime)
        h = None
        record = dict(mode=mode, runtime_seconds=runtime)
        try:
            h = backend.start_held((sys.executable, '-m',
                'verification.nonlinear_port.probe_systemd', '--worker', str(run), mode), run, CAPS)
            record['held_facts'] = h.facts()
            # Whole-task admission MUST refuse the known outside control clients.
            try:
                verify_held_scope(record['held_facts'], h.scope_id)
            except Refusal as exc:
                record['admission_refused'] = str(exc)
            else:
                raise AssertionError('worker-only scope incorrectly admitted whole task')
            h.release()  # explicit benign probe authorization only
            if mode == 'clean':
                record['exit'] = h.wait(8)
                if record['exit']['exit_code'] != 0:
                    raise Refusal('benign clean worker failed')
            else:
                deadline = time.monotonic()+6
                while not (run/'child.json').exists():
                    if time.monotonic() >= deadline:
                        raise Refusal('expiry child not observed')
                    time.sleep(.02)
                child = read(run/'child.json')['pid']
                record['child_pid'] = child
                record['members_before_expiry'] = h.pids()
                if child not in record['members_before_expiry']:
                    raise Refusal('child outside the worker cgroup')
                # No controller stop/wait call before manager expiry observation.
                while time.monotonic() < deadline:
                    props = h.show()
                    if props['ActiveState'] == 'failed':
                        record['independent_exit'] = props
                        break
                    time.sleep(.05)
                else:
                    raise Refusal('independent manager expiry not observed')
                if props.get('Result') != 'timeout':
                    raise Refusal('worker exited for a reason other than manager expiry')
        except Exception as exc:
            record['error'] = f'{type(exc).__name__}: {exc}'
        finally:
            h = h or backend.active_handle
            if h is not None:
                try:
                    h.stop()
                    record['cleanup'] = h.cleanup()
                except Exception as exc:
                    record['cleanup_error'] = str(exc)
            record['elapsed_cumulative_seconds'] = time.monotonic()-start
            results.append(record)
            publish(run/'probe.json', record)
        if ('error' in record or 'cleanup_error' in record
                or record.get('cleanup', {}).get('empty') is not True
                or time.monotonic()-start > 30):
            raise Refusal('benign scope probe incomplete; see retained evidence')
    publish(directory/'summary.json', dict(cases=results, elapsed_seconds=time.monotonic()-start,
                                           fem_attempts=0, whole_task_admitted=False))
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--worker' and sys.argv[3] in ('clean', 'expiry'):
        worker(Path(sys.argv[2]), sys.argv[3])
    elif len(sys.argv) == 2:
        probe(Path(sys.argv[1]).resolve())
    else:
        raise SystemExit('usage: python -m verification.nonlinear_port.probe_systemd NEW_DIRECTORY')
