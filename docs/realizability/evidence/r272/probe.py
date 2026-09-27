"""R272 design arithmetic and saved-data replay; no runtime implementation."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OLD = runpy.run_path(str(HERE.parent/'r271/probe.py'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    guard = OLD['OLD']['Guard']()
    sys.meta_path.insert(0, guard)
    try:
        prior = OLD['run']()
        assert prior == json.loads((HERE.parent/'r271/probe.json').read_text())
        counts = {}
        for n in (2, 4):
            nodes = (2*n+1)**3
            pressure = (n+1)**3
            fixed = 3*((2*n+1)**2-(2*n-1)**2)*(2*n+1)
            mixed = 3*nodes+pressure
            counts[str(n)] = dict(cells=6*n**3, vertices=pressure,
                exterior_facets=12*n*n, facets_per_tag=2*n*n,
                velocity_nodes=nodes, velocity_dofs=3*nodes, pressure_dofs=pressure,
                mixed_dofs=mixed, bordered_dofs=mixed+3, fixed_velocity_dofs=fixed)
        assert counts['2']['mixed_dofs'] == 402 and counts['2']['fixed_velocity_dofs'] == 240
        n4 = counts['4']
        assert n4['bordered_dofs'] == 2315 and n4['fixed_velocity_dofs'] == 864
        # 30 vector-P2 plus 4 scalar-P1 local basis entries; overcount every cell
        # clique, all three borders in both directions and every diagonal.
        structural_bound = n4['cells']*34**2 + 6*n4['mixed_dofs'] + n4['bordered_dofs']
        cap_nnz = 524288
        assert structural_bound == 460091 < cap_nnz
        n, m, f, nodes = (n4[k] for k in ('bordered_dofs', 'mixed_dofs',
                                         'fixed_velocity_dofs', 'velocity_nodes'))
        # Explicit schema bounds: float token <=25 bytes, comma <=1; index
        # <=4 digits; indptr <=6 digits; at most64KiB metadata/bracket overhead.
        linear_bound = 31*cap_nnz + 7*(n+1) + 26*(3*n+f) + 5*f + 65536
        angular_float_count = n + m + 3*nodes + f + 2*m + n
        angular_bound = 26*angular_float_count + 5*(m+f) + 65536
        assert linear_bound < 16*1024**2
        assert angular_bound < 1024**2
        tokens = [-sys.float_info.max, sys.float_info.max, -sys.float_info.min,
                  -5e-324, -1.2345678901234567e-123, 0., -0., 1.]
        assert all(len(json.dumps(x, allow_nan=False)) <= 25 for x in tokens)
        original = json.loads((HERE.parent/'r269/allocation.json').read_text())
        proposal = json.loads((HERE/'proposal.json').read_text())
        for key in ('gates', 'nonlinear', 'diagnostic_policy', 'exact_reference',
                    'versions', 'proposed_caps', 'history', 'load', 'initial_guess',
                    'time', 'dt', 'rho', 'mu', 'degrees', 'backflow_sampling_degree'):
            assert proposal['contract'][key] == original['contract'][key], key
        assert proposal['contract']['subdivisions'] == 4
        assert proposal['contract']['execution_admitted'] is False
        assert proposal['attempts_granted'] == proposal['contract']['attempts_granted'] == 0
        for name, sha in proposal['baseline_sha256'].items():
            assert digest(ROOT/name) == sha, name
        assert proposal['resource_limits'] == {
            k: v for k, v in original['limits'].items()
            if k not in ('actual_bordered_dofs', 'actual_mixed_dofs',
                         'latest_system_bytes_max', 'latest_system_dofs_max', 'latest_system_nnz_max')}
        from verification.nonlinear_port.manufactured_manifest import validate
        from verification.nonlinear_port.prototype import Refusal
        try:
            validate(proposal['contract'])
        except Refusal:
            old_validator_refuses_new_contract = True
        else:
            raise AssertionError('historical manifest accepted n4')
        forbidden = OLD['OLD']['FORBIDDEN']
        loaded = sorted(name for name in sys.modules if name.split('.')[0] in forbidden)
        assert not loaded
        return dict(status='DESIGN_COMPLETE_NOT_ADMITTED', mesh_counts=counts,
            structural_entry_upper_bound=structural_bound,
            proposed_linear_nnz_cap=cap_nnz, linear_serialized_upper_bound=linear_bound,
            proposed_linear_bytes_cap=16*1024**2, angular_float_count=angular_float_count,
            angular_both_degrees_serialized_upper_bound=angular_bound,
            proposed_angular_bytes_cap=1024**2, metadata_overhead_budget_per_record=65536,
            baseline_files_bound=len(proposal['baseline_sha256']),
            saved_r271_probe_reproduced=True, saved_r246_validator=prior['saved_r246_validator'],
            saved_r253_validator=prior['saved_r253_validator'],
            saved_r266_validator=prior['saved_r266_validator'],
            saved_r270_validator=prior['saved_r270_validator'],
            old_validator_refuses_new_contract=old_validator_refuses_new_contract,
            physical_and_resource_gates_unchanged=True, numerical_modules_loaded=loaded,
            new_admissions=0, new_attempts=0, actual_n4_resource_fit='UNMEASURED')
    finally:
        sys.meta_path.remove(guard)


if __name__ == '__main__':
    result = run()
    (HERE/'probe.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
