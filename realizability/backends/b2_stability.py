"""Bounded cylinder energy audit for the B2 SIP discretization.

This diagnostic deliberately uses dense linear algebra only after rejecting
meshes with too many free BDM degrees of freedom.  It tests the dissipative
velocity operator in its mass metric; it is not a production eigensolver.
"""

from __future__ import annotations

from dataclasses import asdict
import math
import resource
import time
from typing import Any

import numpy as np

from ..config import PilotConfig
from .fenicsx_stokes import _block_direct_solve, _mesh_sha256, solver_versions
from .hdiv_stokes import create_hdiv_spaces, sip_viscosity_form


def _dense(form) -> np.ndarray:
    """Assemble a serial PETSc matrix as a NumPy array for a guarded audit."""

    from dolfinx import fem
    from dolfinx.fem import petsc as fem_petsc

    matrix = fem_petsc.assemble_matrix(fem.form(form))
    matrix.assemble()
    rows, columns = matrix.getSize()
    indices_row = np.arange(rows, dtype=np.int32)
    indices_column = np.arange(columns, dtype=np.int32)
    value = matrix.getValues(indices_row, indices_column)
    matrix.destroy()
    return value


def _relative(numerator: float, denominator: float) -> float:
    return float(numerator / max(denominator, np.finfo(float).tiny))


def _backward_euler_step(V, Q, initial, normal, cell_size, viscosity, penalty_factor, constrained):
    """Take one unforced constrained Stokes step from an audit eigenvector."""

    from dolfinx import fem
    import ufl

    trial, test = ufl.TrialFunction(V), ufl.TestFunction(V)
    pressure, pressure_test = ufl.TrialFunction(Q), ufl.TestFunction(Q)
    zero = fem.Function(V)
    boundary_condition = fem.dirichletbc(zero, constrained)
    time_step = 1.0
    lhs = [
        [
            ufl.inner(trial, test) / time_step * ufl.dx
            + sip_viscosity_form(trial, test, normal, cell_size, viscosity, penalty_factor),
            -pressure * ufl.div(test) * ufl.dx,
        ],
        [-pressure_test * ufl.div(trial) * ufl.dx, None],
    ]
    rhs = [ufl.inner(initial / time_step, test) * ufl.dx, ufl.ZeroBaseForm((pressure_test,))]
    (after, _), _, residual, _, nullspace = _block_direct_solve(
        lhs, rhs, [boundary_condition], [V, Q], (1,), "b2_energy_decay_"
    )
    del nullspace
    return after, time_step, residual


