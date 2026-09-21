"""R081 documentation, contract and historical-preservation checks; no workloads."""
from __future__ import annotations

import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = "e40ed7baa536fa607bf99405dbc50ef2782ffb07"
START = "c1e1a71"
DOCS = ["PROJECT_TRACKS.md", "SESSION_HANDOFF.md", "STATUS.md", "REQUEST_LOG.md",
        "WORK_SESSIONS.md", "docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md",
        "docs/realizability/B2_NEXT_STEPS.md",
        "docs/realizability/MAC_PC_PERFORMANCE_MEMORY_PLAN.md",
        "docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md",
        "docs/realizability/evidence/r081/README.md"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def headings(path):
    slugs = set()
    counts = {}
    for title in re.findall(r"^#{1,6}\s+(.+)$", path.read_text(), re.M):
        title = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", title)
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        slugs.add(slug + (f"-{count}" if count else ""))
    return slugs


def check():
    checks = []
    evidence = git("ls-tree", "-r", "-z", BASE, "--", "docs/realizability/evidence")
    historical = 0
    for entry in evidence.split(b"\0"):
        if not entry:
            continue
        metadata, raw_path = entry.split(b"\t", 1)
        _mode, kind, blob = metadata.split()
        assert kind == b"blob"
        path = REPO / raw_path.decode()
        data = path.read_bytes()
        observed = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        assert observed == blob.decode(), str(path)
        historical += 1
    checks.append({"name": "historical evidence byte preservation", "files": historical})

    pins = json.loads((REPO / "docs/realizability/evidence/r033/source/preflight.json").read_text())["source_sha256"]
    for path, digest in pins.items():
        assert hashlib.sha256((REPO / path).read_bytes()).hexdigest() == digest, path
    checks.append({"name": "production source/config pins unchanged", "files": len(pins)})

    for name in ("REQUEST_LOG.md", "WORK_SESSIONS.md"):
        assert (REPO / name).read_bytes().startswith(git("show", f"{START}:{name}")), name
    log = (REPO / "REQUEST_LOG.md").read_text()
    ids = re.findall(r"^## R(\d+) —", log, re.M)
    assert len(set(ids)) == len(ids) and max(map(int, ids)) == 81
    session = (REPO / "WORK_SESSIONS.md").read_text().split("## R081 —", 1)[1]
    assert session.count("STARTED |") == session.count("COMPLETED |") == 1
    assert "released: no" in session
    checks.append({"name": "append-only log prefixes, unique IDs, R081 lifecycle", "max_request": 81})

    handoff = (REPO / "SESSION_HANDOFF.md").read_text()
    assert handoff.count("## Next task\n") == 1
    opening = handoff.split("R072 adds", 1)[0]
    next_task = handoff.split("## Next task\n", 1)[1].split("## Deferred", 1)[0]
    assert "fixture-only" in opening and "fixture-only" in next_task
    assert "Luna" in opening and "Luna" in next_task
    checks.append({"name": "handoff opening and next task agree"})

    local = fragments = shell = 0
    for name in DOCS:
        doc = REPO / name
        content = doc.read_text()
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", content):
            target = target.strip("<>")
            if "://" in target or target.startswith("mailto:"):
                continue
            path_part, _, fragment = target.partition("#")
            destination = (doc.parent / unquote(path_part)).resolve() if path_part else doc
            if destination == HERE / "documentation_validation.json":
                continue  # Written after these checks; avoid claiming a pre-existing pass.
            assert destination.exists(), (name, target)
            local += 1
            if fragment and destination.suffix == ".md":
                assert unquote(fragment) in headings(destination), (name, target)
                fragments += 1
        for block in re.findall(r"```(?:bash|sh)\n(.*?)```", content, re.S):
            subprocess.run(["bash", "-n"], input=block, text=True, check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            shell += 1
    checks.append({"name": "local links/fragments and shell syntax only", "links": local,
                   "fragments": fragments, "shell_blocks_not_executed": shell})

    count = 0
    for path in HERE.rglob("*.json"):
        json.dumps(json.loads(path.read_text()), allow_nan=False)
        count += 1
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    checks.append({"name": "finite evidence JSON and Python syntax", "json_files": count})

    review = json.loads((HERE / "attempt_01/review.json").read_text())
    assert review["status"] == "passed" and len(review["counterexamples"]) == 11
    assert review["audit_source_sha256"] == hashlib.sha256((HERE / "audit.py").read_bytes()).hexdigest()
    manifest = json.loads((HERE.parent / "r076/source_manifest.json").read_text())
    for relative, digest in manifest["source_sha256"].items():
        assert hashlib.sha256((HERE.parent / "r076" / relative).read_bytes()).hexdigest() == digest
    checks.append({"name": "audit source binding and 61 R076 source bindings", "bindings": len(manifest["source_sha256"])})

    contract = json.loads((HERE / "live_suite.json").read_text())
    budget = contract["budgets"]
    cases = contract["cases"]
    assert len(cases) == len({case["id"] for case in cases}) == 10
    assert budget["case_reservation_seconds"] == sum(budget[k] for k in
        ("case_active_seconds", "case_cleanup_seconds", "case_report_seconds"))
    assert budget["cumulative_wall_seconds"] == budget["shared_setup_seconds"] + len(cases) * budget["case_reservation_seconds"] + budget["final_validation_reporting_seconds"] == 180
    assert budget["workload_rss_mib"] == 512 and budget["maximum_payload_mib"] == 384
    assert contract["policy"]["physical_limits_unchanged"] == {"wall_seconds": 180, "rss_mib": 1536}
    assert contract["implementation_present"] is contract["physical_execution_enabled"] is contract["live_execution_authorized_by_R081"] is False
    assert contract["policy"]["windows_launch_available_mib"] == budget["workload_rss_mib"] + 1024
    checks.append({"name": "future ten-case contract arithmetic and disabled execution"})

    changed = git("diff", "--name-only", BASE).decode().splitlines()
    assert all(path in DOCS or path.startswith("docs/realizability/evidence/r081/") for path in changed), changed
    git("diff", "--check")
    checks.append({"name": "scoped changes and whitespace"})
    return {"schema": 1, "status": "passed", "utc": datetime.now(timezone.utc).isoformat(),
        "base": BASE, "start_commit": START, "python": sys.version.split()[0],
        "executable": sys.executable, "checks": checks, "checks_passed": len(checks),
        "skips": ["future command execution", "live Linux/Windows adapter workloads", "FEM/MPI/JIT", "application/render/encoder tests"],
        "source_and_contract_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.glob("*")) if p.suffix in (".py", ".json") and p.name != "documentation_validation.json"}}


if __name__ == "__main__":
    try:
        result = check()
    except BaseException as exc:
        result = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
    output = HERE / "documentation_validation.json"
    with output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(result))
    raise SystemExit(0 if result["status"] == "passed" else 1)
