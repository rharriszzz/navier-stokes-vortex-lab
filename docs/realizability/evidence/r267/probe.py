"""R267 exact algebra and saved-scalar interpretation; no numerical imports."""
from fractions import Fraction as F
import json
from math import fsum, sqrt
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
FORBIDDEN = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}


class Guard:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in FORBIDDEN:
            raise AssertionError('R267 prohibits numerical import: ' + fullname)


def run():
    guard = Guard()
    sys.meta_path.insert(0, guard)
    try:
        from verification.nonlinear_port.polynomial import Poly, x, y, z, volume, face, dot
        from verification.nonlinear_port import fixtures
        from verification.nonlinear_port.sparse import CSR, border_and_lift
        from verification.nonlinear_port.manufactured_report import build_report, validate_report
        from verification.nonlinear_port.prototype import Refusal
        from verification.nonlinear_port.manufactured_driver import _validate_latest
        read = lambda p: json.loads(p.read_text())
        source = runpy.run_path(str(HERE.parent / 'r255/audit.py'))
        reference = source['manufactured_reference']()
        assert reference == read(HERE.parent / 'r255/proposal.json')['exact_reference']
        scalar = source['scalar']
        numerical = read(HERE.parent / 'r266/run/numerical.json')
        manifest = read(ROOT / 'verification/nonlinear_port/future_manufactured.json')
        kwargs = dict(multipliers=numerical['multipliers'], eta=numerical['eta'],
            history=numerical['nonlinear_history'], corrections=numerical['linear_corrections'],
            minimum_normal=numerical['minimum_return_normal_velocity'],
            sample_counts=numerical['return_quadrature_sample_counts'],
            condition=numerical['constraint_condition'], compatibility=numerical['compatibility'],
            measured_targets=numerical['measured_targets'],
            lateral_absolute_flux=numerical['lateral_absolute_flux'])
        assert build_report(numerical['raw_by_degree'], proposal=manifest, **kwargs) == numerical['report']
        try:
            validate_report(numerical['report'], manifest, **kwargs)
        except Refusal as exc:
            assert str(exc) == 'failed or inconsistent manufactured evidence'
        else:
            raise AssertionError('saved refusal lost')
        latest = read(HERE.parent / 'r266/run/linear_system.json')
        _validate_latest(latest, numerical, numerical['linear_corrections'][-1]['linear_system'])
        assert latest['stage'] == 'before_factorization' and latest['correction'] == 3
        assert 'final_state' not in numerical and 'raw_residual' not in numerical
        assert all(latest['rhs'][i] == 0 for i in latest['fixed_indices'])

        degrees = {}
        for degree, raw in numerical['raw_by_degree'].items():
            expected = {k: float(F(v)) for k, v in reference['angular_terms'].items()}
            terms = {k: raw['angular.' + k] for k in expected}
            differences = {k: terms[k] - expected[k] for k in expected}
            defect = fsum(terms.values())
            limit = max(1e-10, .01 * fsum(abs(v) for v in terms.values()))
            report = numerical['report']['degree_validation'][degree]
            assert defect == report['field_report']['angular_budget']['signed_defect']
            assert limit == report['field_report']['angular_budget']['limit']
            assert abs(fsum(differences.values()) - defect) < 1e-17
            l0 = float(F(reference['exact']['angular_initial']))
            endpoint = (raw['angular_momentum'] - l0) / .125
            interval = fsum([raw['angular_momentum'] - l0,
                            *(.125 * terms[k] for k in ('advective', 'traction', 'body'))])
            assert interval == report['interval_budgets']['angular']['defect']
            assert abs(interval - .125 * defect) < 1e-16
            assert abs(endpoint - terms['storage']) < 1e-12
            degrees[degree] = dict(terms=terms, exact_terms=expected,
                errors_against_exact_field=differences, defect=defect, limit=limit,
                failure_ratio=abs(defect)/limit, interval_defect=interval,
                interval_minus_dt_rate=interval-.125*defect,
                endpoint_minus_storage=endpoint-terms['storage'],
                inferred_uneliminated_action=fsum(terms[k] for k in ('storage', 'advective', 'body')),
                physical_total_torque=-terms['traction'],
                cap_torque_error_cauchy_bound=sqrt(F(4, 3)*raw['traction_L2_returns_squared']))

        # Rigid angular virtual velocity is P1, but not an admissible zero trace test.
        phi = [-y, x, Poly()]
        grad = [[v.d(j) for j in range(3)] for v in phi]
        assert all(grad[i][j] + grad[j][i] == 0 for i in range(3) for j in range(3))
        assert sum(phi[i].d(i) for i in range(3)) == 0
        assert all(sum(face(v*v, a, s) for v in phi) != 0
                   for a in (0, 1) for s in (0, 1))
        u_all, p_all = fixtures.manufactured()
        u = [v.at(3, F(1, 8)) for v in u_all]
        p = p_all.at(3, F(1, 8))
        ad = sum(face(dot(phi, u)*(2*s-1)*u[a], a, s)
                 for a in (0, 1) for s in (0, 1))
        assert ad == 0
        for s in (0, 1):
            _, pressure, offset = fixtures.return_data(s)
            prescribed = [offset[i].at(3, F(1, 8)) -
                          (pressure.at(3, F(1, 8))*(2*s-1) if i == 2 else 0)
                          for i in range(3)]
            assert dot(phi, prescribed) == 0
        # No angular div(u) correction is missing for conservative convection.
        # Use a deliberately non-solenoidal smooth field, distinct from the fixture.
        test_u, test_p = [x*y, y*z, z*x], x+y+z
        sigma = fixtures.stress(test_u, test_p)
        conv = [sum((test_u[i]*test_u[j]).d(j) for j in range(3)) for i in range(3)]
        div_sigma = [sum(sigma[i][j].d(j) for j in range(3)) for i in range(3)]
        force = [conv[i]-div_sigma[i] for i in range(3)]
        boundary = lambda fun: sum(face(fun(a, 2*s-1), a, s)
                                   for a in range(3) for s in (0, 1))
        adv = boundary(lambda a, n: dot(phi, test_u)*n*test_u[a])
        tr = -boundary(lambda a, n: dot(phi, [n*sigma[i][a] for i in range(3)]))
        body = -volume(dot(phi, force))
        assert adv+tr+body == 0
        divu = sum(test_u[i].d(i) for i in range(3))
        extra = volume(dot(phi, test_u)*divu)
        assert extra != 0
        # Symmetric tensor / skew gradient contractions vanish pointwise.
        assert sum(test_u[i]*test_u[j]*grad[i][j] for i in range(3) for j in range(3)) == 0
        assert sum(sigma[i][j]*grad[i][j] for i in range(3) for j in range(3)) == 0

        # Fixed-row elimination erases reaction information: two raw residuals
        # produce identical retained systems yet different angular actions.
        core = CSR.from_rows([{0: 2., 1: 1.}, {0: 1., 1: 3.}])
        common = ([0., 0.],)*3
        a = border_and_lift(core, common, common, [2., 0.], [0.]*3, [1., 0., 0., 0., 0.], {0: 1.})
        b = border_and_lift(core, common, common, [7., 0.], [0.]*3, [1., 0., 0., 0., 0.], {0: 1.})
        assert a == b and a[0] == [0.]*5
        # Exact finite-dimensional decomposition and sign/partition controls.
        rf, ru, ad, ar, cd, cr, gp = map(F, ('2', '1/8', '3/7', '5/9', '-4/5', '2/3', '-1/11'))
        action = rf+ru
        storage_body = action-ar-gp
        physical = storage_body+ad+ar+cd+cr
        reconstructed = rf+ad+cd+(cr-gp)+ru
        assert physical == reconstructed
        assert all(value != physical for value in (
            rf+cd+(cr-gp)+ru, rf+ad+cd+(cr+gp)+ru,
            rf+ad+cd+(cr-gp), -rf+ad+cd+(cr-gp)+ru))
        loaded = sorted(n for n in sys.modules if n.split('.')[0] in FORBIDDEN)
        assert not loaded
        return dict(status='SOURCE_REVIEW_COMPLETE_NO_ADMISSION',
            degrees=degrees, exact_reference_rederived=True,
            saved_full_report_rebuilt=True, saved_validator_refuses=True,
            latest_system_validated=True, latest_state_is_pre_correction=True,
            fixed_rows_erased=len(latest['fixed_indices']),
            angular_test_nonzero_on_all_lateral_faces=True,
            exact_lateral_advective_torque='0', prescribed_return_torque='0',
            non_solenoidal_conservative_identity='0',
            erroneous_extra_angular_divergence_term=str(scalar(extra)),
            fixed_row_information_loss_demonstrated=True,
            decomposition_negative_controls=4,
            maximum_degree_term_difference=max(abs(degrees['26']['terms'][k]-degrees['24']['terms'][k])
                                               for k in degrees['24']['terms']),
            numerical_modules_loaded=loaded, runtime_source_changes=0,
            cause_limit='Boundary reaction versus surface-stress split is not recorded; no corrective solver change is justified.')
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    (HERE / 'probe.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
