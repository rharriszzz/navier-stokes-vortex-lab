"""R256 source-only regressions and saved PASS replay; no numerical imports."""
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
MODULES = [
    'test_adapter', 'test_algebra', 'test_driver_supervision',
    'test_driver_wiring', 'test_host_protocol', 'test_linear_evidence',
    'test_package_identity', 'test_poiseuille_policy',
    'test_rotation_oracle', 'test_rotation_integration', 'test_source_bus',
    'test_manufactured_integration',
]


def main():
    from verification.nonlinear_port.supervision import validate_worker_result
    from verification.nonlinear_port.rotation_driver import validate_worker_payload

    started = time.monotonic()
    suite = unittest.defaultTestLoader.loadTestsFromNames(
        ['verification.nonlinear_port.'+name for name in MODULES])
    with (HERE/'tests.txt').open('w', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    old = json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
    r246 = json.loads((ROOT/'docs/realizability/evidence/r246/run/numerical.json').read_text())
    validate_worker_result(r246, old['versions'], old['gates'],
                           policy=old['poiseuille_diagnostic_policy'])
    r253 = ROOT/'docs/realizability/evidence/r253/run'
    rotation = json.loads((ROOT/'verification/nonlinear_port/future_rotation.json').read_text())
    saved = lambda name: json.loads((r253/name).read_text())
    validate_worker_payload(saved('numerical.json'), rotation,
                            saved('reservation.json'), saved('admission.json'))
    loaded = sorted(name for name in ('numpy', 'dolfinx', 'basix', 'ufl', 'ffcx',
        'petsc4py', 'mpi4py', 'scipy') if name in sys.modules)
    record = dict(tests=result.testsRun, failures=len(result.failures),
        errors=len(result.errors), numerical_modules_loaded=loaded,
        saved_r246_validator='PASS', saved_r253_validator='PASS',
        python=sys.version, executable=sys.executable,
        runner_seconds=time.monotonic()-started,
        modules=['verification.nonlinear_port.'+name for name in MODULES])
    (HERE/'tests.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
    print(json.dumps(record, sort_keys=True))
    return 0 if result.wasSuccessful() and not loaded else 1


if __name__ == '__main__':
    raise SystemExit(main())
