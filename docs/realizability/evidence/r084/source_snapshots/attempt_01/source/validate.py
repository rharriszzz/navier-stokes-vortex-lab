"""Fixture-only validation for the versioned R076 monitor bundle."""
from __future__ import annotations

import hashlib
import importlib.util
import contextlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import os
import re
import ast

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(1, str(ROOT.parent))
from attempt_accounting import prior_elapsed
import host_protocol
import linux_adapter
import monitor_core as core
import owned_run

checks: list[dict] = []


def check(name, fn):
    fn()
    checks.append({"name": name, "status": "passed"})


def raises(exc, fn):
    try:
        fn()
    except exc:
        return
    raise AssertionError(f"expected {exc.__name__}")


class Clock:
    def __init__(self, value=0.0):
        self.value = value
        self.waits = []

    def now(self):
        return self.value

    def wait(self, seconds):
        assert seconds > 0
        self.waits.append(seconds)
        self.value += seconds


def host_reading(seq=1, start=0.0, end=0.0, available=(8192 << 20), total=(16384 << 20), status="ok"):
    return core.HostReading(seq, start, end, "fixture-windows", status,
                            available if status == "ok" else None,
                            total if status == "ok" else None,
                            None if status == "ok" else "fixture API error")


def guest_reading(seq=1, start=95.0, end=99.0, available=(4096 << 20), status="ok"):
    return core.GuestReading(seq, start, end, "fixture-wsl", status,
                             available if status == "ok" else None,
                             None if status == "ok" else "fixture guest read error")


def proc_stat(pid, *, comm="fixture ) worker", state="S", ppid=1, pgrp=1,
              session=1, start=100, rss=2):
    fields = [state, str(ppid), str(pgrp), str(session)] + ["0"] * 18
    fields[19] = str(start)
    fields[21] = str(rss)
    return f"{pid} ({comm}) " + " ".join(fields)


