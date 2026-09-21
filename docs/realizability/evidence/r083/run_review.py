"""Single-use R083 audit recorder; timing scope is explicit, not live certification."""
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
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


def main():
    start = time.monotonic()
    sources = [HERE / "audit.py", Path(__file__)]
    sources += list((HERE.parent / "r082").rglob("*.py"))
    hashes = {str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    command = [sys.executable, "-B", str(HERE / "audit.py")]
    persist(HERE / "audit_started.json", {"state": "STARTED", "command": command,
        "sources": hashes, "child_timeout_seconds": 10, "child_address_space_bytes": 256 << 20,
        "child_cpu_seconds": 5, "audit_reservation_seconds": 30,
        "scope": "one source/fake review; no retry; excludes recorder interpreter startup/imports"})
    child_start = time.monotonic()
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=10, preexec_fn=limits)
        result = {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "timed_out": False}
    except subprocess.TimeoutExpired:
        result = {"returncode": None, "timed_out": True}
    result.update(state="COMPLETED", child_elapsed_seconds=time.monotonic() - child_start,
        recorder_elapsed_before_final_persistence_seconds=time.monotonic() - start,
        child_lifetime_peak_rss_bytes=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024,
        timing_limitations="recorder startup/imports and this final fsync excluded; no full-wrapper compliance claim")
    persist(HERE / "audit_completed.json", result)
    print(json.dumps(result))
    return 0 if result.get("returncode") == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
