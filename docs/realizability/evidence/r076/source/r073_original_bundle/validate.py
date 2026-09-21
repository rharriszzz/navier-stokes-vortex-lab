"""Synthetic-only validation for portable_monitor.py; never launches processes."""
import importlib.util
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("portable_monitor", HERE / "portable_monitor.py")
monitor = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = monitor
spec.loader.exec_module(monitor)


class FakeClock:
    def __init__(self):
        self.value = 0.0

    def now(self):
        return self.value


class FakeInputs:
    def __init__(self, clock, rss=100.0, count=2, alive=True,
                 host=4096.0, tree_fault=None, host_fault=None, step=0.05,
                 stop_after=45):
        self.clock = clock
        self.rss, self.count, self.alive, self.host = rss, count, alive, host
        self.tree_fault, self.host_fault = tree_fault, host_fault
        self.step, self.stop_after = step, stop_after
        self.tree_calls = 0
        self.host_calls = 0

    def tree(self):
        self.tree_calls += 1
        if self.tree_fault == "missing":
            return None
        if self.tree_fault == "stale":
            return monitor.TreeReading(self.clock.value - 1.0, self.rss, self.count, self.alive)
        if self.tree_fault == "nonfinite":
            return monitor.TreeReading(self.clock.value, math.inf, self.count, self.alive)
        value = self.rss
        if self.tree_fault == "cross_cap" and self.tree_calls == 2:
            value = 513.0
        if self.tree_fault == "gap" and self.tree_calls == 2:
            self.clock.value += 0.08
        reading = monitor.TreeReading(self.clock.value, value, self.count, self.alive)
        if self.tree_fault != "gap":
            self.clock.value += self.step
        else:
            self.clock.value += self.step
        if self.tree_calls >= self.stop_after:
            self.alive = False
        return reading

    def host_reading(self):
        self.host_calls += 1
        if self.host_fault == "missing":
            return None
        if self.host_fault == "stale":
            return monitor.HostReading(self.clock.value - 2.0, self.host)
        if self.host_fault == "nonfinite":
            return monitor.HostReading(self.clock.value, math.nan)
        availability = 900.0 if self.host_fault == "pressure" and self.clock.value >= 1.0 else self.host
        return monitor.HostReading(self.clock.value, availability)


