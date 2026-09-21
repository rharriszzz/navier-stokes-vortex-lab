"""One-pass, durable outer recorder for the R082 disposable fixture bundle."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
from attempt_accounting import prior_elapsed

EVIDENCE = Path(__file__).resolve().parent
SOURCE = EVIDENCE / "source"
LEDGER = EVIDENCE / "attempt_ledger.json"
LOCK = EVIDENCE / ".attempt.lock"
LIMIT_S = 120.0
AS_LIMIT = 256 * 1024 * 1024
RESERVE_S = 15.0


def atomic_json(path: Path, value: dict) -> None:
    data = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    temp = path.with_name(path.name + ".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    dirfd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dirfd)
    finally:
        os.close(dirfd)


def source_hashes() -> dict[str, str]:
    result = {}
    for path in sorted(SOURCE.rglob("*")):
        if path.is_file() and "__pycache__" not in path.parts:
            result[path.relative_to(EVIDENCE).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def cap_address_space() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (AS_LIMIT, AS_LIMIT))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))


def main() -> int:
    outer_start = time.monotonic()
    lock_fd = os.open(LOCK, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.write(lock_fd, f"pid={os.getpid()}\n".encode())
    os.fsync(lock_fd)
    os.close(lock_fd)
    try:
        if LEDGER.exists():
            ledger = json.loads(LEDGER.read_text())
        else:
            ledger = {"schema": 2, "limit_seconds": LIMIT_S,
                      "address_space_limit_bytes": AS_LIMIT, "attempts": []}
        if (ledger.get("schema") != 2 or ledger.get("limit_seconds") != LIMIT_S or
                ledger.get("address_space_limit_bytes") != AS_LIMIT or
                not isinstance(ledger.get("attempts"), list)):
            raise RuntimeError("ledger schema/policy invalid; refusing continuation")
        elapsed_prior = prior_elapsed(ledger["attempts"], limit_seconds=LIMIT_S,
                                       address_space_limit_bytes=AS_LIMIT,
                                       reconciliations=ledger.get("reconciliations", []))
        remaining = LIMIT_S - elapsed_prior
        if remaining <= RESERVE_S:
            raise RuntimeError("insufficient reserved execution time; no attempt started")
        number = len(ledger["attempts"]) + 1
        setup_elapsed = time.monotonic() - outer_start
        validator_timeout = remaining - RESERVE_S - setup_elapsed
        if validator_timeout <= 0:
            raise RuntimeError("startup consumed the reserved validator share; no attempt started")
        started = {"attempt": number, "state": "STARTED",
            "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "command": [sys.executable, str(SOURCE / "validate.py")],
            "python": sys.version.split()[0], "source_sha256": source_hashes(),
            "remaining_before_seconds": remaining, "validator_timeout_seconds": validator_timeout,
            "finalization_reserve_seconds": RESERVE_S,
            "address_space_limit_bytes": AS_LIMIT, "cpu_limit_seconds": 10,
            "checkpoint": "checkpoints/latest.json"}
        attempt_path = EVIDENCE / f"attempt_{number:02d}.json"
        fd = os.open(attempt_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(started, stream, sort_keys=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        ledger["attempts"].append(started)
        ledger["cumulative_elapsed_seconds"] = elapsed_prior
        atomic_json(LEDGER, ledger)
        checkpoint = EVIDENCE / "checkpoints" / "latest.json"
        checkpoint.parent.mkdir(exist_ok=True)
        atomic_json(checkpoint, {"schema": 1, "state": "STARTED", "attempt": number,
                                 "source_sha256": started["source_sha256"]})
        started_at = time.monotonic()
        timed_out = False
        try:
            proc = subprocess.run([sys.executable, str(SOURCE / "validate.py")],
                cwd=SOURCE, env={**os.environ, "R082_ATTEMPT": str(number)},
                capture_output=True, text=True, timeout=validator_timeout,
                preexec_fn=cap_address_space)
            code, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            code = None
            stdout = str(exc.stdout or "")[-4000:]
            stderr = str(exc.stderr or "")[-4000:]
        measured = time.monotonic() - outer_start
        rss = int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
        fixture = EVIDENCE / f"fixture_results_attempt_{number:02d}.json"
        status = "passed" if code == 0 and not timed_out and rss <= AS_LIMIT and fixture.exists() else "failed"
        row = ledger["attempts"][-1]
        accounted_elapsed = measured + RESERVE_S
        row.update(state="COMPLETED", status=status,
            ended_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            validator_returncode=code, timed_out=timed_out, stdout=stdout[-4000:], stderr=stderr[-4000:],
            validator_elapsed_seconds=time.monotonic() - started_at,
            outer_wall_measured_seconds=measured, outer_elapsed_seconds=accounted_elapsed,
            child_lifetime_peak_rss_bytes=rss,
            source_sha256_after=source_hashes(), fixture_result=fixture.name if fixture.exists() else None)
        ledger["cumulative_elapsed_seconds"] = elapsed_prior + accounted_elapsed
        ledger["maximum_child_lifetime_peak_rss_bytes"] = max(
            [int(item.get("child_lifetime_peak_rss_bytes", 0)) for item in ledger["attempts"]])
        atomic_json(LEDGER, ledger)
        atomic_json(attempt_path, row)
        atomic_json(EVIDENCE / "source_manifest.json", {"schema": 1,
            "task": "R082 fixture-only monitor repairs", "python": sys.version.split()[0],
            "source_sha256": row["source_sha256_after"],
            "physical_execution_enabled": False})
        atomic_json(checkpoint, {"schema": 1, "state": "COMPLETED", "attempt": number,
                                 "status": status, "outer_elapsed_seconds": accounted_elapsed})
        atomic_json(EVIDENCE / "result.json", {"schema": 2, "status": status,
            "attempts": len(ledger["attempts"]),
            "cumulative_elapsed_seconds": ledger["cumulative_elapsed_seconds"],
            "limit_seconds": LIMIT_S, "maximum_child_lifetime_peak_rss_bytes": rss,
            "address_space_limit_bytes": AS_LIMIT, "physical_execution_enabled": False,
            "physical_limits_seconds_mib": {"wall": 180, "rss": 1536},
            "scope": "fixture-only; no live OS operations, workloads, FEM or physical execution"})
        LOCK.unlink()
        return 0 if status == "passed" else 1
    finally:
        # Keep a STARTED record and lock after an exception: that is an open
        # attempt and must be reconciled, never retried as a fresh allowance.
        pass


if __name__ == "__main__":
    raise SystemExit(main())
