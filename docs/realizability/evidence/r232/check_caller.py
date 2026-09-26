"""Import and timer regression checks for the R231 finite caller; no FEM or manager."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import runpy
import signal
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
CALLER = ROOT/'docs/realizability/evidence/r231/run_once.py'
NUMERICAL = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py'}


def loaded_numerical():
    return {name for name in NUMERICAL if name in sys.modules}


def main():
    assert not loaded_numerical(), 'unexpected numerical module before test'
    original_cwd = Path.cwd()
    original_argv = sys.argv
    try:
        with tempfile.TemporaryDirectory() as other:
            os.chdir(other)
            namespace = runpy.run_path(str(CALLER), run_name='r232_caller_check')
            supervise_once, backend, bus = namespace['load_components']()
            assert callable(supervise_once) and callable(backend) and callable(bus)
            assert not loaded_numerical(), 'project import loaded a numerical module'
            globals_ = namespace['main'].__globals__
            reached = []

            def checked_preflight(commit, bus_type):
                remaining, _ = signal.getitimer(signal.ITIMER_REAL)
                assert commit == '0'*40 and remaining > 0
                reached.append('timer active before preflight')
                raise RuntimeError('test-only preflight refusal')

            globals_['preflight'] = checked_preflight
            globals_['load_components'] = lambda: (supervise_once, backend, bus)
            sys.argv = [str(CALLER), '0'*40]
            output = io.StringIO()
            with redirect_stdout(output):
                code = namespace['main']()
            record = json.loads(output.getvalue())
            assert code == 1 and record['status'] == 'INCOMPLETE'
            assert record['reason'] == 'RuntimeError: test-only preflight refusal'
            assert reached == ['timer active before preflight']
            assert signal.getitimer(signal.ITIMER_REAL)[0] == 0
            assert not Path(record['run_directory']).exists()
            assert not loaded_numerical(), 'test loaded a numerical module'
    finally:
        sys.argv = original_argv
        os.chdir(original_cwd)
    print('caller path imports and outer timer: PASS; no manager/FEM/reservation')


if __name__ == '__main__':
    main()
