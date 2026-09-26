"""Saved-data and exact rational R243 review; no FEM or workload launch.

The candidate below is a review calculation, NOT a runtime acceptance gate.
Run with project Python from any directory; writes audit.json beside this file.
"""
from fractions import Fraction as F
import hashlib
import json
from math import fsum, isfinite
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from verification.nonlinear_port.diagnostics import (
    ANGULAR_TERMS, ENERGY_TERMS, field_report, quadrature_comparison,
    poiseuille_endpoint_budgets, step_checks)
from verification.nonlinear_port.fixture_driver import numerical_decision
from verification.nonlinear_port.fixtures import poiseuille, stress, forcing
from verification.nonlinear_port.polynomial import Poly, x, y, dot, face, volume
from verification.nonlinear_port.prototype import Refusal
from verification.nonlinear_port.supervision import validate_worker_result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def constant(p):
    assert set(p.terms) <= {(0, 0, 0, 0)}
    return p.terms.get((0, 0, 0, 0), F(0))


def main():
    source = json.loads((ROOT/'docs/realizability/evidence/r241/checks.json').read_text())['source_sha256']
    assert all(sha(ROOT/p) == value for p, value in source.items())
    runs = []
    for request in ('r232', 'r235', 'r238', 'r242'):
        base = ROOT/'docs/realizability/evidence'/request
        inventory = json.loads((base/'run_hashes.json').read_text())
        original = Path(inventory['source_directory'])
        for name, meta in inventory['files'].items():
            for p in (base/'run'/name, original/name):
                assert sha(p) == meta['sha256'] and p.stat().st_size == meta['bytes']
        held = json.loads((original/'held.json').read_text())
        assert (original/'reservation.json').exists()
        assert not Path('/proc', str(held['pid'])).exists()
        assert not (Path('/sys/fs/cgroup')/held['cgroup'].lstrip('/')).exists()
        runs.append(dict(request=request, files=len(inventory['files']), spent=1,
                         originals_match=True, recorded_pid_and_cgroup_absent=True))

    report_path = ROOT/'docs/realizability/evidence/r242/run/numerical.json'
    payload = json.loads(report_path.read_text())
    manifest = json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
    base = payload['diagnostics_degree24']['raw']
    check = payload['diagnostics_degree26']
    original_comparison = quadrature_comparison(base, check, manifest['gates']['quadrature_relative_change'])
    assert original_comparison == payload['quadrature_comparison']
    try:
        validate_worker_result(payload, manifest['versions'], manifest['gates'])
    except Refusal as exc:
        refusal = str(exc)
        assert refusal == 'failed or inconsistent numerical evidence'
    else:
        raise AssertionError('Historical result must remain refused')

    # Budget proposal: one percent of the 1e-12 absolute identity gate per
    # signed quantity. This is a target, NOT a measured rounding-error bound.
    signed = ({'angular.'+k for k in ANGULAR_TERMS}
              | {'energy.'+k for k in ENERGY_TERMS if k != 'dissipation'}
              | {'energy_identity_storage', 'kinetic_discrete_derivative',
                 'lateral_flux', 'flux_0', 'flux_1', 'pressure_mean', 'p_error_integral'})
    assert len(signed) == 17 and signed <= base.keys()

    def candidate(key, a, b):
        if key not in base or not all(type(v) in (float, int) and isfinite(v) for v in (a, b)):
            raise ValueError('unknown or nonfinite diagnostic')
        threshold = max(1e-8*max(1e-10, abs(a)), 1e-14 if key in signed else 0.)
        return dict(limit=threshold, accepted=abs(b-a) <= threshold)

    rows = {k: dict(degree24=base[k], degree26=check[k], **original_comparison[k],
                   signed_floor_proposed=k in signed, candidate=candidate(k, base[k], check[k]))
            for k in base}
    assert sum(not row['accepted'] for row in rows.values()) == 12
    # Rebuild both physical evaluations with the ORIGINAL physical thresholds.
    physical = {}
    for degree, values in ((24, base), (26, check)):
        field = field_report(values, payload['multipliers'], [0., 0.], [0., 0.], payload['eta'])
        last = payload['linear_corrections'][-1]
        step = step_checks(field, [payload['minimum_return_normal_velocity']],
                           payload['nonlinear_history'], last['true_residual'],
                           manifest['gates'], last['rhs_norm'])
        decision = numerical_decision(field, step, original_comparison,
                                      len(payload['linear_corrections']), manifest['gates'])
        # Keep the known original quadrature failure; list physical gates only.
        checks = {k: v for k, v in decision['checks'].items() if k != 'quadrature_24_26'}
        endpoints = poiseuille_endpoint_budgets(values, payload['dt'])
        checks['physical_endpoint_budgets'] = all(v['physical']['accepted'] for v in endpoints.values())
        assert all(checks.values())
        physical[str(degree)] = dict(checks=checks, step=step, field=field, endpoints=endpoints)

    # Exact oracle surface contributions demonstrate real O(1) cancellation.
    u, p = poiseuille()
    sigma = stress(u, p)
    assert all(v == 0 for v in forcing(u, p))
    angular = lambda v: x*v[1]-y*v[0]
    faces = []
    for axis in range(3):
        for side in (0, 1):
            normal = [0, 0, 0]
            normal[axis] = 2*side-1
            traction = [dot(row, normal) for row in sigma]
            forms = {'angular.advective': angular(u)*dot(u, normal),
                     'angular.traction': -angular(traction),
                     'energy.advective': F(1, 2)*dot(u, u)*dot(u, normal),
                     'energy.traction': -dot(traction, u),
                     'flux': dot(u, normal)}
            faces.append(dict(axis=axis, side=side,
                              values={k: constant(face(v, axis, side)) for k, v in forms.items()}))
    exact = {}
    for key in faces[0]['values']:
        contributions = [entry['values'][key] for entry in faces]
        exact[key] = dict(total=str(sum(contributions)),
                          sum_absolute_face_integrals=str(sum(map(abs, contributions))))
    assert exact['angular.advective']['total'] == '0'
    assert exact['angular.traction']['total'] == '0'
    assert exact['energy.advective']['total'] == '0'
    assert exact['energy.traction']['total'] == '-8/15'
    assert constant(volume(p)) == 0
    for entry in faces:
        entry['values'] = {k: str(v) for k, v in entry['values'].items()}

    # Binary-exact inputs: loss in one ordering, recovery in another.
    terms = [1., 2.**-54, -1.]
    def recursive_sum(values):
        # Explicit recursive addition: Python 3.12's sum has improved accuracy.
        total = 0.
        for value in values:
            total += value
        return total
    toy = dict(terms=terms, exact_sum=str(sum(F(v) for v in terms)),
               forward=recursive_sum(terms), reordered=recursive_sum([terms[0], terms[2], terms[1]]),
               compensated=fsum(terms))
    assert toy['forward'] == 0. and toy['reordered'] == toy['compensated'] == 2.**-54
    assert not quadrature_comparison({'toy': toy['forward']}, {'toy': toy['reordered']})['toy']['accepted']

    controls = {}
    for name, key, a, b, expected in (
        ('small_signed_target', 'pressure_mean', 0., 1e-15, True),
        ('signed_above_target', 'pressure_mean', 0., 2e-14, False),
        ('squared_error_not_widened', 'u_L2_squared', 0., 1e-16, False),
        ('positive_dissipation_not_widened', 'energy_identity_dissipation', 0., 1e-16, False),
        ('nonzero_relative_error', 'kinetic_energy', 1., 1.000001, False),
        ('common_mode_is_invisible', 'pressure_mean', 1e-6, 1e-6, True)):
        result = candidate(key, a, b)
        assert result['accepted'] is expected
        controls[name] = dict(key=key, base=a, check=b, **result)
    corrupted = dict(base, pressure_mean=1e-6)
    corrupt_field = field_report(corrupted, payload['multipliers'], [0., 0.], [0., 0.], payload['eta'])
    corrupt_step = step_checks(corrupt_field, [payload['minimum_return_normal_velocity']],
                              payload['nonlinear_history'], last['true_residual'],
                              manifest['gates'], last['rhs_norm'])
    assert corrupt_step['checks']['constraints'] is False
    controls['common_mode_physical_gate'] = corrupt_step
    for key, value in (('unknown', 0.), ('pressure_mean', float('nan'))):
        try:
            candidate(key, 0., value)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid candidate input accepted')
    controls['unknown_and_nonfinite_refused'] = True

    forbidden = ('numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy')
    loaded = sorted(name for name in sys.modules if name.split('.')[0] in forbidden)
    assert not loaded
    result = dict(scope='PROPOSAL_ONLY; original R242 INCOMPLETE remains unchanged',
                  source_sha256=source, report_sha256=sha(report_path), raw_runs=runs,
                  original_controller_refusal=refusal, comparisons=rows,
                  original_failed_count=12, candidate_pair_disagreements=sum(not v['candidate']['accepted'] for v in rows.values()),
                  candidate_signed_keys=sorted(signed), candidate_absolute_target=1e-14,
                  physical_replay=physical, exact_faces=faces, exact_sums=exact,
                  cancellation_toy=toy, controls=controls, numerical_modules_loaded=loaded,
                  caveats=['Candidate is an accuracy-policy proposal, not an error bound or accepted method.',
                           'Saved scalar sums do not reveal quadrature summands or integrand evaluation errors.',
                           'Both-degree replay reuses saved degree-24 backflow sample minimum; no degree-26 sampling claim.',
                           'Absolute boundary flux is nonpolynomial for a general P2 field.',
                           'Latest matrix state precedes correction 3; final field/DOF coordinates are not retained.'])
    Path(__file__).with_name('audit.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps(dict(source_files=len(source), raw_files=sum(r['files'] for r in runs),
                          compared_quantities=len(rows), original_failures=12,
                          candidate_pair_disagreements=result['candidate_pair_disagreements'],
                          signed_keys=len(signed), numerical_modules_loaded=loaded)))


if __name__ == '__main__':
    main()
