"""R247 saved-result and exact rational review; no FEM imports or execution."""
import hashlib
import json
from pathlib import Path
import sys
from fractions import Fraction as F

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from verification.nonlinear_port.fixtures import rotation, MU
from verification.nonlinear_port.polynomial import Poly, volume, face, dot
from verification.nonlinear_port.supervision import validate_worker_result


def scalar(p):
    assert set(p.terms) <= {(0, 0, 0, 0)}
    return p.terms.get((0, 0, 0, 0), F(0))


def run():
    evidence = ROOT / 'docs/realizability/evidence'
    manifest = json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
    numerical = json.loads((evidence/'r246/run/numerical.json').read_text())
    validate_worker_result(numerical, manifest['versions'], manifest['gates'],
                           policy=manifest['poiseuille_diagnostic_policy'])
    old = json.loads((evidence/'r242/run/numerical.json').read_text())
    same_scalars = (old['diagnostics_degree24']['raw'] == numerical['diagnostics_degree24']['raw']
                    and old['diagnostics_degree26'] == numerical['diagnostics_degree26'])
    assert same_scalars
    raw_count = 0
    runs = []
    for req in ('r232', 'r235', 'r238', 'r242', 'r246'):
        inventory = json.loads((evidence/req/'run_hashes.json').read_text())
        original = Path(inventory['source_directory'])
        for name, item in inventory['files'].items():
            data = (evidence/req/'run'/name).read_bytes()
            assert len(data) == item['bytes']
            assert hashlib.sha256(data).hexdigest() == item['sha256']
            assert data == (original/name).read_bytes()
            raw_count += 1
        held = json.loads((original/'held.json').read_text())
        assert (original/'reservation.json').is_file()
        assert not Path('/proc', str(held['pid'])).exists()
        assert not Path('/sys/fs/cgroup', held['cgroup'].lstrip('/')).exists()
        runs.append(dict(request=req, spent=1, reservation_present=True,
                         recorded_pid_absent=True, recorded_cgroup_absent=True))
    source = json.loads((evidence/'r245/checks.json').read_text())['source_sha256']
    for name, digest in source.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest
    u, p = rotation()
    grad = [[v.d(j) for j in range(3)] for v in u]
    strain = [[F(1,2)*(grad[i][j]+grad[j][i]) for j in range(3)] for i in range(3)]
    conv = [sum((u[i]*u[j]).d(j) for j in range(3)) for i in range(3)]
    gp = [p.d(i) for i in range(3)]
    tensor_norm = lambda a: sum(v*v for row in a for v in row)
    tau = [[2*MU*v for v in row] for row in strain]
    residual = [conv[i]+gp[i]-sum(tau[i][j].d(j) for j in range(3)) for i in range(3)]
    boundary_norm = lambda a: sum(face(sum(a[i][axis]**2 for i in range(3)), axis, side)
                                  for axis in range(3) for side in (0,1))
    sigma = [[tau[i][j]-(p if i==j else 0) for j in range(3)] for i in range(3)]
    derived = {
        'volume': volume(Poly(1)),
        'velocity_l2_squared': volume(dot(u,u)),
        'gradient_l2_squared': volume(tensor_norm(grad)),
        'pressure_mean': volume(p), 'pressure_l2_squared': volume(p*p),
        'convection_l2_squared': volume(dot(conv,conv)),
        'pressure_gradient_l2_squared': volume(dot(gp,gp)),
        'strain_l2_squared': volume(tensor_norm(strain)),
        'divergence_l2_squared': volume(sum(u[i].d(i) for i in range(3))**2),
        'momentum_residual_l2_squared': volume(dot(residual,residual)),
        'viscous_stress_l2_squared': volume(tensor_norm(tau)),
        'viscous_traction_boundary_l2_squared': boundary_norm(tau),
        'total_traction_boundary_l2_squared': boundary_norm(sigma),
        'viscous_dissipation': volume(2*MU*tensor_norm(strain)),
    }
    expected = dict(volume=F(1), velocity_l2_squared=F(1,6), gradient_l2_squared=F(2),
                    pressure_mean=F(0), pressure_l2_squared=F(1,360),
                    convection_l2_squared=F(1,6), pressure_gradient_l2_squared=F(1,6),
                    strain_l2_squared=F(0), divergence_l2_squared=F(0),
                    momentum_residual_l2_squared=F(0), viscous_stress_l2_squared=F(0),
                    viscous_traction_boundary_l2_squared=F(0),
                    total_traction_boundary_l2_squared=F(7,180), viscous_dissipation=F(0))
    assert {k:scalar(v) for k,v in derived.items()} == expected
    for axis in range(3):
        for side in (0,1):
            tag=1+2*axis+side
            expected[f'area_{tag}']=scalar(face(Poly(1),axis,side))
            for j in range(3):
                expected[f'normal_{tag}_{j}']=F(2*side-1 if j==axis else 0)
    wrong_tau = [[MU*v for v in row] for row in grad]
    controls = {
        'omit_pressure_residual_squared': scalar(volume(dot(conv,conv))),
        'reverse_pressure_residual_squared': scalar(volume(dot([a-b for a,b in zip(conv,gp)], [a-b for a,b in zip(conv,gp)]))),
        'omit_pressure_signed_momentum_integrals': [str(scalar(volume(v))) for v in conv],
        'nonsymmetric_viscous_stress_squared': scalar(volume(tensor_norm(wrong_tau))),
        'nonsymmetric_viscous_traction_boundary_squared': scalar(boundary_norm(wrong_tau)),
        'nonsymmetric_viscous_traction_caps_squared': scalar(sum(face(sum(wrong_tau[i][2]**2 for i in range(3)),2,s) for s in (0,1))),
        'gradient_based_dissipation': scalar(volume(MU*tensor_norm(grad))),
    }
    assert controls['omit_pressure_residual_squared']==F(1,6)
    assert controls['reverse_pressure_residual_squared']==F(2,3)
    assert controls['nonsymmetric_viscous_stress_squared']==F(1,50)
    assert controls['nonsymmetric_viscous_traction_boundary_squared']==F(1,25)
    assert controls['gradient_based_dissipation']==F(1,5)
    assert controls['nonsymmetric_viscous_traction_caps_squared']==0
    assert controls['omit_pressure_signed_momentum_integrals']==['0','0','0']
    assert len(expected)==38
    numerical_modules = [m for m in ('numpy','dolfinx','basix','ufl','ffcx','petsc4py','mpi4py','scipy') if m in sys.modules]
    assert not numerical_modules
    return dict(r246_controller_replay='PASS', r242_r246_raw_scalars_identical=same_scalars,
                r242_status_unchanged='INCOMPLETE', raw_files_verified=raw_count,
                prior_runs=runs, source_sha256=source, numerical_modules_loaded=numerical_modules,
                rotation_exact_targets={k:str(v) for k,v in expected.items()},
                rotation_negative_controls={k:str(v) if isinstance(v,F) else v for k,v in controls.items()},
                decision='PROPOSE_SOURCE_ONLY_ROTATION_ASSEMBLY_ORACLE', attempts_granted=0,
                no_manager_connection=True, no_new_numerical_run=True)

if __name__=='__main__':
    print(json.dumps(run(),indent=2,sort_keys=True,allow_nan=False))
