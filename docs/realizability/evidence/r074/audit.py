"""Reproduce review findings with fakes; never call a platform adapter or FEM.

Run from any directory with Python 3.12 and --output pointing to a NEW file.
The archived modules are compiled in memory, without bytecode or file edits.
This is counterexample evidence, not a passing monitor implementation suite.
"""
import resource
import time

STARTED = time.monotonic()
resource.setrlimit(resource.RLIMIT_AS, (256 * 1024**2, 256 * 1024**2))
resource.setrlimit(resource.RLIMIT_CPU, (10, 10))

import argparse
import ast
import hashlib
import json
from pathlib import Path
import signal
import sys
import types

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = ROOT / "docs/realizability/evidence"


def load_archive(name, path):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_text(), str(path), "exec"), module.__dict__)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    # Refuse accidental replacement of either old or new evidence.
    with args.output.open("x") as stream:
        stream.write('{"status": "started"}\n')
    result = {"scope": "source review and fake counterexamples only",
              "python": sys.version, "executable": sys.executable,
              "status": "partial", "findings": {}, "checks": {}}
    def timeout(_signum, _frame):
        raise TimeoutError("review audit exceeded 120 seconds")
    signal.signal(signal.SIGALRM, timeout)
    signal.setitimer(signal.ITIMER_REAL, max(0.001, 120 - (time.monotonic() - STARTED)))
    try:
        monitor = load_archive("r074_archived_monitor", EVIDENCE / "r073/portable_monitor.py")
        guard = load_archive("r074_archived_guard", EVIDENCE / "r070/source/launch_guard.py")

        def run(*, now=lambda: 0.0, tree=None, host=None, terminate=None, **overrides):
            calls = []
            options = dict(tree_reader=tree or (lambda: monitor.TreeReading(0., 1., 1, False)),
                           host_reader=host or (lambda: monitor.HostReading(0., 4096.)),
                           now=now, deadline=5., tree_cap_mib=512.,
                           launch_host_reading=monitor.HostReading(0., 4096.),
                           terminate=terminate or (lambda: calls.append("requested")))
            options.update(overrides)
            try:
                report = monitor.run_monitor(**options)
            except BaseException as exc:
                report = {"raised": type(exc).__name__, "message": str(exc)}
            return {"report": report, "termination_calls": calls}

        findings = result["findings"]
        findings["root_exit_with_remaining_processes"] = run(
            tree=lambda: monitor.TreeReading(0., 10., 2, False))

        termination_calls = []
        def broken_termination():
            termination_calls.append("requested")
            raise OSError("synthetic signal failure")
        failed_stop = run(tree=lambda: monitor.TreeReading(0., 513., 1, True),
                          terminate=broken_termination)
        failed_stop["termination_calls"] = termination_calls
        findings["termination_error_loses_report_and_retries"] = failed_stop
        findings["invalid_launch_reading_outside_cleanup"] = run(launch_host_reading=None)
        findings["nan_deadline_accepted"] = run(deadline=float("nan"))
        findings["boolean_count_accepted"] = run(
            tree=lambda: monitor.TreeReading(0., 1., True, False))
        findings["future_tree_sample_accepted"] = run(
            tree=lambda: monitor.TreeReading(0.5, 1., 1, False))

        launch = monitor.validate_launch_reading(monitor.HostReading(0., 4096.), 5., 512.)
        aged = run(now=lambda: 5., deadline=10.,
                   host=lambda: monitor.HostReading(5., 4096.),
                   tree=lambda: monitor.TreeReading(5., 1., 1, False))
        aged["standalone_launch_acceptance"] = launch
        findings["valid_five_second_launch_sample_runtime_refusal"] = aged

        tree_calls = []
        def unpaced_tree():
            tree_calls.append(0.)
            return monitor.TreeReading(0., 1., 1, len(tree_calls) < 3)
        unpaced = run(tree=unpaced_tree)
        unpaced["tree_read_times"] = tree_calls
        findings["three_samples_without_clock_advance"] = unpaced

        finalized = guard.finalize_child(guard.initial_report(),
            {"stop_reason": None, "returncode": 9}, {"status": "complete", "stage": "done"})
        findings["nonzero_child_returncode_can_complete"] = {
            "status": finalized["status"], "watch": finalized["watch"]}

        checks = result["checks"]
        checks["root_exit_counterexample"] = findings["root_exit_with_remaining_processes"]["report"]["status"] == "completed"
        checks["termination_counterexample"] = failed_stop["report"].get("raised") == "OSError" and len(termination_calls) == 2
        checks["prelaunch_cleanup_boundary"] = findings["invalid_launch_reading_outside_cleanup"]["report"].get("raised") == "MonitorInputError"
        checks["nan_deadline_counterexample"] = findings["nan_deadline_accepted"]["report"]["status"] == "completed"
        checks["boolean_count_counterexample"] = findings["boolean_count_accepted"]["report"]["status"] == "completed"
        checks["future_sample_counterexample"] = findings["future_tree_sample_accepted"]["report"]["status"] == "completed"
        checks["aged_launch_counterexample"] = aged["report"]["stop_reason"] == "monitor_input_failure"
        checks["unpaced_loop_counterexample"] = unpaced["report"]["tree_samples"] == 3 and tree_calls == [0., 0., 0.]
        checks["nonzero_exit_counterexample"] = finalized["status"] == "complete"

        pinned = json.loads((EVIDENCE / "r070/source/preflight.json").read_text())["source_sha256"]
        checks["production_pins_unchanged"] = all(
            hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest
            for p, digest in pinned.items())
        result["production_pin_count"] = len(pinned)
        manifest = json.loads((EVIDENCE / "r073/source_manifest.json").read_text())
        checks["r073_manifest_matches"] = all(hashlib.sha256(
            (EVIDENCE / ("r033/source/toy_runner.py" if p == "archived_r033_toy_runner.py" else "r073/" + p)).read_bytes()
        ).hexdigest() == digest for p, digest in manifest["files"].items())
        tree = ast.parse((EVIDENCE / "r070/source/run_contract.py").read_text())
        physical = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "physical")
        calls = [n for n in ast.walk(physical) if isinstance(n, ast.Call)]
        checks["r070_physical_entry_still_disabled"] = any(
            isinstance(k.value, ast.Constant) and k.arg == "enabled" and k.value.value is False
            for n in calls for k in n.keywords)
        result["source_sha256"] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in (
            "docs/realizability/evidence/r033/source/toy_runner.py",
            "docs/realizability/evidence/r070/source/launch_guard.py",
            "docs/realizability/evidence/r070/source/run_contract.py",
            "docs/realizability/evidence/r073/portable_monitor.py",
            "docs/realizability/evidence/r073/validate.py",
            "docs/realizability/evidence/r073/attempt_ledger.json",
            "docs/realizability/evidence/r074/audit.py")}
        if not all(checks.values()):
            raise AssertionError([k for k, v in checks.items() if not v])
        result["status"] = "review_findings_reproduced"
    except BaseException as exc:
        result["error"] = {"type": type(exc).__name__, "message": str(exc)}
        raise
    finally:
        result["audit_elapsed_seconds"] = time.monotonic() - STARTED
        result["process_lifetime_max_rss_mib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        result["measurement_scope"] = "script entry through audit; excludes interpreter startup and final write; RSS is Linux process-lifetime high-water, possibly including pre-exec history"
        result["limits"] = {"address_space_mib": 256, "cpu_seconds": 10, "alarm_seconds_from_script_entry": 120}
        temporary = args.output.with_suffix(".tmp")
        temporary.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        temporary.replace(args.output)
    print(json.dumps({"status": result["status"], "checks": len(result["checks"]),
                      "seconds": result["audit_elapsed_seconds"]}))


if __name__ == "__main__":
    main()
