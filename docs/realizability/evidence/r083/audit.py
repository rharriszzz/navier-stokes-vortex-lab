"""R083 single fake/source audit. Never run an archived validator main/recorder."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import tempfile
import time

START = time.monotonic()
HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "r082"
SOURCE = BASE / "source"
sys.dont_write_bytecode = True
sys.path[:0] = [str(SOURCE), str(BASE)]
import monitor_core as core
import host_protocol


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    fixtures = load("r083_reviewed_fixtures", SOURCE / "validate.py")
    guard = fixtures.load_guard()
    findings = []
    tree = ast.parse((SOURCE / "validate.py").read_text())
    defined = {n.name for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")}
    main_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "main")
    registered = {n.id for n in ast.walk(main_node) if isinstance(n, ast.Name) and n.id.startswith("test_")}
    omitted = sorted(defined - registered)
    assert omitted == ["test_incomplete_membership_and_provider_freshness", "test_tree_brackets_and_host_identity"]
    for name in omitted:
        getattr(fixtures, name)()
    findings.append({"id": "G01", "defined": len(defined), "registered": len(registered),
                     "omitted": omitted, "direct_R083_calls": "both passed; not retrospective R082 coverage"})

    clock = fixtures.Clock()
    def slow_cleanup(_limit):
        clock.value += 6
        return fixtures.cleanup_result()
    report = core.supervise(policy=core.Policy(1536, 1),
        tree_reader=lambda: fixtures.tree(1, clock.value, members=(), alive=False, code=0),
        host_request=lambda *_: None, host_poll=lambda: fixtures.host_reading(),
        clock=clock.now, wait=clock.wait, cleanup=slow_cleanup)
    assert report["status"] == "completed" and report["elapsed_seconds"]["cleanup"] == 6
    findings.append({"id": "G02", "status": report["status"], "elapsed": report["elapsed_seconds"],
                     "limit": 5, "primary_reasons": report["primary_reasons"]})

    clock = fixtures.Clock()
    pending = []
    polls = 0
    reads = 0
    def request(seq, at):
        pending.append((seq, at))
    def poll():
        nonlocal polls
        if not pending:
            return None
        seq, sent = pending.pop(0)
        polls += 1
        clock.value = 0.4 if polls == 1 else 1.1
        return fixtures.host_reading(seq, sent, clock.value)
    def read():
        nonlocal reads
        reads += 1
        if reads == 1:
            clock.value = 0.8
            return fixtures.tree(1, clock.value)
        return fixtures.tree(2, clock.value, members=(), alive=False, code=0)
    report = core.supervise(policy=core.Policy(1536, 5), tree_reader=read,
        host_request=request, host_poll=poll, clock=clock.now, wait=clock.wait,
        cleanup=lambda _: fixtures.cleanup_result())
    assert report["status"] == "completed" and polls == 2
    findings.append({"id": "G03", "status": report["status"], "first_send": 0,
                     "first_receipt": 0.4, "second_send": 0.8, "second_receipt": 1.1,
                     "previous_send_to_receipt": 1.1, "limit": 1})

    with tempfile.TemporaryDirectory(prefix="r083-fake-") as raw:
        root = Path(raw)
        (root / "input").write_text("fake source\n")
        (root / "evidence").write_text("{}\n")
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({"schema": 1, "files": {"input": sha(root / "input")},
                                       "evidence_files": {"evidence": sha(root / "evidence")}}))
        clean = fixtures.cleanup_result()
        child = {"schema": 2, "status": "complete", "stage": "fixture", "evidence_complete": True,
                 "scientific_checks_passed": True, "primary_reasons": [], "errors": [],
                 "counts": {k: 0 for k in guard.COUNT_KEYS}, "source_manifest_sha256": sha(manifest),
                 "workload_cleanup": clean["workload"], "helper_cleanup": clean["helper"]}
        watch = {"schema": 3, "status": "completed", "returncode": 0, "primary_reasons": [],
                 "secondary_errors": [], "membership_complete": True, "cleanup_confirmed": True,
                 "workload_cleanup": clean["workload"], "helper_cleanup": clean["helper"],
                 "source_manifest_sha256": sha(manifest)}
        def finalize(value, extra=None):
            digest = hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                              allow_nan=False).encode()).hexdigest()
            return guard.finalize_child(guard.initial_report(),
                {**watch, "child_report_sha256": digest, **(extra or {})}, value,
                source_root=root, source_manifest_path=manifest)
        report = finalize(child)
        assert report["status"] == "complete" and all(v is None for v in report["counts"].values())
        contradictory = finalize({**child, **{k: 7 for k in guard.COUNT_KEYS}})
        assert contradictory["status"] == "complete" and set(contradictory["counts"].values()) == {7}
        findings.append({"id": "G04", "accepted_status": report["status"],
                         "output_counts": report["counts"], "contradictory_counts": contradictory["counts"]})
        report = finalize(child, {"cleanup_errors": ["verification failed"], "survivors": [[99, 1]],
                                  "schema": 3.0})
        assert report["status"] == "complete"
        findings.append({"id": "G05", "accepted_status": report["status"],
                         "ignored_watch_errors": ["verification failed"], "ignored_watch_survivors": [[99, 1]],
                         "floating_schema_accepted": True})
        calls = []
        refused = guard.guarded_launch(root / "refused", enabled=True, child_launcher=lambda: calls.append(1))
        assert refused["child_launched"] is False and not calls
        assert not list(root.rglob("attempt.json"))

    protocol = host_protocol.HostProtocol(nonce="run-1", clock=lambda: 0)
    protocol.request(1, 0)
    try:
        protocol.reply(b"bad\n", 0.1)
    except core.MonitorError:
        pass
    else:
        raise AssertionError("malformed input should fail")
    accepted = protocol.reply(fixtures.reply(1), 0.2)
    assert accepted.status == "ok"
    findings.append({"id": "G06", "malformed_then_valid_reply": accepted.status,
                     "terminal_protocol_failure_latch": False})

    ledger = json.loads((BASE / "attempt_ledger.json").read_text())
    assert len(ledger["attempts"]) == 3
    source_checks = {}
    for rel, expected in json.loads((BASE / "source_manifest.json").read_text())["source_sha256"].items():
        source_checks[rel] = sha(BASE / rel) == expected
    for rel, expected in json.loads((BASE / "outer_source_manifest.json").read_text())["files"].items():
        source_checks[rel] = sha(BASE / rel) == expected
    assert all(source_checks.values())
    findings.append({"id": "G07", "per_attempt_outer_source_bound": False,
        "past_source_bytes_available": {str(a["attempt"]): all(sha(BASE / k) == v for k, v in a["source_sha256"].items())
                                       for a in ledger["attempts"]},
        "recorded_charged_seconds": sum(a["outer_elapsed_seconds"] for a in ledger["attempts"]),
        "saved_final_fixture_attempt": json.loads((BASE / "fixture_results_attempt_03.json").read_text())["attempt"],
        "actual_final_attempt": 3,
        "summary_peak_bytes": json.loads((BASE / "result.json").read_text())["maximum_child_lifetime_peak_rss_bytes"],
        "ledger_peak_bytes": max(a["child_lifetime_peak_rss_bytes"] for a in ledger["attempts"])})
    result = {"schema": 1, "status": "review_counterexamples_confirmed", "findings": findings,
        "source_bindings_checked": len(source_checks), "source_bindings_match": True,
        "physical_enabled_launcher_refused": True, "physical_attempt_created": False,
        "audit_sources": {str(p.relative_to(HERE.parent)): sha(p) for p in [Path(__file__),
            SOURCE / "monitor_core.py", SOURCE / "host_protocol.py", SOURCE / "linux_adapter.py",
            SOURCE / "validate.py", SOURCE / "r070_copy/launch_guard.py", BASE / "run_fixtures.py",
            BASE / "attempt_accounting.py"]},
        "python": sys.version.split()[0], "elapsed_from_after_imports_seconds": time.monotonic() - START,
        "lifetime_peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        "scope": "fakes, temporary text files and saved data only; no archived main/recorder or live adapters"}
    # Exclusive result; a failed audit cannot be silently replaced.
    with (HERE / "review.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"findings": len(findings), "status": result["status"]}))


if __name__ == "__main__":
    main()
