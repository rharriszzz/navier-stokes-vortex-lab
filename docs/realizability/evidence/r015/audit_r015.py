"""Read-only checks for the R015 toy-only wrapper repair archive."""
import ast
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent


def strict_json(path):
    return json.loads(path.read_text(), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source_paths = [
        "realizability/__init__.py",
        "realizability/backends/__init__.py",
        "realizability/backends/b1_verification.py",
        "realizability/backends/b2_coercivity.py",
        "realizability/backends/b2_gate.py",
        "realizability/backends/b2_stability.py",
        "realizability/backends/b2_verification.py",
        "realizability/backends/fem_observables.py",
        "realizability/backends/fenicsx_stokes.py",
        "realizability/backends/hdiv_stokes.py",
        "realizability/boundary_modes.py",
        "realizability/cli.py",
        "realizability/config.py",
        "realizability/observables.py",
        "realizability/reference.py",
        "realizability/response.py",
        "realizability/sensors.py",
        "realizability/swirl_reference.py",
        "configs/realizability/pilot.json",
    ]
    report = strict_json(EVIDENCE / "toy-runs/attempt-08/evidence/toy-repair-report.json")
    watches = [strict_json(path / "watch.json") for path in sorted((EVIDENCE / "toy-runs").glob("attempt-*"))]
    assert len(watches) == 8
    elapsed = math.fsum(row["elapsed_seconds"] for row in watches)
    peak_rss = max(row["parent_observed_peak_rss_mib"] for row in watches)
    max_gap = max(row["maximum_sample_gap_seconds"] for row in watches)
    assert elapsed < 60.0 and peak_rss < 512.0
    assert all(row["stop_reason"] is None for row in watches)
    assert all(row["returncode"] == 0 for row in watches if row is watches[-1])
    assert report["status"] == "passed" and report["campaign_ready"] is False
    assert report["physical_meshes"] == report["pde_solves"] == 0
    assert report["matrix_factorizations"] == report["matrix_solves"] == 0
    assert report["source_sha256"] == {name: sha(ROOT / name) for name in source_paths}
    assert report["tetrahedron"]["constrained_dofs_per_block"] == [24, 0, 24, 0]
    assert report["tetrahedron"]["velocity_free_interior_dofs"] == [6, 6]
    assert report["tetrahedron"]["pressure_constraints"] == 0
    assert all(row["exact"] for row in report["tetrahedron"]["complex_target_assignment"])
    assert all(row["refused"] for row in report["refusal_cases"])
    assert all(report["failure_reporting"].values())
    runner = (EVIDENCE / "physical.py").read_text()
    assert "bc.function_space==spaces" not in runner
    assert "bc.function_space == spaces" not in runner
    assert "apply_lifting(rhs,captured['a'],bcs=new_grouped)" in runner
    assert "set_bc(rhs,new_grouped)" in runner
    assert "record_compatibility" in runner and "record_returned_solve" in runner
    old_manifest = strict_json(ROOT / "docs/realizability/evidence/r014/archive_manifest.json")
    for name, item in old_manifest.items():
        assert sha(ROOT / "docs/realizability/evidence/r014" / name) == item["archived_sha256"]
    for path in EVIDENCE.rglob("*.py"):
        ast.parse(path.read_text())
    for path in EVIDENCE.rglob("*.json"):
        strict_json(path)
    result = dict(
        status="passed",
        monitored_toy_attempts=len(watches),
        total_parent_monitored_seconds=elapsed,
        maximum_observed_child_tree_rss_mib=peak_rss,
        maximum_sample_gap_seconds=max_gap,
        toy_contract_passed=True,
        physical_meshes=0,
        pde_solves=0,
        matrix_factorizations=0,
        pinned_source_identities=len(source_paths),
        r014_archived_artifacts_verified=len(old_manifest),
        all_json_finite=True,
        all_python_sources_parse=True,
    )
    (EVIDENCE / "validation.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    manifest = {
        str(path.relative_to(EVIDENCE)): sha(path)
        for path in sorted(EVIDENCE.rglob("*"))
        if path.is_file() and path.name != "archive_manifest.json"
    }
    (EVIDENCE / "archive_manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
