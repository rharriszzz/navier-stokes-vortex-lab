"""Validate R085 documentation, immutable archives and append-only history."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import unicodedata
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = "26f7071a54096822fec78b9ebb16d248870103f1"
START = "5e70f07"
DOCS = ["REQUEST_LOG.md", "WORK_SESSIONS.md", "SESSION_HANDOFF.md", "STATUS.md",
        "PROJECT_TRACKS.md", "docs/realizability/B2_NEXT_STEPS.md",
        "docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md",
        "docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md",
        "docs/realizability/B2_MONITOR_R084_REVIEW.md",
        "docs/realizability/evidence/r085/README.md"]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO)


def headings(path):
    result = set()
    counts = {}
    for line in path.read_text().splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", match.group(1)).replace("`", "")
        base = re.sub(r"[^\w -]", "", unicodedata.normalize("NFKD", title).lower())
        base = re.sub(r"\s", "-", base.strip())
        number = counts.get(base, 0)
        counts[base] = number + 1
        result.add(base if not number else f"{base}-{number}")
    return result


def main():
    evidence_count = preserved_count = 0
    allowed = set(DOCS)
    for record in git("ls-tree", "-r", "-z", BASE).split(b"\0"):
        if not record:
            continue
        meta, name = record.split(b"\t", 1)
        name = name.decode()
        if name in allowed:
            continue
        expected = meta.split()[2].decode()
        data = (REPO / name).read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        assert expected == actual, name
        preserved_count += 1
        evidence_count += name.startswith("docs/realizability/evidence/")
    for name in ("REQUEST_LOG.md", "WORK_SESSIONS.md"):
        assert (REPO / name).read_bytes().startswith(git("show", f"{START}:{name}"))
    log = (REPO / "REQUEST_LOG.md").read_text()
    ids = re.findall(r"^## R(\d+)\b", log, re.M)
    assert len(ids) == len(set(ids)) and max(map(int, ids)) == 86
    assert "Luna Reserve Weekly limit: 1% left" in log and "[REDACTED account email]" in log
    session = (REPO / "WORK_SESSIONS.md").read_text().split("## R085 —", 1)[1]
    assert session.count("STARTED |") == 1 and session.count("COMPLETED |") == 1
    handoff = (REPO / "SESSION_HANDOFF.md").read_text()
    assert handoff.count("## Next task") == 1
    assert "fixture-only integration repair of H01–H04" in " ".join(handoff.split())
    assert "R085 review complete" in handoff and "GPT-6 Astra/high" in handoff
    links = fragments = 0
    for name in DOCS:
        document = REPO / name
        for target in re.findall(r"(?<!!)\[[^\]]*\]\(([^)]+)\)", document.read_text()):
            target = target.split()[0].strip("<>")
            if "://" in target or target.startswith("mailto:"):
                continue
            path_text, _, fragment = target.partition("#")
            dest = (document.parent / unquote(path_text)).resolve() if path_text else document
            if dest == HERE / "documentation_validation.json" and not dest.exists():
                pass  # This script creates that report after successful checks.
            else:
                assert dest.exists(), (name, target)
            links += 1
            if fragment:
                assert fragment in headings(dest), (name, target)
                fragments += 1
    syntax_count = json_count = 0
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
        syntax_count += 1
    for path in HERE.glob("*.json"):
        if path.name == "documentation_validation.json":
            continue
        json.dumps(json.loads(path.read_text()), allow_nan=False)
        json_count += 1
    start = json.loads((HERE / "audit_started.json").read_text())
    for name, digest in start["sources"].items():
        assert hashlib.sha256((HERE.parent / name).read_bytes()).hexdigest() == digest
    completed = json.loads((HERE / "audit_completed.json").read_text())
    assert completed["returncode"] == 0 and completed["timed_out"] is False and completed["sources_unchanged"] is True
    assert completed["child_elapsed_seconds"] < 10 and completed["child_lifetime_peak_rss_bytes"] < 256 << 20
    archive_bindings = {}
    for version in ("r076", "r082"):
        root = HERE.parent / version
        manifest = json.loads((root / "source_manifest.json").read_text())
        for name, digest in manifest["source_sha256"].items():
            assert hashlib.sha256((root / name).read_bytes()).hexdigest() == digest, (version, name)
        archive_bindings[version] = len(manifest["source_sha256"])
    subprocess.run(["git", "diff", "--check"], cwd=REPO, check=True)
    result = dict(status="passed", base_commit=BASE, published_start=START,
        preserved_files=preserved_count, preserved_evidence_files=evidence_count,
        append_only_logs=2, unique_request_ids=len(ids), local_links=links,
        heading_fragments=fragments, python_syntax_files=syntax_count,
        finite_json_files=json_count, audit_bound_files=len(start["sources"]),
        archive_source_bindings=archive_bindings,
        audit_runs=1, live_or_physical_runs=0,
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        delivery_state="completion prepared; publication outcome reported after push")
    (HERE / "documentation_validation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
