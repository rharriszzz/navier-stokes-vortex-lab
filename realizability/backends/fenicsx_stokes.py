"""DOLFINx 0.10 backend for the B1 linear Stokes verification and pilots.

The imports are intentionally confined to this optional module so the B0
NumPy-only package remains usable without a finite-element installation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import math
from pathlib import Path
import time
from typing import Callable

import numpy as np

from ..boundary_modes import BoundaryMode, mode_scalar, parse_mode
from ..config import PilotConfig


VOLUME_TAG = 1
SIDE_TAG = 2
CAP_TAG = 3


@dataclass(frozen=True)
class SolverVersions:
    dolfinx: str
    basix: str
    ufl: str
    ffcx: str
    gmsh: str
    numpy: str
    petsc: str
    petsc_scalar_type: str
    mpi: str


@dataclass(frozen=True)
class SolveDiagnostics:
    converged_reason: int
    iterations: int
    algebraic_residual: float
    velocity_l2: float
    pressure_l2: float
    divergence_ratio: float
    boundary_residual: float
    net_flux: float
    flux_ratio: float
    velocity_dofs: int
    pressure_dofs: int
    cells: int
    elapsed_seconds: float


@dataclass(frozen=True)
class BoundaryInputDiagnostics:
    actual_peak_speed: float
    side_rms_speed: float
    inward_volume_flow_amplitude: float
    displacement_amplitude: float | None
    acceleration_amplitude: float
    pressure_demand: str
    force_and_power: str


@dataclass(frozen=True)
class HarmonicResult:
    mode: str
    frequency_hz: float
    mesh_size: float
    input_amplitude: float
    mesh_sha256: str
    boundary_tag_counts: dict[str, int]
    raw_net_flux: float
    flux_correction_coefficient: float
    input_diagnostics: BoundaryInputDiagnostics
    real: SolveDiagnostics
    imaginary: SolveDiagnostics
    pressure_imaginary_l2: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TransientStep:
    time_seconds: float
    input_amplitude: float
    velocity_l2: float
    pressure_l2: float
    kinetic_energy_per_density: float
    divergence_ratio: float
    algebraic_residual: float
    net_flux: float


@dataclass(frozen=True)
class TransientResult:
    mode: str
    time_step: float
    mesh_size: float
    forcing_status: str
    flux_correction_coefficient: float
    steps: tuple[TransientStep, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def require_fenicsx() -> None:
    """Raise a clear error when the optional B1 environment is not active."""

    try:
        import dolfinx  # noqa: F401
        import gmsh  # noqa: F401
        import mpi4py  # noqa: F401
        import petsc4py  # noqa: F401
        import ufl  # noqa: F401
    except ImportError as error:
        raise RuntimeError(
            "B1 requires the isolated DOLFINx environment documented in "
            "docs/realizability/B1_SETUP.md. B0 remains available without it."
        ) from error


def solver_versions() -> SolverVersions:
    require_fenicsx()
    import dolfinx
    import basix
    import ffcx
    import gmsh
    import ufl
    from mpi4py import MPI
    from petsc4py import PETSc

    mpi_version = MPI.Get_library_version().splitlines()[0].strip()
    return SolverVersions(
        dolfinx=dolfinx.__version__,
        basix=basix.__version__,
        ufl=ufl.__version__,
        ffcx=ffcx.__version__,
        gmsh=gmsh.__version__,
        numpy=np.__version__,
        petsc=".".join(str(value) for value in PETSc.Sys.getVersion()),
        petsc_scalar_type=np.dtype(PETSc.ScalarType).name,
        mpi=mpi_version,
    )


def create_cylinder(config: PilotConfig, mesh_size: float):
    """Create and tag a Gmsh cylinder: volume=1, side=2, both caps=3."""

    require_fenicsx()
    if mesh_size <= 0.0:
        raise ValueError("mesh_size must be positive.")
    import gmsh
    from dolfinx.io import gmsh as dolfinx_gmsh
    from mpi4py import MPI

    geometry = config.geometry
    gmsh.initialize()
    try:
        gmsh.option.setNumber("General.Terminal", 0)
        gmsh.model.add("boundary_control_cylinder")
        volume = gmsh.model.occ.addCylinder(
            0.0,
            0.0,
            -geometry.half_height,
            0.0,
            0.0,
            2.0 * geometry.half_height,
            geometry.radius,
        )
        gmsh.model.occ.synchronize()
        boundary = gmsh.model.getBoundary([(3, volume)], oriented=False, recursive=False)
        side_tags: list[int] = []
        cap_tags: list[int] = []
        for dimension, tag in boundary:
            center = gmsh.model.occ.getCenterOfMass(dimension, tag)
            if math.isclose(abs(center[2]), geometry.half_height, rel_tol=0.0, abs_tol=1.0e-10):
                cap_tags.append(tag)
            else:
                side_tags.append(tag)
        if len(side_tags) != 1 or len(cap_tags) != 2:
            raise RuntimeError(f"Unexpected cylinder boundary topology: side={side_tags}, caps={cap_tags}")
        gmsh.model.addPhysicalGroup(3, [volume], VOLUME_TAG)
        gmsh.model.addPhysicalGroup(2, side_tags, SIDE_TAG)
        gmsh.model.addPhysicalGroup(2, cap_tags, CAP_TAG)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", mesh_size)
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", mesh_size)
        gmsh.model.mesh.generate(3)
        mesh_data = dolfinx_gmsh.model_to_mesh(gmsh.model, MPI.COMM_WORLD, 0, gdim=3)
    finally:
        gmsh.finalize()
    return mesh_data.mesh, mesh_data.cell_tags, mesh_data.facet_tags


def create_taylor_hood_spaces(mesh):
    """Create separate P2 vector-velocity and P1 scalar-pressure spaces."""

    from basix.ufl import element
    from dolfinx import default_real_type, fem

    velocity_element = element(
        "Lagrange", mesh.basix_cell(), degree=2, shape=(mesh.geometry.dim,), dtype=default_real_type
    )
    pressure_element = element("Lagrange", mesh.basix_cell(), degree=1, dtype=default_real_type)
    return fem.functionspace(mesh, velocity_element), fem.functionspace(mesh, pressure_element)


def _mesh_sha256(mesh) -> str:
    topological_dimension = mesh.topology.dim
    mesh.topology.create_connectivity(topological_dimension, 0)
    connectivity = mesh.topology.connectivity(topological_dimension, 0)
    digest = hashlib.sha256()
    digest.update(np.asarray(mesh.geometry.x, dtype=np.float64).tobytes())
    digest.update(np.asarray(connectivity.array, dtype=np.int64).tobytes())
    digest.update(np.asarray(connectivity.offsets, dtype=np.int64).tobytes())
    return digest.hexdigest()


def _mode_expression(mode: BoundaryMode, config: PilotConfig, amplitude: float) -> Callable[[np.ndarray], np.ndarray]:
    geometry = config.geometry

    def expression(x: np.ndarray) -> np.ndarray:
        radius = np.hypot(x[0], x[1])
        theta = np.arctan2(x[1], x[0])
        s = x[2] / geometry.half_height
        scalar = amplitude * mode_scalar(mode, theta, s)
        safe_radius = np.where(radius > 0.0, radius, 1.0)
        radial_x = x[0] / safe_radius
        radial_y = x[1] / safe_radius
        if mode.is_normal:
            return np.vstack((scalar * radial_x, scalar * radial_y, np.zeros_like(scalar)))
        return np.vstack((-scalar * radial_y, scalar * radial_x, np.zeros_like(scalar)))

    return expression


def _return_expression(config: PilotConfig) -> Callable[[np.ndarray], np.ndarray]:
    """Smooth unit radial return field Z0(s)e_r used only for mesh-flux repair."""

    geometry = config.geometry

    def expression(x: np.ndarray) -> np.ndarray:
        radius = np.hypot(x[0], x[1])
        safe_radius = np.where(radius > 0.0, radius, 1.0)
        s = x[2] / geometry.half_height
        scalar = (1.0 - s * s) ** 2
        return np.vstack((scalar * x[0] / safe_radius, scalar * x[1] / safe_radius, np.zeros_like(scalar)))

    return expression


def _velocity_boundary_conditions(V, facet_tags, side_value, cap_value):
    from dolfinx import fem

    facet_dimension = V.mesh.topology.dim - 1
    side_dofs = fem.locate_dofs_topological(V, facet_dimension, facet_tags.find(SIDE_TAG))
    cap_dofs = fem.locate_dofs_topological(V, facet_dimension, facet_tags.find(CAP_TAG))
    return [fem.dirichletbc(side_value, side_dofs), fem.dirichletbc(cap_value, cap_dofs)], side_dofs, cap_dofs


def _pressure_nullspace(problem, pressure_indices: tuple[int, ...]):
    from dolfinx.fem import extract_function_spaces
    from dolfinx.fem.petsc import create_vector
    from petsc4py import PETSc

    spaces = extract_function_spaces(problem.L)
    vectors = []
    for pressure_index in pressure_indices:
        vector = create_vector(spaces, "nest")
        components = vector.getNestSubVecs()
        for component in components:
            component.set(0.0)
        components[pressure_index].set(1.0)
        vector.normalize()
        vectors.append(vector)
    nullspace = PETSc.NullSpace().create(vectors=vectors)
    problem.A.setNullSpace(nullspace)
    return nullspace


def _block_direct_solve(a_ufl, rhs_ufl, bcs, spaces, pressure_indices: tuple[int, ...], prefix: str):
    """Assemble a serial monolithic block system and solve its pressure nullspaces."""

    from dolfinx import fem
    from dolfinx.fem import bcs_by_block, extract_function_spaces
    from dolfinx.fem.petsc import apply_lifting, assemble_matrix, assemble_vector, assign, set_bc
    from petsc4py import PETSc

    mesh = spaces[0].mesh
    if mesh.comm.size != 1:
        raise RuntimeError("The B1 direct verification solver is intentionally serial.")
    a = fem.form(a_ufl)
    rhs = fem.form(rhs_ufl)
    matrix = assemble_matrix(a, bcs=bcs)
    matrix.assemble()
    vector = assemble_vector(rhs, kind=PETSc.Vec.Type.MPI)
    bcs_columns = bcs_by_block(extract_function_spaces(a, 1), bcs)
    apply_lifting(vector, a, bcs=bcs_columns)
    vector.ghostUpdate(addv=PETSc.InsertMode.ADD, mode=PETSc.ScatterMode.REVERSE)
    bcs_rows = bcs_by_block(extract_function_spaces(rhs), bcs)
    set_bc(vector, bcs_rows)

    local_sizes = [space.dofmap.index_map.size_local * space.dofmap.index_map_bs for space in spaces]
    offsets = np.cumsum([0, *local_sizes])
    null_vectors = []
    for pressure_index in pressure_indices:
        null_vector = matrix.createVecLeft()
        null_vector.set(0.0)
        null_vector.array[offsets[pressure_index] : offsets[pressure_index + 1]] = 1.0
        null_vector.normalize()
        null_vectors.append(null_vector)
    nullspace = PETSc.NullSpace().create(vectors=null_vectors)
    if not nullspace.test(matrix):
        raise RuntimeError("Pressure-only constant vectors failed the assembled nullspace test.")
    matrix.setNullSpace(nullspace)
    nullspace.remove(vector)

    solver = PETSc.KSP().create(mesh.comm)
    solver.setOptionsPrefix(prefix)
    solver.setOperators(matrix)
    solver.setType("preonly")
    preconditioner = solver.getPC()
    preconditioner.setType("lu")
    if PETSc.Sys().hasExternalPackage("mumps") and PETSc.IntType != np.int64:
        preconditioner.setFactorSolverType("mumps")
        preconditioner.setFactorSetUpSolverType()
        factor = preconditioner.getFactorMatrix()
        factor.setMumpsIcntl(icntl=24, ival=1)
        factor.setMumpsIcntl(icntl=25, ival=0)
    else:
        preconditioner.setFactorSolverType("superlu_dist")
    solution_vector = matrix.createVecRight()
    start = time.perf_counter()
    solver.solve(vector, solution_vector)
    elapsed = time.perf_counter() - start
    reason = int(solver.getConvergedReason())
    if reason <= 0:
        raise RuntimeError(f"Direct block solve failed; PETSc reason {reason}.")

    residual_vector = vector.copy()
    matrix.mult(solution_vector, residual_vector)
    residual_vector.aypx(-1.0, vector)  # residual = b - A*x
    denominator = max(float(vector.norm()), np.finfo(float).tiny)
    relative_residual = float(residual_vector.norm()) / denominator
    functions = [fem.Function(space) for space in spaces]
    # Block vectors store every owned block first and then every ghost block.
    # DOLFINx's assignment helper knows that layout; direct slicing only works
    # accidentally for a single scalar space.
    assign(solution_vector, functions)
    for function in functions:
        function.x.scatter_forward()
    return functions, solver, relative_residual, elapsed, nullspace


def _global_scalar(mesh, value: float) -> float:
    from mpi4py import MPI

    return float(mesh.comm.allreduce(value, op=MPI.SUM))


def _field_norms(u, p) -> tuple[float, float, float]:
    from dolfinx import fem
    import ufl

    mesh = u.function_space.mesh
    velocity_squared = _global_scalar(mesh, fem.assemble_scalar(fem.form(ufl.inner(u, u) * ufl.dx)))
    pressure_squared = _global_scalar(mesh, fem.assemble_scalar(fem.form(p * p * ufl.dx)))
    divergence_squared = _global_scalar(mesh, fem.assemble_scalar(fem.form(ufl.div(u) ** 2 * ufl.dx)))
    velocity_l2 = math.sqrt(max(velocity_squared, 0.0))
    pressure_l2 = math.sqrt(max(pressure_squared, 0.0))
    divergence_l2 = math.sqrt(max(divergence_squared, 0.0))
    return velocity_l2, pressure_l2, divergence_l2


def _boundary_flux(boundary_value, facet_tags, config: PilotConfig, amplitude: float, normal_mode: bool) -> tuple[float, float]:
    from dolfinx import fem
    import ufl

    mesh = boundary_value.function_space.mesh
    measure = ufl.Measure("ds", domain=mesh, subdomain_data=facet_tags)
    normal = ufl.FacetNormal(mesh)
    signed = _global_scalar(mesh, fem.assemble_scalar(fem.form(ufl.dot(boundary_value, normal) * measure(SIDE_TAG))))
    if normal_mode:
        absolute = _global_scalar(
            mesh, fem.assemble_scalar(fem.form(abs(ufl.dot(boundary_value, normal)) * measure(SIDE_TAG)))
        )
    else:
        side_area = 4.0 * math.pi * config.geometry.radius * config.geometry.half_height
        absolute = side_area * amplitude
    ratio = abs(signed) / absolute if absolute > 0.0 else abs(signed)
    return signed, ratio


def _correct_boundary_flux(boundary_value, V, facet_tags, config: PilotConfig) -> tuple[float, float]:
    """Remove the small faceted-geometry flux using a rim-vanishing return."""

    from dolfinx import fem
    import ufl

    mesh = V.mesh
    measure = ufl.Measure("ds", domain=mesh, subdomain_data=facet_tags)
    normal = ufl.FacetNormal(mesh)

    def signed_flux(field) -> float:
        value = fem.assemble_scalar(fem.form(ufl.dot(field, normal) * measure(SIDE_TAG)))
        return _global_scalar(mesh, value)

    raw_flux = signed_flux(boundary_value)
    return_field = fem.Function(V)
    return_field.interpolate(_return_expression(config))
    return_flux = signed_flux(return_field)
    if abs(return_flux) <= np.finfo(float).eps:
        raise RuntimeError("The side-wall return field has numerically zero flux.")
    coefficient = -raw_flux / return_flux
    if abs(coefficient) > 1.0e-2:
        raise RuntimeError(
            f"Mesh flux correction {coefficient:.6e} exceeds the 1% rejection threshold; refine the geometry."
        )
    boundary_value.x.array[:] += coefficient * return_field.x.array
    boundary_value.x.scatter_forward()
    return raw_flux, coefficient


def boundary_flux_correction_diagnostic(
    config: PilotConfig, mode_name: str, mesh_size: float
) -> dict[str, float | int]:
    """Measure the faceted-cylinder correction without solving a PDE."""

    from dolfinx import fem

    mode = parse_mode(mode_name)
    mesh, _, facet_tags = create_cylinder(config, mesh_size)
    V, _ = create_taylor_hood_spaces(mesh)
    boundary = fem.Function(V)
    boundary.interpolate(_mode_expression(mode, config, 1.0))
    raw_flux, coefficient = _correct_boundary_flux(boundary, V, facet_tags, config)
    corrected_flux, _ = _boundary_flux(boundary, facet_tags, config, 1.0, mode.is_normal)
    return {
        "mesh_size": mesh_size,
        "cells": int(mesh.topology.index_map(mesh.topology.dim).size_global),
        "raw_net_flux": raw_flux,
        "correction_coefficient": coefficient,
        "corrected_net_flux": corrected_flux,
    }


def _boundary_residual(function, prescribed, dofs: np.ndarray) -> float:
    block_size = function.function_space.dofmap.bs
    scalar_dofs = (block_size * dofs[:, None] + np.arange(block_size)[None, :]).ravel()
    difference = function.x.array[scalar_dofs] - prescribed.x.array[scalar_dofs]
    return float(np.max(np.abs(difference))) if difference.size else 0.0


def _boundary_input_diagnostics(
    boundary_value,
    facet_tags,
    config: PilotConfig,
    frequency_hz: float,
    side_dofs: np.ndarray,
    normal_mode: bool,
) -> BoundaryInputDiagnostics:
    from dolfinx import fem
    import ufl

    mesh = boundary_value.function_space.mesh
    measure = ufl.Measure("ds", domain=mesh, subdomain_data=facet_tags)
    normal = ufl.FacetNormal(mesh)
    side_area = _global_scalar(mesh, fem.assemble_scalar(fem.form(1.0 * measure(SIDE_TAG))))
    speed_squared = _global_scalar(
        mesh, fem.assemble_scalar(fem.form(ufl.inner(boundary_value, boundary_value) * measure(SIDE_TAG)))
    )
    normal_velocity = ufl.dot(boundary_value, normal)
    inward_flow = _global_scalar(
        mesh,
        fem.assemble_scalar(fem.form(0.5 * (abs(normal_velocity) - normal_velocity) * measure(SIDE_TAG))),
    )
    block_size = boundary_value.function_space.dofmap.bs
    scalar_dofs = (block_size * side_dofs[:, None] + np.arange(block_size)[None, :]).ravel()
    vectors = boundary_value.x.array[scalar_dofs].reshape(-1, block_size)
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


def harmonic_pilot(
    config: PilotConfig,
    mode_name: str,
    frequency_hz: float,
    mesh_size: float,
    amplitude_scale: float = 1.0,
    *,
    _return_fields: bool = False,
):
    """Solve one real/imaginary harmonic Stokes pilot about rest."""

    require_fenicsx()
    if frequency_hz <= 0.0:
        raise ValueError("frequency_hz must be positive for a harmonic pilot.")
    from dolfinx import fem
    import ufl

    mode = parse_mode(mode_name)
    mesh, _, facet_tags = create_cylinder(config, mesh_size)
    V_r, Q_r = create_taylor_hood_spaces(mesh)
    V_i, Q_i = create_taylor_hood_spaces(mesh)
    if amplitude_scale == 0.0:
        raise ValueError("amplitude_scale must be nonzero; use the zero-field verification for zero input.")
    numerical_amplitude = amplitude_scale
    real_boundary = fem.Function(V_r)
    real_boundary.interpolate(_mode_expression(mode, config, numerical_amplitude))
    raw_net_flux, flux_correction = _correct_boundary_flux(real_boundary, V_r, facet_tags, config)
    real_zero = fem.Function(V_r)
    imag_zero = fem.Function(V_i)
    real_bcs, side_dofs, cap_dofs = _velocity_boundary_conditions(V_r, facet_tags, real_boundary, real_zero)
    imag_bcs, imag_side_dofs, imag_cap_dofs = _velocity_boundary_conditions(V_i, facet_tags, imag_zero, imag_zero)

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
    nu = config.fluid.kinematic_viscosity
    omega = 2.0 * math.pi * frequency_hz
    zero_q_r = ufl.ZeroBaseForm((q_r,))
    zero_q_i = ufl.ZeroBaseForm((q_i,))
    zero_v_r = ufl.ZeroBaseForm((v_r,))
    zero_v_i = ufl.ZeroBaseForm((v_i,))
    a = [
        [nu * ufl.inner(ufl.grad(u_r), ufl.grad(v_r)) * ufl.dx, -p_r * ufl.div(v_r) * ufl.dx, -omega * ufl.inner(u_i, v_r) * ufl.dx, None],
        [-q_r * ufl.div(u_r) * ufl.dx, None, None, None],
        [omega * ufl.inner(u_r, v_i) * ufl.dx, None, nu * ufl.inner(ufl.grad(u_i), ufl.grad(v_i)) * ufl.dx, -p_i * ufl.div(v_i) * ufl.dx],
        [None, None, -q_i * ufl.div(u_i) * ufl.dx, None],
    ]
    rhs = [zero_v_r, zero_q_r, zero_v_i, zero_q_i]
    solutions, solver, residual, elapsed, nullspace = _block_direct_solve(
        a,
        rhs,
        real_bcs + imag_bcs,
        [V_r, Q_r, V_i, Q_i],
        (1, 3),
        f"b1_{mode_name.lower()}_",
    )
    u_real, p_real, u_imag, p_imag = solutions
    # The equations are linear. Solve at order-one scale for a meaningful
    # algebraic stopping test, then convert every field back to the physical
    # probe amplitude before reporting diagnostics.
    for function in (u_real, p_real, u_imag, p_imag, real_boundary):
        function.x.array[:] *= config.probe_velocity
    u_real.x.scatter_forward()
    p_real.x.scatter_forward()
    u_imag.x.scatter_forward()
    p_imag.x.scatter_forward()
    real_velocity_l2, real_pressure_l2, real_divergence_l2 = _field_norms(u_real, p_real)
    imag_velocity_l2, imag_pressure_l2, imag_divergence_l2 = _field_norms(u_imag, p_imag)
    physical_peak = abs(amplitude_scale) * config.probe_velocity
    net_flux, flux_ratio = _boundary_flux(real_boundary, facet_tags, config, physical_peak, mode.is_normal)
    input_diagnostics = _boundary_input_diagnostics(
        real_boundary, facet_tags, config, frequency_hz, side_dofs, mode.is_normal
    )
    cells = mesh.topology.index_map(mesh.topology.dim).size_global
    mesh_hash = _mesh_sha256(mesh)
    boundary_tag_counts = {
        "side_facets": int(facet_tags.find(SIDE_TAG).size),
        "cap_facets": int(facet_tags.find(CAP_TAG).size),
    }
    velocity_dofs = V_r.dofmap.index_map.size_global * V_r.dofmap.index_map_bs
    pressure_dofs = Q_r.dofmap.index_map.size_global
    iterations = int(solver.getIterationNumber())
    reason = int(solver.getConvergedReason())
    if reason <= 0:
        raise RuntimeError(
            f"Harmonic solve did not converge; PETSc reason {reason}, "
            f"iterations {iterations}, residual {residual:.6e}."
        )
    length = config.geometry.radius
    real_scale = real_velocity_l2 or 1.0
    imag_scale = imag_velocity_l2 or 1.0
    real_diagnostics = SolveDiagnostics(
        reason,
        iterations,
        residual,
        real_velocity_l2,
        real_pressure_l2,
        length * real_divergence_l2 / real_scale,
        max(_boundary_residual(u_real, real_boundary, side_dofs), _boundary_residual(u_real, real_zero, cap_dofs)),
        net_flux,
        flux_ratio,
        velocity_dofs,
        pressure_dofs,
        cells,
        elapsed,
    )
    imag_diagnostics = SolveDiagnostics(
        reason,
        iterations,
        residual,
        imag_velocity_l2,
        imag_pressure_l2,
        length * imag_divergence_l2 / imag_scale,
        max(_boundary_residual(u_imag, imag_zero, imag_side_dofs), _boundary_residual(u_imag, imag_zero, imag_cap_dofs)),
        0.0,
        0.0,
        velocity_dofs,
        pressure_dofs,
        cells,
        elapsed,
    )
    # Keep the PETSc nullspace alive through extraction of the result.
    del nullspace
    if mesh.comm.rank == 0:
        result = HarmonicResult(
            mode_name,
            frequency_hz,
            mesh_size,
            amplitude_scale * config.probe_velocity,
            mesh_hash,
            boundary_tag_counts,
            raw_net_flux * config.probe_velocity,
            flux_correction,
            input_diagnostics,
            real_diagnostics,
            imag_diagnostics,
            imag_pressure_l2,
        )
        return (result, (u_real, p_real, u_imag, p_imag)) if _return_fields else result
    result = HarmonicResult(
        mode_name,
        frequency_hz,
        mesh_size,
        amplitude_scale * config.probe_velocity,
        mesh_hash,
        boundary_tag_counts,
        raw_net_flux * config.probe_velocity,
        flux_correction,
        input_diagnostics,
        real_diagnostics,
        imag_diagnostics,
        imag_pressure_l2,
    )
    return (result, (u_real, p_real, u_imag, p_imag)) if _return_fields else result


def transient_pulse(
    config: PilotConfig,
    mode_name: str,
    time_step: float,
    amplitude_scales: tuple[float, ...],
    mesh_size: float,
) -> TransientResult:
    """Advance a boundary-mode pulse with backward Euler and no volume force.

    ``amplitude_scales`` multiplies ``config.probe_velocity`` at each step.
    The zero initial condition and homogeneous momentum right-hand side are
    fixed by this production-facing API, so manufactured forcing cannot leak
    into a boundary-response run.
    """

    require_fenicsx()
    if time_step <= 0.0 or not amplitude_scales:
        raise ValueError("time_step must be positive and amplitude_scales must be nonempty.")
    from dolfinx import fem
    import ufl

    mode = parse_mode(mode_name)
    mesh, _, facet_tags = create_cylinder(config, mesh_size)
    V, Q = create_taylor_hood_spaces(mesh)
    unit_boundary = fem.Function(V)
    unit_boundary.interpolate(_mode_expression(mode, config, 1.0))
    _, correction = _correct_boundary_flux(unit_boundary, V, facet_tags, config)
    boundary = fem.Function(V)
    cap_zero = fem.Function(V)
    previous = fem.Function(V)
    u, p = ufl.TrialFunction(V), ufl.TrialFunction(Q)
    v, q = ufl.TestFunction(V), ufl.TestFunction(Q)
    a = [
        [
            ufl.inner(u, v) / time_step * ufl.dx
            + config.fluid.kinematic_viscosity * ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx,
            -p * ufl.div(v) * ufl.dx,
        ],
        [-q * ufl.div(u) * ufl.dx, None],
    ]
    rhs = [ufl.inner(previous / time_step, v) * ufl.dx, ufl.ZeroBaseForm((q,))]
    records: list[TransientStep] = []
    for index, scale in enumerate(amplitude_scales, start=1):
        boundary.x.array[:] = scale * unit_boundary.x.array
        boundary.x.scatter_forward()
        bcs, _, _ = _velocity_boundary_conditions(V, facet_tags, boundary, cap_zero)
        (uh, ph), _, residual, _, nullspace = _block_direct_solve(
            a, rhs, bcs, [V, Q], (1,), "b1_transient_"
        )
        velocity_l2, pressure_l2, divergence_l2 = _field_norms(uh, ph)
        kinetic = _global_scalar(
            mesh, fem.assemble_scalar(fem.form(0.5 * ufl.inner(uh, uh) * ufl.dx))
        )
        net_flux, _ = _boundary_flux(boundary, facet_tags, config, abs(scale), mode.is_normal)
        velocity_scale = velocity_l2 or 1.0
        physical = config.probe_velocity
        records.append(
            TransientStep(
                index * time_step,
                scale * physical,
                velocity_l2 * physical,
                pressure_l2 * physical,
                kinetic * physical**2,
                config.geometry.radius * divergence_l2 / velocity_scale,
                residual,
                net_flux * physical,
            )
        )
        previous.x.array[:] = uh.x.array
        previous.x.scatter_forward()
        del nullspace
    return TransientResult(
        mode_name,
        time_step,
        mesh_size,
        "none (boundary Dirichlet actuation only)",
        correction,
        tuple(records),
    )
