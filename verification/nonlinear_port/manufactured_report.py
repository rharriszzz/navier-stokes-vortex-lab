"""Pure reductions for the one-level manufactured BE pilot; no FEM imports."""
from fractions import Fraction
import json
from math import fsum, isfinite, sqrt
from sys import float_info

from .diagnostics import field_report
from .manufactured_policy import compare, validate_policy
from .prototype import Refusal
from .sparse import condition_from_gram


def _number(value, name, *, nonnegative=False):
    if type(value) not in (int, float) or not isfinite(value):
        raise Refusal('invalid manufactured number: ' + name)
    if nonnegative and value < 0:
        raise Refusal('negative manufactured number: ' + name)
    return value


def _limit(values, floor, multiplier):
    return max(floor, multiplier*float_info.epsilon*fsum(abs(v) for v in values))


def _identity(observed, expected, gates):
    defect = observed-expected
    limit = _limit((observed, expected), gates['identity_absolute_floor'],
                   gates['identity_epsilon_multiplier'])
    return dict(observed=observed, expected=expected, defect=defect,
                limit=limit, accepted=abs(defect) <= limit)


def _be_identity(raw, gates):
    # Preserve the three separate terms in the frozen R255 roundoff bound.
    storage, inventory, dissipation = (raw[key] for key in
        ('energy.storage', 'energy_identity_storage', 'energy_identity_dissipation'))
    defect = storage-inventory-dissipation
    limit = _limit((storage, inventory, dissipation),
                   gates['identity_absolute_floor'], gates['identity_epsilon_multiplier'])
    return dict(observed=storage, expected=inventory+dissipation,
                defect=defect, limit=limit, accepted=abs(defect) <= limit)


def _interval(inventory, initial, dt, terms, gates):
    pieces = dict(inventory_change=inventory-initial,
                  **{key: dt*value for key, value in terms.items()})
    defect = fsum(pieces.values())
    limit = max(gates['budget_absolute_floor'],
                gates['budget_relative_absolute_sum']*fsum(abs(v) for v in pieces.values()))
    return dict(semantics='discrete_manufactured_BE', terms=pieces,
                defect=defect, limit=limit, accepted=abs(defect) <= limit)


