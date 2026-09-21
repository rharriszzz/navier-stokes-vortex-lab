"""One bounded R096 review; imports functions, never archived runner/test mains."""
from copy import deepcopy
from pathlib import Path
import ast
import hashlib
import json
import sys
import tempfile

HERE = Path(__file__).resolve().parent
R088 = HERE.parent / 'r088'
sys.path.insert(0, str(R088 / 'source'))
from integration import Ownership, Domain, accept_sentinel, digest
from primitives import finite_json
from attempt_accounting import prior_elapsed


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    checks = []
    out = HERE / 'attempt_01'

    def record(name, **details):
        checks.append(dict(name=name, **details))
        (out / 'progress.json').write_text(json.dumps(checks, indent=2, allow_nan=False) + '\n')

    snapshot = R088 / 'attempt_01/snapshot'
    inventory = read(snapshot / 'inventory.json')
    bound = read(R088 / 'attempt_01/bound.json')
    receipt = read(R088 / 'attempt_01/receipt.json')
    ledger = read(R088 / 'ledger.json')
    fixtures = read(R088 / 'attempt_01/output/fixtures.json')
    progress = read(R088 / 'attempt_01/output/progress.json')
    assert all(sha(snapshot / n) == h for n, h in inventory['files'].items())
    assert bound['source_sha256'] == inventory['files']
    assert bound['inventory_sha256'] == receipt['inventory_sha256'] == sha(snapshot / 'inventory.json')
    for path in (R088 / 'source').glob('*.py'):
        assert sha(path) == sha(snapshot / 'source' / path.name)
    assert sha(R088 / 'run.py') == sha(snapshot / 'run.py')
    assert sha(R088 / 'contract.md') == sha(snapshot / 'inputs/contract.md')
    assert all(sha(R088 / 'attempt_01/output' / n) == h for n, h in receipt['output_sha256'].items())
    assert ledger['attempts'][0]['receipt_sha256'] == sha(R088 / 'attempt_01/receipt.json')
    assert len(ledger['attempts']) == 1
    assert ledger['cumulative_charged_seconds'] == receipt['charged_seconds'] < 120
    assert receipt['guarded_child_seconds'] <= receipt['observed_guard_seconds']
    assert receipt['charged_seconds'] >= receipt['observed_guard_seconds'] + 5
    assert type(receipt['returncode']) is int and receipt['returncode'] == 0
    assert receipt['resource_stop'] is False and receipt['timed_out'] is False
    assert receipt['child_lifetime_peak_rss_bytes'] < 256 << 20
    assert receipt['live_guard_certified'] is False and len(receipt['exclusions']) == 2
    old_ledger = read(snapshot / 'inputs/r084_attempt_ledger.json')['attempts']
    reconciliations = read(snapshot / 'inputs/r084_reconciliations.json')['reconciliations']
    assert prior_elapsed(old_ledger, reconciliations=reconciliations) == 15.69079346198123
    record('source_outputs_and_all_attempt_accounting', snapshot_files=len(inventory['files']),
           r088_charged_seconds=receipt['charged_seconds'],
           r084_charged_seconds=15.69079346198123, exclusions=receipt['exclusions'])

    tree = ast.parse((R088 / 'source/validate.py').read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
    names = sorted(n.name for n in functions)
    assert len(names) == len(set(names)) == 14
    assert names == progress['registered'] == [r['name'] for r in progress['checks']]
    assert progress['checks'] == fixtures['checks']
    assert all(r['status'] == 'passed' for r in progress['checks'])
    assert progress['state'] == 'COMPLETED' and progress['active'] is None
    record('all_14_saved_functions', functions=[dict(name=n.name, line=n.lineno, end_line=n.end_lineno)
                                               for n in functions])

    positive = fixtures['examples']['positive']
    own = deepcopy(positive['child']['ownership'])
    for name in ('workload', 'helper'):
        d = own[name]
        own[name] = Domain(tuple(tuple(i) for i in d['identities']), d['container'], tuple(d['reaper']))
    owner = Ownership(**own)
    with tempfile.TemporaryDirectory(prefix='r096-fake-') as directory:
        root = Path(directory)
        # Reconstruct only the two fixed, non-executable fixture inputs described
        # by R088 validate.Fixture; verify the exact original manifest digest.
        (root / 'input.txt').write_text('deterministic sentinel source\n')
        (root / 'evidence.json').write_text('{}\n')
        manifest = dict(schema=1, files={'input.txt': sha(root / 'input.txt')},
                        evidence_files={'evidence.json': sha(root / 'evidence.json')})
        manifest_path = root / 'source_manifest.json'
        manifest_path.write_text(finite_json(manifest) + '\n')
        assert sha(manifest_path) == owner.manifest_sha256

        def accept(m=None, c=None, saved=None):
            return accept_sentinel(owner, positive['monitor'] if m is None else m,
                positive['child'] if c is None else c, source_root=root,
                source_manifest_path=manifest_path,
                persisted_candidate=positive['candidate'] if saved is None else saved)

        result = accept()
        assert result == positive['result']
        assert all(type(v) is int and v == 0 for v in result['counts'].values())
        record('saved_positive_acceptance', result=result)
        for name in ('owner_attempt', 'cleanup_identity'):
            m, c = deepcopy(positive['monitor']), deepcopy(positive['child'])
            candidate = m['finalization']['candidate']
            if name == 'owner_attempt':
                candidate['ownership']['attempt'] = 2
                c['ownership']['attempt'] = 2
            else:
                candidate['cleanup']['workload']['identities'] = [[999, 999]]
                c['cleanup'] = deepcopy(candidate['cleanup'])
            m['finalization']['receipt']['candidate_sha256'] = digest(candidate)
            result = accept(m, c, candidate)
            assert result['status'] == 'partial_failed'
            record('rebound_' + name + '_refused', result=result)

        saved = deepcopy(positive['candidate'])
        saved['schema'] = 4.0
        assert saved == positive['candidate'] and digest(saved) != digest(positive['candidate'])
        result = accept(saved=saved)
        assert result['status'] == 'complete'
        record('J01_persisted_schema_alias_accepted', result=result,
               durable_digest=digest(saved), receipt_digest=positive['monitor']['finalization']['receipt']['candidate_sha256'])

        m = deepcopy(positive['monitor'])
        m['counts'] = {k: 7 for k in m['counts']}
        result = accept(m=m)
        assert result['status'] == 'complete'
        record('J02_contradictory_monitor_counts_accepted', monitor_counts=m['counts'], result=result)

        m = deepcopy(positive['monitor'])
        m['samples'] = []
        result = accept(m=m)
        assert result['status'] == 'complete'
        record('J02_missing_samples_accepted', result=result)

        m = deepcopy(positive['monitor'])
        candidate = m['finalization']['candidate']
        candidate.update(cleanup_started=20.0, cleanup_observed=20.0, cleanup_deadline=25.0)
        m['finalization']['receipt'].update(observed_at=20.0, candidate_sha256=digest(candidate))
        result = accept(m=m, saved=candidate)
        assert result['status'] == 'complete'
        record('J03_rebased_cleanup_times_accepted', result=result,
               source_fixture_active_deadline=10, source_fixture_outer_deadline=15,
               mutated_cleanup_start=20, mutated_cleanup_deadline=25,
               limitation='Acceptance API has no authoritative deadline argument; no supervisor overrun was executed.')

    assert 'validate' not in sys.modules
    result = dict(schema=1, status='review_observations_confirmed', checks=checks,
                  archived_mains_executed=False, physical_enabled=False)
    with (out / 'review.json').open('w') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        import os
        os.fsync(stream.fileno())
    print(json.dumps(dict(status=result['status'], checks=len(checks))))


if __name__ == '__main__':
    main()
