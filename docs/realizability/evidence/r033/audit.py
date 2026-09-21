"""Audit the archived R033 prerequisite attempts using saved data only."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def read(path):
    return json.loads(path.read_text(), parse_constant=lambda value: (_ for _ in ()).throw(
        ValueError(f"Nonfinite JSON constant: {value}")))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = HERE / "source"
    preflight = read(source / "preflight.json")
    assert preflight["status"] == "passed"
    for name, expected in preflight["source_sha256"].items():
        assert sha(REPO / name) == expected, name
    for name, expected in preflight["runner_sha256"].items():
        assert sha(source / name) == expected, name

    attempts = {}
    for number in range(1, 5):
        path = HERE / "attempts" / f"attempt-{number:02d}"
        report = read(path / "toys" / "report.json")
        attempts[number] = report
        for name, expected in read(path / "source" / "preflight.json")["runner_sha256"].items():
            assert sha(path / "source" / name) == expected, (number, name)
        assert report["physical_meshes"] == report["matrix_solves"] == 0
        assert set(report["watches"]) == {
            "wrong_root", "watchdog", "kernels", "wrapper", "block-rhs", "disk",
            "parent-refusal", "advanced"}
    assert attempts[1]["failed_phase"] == "advanced"
    assert "TimeoutError" in (HERE / "attempts/attempt-01/toys/advanced.stderr").read_text()
    assert attempts[2]["failed_phase"] == "advanced"
    assert "read-only access" in (HERE / "attempts/attempt-02/toys/advanced.stderr").read_text()
    assert attempts[3]["status"] == attempts[4]["status"] == "passed"

    current_log = (REPO / "REQUEST_LOG.md").read_bytes()
    committed_log = subprocess.check_output(
        ["git", "show", "HEAD:REQUEST_LOG.md"], cwd=REPO)
    assert current_log.startswith(committed_log)
    log_text = current_log.decode()
    assert log_text.count("## R033 —") == 1
    assert "[R033](REQUEST_LOG.md#r033--2026-09-20--continue-r022-prerequisite-coverage)" in (
        REPO / "SESSION_HANDOFF.md").read_text()

    markdown_names = [
        "REQUEST_LOG.md", "SESSION_HANDOFF.md", "STATUS.md", "PROJECT_TRACKS.md",
        "docs/realizability/B2_NEXT_STEPS.md",
        "docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md",
        "docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md",
        "docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md",
        "docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md",
    ]
    link_count = fence_count = 0
    for name in markdown_names:
        page = REPO / name
        body = page.read_text()
        fences = sum(line.lstrip().startswith("```") for line in body.splitlines())
        assert fences % 2 == 0, name
        fence_count += fences // 2
        for destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", body):
            if destination.startswith(("https://", "http://", "mailto:")):
                continue
            link_count += 1
            local, separator, anchor = destination.partition("#")
            target = (page.parent / local).resolve() if local else page
            assert target.exists(), (name, destination)
            if separator:
                headings = [re.sub(r"\s", "-", re.sub(r"[^a-z0-9 _-]", "",
                    line.lstrip("#").strip().lower())).strip("-")
                    for line in target.read_text().splitlines() if line.startswith("#")]
                assert anchor in headings, (name, destination)

    final = HERE / "attempts/attempt-04/toys"
    report = attempts[4]
    assert report["elapsed_seconds"] < 600
    assert all(row["stop_reason"] is None for row in report["watches"].values())
    assert max(row["parent_observed_peak_rss_mib"] for row in report["watches"].values()) < 1536
    assert report["watches"]["wrong_root"]["returncode"] != 0
    assert report["watches"]["parent-refusal"]["returncode"] == 0
    assert read(final / "watchdog/self-check.json")["memory"]["stop_reason"] == "rss_limit"
    reports = {
        "kernels": "toy-report.json", "wrapper": "toy-repair-report.json",
        "block-rhs": "block-rhs-report.json", "disk": "extra-toys.json",
        "parent-refusal": "parent-report.json",
    }
    for phase, filename in reports.items():
        child = read(final / phase / filename)
        assert child["status"] == "passed", phase

    advanced = read(final / "advanced/advanced-report.json")
    assert advanced["status"] == "passed"
    stages = {row["stage"] for row in advanced["checkpoints"]}
    assert {
        "before_reference_mesh_construction", "after_reference_mesh_construction",
        "before_harmonic_form_compilation", "after_harmonic_form_compilation",
        "before_oracle_matrix_assembly", "after_oracle_matrix_assembly",
        "observer_case_begin_compatible", "observer_compatible", "observer_P",
        "observer_A_64", "observer_A_96", "advanced_toys_complete",
    } <= stages
    assert len(advanced["high_order"]) == 4
    assert sum(len(row["facets"]) for row in advanced["high_order"]) == 16
    assert max(row["maximum_target_batch"] for row in advanced["high_order"]) <= 256
    cases = advanced["observer_cases"]
    assert len(cases) == 4
    all_oracles = [row for case in cases for row in case["oracle_checks"]]
    assert all(row["maximum_error"] <= row["tolerance"] for row in all_oracles)
    assert all(row["pressure_lifting_norm"] > 0 and row["exact_essential"] for row in all_oracles)
    assert cases[0]["status"] == "passed_toy_sentinel"
    assert cases[0]["completed_rhs_assemblies"] == 3
    assert cases[0]["pre_solve_observer"]["calls"] == 1
    assert all(case["pre_solve_observer"]["calls"] == 1 for case in cases)
    assert all(case["matrix_solves"] == 0 for case in cases)
    assert all(all(value == 0 for value in case["factor_counts"].values()) for case in cases)
    assert all(case["failed_raw_unchanged"] for case in cases[1:])
    assert all(case["pre_solve_nullspace"]["right_test_passed"] and
               case["pre_solve_nullspace"]["transpose_test_passed"] for case in cases)
    assert len({case["pre_solve_operator"]["digest"] for case in cases}) == 1

    rhs = read(final / "block-rhs/block-rhs-report.json")
    assert rhs["status"] == "passed"
    assert rhs["missing_layout_refusal"]["refused"]
    assert rhs["wrong_offset_refusal"]["refused"]
    assert rhs["synthetic_lifting_failure"]["refused"]
    assert all(rhs[key]["matrix_solves"] == 0 for key in
               ("missing_layout_refusal", "wrong_offset_refusal", "synthetic_lifting_failure"))

    peak_attempt, peak_value = max(
        ((number, watch["parent_observed_peak_rss_mib"])
         for number, attempt in attempts.items() for watch in attempt["watches"].values()),
        key=lambda row: row[1])
    result = dict(status="passed", attempts=4,
        cumulative_wall_seconds=report["elapsed_seconds"],
        selected_limits=dict(wall_seconds=600, child_tree_rss_mib=1536),
        high_order=dict(trace_order_cases=len(advanced["high_order"]), facet_checks=16),
        observer=dict(cases=len(cases), full_block_oracle_checks=len(all_oracles),
                      once_only_calls=True, all_factor_and_solve_events_zero=True),
        maximum_parent_observed_peak_mib=peak_value,
        maximum_peak_attempt=peak_attempt,
        final_attempt_peak_mib=max(
            row["parent_observed_peak_rss_mib"] for row in report["watches"].values()),
        physical_execution=dict(meshes=0, solves=0, child_launched=False),
        documentation=dict(markdown_files=len(markdown_names), local_links_and_anchors=link_count,
                           fenced_blocks=fence_count, request_history_prefix_preserved=True,
                           R033_recorded_once=True),
        checkpoint_stages=sorted(stages))
    (HERE / "validation.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    archived = {}
    for path in sorted(row for row in HERE.rglob("*")
                       if row.is_file() and row.name != "archive_manifest.json"):
        archived[str(path.relative_to(HERE))] = dict(
            bytes=path.stat().st_size, sha256=sha(path))
    manifest = dict(scope="Exact R033 sources, outputs and audit artifacts; prior R022 evidence is untouched",
                    files=archived)
    (HERE / "archive_manifest.json").write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
