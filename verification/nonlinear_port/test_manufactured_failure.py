"""Source-only failure diagnostics: no FEM, manager, worker or reservation."""
import ast
from contextlib import redirect_stdout, redirect_stderr, ExitStack
import io
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import TracebackType
import unittest
from unittest.mock import patch

from . import manufactured_failure as failure
from . import manufactured_worker as worker
from .manufactured_manifest import expected
from .prototype import Refusal


FORBIDDEN = {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}


def entry_code():
    source = Path(worker.__file__)
    tree = ast.parse(source.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.If)
                and ast.unparse(n.test) == "__name__ == '__main__'")
    return compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec')


ENTRY = entry_code()


class NoNumericalImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in FORBIDDEN:
            raise AssertionError('numerical import prohibited: '+fullname)


class FailureDiagnostics(unittest.TestCase):
    def setUp(self):
        self.guard = NoNumericalImports()
        sys.meta_path.insert(0, self.guard)

    def tearDown(self):
        sys.meta_path.remove(self.guard)
        self.assertFalse({name.split('.')[0] for name in sys.modules} & FORBIDDEN)

    def test_stage_order_and_constant_markers(self):
        tracker = failure.StageTracker()
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            for name in failure.STAGES:
                tracker.mark(name,'begin')
                tracker.mark(name,'end')
        expected_lines = [f'manufactured stage={name} edge={edge}'
                          for name in failure.STAGES for edge in ('begin','end')]
        self.assertEqual(stdout.getvalue().splitlines(), expected_lines)
        self.assertEqual((tracker.last_begun,tracker.last_completed),
                         (failure.STAGES[-1],failure.STAGES[-1]))
        with self.assertRaises(ValueError): tracker.mark('imports','begin')
        with self.assertRaises(ValueError): failure.StageTracker().mark('imports','end')

    def test_injected_failure_sites_and_success_order(self):
        for site, begun, completed_stage in (
            ('imports','imports',None),
            ('mesh','mesh_and_geometry','recorder_init'),
            ('forms','primary_forms','history_and_lift'),
            ('solver','newton','compatibility_and_initial_system'),
            ('save','numerical_save','return_sampling_and_report'),
            ('handshake','completion_handshake','numerical_save'),
            (None,None,None),
        ):
            with self.subTest(site=site), TemporaryDirectory() as parent:
                directory = Path(parent)
                manifest = directory/'manifest.json'
                manifest.write_text(json.dumps(expected()))
                events = []
                def raise_at(name):
                    events.append(name)
                    raise RecursionError('injected '+name)
                def importer(_versions):
                    if site == 'imports': raise_at('imports')
                    events.append('importer')
                    return {}, {}, {}
                def recorder(*args,**kwargs):
                    events.append('recorder')
                    return object()
                def driver(*args,**kwargs):
                    for stage in failure.STAGES[2:11]:
                        kwargs['progress'](stage,'begin')
                        if (site == 'mesh' and stage == 'mesh_and_geometry'
                                or site == 'forms' and stage == 'primary_forms'
                                or site == 'solver' and stage == 'newton'):
                            raise_at(stage)
                        kwargs['progress'](stage,'end')
                    events.append('driver')
                    return {}
                def writer(*args):
                    if site == 'save': raise_at('save')
                    events.append('save')
                def finished(*args):
                    if site == 'handshake': raise_at('handshake')
                    events.append('handshake')
                changes = dict(read_limited=lambda _p:{},validate_reservation=lambda *a:None,
                    verify_source=lambda *a:{'source_commit':'a'*40},
                    _cgroup_path=lambda:'/injected-no-manager',held=lambda *a:events.append('held'),
                    load_pinned_modules=importer,LatestSystem=recorder,
                    run_manufactured=driver,write_limited_new=writer,completed=finished)
                stdout,stderr=io.StringIO(),io.StringIO()
                with ExitStack() as stack:
                    for name, value in changes.items():
                        stack.enter_context(patch.object(worker,name,value))
                    stack.enter_context(patch.dict(os.environ,{key:'1' for key in
                        ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}))
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        with self.assertRaises(SystemExit) as raised:
                            exec(ENTRY,dict(__name__='__main__',sys=sys,
                                StageTracker=failure.StageTracker,main=lambda tracker:
                                    worker.main([str(directory),str(manifest)],tracker=tracker),
                                save_failure=failure.save_failure))
                self.assertEqual(raised.exception.code, 0 if site is None else 1)
                if site is None:
                    self.assertEqual(events,['held','importer','recorder','driver','save','handshake'])
                    self.assertEqual(stderr.getvalue(),'')
                    self.assertFalse((directory/'failure.json').exists())
                    self.assertEqual(len(stdout.getvalue().splitlines()),26)
                else:
                    record=json.loads((directory/'failure.json').read_text())
                    self.assertEqual(record['last_begun_stage'],begun)
                    self.assertEqual(record['last_completed_stage'],completed_stage)
                    self.assertEqual(record['exception_type'],'RecursionError')
                    self.assertEqual(record['source_binding'],{'source_commit':'a'*40})
                    self.assertTrue(record['traceback'])
                    self.assertIn('test_manufactured_failure.py',record['traceback'][-1]['file'])
                    self.assertEqual(stderr.getvalue(),f'RecursionError: injected {events[-1]}\n')
                    self.assertNotIn('handshake',events if site != 'handshake' else [])
                    self.assertTrue(record['diagnostic_only'])

    def test_denied_reservation_never_arms_or_imports(self):
        with TemporaryDirectory() as parent:
            directory=Path(parent)
            manifest=directory/'manifest.json'
            manifest.write_text(json.dumps(expected()))
            tracker=failure.StageTracker()
            with (patch.object(worker,'read_limited',side_effect=[{},{}]),
                  patch.object(worker,'validate_reservation',side_effect=Refusal('denied')),
                  patch.object(worker,'verify_source') as verify,
                  patch.object(worker,'load_pinned_modules') as load):
                with self.assertRaisesRegex(Refusal,'denied'):
                    worker.main([str(directory),str(manifest)],tracker=tracker)
                verify.assert_not_called()
                load.assert_not_called()
            self.assertIsNone(tracker.directory)
            self.assertEqual(sorted(p.name for p in directory.iterdir()),['manifest.json'])

    def test_deep_nonascii_traceback_bounds_and_no_locals(self):
        with TemporaryDirectory() as parent:
            tracker=failure.StageTracker()
            tracker.arm(parent,{'source_commit':'b'*40})
            source='def recurse(n):\n    if n: return recurse(n-1)\n    raise RecursionError("🚀"*800)\n'
            namespace={}
            exec(compile(source,'é'*600,'exec'),namespace)
            try: namespace['recurse'](70)
            except RecursionError as exc: result=failure.save_failure(exc,tracker)
            else: self.fail('expected injected recursion')
            record=json.loads((Path(parent)/'failure.json').read_text())
            self.assertLessEqual(len(record['traceback']),32)
            self.assertGreaterEqual(len(record['traceback']),1)
            self.assertTrue(record['frames_truncated'])
            self.assertTrue(record['traceback_fields_truncated'])
            self.assertTrue(record['message_truncated'])
            self.assertFalse(record['traceback_walk_unfinished'])
            self.assertEqual(record['traceback'][-1]['function'],'recurse')
            self.assertEqual(record['traceback'][-1]['line'],3)
            self.assertLessEqual(len((Path(parent)/'failure.json').read_bytes()),failure.MAX_BYTES)
            self.assertLessEqual(len(record['exception_message']),512)
            self.assertTrue(all(len(frame['file'])<=512 and len(frame['function'])<=256
                                and set(frame)=={'file','function','line'}
                                for frame in record['traceback']))
            self.assertFalse(any('locals' in key for key in record))
            self.assertTrue(result.startswith('RecursionError: '))

    def test_byte_cap_reduces_frames_and_keeps_deepest(self):
        with TemporaryDirectory() as parent:
            tracker=failure.StageTracker();tracker.arm(parent,{})
            ns={}
            name='名'*256
            exec(compile(f'def {name}():\n    return sys._getframe()\n','🚀'*513,'exec'),dict(sys=sys),ns)
            frame=ns[name]()
            try: raise RecursionError('bytes')
            except RecursionError as exc:
                tb=None
                for _ in range(40):
                    tb=TracebackType(tb,frame,0,frame.f_lineno)
                exc.__traceback__=tb
                failure.save_failure(exc,tracker)
            record=json.loads((Path(parent)/'failure.json').read_text())
            self.assertLessEqual(len((Path(parent)/'failure.json').read_bytes()),failure.MAX_BYTES)
            self.assertTrue(record['frames_truncated'])
            self.assertGreaterEqual(len(record['traceback']),1)
            self.assertEqual(record['traceback'][-1]['function'],name)
            self.assertTrue(record['traceback_fields_truncated'])

    def test_first_eight_and_last_twenty_four_frames(self):
        with TemporaryDirectory() as parent:
            tracker=failure.StageTracker();tracker.arm(parent,{})
            def descend(n):
                if n: return descend(n-1)
                raise Refusal('deep but short')
            try: descend(45)
            except Refusal as exc:
                original=[]
                tb=exc.__traceback__
                while tb is not None:
                    original.append((tb.tb_frame.f_code.co_name,tb.tb_lineno))
                    tb=tb.tb_next
                failure.save_failure(exc,tracker)
            record=json.loads((Path(parent)/'failure.json').read_text())
            actual=[(frame['function'],frame['line']) for frame in record['traceback']]
            self.assertEqual(actual,original[:8]+original[-24:])
            self.assertEqual(len(actual),32)
            self.assertTrue(record['frames_truncated'])
            self.assertFalse(record['traceback_walk_unfinished'])

    def test_walk_cap_and_bad_message(self):
        class BadMessage(Exception):
            def __str__(self): raise RecursionError('formatting failed')
        with TemporaryDirectory() as parent:
            tracker=failure.StageTracker();tracker.arm(parent,{})
            try: raise BadMessage()
            except BadMessage as exc:
                frame=sys._getframe()
                tb=None
                for _ in range(failure.MAX_WALK+9):
                    tb=TracebackType(tb,frame,0,frame.f_lineno)
                exc.__traceback__=tb
                summary=failure.save_failure(exc,tracker)
            record=json.loads((Path(parent)/'failure.json').read_text())
            self.assertEqual(summary,'BadMessage: <exception message unavailable>')
            self.assertTrue(record['message_format_failed'])
            self.assertTrue(record['traceback_walk_unfinished'])
            self.assertEqual(len(record['traceback']),32)

    def test_exclusive_write_failure_retains_refusal(self):
        with TemporaryDirectory() as parent:
            tracker=failure.StageTracker();tracker.arm(parent,{})
            path=Path(parent)/'failure.json'
            path.write_text('original')
            try: raise Refusal('underlying failure')
            except Refusal as exc:
                with self.assertRaises(FileExistsError): failure.save_failure(exc,tracker)
            self.assertEqual(path.read_text(),'original')
            self.assertEqual(sorted(p.name for p in Path(parent).iterdir()),['failure.json'])

    def test_entry_persistence_failure_still_exits_one(self):
        def original(*,tracker):
            raise Refusal('original scientific failure')
        stderr=io.StringIO()
        with redirect_stderr(stderr),self.assertRaises(SystemExit) as raised:
            exec(ENTRY,dict(__name__='__main__',sys=sys,
                StageTracker=failure.StageTracker,main=original,
                save_failure=lambda *a:(_ for _ in ()).throw(OSError('write refused'))))
        self.assertEqual(raised.exception.code,1)
        self.assertEqual(stderr.getvalue(),'Refusal: diagnostic persistence failed\n')


if __name__ == '__main__':
    unittest.main()