def load_guard():
    path = ROOT / "r070_copy" / "launch_guard.py"
    spec = importlib.util.spec_from_file_location("r076_launch_guard", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_launch_gate():
    policy = core.Policy(tree_cap_mib=1536, deadline=60)
    exact = host_reading(1, 95.0, 99.0, available=int((1536 + 1024) * (1 << 20)))
    guest = guest_reading(1, 95.0, 100.0)
    result = core.validate_launch(now=100, policy=policy, guest=guest, host=exact)
    assert result["status"] == "passed"
    raises(core.MonitorError, lambda: core.validate_launch(
        now=100, policy=policy, guest=guest_reading(available=(4096 << 20) - 1), host=exact))
    raises(core.MonitorError, lambda: core.validate_launch(
        now=100, policy=policy, guest=guest,
        host=host_reading(1, 95, 99,
            available=int((1536 + 1024) * (1 << 20)) - 1)))
    raises(core.MonitorError, lambda: core.validate_launch(
        now=100, policy=policy,
        guest=core.GuestReading(1, 95, 100, "fixture-wsl", "ok", True), host=exact))
    raises(core.MonitorError, lambda: core.validate_launch(
        now=100, policy=policy, guest=guest_reading(1, 69.0, 69.999), host=exact))
    raises(core.MonitorError, lambda: core.validate_launch(
        now=100, policy=policy, guest=guest_reading(1, 69.999, 100), host=exact))
    raises(core.MonitorError, lambda: core.validate_launch(
        now=100, policy=policy, guest=guest_reading(1, 99, 101), host=exact))
    raises(core.MonitorError, lambda: core.validate_launch(
        now=100, policy=policy, guest=guest_reading(status="error"), host=exact))


def drive(tree_factory, *, cleanup=None, policy=None, sink=None, checkpoint=None):
    clock = Clock()
    reads = iter(tree_factory(clock))
    requests = []
    responses = []

    def request(seq, at):
        requests.append((seq, at))
        responses.append(host_reading(seq, at, at))

    def poll():
        return responses.pop(0) if responses else None

    result = core.supervise(policy=policy or core.Policy(1536, 1.0),
        tree_reader=lambda: next(reads), host_poll=poll, host_request=request,
        clock=clock.now, wait=clock.wait,
        cleanup=cleanup or (lambda limit: cleanup_result()),
        report_sink=sink, checkpoint_sink=checkpoint)
    return result, clock, requests


def tree(seq, at, *, members=None, alive=True, code=None, complete=True,
         status="ok", start=None, end=None):
    return core.TreeReading(seq, at if start is None else start,
        at if end is None else end, "fixture-linux", status,
        tuple(members if members is not None else [core.ProcessMember(10, 7, "S", 1024)]),
        complete, alive, code, None if status == "ok" else "fixture read error")


def cleanup_result(confirmed=True, survivors=None, errors=None):
    return {name: {"confirmed": confirmed,
        "status": "cleanup_confirmed" if confirmed else "cleanup_failed",
        "survivors": [] if survivors is None else survivors,
        "errors": [] if errors is None else errors, "identities": [[10, 7]],
        "requested_actions": ["verify"]} for name in ("workload", "helper")}


def test_scheduler_completion():
    def records(clock):
        yield tree(1, 0.0)
        yield tree(2, 0.05)
        yield tree(3, 0.10, members=(), alive=False, code=0)
    cleanups = []
    checkpoints = []
    with tempfile.TemporaryDirectory() as raw:
        checkpoint_path = Path(raw) / "checkpoint.json"
        def persist(report):
            checkpoints.append(report)
            core.durable_checkpoint(checkpoint_path, report)
        result, clock, requests = drive(records,
            cleanup=lambda _limit: cleanups.append(True) or cleanup_result(), checkpoint=persist)
        durable = json.loads(checkpoint_path.read_text())
        assert durable["status"] == "cleanup_checkpoint"
        assert durable["workload_cleanup"]["confirmed"] and durable["helper_cleanup"]["confirmed"]
    assert result["status"] == "completed" and result["cleanup_confirmed"]
    assert cleanups == [True]
    assert checkpoints and any(item.get("last_tree") for item in checkpoints)
    assert result["returncode"] == 0 and result["tree_samples"] == 3
    assert clock.waits[:2] == [0.05, 0.05]
    assert requests[0] == (1, 0.0)


def test_absolute_scheduler_phase():
    clock = Clock()
    calls = 0
    responses = []
    def request(seq, at):
        responses.append(host_reading(seq, at, at))
    def read_tree():
        nonlocal calls
        calls += 1
        if calls == 2:
            clock.value += 0.03
            return tree(2, 0.05)
        if calls == 3:
            return tree(3, 0.10, members=(), alive=False, code=0)
        return tree(1, 0.0)
    result = core.supervise(policy=core.Policy(1536, 2), tree_reader=read_tree,
        host_poll=lambda: responses.pop(0) if responses else None, host_request=request,
        clock=clock.now, wait=clock.wait, cleanup=lambda _: cleanup_result())
    assert result["status"] == "completed"
    assert clock.waits[:2] == [0.05, 0.020000000000000004]


def test_root_descendants():
    def records(_clock):
        yield tree(1, 0, alive=False, code=0,
                   members=[core.ProcessMember(11, 2, "S", 512)])
    result, _, _ = drive(records)
    assert result["status"] == "stopped_partial"
    assert "abnormal_root_exit_or_remaining_members" in result["primary_reasons"]
    assert result["cleanup_requested"] and result["cleanup_confirmed"]


def test_incomplete_membership_and_provider_freshness():
    calls = []
    def incomplete(_clock):
        yield tree(1, 0, complete=False)
        calls.append("must-not-read")
        yield tree(2, 0.05, members=(), alive=False, code=0)
    result, _, _ = drive(incomplete)
    assert result["cleanup_requested"] and not calls
    clock = Clock()
    def slow_tree():
        clock.value += 1.1
        return tree(1, 0)
    result = core.supervise(policy=core.Policy(1536, 5), tree_reader=slow_tree,
        host_poll=lambda: host_reading(1, 0, 0), host_request=lambda *_: None,
        clock=clock.now, wait=clock.wait,
        cleanup=lambda _: cleanup_result())
    assert "host_baseline_stale" in result["primary_reasons"]


def test_cleanup_error_is_reported():
    def records(_clock):
        yield tree(1, 0, members=[core.ProcessMember(10, 7, "S", 1537 * (1 << 20))])
    result, _, _ = drive(records, cleanup=lambda _limit: (_ for _ in ()).throw(OSError("kill denied")))
    assert result["status"] == "stopped_partial"
    assert result["cleanup_requested"] and not result["cleanup_confirmed"]
    assert result["cleanup_errors"][0]["type"] == "OSError"
    malformed = drive(records, cleanup=lambda _limit: {"workload": {"confirmed": 1}, "helper": {}})[0]
    assert malformed["cleanup_requested"] and not malformed["cleanup_confirmed"]
    assert json.loads(core.finite_json(malformed))["cleanup_errors"]
    sanitized = core._safe_report({"value": float("nan"), "secondary_errors": [
        {"message": "x" * 2000} for _ in range(20)]})
    assert sanitized["value"] is None and len(sanitized["secondary_errors"]) == 16
    assert len(sanitized["secondary_errors"][0]["message"]) == 1024
    finite = drive(records, cleanup=lambda _limit: {
        "workload": {"confirmed": False, "status": "cleanup_unknown", "survivors": [[10, math.nan]],
            "errors": [], "identities": [], "requested_actions": ["verify"]},
        "helper": cleanup_result()["helper"]})[0]
    assert json.loads(core.finite_json(finite))["cleanup_confirmed"] is False


def test_cleanup_deadline():
    for duration, expected in ((5.0, "completed"), (5.001, "partial_cleanup_failure")):
        clock = Clock()
        def finish(_limit, duration=duration):
            clock.value += duration
            return cleanup_result()
        result = core.supervise(policy=core.Policy(1536, 10),
            tree_reader=lambda: tree(1, 0, members=(), alive=False, code=0),
            host_poll=lambda: host_reading(1, 0, 0), host_request=lambda *_: None,
            clock=clock.now, wait=clock.wait, cleanup=finish)
        assert result["status"] == expected
        if duration > 5:
            assert result["primary_reasons"]


def test_owned_independent_finalizer():
    run = owned_run.OwnedRun("fixture", ((10, 7),), ((20, 8),))
    for target in ("OWNED_HELD", "READY", "RUNNING"):
        run.advance(target)
    calls = []
    ticks = iter((0.0, 0.0, 0.1, 0.1, 0.2))
    result = owned_run.finalize_owned(run,
        workload=lambda: (_ for _ in ()).throw(OSError("workload exit")),
        helper=lambda: calls.append("helper") or {**cleanup_result()["helper"],
                                                    "identities": [[20, 8]]},
        now=lambda: next(ticks))
    assert calls == ["helper"] and result["state"] == "FINALIZED"
    assert not result["cleanup_confirmed"] and result["workload"]["errors"]
    assert result["helper"]["identities"] == [[20, 8]]
    raises(core.MonitorError, lambda: run.advance("READY"))


def test_tree_brackets_and_host_identity():
    raises(core.MonitorError, lambda: core._validate_tree(tree(2, 9, start=9, end=9), 10, 1, 10))
    repeated_pid = tree(1, 0, members=[core.ProcessMember(10, 7, "S", 1),
                                       core.ProcessMember(10, 8, "S", 1)])
    raises(core.MonitorError, lambda: core._validate_tree(repeated_pid, 0, 0, 0))
    result = core.supervise(policy=core.Policy(1536, 1), tree_reader=lambda: tree(1, 0),
        host_poll=lambda: host_reading(1, 0, 0), host_request=lambda *_: None,
        clock=Clock().now, wait=lambda _: None, cleanup=lambda _: cleanup_result(), run_nonce="right")
    assert "monitor_input_failure" in result["primary_reasons"]
    responses = iter([host_reading(1, 0, 0), host_reading(2, 0, 0)])
    result = core.supervise(policy=core.Policy(1536, 2), tree_reader=lambda: tree(1, 0),
        host_poll=lambda: next(responses, None), host_request=lambda *_: None,
        clock=Clock().now, wait=lambda _: None, cleanup=lambda _: cleanup_result())
    assert "monitor_input_failure" in result["primary_reasons"]


def test_invalid_clock_and_bool_flags():
    def records(_clock):
        yield tree(1, 0, alive=1)
    result, _, _ = drive(records)
    assert "monitor_input_failure" in result["primary_reasons"]
    assert result["cleanup_requested"]
    raises(core.MonitorError, lambda: core.Policy(1, math.nan).validate())
    raises(core.MonitorError, lambda: core.Policy(True, 1).validate())
    raises(core.MonitorError, lambda: core.Policy(1536, 1, host_minimum_mib=0).validate())
    raises(core.MonitorError, lambda: core.Policy(1536, 1, host_interval_s=0.1).validate())


def test_future_acquisition_and_bad_status():
    def future(_clock):
        yield tree(1, 0, start=0.5, end=0.5)
    result, _, _ = drive(future)
    assert "monitor_input_failure" in result["primary_reasons"]
    def bad(_clock):
        yield tree(1, 0, status="error")
    assert "monitor_input_failure" in drive(bad)[0]["primary_reasons"]


def test_deadline_boundary():
    def records(clock):
        sequence = 0
        while True:
            sequence += 1
            yield tree(sequence, clock.value)
    result, clock, _ = drive(records, policy=core.Policy(1536, 0.10))
    assert result["status"] == "stopped_partial"
    assert "wall_time_limit" in result["primary_reasons"]
    assert result["cleanup_requested"] and clock.value >= 0.10


def test_rss_boundary_and_host_stop():
    def at_cap(_clock):
        yield tree(1, 0, members=[core.ProcessMember(10, 7, "S", 1536 * (1 << 20))])
        yield tree(2, 0.05, members=(), alive=False, code=0)
    assert drive(at_cap)[0]["status"] == "completed"
    clock = Clock()
    responses = [host_reading(1, 0, 0, available=1023 << 20)]
    result = core.supervise(policy=core.Policy(1536, 1),
        tree_reader=lambda: (_ for _ in ()).throw(AssertionError("must stop before tree")),
        host_poll=lambda: responses.pop(0) if responses else None,
        host_request=lambda *_: None, clock=clock.now, wait=clock.wait,
        cleanup=lambda _: cleanup_result())
    assert "host_pressure_limit" in result["primary_reasons"]


def test_partial_report_and_finite_json():
    def records(_clock):
        yield tree(1, 0, status="bad")
    def broken_sink(_report):
        raise OSError("disk full")
    result, _, _ = drive(records, sink=broken_sink)
    assert "monitor_input_failure" in result["primary_reasons"]
    assert result["status"] in ("stopped_partial", "partial_report_failure")
    assert json.loads(core.finite_json(result))["secondary_errors"]
    raises(core.MonitorError, lambda: core.finite_json({"x": float("nan")}))
    assert {"setup", "run", "cleanup", "report", "total"} <= set(result["elapsed_seconds"])
    assert "peak_process_rss_bytes" in result and "maximum_decision_delay_s" in result


def test_host_timeout_and_clock_regression():
    core._require_previous_host_fresh(1.0, 0.0)
    raises(core.MonitorError, lambda: core._require_previous_host_fresh(1.000001, 0.0))
    clock = Clock()
    tree_calls = []
    result = core.supervise(policy=core.Policy(1536, 2),
        tree_reader=lambda: tree_calls.append(True), host_poll=lambda: None,
        host_request=lambda *_: None, clock=clock.now, wait=clock.wait,
        cleanup=lambda _: cleanup_result(False))
    assert "host_response_timeout" in result["primary_reasons"]
    assert not tree_calls and result["cleanup_requested"]

    values = iter([0.0, 1.0, 0.5, 0.5, 0.5])
    regressing = core.supervise(policy=core.Policy(1536, 10),
        tree_reader=lambda: tree(1, 0), host_poll=lambda: None,
        host_request=lambda *_: None, clock=lambda: next(values), wait=lambda _: None,
        cleanup=lambda _: cleanup_result())
    assert "monitor_input_failure" in regressing["primary_reasons"]
    assert regressing["cleanup_requested"]


def test_proc_stat_parsing_and_membership():
    parsed = linux_adapter.parse_proc_stat(21, proc_stat(21, comm="worker ) odd name", start=314))
    assert parsed.comm == "worker ) odd name" and parsed.start_ticks == 314
    assert parsed.ppid == 1 and parsed.session == 1 and parsed.rss_pages == 2
    members = linux_adapter.make_membership_reading(
        cgroup_pids={21, 22}, proc_text={21: proc_stat(21, start=314, rss=0, state="S"),
                                        22: proc_stat(22, start=315, rss=3, state="Z")},
        root=(21, 314), page_size=4096)
    assert [m.rss_bytes for m in members] == [0, 12288]
    assert members[1].state == "Z"
    linux_adapter.verify_launch_root(root=(21, 314), members=members)
    assert linux_adapter.make_membership_reading(cgroup_pids={22},
        proc_text={22: proc_stat(22, start=315)}, root=(21, 314), page_size=4096)
    raises(core.MonitorError, lambda: linux_adapter.verify_launch_root(
        root=(21, 314), members=members[1:]))
    raises(core.MonitorError, lambda: linux_adapter.parse_proc_stat(21, "21 (bad) S"))
    raises(core.MonitorError, lambda: linux_adapter.make_membership_reading(
        cgroup_pids={21, 22}, proc_text={21: proc_stat(21)}, root=(21, 100), page_size=4096))
    raises(core.MonitorError, lambda: linux_adapter.make_membership_reading(
        cgroup_pids={21}, proc_text={21: proc_stat(22)}, root=(21, 100), page_size=4096))
    raises(core.MonitorError, lambda: linux_adapter.make_membership_reading(
        cgroup_pids={21}, proc_text={21: proc_stat(21, rss=-1)}, root=(21, 100), page_size=4096))


def test_cleanup_classification():
    ok = linux_adapter.classify_cleanup(kill_error=None, child_reaped=True,
        cgroup_populated=False, survivors=[])
    failed = linux_adapter.classify_cleanup(kill_error="denied", child_reaped=False,
        cgroup_populated=None, survivors=[(1, 10)])
    unknown = linux_adapter.classify_cleanup(kill_error=None, child_reaped=True,
        cgroup_populated=None, survivors=None)
    assert ok["confirmed"] and failed["status"] == "cleanup_failed"
    assert unknown["status"] == "cleanup_unknown"


def test_attempt_accounting_refuses_open_unknown_failed_and_exhausted():
    source_map = {"validate.py": "a" * 64}
    good = {"attempt": 1, "state": "COMPLETED", "status": "passed",
        "outer_elapsed_seconds": 2.0, "child_lifetime_peak_rss_bytes": 1024,
        "timed_out": False, "resource_stop": False, "validator_returncode": 0,
        "source_sha256_before": source_map, "source_sha256_after": source_map,
        "source_archive_sha256": source_map,
        "timing_intervals_seconds": {"setup_and_snapshot": 0.2,
            "validator_child": 0.8, "finalization": 0.2},
        "uncovered_measurement_scope": ["interpreter startup/imports"]}
    assert prior_elapsed([good]) == 2.0
    for bad in ({**good, "state": "STARTED"},
                {key: value for key, value in good.items() if key != "outer_elapsed_seconds"},
                {**good, "status": "failed"}, {**good, "timed_out": True},
                {**good, "child_lifetime_peak_rss_bytes": 256 * 1024 * 1024 + 1}):
        raises(ValueError, lambda bad=bad: prior_elapsed([bad]))
    raises(ValueError, lambda: prior_elapsed([good], limit_seconds=1.0))
    failed = {**good, "status": "failed", "validator_returncode": 1}
    raises(ValueError, lambda: prior_elapsed([failed]))
    raises(ValueError, lambda: prior_elapsed([{**good, "source_archive_sha256": {}}]))
    raises(ValueError, lambda: prior_elapsed([{**good, "timing_intervals_seconds": {}}]))


def reply(seq, nonce="run-1", available=8 << 30, total=16 << 30, status="ok"):
    return (json.dumps({"schema": 1, "sequence": seq, "nonce": nonce,
        "status": status, "available_bytes": available if status == "ok" else None,
        "total_bytes": total if status == "ok" else None,
        "provider_pid": 4312, "provider_created": 721004,
        "error": None if status == "ok" else "API failure"}, separators=(",", ":")) + "\n").encode()


def test_host_protocol_success_and_sequence():
    protocol = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    request = protocol.request(1, 0)
    assert json.loads(request)["operation"] == "memory"
    reading = protocol.reply(reply(1), 0.1)
    assert reading.available_bytes == 8 << 30 and reading.start == 0 and reading.end == 0.1
    raises(core.MonitorError, lambda: protocol.reply(reply(1), 0.2))
    protocol.request(2, 0.5)
    assert protocol.reply(reply(2), 0.6).sequence == 2


def test_host_protocol_fail_closed_cases():
    cases = [
        lambda p: p.reply(reply(1, nonce="wrong"), 0.1),
        lambda p: p.reply(reply(2), 0.1),
        lambda p: p.reply(b"{}", 0.1),
        lambda p: p.reply(b"x" * 4097 + b"\n", 0.1),
        lambda p: p.reply(reply(1, available=True), 0.1),
        lambda p: p.reply(reply(1, available=(17 << 30), total=(16 << 30)), 0.1),
        lambda p: p.reply(b'{"schema":true,"sequence":1,"nonce":"run-1"}\n', 0.1),
        lambda p: p.reply(reply(1) + reply(1), 0.1),
        lambda p: p.reply(b'{"schema":1,"sequence":1,"nonce":"run-1","status":"ok","available_bytes":NaN,"total_bytes":2,"error":null}\n', 0.1),
        lambda p: p.reply(reply(1).replace(b'"provider_pid":4312', b'"provider_pid":true'), 0.1),
    ]
    for operation in cases:
        p = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
        p.request(1, 0)
        raises(core.MonitorError, lambda operation=operation, p=p: operation(p))
    p = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    p.request(1, 0)
    raises(core.MonitorError, lambda: p.request(2, 0.1))
    assert p.expired(0.5)
    failed = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    failed.request(1, 0)
    assert failed.reply(reply(1, status="error"), 0.1).status == "error"
    at_deadline = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    at_deadline.request(1, 0)
    raises(core.MonitorError, lambda: at_deadline.reply(reply(1), 0.5))
    duplicate = b'{"schema":1,"sequence":1,"nonce":"run-1","status":"ok","available_bytes":1,"total_bytes":2,"error":null,"status":"ok"}\n'
    p = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    p.request(1, 0)
    raises(core.MonitorError, lambda: p.reply(duplicate, 0.1))
    contradiction = reply(1).replace(b'"error":null', b'"error":"api failure"')
    p = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    p.request(1, 0)
    raises(core.MonitorError, lambda: p.reply(contradiction, 0.1))
    p = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    p.request(1, 0)
    p.reply(reply(1), 0.1)
    p.request(2, 0.5)
    changed = reply(2).replace(b'"provider_pid":4312', b'"provider_pid":4313')
    raises(core.MonitorError, lambda: p.reply(changed, 0.6))
    # Parser/framing failures latch terminal state, including incremental input.
    p = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    p.request(1, 0)
    raises(core.MonitorError, lambda: p.feed(b"{bad}\n", 0.1))
    raises(core.MonitorError, lambda: p.feed(reply(1), 0.2))
    p = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    p.request(1, 0)
    frame = reply(1)
    assert p.feed(frame[:10], 0.1) is None
    assert p.feed(frame[10:], 0.1).sequence == 1
    p.request(2, 0.5)
    raises(core.MonitorError, lambda: p.feed(b"", 1.0, eof=True))


def test_disabled_r070_and_completion_binding():
    guard = load_guard()
    with tempfile.TemporaryDirectory() as raw:
        base = Path(raw)
        called = []
        disabled = guard.guarded_launch(base / "disabled")
        assert not disabled["child_launched"] and not (base / "never").exists()
        refused = guard.guarded_launch(base / "enabled", enabled=True,
                                       child_launcher=lambda: called.append(True))
        assert not refused["child_launched"] and not called
        sentinel = guard.run_test_sentinel(lambda: "ok")
        assert sentinel["status"] == "sentinel_passed" and not sentinel["attempt_consumed"]
        assert not (base / "attempt.json").exists()
        source_root = base / "source"
        source_root.mkdir()
        (source_root / "input.txt").write_text("fixture source\n")
        (source_root / "evidence.json").write_text("{}\n")
        manifest_path = source_root / "source_manifest.json"
        manifest = {"schema": 1,
            "files": {"input.txt": guard.sha(source_root / "input.txt")},
            "evidence_files": {"evidence.json": guard.sha(source_root / "evidence.json")}}
        guard.write_json(manifest_path, manifest)
        manifest_hash = guard.sha(manifest_path)
        good_watch = {"status": "completed", "stop_reason": None, "returncode": 0,
                      "membership_complete": True, "cleanup_confirmed": True,
                      "schema": 3, "primary_reasons": [], "secondary_errors": [],
                      "workload_cleanup": {"confirmed": True, "status": "cleanup_confirmed",
                          "survivors": [], "errors": [],
                          "identities": [], "requested_actions": []},
                      "helper_cleanup": {"confirmed": True, "status": "cleanup_confirmed",
                          "survivors": [], "errors": [],
                          "identities": [], "requested_actions": []},
                      "source_manifest_sha256": manifest_hash}
        good_watch.update(cleanup_errors=[], survivors=[])
        good_child = {"schema": 2, "status": "complete", "stage": "fixture",
                      "evidence_complete": True, "primary_reasons": [], "errors": [],
                      "counts": {key: 0 for key in guard.COUNT_KEYS},
                      "workload_cleanup": {"confirmed": True, "status": "cleanup_confirmed",
                          "survivors": [], "errors": [],
                          "identities": [], "requested_actions": []},
                      "helper_cleanup": {"confirmed": True, "status": "cleanup_confirmed",
                          "survivors": [], "errors": [],
                          "identities": [], "requested_actions": []},
                      "scientific_checks_passed": True,
                      "source_manifest_sha256": manifest_hash}
        for owner_record in (good_watch, good_child):
            owner_record["workload_cleanup"]["identities"] = [[10, 7]]
            owner_record["workload_cleanup"]["requested_actions"] = ["verify"]
            owner_record["helper_cleanup"]["identities"] = [[20, 8]]
            owner_record["helper_cleanup"]["requested_actions"] = ["verify"]
        good_watch["child_report_sha256"] = hashlib.sha256(
            json.dumps(good_child, sort_keys=True, separators=(",", ":"),
                       allow_nan=False).encode()).hexdigest()
        accepted = guard.finalize_child(guard.initial_report(), good_watch, good_child,
            source_root=source_root, source_manifest_path=manifest_path)
        assert accepted["status"] == "complete"
        for change in ({"returncode": 9}, {"returncode": True}, {"cleanup_confirmed": False},
                       {"status": "stopped_partial"}, {"membership_complete": False}):
            rejected = guard.finalize_child(guard.initial_report(), {**good_watch, **change}, good_child,
                source_root=source_root, source_manifest_path=manifest_path)
            assert rejected["status"] == "partial_failed"
        rejected = guard.finalize_child(guard.initial_report(), good_watch,
            {**good_child, "evidence_complete": False},
            source_root=source_root, source_manifest_path=manifest_path)
        assert rejected["status"] == "partial_failed"
        for mutation in ({"primary_reasons": ["failure"]},
                         {"cleanup_errors": ["contradictory monitor error"]},
                         {"survivors": [[99, 1]]},
                         {"schema": 3.0},
                         {"helper_cleanup": {"confirmed": False, "status": "cleanup_failed",
                             "survivors": [[1, 2]],
                             "errors": [], "identities": [[1, 2]], "requested_actions": ["kill"]}},
                         {"counts": {key: None for key in guard.COUNT_KEYS}}):
            rejected = guard.finalize_child(guard.initial_report(), good_watch,
                {**good_child, **mutation}, source_root=source_root,
                source_manifest_path=manifest_path)
            assert rejected["status"] == "partial_failed"
        contradictory = {**good_child, "physical_meshes": 7}
        rebound_watch = {**good_watch, "child_report_sha256": hashlib.sha256(
            json.dumps(contradictory, sort_keys=True, separators=(",", ":"),
                       allow_nan=False).encode()).hexdigest()}
        assert guard.finalize_child(guard.initial_report(), rebound_watch, contradictory,
            source_root=source_root, source_manifest_path=manifest_path)["status"] == "partial_failed"
        rejected = guard.finalize_child(guard.initial_report(),
            {**good_watch, "child_report_sha256": "0" * 64}, good_child,
            source_root=source_root, source_manifest_path=manifest_path)
        assert rejected["status"] == "partial_failed"
        rejected = guard.finalize_child(guard.initial_report(), good_watch, good_child)
        assert rejected["status"] == "partial_failed"
        copy = ROOT / "r070_copy"
        sys.path.insert(0, str(copy))
        try:
            contract_spec = importlib.util.spec_from_file_location(
                "r076_run_contract", copy / "run_contract.py")
            contract = importlib.util.module_from_spec(contract_spec)
            assert contract_spec and contract_spec.loader
            contract_spec.loader.exec_module(contract)
            api_result = contract.physical(base / "api-physical")
            assert api_result["status"] == "prerequisite_refused"
            assert api_result["child_launched"] is False
            old_argv = sys.argv
            output = io.StringIO()
            try:
                sys.argv = ["run_contract.py", "physical", "--output", str(base / "cli-physical")]
                with contextlib.redirect_stdout(output):
                    contract.main()
            finally:
                sys.argv = old_argv
            cli_result = json.loads(output.getvalue())
            assert cli_result["status"] == "prerequisite_refused"
            assert cli_result["child_launched"] is False
        finally:
            sys.path.remove(str(copy))
        physical_source = (copy / "physical.py").read_text()
        assert "physical child execution disabled pending reviewed launch contract" in physical_source
        assert "legacy physical launch path disabled" in physical_source


def test_continuity_and_source_bindings():
    repo = Path(__file__).resolve().parents[5]
    docs = [repo / "SESSION_HANDOFF.md", repo / "REQUEST_LOG.md", repo / "WORK_SESSIONS.md"]
    link_count = 0
    for document in docs:
        content = document.read_text()
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", content):
            target = target.split()[0].strip("<>")
            if "://" in target or target.startswith("mailto:"):
                continue
            path_part = target.split("#", 1)[0]
            local = (document.parent / path_part).resolve() if path_part else document
            assert local.exists(), f"broken local link in {document}: {target}"
            link_count += 1
    handoff = (repo / "SESSION_HANDOFF.md").read_text()
    request_log = (repo / "REQUEST_LOG.md").read_text()
    sessions = (repo / "WORK_SESSIONS.md").read_text()
    assert handoff.startswith("# Current session handoff")
    assert handoff.count("## Next task") == 1
    assert request_log.count("## R084 —") == 1
    assert sessions.count("## R084 —") == 1
    assert sessions.split("## R084 —", 1)[1].count("STARTED | 2026-09-21 15:39:26 UTC") == 1
    evidence_root = repo / "docs/realizability/evidence/r084"
    for python_source in evidence_root.joinpath("source").rglob("*.py"):
        ast.parse(python_source.read_text(), filename=str(python_source))
    ast.parse((evidence_root / "run_r084.py").read_text(), filename="run_r084.py")
    manifest = json.loads((evidence_root / "source_manifest.json").read_text())
    for relative, expected in manifest["source_sha256"].items():
        actual = hashlib.sha256((evidence_root / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
    active_attempt = json.loads((evidence_root / "attempt_01.json").read_text())
    snapshot_root = evidence_root / active_attempt["source_archive"]
    assert active_attempt["source_archive_sha256"] == active_attempt["source_sha256_before"]
    for relative, expected in active_attempt["source_archive_sha256"].items():
        assert hashlib.sha256((snapshot_root / relative).read_bytes()).hexdigest() == expected
    json_count = 0
    for json_path in evidence_root.rglob("*.json"):
        parsed = json.loads(json_path.read_text())
        json.dumps(parsed, allow_nan=False)
        json_count += 1
    old_manifest = json.loads((repo / "docs/realizability/evidence/r082/source_manifest.json").read_text())
    for relative, expected in old_manifest["source_sha256"].items():
        actual = hashlib.sha256((repo / "docs/realizability/evidence/r082" / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
    validation = {"schema": 3, "status": "passed", "checked_documents": [
        str(path.relative_to(repo)) for path in docs], "local_links": link_count,
        "source_hashes": len(manifest["source_sha256"]), "continuity": "R082 archive preserved; R084 request/session linked",
        "finite_json_files": json_count}
    evidence = evidence_root / "documentation_validation.json"
    evidence.write_text(json.dumps(validation, indent=2, sort_keys=True, allow_nan=False) + "\n")


def main():
    checks_to_run = [
        ("independent launch gates/exact headroom/staleness", test_launch_gate),
        ("explicit 50ms wait scheduling and clean root completion", test_scheduler_completion),
        ("absolute sampling schedule retains its original phase", test_absolute_scheduler_phase),
        ("root exit with remaining descendants refuses completion", test_root_descendants),
        ("incomplete membership and slow provider freshness fail closed", test_incomplete_membership_and_provider_freshness),
        ("cleanup exception preserves primary reason and partial report", test_cleanup_error_is_reported),
        ("cleanup verification enforces the exact five-second boundary", test_cleanup_deadline),
        ("owned run attempts workload and helper cleanup independently", test_owned_independent_finalizer),
        ("tree brackets and host identity remain ordered", test_tree_brackets_and_host_identity),
        ("NaN/Boolean/invalid flags and finite configuration refused", test_invalid_clock_and_bool_flags),
        ("future/stale provider status failures are fail closed", test_future_acquisition_and_bad_status),
        ("absolute deadline stops at equality", test_deadline_boundary),
        ("RSS equality passes and host pressure below threshold stops", test_rss_boundary_and_host_stop),
        ("partial reporting failure and finite JSON", test_partial_report_and_finite_json),
        ("host baseline timeout and monotonic clock regression clean up", test_host_timeout_and_clock_regression),
        ("Linux stat parsing, identity, membership, zero RSS and zombie", test_proc_stat_parsing_and_membership),
        ("Linux cleanup confirmed/failed/unknown classification", test_cleanup_classification),
        ("exclusive cumulative ledger refuses open/unknown/failed/resource-stopped history", test_attempt_accounting_refuses_open_unknown_failed_and_exhausted),
        ("host protocol sequence, nonce and bounded round trip", test_host_protocol_success_and_sequence),
        ("host protocol malformed/duplicate/oversized/API failures", test_host_protocol_fail_closed_cases),
        ("R070 default deny, separate sentinel and strict completion binding", test_disabled_r070_and_completion_binding),
        ("handoff/log/link/source binding and resource-budget integrity", test_continuity_and_source_bindings),
    ]
    discovered = {name: value for name, value in globals().items()
                  if name.startswith("test_") and callable(value)}
    registered = [function.__name__ for _name, function in checks_to_run]
    assert len(registered) == len(set(registered)), "duplicate fixture registration"
    assert set(registered) == set(discovered), "fixture registry is incomplete or contains unknown cases"
    for name, function in checks_to_run:
        check(name, function)
    attempt_number = int(os.environ.get("R084_ATTEMPT", "1"))
    report = {"schema": 1, "attempt": attempt_number, "status": "passed",
              "checks_passed": len(checks), "checks": checks,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in sorted(ROOT.glob("*.py")) if p.name != "validate.py"},
              "scope": "deterministic fixtures only; no live OS operations or workloads"}
    output = Path(__file__).resolve().parents[1] / f"fixture_results_attempt_{attempt_number:02d}.json"
    output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": "passed", "checks": len(checks), "output": str(output)}))


if __name__ == "__main__":
    main()
