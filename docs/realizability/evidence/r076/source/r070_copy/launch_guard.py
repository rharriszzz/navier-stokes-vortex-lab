"""Standard-library safeguards for the disposable R070 runner copy."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path

POLICY = {
    "schema": 1,
    "wall_limit_seconds": 600.0,
    "child_tree_rss_limit_mib": 1536.0,
    "required_phases": ["wrong_root", "watchdog", "kernels", "wrapper",
                        "block-rhs", "disk", "parent-refusal", "advanced"],
    "physical_wall_limit_seconds": 180.0,
    "physical_child_tree_rss_limit_mib": 1536.0,
    "physical_attempt_limit": 1,
}
COUNT_KEYS = ("physical_meshes", "primary_rhs", "returned_primary_solves",
              "correction_rhs", "matrix_factorizations", "matrix_solves")


class Refusal(RuntimeError):
    pass


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise Refusal(f"JSON object required: {path}")
    return value


def verify_source_manifest(root: Path, manifest_path: Path) -> dict:
    manifest = read_json(manifest_path)
    if manifest.get("schema") != 1 or not isinstance(manifest.get("files"), dict):
        raise Refusal("invalid source manifest")
    expected_files = dict(manifest["files"])
    evidence_files = manifest.get("evidence_files", {})
    if not isinstance(evidence_files, dict) or not evidence_files:
        raise Refusal("missing evidence manifest")
    expected_files.update(evidence_files)
    for rel, expected in expected_files.items():
        path = (root / rel).resolve()
        if root.resolve() not in path.parents or not path.is_file():
            raise Refusal(f"missing or unsafe source: {rel}")
        if sha(path) != expected:
            raise Refusal(f"source hash mismatch: {rel}")
    return manifest


def _finite_number(obj: dict, key: str) -> float:
    value = obj.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise Refusal(f"missing/nonfinite {key}")
    return float(value)


def _finite_tree(value) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite_tree(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite_tree(v) for v in value)
    return True


def validate_prerequisites(report: dict, child_reports: dict[str, dict],
                            child_hashes: dict[str, str], *, preflight: dict,
                            binding: dict, source_hashes: dict[str, str],
                            policy: dict = POLICY) -> dict:
    canonical_report_hash = hashlib.sha256(
        json.dumps(report, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if (binding.get("schema") != 1 or
            binding.get("prerequisite_report_sha256") != canonical_report_hash or
            binding.get("child_report_sha256") != child_hashes or
            binding.get("archived_runner_sha256") != preflight.get("runner_sha256") or
            binding.get("production_source_sha256") != preflight.get("source_sha256")):
        raise Refusal("saved report/child/source evidence binding mismatch")
    archived = preflight.get("runner_sha256")
    if not isinstance(archived, dict):
        raise Refusal("R033 archived runner hashes missing")
    for name, expected in archived.items():
        if name not in ("physical.py", "run_contract.py") and source_hashes.get(name) != expected:
            raise Refusal(f"archived helper source changed: {name}")
    if report.get("status") != "passed":
        raise Refusal("prerequisite status is not passed")
    if not _finite_tree(report):
        raise Refusal("nonfinite prerequisite report data")
    if report.get("wall_limit_seconds") != policy["wall_limit_seconds"] or \
            report.get("rss_limit_mib") != policy["child_tree_rss_limit_mib"]:
        raise Refusal("report policy differs from declared policy")
    elapsed = _finite_number(report, "elapsed_seconds")
    if elapsed > policy["wall_limit_seconds"]:
        raise Refusal("cumulative prerequisite wall budget exceeded")
    watches = report.get("watches")
    if not isinstance(watches, dict) or set(watches) != set(policy["required_phases"]):
        raise Refusal("prerequisite watch inventory incomplete")
    if set(child_reports) != set(policy["required_phases"]):
        raise Refusal("child report inventory incomplete")
    if set(child_hashes) != set(child_reports):
        raise Refusal("child hash inventory incomplete")
    for phase, watch in watches.items():
        if not isinstance(watch, dict):
            raise Refusal(f"malformed watch: {phase}")
        if phase == "wrong_root":
            if watch.get("returncode") == 0 or watch.get("stop_reason") is not None:
                raise Refusal("wrong-root case did not refuse cleanly")
        elif (watch.get("returncode") != 0 or watch.get("stop_reason") is not None or
              _finite_number(watch, "elapsed_seconds") < 0 or
              _finite_number(watch, "parent_observed_peak_rss_mib") > policy["child_tree_rss_limit_mib"]):
            raise Refusal(f"watch failed policy: {phase}")
    watchdog = child_reports["watchdog"]
    if (watchdog.get("timeout", {}).get("stop_reason") != "wall_time_limit" or
            watchdog.get("memory", {}).get("stop_reason") != "rss_limit" or
            watchdog.get("memory", {}).get("largest_observed_process_tree", 0) < 2):
        raise Refusal("watchdog self-check failed")
    for phase, child in child_reports.items():
        if not _finite_tree(child):
            raise Refusal(f"nonfinite child report: {phase}")
        canonical_child_hash = hashlib.sha256(
            json.dumps(child, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if phase != "wrong_root" and child_hashes[phase] != canonical_child_hash:
            raise Refusal(f"child report hash mismatch: {phase}")
        if phase == "wrong_root":
            if child.get("status") != "partial_failed" or child.get("stage") != "imports":
                raise Refusal("wrong-root child report did not record import refusal")
            if report.get("wrong_root_refusal", {}).get("report_sha256") != child_hashes[phase]:
                raise Refusal("wrong-root child report is not bound by parent")
        elif phase != "watchdog" and child.get("status") != "passed":
            raise Refusal(f"child did not pass: {phase}")
    advanced = child_reports["advanced"]
    cases = advanced.get("observer_cases")
    if not isinstance(cases, list) or len(cases) != 4:
        raise Refusal("observer case evidence incomplete")
    expected_by_stage = {"observer_case_complete_compatible": 3,
                         "observer_case_complete_P": 1,
                         "observer_case_complete_A_64": 2,
                         "observer_case_complete_A_96": 3}
    if {case.get("stage") for case in cases} != set(expected_by_stage):
        raise Refusal("observer case names differ from contract")
    for case in cases:
        if (case.get("status") not in ("passed_toy_sentinel", "passed_expected_refusal") or
                case.get("matrix_solves") != 0 or case.get("physical_meshes") != 0 or
                case.get("pre_solve_observer", {}).get("calls") != 1 or
                case.get("factor_counts") != {"MatLUFactorSym": 0,
                    "MatLUFactorNum": 0, "MatSolve": 0} or
                len(case.get("oracle_checks", [])) != expected_by_stage[case["stage"]] or
                any(check.get("maximum_error", math.inf) > check.get("tolerance", -1)
                    for check in case.get("oracle_checks", []))):
            raise Refusal("observer acceptance/zero-event evidence failed")
    totals = report.get("wrong_root_refusal", {}).get("counts", {})
    if any(totals.get(key) != 0 for key in COUNT_KEYS):
        raise Refusal("wrong-root refusal counts are not zero")
    return {"status": "validated", "elapsed_seconds": elapsed,
            "wall_limit_seconds": policy["wall_limit_seconds"],
            "rss_limit_mib": policy["child_tree_rss_limit_mib"],
            "phases": sorted(watches), "child_report_sha256": dict(child_hashes)}


def initial_report() -> dict:
    return {"schema": 1, "status": "partial", "stage": "parent_initialization",
            "error": None, "last_observed": {"stage": "parent_initialization", "counts": None},
            "counts": {key: 0 for key in COUNT_KEYS}, "child_launched": False,
            "campaign_ready": False, "physical_gate_passed": False,
            "physical_attempt": 1, "policy": dict(POLICY)}


def refuse(report: dict, stage: str, error: BaseException | str,
           child_launched: bool = False, last_counts: dict | None = None) -> dict:
    report.update(status="prerequisite_refused" if not child_launched else "partial_failed",
                  stage=stage, child_launched=child_launched,
                  error={"type": type(error).__name__, "message": str(error)})
    report["last_observed"] = {"stage": stage, "counts": last_counts}
    report["counts"] = ({key: 0 for key in COUNT_KEYS} if not child_launched
                        else {key: None for key in COUNT_KEYS})
    return report


def finalize_child(report: dict, watch: dict, child_report: dict | None, *,
                   source_root: Path | None = None,
                   source_manifest_path: Path | None = None) -> dict:
    """Accept only when monitor, child hash, verified source manifest and cleanup agree."""
    report["watch"] = watch
    report["child_launched"] = True
    if child_report is None:
        report.update(status="partial_no_child_report", stage="child_report_missing")
        report["counts"] = {key: None for key in COUNT_KEYS}
        report["last_observed"] = {"stage": "unknown_child_stage", "counts": None}
        return report
    stage = child_report.get("stage", "unknown_child_stage")
    raw_counts = {key: child_report.get(key) for key in COUNT_KEYS}
    counts = {key: value if isinstance(value, int) and not isinstance(value, bool) and value >= 0
              else None for key, value in raw_counts.items()}
    report["last_observed"] = {"stage": stage, "counts": counts,
                               "child_status": child_report.get("status")}
    report["counts"] = counts
    try:
        report["child_report_sha256"] = hashlib.sha256(
            json.dumps(child_report, sort_keys=True, separators=(",", ":"),
                       allow_nan=False).encode()).hexdigest()
    except (TypeError, ValueError) as exc:
        report.update(status="partial_failed", stage=stage,
                      completion_refusal={"child_report_finite_json": False,
                                          "error": str(exc)})
        return report
    manifest_hash = None
    source_binding_error = None
    if source_root is None or source_manifest_path is None:
        source_binding_error = "source manifest path/root not supplied"
    else:
        try:
            verify_source_manifest(source_root, source_manifest_path)
            manifest_hash = sha(source_manifest_path)
        except BaseException as exc:
            source_binding_error = f"{type(exc).__name__}: {exc}"
    report["source_manifest_sha256"] = manifest_hash
    accepted = (
        watch.get("status") == "completed" and
        watch.get("stop_reason") is None and
        type(watch.get("returncode")) is int and watch.get("returncode") == 0 and
        watch.get("membership_complete") is True and
        watch.get("cleanup_confirmed") is True and
        watch.get("child_report_sha256") == report["child_report_sha256"] and
        manifest_hash is not None and
        child_report.get("source_manifest_sha256") == manifest_hash and
        watch.get("source_manifest_sha256") == manifest_hash and
        child_report.get("status") == "complete" and
        child_report.get("evidence_complete") is True and
        child_report.get("scientific_checks_passed") is True
    )
    if not accepted:
        report["status"] = "partial_failed"
        report["stage"] = stage
        report["completion_refusal"] = {
            "monitor_status": watch.get("status"),
            "returncode": watch.get("returncode"),
            "membership_complete": watch.get("membership_complete"),
            "cleanup_confirmed": watch.get("cleanup_confirmed"),
            "child_report_hash_matches": watch.get("child_report_sha256") == report["child_report_sha256"],
            "source_manifest_sha256": manifest_hash,
            "source_binding_error": source_binding_error,
            "child_status": child_report.get("status"),
            "evidence_complete": child_report.get("evidence_complete"),
            "scientific_checks_passed": child_report.get("scientific_checks_passed"),
        }
    else:
        report["status"] = "complete"
        report["stage"] = stage
    return report


def run_test_sentinel(callback) -> dict:
    """Exercise callback plumbing without enabling guarded_launch or claiming attempts."""
    if not callable(callback):
        raise Refusal("test sentinel callback is required")
    try:
        value = callback()
        return {"schema": 1, "status": "sentinel_passed", "value": value,
                "physical_enabled": False, "attempt_consumed": False}
    except BaseException as exc:
        return {"schema": 1, "status": "sentinel_failed",
                "error": {"type": type(exc).__name__, "message": str(exc)},
                "physical_enabled": False, "attempt_consumed": False}


def claim_once(record_path: Path, contract_id: str, manifest_sha256: str) -> None:
    record_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema": 1, "contract_id": contract_id,
               "source_manifest_sha256": manifest_sha256, "consumed": True}
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(record_path, flags, 0o600)
    except FileExistsError as exc:
        raise Refusal("physical attempt already consumed") from exc
    with os.fdopen(fd, "w") as stream:
        json.dump(payload, stream, sort_keys=True)
        stream.write("\n")


def record_solve(record: dict, stage: str, reason: int,
                 observed: dict[str, int], expected_solve_count: int) -> None:
    """Validate one returned KSP solve before any later correction/diagnostic."""
    record["matrix_solves"] = int(record.get("matrix_solves", 0)) + 1
    record["returned_primary_solves"] = int(record.get("returned_primary_solves", 0)) + 1
    record["last_observed"] = {"stage": stage, "counts": dict(observed),
                               "converged_reason": int(reason)}
    if reason <= 0:
        raise Refusal(f"{stage}: primary KSP reason is not converged ({reason})")
    expected = {"MatLUFactorSym": 1, "MatLUFactorNum": 1,
                "MatSolve": expected_solve_count}
    if observed != expected:
        raise Refusal(f"{stage}: PETSc events {observed}, expected {expected}")


def record_correction(record: dict, stage: str, reason: int,
                       observed: dict[str, int], expected_solve_count: int) -> None:
    record["matrix_solves"] = int(record.get("matrix_solves", 0)) + 1
    record["returned_correction_solves"] = int(record.get("returned_correction_solves", 0)) + 1
    record["last_observed"] = {"stage": stage, "counts": dict(observed),
                               "converged_reason": int(reason)}
    if reason <= 0:
        raise Refusal(f"{stage}: correction KSP reason is not converged ({reason})")
    expected = {"MatLUFactorSym": 1, "MatLUFactorNum": 1,
                "MatSolve": expected_solve_count}
    if observed != expected:
        raise Refusal(f"{stage}: PETSc events {observed}, expected {expected}")


def guarded_launch(output: Path, *, enabled: bool = False,
                   before_child=None, child_launcher=None,
                   attempt_record: Path | None = None,
                   contract_id: str = "R021-q64-q96",
                   manifest_sha256: str | None = None,
                   source_check=None) -> dict:
    """Default-deny parent entry; injected launchers exist only for sentinels."""
    output.parent.mkdir(parents=True, exist_ok=True)
    report = initial_report()
    parent_report_path = output.parent / f".{output.name}.parent-report.json"
    if parent_report_path.exists():
        return refuse(report, "parent_report_initialization", "parent report already exists")
    write_json(parent_report_path, report)
    output_created = False
    try:
        output.mkdir(exist_ok=False)
        output_created = True
        report_path = output / "report.json"
        write_json(report_path, report)
        if source_check:
            source_check()
        if child_launcher is not None:
            raise Refusal("child launcher is unavailable in the disabled physical entry")
        raise Refusal("physical execution hard-disabled in R076 validation copy")
        if before_child:
            before_child()
        if attempt_record is not None:
            if not manifest_sha256:
                raise Refusal("manifest hash required before consuming attempt")
            claim_once(attempt_record, contract_id, manifest_sha256)
        report["status"] = "launch_authorized_for_test"
        report["stage"] = "before_child"
        report["child_launched"] = True
        write_json(report_path, report)
        sentinel = child_launcher() if child_launcher else None
        report.update(status="sentinel_returned", stage="sentinel_returned",
                      sentinel=sentinel, counts={key: None for key in COUNT_KEYS})
    except BaseException as error:
        report = refuse(report, report.get("stage", "prerequisite_validation"), error,
                        bool(report.get("child_launched")), report.get("counts"))
    write_json(parent_report_path, report)
    if output_created:
        write_json(output / "report.json", report)
    return report
