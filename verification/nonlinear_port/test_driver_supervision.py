"""Import-free driver decisions and finite supervision failure paths."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from .fixture_driver import nonexact_guess, numerical_decision, return_quadrature_samples
from .diagnostics import ANGULAR_TERMS, ENERGY_TERMS, field_report
from .prototype import Refusal
from .supervision import supervise_once, verify_held_scope, validate_worker_result
from .worker import verify_release


MANIFEST = Path(__file__).with_name('future_fem.json')
SOURCE = 'a'*40


def admission():
    return dict(approved=True, fixture='poiseuille', attempts_granted=1,
                source_commit=SOURCE,
                manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest())


def payload():
    versions = json.loads(MANIFEST.read_text())['versions']
    gates = json.loads(MANIFEST.read_text())['gates']
    values = dict(volume=1., pressure_mean=0., p_error_integral=0., p_error_squared=0.,
                  flux_0=0., flux_1=0., area_0=1., area_1=1., lateral_flux=0.,
                  boundary_absolute_flux=1., energy_identity_storage=0.,
                  energy_identity_dissipation=0., kinetic_discrete_derivative=0.)
    values.update({k+'_squared': 0. for k in
                   ('u_L2', 'u_H1_seminorm', 'div_u_L2', 'traction_L2_returns')})
    values.update({'angular.'+k: 0. for k in ANGULAR_TERMS})
    values.update({'energy.'+k: 0. for k in ENERGY_TERMS})
    report = field_report(values, [0., 0.], [0., 0.], [0., 0.], 0.)
    comparison = {k: {'accepted': True} for k in values}
    checked = {'numerical_step_accepted': True}
    decision = numerical_decision(report, checked, comparison, 1, gates)
    return dict(fixture='poiseuille', subdivisions=2, numerical_accepted=True,
                checks=decision['checks'], compatibility={'defect': 0., 'limit': 1e-12},
                constraint_condition={'condition_bound': 2.}, nonlinear_history=[1., 1e-12],
                linear_corrections=[{'true_residual': 0., 'rhs_norm': 1.}],
                return_quadrature_sample_counts=[6, 6], minimum_return_normal_velocity=0.,
                diagnostics_degree24=report, diagnostics_degree26=values,
                quadrature_comparison=comparison,
                step_checks=checked,
                phase_seconds=dict(mesh_and_lift=0., primary_form_setup_jit=0.,
                                   compatibility_rank_newton=0.,
                                   diagnostic_form_jit_assembly_sampling=0.),
                worker_intervals={'import_seconds': 0.,
                                  'fixture_setup_jit_and_solve_seconds': 0.},
                actual_versions=versions)


class Clock:
    def __init__(self):
        self.value = 0.

    def __call__(self):
        return self.value


class FakeHandle:
    scope_id = '/user.slice/fixture.scope'

    def __init__(self, directory, clock, *, write_result=True, cleanup_ok=True,
                 exit_code=0, work_seconds=1.):
        self.directory, self.clock = directory, clock
        self.write_result, self.cleanup_ok = write_result, cleanup_ok
        self.exit_code, self.work_seconds = exit_code, work_seconds
        self.released = False

    def facts(self):
        return dict(cgroup_path=self.scope_id, memory_max_bytes=1536*1024**2,
                    swap_max_bytes=0, pids_max=32, independent_expiry_seconds=150,
                    worker_held=True, all_task_processes_in_scope=True,
                    mpi_ranks=1, threads=1)

    def release(self):
        self.released = True

    def wait(self, timeout):
        assert timeout == 150 and self.released
        self.clock.value += self.work_seconds
        if self.write_result:
            (self.directory/'numerical.json').write_text(json.dumps(payload()))
        return {'exit_code': self.exit_code}

    def stop(self):
        self.stopped = True

    def cleanup(self):
        return dict(empty=self.cleanup_ok, unknown_children=not self.cleanup_ok,
                    memory_peak_bytes=1024, memory_events={'oom': 0, 'oom_kill': 0}, pids_peak=1)


class FakeBackend:
    def __init__(self, clock, **kwargs):
        self.clock, self.kwargs, self.handle = clock, kwargs, None

    def start_held(self, command, directory, caps):
        self.handle = FakeHandle(directory, self.clock, **self.kwargs)
        return self.handle


class DriverSupervisionChecks(unittest.TestCase):
    def test_return_samples_cover_both_tagged_caps_with_outward_signs(self):
        class Vec(tuple):
            def __mul__(self, scalar):
                return Vec(v*scalar for v in self)

            __rmul__ = __mul__

            def __add__(self, other):
                return Vec(a+b for a, b in zip(self, other))

        class Coordinates:
            def __init__(self):
                self.nodes = [Vec(v) for v in ((0, 0, 0), (1, 0, 0), (0, 1, 0),
                                               (0, 0, 1), (1, 0, 1), (0, 1, 1))]

            def __getitem__(self, indices):
                return [self.nodes[i] for i in indices]

        class Mesh:
            entities_to_geometry = staticmethod(lambda domain, dim, facets:
                                                 [[0, 1, 2] if int(f) == 5 else [3, 4, 5]
                                                  for f in facets])

        class Tags:
            find = staticmethod(lambda tag: [tag])

        class Connectivity:
            links = staticmethod(lambda facet: [facet-5])

        class Topology:
            dim = 3
            create_connectivity = staticmethod(lambda a, b: None)
            connectivity = staticmethod(lambda a, b: Connectivity())

        class Domain:
            topology = Topology()
            geometry = type('Geometry', (), {'x': Coordinates()})()

        class Velocity:
            eval = staticmethod(lambda points, cells: [[0., 0., .1 if cell == 0 else .2]
                                                        for cell in cells])

        array = type('Array', (), {'int32': int, 'asarray': staticmethod(lambda value, dtype=None: value)})()
        basix = type('Basix', (), {'CellType': type('CellType', (), {'triangle': 'triangle'}),
                                   'make_quadrature': staticmethod(lambda cell, degree:
                                                                   ([(1/3, 1/3)], [.5]))})()
        values, counts = return_quadrature_samples(array, Mesh(), basix, Domain(),
                                                    Tags(), Velocity(), 24)
        self.assertEqual(values, [-.1, .2])
        self.assertEqual(counts, [1, 1])

    def test_free_velocity_perturbation_preserves_trace(self):
        guess, dof = nonexact_guess([2., 3., 4., 5.], [0, 1, 2], {0: 2., 2: 4.})
        self.assertEqual(dof, 1)
        self.assertEqual(guess, [2., 3.05, 4., 5.])
        with self.assertRaises(Refusal):
            nonexact_guess([2.], [0], {0: 2.})

    def test_complete_oracle_decision_and_missing_correction(self):
        report = dict(u_L2=0., p_L2_mean_zero=0., div_u_L2=0.,
                      traction_L2_returns=0., multiplier_errors=[0., 0.],
                      both_flux_errors=[0., 0.])
        checked = {'numerical_step_accepted': True}
        comparison = {'x': {'accepted': True}}
        gates = {'flux_gauge_eta_absolute': 1e-10}
        self.assertTrue(numerical_decision(report, checked, comparison, 1, gates)['numerical_accepted'])
        self.assertFalse(numerical_decision(dict(report, u_L2=2e-9), checked,
                                             comparison, 1, gates)['numerical_accepted'])
        with self.assertRaises(Refusal):
            numerical_decision(report, checked, comparison, 0, gates)

    def test_held_scope_refuses_missing_or_inexact_enforcement(self):
        facts = FakeHandle(Path('.'), Clock()).facts()
        self.assertEqual(verify_held_scope(facts, facts['cgroup_path']), facts)
        for changed in (dict(facts, swap_max_bytes=1),
                        dict(facts, worker_held=False),
                        dict(facts, cgroup_path='/')):
            with self.assertRaises(Refusal):
                verify_held_scope(changed, '/user.slice/fixture.scope')

    def test_no_admission_no_reservation_or_backend_call(self):
        with TemporaryDirectory() as base:
            path = Path(base)/'run'
            backend = FakeBackend(Clock())
            with self.assertRaises(Refusal):
                supervise_once(path, MANIFEST, None, backend,
                               source_commit=SOURCE, interpreter='python', owner='daisy')
            self.assertFalse(path.exists())
            self.assertIsNone(backend.handle)

    def test_mock_complete_path_and_prior_reservation_refusal(self):
        with TemporaryDirectory() as base:
            path = Path(base)/'run'
            clock = Clock()
            backend = FakeBackend(clock)
            result = supervise_once(path, MANIFEST, admission(), backend,
                                    source_commit=SOURCE, interpreter='python',
                                    owner='daisy', monotonic=clock)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(json.loads((path/'result.json').read_text())['status'], 'PROVISIONAL_PASS')
            self.assertEqual(json.loads((path/'completion.json').read_text())['status'], 'PASS')
            self.assertTrue(backend.handle.stopped)
            with self.assertRaises(FileExistsError):
                supervise_once(path, MANIFEST, admission(), backend,
                               source_commit=SOURCE, interpreter='python',
                               owner='daisy', monotonic=clock)

    def test_missing_worker_result_late_or_unknown_cleanup_refused(self):
        for kwargs in ({'write_result': False}, {'cleanup_ok': False},
                       {'exit_code': 1}, {'work_seconds': 151.}):
            with self.subTest(kwargs=kwargs), TemporaryDirectory() as base:
                path = Path(base)/'run'
                clock = Clock()
                result = supervise_once(path, MANIFEST, admission(), FakeBackend(clock, **kwargs),
                                        source_commit=SOURCE,
                                        interpreter='python', owner='daisy', monotonic=clock)
                self.assertEqual(result['status'], 'INCOMPLETE')
                self.assertIn('reason', result)
                self.assertTrue((path/'reservation.json').exists())

    def test_incomplete_payload_does_not_accept_field_report(self):
        valid = payload()
        self.assertEqual(validate_worker_result(valid), valid)
        for bad in (dict(valid, numerical_accepted=False),
                    dict(valid, linear_corrections=[]),
                    dict(valid, minimum_return_normal_velocity=-1e-7),
                    {'diagnostics_degree24': valid['diagnostics_degree24']}):
            with self.assertRaises(Refusal):
                validate_worker_result(bad)

    def test_worker_release_requires_reserved_nonce_and_own_scope(self):
        reservation = {'release_nonce': 'abc'}
        verify_release('RELEASE abc /user.slice/fixture.scope\n', reservation,
                       '/user.slice/fixture.scope')
        for line in ('RELEASE wrong /user.slice/fixture.scope\n',
                     'RELEASE abc /other.scope\n', 'RELEASE abc /\n', ''):
            with self.assertRaises(Refusal):
                verify_release(line, reservation, '/user.slice/fixture.scope')


if __name__ == '__main__':
    unittest.main()
