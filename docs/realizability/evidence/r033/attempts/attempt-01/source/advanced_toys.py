"""R022 high-order polynomial oracles and actual harmonic pre-solve observer."""
import argparse
import math
from pathlib import Path
import resource
import sys
import time

import numpy as np

import kernels
import physical
import presolve
import toy_runner as support

EPS = np.finfo(float).eps


def polynomial_cases(x, stack):
    """Identical polynomial specification for NumPy and independent UFL assembly."""
    a, b, c = x
    return [
        (stack((-b + .2*c, a + .1*c, -.2*a - .1*b)),
         stack((-.3*b + .1*c, .3*a + .4*c, -.1*a - .4*b))),
        (stack((1 + a + b*b, b + c*a, c + a*a)),
         stack((-b + c*c, a*a + b*c, 1 - a*c))),
    ]


def run(output):
    started = time.monotonic()
    record = dict(status='partial', stage='imports', physical_meshes=0,
        pde_solves=0, matrix_factorizations=0, matrix_solves=0,
        high_order=[], observer_cases=[], campaign_ready=False)
    def checkpoint(stage):
        record['stage'] = stage
        record['elapsed_seconds'] = time.monotonic() - started
        record['process_peak_rss_mib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        support.write_json(output / 'advanced-report.json', record)
    checkpoint('imports')
    try:
        sys.path.insert(0, str(Path.cwd()))
        support.verify_sources()
        import basix.ufl
        import ufl
        from dolfinx import fem, mesh
        from dolfinx.fem.petsc import assemble_matrix
        from mpi4py import MPI
        from petsc4py import PETSc
        from realizability.backends import hdiv_stokes as hdiv, fenicsx_stokes as base
        PETSc.Log.begin()
        ufl_domain = ufl.Mesh(basix.ufl.element('Lagrange', 'tetrahedron', 1, shape=(3,)))
        # A skew tetrahedron exercises the affine map without a physical mesh.
        skew = np.array([[.1, -.2, .05], [1.2, .1, -.1], [.2, .9, .2], [-.1, .2, 1.1]])
        domain = mesh.create_mesh(MPI.COMM_SELF, np.array([[0, 1, 2, 3]], dtype=np.int64),
                                 ufl_domain, skew)
        V, _ = hdiv.create_hdiv_spaces(domain)
        v = ufl.TestFunction(V)
        n, h = ufl.FacetNormal(domain), ufl.CellDiameter(domain)
        expressions = polynomial_cases(ufl.SpatialCoordinate(domain), ufl.as_vector)
        dofs = V.dofmap.cell_dofs(0)
        for case, parts in enumerate(expressions):
            calls = []
            def target(points):
                calls.append(len(points))
                assert len(points) <= 256
                real, imag = polynomial_cases(points.T, lambda x: np.column_stack(x))[case]
                return real + 1j*imag
            interpolated = []
            assembled = []
            for component, expr in enumerate(parts):
                fn = fem.Function(V)
                fn.interpolate(lambda x: (target(x.T).real if component == 0 else target(x.T).imag).T)
                interpolated.append(fn.x.array.copy())
                assembled.append(fem.assemble_vector(fem.form(1e-6 * (
                    -ufl.inner(ufl.outer(expr, n), ufl.grad(v)) + 96/h*ufl.inner(expr, v))*ufl.ds)).array.copy())
            expected_coeff = interpolated[0] + 1j*interpolated[1]
            ufl_load = assembled[0] + 1j*assembled[1]
            for order in presolve.ORDERS:
                row = dict(case=case, order=order, facets=[])
                record['high_order'].append(row)
                checkpoint('high_order_polynomial')
                total = np.zeros(len(ufl_load), dtype=complex)
                absolute = 0.
                for facet in range(4):
                    result = kernels.local_project_load(V, 0, facet, target, order, nu=1e-6)
                    wanted = expected_coeff[dofs[result['facet_dofs']]]
                    projection_error = float(np.max(abs(result['coefficients'] - wanted)))
                    projection_scale = float(np.sum(abs(wanted)) + np.sum(abs(result['coefficients'])))
                    triangle, normal, diameter = kernels.facet_geometry(V, 0, facet)
                    points, weights = kernels.duffy(triangle, 5)
                    basis, gradient = kernels.cell_basis(V, 0, points)
                    dn = np.einsum('pbij,j->pbi', gradient, normal)
                    terms = 1e-6 * weights[:, None] * np.einsum('pi,pbi->pb', target(points),
                        -dn + 96/diameter*basis)
                    direct = np.sum(terms, axis=0)
                    load_error = float(np.max(abs(result['load'] - direct)))
                    load_scale = float(np.sum(abs(terms)) + np.sum(result['absolute']))
                    facet_row = dict(facet=facet, projection_error=projection_error,
                        projection_tolerance=256*EPS*projection_scale,
                        weak_load_error=load_error, weak_load_tolerance=256*EPS*load_scale,
                        nonzero_complex_normal=bool(np.linalg.norm(result['coefficients'].real)>0
                                                   and np.linalg.norm(result['coefficients'].imag)>0))
                    row['facets'].append(facet_row)
                    checkpoint('high_order_polynomial')
                    assert projection_error <= facet_row['projection_tolerance']
                    assert load_error <= facet_row['weak_load_tolerance']
                    assert facet_row['nonzero_complex_normal']
                    total[dofs] += result['load']
                    absolute += float(np.sum(result['absolute']))
                    del result
                row['ufl_error'] = float(np.max(abs(total - ufl_load)))
                row['ufl_tolerance'] = 256*EPS*absolute
                row['maximum_target_batch'] = max(calls)
                assert row['ufl_error'] <= row['ufl_tolerance']
                assert row['maximum_target_batch'] <= 256
                checkpoint('high_order_polynomial')

        # Actual pinned harmonic block form on one reference tetrahedron.
        ref = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        checkpoint('before_reference_mesh_construction')
        domain = mesh.create_mesh(MPI.COMM_SELF, np.array([[0, 1, 2, 3]], dtype=np.int64),
                                 ufl_domain, ref)
        checkpoint('after_reference_mesh_construction')
        domain.topology.create_connectivity(2, 3)
        domain.topology.create_connectivity(3, 2)
        Vr, Qr = hdiv.create_hdiv_spaces(domain)
        Vi, Qi = hdiv.create_hdiv_spaces(domain)
        spaces = [Vr, Qr, Vi, Qi]
        ur, pr, ui, pi = [ufl.TrialFunction(s) for s in spaces]
        vr, qr, vi, qi = [ufl.TestFunction(s) for s in spaces]
        normal, diameter = ufl.FacetNormal(domain), ufl.CellDiameter(domain)
        alpha = fem.Constant(domain, 96.)
        nu, omega = 1e-6, 2*math.pi*.01
        forms = [
            [hdiv.sip_viscosity_form(ur, vr, normal, diameter, nu, alpha),
             -pr*ufl.div(vr)*ufl.dx, -omega*ufl.inner(ui, vr)*ufl.dx, None],
            [-qr*ufl.div(ur)*ufl.dx, None, None, None],
            [omega*ufl.inner(ur, vi)*ufl.dx, None,
             hdiv.sip_viscosity_form(ui, vi, normal, diameter, nu, alpha), -pi*ufl.div(vi)*ufl.dx],
            [None, None, -qi*ufl.div(ui)*ufl.dx, None],
        ]
        checkpoint('harmonic_forms_constructed')
        expressions = polynomial_cases(ufl.SpatialCoordinate(domain), ufl.as_vector)[0]
        def target(points):
            real, imag = polynomial_cases(points.T, lambda x: np.column_stack(x))[0]
            return real + 1j*imag
        def weak(expr, test):
            return nu*(-ufl.inner(ufl.outer(expr, normal), ufl.grad(test))
                       + alpha/diameter*ufl.inner(expr, test))*ufl.ds
        rhs_forms = [weak(expressions[0], vr), ufl.ZeroBaseForm((qr,)),
                     weak(expressions[1], vi), ufl.ZeroBaseForm((qi,))]
        exterior = mesh.exterior_facet_indices(domain.topology)
        expected = [fem.locate_dofs_topological(Vr, 2, exterior), np.empty(0, dtype=np.int32),
                    fem.locate_dofs_topological(Vi, 2, exterior), np.empty(0, dtype=np.int32)]
        sizes = [s.dofmap.index_map.size_local * s.dofmap.index_map_bs for s in spaces]
        offsets = np.cumsum([0, *sizes])
        targets, bcs = [], []
        for index, component in ((0, np.real), (2, np.imag)):
            fn = fem.Function(spaces[index])
            fn.interpolate(lambda x: component(target(x.T)).T)
            targets.append(fn)
            bcs.append(fem.dirichletbc(fn, expected[index]))
        # Independent unconstrained UFL matrix and load: a lifting oracle only.
        checkpoint('before_harmonic_form_compilation')
        compiled_forms = fem.form(forms)
        compiled_rhs_forms = [fem.form(form) for form in rhs_forms]
        checkpoint('after_harmonic_form_compilation')
        checkpoint('before_oracle_matrix_assembly')
        oracle_matrix = assemble_matrix(compiled_forms)
        oracle_matrix.assemble()
        checkpoint('after_oracle_matrix_assembly')
        indices = np.arange(offsets[-1], dtype=PETSc.IntType)
        dense = oracle_matrix.getValues(indices, indices)
        oracle_load = np.zeros(offsets[-1])
        checkpoint('before_oracle_load_assembly')
        for index in (0, 2):
            oracle_load[offsets[index]:offsets[index+1]] = fem.assemble_vector(compiled_rhs_forms[index]).array
        checkpoint('after_oracle_load_assembly')
        oracle_matrix.destroy()
        projection = np.zeros(sizes[0], dtype=complex)
        load = np.zeros(sizes[0], dtype=complex)
        signed, absolutes = [], []
        for facet in range(4):
            result = kernels.local_project_load(Vr, 0, facet, target, 4, nu=nu)
            dofs = Vr.dofmap.cell_dofs(0)
            projection[dofs[result['facet_dofs']]] = result['coefficients']
            load[dofs] += result['load']
            signed.append(result['signed_flux'])
            absolutes.append(result['absolute_flux'])
        total = complex(math.fsum(z.real for z in signed), math.fsum(z.imag for z in signed))
        denom = np.sum(absolutes, axis=0)
        ratios = [abs(total.real)/denom[0], abs(total.imag)/denom[1]]
        assert max(ratios) < 1e-8
        for injected in (None, 'P', 'A_64', 'A_96'):
            label = injected or 'compatible'
            case = dict(status='partial', stage='observer_start', primary_rhs=0,
                attempted_primary_solves=0, returned_primary_solves=0, correction_rhs=0,
                matrix_solves=0, physical_meshes=0, injections=[], oracle_checks=[])
            record['observer_cases'].append(case)
            checkpoint('observer_case_begin_' + label)
            prepared, captured, snapshots = {}, {}, {}
            def case_checkpoint(stage):
                case['stage'] = stage
                case['factor_counts'] = presolve.factor_counts()
                support.write_json(output / (label + '.json'), case)
                checkpoint('observer_' + label)
            def candidate_factory(name, local):
                local_targets, local_bcs = [], []
                for index, part in ((0, np.real), (2, np.imag)):
                    fn = fem.Function(local['spaces'][index])
                    fn.x.array[:] = part(projection)
                    local_targets.append(fn)
                    local_bcs.append(fem.dirichletbc(fn, expected[index]))
                return dict(bcs=local_bcs, targets=local_targets,
                    block_loads=[load.real, np.zeros(sizes[1]), load.imag, np.zeros(sizes[3])],
                    flux_ratios=ratios)
            def probe(name, vector, local):
                extension = np.zeros(offsets[-1])
                for index, target_fn in zip((0, 2), targets):
                    coeff = target_fn.x.array if name == 'P' else (
                        projection.real if index == 0 else projection.imag)
                    extension[offsets[index] + expected[index]] = coeff[expected[index]]
                oracle = oracle_load - dense @ extension
                constrained = np.r_[expected[0], offsets[2]+expected[2]]
                oracle[constrained] = extension[constrained]
                scale = float(np.sum(abs(oracle_load)) + np.sum(abs(dense)*abs(extension)[None, :])
                              + np.sum(abs(extension)))
                error = float(np.max(abs(vector.array - oracle)))
                pressure = np.r_[offsets[1]:offsets[2], offsets[3]:offsets[4]].astype(int)
                pressure_lift = float(np.linalg.norm(vector.array[pressure]-oracle_load[pressure]))
                case['oracle_checks'].append(dict(name=name, maximum_error=error,
                    tolerance=256*EPS*scale, pressure_lifting_norm=pressure_lift,
                    exact_essential=bool(np.array_equal(vector.array[constrained], extension[constrained]))))
                assert error <= 256*EPS*scale
                assert case['oracle_checks'][-1]['exact_essential'] and pressure_lift > 256*EPS*scale
                if name == injected:
                    # Injection occurs only in a copy; keep layout explicitly for this toy.
                    original_hash = presolve.vector_sha(vector)
                    copied = vector.copy()
                    copied.setAttr('_blocks', vector.getAttr('_blocks'))
                    amount = 16*256*EPS*float(vector.norm())
                    copied.axpy(amount, local['null_vectors'][0])
                    case['injections'].append(dict(name=name, amount=amount,
                        original_unchanged=presolve.vector_sha(vector)==original_hash))
                    snapshots[name] = (copied, presolve.vector_sha(copied))
                    return copied
                return vector
            try:
                presolve.call_with_barrier(base._block_direct_solve, captured,
                    (forms, rhs_forms, bcs, spaces, (1, 3), 'r022_toy_'), {},
                    expected, candidate_factory, prepared, case, case_checkpoint,
                    toy_stop=True, toy_probe=probe)
            except presolve.ToyPreparedStop as error:
                assert injected is None
                case['status'] = 'passed_toy_sentinel'
                case['sentinel'] = str(error)
                assert list(prepared) == ['A_64', 'A_96']
                assert case['completed_rhs_assemblies'] == 3
            except RuntimeError as error:
                assert injected is not None
                assert str(error) == 'Primal pressure compatibility failed before solve'
                assert case['stage'] == injected + '_primary_rhs_compatibility'
                candidate, digest = snapshots[injected]
                assert presolve.vector_sha(candidate) == digest
                expected_count = {'P': 1, 'A_64': 2, 'A_96': 3}[injected]
                assert case['completed_rhs_assemblies'] == expected_count
                assert len(case['candidates']) == expected_count
                case['status'] = 'passed_expected_refusal'
                case['error'] = str(error)
                case['failed_raw_unchanged'] = True
            else:
                raise AssertionError('Toy crossed the pre-solve sentinel')
            assert case['pre_solve_observer']['calls'] == 1
            assert case['attempted_primary_solves'] == case['matrix_solves'] == 0
            assert all(value == 0 for value in presolve.factor_counts().values())
            case_checkpoint('observer_case_complete_' + label)
        record['factor_counts'] = presolve.factor_counts()
        record['status'] = 'passed'
        checkpoint('advanced_toys_complete')
    except Exception as error:
        record['status'] = 'partial_failed'
        record['error'] = dict(type=type(error).__name__, message=str(error))
        checkpoint(record['stage'])
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    run(args.output)
