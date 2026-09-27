"""R271 rational reference and saved-array interpretation; no numerical imports."""
from fractions import Fraction as F
import json
from math import fsum, sqrt
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
OLD = runpy.run_path(str(HERE.parent / 'r267/probe.py'))


def run():
    guard = OLD['Guard']()
    sys.meta_path.insert(0, guard)
    try:
        from verification.nonlinear_port import fixtures
        from verification.nonlinear_port.polynomial import Poly, x, y, face, dot
        from verification.nonlinear_port.manufactured_angular import (
            strict_json, validate_record, validate_numerical_aliases)
        from verification.nonlinear_port.manufactured_report import build_report, validate_report
        from verification.nonlinear_port.prototype import Refusal
        from verification.nonlinear_port.supervision import validate_worker_result
        from verification.nonlinear_port.rotation_driver import validate_worker_payload
        read = lambda p: json.loads(p.read_text())
        old = OLD['run']()
        assert old['decomposition_negative_controls'] == 4
        saved_check = runpy.run_path(str(HERE.parent / 'r270/verify_saved.py'))['run']()
        assert saved_check == read(HERE.parent / 'r270/verification.json')
        numerical = read(HERE.parent / 'r270/run/numerical.json')
        side = strict_json((HERE.parent / 'r270/run/angular_audit.json').read_bytes())
        validate_record(side, numerical['source_binding'])
        validate_numerical_aliases(side, numerical, numerical['source_binding'])
        proposal = read(ROOT / 'verification/nonlinear_port/future_manufactured.json')
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
            raise AssertionError('R270 refusal lost')
        prior = read(HERE.parent / 'r266/run/numerical.json')
        assert numerical['raw_by_degree'] == prior['raw_by_degree']
        assert numerical['multipliers'] == prior['multipliers']
        assert numerical['nonlinear_history'] == prior['nonlinear_history']

        oracle = runpy.run_path(str(HERE.parent / 'r255/audit.py'))
        reference = oracle['manufactured_reference']()
        assert reference == proposal['exact_reference']
        scalar = oracle['scalar']
        ua, pa = fixtures.manufactured()
        u, p = [v.at(3, F(1, 8)) for v in ua], pa.at(3, F(1, 8))
        sigma = fixtures.stress(u, p)
        phi = [-y, x, Poly()]
        parts = {}
        for label, axes in [('D', (0, 1)), ('R', (2,))]:
            parts['A_' + label] = scalar(sum(face(dot(phi, u)*(2*s-1)*u[a], a, s)
                for a in axes for s in (0, 1)))
            parts['C_' + label] = scalar(-sum(face(dot(phi,
                [(2*s-1)*sigma[i][a] for i in range(3)]), a, s)
                for a in axes for s in (0, 1)))
        gr = Poly()
        for s in (0, 1):
            _, pressure, offset = fixtures.return_data(s)
            traction = [offset[i] - (pressure*(2*s-1) if i == 2 else 0) for i in range(3)]
            assert dot(phi, traction) == 0
            gr -= face(dot(phi, traction).at(3, F(1, 8)), 2, s)
        parts['G_R'] = scalar(gr)
        assert parts['A_D'] == parts['C_R'] == parts['G_R'] == 0
        parts['reaction_torque_D'] = -parts['C_D']
        exact = {k: float(v) for k, v in parts.items()}
        exact_terms = {k: float(F(v)) for k, v in reference['angular_terms'].items()}

        fixed = set(side['fixed_indices'])
        vm = side['phi']['velocity_parent_map']
        coords = side['phi']['velocity_node_coordinates']
        expected_fixed, nodal_errors = set(), []
        for j, xyz in enumerate(coords):
            # Affine n=2 P2 nodes lie on the quarter grid; tabulation has ulp noise.
            grid = [round(4*v)/4 for v in xyz]
            assert all(abs(a-b) < 1e-14 for a, b in zip(xyz, grid))
            lateral = any(grid[a] in (0., 1.) for a in (0, 1))
            for c in range(3):
                index = vm[3*j+c]
                truth = u[c].evaluate([*xyz, 0.])
                error = side['state'][index] - truth
                nodal_errors.append((index, error, lateral))
                if lateral:
                    expected_fixed.add(index)
                    assert abs(error) < 1e-14
        assert expected_fixed == fixed
        degrees = {}
        for degree, entry in side['degrees'].items():
            coefficients, residual = side['phi']['coefficients'], entry['raw_residual']
            rd = fsum(coefficients[i]*residual[i] for i in sorted(fixed))
            rf = fsum(coefficients[i]*residual[i] for i in range(402) if i not in fixed)
            s = entry['scalar']
            reaction = fsum((rd, s['A_D']))
            errors = {k: s[k]-exact[k] for k in ('A_D', 'A_R', 'C_D', 'C_R', 'G_R')}
            errors['reaction_torque_D'] = reaction-exact['reaction_torque_D']
            original = entry['original']
            term_errors = {k: original[k]-exact_terms[k] for k in exact_terms}
            reaction_prediction = fsum((term_errors['storage'], term_errors['body'],
                                       errors['A_D'], errors['A_R'], errors['G_R'], -rf))
            assert abs(errors['reaction_torque_D']-reaction_prediction) < 1e-12
            lateral = fsum((reaction, s['C_D']))
            returns = s['C_R']-s['G_R']
            defect = original['physical_defect']
            assert abs(fsum((errors['reaction_torque_D'], errors['C_D']))-lateral) < 1e-15
            assert abs(fsum((lateral, returns, rf))-defect) < 1e-12
            budget = numerical['report']['degree_validation'][degree]['field_report']['angular_budget']
            # Counterfactual arithmetic only; these do not change any saved report.
            counterfactual = dict(return_mismatch_zero=fsum((lateral, rf)),
                exact_lateral_stress=fsum((errors['reaction_torque_D'], returns, rf)),
                exact_reaction=fsum((errors['C_D'], returns, rf)))
            assert all(abs(v) > budget['limit'] for v in counterfactual.values())
            degrees[degree] = dict(scalars=s, R_D=rd, R_F=rf,
                free_residual_l2=sqrt(fsum(residual[i]**2 for i in range(402) if i not in fixed)),
                reaction_torque_D=reaction, errors_against_exact=errors,
                original_term_errors=term_errors,
                reaction_error_prediction=reaction_prediction,
                lateral_mismatch=lateral, return_mismatch=returns, physical_defect=defect,
                unchanged_budget_limit=budget['limit'], failure_ratio=abs(defect)/budget['limit'],
                lateral_share_of_signed_defect=lateral/defect,
                return_offset_fraction_of_lateral=abs(returns/lateral),
                counterfactual_arithmetic_at_original_limit=counterfactual,
                endpoint_error=numerical['raw_by_degree'][degree]['angular_momentum']-
                    float(F(reference['exact']['angular_final'])))

        old_manifest = read(ROOT/'verification/nonlinear_port/future_fem.json')
        validate_worker_result(read(HERE.parent/'r246/run/numerical.json'),
            old_manifest['versions'], old_manifest['gates'], policy=old_manifest['poiseuille_diagnostic_policy'])
        rotation = HERE.parent/'r253/run'
        validate_worker_payload(read(rotation/'numerical.json'),
            read(ROOT/'verification/nonlinear_port/future_rotation.json'),
            read(rotation/'reservation.json'), read(rotation/'admission.json'))
        loaded = sorted(n for n in sys.modules if n.split('.')[0] in OLD['FORBIDDEN'])
        assert not loaded
        return dict(status='INTERPRETATION_COMPLETE_REPAIR_NOT_JUSTIFIED',
            exact_face_parts_rational={k: str(v) for k, v in parts.items()}, degrees=degrees,
            exact_spatial_polynomial_degrees=dict(velocity=[max(sum(k[:3]) for k in v.terms) for v in u],
                                                   pressure=max(sum(k[:3]) for k in p.terms)),
            saved_lateral_fixed_entries=len(expected_fixed),
            maximum_lateral_nodal_error=max(abs(e) for _, e, b in nodal_errors if b),
            maximum_free_velocity_nodal_error=max(abs(e) for _, e, b in nodal_errors if not b),
            maximum_degree_scalar_difference=max(abs(degrees['24']['scalars'][k]-degrees['26']['scalars'][k])
                                                 for k in degrees['24']['scalars']),
            r266_r270_raw_fields_multipliers_and_history_identical=True,
            r270_verifier_reproduced=True, r270_full_report_rebuilt=True,
            saved_r246_validator='PASS', saved_r253_validator='PASS',
            saved_r266_validator='INCOMPLETE', saved_r270_validator='INCOMPLETE',
            r267_decomposition_negative_controls=4,
            mesh_family_dofs={str(n): 3*(2*n+1)**3+(n+1)**3+3 for n in (2, 4, 8)},
            numerical_modules_loaded=loaded, new_admissions=0, new_attempts=0)
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    (HERE/'probe.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
