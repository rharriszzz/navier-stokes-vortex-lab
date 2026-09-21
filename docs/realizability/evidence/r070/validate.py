"""Saved-data and synthetic launch/report contract checks (stdlib only)."""
import copy
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(BASE / 'source'))
import launch_guard as guard
import run_contract

CHILD_FILES = {'wrong_root':'wrong-root.json', 'watchdog':'watchdog.json',
    'kernels':'kernels.json', 'wrapper':'wrapper.json', 'block-rhs':'block-rhs.json',
    'disk':'disk.json', 'parent-refusal':'parent-refusal.json', 'advanced':'advanced.json'}
PHASES = tuple(CHILD_FILES)


def canon_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def saved_fixture():
    report = json.loads((BASE/'source/evidence/r033/runner-report.json').read_text())
    children = {name: json.loads((BASE/'source/evidence/r033/children'/filename).read_text())
                for name, filename in CHILD_FILES.items() if name != 'wrong_root'}
    children['wrong_root'] = json.loads((BASE/'source/evidence/r033/children/wrong-root.json').read_text())
    hashes = {name: canon_hash(child) for name, child in children.items()}
    hashes['wrong_root'] = hashlib.sha256((BASE/'source/evidence/r033/children/wrong-root.json').read_bytes()).hexdigest()
    preflight = json.loads((BASE/'source/preflight.json').read_text())
    return report, children, hashes, preflight


def binding_for(report, hashes, preflight):
    return {'schema':1, 'prerequisite_report_sha256':canon_hash(report),
            'child_report_sha256':dict(hashes),
            'archived_runner_sha256':dict(preflight['runner_sha256']),
            'production_source_sha256':dict(preflight['source_sha256'])}


