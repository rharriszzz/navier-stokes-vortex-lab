"""R255 saved-data and rational-polynomial review; no FEM or manager access."""
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from verification.nonlinear_port import fixtures
from verification.nonlinear_port.polynomial import Poly, x, y, z, t, dot, volume, face


def scalar(p):
    p = Poly.cast(p)
    assert set(p.terms) <= {(0, 0, 0, 0)}
    return p.terms.get((0, 0, 0, 0), F(0))


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def rotation_targets():
    # Recompute R247 algebra independently of UFL, rotation_oracle and its targets.
    u = [F(1, 2)-y, x-F(1, 2), Poly()]
    p = F(1, 2)*((x-F(1, 2))**2+(y-F(1, 2))**2-F(1, 6))
    grad = [[v.d(j) for j in range(3)] for v in u]
    strain = [[F(1, 2)*(grad[i][j]+grad[j][i]) for j in range(3)] for i in range(3)]
    tau = [[F(1, 5)*v for v in row] for row in strain]
    sigma = [[tau[i][j]-(p if i == j else 0) for j in range(3)] for i in range(3)]
    conv = [sum((u[i]*u[j]).d(j) for j in range(3)) for i in range(3)]
    gp = [p.d(i) for i in range(3)]
    residual = [conv[i]+gp[i]-sum(tau[i][j].d(j) for j in range(3)) for i in range(3)]
    norm = lambda a: sum(v*v for row in a for v in row)
    surface_norm = lambda a: sum(face(sum(a[i][axis]**2 for i in range(3)), axis, side)
                                 for axis in range(3) for side in (0, 1))
    targets = dict(volume=volume(1), velocity_l2_squared=volume(dot(u, u)),
        gradient_l2_squared=volume(norm(grad)), pressure_mean=volume(p),
        pressure_l2_squared=volume(p*p), convection_l2_squared=volume(dot(conv, conv)),
        pressure_gradient_l2_squared=volume(dot(gp, gp)), strain_l2_squared=volume(norm(strain)),
        divergence_l2_squared=volume(sum(u[i].d(i) for i in range(3))**2),
        momentum_residual_l2_squared=volume(dot(residual, residual)),
        viscous_stress_l2_squared=volume(norm(tau)),
        viscous_traction_boundary_l2_squared=surface_norm(tau),
        total_traction_boundary_l2_squared=surface_norm(sigma),
        viscous_dissipation=volume(F(1, 5)*norm(strain)))
    for axis in range(3):
        for side in (0, 1):
            tag = 1+2*axis+side
            targets[f'area_{tag}'] = face(Poly(1), axis, side)
            for j in range(3):
                targets[f'normal_{tag}_{j}'] = Poly(2*side-1 if j == axis else 0)
    return {k: str(scalar(v)) for k, v in targets.items()}


