"""Outer, all-outcome recorder for one resource-capped fixture validation."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

SOURCE = Path(__file__).resolve().parent
EVIDENCE = SOURCE.parent
LEDGER = EVIDENCE / "attempt_ledger.json"


def hashes():
    roots = [SOURCE, SOURCE / "r070_copy"]
    files = []
    for root in roots:
        files.extend(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return {p.relative_to(EVIDENCE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files)) if p != LEDGER}


def cap_address_space():
    import resource as res
    limit = 256 * 1024 * 1024
    res.setrlimit(res.RLIMIT_AS, (limit, limit))


def main():
    if LEDGER.exists():
        ledger = json.loads(LEDGER.read_text())
    else:
        ledger = {"schema": 1, "cumulative_limit_seconds": 120,
                  "address_space_limit_bytes": 256 * 1024 * 1024, "attempts": []}
    if ledger.get("schema") != 1 or not isinstance(ledger.get("attempts"), list):
        raise SystemExit("invalid existing attempt ledger")
    runner_command = [sys.executable, str(Path(__file__).resolve())]
    validator_command = [sys.executable, str((SOURCE / "validate.py").resolve())]
    reconciled = ledger.setdefault("recording_reconciliations", [])
    known = {item.get("attempt") for item in reconciled}
    for previous in ledger["attempts"]:
        if "command" not in previous and previous.get("attempt") not in known:
            reconciled.append({"attempt": previous.get("attempt"),
                "outer_command": runner_command, "validator_command": validator_command,
                "working_directory": str(SOURCE),
                "basis": "reconstructed from the recorded exec invocation and runner source; original attempt record preserved"})
    elapsed_before = sum(float(item.get("elapsed_seconds", 0))
                         for item in ledger["attempts"])
    remaining = 120.0 - elapsed_before
    if remaining <= 0:
        raise SystemExit("cumulative validation budget exhausted; no retry")
    attempt_number = len(ledger["attempts"]) + 1
    r070_original = SOURCE / "r070_original"
    r070_manifest_path = r070_original / "source_manifest.json"
    r070_manifest = json.loads(r070_manifest_path.read_text())
    r070_checks = {}
    for name, expected in r070_manifest["files"].items():
        observed = hashlib.sha256((r070_original / name).read_bytes()).hexdigest()
        r070_checks[name] = {"expected": expected, "observed": observed,
                             "matches": expected == observed}
        if expected != observed:
            raise SystemExit(f"pristine R070 source copy mismatch: {name}")
    r070_copy_guard_hash = hashlib.sha256(
        (SOURCE / "r070_copy" / "launch_guard.py").read_bytes()).hexdigest()
    r070_copy_manifest = json.loads(json.dumps(r070_manifest))
    r070_copy_manifest["files"]["launch_guard.py"] = r070_copy_guard_hash
    r070_copy_manifest["purpose"] = "R076 integration copy; physical launch remains hard-disabled"
    r070_copy_manifest_path = SOURCE / "r070_copy" / "source_manifest.json"
    r070_copy_manifest_path.write_text(json.dumps(
        r070_copy_manifest, indent=2, sort_keys=True) + "\n")
    r073_manifest_path = Path(__file__).resolve().parents[2] / "r073" / "source_manifest.json"
    r073_manifest = json.loads(r073_manifest_path.read_text())
    r073_bundle_checks = {}
    r073_bundle = SOURCE / "r073_original_bundle"
    for name in ("portable_monitor.py", "validate.py", "monitor_contract.md"):
        expected = r073_manifest["files"][name]
        observed = hashlib.sha256((r073_bundle / name).read_bytes()).hexdigest()
        r073_bundle_checks[name] = {"expected": expected, "observed": observed,
                                    "matches": expected == observed}
        if expected != observed:
            raise SystemExit(f"pristine R073 copy mismatch: {name}")
    r073_core_hash = hashlib.sha256((SOURCE / "r073_original.py").read_bytes()).hexdigest()
    if r073_core_hash != r073_manifest["files"]["portable_monitor.py"]:
        raise SystemExit("standalone pristine R073 monitor copy mismatch")
    for name in ("attempt_ledger.json", "result.json", "source_manifest.json"):
        copied = SOURCE / "r073_original_bundle" / name
        archived = Path(__file__).resolve().parents[2] / "r073" / name
        if copied.read_bytes() != archived.read_bytes():
            raise SystemExit(f"pristine R073 evidence copy mismatch: {name}")
    r070_copy_checks = {}
    for name, expected in r070_manifest["files"].items():
        observed = hashlib.sha256((SOURCE / "r070_copy" / name).read_bytes()).hexdigest()
        intended = name == "launch_guard.py"
        if not intended and observed != expected:
            raise SystemExit(f"R070 integration copy changed outside launch guard: {name}")
        r070_copy_checks[name] = {"baseline_sha256": expected,
                                  "copy_sha256": observed,
                                  "modified_for_integration": intended}
    source_manifest = {"schema": 1, "attempt": attempt_number,
        "task": "R076 fixture-only monitor implementation",
        "python": sys.version.split()[0], "source_sha256": hashes(),
        "r070_baseline_manifest_sha256": hashlib.sha256(r070_manifest_path.read_bytes()).hexdigest(),
        "r070_integration_manifest_sha256": hashlib.sha256(
            r070_copy_manifest_path.read_bytes()).hexdigest(),
        "r070_pristine_copy_checks": r070_checks,
        "r070_integration_copy_checks": r070_copy_checks,
        "r073_baseline_manifest_sha256": hashlib.sha256(r073_manifest_path.read_bytes()).hexdigest(),
        "r073_pristine_monitor_sha256": r073_core_hash,
        "r073_pristine_bundle_checks": r073_bundle_checks,
        "physical_execution_enabled": False}
    manifest_path = EVIDENCE / f"source_manifest_attempt_{attempt_number:02d}.json"
    if manifest_path.exists():
        raise SystemExit("source manifest for this attempt already exists")
    manifest_bytes = json.dumps(source_manifest, indent=2, sort_keys=True, allow_nan=False) + "\n"
    manifest_path.write_text(manifest_bytes)
    (EVIDENCE / "source_manifest.json").write_text(manifest_bytes)
    started_wall = time.time()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started_wall))
    entry = {"attempt": attempt_number, "state": "STARTED", "started_utc": started_utc,
             "command": {"runner": runner_command, "validator": validator_command,
                         "working_directory": str(SOURCE)},
             "source_sha256": hashes(), "source_manifest_sha256": hashlib.sha256(manifest_bytes.encode()).hexdigest(),
             "remaining_budget_before_seconds": remaining,
             "time_budget_seconds": 120,
             "address_space_limit_bytes": 256 * 1024 * 1024,
             "measurement": "parent monotonic wall time and child process-lifetime ru_maxrss; includes child interpreter startup/import/reporting"}
    ledger["attempts"].append(entry)
    ledger["cumulative_elapsed_seconds"] = elapsed_before
    LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True) + "\n")
    (EVIDENCE / "result.json").write_text(json.dumps({
        "schema": 1, "status": "in_progress", "attempt": attempt_number,
        "source_manifest": "source_manifest.json", "attempt_ledger": LEDGER.name},
        indent=2, sort_keys=True) + "\n")
    started = time.monotonic()
    timed_out = False
    error = None
    try:
        env = dict(os.environ)
        env["R076_ATTEMPT"] = str(attempt_number)
        proc = subprocess.run([sys.executable, str(SOURCE / "validate.py")],
            cwd=SOURCE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            timeout=remaining, preexec_fn=cap_address_space, env=env)
        returncode = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        returncode = None
        stdout = (exc.stdout or b"").decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = (exc.stderr or b"").decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
    except BaseException as exc:
        returncode = None
        stdout, stderr = "", f"{type(exc).__name__}: {exc}"
        error = {"type": type(exc).__name__, "message": str(exc)}
    elapsed = time.monotonic() - started
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    # Linux reports ru_maxrss in KiB; convert to bytes.
    peak_rss_bytes = int(usage.ru_maxrss * 1024)
    status = "passed" if returncode == 0 and not timed_out else "failed"
    entry.update(state="COMPLETED", ended_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        status=status, returncode=returncode, timed_out=timed_out,
        elapsed_seconds=elapsed, child_process_lifetime_peak_rss_bytes=peak_rss_bytes,
        stdout=stdout, stderr=stderr, error=error)
    ledger["cumulative_elapsed_seconds"] = elapsed_before + elapsed
    prior_peaks = [int(item.get("child_process_lifetime_peak_rss_bytes", 0))
                   for item in ledger["attempts"][:-1]]
    ledger["maximum_measured_child_rss_bytes"] = max(prior_peaks + [peak_rss_bytes])
    LEDGER.write_text(json.dumps(ledger, indent=2, sort_keys=True, allow_nan=False) + "\n")
    fixture_path = EVIDENCE / f"fixture_results_attempt_{attempt_number:02d}.json"
    documentation_path = EVIDENCE / "documentation_validation.json"
    fixture_result = json.loads(fixture_path.read_text()) if fixture_path.exists() else None
    documentation_result = json.loads(documentation_path.read_text()) if documentation_path.exists() else None
    result = {"schema": 1, "status": status, "python": sys.version.split()[0],
        "attempts": len(ledger["attempts"]),
        "cumulative_elapsed_seconds": ledger["cumulative_elapsed_seconds"],
        "cumulative_limit_seconds": ledger["cumulative_limit_seconds"],
        "maximum_child_lifetime_rss_bytes": ledger["maximum_measured_child_rss_bytes"],
        "address_space_limit_bytes": ledger["address_space_limit_bytes"],
        "fixture_checks": fixture_result.get("checks_passed") if fixture_result else None,
        "documentation_validation": documentation_result,
        "physical_execution_enabled": False,
        "physical_limits_seconds_mib": {"wall": 180, "rss": 1536},
        "live_platform_checks": "not run; fixtures only",
        "attempt_ledger": LEDGER.name, "source_manifest": "source_manifest.json"}
    (EVIDENCE / "result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": status, "elapsed_seconds": elapsed,
                      "child_process_lifetime_peak_rss_bytes": peak_rss_bytes,
                      "ledger": str(LEDGER), "returncode": returncode}))
    raise SystemExit(0 if status == "passed" else 1)


if __name__ == "__main__":
    main()