class RepairContract(unittest.TestCase):
    def test_python_sources_parse(self):
        paths = sorted((BASE/'source').rglob('*.py'))
        self.assertTrue(paths)
        for path in paths:
            compile(path.read_text(), str(path), 'exec')

    def test_production_pins_and_prior_archive_are_byte_identical(self):
        root = next((path for path in (BASE, *BASE.parents)
                     if (path/'REQUEST_LOG.md').is_file()), None)
        self.assertIsNotNone(root, 'repository root not found from evidence path')
        preflight = json.loads((BASE/'source/preflight.json').read_text())
        for rel, digest in preflight['source_sha256'].items():
            self.assertEqual(guard.sha(root/rel), digest, rel)
        archive_path = root/'docs/realizability/evidence/r033/archive_manifest.json'
        archive = json.loads(archive_path.read_text())
        archived_root = archive_path.parent
        for rel, expected in archive['files'].items():
            path = archived_root/rel
            self.assertTrue(path.is_file(), rel)
            self.assertEqual(path.stat().st_size, expected['bytes'], rel)
            self.assertEqual(guard.sha(path), expected['sha256'], rel)

    def test_saved_final_evidence_and_policy_boundary_examples(self):
        report, children, hashes, preflight = saved_fixture()
        result = guard.validate_prerequisites(report, children, hashes, preflight=preflight, binding=binding_for(report, hashes, preflight), source_hashes=preflight['runner_sha256'])
        self.assertEqual(result['status'], 'validated')
        relaxed = copy.deepcopy(report)
        relaxed['elapsed_seconds'] = 61.0
        relaxed['watches']['advanced']['parent_observed_peak_rss_mib'] = 600.0
        self.assertEqual(guard.validate_prerequisites(relaxed, children, hashes, preflight=preflight, binding=binding_for(relaxed, hashes, preflight), source_hashes=preflight['runner_sha256'])['elapsed_seconds'], 61.0)
        relaxed['elapsed_seconds'] = 600.0001
        with self.assertRaises(guard.Refusal):
            guard.validate_prerequisites(relaxed, children, hashes, preflight=preflight, binding=binding_for(relaxed, hashes, preflight), source_hashes=preflight['runner_sha256'])

    def test_missing_modified_child_and_failed_observer_refuse(self):
        report, children, hashes, preflight = saved_fixture()
        with self.assertRaises(guard.Refusal):
            guard.validate_prerequisites(report, {k:v for k,v in children.items() if k != 'disk'}, hashes, preflight=preflight, binding=binding_for(report, hashes, preflight), source_hashes=preflight['runner_sha256'])
        broken_hashes = dict(hashes, advanced='0'*64)
        with self.assertRaises(guard.Refusal):
            guard.validate_prerequisites(report, children, broken_hashes, preflight=preflight, binding=binding_for(report, broken_hashes, preflight), source_hashes=preflight['runner_sha256'])
        altered = copy.deepcopy(children)
        altered['advanced']['observer_cases'][0]['factor_counts']['MatSolve'] = 1
        altered_hashes = dict(hashes, advanced=canon_hash(altered['advanced']))
        with self.assertRaises(guard.Refusal):
            guard.validate_prerequisites(report, altered, altered_hashes, preflight=preflight, binding=binding_for(report, altered_hashes, preflight), source_hashes=preflight['runner_sha256'])

    def test_nonfinite_and_wrong_root_refuse(self):
        report, children, hashes, preflight = saved_fixture()
        report['watches']['advanced']['elapsed_seconds'] = math.nan
        with self.assertRaises(guard.Refusal):
            guard.validate_prerequisites(report, children, hashes, preflight=preflight, binding=binding_for(report, hashes, preflight), source_hashes=preflight['runner_sha256'])
        report, children, hashes, preflight = saved_fixture()
        report['watches']['wrong_root']['returncode'] = 0
        with self.assertRaises(guard.Refusal):
            guard.validate_prerequisites(report, children, hashes, preflight=preflight, binding=binding_for(report, hashes, preflight), source_hashes=preflight['runner_sha256'])

    def test_source_manifest_missing_and_modified_files_refuse(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root/'source.py').write_text('pinned')
            manifest = root/'source_manifest.json'
            manifest.write_text(json.dumps({'schema':1, 'files':{'source.py':guard.sha(root/'source.py')},
                                            'evidence_files':{'report.json':'1'*64}}))
            with self.assertRaises(guard.Refusal):
                guard.verify_source_manifest(root, manifest)
            (root/'report.json').write_text('saved')
            manifest.write_text(json.dumps({'schema':1, 'files':{'source.py':guard.sha(root/'source.py')},
                                            'evidence_files':{'report.json':guard.sha(root/'report.json')}}))
            guard.verify_source_manifest(root, manifest)
            (root/'source.py').write_text('modified')
            with self.assertRaises(guard.Refusal):
                guard.verify_source_manifest(root, manifest)
        guard.verify_source_manifest(BASE/'source', BASE/'source/source_manifest.json')
        self.assertEqual(run_contract.verify()['schema'], 1)

    def test_new_parent_entrypoint_is_default_deny(self):
        with tempfile.TemporaryDirectory() as td:
            report = run_contract.physical(Path(td)/'parent')
            self.assertEqual(report['status'], 'prerequisite_refused')
            self.assertFalse(report['child_launched'])
            self.assertTrue(all(value == 0 for value in report['counts'].values()))

    def test_attempt_is_once_only(self):
        with tempfile.TemporaryDirectory() as td:
            record = Path(td)/'consumed.json'
            guard.claim_once(record, 'R021-q64-q96', 'a'*64)
            with self.assertRaises(guard.Refusal):
                guard.claim_once(record, 'R021-q64-q96', 'a'*64)

    def test_prelaunch_exception_keeps_zero_counts_and_never_calls_child(self):
        with tempfile.TemporaryDirectory() as td:
            called = []
            def fail(): raise ValueError('synthetic prelaunch failure')
            report = guard.guarded_launch(Path(td)/'out', enabled=True,
                before_child=fail, child_launcher=lambda: called.append('child'))
            self.assertFalse(called)
            self.assertFalse(report['child_launched'])
            self.assertTrue(all(v == 0 for v in report['counts'].values()))
            self.assertEqual(report['error']['message'], 'synthetic prelaunch failure')

    def test_missing_child_report_and_interrupted_checkpoint_preserve_unknowns(self):
        report = guard.initial_report()
        result = guard.finalize_child(report, {'returncode':-9, 'stop_reason':'wall_time_limit'}, None)
        self.assertEqual(result['status'], 'partial_no_child_report')
        self.assertTrue(all(v is None for v in result['counts'].values()))
        partial = {'status':'partial_failed','stage':'A_64_primary_solve',
                   'physical_meshes':1,'primary_rhs':2,'returned_primary_solves':1,
                   'correction_rhs':1,'matrix_factorizations':1,'matrix_solves':2}
        result = guard.finalize_child(guard.initial_report(),
            {'returncode':1,'stop_reason':None}, partial)
        self.assertEqual(result['last_observed']['stage'], 'A_64_primary_solve')
        self.assertEqual(result['counts']['matrix_solves'], 2)

    def test_primary_convergence_and_stage_local_events(self):
        good = {'MatLUFactorSym':1,'MatLUFactorNum':1,'MatSolve':3}
        record = {'matrix_solves':2}
        with self.assertRaises(guard.Refusal):
            guard.record_solve(record, 'A_64_solver_returned', -3, good, 3)
        record = {'matrix_solves':2}
        with self.assertRaises(guard.Refusal):
            guard.record_solve(record, 'A_64_solver_returned', 1,
                {'MatLUFactorSym':1,'MatLUFactorNum':1,'MatSolve':4}, 3)
        record = {'matrix_solves':2}
        guard.record_solve(record, 'A_64_solver_returned', 1, good, 3)
        with self.assertRaises(guard.Refusal):
            guard.record_correction(record, 'A_64_correction_solver_returned', 1,
                {'MatLUFactorSym':1,'MatLUFactorNum':1,'MatSolve':5}, 4)

    def test_success_sentinel_only_after_checks_and_default_never_launches(self):
        with tempfile.TemporaryDirectory() as td:
            order = []
            report = guard.guarded_launch(Path(td)/'sentinel', enabled=True,
                before_child=lambda: order.append('checks-passed'),
                child_launcher=lambda: (order.append('labelled-sentinel') or 'R070_SENTINEL'),
                attempt_record=Path(td)/'once.json', manifest_sha256='b'*64)
            self.assertEqual(order, ['checks-passed','labelled-sentinel'])
            self.assertEqual(report['status'], 'sentinel_returned')
            self.assertEqual(report['sentinel'], 'R070_SENTINEL')
            refused_calls = []
            refused = guard.guarded_launch(Path(td)/'disabled', enabled=False,
                before_child=lambda: refused_calls.append('validate'),
                child_launcher=lambda: refused_calls.append('child'))
            self.assertEqual(refused['status'], 'prerequisite_refused')
            self.assertEqual(refused_calls, [])
            self.assertFalse(refused['child_launched'])


