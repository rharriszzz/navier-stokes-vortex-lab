"""Read-only Git/source/document checks; write only new R074 check evidence."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
BASE = "3fcc82f832737381bed90b7d6073644cd87c52e0"
DOCS = ["AGENTS.md", "SESSION_HANDOFF.md", "STATUS.md", "PROJECT_TRACKS.md",
        "docs/realizability/B2_NEXT_STEPS.md",
        "docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md",
        "docs/realizability/evidence/r074/process_review.md"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def headings(path):
    slugs = set()
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            title = re.sub(r"^#+\s*", "", line).lower()
            slug = re.sub(r"[^\w\- ]", "", title).replace(" ", "-")
            slugs.add(slug)
    return slugs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    with args.output.open("x") as stream:
        stream.write('{"status": "started"}\n')
    result = {"base": BASE, "checks": {}, "status": "partial",
              "scope": "documentation, Git history and source integrity; no application/live adapter tests"}
    checks = result["checks"]
    try:
        history = git("ls-tree", "-r", "-z", BASE,
                      "docs/realizability/evidence").decode().rstrip("\0").split("\0")
        mismatches = []
        for row in history:
            metadata, name = row.split("\t", 1)
            digest = metadata.split()[2]
            payload = (ROOT / name).read_bytes()
            actual = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
            if actual != digest:
                mismatches.append(name)
        checks["all_historical_evidence_unchanged"] = not mismatches
        result["historical_evidence_files"] = len(history)
        result["historical_mismatches"] = mismatches
        for path in ("REQUEST_LOG.md", "WORK_SESSIONS.md"):
            checks[path + "_base_prefix_preserved"] = (ROOT / path).read_bytes().startswith(git("show", BASE + ":" + path))

        ids = re.findall(r"^## R(\d+)\s", (ROOT / "REQUEST_LOG.md").read_text(), re.M)
        checks["request_ids_unique_and_next_74"] = len(ids) == len(set(ids)) and max(map(int, ids)) == 74
        session = (ROOT / "WORK_SESSIONS.md").read_text().split("## R074 —", 1)[1]
        checks["r074_single_start_completion_pair"] = len(re.findall(r"^STARTED \|", session, re.M)) == 1 and len(re.findall(r"^COMPLETED \|", session, re.M)) == 1
        handoff = (ROOT / "SESSION_HANDOFF.md").read_text()
        next_task = handoff.split("## Next task\n", 1)[1].split("\n## ", 1)[0]
        checks["one_next_task_fixture_implementation"] = handoff.count("\n## Next task\n") == 1 and "fixture-only monitor" in next_task and "implementation" in next_task and "GPT-5.6 Luna" in next_task and "120 s cumulative / 256 MiB" in next_task

        broken = []
        local_links = 0
        fragments = 0
        for rel in DOCS:
            path = ROOT / rel
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                if re.match(r"[a-zA-Z]+:", link):
                    continue
                target, _, fragment = unquote(link).partition("#")
                resolved = (path.parent / target).resolve() if target else path
                local_links += 1
                if not resolved.exists():
                    broken.append([rel, link, "missing path"])
                elif fragment and resolved.suffix == ".md":
                    fragments += 1
                    if fragment not in headings(resolved):
                        broken.append([rel, link, "missing heading"])
        checks["local_links_and_fragments"] = not broken
        result.update(local_links=local_links, heading_fragments=fragments, broken_links=broken)
        for path in HERE.glob("*.py"):
            ast.parse(path.read_text(), filename=str(path))
        checks["new_python_syntax"] = True
        def reject(value):
            raise ValueError("nonfinite JSON: " + value)
        for path in HERE.glob("*.json"):
            json.loads(path.read_text(), parse_constant=reject)
        checks["evidence_json_finite"] = True
        audit = json.loads((HERE / "audit_attempt_01.json").read_text())
        checks["audit_12_checks_reproduced"] = len(audit["checks"]) == 12 and all(audit["checks"].values())
        checks["audit_source_bindings"] = all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == digest for p, digest in audit["source_sha256"].items())
        changed = git("diff", "--name-only", BASE).decode().splitlines()
        allowed = set(DOCS + ["REQUEST_LOG.md", "WORK_SESSIONS.md"])
        checks["only_scoped_tracked_changes"] = all(p in allowed or p.startswith("docs/realizability/evidence/r074/") for p in changed)
        git("diff", "--check")
        checks["git_diff_check"] = True
        if not all(checks.values()):
            raise AssertionError([k for k, v in checks.items() if not v])
        result["status"] = "passed"
    except BaseException as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        result["elapsed_seconds"] = time.monotonic() - started
        args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    artifacts = [p for p in HERE.iterdir() if p.is_file() and p.name != "manifest.json"]
    artifacts.append(ROOT / "docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md")
    manifest = {"base": BASE, "scope": "R074 review source/evidence only",
                "physical_execution_enabled": False,
                "files": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(artifacts)}}
    (HERE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "checks": len(checks),
                      "historical_files": len(history), "links": local_links}))


if __name__ == "__main__":
    main()
