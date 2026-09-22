"""Retain import-free R196 results; does not import, mesh or run a FEM backend."""
from pathlib import Path
import hashlib
import io
import json
import platform
import sys
import unittest

root = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(root))
output = Path(__file__).resolve().parent
stream = io.StringIO()
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in
                          ('verification.nonlinear_port.test_algebra', 'verification.nonlinear_port.test_adapter'))
result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
text = stream.getvalue()
(output / 'algebra_checks.txt').write_text(text)
forbidden = sorted({'ufl', 'dolfinx', 'basix', 'petsc4py', 'mpi4py', 'numpy', 'sympy'} & set(sys.modules))
passed = result.wasSuccessful() and not forbidden
sources = sorted((root / 'verification/nonlinear_port').glob('*.py'))
sources.append(root / 'verification/nonlinear_port/future_fem.json')
record = dict(request='R196', python=platform.python_version(), tests_run=result.testsRun,
              failures=len(result.failures), errors=len(result.errors), passed=passed,
              forbidden_imports=forbidden, fem_executed=False, execution_admitted=False,
              attempts_granted=0, scope='source and standard-library algebra only',
              source_sha256={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources})
(output / 'checks.json').write_text(json.dumps(record, indent=2)+'\n')
print(text, end='')
raise SystemExit(0 if passed else 1)
