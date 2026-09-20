"""Archive R020 once its monitored physical child has stopped; no FEM imports."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
DEST = Path.cwd() / 'docs/realizability/evidence/r020'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = json.loads((HERE / 'physical/report.json').read_text())
    watch = json.loads((HERE / 'physical/watch.json').read_text())
    assert report['status'] != 'partial'
    assert isinstance(watch['returncode'], int)
    DEST.mkdir(exist_ok=False)
    manifest = {}
    for source in sorted(HERE.rglob('*')):
        if not source.is_file() or '__pycache__' in source.parts:
            continue
        relative = source.relative_to(HERE)
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        # Preserve all parsed facet data with compact JSON formatting.
        if source.name in ('A_32_facets.json', 'A_64_facets.json'):
            value = json.loads(source.read_text())
            target.write_text(json.dumps(value, separators=(',', ':'), allow_nan=False) + '\n')
            assert json.loads(target.read_text()) == value
        else:
            shutil.copyfile(source, target)
        manifest[str(relative)] = dict(original_path=str(source),
            original_sha256=sha(source), archived_sha256=sha(target))
    (DEST / 'archive_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(dict(artifacts=len(manifest), status=report['status'],
                         stage=report['stage']), indent=2))


if __name__ == '__main__':
    main()
