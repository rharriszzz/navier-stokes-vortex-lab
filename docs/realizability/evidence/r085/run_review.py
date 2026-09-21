"""One R085 audit invocation, exclusive record, bounded child, explicit timing limits."""
from pathlib import Path
import hashlib
import json
import os
import resource
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def persist(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_FSIZE, (64 << 10, 64 << 10))


def main():
    started = time.monotonic()
    assert sys.version_info[:3] == (3, 12, 13)
    sources = [HERE / "audit.py", Path(__file__)]
    sources += [p for p in (HERE.parent / "r084").rglob("*") if p.is_file() and "__pycache__" not in p.parts]
    sources += [HERE.parent / "r081/live_suite.json"]
    hashes = {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    command = [sys.executable, "-B", str(HERE / "audit.py")]
    persist(HERE / "audit_started.json", dict(state="STARTED", command=command,
        sources=hashes, child_timeout_seconds=10, child_address_space_bytes=256 << 20,
        child_cpu_seconds=5, child_file_limit_bytes=64 << 10, audit_reservation_seconds=30,
        scope="one source/fake audit; no retry; excludes recorder startup/imports"))
    child_start = time.monotonic()
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            proc = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=10, preexec_fn=limits)
            result = dict(returncode=proc.returncode, timed_out=False)
        except subprocess.TimeoutExpired:
            result = dict(returncode=None, timed_out=True)
        child_elapsed = time.monotonic() - child_start
        for name, stream in (("stdout", stdout), ("stderr", stderr)):
            stream.seek(0)
            result[name] = stream.read(64 << 10).decode(errors="replace")
    result.update(state="COMPLETED", child_elapsed_seconds=child_elapsed,
        child_lifetime_peak_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
        sources_unchanged=all(hashlib.sha256(p.read_bytes()).hexdigest() == hashes[str(p.relative_to(HERE.parent))] for p in sources),
        recorder_elapsed_before_final_persistence_seconds=time.monotonic() - started,
        timing_limitations="startup/imports and final fsync excluded; 30 s reservation is not independently certified whole-recorder time")
    persist(HERE / "audit_completed.json", result)
    print(json.dumps(result))
    return 0 if result["returncode"] == 0 and result["sources_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
