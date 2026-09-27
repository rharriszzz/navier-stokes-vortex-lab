"""R269 caller controls: real file preflight with fake Git/manager; no FEM/launch."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import signal
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
CALLER = Path(__file__).with_name('run_once.py')
NUMERICAL = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}


class CallerChecks(unittest.TestCase):
    def setUp(self):
        self.ns = runpy.run_path(str(CALLER), run_name='r269_caller_check')
        self.g = self.ns['main'].__globals__
        self.run = self.g['RUN']
        self.assertFalse(self.run.exists() or self.run.is_symlink())
        self.replies = {('rev-parse', 'HEAD'): '0'*40,
                        ('status', '--porcelain', '--untracked-files=all'): '',
                        ('rev-parse', '--show-toplevel'): str(ROOT)}
        self.g['git'] = lambda *args: self.replies[args]
        self.events = []
        events = self.events
        class FakeBus:
            path = '/fake'
            def __init__(self): events.append('connect')
            def property(self, *args): return '249.11-0ubuntu3.22'
            def close(self): events.append('close')
        self.bus = FakeBus

    def tearDown(self):
        self.assertFalse(self.run.exists() or self.run.is_symlink())
        self.assertFalse(NUMERICAL.intersection(sys.modules))
        signal.setitimer(signal.ITIMER_REAL, 0)

    def preflight(self):
        return self.ns['preflight']('0'*40, self.bus)

    def refuses(self, text):
        self.events.clear()
        with self.assertRaisesRegex(RuntimeError, text): self.preflight()
        self.assertEqual(self.events, [])

    def test_valid_admission_and_strict_supervisor_binding(self):
        facts = self.preflight()
        self.assertEqual(self.events, ['connect', 'close'])
        self.assertEqual(facts['source_files'], 50)
        self.assertEqual(facts['runtime_artifacts_verified'], 15)
        self.assertEqual(facts['admission']['fixture'], 'manufactured')
        self.assertEqual(facts['admission']['source_commit'], '0'*40)
        self.assertEqual(facts['admission']['run_directory'], str(self.run))

    def test_source_allocation_contract_and_artifact_refusals(self):
        self.replies[('rev-parse', 'HEAD')] = '1'*40
        self.refuses('expected clean commit')
        self.replies[('rev-parse', 'HEAD')] = '0'*40
        self.replies[('status', '--porcelain', '--untracked-files=all')] = ' M source.py'
        self.refuses('expected clean commit')
        self.replies[('status', '--porcelain', '--untracked-files=all')] = ''
        digest = self.g['digest']
        for path, reason in [
            (CALLER, 'allocation or caller binding'),
            (self.g['INVENTORY'], 'allocation or caller binding'),
            (self.g['ARTIFACTS'], 'allocation or caller binding'),
            (ROOT/'verification/nonlinear_port/manufactured_driver.py', 'source or frozen manifest'),
            (self.g['MANIFEST'], 'source or frozen manifest'),
            (Path(self.g['PYTHON']).resolve(), 'interpreter changed'),
            (Path('/tmp/navier-fenicsx-r229/lib/python3.12/site-packages/dolfinx/fem/forms.py'), 'runtime artifact changed'),
        ]:
            with self.subTest(path=path):
                self.g['digest'] = lambda p, bad=path: '0'*64 if p == bad else digest(p)
                self.refuses(reason)
                self.g['digest'] = digest
        from verification.nonlinear_port import manufactured_driver
        reader = manufactured_driver.read_limited
        def changed_allocation(path):
            value = reader(path)
            if path == self.g['ALLOCATION']: value['contract_sha256'] = '0'*64
            return value
        with patch.object(manufactured_driver, 'read_limited', changed_allocation):
            self.refuses('manufactured contract changed')
        artifacts = json.loads(self.g['ARTIFACTS'].read_text())
        archive = Path(artifacts['cached_archive'])
        self.g['digest'] = lambda p: '0'*64 if p == archive else digest(p)
        self.refuses('cached archive changed')

    def test_library_resolution_and_spent_directory_refusals(self):
        resolve = Path.resolve
        lib = Path('/tmp/navier-fenicsx-r229/lib/libsuperlu.so')
        def changed(path, *args, **kw):
            return Path('/tmp/unreviewed-library') if path == lib else resolve(path, *args, **kw)
        with patch.object(Path, 'resolve', changed): self.refuses('library resolution changed')
        exists, symlink = Path.exists, Path.is_symlink
        with patch.object(Path, 'exists', lambda p: True if p == self.run else exists(p)):
            self.refuses('output directory already exists')
        with patch.object(Path, 'is_symlink', lambda p: True if p == self.run else symlink(p)):
            self.refuses('output directory already exists')

    def test_capacity_controllers_and_manager_drift(self):
        read = Path.read_text
        def low_memory(path, *args, **kw):
            return 'MemAvailable: 1 kB\n' if str(path) == '/proc/meminfo' else read(path,*args,**kw)
        with patch.object(Path, 'read_text', low_memory): self.refuses('host memory available')
        def missing_controller(path,*args,**kw):
            return 'cpu\n' if path.name == 'cgroup.controllers' else read(path,*args,**kw)
        with patch.object(Path,'read_text',missing_controller): self.refuses('controllers unavailable')
        with patch.object(self.bus,'property',lambda *a:'changed'):
            with self.assertRaisesRegex(RuntimeError,'manager version changed'): self.preflight()
        self.assertEqual(self.events,['connect','close'])

    def invoke(self):
        output = io.StringIO()
        handler = signal.getsignal(signal.SIGALRM)
        try:
            with patch.object(sys, 'argv', [str(CALLER), '0'*40]), redirect_stdout(output):
                code = self.ns['main']()
            self.assertEqual(signal.getitimer(signal.ITIMER_REAL)[0], 0)
            return code, json.loads(output.getvalue())
        finally:
            signal.signal(signal.SIGALRM, handler)

    def test_timer_before_imports_and_preflight_no_writes_on_refusal(self):
        original_load = self.g['load_components']
        sequence = []
        def load():
            self.assertGreater(signal.getitimer(signal.ITIMER_REAL)[0], 0)
            sequence.append('load')
            return original_load()
        def refuse(*args):
            self.assertGreater(signal.getitimer(signal.ITIMER_REAL)[0], 0)
            sequence.append('preflight')
            raise RuntimeError('test-only refusal')
        self.g['load_components'],self.g['preflight']=load,refuse
        with tempfile.TemporaryDirectory() as base:
            self.g['RUN']=Path(base)
            sentinel=Path(base)/'existing'; sentinel.write_text('keep')
            cwd=Path.cwd()
            try:
                os.chdir(base)
                code, record = self.invoke()
            finally:
                os.chdir(cwd)
            self.assertEqual(sorted(p.name for p in Path(base).iterdir()), ['existing'])
            self.assertEqual(sentinel.read_text(),'keep')
        self.assertEqual(sequence,['load','preflight'])
        self.assertEqual((code,record['status']),(1,'INCOMPLETE'))
        self.assertIn('test-only refusal',record['reason'])

    def test_finite_dispatch_persistence_and_nonzero_outcome(self):
        for status in ('PASS','INCOMPLETE'):
            with self.subTest(status=status),tempfile.TemporaryDirectory() as base:
                target=Path(base)/'synthetic'; self.g['RUN']=target
                admission={'synthetic':True}; calls=[]
                def preflight(*args): return {'admission':admission}
                def backend(root,*,runtime_seconds):
                    self.assertEqual((root,runtime_seconds),(ROOT,149)); return 'fake-backend'
                def supervise(path,manifest,given,handle,**kw):
                    self.assertGreater(signal.getitimer(signal.ITIMER_REAL)[0],0)
                    self.assertIs(given,admission)
                    self.assertEqual((path,manifest,handle),(target,self.g['MANIFEST'],'fake-backend'))
                    self.assertEqual(kw['owner'],'PC/WSL daisy / R269')
                    self.assertEqual(kw['interpreter'],self.g['PYTHON'])
                    calls.append(kw); path.mkdir(); return {'status':status}
                self.g['check_angular']=lambda *args:dict(valid=True,consistent=True)
                self.g['preflight']=preflight
                self.g['load_components']=lambda:(supervise,backend,self.bus)
                code,record=self.invoke()
                self.assertEqual(len(calls),1)
                self.assertEqual(code,0 if status=='PASS' else 1)
                self.assertEqual(record['status'],status)
                for name in ('caller.json','caller_completion.json'):
                    self.assertEqual(json.loads((target/name).read_text())['status'],status)

    def test_sidecar_reader_cross_checks_and_retains_measured_mismatch(self):
        from copy import deepcopy
        from verification.nonlinear_port.test_manufactured_angular import sample
        from verification.nonlinear_port.source_binding import expected_binding
        from verification.nonlinear_port.prototype import Refusal
        record=sample()
        binding=expected_binding(ROOT,dict(source_commit='0'*40,
            interpreter=self.g['PYTHON']),self.g['PYTHON'])
        record['source_binding']=binding
        numerical={key:deepcopy(record[key]) for key in
                   ('source_binding','geometry','step','time','dt')}
        numerical.update(fixed_inventory={str(i):v for i,v in
            zip(record['fixed_indices'],record['fixed_values'])},
            fixed_velocity_dofs=240,multipliers=record['state'][402:404],
            eta=record['state'][404],report=dict(numerical_accepted=False),
            raw_by_degree={d:{'angular.'+k:v for k,v in e['original'].items()
                if k!='physical_defect'} for d,e in record['degrees'].items()})
        with tempfile.TemporaryDirectory() as parent:
            directory=Path(parent); sidecar=directory/'angular_audit.json'
            path=directory/'numerical.json'
            sidecar.write_text(json.dumps(record)); path.write_text(json.dumps(numerical))
            receipt=self.ns['check_angular'](directory,'0'*40)
            self.assertTrue(receipt['consistent'])
            self.assertFalse(json.loads(path.read_text())['report']['numerical_accepted'])
            from verification.nonlinear_port.manufactured_angular import _reductions
            bad=deepcopy(record); entry=bad['degrees']['26']; entry['scalar']['G_R']+=1.
            entry['reductions'],entry['comparisons']=_reductions(bad['phi']['coefficients'],
                entry['raw_residual'],bad['fixed_indices'],entry['scalar'],entry['original'])
            sidecar.write_text(json.dumps(bad))
            self.assertFalse(self.ns['check_angular'](directory,'0'*40)['consistent'])
            for blob in (b'{"schema":1,"schema":1}', b' '*262145):
                sidecar.write_bytes(blob)
                with self.assertRaises(Refusal): self.ns['check_angular'](directory,'0'*40)
            sidecar.write_text(json.dumps(record)); numerical['eta']+=1.
            path.write_text(json.dumps(numerical))
            with self.assertRaises(Refusal): self.ns['check_angular'](directory,'0'*40)

    def test_missing_or_inconsistent_sidecar_never_promotes_inner_pass(self):
        for check in ('missing','inconsistent'):
            with self.subTest(check=check),tempfile.TemporaryDirectory() as parent:
                target=Path(parent)/'synthetic'; self.g['RUN']=target
                self.g['preflight']=lambda *args:dict(admission={})
                def supervise(*args,**kw): target.mkdir(); return dict(status='PASS')
                self.g['load_components']=lambda:(supervise,lambda *a,**kw:None,self.bus)
                def angular(*args):
                    if check=='missing': raise FileNotFoundError('angular_audit.json')
                    return dict(valid=True,consistent=False)
                self.g['check_angular']=angular
                code,result=self.invoke()
                self.assertEqual((code,result['status']),(1,'INCOMPLETE'))
                saved=json.loads((target/'caller.json').read_text())
                self.assertEqual(saved['inner_status'],'PASS')
                if check=='missing': self.assertIn('FileNotFoundError',saved['reason'])
                else: self.assertFalse(saved['angular_evidence']['consistent'])


if __name__ == '__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CallerChecks)
    with Path(__file__).with_name('caller_tests.txt').open('w') as stream:
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    summary=dict(count=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                 numerical_modules_loaded=sorted(NUMERICAL.intersection(sys.modules)),
                 python=sys.version,executable=sys.executable,
                 manager='injected fake only',fixed_directory_created=False)
    Path(__file__).with_name('caller_tests.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary))
    raise SystemExit(0 if result.wasSuccessful() and not summary['numerical_modules_loaded'] else 1)
