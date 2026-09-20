"""Archive the stopped R018 prerequisite attempt; standard library only."""
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = Path.cwd()
DEST = ROOT / 'docs/realizability/evidence/r018'


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    preflight = read(HERE / 'preflight.json')
    toy = read(HERE / 'toys/report.json')
    assert toy['status'] == 'prerequisite_refused' and toy['failed_phase'] == 'wrapper'
    assert not (HERE / 'physical').exists()
    assert not (HERE / 'toys/wrapper/toy-repair-report.json').exists()
    source = (HERE / 'wrapper_toys.py').read_text()
    location = 'repository_root = Path(__file__).resolve().parents[4]'
    line = next(i for i, text in enumerate(source.splitlines(), 1) if location in text)
    assert line == 22
    parents = list((HERE / 'wrapper_toys.py').resolve().parents)
    assert len(parents) == 3
    report = dict(
        status='stopped_before_physical_execution', stage='wrapper_toy_repository_root',
        physical_attempts=0, physical_meshes=0, pde_solves=0,
        primary_rhs=0, correction_rhs=0, matrix_solves=0, factorizations=0,
        campaign_ready=False, physical_gate_passed=False,
        error=dict(type='IndexError', message='4', file='wrapper_toys.py', line=line),
        cause='The unchanged R017 toy assumes archive-relative parents[4]; the R018 disposable /tmp copy has only three parents. R018 preflight overlooked this launch-layout dependency.',
        child_report_present=False,
        child_report_absence_reason='Root resolution precedes record construction, first checkpoint and try/except.',
        completed_phases=['watchdog', 'kernels'], failed_phase='wrapper',
        skipped_phases=['block-rhs', 'disk', 'physical'],
        toy_total_seconds=toy['elapsed_seconds'],
        toy_peak_child_tree_rss_mib=max(w['parent_observed_peak_rss_mib'] for w in toy['watches'].values()),
        toy_maximum_sample_gap_seconds=max(w['maximum_sample_gap_seconds'] for w in toy['watches'].values()),
        disposable_parent_paths=[str(p) for p in parents],
        production_source_identities=len(preflight['source_sha256']),
        prior_evidence_files_preserved=len(preflight['historical_file_sha256']),
        physical_runner_changed=False, scientific_parameters_changed=False,
        retry_after_stop=False,
        next_task='Repair repository-root discovery and early failure reporting on toys; validate the exact disposable launch context before any separately continued physical attempt.')
    (HERE / 'poststop_review.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    DEST.mkdir(exist_ok=False)
    manifest = {}
    for path in sorted(HERE.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        relative = path.relative_to(HERE)
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
        manifest[str(relative)] = dict(original_path=str(path), original_sha256=sha(path),
                                      archived_sha256=sha(target))
    (DEST / 'archive_manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(archived_files=len(manifest), report=report), indent=2))


if __name__ == '__main__':
    main()
