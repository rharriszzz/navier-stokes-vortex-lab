"""R015 toy-only tests for disposable R014 wrapper repairs."""
import json
import math
from pathlib import Path
import resource
import time

import numpy as np

import physical
import toy_runner as support


def run(output):
    from dolfinx import fem, mesh
    from mpi4py import MPI
    from petsc4py import PETSc
    import basix.ufl
    import ufl

    started = time.monotonic()
    repository_root = Path(__file__).resolve().parents[4]
    record = dict(status='partial', stage='imports', campaign_ready=False,
                  physical_meshes=0, pde_solves=0, matrix_factorizations=0,
                  primary_rhs=0, returned_primary_solves=0, correction_rhs=0,
                  matrix_solves=0, source_sha256={},
                  source_archive_sha256=support.sha(Path(__file__).with_name('physical.py')))

    def checkpoint(stage):
        record['stage'] = stage
        record['elapsed_seconds'] = time.monotonic() - started
        record['process_peak_rss_mib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
        support.write_json(output / 'toy-repair-report.json', record)

    checkpoint('imports')
    try:
        production_hashes = {name: support.sha(repository_root / name)
                             for name in support.EXPECTED_SOURCES}
        if production_hashes != support.EXPECTED_SOURCES:
            raise RuntimeError('Pinned production source identity mismatch')
        record['source_sha256'] = production_hashes
        checkpoint('production_source_hashes_verified')
        ref = np.array([[0., 0., 0.], [1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        domain = mesh.create_mesh(MPI.COMM_SELF, np.array([[0, 1, 2, 3]], dtype=np.int64),
            ufl.Mesh(basix.ufl.element('Lagrange', 'tetrahedron', 1, shape=(3,))), ref)
        domain.topology.create_connectivity(2, 3)
        domain.topology.create_connectivity(3, 2)
        element_v = basix.ufl.element('BDM', 'tetrahedron', 2, shape=(3,))
        element_q = basix.ufl.element('Lagrange', 'tetrahedron', 1, discontinuous=True)
        spaces = [fem.functionspace(domain, element_v), fem.functionspace(domain, element_q),
                  fem.functionspace(domain, element_v), fem.functionspace(domain, element_q)]
        exterior = mesh.exterior_facet_indices(domain.topology)
        expected = [np.empty(0, dtype=np.int32) for _ in spaces]
        expected[0] = fem.locate_dofs_topological(spaces[0], 2, exterior)
        expected[2] = fem.locate_dofs_topological(spaces[2], 2, exterior)
        sizes = [space.dofmap.index_map.size_local * space.dofmap.index_map_bs for space in spaces]
        offsets = np.cumsum([0, *sizes])
        a_ufl = [[None for _ in spaces] for _ in spaces]
        for index, space in enumerate(spaces):
            trial, test = ufl.TrialFunction(space), ufl.TestFunction(space)
            a_ufl[index][index] = ufl.inner(trial, test) * ufl.dx
        grouping_spaces = fem.extract_function_spaces(fem.form(a_ufl), 1)
        target_sets = []
        bc_sets = []
        for real_value, imaginary_value in ((0.0, 0.0), (0.125, -0.375)):
            targets = []
            bcs = []
            for index, value_scalar in ((0, real_value), (2, imaginary_value)):
                value = fem.Function(spaces[index])
                value.x.array[:] = value_scalar
                targets.append(value)
                bcs.append(fem.dirichletbc(value, expected[index]))
            target_sets.append(targets)
            bc_sets.append(bcs)
        groups, global_sets, local_sets = physical.collect_constraints(
            fem, spaces, bc_sets[1], offsets, expected, grouping_spaces)
        counts = [len(row) for row in local_sets]
        assert counts == [24, 0, 24, 0], counts
        assert sizes[0] - counts[0] == 6 and sizes[2] - counts[2] == 6
        assert all(len(groups[i]) == 1 for i in (0, 2)) and not groups[1] and not groups[3]
        assignment_results = []
        for case_index, case_bcs in enumerate(bc_sets):
            case_groups, case_global_sets, case_local_sets = physical.collect_constraints(
                fem, spaces, case_bcs, offsets, expected, grouping_spaces)
            flat = np.full(offsets[-1], -9.0)
            for index in (0, 2):
                for bc in case_groups[index]:
                    bc.set(flat[offsets[index]:offsets[index + 1]])
                wanted = target_sets[case_index][0 if index == 0 else 1].x.array[case_local_sets[index]]
                assert np.array_equal(flat[case_global_sets[index]], wanted)
                free = np.setdiff1d(np.arange(sizes[index]), case_local_sets[index])
                assert np.all(flat[offsets[index] + free] == -9.0)
            assignment_results.append(dict(real_value=[0.0, 0.125][case_index],
                                            imaginary_value=[0.0, -0.375][case_index],
                                            exact=True))
        frozen = [item.copy() for item in global_sets]
        assert all(np.array_equal(a, b) for a, b in zip(frozen, global_sets))
        record['tetrahedron'] = dict(block_sizes=sizes, offsets=offsets.tolist(),
            constrained_dofs_per_block=counts, velocity_free_interior_dofs=[6, 6],
            pressure_constraints=0, exact_assignment=True, unchanged_constraint_sets=True,
            complex_target_assignment=assignment_results)
        checkpoint('tetrahedron_constraints_passed')

        def must_refuse(candidate_bcs, label):
            try:
                physical.collect_constraints(fem, spaces, candidate_bcs, offsets, expected, grouping_spaces)
            except (RuntimeError, ValueError, IndexError):
                return dict(case=label, refused=True)
            raise AssertionError(label + ' did not refuse')

        missing = must_refuse([bcs[0]], 'missing imaginary block')
        wrong_space = fem.functionspace(domain, element_v)
        wrong_value = fem.Function(wrong_space)
        wrong_bc = fem.dirichletbc(wrong_value, fem.locate_dofs_topological(wrong_space, 2, exterior))
        wrong = must_refuse([bcs[0], wrong_bc], 'wrong-space block')
        record['refusal_cases'] = [missing, wrong]
        checkpoint('group_refusals_passed')

        compatible_path = output / 'synthetic-compatible-pressure.json'
        compatible_record = dict(status='partial', matrix_solves=0)
        def compatible_checkpoint(stage):
            compatible_record['stage'] = stage
            support.write_json(compatible_path, compatible_record)
        compatible_rhs = PETSc.Vec().createSeq(2, comm=MPI.COMM_SELF)
        compatible_rhs.array[:] = [0.0, 2.0]
        compatible_null = PETSc.Vec().createSeq(2, comm=MPI.COMM_SELF)
        compatible_null.array[:] = [1.0, 0.0]
        physical.record_compatibility(compatible_rhs, [compatible_null], compatible_record,
            compatible_checkpoint, 'pressure_compatibility', 'synthetic_compatible_pressure')
        persisted_compatible = support.read_json(compatible_path)
        assert persisted_compatible['pressure_compatibility']['pressure_constant_products_before'] == [0.0]
        assert persisted_compatible['pressure_compatibility']['removed_norm'] == 0.0

        compat_path = output / 'synthetic-compatibility-failure.json'
        failure_record = dict(status='partial', matrix_solves=0)
        def compat_checkpoint(stage):
            failure_record['stage'] = stage
            support.write_json(compat_path, failure_record)
        rhs = PETSc.Vec().createSeq(2, comm=MPI.COMM_SELF)
        rhs.array[:] = [1.0, 2.0]
        null = PETSc.Vec().createSeq(2, comm=MPI.COMM_SELF)
        null.array[:] = [1.0, 0.0]
        try:
            physical.record_compatibility(rhs, [null], failure_record, compat_checkpoint,
                                          'pressure_compatibility', 'synthetic_compatibility')
        except RuntimeError as error:
            failure_record['error'] = dict(type=type(error).__name__, message=str(error))
        else:
            raise AssertionError('incompatible synthetic RHS was accepted')
        persisted = support.read_json(compat_path)
        assert persisted['pressure_compatibility']['pressure_constant_products_before'] == [1.0]
        assert persisted['pressure_compatibility']['removed_norm'] == 1.0
        assert persisted['pressure_compatibility']['rhs_norm'] == math.sqrt(5.0)

        bookkeeping_path = output / 'synthetic-return-checkpoint.json'
        bookkeeping = dict(status='partial', matrix_solves=0, returned_primary_solves=0)
        def book_checkpoint(stage):
            bookkeeping['stage'] = stage
            support.write_json(bookkeeping_path, bookkeeping)
        try:
            physical.record_returned_solve(bookkeeping, book_checkpoint, 'synthetic_solver_returned',
                                           lambda: {'symbolic': 1, 'numeric': 1, 'solve': 1})
            raise RuntimeError('synthetic post-return bookkeeping failure')
        except RuntimeError as error:
            bookkeeping['error'] = dict(type=type(error).__name__, message=str(error))
            support.write_json(bookkeeping_path, bookkeeping)
        persisted = support.read_json(bookkeeping_path)
        assert persisted['stage'] == 'synthetic_solver_returned'
        assert persisted['returned_primary_solves'] == persisted['matrix_solves'] == 1
        assert persisted['factor_counts_at_return'] == {'symbolic': 1, 'numeric': 1, 'solve': 1}
        record['pressure_compatibility_fixtures'] = dict(compatible_accepted=True,
            incompatible_refused=True, compatible_removed_norm=0.0,
            incompatible_removed_norm=1.0)
        record['failure_reporting'] = dict(compatibility_pre_removal_persisted=True,
            returned_solve_and_factor_counts_persisted=True)
        record['status'] = 'passed'
        checkpoint('toy_repair_complete')
    except Exception as error:
        record['status'] = 'partial_failed'
        record['error'] = dict(type=type(error).__name__, message=str(error))
        checkpoint(record['stage'])
        raise


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    run(args.output)
