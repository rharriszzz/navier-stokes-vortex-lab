"""R264 source/fake regressions and saved-result replay; no numerical imports."""
from contextlib import redirect_stdout
import json
from pathlib import Path
import runpy
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
MODULES = runpy.run_path(str(HERE.parent/'r261/test_runner.py'))['MODULES'] + [
    'test_balanced_polynomial']
FORBIDDEN = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}


class NoNumericalImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in FORBIDDEN:
            raise AssertionError('R264 prohibits numerical import: '+fullname)


def run():
    guard = NoNumericalImports()
    sys.meta_path.insert(0, guard)
    started = time.monotonic()
    try:
        suite = unittest.defaultTestLoader.loadTestsFromNames(
            ['verification.nonlinear_port.'+name for name in MODULES])
        with (HERE/'tests.txt').open('w', encoding='utf-8') as stream, redirect_stdout(stream):
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        from verification.nonlinear_port.supervision import validate_worker_result
        from verification.nonlinear_port.rotation_driver import validate_worker_payload
        old = json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
        r246 = json.loads((HERE.parent/'r246/run/numerical.json').read_text())
        validate_worker_result(r246, old['versions'], old['gates'],
                               policy=old['poiseuille_diagnostic_policy'])
        r253 = HERE.parent/'r253/run'
        rotation = json.loads((ROOT/'verification/nonlinear_port/future_rotation.json').read_text())
        read = lambda name: json.loads((r253/name).read_text())
        validate_worker_payload(read('numerical.json'), rotation,
                                read('reservation.json'), read('admission.json'))
        reference = runpy.run_path(str(HERE.parent/'r255/audit.py'))['manufactured_reference']()
        assert reference == json.loads((HERE.parent/'r255/proposal.json').read_text())['exact_reference']
        loaded = sorted(name for name in sys.modules if name.split('.')[0] in FORBIDDEN)
        record = dict(tests=result.testsRun, failures=len(result.failures),
                      errors=len(result.errors), numerical_modules_loaded=loaded,
                      saved_r246_validator='PASS', saved_r253_validator='PASS',
                      rational_r255_reference_rederived=True,
                      python=sys.version, executable=sys.executable,
                      runner_seconds=time.monotonic()-started,
                      modules=['verification.nonlinear_port.'+name for name in MODULES])
        (HERE/'tests.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
        print(json.dumps(record, sort_keys=True))
        return 0 if result.wasSuccessful() and not loaded and result.testsRun == 118 else 1
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    raise SystemExit(run())