def run_cylinder_stability_audit(
    config: PilotConfig,
    mesh_sizes: tuple[float, ...] = (0.10, 0.07),
    penalty_factors: tuple[float, ...] = (6.0, 48.0),
    *,
    max_free_velocity_dofs: int = 3000,
    include_backward_euler: bool = True,
) -> dict[str, Any]:
    """Check energy dissipation on small cylinder fixtures in a mass metric.

    Exterior normal BDM trace degrees of freedom are removed before the
    divergence-free restriction is constructed.  A negative generalized
    eigenvalue means the unforced semidiscrete operator adds kinetic energy.
    """

    if not mesh_sizes or not penalty_factors:
        raise ValueError("mesh_sizes and penalty_factors must not be empty.")
    if any(size <= 0.0 for size in mesh_sizes) or any(alpha <= 0.0 for alpha in penalty_factors):
        raise ValueError("mesh sizes and penalty factors must be positive.")
    if max_free_velocity_dofs < 1:
        raise ValueError("max_free_velocity_dofs must be positive.")

    try:
        import scipy
        import scipy.linalg as linear_algebra
        from dolfinx import fem, mesh as dolfinx_mesh
        import ufl
    except ImportError as error:  # pragma: no cover - optional environment
        raise RuntimeError("The B2 cylinder stability audit requires the optional DOLFINx/SciPy environment.") from error

    from .fenicsx_stokes import create_cylinder, require_fenicsx

    require_fenicsx()
    results: list[dict[str, Any]] = []
    for mesh_size in mesh_sizes:
        started = time.perf_counter()
        mesh, _, _ = create_cylinder(config, mesh_size)
        if mesh.comm.size != 1:
            raise RuntimeError("The dense B2 cylinder stability audit is serial only.")
        V, Q = create_hdiv_spaces(mesh)
        trial, test = ufl.TrialFunction(V), ufl.TestFunction(V)
        pressure_test = ufl.TestFunction(Q)
        normal = ufl.FacetNormal(mesh)
        cell_size = ufl.CellDiameter(mesh)
        mesh.topology.create_connectivity(mesh.topology.dim - 1, mesh.topology.dim)
        constrained = fem.locate_dofs_topological(
            V, mesh.topology.dim - 1, dolfinx_mesh.exterior_facet_indices(mesh.topology)
        )
        all_dofs = np.arange(V.dofmap.index_map.size_global * V.dofmap.index_map_bs, dtype=np.int32)
        free = np.setdiff1d(all_dofs, constrained, assume_unique=False)
        if free.size > max_free_velocity_dofs:
            raise ValueError(
                f"Mesh {mesh_size:g} m has {free.size} free velocity DOFs; audit limit is {max_free_velocity_dofs}."
            )
        divergence = _dense(-pressure_test * ufl.div(trial) * ufl.dx)[:, free]
        nullspace = linear_algebra.null_space(divergence)
        if nullspace.shape[1] == 0:
            raise RuntimeError("No discrete divergence-free velocity DOFs remain in the audit fixture.")
        mass = _dense(ufl.inner(trial, test) * ufl.dx)[np.ix_(free, free)]
        projected_mass = nullspace.T @ mass @ nullspace
        cases: list[dict[str, Any]] = []
        for penalty_factor in penalty_factors:
            viscous = _dense(
                sip_viscosity_form(
                    trial, test, normal, cell_size, config.fluid.kinematic_viscosity, penalty_factor
                )
            )[np.ix_(free, free)]
            projected_viscous = nullspace.T @ viscous @ nullspace
            symmetric_viscous = 0.5 * (projected_viscous + projected_viscous.T)
            symmetric_mass = 0.5 * (projected_mass + projected_mass.T)
            eigenvalues, eigenvectors = linear_algebra.eigh(
                symmetric_viscous, symmetric_mass, subset_by_index=(0, 0)
            )
            decay_rate = float(eigenvalues[0])
            vector = eigenvectors[:, 0]
            coefficient = nullspace @ vector
            field = fem.Function(V)
            field.x.array[free] = coefficient
            field.x.scatter_forward()
            velocity_mass = float(fem.assemble_scalar(fem.form(ufl.inner(field, field) * ufl.dx)))
            divergence_l2_squared = float(fem.assemble_scalar(fem.form(ufl.div(field) ** 2 * ufl.dx)))
            boundary_normal_squared = float(
                fem.assemble_scalar(fem.form(ufl.dot(field, normal) ** 2 * ufl.ds))
            )
            direct_quadratic = float(
                fem.assemble_scalar(
                    fem.form(
                        sip_viscosity_form(
                            field, field, normal, cell_size, config.fluid.kinematic_viscosity, penalty_factor
                        )
                    )
                )
            )
            eigenpair_residual = _relative(
                float(np.linalg.norm(projected_viscous @ vector - decay_rate * (projected_mass @ vector))),
                float(np.linalg.norm(projected_viscous @ vector)
                      + abs(decay_rate) * np.linalg.norm(projected_mass @ vector)),
            )
            case: dict[str, Any] = {
                "penalty_factor": float(penalty_factor),
                "minimum_decay_rate_per_s": decay_rate,
                "projected_matrix_symmetry_relative_error": _relative(
                    float(np.linalg.norm(projected_viscous - projected_viscous.T)),
                    float(np.linalg.norm(projected_viscous)),
                ),
                "eigenpair_relative_residual": eigenpair_residual,
                "velocity_mass": velocity_mass,
                "divergence_ratio": config.geometry.radius * math.sqrt(
                    max(divergence_l2_squared / max(velocity_mass, np.finfo(float).tiny), 0.0)
                ),
                "boundary_normal_l2": math.sqrt(max(boundary_normal_squared, 0.0)),
                "assembled_rayleigh_per_s": direct_quadratic / max(velocity_mass, np.finfo(float).tiny),
                "quadratic_form_absolute_error_per_s": abs(
                    direct_quadratic / max(velocity_mass, np.finfo(float).tiny) - decay_rate
                ),
            }
            if include_backward_euler and math.isclose(mesh_size, mesh_sizes[-1]):
                after, time_step, solve_residual = _backward_euler_step(
                    V, Q, field, normal, cell_size, config.fluid.kinematic_viscosity,
                    penalty_factor, constrained,
                )
                after_mass = float(fem.assemble_scalar(fem.form(ufl.inner(after, after) * ufl.dx)))
                case["backward_euler"] = {
                    "time_step_s": time_step,
                    "measured_energy_ratio": after_mass / max(velocity_mass, np.finfo(float).tiny),
                    "predicted_energy_ratio": 1.0 / (1.0 + time_step * decay_rate) ** 2,
                    "step_algebraic_residual": solve_residual,
                }
            case["stability_checks_passed"] = bool(
                decay_rate > 0.0
                and case["projected_matrix_symmetry_relative_error"] < 1.0e-12
                and eigenpair_residual < 1.0e-9
                and case["divergence_ratio"] < 1.0e-10
                and case["boundary_normal_l2"] < 1.0e-10
                and case["quadratic_form_absolute_error_per_s"] < 1.0e-10
            )
            cases.append(case)
        results.append(
            {
                "mesh_size_m": float(mesh_size),
                "cells": int(mesh.topology.index_map(mesh.topology.dim).size_global),
                "mesh_sha256": _mesh_sha256(mesh),
                "free_velocity_dofs": int(free.size),
                "divergence_free_velocity_dofs": int(nullspace.shape[1]),
                "divergence_nullspace_relative_residual": _relative(
                    float(np.linalg.norm(divergence @ nullspace)), float(np.linalg.norm(divergence))
                ),
                "penalty_cases": cases,
                "elapsed_seconds": time.perf_counter() - started,
                "peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
            }
        )
    return {
        "schema_version": 1,
        "claim": "Bounded B2 cylinder energy audit; it does not certify a production mesh or response accuracy.",
        "configuration": config.as_dict(),
        "audit_mesh_sizes_m": [float(size) for size in mesh_sizes],
        "penalty_factors": [float(value) for value in penalty_factors],
        "max_free_velocity_dofs": max_free_velocity_dofs,
        "mass_metric": "Z^T A Z y = lambda Z^T M Z y after exterior normal-trace elimination.",
        "solver_versions": asdict(solver_versions()),
        "scipy_version": scipy.__version__,
        "mesh_results": results,
        "all_requested_cases_stable": all(
            case["stability_checks_passed"]
            for result in results
            for case in result["penalty_cases"]
        ),
    }


def format_cylinder_stability_audit(report: dict[str, Any]) -> str:
    """Render the bounded audit alongside its strict JSON record."""

    lines = [
        "# B2 cylinder energy-stability audit",
        "",
        report["claim"],
        "",
        f"All requested cases stable: **{report['all_requested_cases_stable']}**",
        "",
        "| Mesh (m) | Penalty | Minimum decay rate (1/s) | Stable |",
        "|---:|---:|---:|:---:|",
    ]
    for mesh in report["mesh_results"]:
        for case in mesh["penalty_cases"]:
            lines.append(
                f"| {mesh['mesh_size_m']:g} | {case['penalty_factor']:g} | "
                f"{case['minimum_decay_rate_per_s']:.12g} | {case['stability_checks_passed']} |"
            )
    return "\n".join(lines) + "\n"
