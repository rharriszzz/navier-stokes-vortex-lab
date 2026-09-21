"""One-shot outer recorder for the R084 fixture-only validation bundle."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import shutil
import subprocess
import sys
import time
import tempfile

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "source"
LOCK = HERE / ".attempt.lock"
LEDGER = HERE / "attempt_ledger.json"
RECONCILIATIONS = HERE / "reconciliations.json"
AS_LIMIT = 256 * 1024 * 1024
LIMIT_S = 120.0
FINAL_RESERVE_S = 15.0
UNMEASURED_RESERVE_S = 5.0

sys.path.insert(0, str(SOURCE))
from attempt_accounting import prior_elapsed


def atomic_json(path: Path, value: dict) -> None:
    payload = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    temp = path.with_name(path.name + f".{os.getpid()}.tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)
    dfd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(dfd)
    finally:
        os.close(dfd)


def inventory() -> dict[str, Path]:
    files = {path.relative_to(HERE).as_posix(): path
             for path in sorted(SOURCE.rglob("*"))
             if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"}
    files["run_r084.py"] = HERE / "run_r084.py"
    return files


def hashes(files: dict[str, Path]) -> dict[str, str]:
    return {name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in sorted(files.items())}


def cap_child() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (AS_LIMIT, AS_LIMIT))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 * 1024, 16 * 1024))


def bounded_text(stream) -> str:
    stream.flush()
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(max(0, size - 4096))
    return stream.read(4096).decode("utf-8", errors="replace")


def main() -> int:
    if sys.version_info[:3] != (3, 12, 13):
        raise RuntimeError("R084 requires the verified Python 3.12.13 environment")
    outer_start = time.monotonic()
    fd = os.open(LOCK, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.write(fd, f"pid={os.getpid()}\n".encode())
    os.fsync(fd)
    os.close(fd)
    start_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    source_files = inventory()
    source_before = hashes(source_files)
    if LEDGER.exists():
        ledger = json.loads(LEDGER.read_text())
    else:
        ledger = {"schema": 1, "limit_seconds": LIMIT_S,
                  "address_space_limit_bytes": AS_LIMIT, "attempts": []}
    if (ledger.get("schema") != 1 or ledger.get("limit_seconds") != LIMIT_S or
            ledger.get("address_space_limit_bytes") != AS_LIMIT):
        raise RuntimeError("ledger schema/policy mismatch; no retry")
    reconciliation_doc = json.loads(RECONCILIATIONS.read_text()) if RECONCILIATIONS.exists() else {
        "schema": 1, "reconciliations": []}
    if reconciliation_doc.get("schema") != 1 or not isinstance(
            reconciliation_doc.get("reconciliations"), list):
        raise RuntimeError("reconciliation evidence malformed; no retry")
    reconciliations = reconciliation_doc["reconciliations"]
    prior = prior_elapsed(ledger.get("attempts"), limit_seconds=LIMIT_S,
                          address_space_limit_bytes=AS_LIMIT,
                          reconciliations=reconciliations,
                          allow_pending_reconciliation=True)
    for event in reconciliations:
        if event.get("attempt") == len(ledger.get("attempts", [])) and \
                event.get("corrected_source_sha256") != source_before:
            raise RuntimeError("pending reconciliation does not bind current source; no retry")
    remaining = LIMIT_S - prior
    if remaining <= FINAL_RESERVE_S + UNMEASURED_RESERVE_S:
        raise RuntimeError("insufficient reserved execution time; no attempt")
    number = len(ledger["attempts"]) + 1
    attempt_path = HERE / f"attempt_{number:02d}.json"
    started = {"schema": 1, "attempt": number, "state": "STARTED",
        "started_utc": start_utc, "command": [sys.executable, str(SOURCE / "validate.py")],
        "python": sys.version.split()[0], "executable": sys.executable,
        "source_sha256_before": source_before,
        "remaining_before_seconds": remaining,
        "address_space_limit_bytes": AS_LIMIT, "cpu_limit_seconds": 10,
        "per_stream_output_limit_bytes": 16384,
        "uncovered_measurement_scope": [
            "Python interpreter startup/imports before recorder main entry",
            "fixed five-second final-persistence reserve is conservatively charged, not timed"]}
    afd = os.open(attempt_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(afd, "w") as stream:
        json.dump(started, stream, sort_keys=True, allow_nan=False)
        stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
    ledger["attempts"].append(started)
    ledger["reconciliations"] = reconciliations
    atomic_json(LEDGER, ledger)
    checkpoint = HERE / "checkpoints" / "latest.json"
    checkpoint.parent.mkdir(exist_ok=True)
    atomic_json(checkpoint, {"schema": 1, "state": "STARTED", "attempt": number,
                             "source_sha256": source_before})

    setup_start = time.monotonic()
    manifest = {"schema": 1, "task": "R084 fixture-only monitor repairs",
        "python": sys.version.split()[0], "physical_execution_enabled": False,
        "source_sha256": {name.removeprefix("source/"): digest
                           for name, digest in source_before.items()
                           if name.startswith("source/") and name.endswith(".py")},
        "file_sha256": source_before}
    atomic_json(HERE / "source_manifest.json", manifest)
    snapshot = HERE / "source_snapshots" / f"attempt_{number:02d}"
    snapshot.mkdir(parents=True, exist_ok=False)
    archived = {}
    for name, source_path in source_files.items():
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target)
        archived[name] = hashlib.sha256(target.read_bytes()).hexdigest()
    if archived != source_before or hashes(inventory()) != source_before:
        raise RuntimeError("source changed during archival; attempt remains open")
    setup_elapsed = time.monotonic() - setup_start
    setup_map = dict(started, source_archive_sha256=archived,
        source_archive="source_snapshots/attempt_%02d" % number,
        setup_elapsed_seconds=setup_elapsed)
    atomic_json(attempt_path, setup_map)
    ledger["attempts"][-1] = setup_map
    atomic_json(LEDGER, ledger)

    elapsed_before_child = time.monotonic() - outer_start
    child_timeout = remaining - FINAL_RESERVE_S - UNMEASURED_RESERVE_S - elapsed_before_child
    if child_timeout <= 0:
        raise RuntimeError("setup exhausted the reserved validator share; attempt stays open")
    child_start = time.monotonic()
    timed_out = False
    try:
        with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:
            proc = subprocess.run([sys.executable, str(SOURCE / "validate.py")],
                cwd=SOURCE, env={**os.environ, "R084_ATTEMPT": str(number)},
                stdout=stdout_file, stderr=stderr_file, timeout=child_timeout,
                preexec_fn=cap_child)
            code, stdout, stderr = (proc.returncode, bounded_text(stdout_file),
                                    bounded_text(stderr_file))
    except subprocess.TimeoutExpired as exc:
        timed_out, code = True, None
        stdout, stderr = str(exc.stdout or "")[-4096:], str(exc.stderr or "")[-4096:]
    child_elapsed = time.monotonic() - child_start
    final_start = time.monotonic()
    measured_rss = int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss * 1024)
    fixture = HERE / f"fixture_results_attempt_{number:02d}.json"
    progress_path = HERE / f"progress_attempt_{number:02d}.json"
    partial_progress = (json.loads(progress_path.read_text()) if progress_path.exists() else
                        {"status": "no validator check checkpoint was emitted"})
    fixture_data = json.loads(fixture.read_text()) if fixture.is_file() else None
    fixture_hash = hashlib.sha256(fixture.read_bytes()).hexdigest() if fixture.is_file() else None
    report_matches = (isinstance(fixture_data, dict) and fixture_data.get("attempt") == number and
        fixture_data.get("status") == "passed" and
        fixture_data.get("checks_passed") == len(fixture_data.get("checks", [])) and
        partial_progress.get("state") == "COMPLETED" and
        partial_progress.get("attempt") == number and
        partial_progress.get("checks") == fixture_data.get("checks"))
    resource_stop = (timed_out or measured_rss > AS_LIMIT or
                     code in (-signal.SIGXCPU, -signal.SIGXFSZ))
    status = "passed" if code == 0 and not timed_out and measured_rss <= AS_LIMIT and fixture.is_file() else "failed"
    if not report_matches:
        status = "failed"
        stderr += "\nfixture report/progress checkpoint disagreement"
    source_after = hashes(inventory())
    if source_after != source_before:
        status = "failed"
        stderr += "\nsource changed during validator execution"
    final_elapsed = time.monotonic() - final_start
    measured = time.monotonic() - outer_start
    outer_elapsed = measured + UNMEASURED_RESERVE_S
    completed = {**setup_map, "state": "COMPLETED", "status": status,
        "ended_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "validator_returncode": code, "timed_out": timed_out,
        "resource_stop": resource_stop, "stdout": stdout, "stderr": stderr,
        "validator_child_elapsed_seconds": child_elapsed,
        "outer_wall_measured_seconds": measured,
        "outer_elapsed_seconds": outer_elapsed,
        "timing_intervals_seconds": {"setup_and_snapshot": setup_elapsed,
            "validator_child": child_elapsed, "finalization": final_elapsed},
        "child_lifetime_peak_rss_bytes": measured_rss,
        "source_sha256_after": source_after,
        "source_archive_sha256": archived,
        "partial_fixture_progress": partial_progress,
        "fixture_result": fixture.name if fixture.is_file() else None,
        "fixture_result_sha256": fixture_hash}
    # Keep the COMPLETE record and lock on any failed outcome: accounting will refuse it.
    atomic_json(attempt_path, completed)
    ledger["attempts"][-1] = completed
    ledger["cumulative_elapsed_seconds"] = prior + outer_elapsed
    ledger["maximum_child_lifetime_peak_rss_bytes"] = max(
        [row.get("child_lifetime_peak_rss_bytes", 0) for row in ledger["attempts"]])
    atomic_json(LEDGER, ledger)
    atomic_json(checkpoint, {"schema": 1, "state": "COMPLETED", "attempt": number,
        "status": status, "outer_elapsed_seconds": outer_elapsed,
        "maximum_child_lifetime_peak_rss_bytes": ledger["maximum_child_lifetime_peak_rss_bytes"]})
    result = {"schema": 1, "status": status, "attempts": len(ledger["attempts"]),
        "cumulative_elapsed_seconds": ledger["cumulative_elapsed_seconds"],
        "limit_seconds": LIMIT_S,
        "maximum_child_lifetime_peak_rss_bytes": ledger["maximum_child_lifetime_peak_rss_bytes"],
        "address_space_limit_bytes": AS_LIMIT, "physical_execution_enabled": False,
        "scope": "fixtures only; no live operation, workload, FEM or physical execution"}
    atomic_json(HERE / "result.json", result)
    if status == "passed":
        prior_elapsed(ledger["attempts"], limit_seconds=LIMIT_S,
                      address_space_limit_bytes=AS_LIMIT,
                      reconciliations=reconciliations)
        if (result["attempts"] != len(ledger["attempts"]) or
                result["cumulative_elapsed_seconds"] != prior_elapsed(
                    ledger["attempts"], limit_seconds=LIMIT_S,
                    address_space_limit_bytes=AS_LIMIT, reconciliations=reconciliations) or
                result["maximum_child_lifetime_peak_rss_bytes"] != max(
                    row["child_lifetime_peak_rss_bytes"] for row in ledger["attempts"])):
            raise RuntimeError("derived attempt summaries disagree with the ledger")
        LOCK.unlink()
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
