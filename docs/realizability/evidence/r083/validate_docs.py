"""R083 read-only repository checks; writes only its new validation evidence."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = "c5ffc2c8041144d8b0362f44bbcfbb7ae8daaa0d"
START = "13b38ae"


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    value = json.loads(path.read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    json.dumps(value, allow_nan=False)
    return value


def main():
    checks = []
    counts = {}
    try:
        old = git("ls-tree", "-r", "-z", BASE, "--", "docs/realizability/evidence")
        count = 0
        for entry in old.split(b"\0"):
            if not entry:
                continue
            meta, name = entry.split(b"\t", 1)
            data = (REPO / name.decode()).read_bytes()
            digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            assert digest == meta.split()[2].decode(), name
            count += 1
        counts["archived_evidence_files"] = count
        pins = load(REPO / "docs/realizability/evidence/r033/source/preflight.json")["source_sha256"]
        for name, digest in pins.items():
            assert sha(REPO / name) == digest, name
        counts["production_pins"] = len(pins)
        checks.append("all prior evidence blobs and production pins unchanged")

        for name in ("REQUEST_LOG.md", "WORK_SESSIONS.md"):
            assert (REPO / name).read_bytes().startswith(git("show", f"{START}:{name}")), name
        requests = (REPO / "REQUEST_LOG.md").read_text()
        ids = re.findall(r"^## R(\d+) —", requests, re.M)
        assert len(ids) == len(set(ids)) and max(map(int, ids)) == 83
        sessions = (REPO / "WORK_SESSIONS.md").read_text().split("## R083 —", 1)[1]
        assert sessions.count("STARTED |") == sessions.count("COMPLETED |") == 1
        assert "released: no" in sessions
        handoff = (REPO / "SESSION_HANDOFF.md").read_text()
        assert handoff.count("## Next task") == 1
        task = handoff.split("## Next task", 1)[1].split("## Deferred", 1)[0]
        assert "GPT-5.6 Luna/medium" in task and "G01–G07" in task and "fixture-only" in task
        assert "PC/WSL `daisy` retains ownership" in handoff
        checks.append("append-only log prefixes, unique IDs, lifecycle and single current task")

        docs = [REPO / name for name in ("REQUEST_LOG.md", "WORK_SESSIONS.md", "SESSION_HANDOFF.md",
            "STATUS.md", "PROJECT_TRACKS.md", "docs/realizability/B2_NEXT_STEPS.md",
            "docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md",
            "docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md",
            "docs/realizability/B2_MONITOR_R082_REVIEW.md")]
        docs.append(HERE / "README.md")
        link_count = fragment_count = 0
        def headings(path):
            slugs = set()
            for title in re.findall(r"^#{1,6}\s+(.+)$", path.read_text(), re.M):
                title = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", title)
                slugs.add(re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-"))
            return slugs
        for doc in docs:
            for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", doc.read_text()):
                target = target.split()[0].strip("<>")
                if "://" in target or target.startswith("mailto:"):
                    continue
                path, _, fragment = target.partition("#")
                resolved = (doc.parent / path).resolve() if path else doc
                assert resolved.exists() or resolved == HERE / "documentation_validation.json", (doc, target)
                link_count += 1
                if fragment and resolved.suffix == ".md":
                    assert fragment in headings(resolved), (doc, target)
                    fragment_count += 1
        counts.update(local_links=link_count, heading_fragments=fragment_count)
        checks.append("local Markdown links and heading fragments")

        started = load(HERE / "audit_started.json")
        for name, digest in started["sources"].items():
            assert sha(HERE.parent / name) == digest, name
        review = load(HERE / "review.json")
        for name, digest in review["audit_sources"].items():
            assert sha(HERE.parent / name) == digest, name
        completed = load(HERE / "audit_completed.json")
        assert completed["returncode"] == 0 and completed["timed_out"] is False
        assert [f["id"] for f in review["findings"]] == [f"G{i:02d}" for i in range(1, 8)]
        assert review["physical_enabled_launcher_refused"] and not review["physical_attempt_created"]
        counts["bound_audit_input_sources"] = len(started["sources"])
        checks.append("one audit, immutable executed sources, findings and default-deny evidence")

        contract = load(REPO / "docs/realizability/evidence/r081/live_suite.json")
        assert not contract["physical_execution_enabled"] and not contract["implementation_present"]
        assert contract["budgets"]["cumulative_wall_seconds"] == 30 + 10 * 12 + 30 == 180
        review_doc = (REPO / "docs/realizability/B2_MONITOR_R082_REVIEW.md").read_text()
        for case in contract["cases"]:
            assert f'| {case["id"]} |' in review_doc
        for i in range(1, 12):
            assert f"| F{i:02d} " in review_doc
        assert contract["policy"]["physical_limits_unchanged"] == {"wall_seconds": 180, "rss_mib": 1536}
        checks.append("F01–F11 and ten-case maps, frozen contract and physical limits")

        python_files = list(HERE.glob("*.py"))
        for path in python_files:
            ast.parse(path.read_text(), filename=str(path))
        json_files = list(HERE.glob("*.json"))
        for path in json_files:
            load(path)
        counts.update(new_python_syntax_files=len(python_files), finite_json_inputs=len(json_files))
        checks.append("new Python syntax and finite evidence JSON without application execution")
        git("diff", "--check")
        checks.append("scoped unstaged whitespace")
        result = {"status": "passed", "checks": checks, "counts": counts, "base": BASE,
                  "scope": "documentation/integrity only; no audit replay or live adapters",
                  "checker_sha256": sha(Path(__file__))}
    except BaseException:
        result = {"status": "failed", "checks_completed": checks, "counts": counts,
                  "error": traceback.format_exc(), "checker_sha256": sha(Path(__file__))}
    with (HERE / "documentation_validation.json").open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps(result))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
