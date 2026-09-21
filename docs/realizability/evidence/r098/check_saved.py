"""Read saved R097 bytes/AST only. Never import or execute archived code."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'r097'
ATTEMPT = OLD / 'attempt_01'
BASE = '9ed35fca076d413916e2b0ab9bb4a041a9adcb02'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def reject(value):
        raise ValueError(value)
    return json.loads(path.read_text(), parse_constant=reject)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(',', ':')).encode()).hexdigest()


def main():
    inventory = read(ATTEMPT / 'snapshot/inventory.json')
    for name, expected in inventory['files'].items():
        assert sha(ATTEMPT / 'snapshot' / name) == expected
        if name != 'handoff.md':
            assert sha(ROOT / inventory['origins'][name]) == expected
    # Historical handoff is the input at the published R097 STARTED commit.
    historical = subprocess.check_output(['git', 'show', '57b90a1:SESSION_HANDOFF.md'], cwd=ROOT)
    assert hashlib.sha256(historical).hexdigest() == inventory['files']['handoff.md']
    receipt = read(ATTEMPT / 'receipt.json')
    for name, expected in receipt['output_sha256'].items():
        assert sha(ATTEMPT / name) == expected
    bound = read(ATTEMPT / 'bound.json')
    assert bound['inventory_sha256'] == sha(ATTEMPT / 'snapshot/inventory.json')
    assert bound['started_sha256'] == sha(ATTEMPT / 'started.json')
    ledger = read(OLD / 'ledger.json')
    assert len(ledger['attempts']) == 1 and ledger['retry_enabled'] is False
    row = ledger['attempts'][0]
    assert row['receipt_sha256'] == sha(ATTEMPT / 'receipt.json')
    assert row['state'] == receipt['state'] == 'COMPLETED'
    assert row['status'] == receipt['status'] == 'passed'
    assert type(receipt['returncode']) is int and receipt['returncode'] == 0
    assert receipt['timed_out'] is False and receipt['error'] is None
    assert row['charged_seconds'] == ledger['total_charged_seconds'] == receipt['charged_seconds']
    assert receipt['charged_seconds'] == receipt['observed_guard_seconds'] + 5 < 120
    assert 0 < receipt['child_seconds'] <= receipt['observed_guard_seconds']
    assert 0 < receipt['child_lifetime_peak_rss_bytes'] <= 256 << 20
    assert receipt['whole_recorder_certified'] is False and receipt['live_enabled'] is False
    tree = ast.parse((OLD / 'source/validate.py').read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
    registration = next(n.value for n in tree.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == 'REGISTRY' for t in n.targets))
    names = [n.id for n in registration.elts]
    assert len(names) == len(set(names)) == len(functions) == 9
    assert set(names) == {n.name for n in functions}
    progress = read(ATTEMPT / 'output/progress.json')
    fixtures = read(ATTEMPT / 'output/fixtures.json')
    assert names == progress['registered'] == [c['name'] for c in progress['checks']]
    assert fixtures['checks'] == progress['checks']
    assert all(c['status'] == 'passed' for c in fixtures['checks'])
    assert progress['active'] is None and progress['state'] == 'COMPLETED'
    assert progress['status'] == fixtures['status'] == 'passed'
    positive = fixtures['examples']['positive']
    monitor, child, candidate, outer, witness, result = [positive[k] for k in
        ('monitor', 'child', 'candidate', 'outer', 'witness', 'result')]
    assert digest(candidate) == digest(monitor['finalization']['candidate'])
    assert digest(candidate) == monitor['finalization']['receipt']['candidate_sha256']
    expected = dict(monitor_sha256=digest(monitor), child_sha256=digest(child),
                    candidate_sha256=digest(candidate),
                    inner_receipt_sha256=digest(monitor['finalization']['receipt']),
                    owner_sha256=digest(candidate['ownership']))
    assert all(outer[k] == value for k, value in expected.items())
    assert outer['admission_sha256'] == candidate['admission_sha256'] == monitor['finalization']['receipt']['admission_sha256']
    assert witness['receipt_sha256'] == result['outer_receipt_sha256'] == digest(outer)
    assert result['receipt_sha256'] == digest(monitor['finalization']['receipt'])
    assert result['whole_recorder_certified'] is False and result['live_enabled'] is False
    assert result['status'] == 'complete' and all(type(v) is int and v == 0 for v in result['counts'].values())
    assert len(result['counts']) == 6 and all(v is None for v in monitor['counts'].values())
    partials = []
    for name, example in fixtures['examples'].items():
        if name == 'positive':
            continue
        assert all(v is None for v in example['monitor']['counts'].values())
        if 'result' in example:
            assert example['result']['status'] == 'partial_failed'
            assert all(v is None for v in example['result']['counts'].values())
        partials.append(name)
    # Neither sources nor evidence from a prior request may change in this review.
    assert not subprocess.check_output(['git', 'diff', BASE, '--', str(OLD)], cwd=ROOT)
    result = dict(status='passed', method='saved bytes, JSON arithmetic and AST only; no fixture execution',
        baseline_commit=BASE, snapshot_bindings=len(inventory['files']),
        output_bindings=len(receipt['output_sha256']), historical_handoff_verified=True,
        groups=[dict(name=n.name, start=n.lineno, end=n.end_lineno) for n in functions],
        saved_partial_examples=partials, child_seconds=receipt['child_seconds'],
        observed_guard_seconds=receipt['observed_guard_seconds'], charged_seconds=receipt['charged_seconds'],
        peak_child_rss_bytes=receipt['child_lifetime_peak_rss_bytes'],
        exclusions=receipt['exclusions'], whole_recorder_certified=False,
        input_sha256={str(p.relative_to(ROOT)): sha(p) for p in sorted(OLD.rglob('*')) if p.is_file()},
        checker_sha256=sha(Path(__file__)))
    (HERE / 'saved_validation.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'snapshot_bindings', 'output_bindings', 'saved_partial_examples')}))


if __name__ == '__main__':
    main()