def manufactured_reference():
    # Construct the fixture independently, then cross-check the source generator.
    A, C, E, H = 1+t+t**3, F(1, 2)+t, 1+t**2+t**3, 1+t
    psi = E*x**2*(1-x)**2*y**2*(1-y)**2
    all_u = [-A*x+psi.d(1), -A*y-psi.d(0), 2*A*z-C]
    all_p = H*(x*x+y*y+z*z-1)
    assert (all_u, all_p) == fixtures.manufactured()
    assert sum(v.d(i) for i, v in enumerate(all_u)) == 0
    assert volume(all_p) == 0
    for axis in (0, 1):
        for side in (0, 1):
            for v in (psi.d(0), psi.d(1)):
                assert v.at(axis, side) == 0
    dt = F(1, 8)
    u, old = [v.at(3, dt) for v in all_u], [v.at(3, 0) for v in all_u]
    p = all_p.at(3, dt)
    du = [(v-w)*8 for v, w in zip(u, old)]
    continuous_du = [v.d(3).at(3, dt) for v in all_u]
    grad = [[v.d(j) for j in range(3)] for v in u]
    strain = [[F(1, 2)*(grad[i][j]+grad[j][i]) for j in range(3)] for i in range(3)]
    sigma = [[F(1, 5)*strain[i][j]-(p if i == j else 0)
              for j in range(3)] for i in range(3)]
    # Advective expression differs from production's conservative generator.
    spatial = [sum(u[j]*u[i].d(j) for j in range(3))+p.d(i)
               -F(1, 10)*sum(u[i].d(j).d(j) for j in range(3)) for i in range(3)]
    force = [du[i]+spatial[i] for i in range(3)]
    continuous = [v.at(3, dt) for v in fixtures.forcing(all_u, all_p)]
    assert force == [continuous[i]+du[i]-continuous_du[i] for i in range(3)]
    Q = [face((2*s-1)*u[2], 2, s) for s in (0, 1)]
    P = [-face(sigma[2][2], 2, s) for s in (0, 1)]
    for s in (0, 1):
        q, pressure, offset = fixtures.return_data(s)
        assert Q[s] == q.at(3, dt) and P[s] == pressure.at(3, dt)
        n = 2*s-1
        expected_offset = -F(9, 8)*(x*x+y*y-F(2, 3))*n
        assert [v.at(3, dt) for v in offset] == [Poly(), Poly(), expected_offset]
        assert face(expected_offset*n, 2, s) == 0
    lateral = sum(face((2*s-1)*u[a], a, s) for a in (0, 1) for s in (0, 1))
    assert scalar(lateral+sum(Q)) == 0
    angular = lambda v: x*v[1]-y*v[0]
    boundary = lambda fun: sum(face(fun(a, 2*s-1), a, s)
                               for a in range(3) for s in (0, 1))
    traction = lambda a, n: [n*sigma[i][a] for i in range(3)]
    k = F(1, 2)*volume(dot(u, u))
    k0 = F(1, 2)*volume(dot(old, old))
    l, l0 = volume(angular(u)), volume(angular(old))
    diss = F(1, 5)*volume(sum(v*v for row in strain for v in row))
    energy = dict(storage=volume(dot(du, u)),
        advective=boundary(lambda a, n: F(1, 2)*dot(u, u)*n*u[a]),
        traction=-boundary(lambda a, n: dot(traction(a, n), u)),
        body=-volume(dot(force, u)), dissipation=diss,
        conservative_divergence=Poly(), pressure_divergence=Poly())
    ang = dict(storage=volume(angular(du)),
        advective=boundary(lambda a, n: angular(u)*n*u[a]),
        traction=-boundary(lambda a, n: angular(traction(a, n))),
        body=-volume(angular(force)))
    be_diss = F(1, 2)*volume(dot([v-w for v, w in zip(u, old)],
                               [v-w for v, w in zip(u, old)]))*8
    assert sum(energy.values()) == sum(ang.values()) == 0
    assert energy['storage'] == (k-k0)*8+be_diss
    assert ang['storage'] == (l-l0)*8
    force_error = [a-b for a, b in zip(du, continuous_du)]
    half_viscosity_error = [F(1, 20)*sum(v.d(j).d(j) for j in range(3)) for v in u]
    controls = dict(continuous_load_residual_l2_squared=volume(dot(force_error, force_error)),
        half_viscosity_residual_l2_squared=volume(dot(half_viscosity_error, half_viscosity_error)),
        omit_body_energy_defect=-energy['body'], omit_body_angular_defect=-ang['body'],
        omit_be_dissipation_interval_energy_defect=-dt*be_diss)
    assert all(scalar(v) != 0 for v in controls.values())
    assert scalar(diss) > 0 and scalar(be_diss) > 0
    values = dict(A=A.at(3, dt), C=C.at(3, dt), E=E.at(3, dt), H=H.at(3, dt),
        Q_minus=Q[0], Q_plus=Q[1], Q_lateral=lateral, P_minus=P[0], P_plus=P[1],
        pressure_mean=volume(p), divergence_squared=volume(sum(u[i].d(i) for i in range(3))**2),
        strain_l2_squared=volume(sum(v*v for row in strain for v in row)),
        kinetic_initial=k0, kinetic_final=k, angular_initial=l0, angular_final=l,
        be_energy_dissipation=be_diss)
    return dict(time='1/8', dt='1/8', exact={k: str(scalar(v)) for k, v in values.items()},
        energy_terms={k: str(scalar(v)) for k, v in energy.items()},
        angular_terms={k: str(scalar(v)) for k, v in ang.items()},
        negative_controls={k: str(scalar(v)) for k, v in controls.items()},
        exact_energy_defect='0', exact_angular_defect='0',
        exact_be_identity_defect='0', exact_flux_compatibility='0',
        interpretation='Exact-polynomial reference only; approximate pilot errors are unknown.')


