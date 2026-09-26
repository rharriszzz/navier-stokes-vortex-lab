"""R237 caller checks: standard library only, no manager or reservation."""
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
CALLER = Path(__file__).with_name('run_once.py')
NUMERICAL = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py'}


def main():
    cwd, argv = Path.cwd(), sys.argv
    original_timer = signal.getsignal(signal.SIGALRM)
    assert not signal.getitimer(signal.ITIMER_REAL)[0]
    assert not NUMERICAL.intersection(sys.modules)
    try:
        with tempfile.TemporaryDirectory() as other:
            os.chdir(other)
            namespace = runpy.run_path(str(CALLER), run_name='r237_caller_check')
            g = namespace['main'].__globals__
            run = g['RUN']
            assert run == Path('/tmp/navier-poiseuille-r237-once')
            assert not run.exists() and not run.is_symlink()
            assert g['INVENTORY'] == ROOT/'docs/realizability/evidence/r236/checks.json'
            original_load = g['load_components']
            original_preflight = g['preflight']
            reached = []

            def checked_load():
                assert signal.getitimer(signal.ITIMER_REAL)[0] > 0
                reached.append('timer before project imports')
                return original_load()

            def refuse(commit, bus):
                assert commit == '0'*40 and signal.getitimer(signal.ITIMER_REAL)[0] > 0
                reached.append('timer before preflight')
                raise RuntimeError('test-only preflight refusal')

            g['load_components'], g['preflight'] = checked_load, refuse
            sys.argv = [str(CALLER), '0'*40]
            output = io.StringIO()
            with redirect_stdout(output):
                code = namespace['main']()
            record = json.loads(output.getvalue())
            assert code == 1 and record['status'] == 'INCOMPLETE'
            assert record['reason'] == 'RuntimeError: test-only preflight refusal'
            assert reached == ['timer before project imports', 'timer before preflight']
            assert signal.getitimer(signal.ITIMER_REAL)[0] == 0

            # Exercise real preflight refusals with synthetic clean Git answers.
            # All cases must fail before a manager connection or reservation.
            def no_bus():
                raise AssertionError('manager connection must not be reached')

            replies = {('rev-parse', 'HEAD'): '0'*40,
                       ('status', '--porcelain', '--untracked-files=all'): '',
                       ('rev-parse', '--show-toplevel'): str(ROOT)}
            g['git'] = lambda *args: replies[args]

            def expect_refusal(fragment):
                try:
                    original_preflight('0'*40, no_bus)
                except RuntimeError as exc:
                    assert fragment in str(exc), str(exc)
                else:
                    raise AssertionError('preflight should refuse')

            inventory = g['INVENTORY']
            altered = json.loads(inventory.read_text())
            altered['source_sha256']['verification/nonlinear_port/cube_adapter.py'] = '0'*64
            synthetic = Path(other)/'changed_inventory.json'
            synthetic.write_text(json.dumps(altered))
            g['INVENTORY'] = synthetic
            expect_refusal('reviewed source or frozen manifest changed')
            g['INVENTORY'] = inventory
            g['RUN'] = Path(other)
            expect_refusal('one-use output directory already exists')
            g['RUN'] = Path(other)/'dangling'
            g['RUN'].symlink_to(Path(other)/'missing')
            expect_refusal('one-use output directory already exists')
            assert not run.exists() and not run.is_symlink()
            assert not NUMERICAL.intersection(sys.modules)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, original_timer)
        os.chdir(cwd)
        sys.argv = argv
    print('PASS: outside-directory imports, timer before imports/preflight, changed-source and existing/symlink-directory refusals; no numerical modules/manager/reservation')


if __name__ == '__main__':
    main()
