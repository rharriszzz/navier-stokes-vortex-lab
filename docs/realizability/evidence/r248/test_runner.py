"""R248 stdlib regression and import audit; no numerical packages."""
import json
import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
MODULES = [
    'test_adapter', 'test_algebra', 'test_driver_supervision',
    'test_driver_wiring', 'test_host_protocol', 'test_linear_evidence',
    'test_package_identity', 'test_poiseuille_policy',
    'test_rotation_oracle', 'test_source_bus',
]
start = time.monotonic()
suite = unittest.defaultTestLoader.loadTestsFromNames(
    ['verification.nonlinear_port.' + name for name in MODULES])
with (Path(__file__).with_name('tests.txt')).open('w') as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
loaded = sorted(name for name in ('numpy', 'dolfinx', 'basix', 'ufl', 'ffcx',
                                   'petsc4py', 'mpi4py', 'scipy') if name in sys.modules)
record = dict(count=result.testsRun, failures=len(result.failures),
              errors=len(result.errors), numerical_modules_loaded=loaded,
              python=sys.version, executable=sys.executable,
              runner_seconds=time.monotonic()-start,
              modules=['verification.nonlinear_port.'+n for n in MODULES])
Path(__file__).with_name('tests.json').write_text(
    json.dumps(record, indent=2, sort_keys=True)+'\n')
if not result.wasSuccessful() or loaded:
    raise SystemExit(1)
print(json.dumps(record, sort_keys=True))
