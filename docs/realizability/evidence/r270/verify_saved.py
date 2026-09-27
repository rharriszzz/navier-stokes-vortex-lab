"""Independent standard-library checks of the saved R270 bytes; no numerical import."""
import hashlib
import json
from math import fsum, isfinite
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = Path('/tmp/navier-manufactured-r269-once')
RUN = HERE / 'run'


def load(name):
    return json.loads((RUN / name).read_text())


def close(actual, expected):
    assert isfinite(actual) and isfinite(expected)
    assert abs(actual - expected) <= 1e-12, (actual, expected)
    return abs(actual - expected)


def run():
    side = load('angular_audit.json')
    numerical = load('numerical.json')
    result = load('result.json')
    caller = load('caller.json')
    held = load('held.json')
    assert side['source_binding'] == numerical['source_binding']
    assert side['source_binding']['source_commit'] == '950c2a72fe04fadc2d5a262539f0748d24924646'
    for key in ('geometry', 'step', 'time', 'dt'):
        assert side[key] == numerical[key]
    assert side['state'][402:] == numerical['multipliers'] + [numerical['eta']]
    assert len(side['state']) == 405 and len(side['phi']['coefficients']) == 402
    assert len(side['fixed_indices']) == len(side['fixed_values']) == numerical['fixed_velocity_dofs'] == 240
    assert {str(i): v for i, v in zip(side['fixed_indices'], side['fixed_values'])} == numerical['fixed_inventory']
    phi = side['phi']
    vm, pm = phi['velocity_parent_map'], phi['pressure_parent_map']
    assert len(vm) == 375 and len(pm) == 27 and sorted(vm + pm) == list(range(402))
    assert len(phi['velocity_node_coordinates']) == 125 and phi['velocity_block_size'] == 3
    assert all(phi['coefficients'][i] == 0.0 for i in pm)
    for j, (x, y, z) in enumerate(phi['velocity_node_coordinates']):
        for component, expected in enumerate((-y, x, 0.0)):
            close(phi['coefficients'][vm[3*j + component]], expected)
    fixed = set(side['fixed_indices'])
    assert fixed <= set(vm)
    summary = {}
    max_identity_error = 0.0
    for degree in ('24', '26'):
        entry = side['degrees'][degree]
        original = entry['original']
        scalar = entry['scalar']
        residual = entry['raw_residual']
        assert len(residual) == 402 and entry['multipliers'] == side['state'][402:]
        for key in ('storage', 'advective', 'traction', 'body'):
            assert original[key] == numerical['raw_by_degree'][degree]['angular.' + key]
        close(original['physical_defect'], fsum(original[k] for k in ('storage', 'advective', 'traction', 'body')))
        rd = fsum(phi['coefficients'][i] * residual[i] for i in sorted(fixed))
        rf = fsum(phi['coefficients'][i] * residual[i] for i in range(402) if i not in fixed)
        ad, ar = scalar['A_D'], scalar['A_R']
        cd, cr, gr = scalar['C_D'], scalar['C_R'], scalar['G_R']
        action = scalar['residual_action']
        reductions = dict(R_D=rd, R_F=rf, reaction_torque_D=fsum((rd, ad)),
                          lateral_mismatch=fsum((rd, ad, cd)),
                          return_mismatch=fsum((cr, -gr)))
        reductions['reconstructed_defect'] = fsum((reductions['lateral_mismatch'],
                                                   reductions['return_mismatch'], rf))
        for key, value in reductions.items():
            max_identity_error = max(max_identity_error, close(value, entry['reductions'][key]))
        terms = dict(
            advection=(ad, ar, -original['advective']),
            traction=(cd, cr, -original['traction']),
            residual_vector_action=(rd, rf, -action),
            residual_scalar_action=(action, -original['storage'], -original['body'], -ar, -gr),
            physical_defect=(reductions['reconstructed_defect'], -original['physical_defect']),
        )
        for key, values in terms.items():
            saved = entry['comparisons'][key]
            assert saved['accepted'] and saved['limit'] == 1e-12
            for value, recorded in zip(values, saved['terms'], strict=True):
                max_identity_error = max(max_identity_error, close(value, recorded))
            max_identity_error = max(max_identity_error, close(fsum(values), saved['defect']))
            assert abs(fsum(values)) <= saved['limit']
        budget = numerical['report']['degree_validation'][degree]['field_report']['angular_budget']
        assert not budget['accepted'] and not numerical['report']['degree_validation'][degree]['accepted']
        assert original['physical_defect'] == budget['signed_defect']
        summary[degree] = dict(physical_defect=original['physical_defect'],
                               physical_limit=budget['limit'],
                               lateral_mismatch=reductions['lateral_mismatch'],
                               return_mismatch=reductions['return_mismatch'],
                               free_residual_action=rf,
                               comparisons_passed=len(terms))
    assert not numerical['report']['numerical_accepted']
    assert caller['status'] == result['status'] == 'INCOMPLETE'
    assert caller['angular_evidence']['consistent'] and caller['inner_status'] == 'INCOMPLETE'
    assert load('reservation.json')['attempt'] == 1
    assert result['cleanup']['empty'] and result['exit']['exit_code'] == 0
    assert result['cleanup']['memory_events']['max'] == result['cleanup']['memory_events']['oom'] == 0
    assert result['cleanup']['pids_events']['max'] == 0
    assert not Path('/proc', str(held['pid'])).exists()
    assert not (Path('/sys/fs/cgroup') / held['cgroup'].lstrip('/')).exists()
    files = {}
    for copy in sorted(RUN.iterdir()):
        assert copy.is_file() and (ORIGINAL / copy.name).read_bytes() == copy.read_bytes()
        files[copy.name] = dict(bytes=copy.stat().st_size,
                                sha256=hashlib.sha256(copy.read_bytes()).hexdigest())
    side_bytes = (RUN / 'angular_audit.json').read_bytes()
    assert caller['angular_evidence']['bytes'] == len(side_bytes)
    assert caller['angular_evidence']['sha256'] == hashlib.sha256(side_bytes).hexdigest()
    return dict(status='INCOMPLETE', allocation_spent='1/1', copied_run_files=files,
                degrees=summary, max_identity_recalculation_error=max_identity_error,
                new_worker_pid_cgroup_absent=True)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, sort_keys=True))