if __name__ == '__main__':
    import resource, signal, time
    started = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
    signal.alarm(120)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RepairContract)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    elapsed = time.monotonic() - started
    prior_path = BASE/'attempt.json'
    prior_record = json.loads(prior_path.read_text()) if prior_path.exists() else {'attempts':[]}
    attempts = prior_record.get('attempts', [])
    if not attempts and prior_record.get('attempt'):
        attempts = [{key:value for key,value in prior_record.items() if key != 'attempt'} | {'attempt':prior_record['attempt']}]
    attempts.append({'attempt':len(attempts)+1, 'status':'passed' if result.wasSuccessful() else 'failed',
        'command':'/tmp/navier-fenicsx/bin/python validate.py',
        'python':'3.12.13', 'wall_limit_seconds':120, 'address_space_limit_mib':256,
        'elapsed_seconds':elapsed, 'peak_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
        'tests_run':result.testsRun, 'failures':len(result.failures), 'errors':len(result.errors)})
    cumulative = sum(item['elapsed_seconds'] for item in attempts)
    record = {'status':'passed' if result.wasSuccessful() and cumulative <= 120 else 'failed',
        'cumulative_wall_limit_seconds':120, 'address_space_limit_mib':256,
        'cumulative_wall_seconds':cumulative, 'attempts':attempts}
    prior_path.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
