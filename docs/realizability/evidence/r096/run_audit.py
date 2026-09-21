"""Exclusive R096 audit invocation; not a replacement R088 recorder or allowance."""
import time
ENTRY = time.monotonic()
from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('w') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def caps():
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1 << 20, 1 << 20))


def main():
    assert sys.version_info[:3] == (3, 12, 13)
    out = HERE / 'attempt_01'
    out.mkdir(exist_ok=False)
    paths = sorted(p for p in (HERE.parent / 'r088').rglob('*') if p.is_file())
    paths += [HERE / 'audit.py', Path(__file__).resolve()]
    bindings = {str(p.relative_to(HERE.parent)): sha(p) for p in paths}
    save(out / 'started.json', dict(schema=1, state='STARTED', request='R096', attempt=1,
         python=sys.version, source_input_sha256=bindings, child_wall_seconds=10,
         child_address_space_bytes=256 << 20, setup_final_reservation_seconds=10,
         total_review_reservation_seconds=20, historical_allowances_reset=False,
         exclusions=['audit guard startup before ENTRY', 'audit guard final receipt fsync and exit']))
    start = time.monotonic()
    code, timed_out = None, False
    with (out / 'stdout.txt').open('wb') as stdout, (out / 'stderr.txt').open('wb') as stderr:
        try:
            proc = subprocess.run([sys.executable, '-B', str(HERE / 'audit.py')],
                                  stdout=stdout, stderr=stderr, timeout=min(10, 15-(start-ENTRY)),
                                  preexec_fn=caps)
            code = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
    end = time.monotonic()
    unchanged = all(sha(HERE.parent / n) == h for n, h in bindings.items())
    rss = int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
    result = dict(schema=1, state='COMPLETED', request='R096', attempt=1,
         status='passed' if code == 0 and not timed_out and unchanged else 'STOP_REVIEW_REQUIRED',
         returncode=code, timed_out=timed_out, child_seconds=end-start,
         child_lifetime_peak_rss_bytes=rss, unchanged_inputs=unchanged,
         output_sha256={p.name:sha(p) for p in out.iterdir() if p.is_file()},
         observed_guard_seconds=time.monotonic()-ENTRY,
         unmeasured_final_reserve_seconds=5,
         charged_seconds=time.monotonic()-ENTRY+5,
         exclusions=['audit guard startup before ENTRY', 'audit guard final receipt fsync and exit'],
         whole_recorder_certified=False, archived_mains_executed=False)
    if result['charged_seconds'] > 20 or rss > 256 << 20:
        result['status'] = 'STOP_REVIEW_REQUIRED'
    save(out / 'receipt.json', result)
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
