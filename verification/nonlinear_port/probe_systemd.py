"""Explicit benign host probe, never a FEM admission or numerical fixture.

Two cases only: held/released clean completion and independent expiry with a
child. A new exclusive output directory retains evidence. Stop on unexpected
failure; there is no automatic retry. Run externally on the owning Linux host.
"""
import json
import os
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
from .source_binding import verify_source


def worker(directory, mode):
    reservation = read(directory/'reservation.json')
    held(directory, reservation, _cgroup_path(), verify_source(reservation))
    if mode == 'clean':
        completed(directory, reservation)
        return
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    child = subprocess.Popen([sys.executable, '-c',
        'import os,signal,time; from pathlib import Path; '
        'from verification.nonlinear_port.handshake import publish; '
        'signal.signal(signal.SIGTERM,signal.SIG_IGN); '
        'publish(Path('+repr(str(directory/'child.json'))+'),dict(pid=os.getpid(),ready=True)); '
        'time.sleep(30)'])
    time.sleep(30)
    raise Refusal('independent expiry did not terminate probe')


def probe(directory, source_commit):
    start = time.monotonic()
    directory.mkdir(exist_ok=False)
    results = []
    for mode, runtime in [('clean', 8), ('expiry', 4)]:
        run = directory/mode
        run.mkdir()
        publish(run/'reservation.json', dict(release_nonce=mode,
                source_commit=source_commit, interpreter=sys.executable))
        backend = SystemdBackend(Path(__file__).resolve().parents[2], runtime_seconds=runtime)
        h = None
        record = dict(mode=mode, runtime_seconds=runtime)
        try:
            h = backend.start_held((sys.executable, '-m',
                'verification.nonlinear_port.probe_systemd', '--worker', str(run), mode), run, CAPS)
            record['held_facts'] = h.facts()
            verify_held_scope(record['held_facts'], h.scope_id)
            record['benign_scope_verified'] = True
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
                child_message = read(run/'child.json')
                if child_message.get('ready') is not True:
                    raise Refusal('expiry child not ready')
                child = child_message['pid']
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
            record['elapsed_cumulative_seconds_before_save'] = time.monotonic()-start
            results.append(record)
            publish(run/'probe.json', record)
            elapsed = time.monotonic()-start
            publish(run/'saved.json', dict(observed_elapsed_after_probe_save=elapsed,
                    final_marker_save_tail_observed=False))
        if ('error' in record or 'cleanup_error' in record
                or record.get('cleanup', {}).get('empty') is not True
                or time.monotonic()-start > 30):
            raise Refusal('benign scope probe incomplete; see retained evidence')
    publish(directory/'summary.json', dict(cases=results, elapsed_seconds_before_summary=time.monotonic()-start,
            fem_attempts=0, benign_scope_verified=True, fem_admitted=False))
    elapsed = time.monotonic()-start
    if elapsed > 30:
        publish(directory/'late.json', dict(elapsed_seconds=elapsed))
        raise Refusal('benign probe persistence exceeded allocation')
    print(json.dumps(dict(elapsed_after_summary_save=elapsed, cases=results), indent=2))


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == '--worker' and sys.argv[3] in ('clean', 'expiry'):
        worker(Path(sys.argv[2]), sys.argv[3])
    elif len(sys.argv) == 3:
        probe(Path(sys.argv[1]).resolve(), sys.argv[2])
    else:
        raise SystemExit('usage: python -m verification.nonlinear_port.probe_systemd NEW_DIRECTORY EXPECTED_COMMIT')
