"""Divergence-conforming Stokes discretization for B2 response gates.

This backend uses Brezzi--Douglas--Marini velocity and discontinuous pressure
spaces.
The viscous term follows the symmetric interior-penalty formulation in the
official DOLFINx divergence-conforming Navier--Stokes demo.  It is separate
from the B1 Taylor--Hood verification backend so the change of discretization
is explicit and can be cross-checked rather than silently replacing B1.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np

from ..boundary_modes import parse_mode
from ..config import PilotConfig
from .fenicsx_stokes import (
    CAP_TAG,
    SIDE_TAG,
    BoundaryInputDiagnostics,
    _block_direct_solve,
    _boundary_flux,
    _boundary_residual,
    _correct_boundary_flux,
    _field_norms,
    _global_scalar,
    _mesh_sha256,
    _mode_expression,
    _return_expression,
    _velocity_boundary_conditions,
    create_cylinder,
    require_fenicsx,
)


@dataclass(frozen=True)
class HdivComponentDiagnostics:
    velocity_l2: float
    pressure_l2: float
    divergence_l2: float
    divergence_ratio: float
    algebraic_residual: float
    boundary_dof_residual: float


@dataclass(frozen=True)
class BoundaryTraceDiagnostics:
    """Facet-wise weak-boundary diagnostics, normalized by the command scale."""

    side_tangential_relative_l2: float
    cap_tangential_relative_l2: float
    target_normal_mismatch_relative_l2: float
    actual_side_normal_relative_l2: float
    actual_cap_normal_relative_l2: float
    interior_tangential_jump_relative_l2: float


@dataclass(frozen=True)
class HdivHarmonicResult:
    mode: str
    frequency_hz: float
    mesh_size: float
    cells: int
    velocity_dofs: int
    pressure_dofs: int
    mesh_sha256: str
    flux_correction_coefficient: float
    corrected_flux_ratio: float
    input_diagnostics: BoundaryInputDiagnostics
    real_boundary_trace: BoundaryTraceDiagnostics
    imaginary_boundary_trace: BoundaryTraceDiagnostics
    elapsed_seconds: float
    real: HdivComponentDiagnostics
    imaginary: HdivComponentDiagnostics
    formulation: str = "BDM2/DG1 divergence-conforming SIP Stokes"

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def create_hdiv_spaces(mesh):
    """Create BDM2 velocity and discontinuous P1 pressure spaces."""

    from basix.ufl import element
    from dolfinx import default_real_type, fem

    velocity_element = element("BDM", mesh.basix_cell(), degree=2, dtype=default_real_type)
    pressure_element = element(
        "Lagrange",
        mesh.basix_cell(),
        degree=1,
        discontinuous=True,
        dtype=default_real_type,
    )
    return fem.functionspace(mesh, velocity_element), fem.functionspace(mesh, pressure_element)


def _jump(vector, normal):
    """Tensor jump used by the H(div) interior-penalty viscous form."""

    import ufl

    return ufl.outer(vector("+"), normal("+")) + ufl.outer(vector("-"), normal("-"))


def sip_viscosity_form(trial, test, normal, cell_size, viscosity, alpha):
    """Return the shared BDM SIP viscous bilinear form.

    ``alpha`` is the dimensionless penalty coefficient.  This helper is used
    by both the production harmonic solve and the small-mesh stability audit.
    """

    import ufl

    return viscosity * (
        ufl.inner(ufl.grad(trial), ufl.grad(test)) * ufl.dx
        - ufl.inner(ufl.avg(ufl.grad(trial)), _jump(test, normal)) * ufl.dS
        - ufl.inner(_jump(trial, normal), ufl.avg(ufl.grad(test))) * ufl.dS
        + alpha / ufl.avg(cell_size) * ufl.inner(_jump(trial, normal), _jump(test, normal)) * ufl.dS
        - ufl.inner(ufl.grad(trial), ufl.outer(test, normal)) * ufl.ds
        - ufl.inner(ufl.outer(trial, normal), ufl.grad(test)) * ufl.ds
        + alpha / cell_size * ufl.inner(ufl.outer(trial, normal), ufl.outer(test, normal)) * ufl.ds
    )


def _input_diagnostics(
    boundary_target,
    boundary_normal,
    facet_tags,
    config: PilotConfig,
    frequency_hz: float,
    normal_mode: bool,
) -> BoundaryInputDiagnostics:
    """Measure the physical target speed and the actual essential normal trace."""

    from dolfinx import fem
    import ufl

    mesh = boundary_target.function_space.mesh
    measure = ufl.Measure("ds", domain=mesh, subdomain_data=facet_tags)
    normal = ufl.FacetNormal(mesh)
    side_area = _global_scalar(
        mesh, fem.assemble_scalar(fem.form(1.0 * measure(SIDE_TAG)))
    )
    speed_squared = _global_scalar(
        mesh,
        fem.assemble_scalar(
            fem.form(ufl.inner(boundary_target, boundary_target) * measure(SIDE_TAG))
        ),
    )
    normal_velocity = ufl.dot(boundary_normal, normal)
    inward_flow = _global_scalar(
        mesh,
        fem.assemble_scalar(
            fem.form(0.5 * (abs(normal_velocity) - normal_velocity) * measure(SIDE_TAG))
        ),
    )
    facet_dimension = mesh.topology.dim - 1
    side_dofs = fem.locate_dofs_topological(
        boundary_target.function_space, facet_dimension, facet_tags.find(SIDE_TAG)
    )
    block_size = boundary_target.function_space.dofmap.bs
    scalar_dofs = (block_size * side_dofs[:, None] + np.arange(block_size)[None, :]).ravel()
    vectors = boundary_target.x.array[scalar_dofs].reshape(-1, block_size)
    peak = float(np.max(np.linalg.norm(vectors, axis=1))) if vectors.size else 0.0
    omega = 2.0 * math.pi * frequency_hz
    return BoundaryInputDiagnostics(
        peak,
        math.sqrt(max(speed_squared / side_area, 0.0)),
        inward_flow,
        None if normal_mode else peak / omega,
        omega * peak,
        "not assessed",
        "not assessed",
    )


def _mode_ufl(mode, config: PilotConfig, coordinate):
    """Return the smooth cylindrical command as a UFL vector expression.

    This is used only on exterior facets.  Keeping it symbolic lets the
    Nitsche target use each planar facet normal rather than a nodal normal
    averaged at edges of the faceted cylinder.
    """

    import ufl

    radius = ufl.sqrt(coordinate[0] ** 2 + coordinate[1] ** 2)
    radial_x = coordinate[0] / radius
    radial_y = coordinate[1] / radius
    cosine, sine = 1.0, 0.0
    for _ in range(mode.m):
        cosine, sine = cosine * radial_x - sine * radial_y, sine * radial_x + cosine * radial_y
    angular = cosine if mode.phase == "c" else sine
    s = coordinate[2] / config.geometry.half_height
    window = (1.0 - s**2) ** 2
    if mode.k == 0:
        axial = window
    elif mode.k == 1:
        axial = s * window
    elif mode.k == 2:
        axial = (s**2 - 1.0 / 7.0) * window
    else:  # parse_mode currently excludes this, but keep the invariant local.
        raise ValueError(f"Unsupported axial mode index {mode.k}.")
    scalar = angular * axial / mode.peak_raw_amplitude
    if mode.is_normal:
        return scalar * ufl.as_vector((radial_x, radial_y, 0.0))
    return scalar * ufl.as_vector((-radial_y, radial_x, 0.0))


def _boundary_trace_diagnostics(
    field,
    smooth_target,
    imposed_normal,
    facet_tags,
    command_speed: float,
) -> BoundaryTraceDiagnostics:
    """Measure facet-consistent target, trace, and tangential-jump errors."""

    from dolfinx import fem
    import ufl

    mesh = field.function_space.mesh
    normal = ufl.FacetNormal(mesh)
    ds = ufl.Measure("ds", domain=mesh, subdomain_data=facet_tags)
    dS = ufl.Measure("dS", domain=mesh)
    side_area = _global_scalar(mesh, fem.assemble_scalar(fem.form(1.0 * ds(SIDE_TAG))))
    cap_area = _global_scalar(mesh, fem.assemble_scalar(fem.form(1.0 * ds(CAP_TAG))))
    interior_area = _global_scalar(mesh, fem.assemble_scalar(fem.form(1.0 * dS)))
    scale = max(command_speed, np.finfo(float).tiny)

    def tangent(value):
        return value - ufl.dot(value, normal) * normal

    consistent_target = tangent(smooth_target) + ufl.dot(imposed_normal, normal) * normal
    side_tangent = _global_scalar(
        mesh, fem.assemble_scalar(fem.form(ufl.inner(tangent(field - consistent_target), tangent(field - consistent_target)) * ds(SIDE_TAG)))
    )
    cap_tangent = _global_scalar(
        mesh, fem.assemble_scalar(fem.form(ufl.inner(tangent(field), tangent(field)) * ds(CAP_TAG)))
    )
    target_normal = _global_scalar(
        mesh, fem.assemble_scalar(fem.form((ufl.dot(smooth_target - imposed_normal, normal)) ** 2 * ds(SIDE_TAG)))
    )
    side_normal = _global_scalar(
        mesh, fem.assemble_scalar(fem.form((ufl.dot(field - imposed_normal, normal)) ** 2 * ds(SIDE_TAG)))
    )
    cap_normal = _global_scalar(
        mesh, fem.assemble_scalar(fem.form((ufl.dot(field, normal)) ** 2 * ds(CAP_TAG)))
    )
    jump_value = ufl.jump(field)
    tangent_jump = jump_value - ufl.dot(jump_value, normal("+")) * normal("+")
    interior_jump = _global_scalar(
        mesh, fem.assemble_scalar(fem.form(ufl.inner(tangent_jump, tangent_jump) * dS))
    )
    return BoundaryTraceDiagnostics(
        math.sqrt(max(side_tangent / max(side_area, np.finfo(float).tiny), 0.0)) / scale,
        math.sqrt(max(cap_tangent / max(cap_area, np.finfo(float).tiny), 0.0)) / scale,
        math.sqrt(max(target_normal / max(side_area, np.finfo(float).tiny), 0.0)) / scale,
        math.sqrt(max(side_normal / max(side_area, np.finfo(float).tiny), 0.0)) / scale,
        math.sqrt(max(cap_normal / max(cap_area, np.finfo(float).tiny), 0.0)) / scale,
        math.sqrt(max(interior_jump / max(interior_area, np.finfo(float).tiny), 0.0)) / scale,
    )
def affine_reaction_verification(
    resolution: int = 3,
    strain: float = 0.07,
    rotation: float = -0.11,
    *,
    penalty_factor: float = 6.0,
) -> dict[str, float]:
    """Verify the H(div) SIP form against an exactly represented affine flow.

    A unit reaction term and matching manufactured volume source remove any
    steady SIP kernel.  The source is confined to this verification fixture.
    """

    require_fenicsx()
    if resolution < 1:
        raise ValueError("resolution must be positive.")

    from basix.ufl import element
    from dolfinx import default_real_type, fem, mesh as dmesh
    from mpi4py import MPI
    import ufl

    domain = dmesh.create_unit_cube(MPI.COMM_WORLD, resolution, resolution, resolution)
    V, Q = create_hdiv_spaces(domain)
    u, p = ufl.TrialFunction(V), ufl.TrialFunction(Q)
    v, q = ufl.TestFunction(V), ufl.TestFunction(Q)
    normal = ufl.FacetNormal(domain)
    cell_size = ufl.CellDiameter(domain)
    alpha = fem.Constant(domain, float(penalty_factor))
    viscosity = 1.0

    def affine_expression(x: np.ndarray) -> np.ndarray:
        return np.vstack(
            (
                -strain * x[0] - rotation * x[1],
                -strain * x[1] + rotation * x[0],
                2.0 * strain * x[2],
            )
        )

    boundary_normal = fem.Function(V)
    boundary_normal.interpolate(affine_expression)
    target_element = element(
        "Lagrange",
        domain.basix_cell(),
        degree=2,
        shape=(domain.geometry.dim,),
        dtype=default_real_type,
    )
    target_space = fem.functionspace(domain, target_element)
    boundary_target = fem.Function(target_space)
    boundary_target.interpolate(affine_expression)
    domain.topology.create_connectivity(domain.topology.dim - 1, domain.topology.dim)
    facets = dmesh.exterior_facet_indices(domain.topology)
    boundary_dofs = fem.locate_dofs_topological(V, domain.topology.dim - 1, facets)
    bc = fem.dirichletbc(boundary_normal, boundary_dofs)

    viscous = sip_viscosity_form(u, v, normal, cell_size, viscosity, alpha)
    a = [
        [viscous + ufl.inner(u, v) * ufl.dx, -p * ufl.div(v) * ufl.dx],
        [-q * ufl.div(u) * ufl.dx, None],
    ]
    rhs = [
        ufl.inner(boundary_target, v) * ufl.dx
        + viscosity
        * (
            -ufl.inner(ufl.outer(boundary_target, normal), ufl.grad(v)) * ufl.ds
            + alpha
            / cell_size
            * ufl.inner(ufl.outer(boundary_target, normal), ufl.outer(v, normal))
            * ufl.ds
        ),
        ufl.ZeroBaseForm((q,)),
    ]
    (velocity, pressure), _, residual, _, nullspace = _block_direct_solve(
        a, rhs, [bc], [V, Q], (1,), "b2_hdiv_affine_"
    )
    coordinates = ufl.SpatialCoordinate(domain)
    exact = ufl.as_vector(
        (
            -strain * coordinates[0] - rotation * coordinates[1],
            -strain * coordinates[1] + rotation * coordinates[0],
            2.0 * strain * coordinates[2],
        )
    )
    error_squared = fem.assemble_scalar(
        fem.form(ufl.inner(velocity - exact, velocity - exact) * ufl.dx)
    )
    velocity_error = math.sqrt(max(float(error_squared), 0.0))
    velocity_l2, pressure_l2, divergence_l2 = _field_norms(velocity, pressure)
    del velocity_l2, nullspace
    return {
        "velocity_l2_error": velocity_error,
        "pressure_l2": pressure_l2,
        "divergence_l2": divergence_l2,
        "algebraic_residual": residual,
    }


def non_affine_manufactured_convergence(
    resolutions: tuple[int, ...] = (3, 4), *, penalty_factor: float = 48.0
) -> list[dict[str, float | int]]:
    """Run a smooth divergence-free BDM convergence fixture on unit cubes.

    The source and all boundary data are manufactured from the curl of a
    smooth vector potential.  This is a numerical fixture only; it does not
    introduce volume forcing into a boundary-response calculation.
    """

    require_fenicsx()
    if len(resolutions) < 2 or any(resolution < 1 for resolution in resolutions):
        raise ValueError("Use at least two positive cube resolutions.")
    if any(finer <= coarser for coarser, finer in zip(resolutions, resolutions[1:])):
        raise ValueError("resolutions must increase.")

    from dolfinx import fem, mesh as dmesh
    from mpi4py import MPI
    import ufl

    viscosity = 1.0
    rows: list[dict[str, float | int]] = []
    for resolution in resolutions:
        domain = dmesh.create_unit_cube(MPI.COMM_WORLD, resolution, resolution, resolution)
        if domain.comm.size != 1:
            raise RuntimeError("The B2 manufactured convergence fixture is serial only.")
        V, Q = create_hdiv_spaces(domain)
        trial, pressure = ufl.TrialFunction(V), ufl.TrialFunction(Q)
        test, pressure_test = ufl.TestFunction(V), ufl.TestFunction(Q)
        normal = ufl.FacetNormal(domain)
        cell_size = ufl.CellDiameter(domain)
        coordinate = ufl.SpatialCoordinate(domain)
        pi = math.pi
        exact = ufl.as_vector(
            (
                pi * ufl.sin(pi * coordinate[0]) * ufl.cos(pi * coordinate[1]) * ufl.sin(pi * coordinate[2]),
                -pi * ufl.cos(pi * coordinate[0]) * ufl.sin(pi * coordinate[1]) * ufl.sin(pi * coordinate[2]),
                0.0,
            )
        )

        def exact_expression(points: np.ndarray) -> np.ndarray:
            return np.vstack(
                (
                    pi * np.sin(pi * points[0]) * np.cos(pi * points[1]) * np.sin(pi * points[2]),
                    -pi * np.cos(pi * points[0]) * np.sin(pi * points[1]) * np.sin(pi * points[2]),
                    np.zeros_like(points[0]),
                )
            )

        normal_data = fem.Function(V)
        normal_data.interpolate(exact_expression)
        domain.topology.create_connectivity(domain.topology.dim - 1, domain.topology.dim)
        facets = dmesh.exterior_facet_indices(domain.topology)
        boundary_dofs = fem.locate_dofs_topological(V, domain.topology.dim - 1, facets)
        boundary_condition = fem.dirichletbc(normal_data, boundary_dofs)
        alpha = fem.Constant(domain, float(penalty_factor))
        consistent_target = (
            exact - ufl.dot(exact, normal) * normal + ufl.dot(normal_data, normal) * normal
        )
        bilinear = sip_viscosity_form(trial, test, normal, cell_size, viscosity, alpha)
        lhs = [
            [bilinear + ufl.inner(trial, test) * ufl.dx, -pressure * ufl.div(test) * ufl.dx],
            [-pressure_test * ufl.div(trial) * ufl.dx, None],
        ]
        rhs = [
            (1.0 + 3.0 * pi**2 * viscosity) * ufl.inner(exact, test) * ufl.dx
            + viscosity
            * (
                -ufl.inner(ufl.outer(consistent_target, normal), ufl.grad(test)) * ufl.ds
                + alpha / cell_size * ufl.inner(ufl.outer(consistent_target, normal), ufl.outer(test, normal)) * ufl.ds
            ),
            ufl.ZeroBaseForm((pressure_test,)),
        ]
        (velocity, pressure_field), _, residual, _, nullspace = _block_direct_solve(
            lhs, rhs, [boundary_condition], [V, Q], (1,), f"b2_hdiv_non_affine_{resolution}_"
        )
        del nullspace
        error_squared = float(fem.assemble_scalar(fem.form(ufl.inner(velocity - exact, velocity - exact) * ufl.dx)))
        velocity_l2, pressure_l2, divergence_l2 = _field_norms(velocity, pressure_field)
        rows.append(
            {
                "resolution": resolution,
                "cells": int(domain.topology.index_map(domain.topology.dim).size_global),
                "velocity_l2_error": math.sqrt(max(error_squared, 0.0)),
                "velocity_l2": velocity_l2,
                "pressure_l2": pressure_l2,
                "divergence_l2": divergence_l2,
                "algebraic_residual": residual,
            }
        )
    return rows


def sip_stability_diagnostics(
    resolution: int = 2, *, penalty_factor: float = 6.0
) -> dict[str, float | int]:
    """Measure small-mesh SIP coercivity after homogeneous normal constraints.

    The result reports the velocity block both on all free velocity degrees of
    freedom and on its discrete divergence-free nullspace.  It is deliberately
    a dense, serial diagnostic for a very small cube; it is not a production
    eigensolver or a claim about the full saddle-point spectrum.
    """

    require_fenicsx()
    if resolution < 1 or penalty_factor <= 0.0:
        raise ValueError("resolution and penalty_factor must be positive.")

    from dolfinx import fem, mesh as dmesh
    from mpi4py import MPI
    import ufl

    domain = dmesh.create_unit_cube(MPI.COMM_WORLD, resolution, resolution, resolution)
    if domain.comm.size != 1:
        raise RuntimeError("The dense SIP stability diagnostic is serial only.")
    V, Q = create_hdiv_spaces(domain)
    u, v = ufl.TrialFunction(V), ufl.TestFunction(V)
    q = ufl.TestFunction(Q)
    normal = ufl.FacetNormal(domain)
    cell_size = ufl.CellDiameter(domain)
    alpha = fem.Constant(domain, float(penalty_factor))
    from dolfinx.fem import petsc as fem_petsc

    velocity_matrix = fem_petsc.assemble_matrix(
        fem.form(sip_viscosity_form(u, v, normal, cell_size, 1.0, alpha))
    )
    velocity_matrix.assemble()
    divergence_matrix = fem_petsc.assemble_matrix(fem.form(-q * ufl.div(u) * ufl.dx))
    divergence_matrix.assemble()

    velocity_size = velocity_matrix.getSize()[0]
    pressure_size = divergence_matrix.getSize()[0]
    indices = np.arange(velocity_size, dtype=np.int32)
    pressure_indices = np.arange(pressure_size, dtype=np.int32)
    dense_velocity = velocity_matrix.getValues(indices, indices)
    dense_divergence = divergence_matrix.getValues(pressure_indices, indices)
    domain.topology.create_connectivity(domain.topology.dim - 1, domain.topology.dim)
    facets = dmesh.exterior_facet_indices(domain.topology)
    constrained = fem.locate_dofs_topological(V, domain.topology.dim - 1, facets)
    free = np.setdiff1d(indices, constrained, assume_unique=False)
    if free.size == 0:
        raise RuntimeError("No free velocity degrees of freedom remain after normal constraints.")
    reduced_velocity = dense_velocity[np.ix_(free, free)]
    reduced_divergence = dense_divergence[:, free]
    symmetry_error = np.linalg.norm(reduced_velocity - reduced_velocity.T) / max(
        np.linalg.norm(reduced_velocity), np.finfo(float).tiny
    )
    full_eigenvalues = np.linalg.eigvalsh(0.5 * (reduced_velocity + reduced_velocity.T))
    _, singular_values, right_vectors = np.linalg.svd(reduced_divergence, full_matrices=True)
    divergence_tolerance = max(reduced_divergence.shape) * np.finfo(float).eps * max(
        float(singular_values[0]) if singular_values.size else 0.0, 1.0
    )
    rank = int(np.count_nonzero(singular_values > divergence_tolerance))
    nullspace_basis = right_vectors[rank:].T
    if nullspace_basis.shape[1] == 0:
        raise RuntimeError("No discrete divergence-free degrees of freedom were found.")
    divergence_free_matrix = nullspace_basis.T @ reduced_velocity @ nullspace_basis
    divergence_free_eigenvalues = np.linalg.eigvalsh(
        0.5 * (divergence_free_matrix + divergence_free_matrix.T)
    )
    return {
        "penalty_factor": float(penalty_factor),
        "free_velocity_dofs": int(free.size),
        "discrete_divergence_rank": rank,
        "discrete_divergence_free_dofs": int(nullspace_basis.shape[1]),
        "symmetry_relative_error": float(symmetry_error),
        "minimum_free_velocity_eigenvalue": float(full_eigenvalues[0]),
        "minimum_divergence_free_eigenvalue": float(divergence_free_eigenvalues[0]),
    }


def harmonic_response(
    config: PilotConfig,
    mode_name: str,
    frequency_hz: float,
    mesh_size: float,
    *,
    penalty_factor: float = 6.0,
    _return_fields: bool = False,
):
    """Solve one boundary-driven harmonic Stokes response with exact mass balance.

    BDM normal traces are imposed strongly.  Tangential traces are imposed by
    symmetric Nitsche terms.  The real-valued PETSc build uses coupled real and
    imaginary systems with the same ``exp(i*omega*t)`` convention as B1.
    """

    require_fenicsx()
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive.")
    if penalty_factor <= 0.0:
        raise ValueError("penalty_factor must be positive.")

    from dolfinx import fem
    import ufl

    mode = parse_mode(mode_name)
    mesh, _, facet_tags = create_cylinder(config, mesh_size)
    V_r, Q_r = create_hdiv_spaces(mesh)
    V_i, Q_i = create_hdiv_spaces(mesh)

    # H(div) essential boundary DOFs control only the normal trace.  A
    # tangential actuator must therefore have exactly zero essential normal
    # trace on the faceted mesh; its full tangential value is imposed by the
    # Nitsche terms below.  Normal modes retain the measured flux repair.
    boundary_normal = fem.Function(V_r)
    if mode.is_normal:
        boundary_normal.interpolate(_mode_expression(mode, config, 1.0))
        _, correction = _correct_boundary_flux(boundary_normal, V_r, facet_tags, config)
    else:
        correction = 0.0

    from basix.ufl import element
    from dolfinx import default_real_type

    target_element = element(
        "Lagrange",
        mesh.basix_cell(),
        degree=2,
        shape=(mesh.geometry.dim,),
        dtype=default_real_type,
    )
    target_space = fem.functionspace(mesh, target_element)
    boundary_target = fem.Function(target_space)
    boundary_target.interpolate(_mode_expression(mode, config, 1.0))
    if mode.is_normal and correction != 0.0:
        return_target = fem.Function(target_space)
        return_target.interpolate(_return_expression(config))
        boundary_target.x.array[:] += correction * return_target.x.array
        boundary_target.x.scatter_forward()
    zero_real = fem.Function(V_r)
    zero_imag = fem.Function(V_i)
    real_bcs, side_dofs, cap_dofs = _velocity_boundary_conditions(
        V_r, facet_tags, boundary_normal, zero_real
    )
    imaginary_bcs, imaginary_side_dofs, imaginary_cap_dofs = _velocity_boundary_conditions(
        V_i, facet_tags, zero_imag, zero_imag
    )

    u_r, p_r, u_i, p_i = (
        ufl.TrialFunction(V_r),
        ufl.TrialFunction(Q_r),
        ufl.TrialFunction(V_i),
        ufl.TrialFunction(Q_i),
    )
    v_r, q_r, v_i, q_i = (
        ufl.TestFunction(V_r),
        ufl.TestFunction(Q_r),
        ufl.TestFunction(V_i),
        ufl.TestFunction(Q_i),
    )
    normal = ufl.FacetNormal(mesh)
    cell_size = ufl.CellDiameter(mesh)
    side_measure = ufl.Measure("ds", domain=mesh, subdomain_data=facet_tags)
    alpha = fem.Constant(mesh, float(penalty_factor))
    nu = config.fluid.kinematic_viscosity
    omega = 2.0 * math.pi * frequency_hz

    a = [
        [
            sip_viscosity_form(u_r, v_r, normal, cell_size, nu, alpha),
            -p_r * ufl.div(v_r) * ufl.dx,
            -omega * ufl.inner(u_i, v_r) * ufl.dx,
            None,
        ],
        [-q_r * ufl.div(u_r) * ufl.dx, None, None, None],
        [
            omega * ufl.inner(u_r, v_i) * ufl.dx,
            None,
            sip_viscosity_form(u_i, v_i, normal, cell_size, nu, alpha),
            -p_i * ufl.div(v_i) * ufl.dx,
        ],
        [None, None, -q_i * ufl.div(u_i) * ufl.dx, None],
    ]

    coordinate = ufl.SpatialCoordinate(mesh)
    smooth_target = _mode_ufl(mode, config, coordinate)
    facet_consistent_target = (
        smooth_target - ufl.dot(smooth_target, normal) * normal
        + ufl.dot(boundary_normal, normal) * normal
    )
    # Projecting in UFL retains each planar facet normal.  A continuous nodal
    # target would average incompatible normals where side facets meet caps.
    boundary_rhs = nu * (
        -ufl.inner(ufl.outer(facet_consistent_target, normal), ufl.grad(v_r)) * side_measure(SIDE_TAG)
        + alpha / cell_size
        * ufl.inner(ufl.outer(facet_consistent_target, normal), ufl.outer(v_r, normal))
        * side_measure(SIDE_TAG)
    )
    rhs = [
        boundary_rhs,
        ufl.ZeroBaseForm((q_r,)),
        ufl.ZeroBaseForm((v_i,)),
        ufl.ZeroBaseForm((q_i,)),
    ]
    solutions, solver, residual, elapsed, nullspace = _block_direct_solve(
        a,
        rhs,
        real_bcs + imaginary_bcs,
        [V_r, Q_r, V_i, Q_i],
        (1, 3),
        f"b2_hdiv_{mode_name.lower()}_",
    )
    u_real, p_real, u_imaginary, p_imaginary = solutions

    physical = config.probe_velocity
    for function in (
        u_real,
        p_real,
        u_imaginary,
        p_imaginary,
        boundary_normal,
        boundary_target,
    ):
        function.x.array[:] *= physical
        function.x.scatter_forward()

    real_velocity, real_pressure, real_divergence = _field_norms(u_real, p_real)
    imag_velocity, imag_pressure, imag_divergence = _field_norms(u_imaginary, p_imaginary)
    length = config.geometry.radius
    corrected_flux, corrected_flux_ratio = _boundary_flux(
        boundary_normal, facet_tags, config, physical, mode.is_normal
    )
    del corrected_flux
    input_diagnostics = _input_diagnostics(
        boundary_target,
        boundary_normal,
        facet_tags,
        config,
        frequency_hz,
        mode.is_normal,
    )
    real_boundary_trace = _boundary_trace_diagnostics(
        u_real, physical * smooth_target, boundary_normal, facet_tags, physical
    )
    imaginary_boundary_trace = _boundary_trace_diagnostics(
        u_imaginary, 0.0 * smooth_target, zero_imag, facet_tags, physical
    )

    real_diagnostics = HdivComponentDiagnostics(
        real_velocity,
        real_pressure,
        real_divergence,
        length * real_divergence / max(real_velocity, np.finfo(float).tiny),
        residual,
        max(
            _boundary_residual(u_real, boundary_normal, side_dofs),
            _boundary_residual(u_real, zero_real, cap_dofs),
        ),
    )
    imaginary_diagnostics = HdivComponentDiagnostics(
        imag_velocity,
        imag_pressure,
        imag_divergence,
        length * imag_divergence / max(imag_velocity, np.finfo(float).tiny),
        residual,
        max(
            _boundary_residual(u_imaginary, zero_imag, imaginary_side_dofs),
            _boundary_residual(u_imaginary, zero_imag, imaginary_cap_dofs),
        ),
    )
    result = HdivHarmonicResult(
        mode_name,
        frequency_hz,
        mesh_size,
        int(mesh.topology.index_map(mesh.topology.dim).size_global),
        int(V_r.dofmap.index_map.size_global * V_r.dofmap.index_map_bs),
        int(Q_r.dofmap.index_map.size_global * Q_r.dofmap.index_map_bs),
        _mesh_sha256(mesh),
        correction,
        corrected_flux_ratio,
        input_diagnostics,
        real_boundary_trace,
        imaginary_boundary_trace,
        elapsed,
        real_diagnostics,
        imaginary_diagnostics,
    )
    del nullspace
    if _return_fields:
        return result, (u_real, p_real, u_imaginary, p_imaginary, facet_tags)
    return result
