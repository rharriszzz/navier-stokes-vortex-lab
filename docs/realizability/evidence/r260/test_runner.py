"""R260 full standard-library/injected-fake suite and saved PASS replay."""
from contextlib import redirect_stdout
import json
from pathlib import Path
import runpy
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
OLD = ROOT/'docs/realizability/evidence/r257'
MODULES = runpy.run_path(str(OLD/'test_runner.py'))['MODULES'] + ['test_manufactured_failure']
FORBIDDEN = {'numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy'}


class NoNumericalImports:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in FORBIDDEN:
            raise AssertionError('R260 prohibits numerical import: '+fullname)


def run():
    from verification.nonlinear_port.supervision import validate_worker_result
    from verification.nonlinear_port.rotation_driver import validate_worker_payload
    guard=NoNumericalImports()
    sys.meta_path.insert(0,guard)
    started=time.monotonic()
    try:
        suite=unittest.defaultTestLoader.loadTestsFromNames(
            ['verification.nonlinear_port.'+name for name in MODULES])
        with (HERE/'tests.txt').open('w',encoding='utf-8') as stream,redirect_stdout(stream):
            result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
        old=json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
        r246=json.loads((ROOT/'docs/realizability/evidence/r246/run/numerical.json').read_text())
        validate_worker_result(r246,old['versions'],old['gates'],
                               policy=old['poiseuille_diagnostic_policy'])
        r253=ROOT/'docs/realizability/evidence/r253/run'
        rotation=json.loads((ROOT/'verification/nonlinear_port/future_rotation.json').read_text())
        read=lambda name:json.loads((r253/name).read_text())
        validate_worker_payload(read('numerical.json'),rotation,
                                read('reservation.json'),read('admission.json'))
        r258=runpy.run_path(str(ROOT/'docs/realizability/evidence/r258/audit.py'))['run']()
        assert r258['status']=='INCOMPLETE' and r258['attempts_spent']==1
        loaded=sorted(name for name in sys.modules if name.split('.')[0] in FORBIDDEN)
        record=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                    numerical_modules_loaded=loaded,saved_r246_validator='PASS',
                    saved_r253_validator='PASS',saved_r258_status='INCOMPLETE',
                    saved_r258_raw_files=r258['raw_files'],
                    python=sys.version,executable=sys.executable,
                    runner_seconds=time.monotonic()-started,
                    modules=['verification.nonlinear_port.'+name for name in MODULES])
        (HERE/'tests.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
        print(json.dumps(record,sort_keys=True))
        return 0 if result.wasSuccessful() and not loaded and result.testsRun==113 else 1
    finally:
        sys.meta_path.remove(guard)


if __name__=='__main__':
    raise SystemExit(run())
