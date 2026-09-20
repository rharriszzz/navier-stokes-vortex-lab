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

    viscous = viscosity * (
        ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx
        - ufl.inner(ufl.avg(ufl.grad(u)), _jump(v, normal)) * ufl.dS
        - ufl.inner(_jump(u, normal), ufl.avg(ufl.grad(v))) * ufl.dS
        + alpha / ufl.avg(cell_size) * ufl.inner(_jump(u, normal), _jump(v, normal)) * ufl.dS
        - ufl.inner(ufl.grad(u), ufl.outer(v, normal)) * ufl.ds
        - ufl.inner(ufl.outer(u, normal), ufl.grad(v)) * ufl.ds
        + alpha / cell_size * ufl.inner(ufl.outer(u, normal), ufl.outer(v, normal)) * ufl.ds
    )
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
    alpha = fem.Constant(mesh, float(penalty_factor))
    nu = config.fluid.kinematic_viscosity
    omega = 2.0 * math.pi * frequency_hz

    def viscosity_form(trial, test):
        return nu * (
            ufl.inner(ufl.grad(trial), ufl.grad(test)) * ufl.dx
            - ufl.inner(ufl.avg(ufl.grad(trial)), _jump(test, normal)) * ufl.dS
            - ufl.inner(_jump(trial, normal), ufl.avg(ufl.grad(test))) * ufl.dS
            + alpha / ufl.avg(cell_size) * ufl.inner(
                _jump(trial, normal), _jump(test, normal)
            ) * ufl.dS
            - ufl.inner(ufl.grad(trial), ufl.outer(test, normal)) * ufl.ds
            - ufl.inner(ufl.outer(trial, normal), ufl.grad(test)) * ufl.ds
            + alpha / cell_size * ufl.inner(
                ufl.outer(trial, normal), ufl.outer(test, normal)
            ) * ufl.ds
        )

    a = [
        [
            viscosity_form(u_r, v_r),
            -p_r * ufl.div(v_r) * ufl.dx,
            -omega * ufl.inner(u_i, v_r) * ufl.dx,
            None,
        ],
        [-q_r * ufl.div(u_r) * ufl.dx, None, None, None],
        [
            omega * ufl.inner(u_r, v_i) * ufl.dx,
            None,
            viscosity_form(u_i, v_i),
            -p_i * ufl.div(v_i) * ufl.dx,
        ],
        [None, None, -q_i * ufl.div(u_i) * ufl.dx, None],
    ]

    boundary_rhs = nu * (
        -ufl.inner(ufl.outer(boundary_target, normal), ufl.grad(v_r)) * ufl.ds
        + alpha / cell_size
        * ufl.inner(ufl.outer(boundary_target, normal), ufl.outer(v_r, normal))
        * ufl.ds
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
        elapsed,
        real_diagnostics,
        imaginary_diagnostics,
    )
    del nullspace
    if _return_fields:
        return result, (u_real, p_real, u_imaginary, p_imaginary, facet_tags)
    return result
