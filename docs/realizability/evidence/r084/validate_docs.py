"""Final documentation, archive and derived-evidence integrity check for R084."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def headings(path: Path) -> set[str]:
    result: set[str] = set()
    counts: dict[str, int] = {}
    for line in path.read_text().splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", match.group(1))
        title = title.replace("`", "")
        title = unicodedata.normalize("NFKD", title).lower()
        base = re.sub(r"[^\w -]", "", title, flags=re.UNICODE)
        base = re.sub(r"\s", "-", base.strip())
        number = counts.get(base, 0)
        counts[base] = number + 1
        result.add(base if number == 0 else f"{base}-{number}")
    return result


def main() -> None:
    docs = [REPO / name for name in (
        "REQUEST_LOG.md", "WORK_SESSIONS.md", "SESSION_HANDOFF.md", "STATUS.md",
        "PROJECT_TRACKS.md", "docs/realizability/B2_NEXT_STEPS.md",
        "docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md",
        "docs/realizability/B2_MONITOR_R082_REVIEW.md", "README.md", "AGENTS.md",
        "docs/realizability/evidence/r084/README.md")]
    link_count = fragment_count = 0
    for document in docs:
        source = document.read_text()
        available = headings(document)
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", source):
            target = target.split()[0].strip("<>")
            if "://" in target or target.startswith("mailto:"):
                continue
            path_text, _, fragment = target.partition("#")
            target_path = (document.parent / unquote(path_text)).resolve() if path_text else document
            if not target_path.exists():
                raise AssertionError(f"missing local link {document}: {target}")
            link_count += 1
            if fragment:
                if fragment not in headings(target_path):
                    raise AssertionError(f"missing heading fragment {document}: {target}")
                fragment_count += 1

    log = (REPO / "REQUEST_LOG.md").read_text()
    sessions = (REPO / "WORK_SESSIONS.md").read_text()
    handoff = (REPO / "SESSION_HANDOFF.md").read_text()
    assert log.count("## R084 —") == 1
    assert sessions.count("## R084 —") == 1
    r084_session = sessions.split("## R084 —", 1)[1]
    assert r084_session.count("STARTED | 2026-09-21 15:39:26 UTC") == 1
    assert r084_session.count("COMPLETED | ") == 1
    assert handoff.count("## Next task") == 1
    assert "GPT-6 Astra/high" in handoff.split("## Next task", 1)[1].split("## Deferred Mac", 1)[0]

    attempts = json.loads((HERE / "attempt_ledger.json").read_text())
    reconciliation_doc = json.loads((HERE / "reconciliations.json").read_text())
    rows = attempts["attempts"]
    reconciliations = reconciliation_doc["reconciliations"]
    assert len(rows) == 3 and len(reconciliations) == 2
    assert [row["status"] for row in rows] == ["failed", "failed", "passed"]
    assert all(row["resource_stop"] is False and row["timed_out"] is False for row in rows)
    assert attempts["cumulative_elapsed_seconds"] == sum(
        row["outer_elapsed_seconds"] for row in rows)
    assert attempts["maximum_child_lifetime_peak_rss_bytes"] == max(
        row["child_lifetime_peak_rss_bytes"] for row in rows)
    for event in reconciliations:
        number = event["attempt"]
        assert event["failed_source_sha256"] == rows[number - 1]["source_sha256_after"]
        assert event["corrected_source_sha256"] == rows[number]["source_sha256_before"]
    result = json.loads((HERE / "result.json").read_text())
    assert result["status"] == "passed"
    assert result["attempts"] == len(rows)
    assert result["cumulative_elapsed_seconds"] == attempts["cumulative_elapsed_seconds"]
    assert result["maximum_child_lifetime_peak_rss_bytes"] == attempts[
        "maximum_child_lifetime_peak_rss_bytes"]
    fixture_path = HERE / rows[-1]["fixture_result"]
    fixture = json.loads(fixture_path.read_text())
    progress = json.loads((HERE / "progress_attempt_03.json").read_text())
    assert fixture["attempt"] == 3 and fixture["checks_passed"] == 22
    assert fixture["checks"] == progress["checks"]
    assert len({row["name"] for row in fixture["checks"]}) == 22
    assert digest(fixture_path) == rows[-1]["fixture_result_sha256"]

    manifest = json.loads((HERE / "source_manifest.json").read_text())
    for relative, expected in manifest["source_sha256"].items():
        assert digest(HERE / "source" / relative) == expected
    for relative, expected in manifest["file_sha256"].items():
        assert digest(HERE / relative) == expected
    for row in rows:
        snapshot = HERE / row["source_archive"]
        assert row["source_sha256_before"] == row["source_archive_sha256"]
        assert row["source_sha256_after"] == row["source_sha256_before"]
        for relative, expected in row["source_archive_sha256"].items():
            assert digest(snapshot / relative) == expected
    old_manifest = json.loads((REPO / "docs/realizability/evidence/r082/source_manifest.json").read_text())
    for relative, expected in old_manifest["source_sha256"].items():
        assert digest(REPO / "docs/realizability/evidence/r082" / relative) == expected

    finite_json = 0
    for path in HERE.rglob("*.json"):
        value = json.loads(path.read_text())
        json.dumps(value, allow_nan=False)
        finite_json += 1
    report = {"schema": 4, "status": "passed", "documents": [
        str(path.relative_to(REPO)) for path in docs], "local_links": link_count,
        "heading_fragments": fragment_count, "finite_json_files": finite_json,
        "attempts": len(rows), "reconciliations": len(reconciliations),
        "fixture_checks": len(fixture["checks"]),
        "source_files": len(manifest["file_sha256"]),
        "checker_sha256": digest(Path(__file__).resolve()),
        "source_snapshot_files": sum(len(row["source_archive_sha256"]) for row in rows),
        "r082_archive_sources": len(old_manifest["source_sha256"]),
        "delivery_state": "completion prepared; final scoped publication follows"}
    (HERE / "documentation_validation.json").write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