def build_report(raw_by_degree, multipliers, eta, history, corrections,
                 minimum_normal, sample_counts, condition, compatibility,
                 measured_targets, lateral_absolute_flux, proposal):
    """Recompute all decisions from finite records, keeping failed gate evidence."""
    from .manufactured_manifest import canonical, validate
    validate(proposal)
    policy, gates = proposal['diagnostic_policy'], proposal['gates']
    validate_policy(policy)
    if type(raw_by_degree) is not dict or set(raw_by_degree) != {'24', '26'}:
        raise Refusal('both manufactured diagnostic degrees required')
    comparison = compare(raw_by_degree['24'], raw_by_degree['26'], policy)
    if (type(multipliers) is not list or len(multipliers) != 2
            or type(measured_targets) is not list or len(measured_targets) != 2
            or type(sample_counts) is not list or len(sample_counts) != 2
            or any(type(n) is not int or n < 1 for n in sample_counts)):
        raise Refusal('incomplete manufactured return evidence')
    for name, values in (('multipliers', multipliers), ('targets', measured_targets)):
        for value in values:
            _number(value, name)
    _number(eta, 'eta')
    _number(minimum_normal, 'minimum normal velocity')
    _number(lateral_absolute_flux, 'lateral absolute flux', nonnegative=True)
    if (type(history) is not list or not 2 <= len(history) <= 13
            or type(corrections) is not list or len(corrections) != len(history)-1
            or len(corrections) > 12):
        raise Refusal('incomplete manufactured Newton history')
    for value in history:
        _number(value, 'nonlinear residual', nonnegative=True)
    for index, item in enumerate(corrections, 1):
        if type(item) is not dict or set(item) != {'true_residual', 'rhs_norm', 'linear_system'}:
            raise Refusal('incomplete manufactured linear correction')
        for name in ('true_residual', 'rhs_norm'):
            _number(item[name], name, nonnegative=True)
        receipt = item['linear_system']
        if (type(receipt) is not dict or set(receipt) != {'file', 'correction', 'sha256', 'bytes'}
                or receipt['file'] != 'linear_system.json'
                or type(receipt['correction']) is not int
                or receipt['correction'] != index
                or type(receipt['sha256']) is not str or len(receipt['sha256']) != 64
                or any(ch not in '0123456789abcdef' for ch in receipt['sha256'])
                or type(receipt['bytes']) is not int or not 0 < receipt['bytes'] <= 4*1024*1024):
            raise Refusal('invalid manufactured linear-system receipt')
    if (type(condition) is not dict or type(condition.get('gram')) is not list
            or len(condition['gram']) != 3
            or any(type(row) is not list or len(row) != 3
                   or any(type(v) not in (int, float) or not isfinite(v) for v in row)
                   for row in condition['gram'])
            or canonical(condition_from_gram(condition['gram'])) != canonical(condition)):
        raise Refusal('manufactured condition differs from measured Gram')
    if (type(compatibility) is not dict
            or set(compatibility) != {'defect', 'limit', 'condition', 'absolute_term_sum',
                                      'lateral_flux', 'targets'}):
        raise Refusal('incomplete manufactured compatibility')
    for name in ('defect', 'limit', 'condition', 'absolute_term_sum', 'lateral_flux'):
        _number(compatibility[name], name)
    if (compatibility['targets'] != measured_targets
            or compatibility['condition'] != condition['condition_bound']
            or compatibility['absolute_term_sum'] !=
               lateral_absolute_flux+fsum(abs(v) for v in measured_targets)
            or compatibility['absolute_term_sum'] < abs(compatibility['lateral_flux'])
               + sum(abs(v) for v in measured_targets)):
        raise Refusal('manufactured compatibility inputs changed')
    compatibility_defect = compatibility['lateral_flux']+sum(measured_targets)
    compatibility_limit = (gates['compatibility_epsilon_multiplier']*float_info.epsilon
                           *condition['condition_bound']*compatibility['absolute_term_sum'])
    if (compatibility['defect'] != compatibility_defect
            or compatibility['limit'] != compatibility_limit):
        raise Refusal('manufactured compatibility decision changed')
    reference = proposal['exact_reference']['exact']
    targets = [float(Fraction(reference[key])) for key in ('Q_minus', 'Q_plus')]
    expected_multipliers = [float(Fraction(reference[key])) for key in ('P_minus', 'P_plus')]
    target_checks = {str(side): dict(measured=measured_targets[side], expected=targets[side],
                                     difference=measured_targets[side]-targets[side],
                                     limit=1e-12,
                                     accepted=abs(measured_targets[side]-targets[side]) <= 1e-12)
                     for side in (0, 1)}
    target_checks['lateral'] = dict(measured=compatibility['lateral_flux'],
        expected=float(Fraction(reference['Q_lateral'])),
        difference=compatibility['lateral_flux']-float(Fraction(reference['Q_lateral'])),
        limit=1e-12,
        accepted=abs(compatibility['lateral_flux']-float(Fraction(reference['Q_lateral']))) <= 1e-12)
    dt = proposal['dt']
    k0 = float(Fraction(reference['kinetic_initial']))
    l0 = float(Fraction(reference['angular_initial']))
    degrees = {}
    for degree in ('24', '26'):
        raw = raw_by_degree[degree]
        field = field_report(raw, multipliers, expected_multipliers, targets, eta)
        angular_rate = (raw['angular_momentum']-l0)/dt
        energy_rate = (raw['kinetic_energy']-k0)/dt
        identities = dict(
            angular_storage=_identity(angular_rate, raw['angular.storage'], gates),
            energy_storage=_identity(energy_rate, raw['energy_identity_storage'], gates),
            kinetic_derivative=_identity(energy_rate, raw['kinetic_discrete_derivative'], gates),
            be_storage=_be_identity(raw, gates))
        angular = _interval(raw['angular_momentum'], l0, dt,
            {key: raw['angular.'+key] for key in ('advective', 'traction', 'body')}, gates)
        energy = _interval(raw['kinetic_energy'], k0, dt,
            dict(BE_dissipation=raw['energy_identity_dissipation'],
                 **{key: raw['energy.'+key] for key in
                    ('advective', 'traction', 'body', 'dissipation',
                     'conservative_divergence', 'pressure_divergence')}), gates)
        linear = [item['true_residual'] <= max(gates['linear_residual_absolute'],
                   gates['linear_residual_relative']*item['rhs_norm']) for item in corrections]
        constraints = [*field['both_flux_errors'], field['pressure_mean'], eta]
        checks = dict(
            volume_and_caps=all(abs(raw[key]-1) <= 1e-12 for key in ('volume', 'area_0', 'area_1')),
            constraints=all(abs(value) <= gates['flux_gauge_eta_absolute'] for value in constraints),
            backflow=minimum_normal >= gates['backflow_minimum'],
            nonlinear=history[-1] <= max(proposal['nonlinear']['scaled_absolute_residual'],
                           proposal['nonlinear']['scaled_relative_residual']*history[0]),
            linear=all(linear), angular_budget=field['angular_budget']['accepted'],
            energy_budget=field['energy_budget']['accepted'],
            be_identities=all(item['accepted'] for item in identities.values()),
            angular_interval=angular['accepted'], energy_interval=energy['accepted'])
        degrees[degree] = dict(field_report=field, identities=identities,
            interval_budgets=dict(angular=angular, energy=energy),
            checks=checks, accepted=all(checks.values()))
    checks = dict(targets=all(item['accepted'] for item in target_checks.values()),
        compatibility=abs(compatibility_defect) <= compatibility_limit,
        constraint_condition=condition['condition_bound'] <= gates['constraint_condition_max'],
        verified_corrections=len(corrections) >= gates['minimum_verified_corrections'],
        degree24=degrees['24']['accepted'], degree26=degrees['26']['accepted'],
        quadrature=all(item['accepted'] for item in comparison.values()))
    return dict(schema=1, semantics='discrete_manufactured_BE',
        time=proposal['time'], dt=dt, step=1, history=proposal['history'],
        load=proposal['load'], diagnostic_policy=policy,
        raw_by_degree=raw_by_degree, measured_targets=measured_targets,
        lateral_absolute_flux=lateral_absolute_flux,
        target_checks=target_checks, compatibility=compatibility,
        constraint_condition=condition, degree_validation=degrees,
        quadrature_comparison=comparison, checks=checks,
        numerical_accepted=all(checks.values()))


def validate_report(report, proposal, **evidence):
    if type(report) is not dict:
        raise Refusal('missing manufactured report')
    expected = build_report(report.get('raw_by_degree'), proposal=proposal, **evidence)
    try:
        actual_text = json.dumps(report, sort_keys=True, allow_nan=False)
        expected_text = json.dumps(expected, sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise Refusal('invalid manufactured report JSON') from exc
    if actual_text != expected_text or report['numerical_accepted'] is not True:
        raise Refusal('failed or inconsistent manufactured evidence')
    return report
