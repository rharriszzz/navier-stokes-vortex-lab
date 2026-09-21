"""R085 read-only archive review and bounded fake counterexamples; no archived main."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "r084"
sys.path.insert(0, str(OLD / "source"))
import monitor_core as core
import owned_run
import host_protocol
import attempt_accounting


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def cleanup(identity=(10, 7)):
    return dict(confirmed=True, status="cleanup_confirmed", survivors=[], errors=[],
                identities=[list(identity)], requested_actions=["verify"])


def main():
    results = {}
    ledger = read(OLD / "attempt_ledger.json")
    rows = ledger["attempts"]
    reconciliations = read(OLD / "reconciliations.json")["reconciliations"]
    total = attempt_accounting.prior_elapsed(rows, reconciliations=reconciliations)
    summary = read(OLD / "result.json")
    assert total == summary["cumulative_elapsed_seconds"]
    assert max(r["child_lifetime_peak_rss_bytes"] for r in rows) == summary["maximum_child_lifetime_peak_rss_bytes"]
    snapshots = 0
    for row in rows:
        assert row == read(OLD / f'attempt_{row["attempt"]:02d}.json')
        assert row["source_sha256_before"] == row["source_sha256_after"] == row["source_archive_sha256"]
        for name, expected in row["source_archive_sha256"].items():
            assert digest(OLD / row["source_archive"] / name) == expected
            snapshots += 1
    for name, expected in rows[-1]["source_sha256_after"].items():
        assert digest(OLD / name) == expected
    for event in reconciliations:
        index = event["attempt"] - 1
        assert event["failed_source_sha256"] == rows[index]["source_sha256_after"]
        assert event["corrected_source_sha256"] == rows[index + 1]["source_sha256_before"]
        assert event["charged_outer_elapsed_seconds"] == rows[index]["outer_elapsed_seconds"]
    fixture = read(OLD / "fixture_results_attempt_03.json")
    progress = read(OLD / "progress_attempt_03.json")
    assert fixture["attempt"] == progress["attempt"] == 3
    assert fixture["checks"] == progress["checks"] == rows[-1]["partial_fixture_progress"]["checks"]
    assert digest(OLD / "fixture_results_attempt_03.json") == rows[-1]["fixture_result_sha256"]
    syntax = ast.parse((OLD / "source/validate.py").read_text())
    functions = [node.name for node in syntax.body if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
    main_node = next(node for node in syntax.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    registry = next(node.value for node in main_node.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "checks_to_run" for t in node.targets))
    registered = [(item.elts[0].value, item.elts[1].id) for item in registry.elts]
    assert len(functions) == len(registered) == len(fixture["checks"]) == 22
    assert set(functions) == {function for _, function in registered}
    assert [name for name, _ in registered] == [item["name"] for item in fixture["checks"]]
    assert all(item["status"] == "passed" for item in fixture["checks"])
    assert read(OLD / "checkpoints/latest.json")["status"] == "passed"
    results["archive_integrity"] = dict(source_files=len(rows[-1]["source_sha256_after"]),
        snapshots=snapshots, registered_functions=registered, charged_seconds=total,
        max_child_rss_bytes=summary["maximum_child_lifetime_peak_rss_bytes"],
        saved_checks_reviewed=True, archived_tests_rerun=False)

    spec = importlib.util.spec_from_file_location("r085_guard", OLD / "source/r070_copy/launch_guard.py")
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    with tempfile.TemporaryDirectory(prefix="r085-review-") as raw:
        root = Path(raw)
        (root / "input.txt").write_text("fake source\n")
        (root / "evidence.json").write_text("{}\n")
        manifest = root / "source_manifest.json"
        manifest.write_text(json.dumps(dict(schema=1, files={"input.txt": digest(root / "input.txt")}, evidence_files={"evidence.json": digest(root / "evidence.json")})))
        child = dict(schema=2, status="complete", stage="fixture", evidence_complete=True,
            primary_reasons=[], errors=[], counts={key: 0 for key in guard.COUNT_KEYS},
            workload_cleanup=cleanup(), helper_cleanup=cleanup((20, 8)),
            scientific_checks_passed=True, source_manifest_sha256=digest(manifest))
        watch = dict(schema=3, status="completed", stop_reason=None, returncode=0,
            membership_complete=True, cleanup_confirmed=True, primary_reasons=[],
            secondary_errors=[], workload_cleanup=cleanup(), helper_cleanup=cleanup((20, 8)),
            source_manifest_sha256=digest(manifest), cleanup_errors=[], survivors=[])
        def finalize(watch_value, child_value):
            rebound = {**watch_value, "child_report_sha256": hashlib.sha256(json.dumps(child_value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()}
            return guard.finalize_child(guard.initial_report(), rebound, child_value,
                source_root=root, source_manifest_path=manifest)
        good = finalize(watch, child)
        assert good["status"] == "complete" and good["counts"] == {key: 0 for key in guard.COUNT_KEYS}
        assert finalize(watch, {**child, "physical_meshes": 7})["status"] == "partial_failed"
        for change in ({"schema": 3.0}, {"cleanup_errors": ["contradiction"]}, {"survivors": [[99, 1]]}):
            assert finalize({**watch, **change}, child)["status"] == "partial_failed"
        results["G04_G05_rebound_positive_and_negative_controls"] = "passed"
        mismatched = copy.deepcopy(child)
        mismatched["workload_cleanup"]["identities"] = [[999, 999]]
        mismatched_result = finalize(watch, mismatched)
        assert mismatched_result["status"] == "complete"
        results["H01_unowned_cleanup_accepted"] = {"status": mismatched_result["status"], "watch": [[10, 7]], "child": [[999, 999]]}
        launched = []
        refused = guard.guarded_launch(root / "disabled", enabled=True, child_launcher=lambda: launched.append(True))
        assert not launched and refused["status"] == "prerequisite_refused" and not refused["child_launched"]
        results["physical_guard_default_deny"] = "passed"

    owner = owned_run.OwnedRun("fake", ((10, 7),), ((20, 8),))
    for state in ("OWNED_HELD", "READY", "RUNNING"):
        owner.advance(state)
    owned = owned_run.finalize_owned(owner, workload=cleanup,
        helper=lambda: cleanup((20, 8)), now=lambda: 0.0)
    assert owned["cleanup_confirmed"]
    try:
        core._validate_cleanup({name: owned[name] for name in ("workload", "helper")})
    except core.MonitorError as error:
        results["H01_owner_output_rejected_by_core"] = str(error)
    else:
        raise AssertionError("expected schema mismatch")
    calls = []
    early = owned_run.OwnedRun("held", ((10, 7),), ((20, 8),))
    early.advance("OWNED_HELD")
    try:
        owned_run.finalize_owned(early, workload=lambda: calls.append("workload"),
            helper=lambda: calls.append("helper"), now=lambda: 0)
    except core.MonitorError:
        pass
    assert calls == []
    results["H01_held_failure_skips_both_domains"] = {"calls": calls, "state": early.state}

    clock = [0.0]
    def checkpoint(value):
        if value["status"] == "cleanup_checkpoint":
            clock[0] += 6.0
    report = core.supervise(policy=core.Policy(1536, 10),
        tree_reader=lambda: core.TreeReading(1, 0, 0, "fake-linux", "ok", (), True, False, 0),
        host_poll=lambda: core.HostReading(1, 0, 0, "fake-windows", "ok", 8 << 30, 16 << 30),
        host_request=lambda *_: None, clock=lambda: clock[0], wait=lambda delay: None,
        cleanup=lambda _: {"workload": cleanup(), "helper": cleanup((20, 8))},
        checkpoint_sink=checkpoint)
    assert report["status"] == "completed" and report["elapsed_seconds"]["cleanup"] == 6
    results["H02_cleanup_checkpoint_overrun_accepted"] = {key: report[key] for key in ("status", "cleanup_errors", "elapsed_seconds")}

    protocol = host_protocol.HostProtocol(nonce="fake", clock=lambda: 0)
    protocol.request(1, 0)
    try:
        protocol.request(2, 0.1)
    except core.MonitorError:
        pass
    wire = dict(schema=1, sequence=1, nonce="fake", status="ok", available_bytes=8 << 30,
        total_bytes=16 << 30, error=None, provider_pid=20, provider_created=8)
    reading = protocol.reply((json.dumps(wire) + "\n").encode(), 0.2)
    assert reading.status == "ok" and protocol.terminal_error is None
    results["H03_request_failure_not_terminal"] = "valid reply accepted after duplicate pending request"
    protocol.request(2, 0.05)
    wire["sequence"] = 2
    regressed = protocol.reply((json.dumps(wire) + "\n").encode(), 0.1)
    assert regressed.end < reading.end
    results["H03_regressing_reply_brackets_accepted"] = [reading.end, regressed.end]
    wide = host_protocol.HostProtocol(nonce="fake", clock=lambda: 0, max_line_bytes=8192)
    wide.request(1, 0)
    wire["sequence"] = 1
    padded = (json.dumps(wire) + " " * 4200 + "\n").encode()
    assert wide.reply(padded, 0.1).status == "ok"
    results["H03_over_contract_frame_accepted"] = len(padded)

    changed = copy.deepcopy(rows)
    changed[-1]["validator_returncode"] = False
    assert attempt_accounting.prior_elapsed(changed, reconciliations=reconciliations) == total
    results["H04_boolean_returncode_accepted"] = True
    core.Policy(1536, 10, schema=3.0).validate()
    results["H04_float_policy_schema_accepted"] = True
    frozen = HERE.parent / "r081/live_suite.json"
    results["frozen_live_contract_sha256"] = digest(frozen)
    results["scope"] = "saved-data review and fake counterexamples only; no archived main/recorder, native or live operation"
    (HERE / "review.json").write_text(json.dumps(results, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": "passed", "groups": len(results), "output": "review.json"}))


if __name__ == "__main__":
    main()
