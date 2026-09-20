"""Archive the stopped R022 disposable run; no numerical imports or execution."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
WORK = Path('/tmp/navier-b2-compatible-r022')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = {}
    for path in sorted(WORK.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts or path.suffix == '.tmp':
            continue
        relative = path.relative_to(WORK)
        # Initial support sources that did not change are represented by their
        # exact root copy. Preserve the two different initial sources in place.
        destination = HERE / relative
        if relative.parts[:2] == ('attempts', 'attempt-01') and path.suffix == '.py':
            current = WORK / path.name
            if sha(path) == sha(current):
                destination = HERE / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        assert sha(destination) == sha(path)
        manifest[str(relative)] = dict(sha256=sha(path),
            archive_path=str(destination.relative_to(HERE)))
    (HERE / 'archive_manifest.json').write_text(json.dumps(dict(
        scope='Exact execution sources and reports, with identical support sources shared',
        artifacts=manifest), indent=2, allow_nan=False) + '\n')
    print(json.dumps(dict(artifacts=len(manifest),
        unique_archived_files=len({row['archive_path'] for row in manifest.values()}))))


if __name__ == '__main__':
    main()
