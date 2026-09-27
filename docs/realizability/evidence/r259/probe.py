"""Injected evidence of R258's ambiguous error log; no numerical import/worker."""
import ast
from contextlib import ExitStack, redirect_stderr
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
FORBIDDEN = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}


class NoNumericalImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in FORBIDDEN:
            raise AssertionError('numerical import prohibited: '+fullname)


def run():
    guard = NoNumericalImports()
    sys.meta_path.insert(0, guard)
    try:
        from verification.nonlinear_port import manufactured_worker as worker
        from verification.nonlinear_port import manufactured_driver as driver
        from verification.nonlinear_port.manufactured_manifest import expected
        source_path = ROOT/'verification/nonlinear_port/manufactured_worker.py'
        tree = ast.parse(source_path.read_text())
        entry = next(node for node in tree.body if isinstance(node, ast.If)
                     and ast.unparse(node.test) == "__name__ == '__main__'")
        code = compile(ast.Module(body=[entry], type_ignores=[]), str(source_path), 'exec')
        cases = []
        for fail_at in ('pinned_import', 'driver_entry', 'create_cube', None):
            calls = []
            def fail(site):
                calls.append(site)
                raise RecursionError('maximum recursion depth exceeded')
            modules = dict.fromkeys(('np','mesh','fem','fem_petsc','basix_ufl','basix','ufl','PETSc'))
            modules['comm'] = SimpleNamespace(size=1)
            def load(_versions):
                if fail_at == 'pinned_import':
                    fail('pinned_import')
                calls.append('imports_returned_fake_modules')
                return modules, {}, {}
            def run_driver(*args, **kwargs):
                if fail_at == 'driver_entry':
                    fail('driver_entry')
                if fail_at == 'create_cube':
                    return driver.run_manufactured(*args, **kwargs)
                calls.append('driver_returned_fake_payload')
                return {}
            with TemporaryDirectory(prefix='navier-r259-fakes-') as parent, ExitStack() as stack:
                directory = Path(parent)
                manifest = directory/'manifest.json'
                manifest.write_text(json.dumps(expected()))
                values = {
                    'read_limited': lambda _p: {},
                    'validate_reservation': lambda *a: None,
                    'verify_source': lambda *a: {},
                    '_cgroup_path': lambda: '/injected-no-manager',
                    'held': lambda *a: calls.append('held_returned_fake_release'),
                    'load_pinned_modules': load,
                    'LatestSystem': lambda *a, **k: object(),
                    'run_manufactured': run_driver,
                    'write_limited_new': lambda *a: calls.append('fake_payload_saved'),
                    'completed': lambda *a: calls.append('fake_completion'),
                }
                for name, value in values.items():
                    stack.enter_context(patch.object(worker, name, value))
                stack.enter_context(patch.object(driver, 'create_cube', lambda *a: fail('create_cube')))
                stack.enter_context(patch.dict(worker.os.environ, {k:'1' for k in
                    ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}))
                stderr = io.StringIO()
                namespace = dict(__name__='__main__', sys=sys,
                    main=lambda: worker.main([str(directory), str(manifest)]))
                with redirect_stderr(stderr):
                    try:
                        exec(code, namespace)
                    except SystemExit as exc:
                        exit_code = exc.code
                    else:
                        raise AssertionError('worker entry must exit')
                expected_code = 0 if fail_at is None else 1
                assert exit_code == expected_code
                if fail_at is not None:
                    assert stderr.getvalue() == 'RecursionError: maximum recursion depth exceeded\n'
                    assert 'fake_payload_saved' not in calls and 'fake_completion' not in calls
                else:
                    assert not stderr.getvalue()
                    assert calls[-2:] == ['fake_payload_saved', 'fake_completion']
                assert sorted(p.name for p in directory.iterdir()) == ['manifest.json']
                cases.append(dict(injected_failure=fail_at, events=calls,
                                  exit_code=exit_code, stderr=stderr.getvalue()))
        raw = (ROOT/'docs/realizability/evidence/r258/run/worker.log').read_text()
        assert all(case['stderr'] == raw for case in cases[:3])
        loaded = sorted(name for name in sys.modules if name.split('.')[0] in FORBIDDEN)
        assert not loaded
        return dict(status='PASS', cases=cases, checks=4,
            three_distinct_sites_match_saved_log=True, successful_fake_path_checked=True,
            numerical_import_guard=True, numerical_modules_loaded=loaded,
            real_worker_or_manager=False, actual_r258_failure_site='undetermined',
            limitation='Injected control-flow proof; does not reproduce real FEM failure')
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    Path(__file__).with_name('probe.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
