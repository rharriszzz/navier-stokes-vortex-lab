"""R268 guarded source/fake tests and saved-result replays."""
from contextlib import redirect_stdout
import json
from pathlib import Path
import runpy
import sys
import time
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
OLD = runpy.run_path(str(HERE.parent/'r265/test_runner.py'))
MODULES = OLD['MODULES'] + ['test_manufactured_angular']
FORBIDDEN = OLD['FORBIDDEN']


def run():
    guard = OLD['NoNumericalImports']()
    sys.meta_path.insert(0, guard)
    began = time.monotonic()
    try:
        suite = unittest.defaultTestLoader.loadTestsFromNames(
            ['verification.nonlinear_port.'+name for name in MODULES])
        with (HERE/'tests.txt').open('w', encoding='utf-8') as stream, redirect_stdout(stream):
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        from verification.nonlinear_port.supervision import validate_worker_result
        from verification.nonlinear_port.rotation_driver import validate_worker_payload
        from verification.nonlinear_port.manufactured_report import build_report, validate_report
        from verification.nonlinear_port.prototype import Refusal
        read = lambda path: json.loads(path.read_text())
        old = read(ROOT/'verification/nonlinear_port/future_fem.json')
        r246 = read(HERE.parent/'r246/run/numerical.json')
        validate_worker_result(r246, old['versions'], old['gates'],
                               policy=old['poiseuille_diagnostic_policy'])
        r253 = HERE.parent/'r253/run'
        rotation = read(ROOT/'verification/nonlinear_port/future_rotation.json')
        r253_read = lambda name: read(r253/name)
        validate_worker_payload(r253_read('numerical.json'), rotation,
                                r253_read('reservation.json'), r253_read('admission.json'))
        proposal = read(ROOT/'verification/nonlinear_port/future_manufactured.json')
        numerical = read(HERE.parent/'r266/run/numerical.json')
        kwargs = dict(multipliers=numerical['multipliers'], eta=numerical['eta'],
            history=numerical['nonlinear_history'], corrections=numerical['linear_corrections'],
            minimum_normal=numerical['minimum_return_normal_velocity'],
            sample_counts=numerical['return_quadrature_sample_counts'],
            condition=numerical['constraint_condition'], compatibility=numerical['compatibility'],
            measured_targets=numerical['measured_targets'],
            lateral_absolute_flux=numerical['lateral_absolute_flux'])
        assert build_report(numerical['raw_by_degree'], proposal=proposal, **kwargs) == numerical['report']
        try:
            validate_report(numerical['report'], proposal, **kwargs)
        except Refusal as exc:
            assert str(exc) == 'failed or inconsistent manufactured evidence'
        else:
            raise AssertionError('R266 physical refusal lost')
        probe = runpy.run_path(str(HERE.parent/'r267/probe.py'))['run']()
        assert probe['decomposition_negative_controls'] == 4
        loaded = sorted(name for name in sys.modules if name.split('.')[0] in FORBIDDEN)
        record = dict(tests=result.testsRun, failures=len(result.failures),
            errors=len(result.errors), modules=MODULES, numerical_modules_loaded=loaded,
            saved_r246_validator='PASS', saved_r253_validator='PASS',
            saved_r266_validator='INCOMPLETE', r267_decomposition_controls=4,
            python=sys.version, executable=sys.executable,
            runner_seconds=time.monotonic()-began)
        (HERE/'tests.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
        print(json.dumps(record, sort_keys=True))
        return 0 if result.wasSuccessful() and result.testsRun == 123 and not loaded else 1
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    raise SystemExit(run())
