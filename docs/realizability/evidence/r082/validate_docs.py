"""Final read-only integrity checks for the R082 result and its handoff."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[3]


def load(path: Path):
    return json.loads(path.read_text())


def main() -> None:
    checks = []
    def passed(name: str) -> None:
        checks.append({"name": name, "status": "passed"})

    result = load(EVIDENCE / "result.json")
    ledger = load(EVIDENCE / "attempt_ledger.json")
    manifest = load(EVIDENCE / "source_manifest.json")
    outer = load(EVIDENCE / "outer_source_manifest.json")
    assert result["status"] == "passed" and result["physical_execution_enabled"] is False
    assert len(ledger["attempts"]) == 3
    assert [row["status"] for row in ledger["attempts"]] == ["passed", "failed", "passed"]
    assert all(row["state"] == "COMPLETED" and row["timed_out"] is False for row in ledger["attempts"])
    assert ledger["cumulative_elapsed_seconds"] < ledger["limit_seconds"] == 120.0
    assert ledger["maximum_child_lifetime_peak_rss_bytes"] <= ledger["address_space_limit_bytes"]
    assert len(ledger.get("reconciliations", [])) == 1
    reconciliation = ledger["reconciliations"][0]
    assert reconciliation["attempt"] == 2 and reconciliation["resource_stop"] is False
    assert reconciliation["source_sha256"] == ledger["attempts"][1]["source_sha256_after"]
    assert (EVIDENCE / "fixture_results_attempt_02.json").exists() is False
    passed("exclusive attempts, known-failure reconciliation and cumulative caps")

    assert manifest["physical_execution_enabled"] is False
    assert manifest["source_sha256"] == ledger["attempts"][-1]["source_sha256_after"]
    for relative, expected in manifest["source_sha256"].items():
        actual = hashlib.sha256((EVIDENCE / relative).read_bytes()).hexdigest()
        assert actual == expected, relative
    for name, expected in outer["files"].items():
        assert hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() == expected
    assert "disabled pending reviewed launch contract" in (EVIDENCE / "source/r070_copy/physical.py").read_text()
    passed("final source manifests and hard-disabled R070 physical entry")

    fixture = load(EVIDENCE / "fixture_results_attempt_03.json")
    assert fixture["status"] == "passed" and fixture["checks_passed"] == 17
    assert all(row["status"] == "passed" for row in fixture["checks"])
    baseline = load(REPO / "docs/realizability/evidence/r076/source_manifest.json")
    for relative, expected in baseline["source_sha256"].items():
        assert hashlib.sha256((REPO / "docs/realizability/evidence/r076" / relative).read_bytes()).hexdigest() == expected
    passed("17 final fixture groups and R076 archive source bindings")

    request = (REPO / "REQUEST_LOG.md").read_text()
    sessions = (REPO / "WORK_SESSIONS.md").read_text()
    handoff = (REPO / "SESSION_HANDOFF.md").read_text()
    assert request.count("## R082 —") == 1
    assert "R082 count correction" in request
    assert sessions.count("## R082 —") == 1
    block = sessions.split("## R082 —", 1)[1]
    assert block.count("STARTED | 2026-09-21 14:55:29 UTC") == 1
    assert block.count("COMPLETED | 2026-09-21") == 1
    assert "R082 append-only count correction" in sessions
    assert handoff.count("## Next task") == 1 and "GPT-6 Astra/high" in handoff.split("## Next task", 1)[1]
    assert "R082 fixture repairs complete" in handoff.split("| Current task/owner |", 1)[1].splitlines()[0]
    passed("request/lifecycle/handoff continuity and single next task")

    documents = [REPO / "SESSION_HANDOFF.md", REPO / "STATUS.md", REPO / "PROJECT_TRACKS.md",
                 REPO / "REQUEST_LOG.md", REPO / "WORK_SESSIONS.md",
                 REPO / "docs/realizability/B2_NEXT_STEPS.md", EVIDENCE / "README.md"]
    link_count = 0
    import re
    for document in documents:
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", document.read_text()):
            target = target.split()[0].strip("<>")
            if "://" in target or target.startswith("mailto:"):
                continue
            local = target.split("#", 1)[0]
            path = (document.parent / local).resolve() if local else document
            assert path.exists(), f"broken local link: {document}: {target}"
            link_count += 1
    passed(f"local Markdown links ({link_count})")

    json_files = list(EVIDENCE.rglob("*.json"))
    for path in json_files:
        value = load(path)
        json.dumps(value, allow_nan=False)
    passed(f"finite JSON evidence ({len(json_files)} files)")

    changed = subprocess.run(["git", "diff", "--name-only", "HEAD"], cwd=REPO,
                             check=True, capture_output=True, text=True).stdout.splitlines()
    assert not any(path.startswith("docs/realizability/evidence/r076/") or
                   path.startswith("docs/realizability/evidence/r070/") or
                   path.startswith("docs/realizability/evidence/r073/") for path in changed)
    passed("tracked historical evidence archives unchanged")

    payload = {"schema": 1, "status": "passed", "checks_passed": len(checks),
        "checks": checks, "local_links": link_count, "finite_json_files": len(json_files),
        "attempt_count": len(ledger["attempts"]),
        "conservative_cumulative_seconds": ledger["cumulative_elapsed_seconds"],
        "validator_process_seconds": sum(row["validator_elapsed_seconds"] for row in ledger["attempts"]),
        "maximum_child_lifetime_rss_bytes": ledger["maximum_child_lifetime_peak_rss_bytes"],
        "historical_archives_modified": False,
        "scope": "documentation, ledger and source-integrity checks; no fixture rerun"}
    (EVIDENCE / "documentation_validation.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"status": "passed", "checks": len(checks), "local_links": link_count,
                      "finite_json_files": len(json_files)}))


if __name__ == "__main__":
    main()