def run_case(deadline=5.0, **kwargs):
    clock = FakeClock()
    inputs = FakeInputs(clock, **kwargs)
    terminated = []
    launch = monitor.HostReading(0.0, 4096.0)
    report = monitor.run_monitor(
        tree_reader=inputs.tree, host_reader=inputs.host_reading,
        now=clock.now, deadline=deadline, tree_cap_mib=512.0,
        launch_host_reading=launch, terminate=lambda: terminated.append(True))
    report["fake_termination_count"] = len(terminated)
    report["fake_tree_reader_calls"] = inputs.tree_calls
    report["fake_host_reader_calls"] = inputs.host_calls
    return report


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    started = time.monotonic()
    checks = {}
    ok = run_case(stop_after=45)
    checks["completion_and_one_second_host_sampling"] = (
        ok["status"] == "completed" and ok["host_samples"] == 3
        and ok["maximum_tree_sample_gap_seconds"] <= 0.05 + 1e-9
        and ok["maximum_host_sample_gap_seconds"] <= 1.0 + 1e-9
        and ok["fake_termination_count"] == 0)

    crossed = run_case(tree_fault="cross_cap")
    checks["tree_cap_and_termination"] = (
        crossed["stop_reason"] == "tree_rss_limit" and crossed["fake_termination_count"] == 1)
    timed = run_case(deadline=0.5, stop_after=45)
    checks["wall_cap_and_termination"] = (
        timed["stop_reason"] == "wall_time_limit" and timed["fake_termination_count"] == 1)
    pressured = run_case(host_fault="pressure", stop_after=40)
    checks["host_pressure_and_termination"] = (
        pressured["stop_reason"] == "host_pressure_limit" and pressured["fake_termination_count"] == 1)
    gap = run_case(tree_fault="gap", stop_after=3)
    checks["sample_gap_reported"] = gap["maximum_tree_sample_gap_seconds"] >= 0.08

    for name in ("missing", "stale", "nonfinite"):
        tree_failure = run_case(tree_fault=name)
        checks[f"tree_{name}_partial_stop"] = (
            tree_failure["status"] == "partial" and tree_failure["termination_requested"])
        host_failure = run_case(host_fault=name)
        checks[f"host_{name}_partial_stop"] = (
            host_failure["status"] == "partial" and host_failure["termination_requested"])

    checks["launch_missing_refused"] = _launch_refused(None)
    checks["launch_stale_refused"] = _launch_refused(monitor.HostReading(-31.0, 4096.0))
    checks["launch_nonfinite_refused"] = _launch_refused(monitor.HostReading(0.0, math.inf))
    checks["launch_headroom_refused"] = _launch_refused(monitor.HostReading(0.0, 1535.0))

    # A reader exception after a live-tree checkpoint must preserve partial data
    # and request termination through the injected callback.
    clock = FakeClock()
    calls = [0]
    terminated = []
    def interrupting_tree():
        calls[0] += 1
        if calls[0] == 1:
            return monitor.TreeReading(0.0, 12.0, 1, True)
        raise KeyboardInterrupt("synthetic interruption")
    partial = monitor.run_monitor(
        tree_reader=interrupting_tree,
        host_reader=lambda: monitor.HostReading(clock.value, 4096.0),
        now=clock.now, deadline=5.0, tree_cap_mib=512.0,
        launch_host_reading=monitor.HostReading(0.0, 4096.0),
        terminate=lambda: terminated.append(True))
    checks["interrupted_partial_report_and_stop"] = (
        partial["status"] == "partial" and partial["tree_samples"] == 1
        and partial["termination_requested"] and len(terminated) == 1)

    for name, passed in checks.items():
        assert_true(passed, f"failed: {name}")
    elapsed = time.monotonic() - started
    if elapsed > 120.0:
        raise RuntimeError("120-second cumulative validation budget exceeded")
    peak_rss_mib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    if peak_rss_mib > 256.0:
        raise RuntimeError("256 MiB validation address-space/RSS cap exceeded")
    result = {
        "scope": "synthetic monitor contract only; no subprocess or physical child",
        "python": sys.version.split()[0], "checks_passed": sum(checks.values()),
        "checks_total": len(checks), "checks": checks,
        "representative_reports": {"normal": ok, "tree_cap": crossed, "wall_cap": timed,
                                   "host_pressure": pressured, "sample_gap": gap,
                                   "interrupted": partial},
        "elapsed_seconds": elapsed, "max_rss_mib": peak_rss_mib,
        "budgets": {"cumulative_seconds": 120.0, "rss_mib": 256.0},
        "source_sha256": {
            "portable_monitor.py": hashlib.sha256((HERE / "portable_monitor.py").read_bytes()).hexdigest(),
            "validate.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "archived_r033_toy_runner.py": hashlib.sha256(
                (HERE.parents[1] / "evidence" / "r033" / "source" / "toy_runner.py").read_bytes()).hexdigest(),
        },
    }
    (HERE / "result.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    ledger_path = HERE / "attempt_ledger.json"
    ledger = json.loads(ledger_path.read_text())
    ledger["attempts"].append({"attempt": len(ledger["attempts"]) + 1,
                               "outcome": "passed", "elapsed_seconds": elapsed,
                               "max_rss_mib": peak_rss_mib})
    ledger["cumulative_elapsed_seconds"] = sum(
        a["elapsed_seconds"] for a in ledger["attempts"] if a["elapsed_seconds"] is not None)
    rss_samples = [a["max_rss_mib"] for a in ledger["attempts"] if a["max_rss_mib"] is not None]
    ledger["maximum_sampled_rss_mib"] = max(rss_samples) if rss_samples else None
    if ledger["cumulative_elapsed_seconds"] > ledger["budget_seconds"]:
        raise RuntimeError("120-second cumulative validation budget exceeded")
    ledger_path.write_text(json.dumps(ledger, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2))


def _launch_refused(reading):
    try:
        monitor.validate_launch_reading(reading, 0.0, 512.0)
    except monitor.MonitorInputError:
        return True
    return False


if __name__ == "__main__":
    main()
