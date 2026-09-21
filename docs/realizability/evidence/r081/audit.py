"""Read-only R076 review counterexamples; fake clocks/callbacks, no live adapters.

Run with Python 3.12 -B and a NEW output directory. Never run the R076 recorder:
it writes its archived ledger. This audit preserves the reviewed source.
"""
from __future__ import annotations

import time
ENTRY = time.monotonic()
import argparse
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import resource
import shutil
import signal
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SOURCE = HERE.parent / "r076/source"
sys.dont_write_bytecode = True
sys.path.insert(0, str(SOURCE))
import monitor_core as core
import host_protocol
import linux_adapter


def dump(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


class Clock:
    def __init__(self, now=10.0):
        self.now = now
    def __call__(self):
        return self.now
    def wait(self, delay):
        assert delay > 0
        self.now += delay


def run_case(tree_fn, *, cleanup_value=None, extra_host=False):
    clock = Clock()
    calls = {"tree": 0, "cleanup": 0, "host": 0}
    pending = []
    def request(seq, sent):
        pending.append((seq, sent))
    def host():
        if pending:
            seq, sent = pending.pop(0)
        elif extra_host:
            seq, sent = calls["host"] + 1, clock()
        else:
            return None
        calls["host"] += 1
        return core.HostReading(seq, sent, clock(), "windows", "ok", 8 << 30, 16 << 30)
    def tree():
        calls["tree"] += 1
        return tree_fn(clock, calls["tree"])
    def cleanup(limit):
        calls["cleanup"] += 1
        return cleanup_value if cleanup_value is not None else {
            "confirmed": True, "errors": [], "survivors": []}
    result = core.supervise(policy=core.Policy(512, 20), tree_reader=tree,
        host_poll=host, host_request=request, clock=clock, wait=clock.wait,
        cleanup=cleanup)
    return result, calls


def tree(clock, seq, *, complete=True, live=False):
    return core.TreeReading(seq, clock(), clock(), "linux", "ok",
        (core.ProcessMember(42, 100, "S", 4096),) if live else (),
        complete, live, None if live else 0)


def counterexamples():
    found = []
    def record(code, detail):
        found.append({"id": code, "status": "reproduced", "observed": detail})

    result, calls = run_case(lambda c, n: tree(c, n, complete=n != 1, live=n == 1))
    assert result["status"] == "completed" and calls["tree"] == 2
    record("F01", {"incomplete_membership_then_completion": result["status"], "calls": calls})

    result, calls = run_case(lambda c, n: tree(c, n))
    assert result["cleanup_confirmed"] and calls["cleanup"] == 0
    record("F02", {"cleanup_confirmed_without_callback": True, "calls": calls})

    def slow(c, n):
        before = c()
        c.now += 1.1
        return replace(tree(c, n), start=before)
    result, calls = run_case(slow)
    assert result["status"] == "completed" and result["elapsed_seconds"]["run"] > 1
    record("F03", {"stale_host_after_tree_read_status": result["status"],
                    "host_end": result["last_host"]["end"], "tree_end": result["last_tree"]["end"]})

    launch = core.validate_launch(now=100, policy=core.Policy(512, 200),
        guest=core.GuestReading(1, 0, 100, "linux", "ok", 8 << 30),
        host=core.HostReading(1, 0, 100, "windows", "ok", 8 << 30, 16 << 30))
    assert launch["status"] == "passed"
    record("F04", {"100_second_acquisition_launch": launch})

    def backwards(c, n):
        value = tree(c, n, live=n == 1)
        return value if n == 1 else replace(value, start=9, end=9)
    result, _ = run_case(backwards)
    assert result["status"] == "completed" and result["last_tree"]["end"] == 9
    record("F05", {"regressed_tree_timestamp_status": result["status"]})

    classified = linux_adapter.classify_cleanup(kill_error=None, child_reaped=1,
        cgroup_populated=0, survivors=[])
    assert classified["confirmed"]
    inconsistent, _ = run_case(lambda c, n: replace(tree(c, n), root_returncode=7),
        cleanup_value={"confirmed": True, "errors": ["kill failed"], "survivors": [[42, 100]]})
    assert inconsistent["cleanup_confirmed"] and inconsistent["survivors"]
    record("F06", {"numeric_flags_confirm_cleanup": classified,
                    "contradictory_cleanup_confirmed": inconsistent["cleanup_confirmed"]})

    try:
        run_case(lambda c, n: replace(tree(c, n), root_returncode=7),
            cleanup_value={"confirmed": False, "errors": [], "survivors": float("nan")})
    except core.MonitorError as exc:
        record("F07", {"nonfinite_cleanup_escapes_report_boundary": str(exc)})
    else:
        raise AssertionError("expected nonfinite cleanup to escape")

    result, calls = run_case(lambda c, n: tree(c, n, live=n == 1), extra_host=True)
    assert result["status"] == "completed" and calls["host"] == 2
    record("F08", {"unsolicited_second_host_reply_accepted": calls["host"]})

    p = host_protocol.HostProtocol(nonce="audit", clock=lambda: 0)
    p.request(1, 0)
    reading = p.reply(b'{"schema":1,"sequence":1,"nonce":"audit","status":"error",'
        b'"status":"ok","error":"API failed","available_bytes":8192,"total_bytes":16384}\n', 0.1)
    assert reading.status == "ok" and reading.error is None
    record("F09", {"duplicate_status_and_API_error_accepted": reading.status})

    spec = importlib.util.spec_from_file_location("r081_guard", SOURCE / "r070_copy/launch_guard.py")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    with tempfile.TemporaryDirectory(prefix="r081-review-") as raw:
        root = Path(raw)
        (root / "input").write_text("fixture\n")
        manifest = root / "manifest.json"
        dump(manifest, {"schema": 1, "files": {"input": guard.sha(root / "input")},
                        "evidence_files": {"input": guard.sha(root / "input")}})
        digest = guard.sha(manifest)
        child = {"status": "complete", "evidence_complete": True,
                 "scientific_checks_passed": True, "source_manifest_sha256": digest}
        watch = {"status": "completed", "returncode": 0, "membership_complete": True,
            "cleanup_confirmed": True, "primary_reasons": ["host_pressure_limit"],
            "cleanup_errors": ["helper still live"], "helper_cleanup_confirmed": False,
            "source_manifest_sha256": digest,
            "child_report_sha256": hashlib.sha256(json.dumps(child, sort_keys=True,
                separators=(",", ":")).encode()).hexdigest()}
        accepted = guard.finalize_child(guard.initial_report(), watch, child,
            source_root=root, source_manifest_path=manifest)
        assert accepted["status"] == "complete" and all(x is None for x in accepted["counts"].values())
        record("F10", {"contradictory_watch_and_missing_counts_status": accepted["status"],
                        "counts": accepted["counts"]})
        before = []
        refused = guard.guarded_launch(root / "disabled", enabled=True,
            child_launcher=lambda: before.append("launched"), attempt_record=root / "attempt.json")
        assert refused["status"] == "prerequisite_refused" and not before and not (root / "attempt.json").exists()

    # Complete empty membership/root-reaped input cannot traverse the Linux helper.
    try:
        linux_adapter.make_membership_reading(cgroup_pids=set(), proc_text={},
            root=(42, 100), page_size=4096)
    except core.MonitorError as exc:
        record("F11", {"empty_membership_helper_refusal": str(exc)})
    else:
        raise AssertionError("expected root-presence precondition")
    return found


def capabilities():
    def read(path):
        try:
            return {"value": Path(path).read_text().strip(), "error": None}
        except OSError as exc:
            return {"value": None, "error": f"{type(exc).__name__}: {exc}"}
    group = read("/proc/self/cgroup")
    mounts = [line for line in Path("/proc/self/mountinfo").read_text().splitlines()
              if " - cgroup2 " in line]
    cg = Path("/sys/fs/cgroup")
    paths = [cg]
    if group["value"]:
        for line in group["value"].splitlines():
            if line.startswith("0::"):
                candidate = cg / line[3:].lstrip("/")
                if candidate != cg:
                    paths.append(candidate)
    rows = []
    for path in paths:
        for name in ("", "cgroup.procs", "cgroup.events", "cgroup.kill", "cgroup.controllers", "cgroup.subtree_control"):
            target = path / name
            try:
                st = target.stat()
                rows.append({"path": str(target), "uid": st.st_uid, "gid": st.st_gid,
                    "mode": oct(st.st_mode & 0o7777), "access_write": os.access(target, os.W_OK),
                    "access_read": os.access(target, os.R_OK)})
            except OSError as exc:
                rows.append({"path": str(target), "error": str(exc)})
    pidfd = {"os_pidfd_open": hasattr(os, "pidfd_open"),
             "signal_pidfd_send_signal": hasattr(signal, "pidfd_send_signal"), "signals_sent": 0}
    try:
        fd = os.pidfd_open(os.getpid())
        os.close(fd)
        pidfd["self_handle_open_close"] = "passed"
    except (OSError, AttributeError) as exc:
        pidfd["self_handle_open_close"] = str(exc)
    mem = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.split(":")[0] in {"MemTotal", "MemAvailable", "SwapTotal", "SwapFree"}:
            key, value = line.split(":")
            mem[key] = int(value.split()[0]) * 1024
    return {"utc": datetime.now(timezone.utc).isoformat(), "os": platform.system(),
        "kernel": platform.release(), "machine": platform.machine(), "hostname": platform.node(),
        "checkout": str(REPO), "python": sys.version, "executable": sys.executable,
        "uid": os.getuid(), "gid": os.getgid(), "page_size": os.sysconf("SC_PAGE_SIZE"),
        "pid1_comm": read("/proc/1/comm"), "self_cgroup": group, "cgroup2_mounts": mounts,
        "cgroup_access_metadata": rows, "pidfd": pidfd, "guest_meminfo_bytes": mem,
        "tool_paths_only_no_launch": {name: shutil.which(name) for name in
            ("powershell.exe", "pwsh.exe", "dotnet", "dotnet.exe", "csc.exe", "x86_64-w64-mingw32-gcc")},
        "windows_native_API_job_assignment_transport": "not exercised",
        "cgroup_write_migration_kill": "not exercised; access metadata is not validation",
        "launch_readiness": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    dump(args.output / "started.json", {"state": "STARTED", "argv": sys.argv,
        "executable": sys.executable, "utc": datetime.now(timezone.utc).isoformat(),
        "scope": "source/fake counterexamples and read-only capability inspection"})
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    signal.alarm(120)
    report = {"status": "in_progress", "physical_execution_enabled": False}
    try:
        report["counterexamples"] = counterexamples()
        report["capabilities"] = capabilities()
        manifest = json.loads((HERE.parent / "r076/source_manifest.json").read_text())
        bindings = manifest["source_sha256"]
        for name, digest in bindings.items():
            assert hashlib.sha256((HERE.parent / "r076" / name).read_bytes()).hexdigest() == digest, name
        for copy, archive in (("r070_original", "r070/source"), ("r073_original_bundle", "r073")):
            for path in (SOURCE / copy).rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts:
                    assert path.read_bytes() == (HERE.parent / archive / path.relative_to(SOURCE / copy)).read_bytes()
        report.update(status="passed", source_bindings=len(bindings),
            preservation="R070/R073 original copies match archives; R076 manifest verified",
            default_deny="enabled=True with injected launcher refused; no attempt claimed")
    except BaseException as exc:
        report.update(status="failed", error={"type": type(exc).__name__, "message": str(exc)})
    report.update(script_entry_to_checks_seconds=time.monotonic() - ENTRY,
        process_lifetime_peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        measurement_limits="duration excludes interpreter startup and final report write; RSS is one process, not a tree",
        audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    dump(args.output / "review.json", report)
    print(json.dumps({"status": report["status"], "counterexamples": len(report.get("counterexamples", [])),
                      "output": str(args.output), "error": report.get("error")}))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