def run():
    evidence = ROOT/'docs/realizability/evidence'
    saved = runpy.run_path(str(evidence/'r253/audit.py'))['run']()
    assert saved == json.loads((evidence/'r253/audit.json').read_text())
    targets = rotation_targets()
    prior = json.loads((evidence/'r247/audit.json').read_text())
    assert targets == prior['rotation_exact_targets'] and len(targets) == 38
    manifest = json.loads((ROOT/'verification/nonlinear_port/future_rotation.json').read_text())
    assert targets == manifest['contract']['raw_targets_rational']
    allocation = json.loads((evidence/'r251/allocation.json').read_text())
    for key, path in [('caller_sha256', evidence/'r251/run_once.py'),
                      ('source_inventory_sha256', evidence/'r251/source_inventory.json'),
                      ('artifact_inventory_sha256', evidence/'r251/artifacts.json')]:
        assert digest(path) == allocation[key]
    artifacts = json.loads((evidence/'r251/artifacts.json').read_text())
    for path, sha in artifacts['runtime_files_sha256'].items():
        assert digest(path) == sha, path
    for path, resolved in artifacts['library_resolutions'].items():
        assert str(Path(path).resolve(strict=True)) == resolved
    assert digest(artifacts['cached_archive']) == artifacts['package']['sha256']
    assert digest(Path(allocation['interpreter']).resolve(strict=True)) == allocation['executable_sha256']
    reference = manufactured_reference()
    proposal = json.loads((HERE/'proposal.json').read_text())
    old_manifest = json.loads((ROOT/'verification/nonlinear_port/future_fem.json').read_text())
    from verification.nonlinear_port.poiseuille_policy import RAW_KEYS, SIGNED_KEYS, NONNEGATIVE_KEYS
    from verification.nonlinear_port.linear_evidence import MAX_DOFS
    assert proposal['exact_reference'] == reference
    assert proposal['execution_admitted'] is False and proposal['attempts_granted'] == 0
    assert proposal['versions'] == old_manifest['versions']
    assert proposal['proposed_caps'] == old_manifest['proposed_caps']
    assert proposal['nonlinear'] == old_manifest['nonlinear']
    assert proposal['subdivisions'] == 2 and proposal['step'] == 1
    assert proposal['time'] == proposal['dt'] == .125
    assert proposal['rho'] == 1. and proposal['mu'] == .1
    assert proposal['degrees'] == [24, 26] and proposal['backflow_sampling_degree'] == 24
    policy = proposal['diagnostic_policy']
    assert policy['raw_keys'] == sorted(RAW_KEYS) and len(RAW_KEYS) == 30
    assert policy['signed_keys'] == sorted(SIGNED_KEYS) and len(SIGNED_KEYS) == 17
    assert policy['nonnegative_keys'] == sorted(NONNEGATIVE_KEYS) and len(NONNEGATIVE_KEYS) == 12
    assert (policy['relative'], policy['scale_floor'], policy['signed_absolute_floor']) == (1e-8, 1e-10, 1e-14)
    assert proposal['mixed_dofs'] == 402 and proposal['global_dofs'] == 405
    assert proposal['latest_system_dofs_max'] == MAX_DOFS == 512
    mesh_counts = {str(n): dict(mixed=3*(2*n+1)**3+(n+1)**3,
                               bordered=3*(2*n+1)**3+(n+1)**3+3) for n in (2, 4, 8)}
    assert mesh_counts['2']['bordered'] < MAX_DOFS < mesh_counts['4']['bordered']
    forbidden = {'numpy', 'dolfinx', 'basix', 'ufl', 'ffcx', 'petsc4py', 'mpi4py', 'scipy'}
    loaded = [m for m in sys.modules if m.split('.')[0] in forbidden]
    assert not loaded
    return dict(status='SOURCE_CONTRACT_READY_NO_ADMISSION', attempts_granted=0,
        r253_audit_reproduced=True, r253_status='PASS', r246_status='PASS', r242_status='INCOMPLETE',
        raw_originals_verified=74, spent_allocations=6, source_files_unchanged=36,
        runtime_artifacts_verified=len(artifacts['runtime_files_sha256']),
        library_resolutions_verified=len(artifacts['library_resolutions']),
        archive_and_interpreter_verified=True, rotation_targets_rederived=targets,
        saved_rotation_assembly_calls=76, saved_rotation_pair_checks=38,
        proposal_sha256=digest(HERE/'proposal.json'), mesh_family_dof_counts=mesh_counts,
        proposal_reference_verified=True,
        manufactured_reference=reference, numerical_modules_loaded=loaded,
        new_numerical_work=False, manager_connection=False)


if __name__ == '__main__':
    result = run()
    (HERE/'audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True))
