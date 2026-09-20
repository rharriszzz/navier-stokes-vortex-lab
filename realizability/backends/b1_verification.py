"""Independent B1 verification cases for the optional DOLFINx backend."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Any

import numpy as np

from ..config import PilotConfig
from ..boundary_modes import canonical_modes, gram_matrix
from .fenicsx_stokes import (
    _block_direct_solve,
    _field_norms,
    _global_scalar,
    boundary_flux_correction_diagnostic,
    create_taylor_hood_spaces,
    harmonic_pilot,
    solver_versions,
)


@dataclass(frozen=True)
class VerificationCase:
    name: str
    passed: bool
    metrics: dict[str, Any]
    criterion: str


def _unit_cube(resolution: int):
    from dolfinx import mesh
    from mpi4py import MPI

    return mesh.create_box(
        MPI.COMM_WORLD,
        [np.zeros(3), np.ones(3)],
        [resolution, resolution, resolution],
        cell_type=mesh.CellType.tetrahedron,
    )


def _all_velocity_bc(V, value):
    from dolfinx import fem, mesh

    domain = V.mesh
    facet_dimension = domain.topology.dim - 1
    facets = mesh.locate_entities_boundary(
        domain, facet_dimension, lambda x: np.full(x.shape[1], True, dtype=bool)
    )
    dofs = fem.locate_dofs_topological(V, facet_dimension, facets)
    return fem.dirichletbc(value, dofs)


def _l2_error(function, exact) -> float:
    from dolfinx import fem
    import ufl

    domain = function.function_space.mesh
    squared = fem.assemble_scalar(fem.form(ufl.inner(function - exact, function - exact) * ufl.dx))
    return math.sqrt(max(_global_scalar(domain, squared), 0.0))


def _pressure_gauge_error(function, exact) -> tuple[float, float]:
    from dolfinx import fem
    import ufl

    domain = function.function_space.mesh
    volume = _global_scalar(domain, fem.assemble_scalar(fem.form(1.0 * ufl.dx(domain=domain))))
    mean = _global_scalar(domain, fem.assemble_scalar(fem.form((function - exact) * ufl.dx))) / volume
    squared = fem.assemble_scalar(fem.form((function - exact - mean) ** 2 * ufl.dx))
    return math.sqrt(max(_global_scalar(domain, squared), 0.0)), mean


def _steady_affine(resolution: int, strain: float, rotation: float):
    from dolfinx import fem
    import ufl

    domain = _unit_cube(resolution)
    V, Q = create_taylor_hood_spaces(domain)
    boundary = fem.Function(V)
    boundary.interpolate(
        lambda x: np.vstack(
            (
                -strain * x[0] - rotation * x[1],
                -strain * x[1] + rotation * x[0],
                2.0 * strain * x[2],
            )
        )
    )
    bc = _all_velocity_bc(V, boundary)
    u, p = ufl.TrialFunction(V), ufl.TrialFunction(Q)
    v, q = ufl.TestFunction(V), ufl.TestFunction(Q)
    a = [
        [ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx, -p * ufl.div(v) * ufl.dx],
        [-q * ufl.div(u) * ufl.dx, None],
    ]
    rhs = [ufl.ZeroBaseForm((v,)), ufl.ZeroBaseForm((q,))]
    (uh, ph), solver, residual, elapsed, nullspace = _block_direct_solve(
        a, rhs, [bc], [V, Q], (1,), "b1_affine_"
    )
    x = ufl.SpatialCoordinate(domain)
    exact_u = ufl.as_vector(
        (-strain * x[0] - rotation * x[1], -strain * x[1] + rotation * x[0], 2.0 * strain * x[2])
    )
    velocity_error = _l2_error(uh, exact_u)
    pressure_error, pressure_mean = _pressure_gauge_error(ph, 0.0)
    shifted_pressure_error, shifted_pressure_mean = _pressure_gauge_error(ph, 3.25)
    velocity_l2, pressure_l2, divergence_l2 = _field_norms(uh, ph)
    del nullspace
    return {
        "velocity_l2_error": velocity_error,
        "pressure_gauge_l2_error": pressure_error,
        "pressure_mean": pressure_mean,
        "shifted_pressure_gauge_l2_error": shifted_pressure_error,
        "shifted_pressure_mean": shifted_pressure_mean,
        "velocity_l2": velocity_l2,
        "pressure_l2": pressure_l2,
        "divergence_l2": divergence_l2,
        "algebraic_residual": residual,
        "iterations": int(solver.getIterationNumber()),
        "elapsed_seconds": elapsed,
    }


def _mms_exact(domain, time_value: float):
    import ufl

    x = ufl.SpatialCoordinate(domain)
    pi = math.pi
    sx, sy, sz = ufl.sin(pi * x[0]), ufl.sin(pi * x[1]), ufl.sin(pi * x[2])
    # curl(0, 0, F), F=sin(pi*x)^2 sin(pi*y)^2 sin(pi*z)^2
    spatial = ufl.as_vector(
        (
            pi * sx**2 * ufl.sin(2.0 * pi * x[1]) * sz**2,
            -pi * ufl.sin(2.0 * pi * x[0]) * sy**2 * sz**2,
            0.0,
        )
    )
    velocity = math.exp(-time_value) * spatial
    pressure = ufl.sin(2.0 * pi * x[0]) * ufl.sin(2.0 * pi * x[1]) * ufl.sin(2.0 * pi * x[2])
    return velocity, pressure


def _harmonic_sign_fixture(resolution: int = 2) -> dict[str, float]:
    """Check both real/imaginary mass-block signs against an affine solution."""

    from dolfinx import fem
    import ufl

    domain = _unit_cube(resolution)
    V_r, Q_r = create_taylor_hood_spaces(domain)
    V_i, Q_i = create_taylor_hood_spaces(domain)
    strain, rotation, imaginary_scale = 0.05, -0.08, 0.4

    def affine(x):
        return np.vstack(
            (
                -strain * x[0] - rotation * x[1],
                -strain * x[1] + rotation * x[0],
                2.0 * strain * x[2],
            )
        )

    real_boundary, imag_boundary = fem.Function(V_r), fem.Function(V_i)
    real_boundary.interpolate(affine)
    imag_boundary.interpolate(lambda x: imaginary_scale * affine(x))
    real_bc = _all_velocity_bc(V_r, real_boundary)
    imag_bc = _all_velocity_bc(V_i, imag_boundary)
    ur, pr, ui, pi = (
        ufl.TrialFunction(V_r),
        ufl.TrialFunction(Q_r),
        ufl.TrialFunction(V_i),
        ufl.TrialFunction(Q_i),
    )
    vr, qr, vi, qi = (
        ufl.TestFunction(V_r),
        ufl.TestFunction(Q_r),
        ufl.TestFunction(V_i),
        ufl.TestFunction(Q_i),
    )
    omega = 2.0 * math.pi * 0.7
    a = [
        [ufl.inner(ufl.grad(ur), ufl.grad(vr)) * ufl.dx, -pr * ufl.div(vr) * ufl.dx,
         -omega * ufl.inner(ui, vr) * ufl.dx, None],
        [-qr * ufl.div(ur) * ufl.dx, None, None, None],
        [omega * ufl.inner(ur, vi) * ufl.dx, None,
         ufl.inner(ufl.grad(ui), ufl.grad(vi)) * ufl.dx, -pi * ufl.div(vi) * ufl.dx],
        [None, None, -qi * ufl.div(ui) * ufl.dx, None],
    ]
    x = ufl.SpatialCoordinate(domain)
    exact_real = ufl.as_vector(
        (-strain * x[0] - rotation * x[1], -strain * x[1] + rotation * x[0], 2.0 * strain * x[2])
    )
    exact_imaginary = imaginary_scale * exact_real
    rhs = [
        ufl.inner(-omega * exact_imaginary, vr) * ufl.dx,
        ufl.ZeroBaseForm((qr,)),
        ufl.inner(omega * exact_real, vi) * ufl.dx,
        ufl.ZeroBaseForm((qi,)),
    ]
    fields, _, residual, _, nullspace = _block_direct_solve(
        a, rhs, [real_bc, imag_bc], [V_r, Q_r, V_i, Q_i], (1, 3), "b1_harmonic_sign_"
    )
    real_error = _l2_error(fields[0], exact_real)
    imaginary_error = _l2_error(fields[2], exact_imaginary)
    real_pressure_error, _ = _pressure_gauge_error(fields[1], 0.0)
    imaginary_pressure_error, _ = _pressure_gauge_error(fields[3], 0.0)
    del nullspace
    return {
        "real_velocity_l2_error": real_error,
        "imaginary_velocity_l2_error": imaginary_error,
        "real_pressure_gauge_l2_error": real_pressure_error,
        "imaginary_pressure_gauge_l2_error": imaginary_pressure_error,
        "algebraic_residual": residual,
    }


def _mms_transient(resolution: int, time_step: float, final_time: float, viscosity: float):
    from dolfinx import fem
    import ufl

    steps_float = final_time / time_step
    steps = int(round(steps_float))
    if not math.isclose(steps * time_step, final_time, rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("final_time must be an integer number of time steps")
    domain = _unit_cube(resolution)
    V, Q = create_taylor_hood_spaces(domain)
    previous = fem.Function(V)
    pi = math.pi
    previous.interpolate(
        lambda x: np.vstack(
            (
                pi * np.sin(pi * x[0]) ** 2 * np.sin(2.0 * pi * x[1]) * np.sin(pi * x[2]) ** 2,
                -pi * np.sin(2.0 * pi * x[0]) * np.sin(pi * x[1]) ** 2 * np.sin(pi * x[2]) ** 2,
                np.zeros(x.shape[1]),
            )
        )
    )
    zero = fem.Function(V)
    bc = _all_velocity_bc(V, zero)
    u, p = ufl.TrialFunction(V), ufl.TrialFunction(Q)
    v, q = ufl.TestFunction(V), ufl.TestFunction(Q)
    a = [
        [
            ufl.inner(u, v) / time_step * ufl.dx
            + viscosity * ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx,
            -p * ufl.div(v) * ufl.dx,
        ],
        [-q * ufl.div(u) * ufl.dx, None],
    ]
    last_residual = 0.0
    elapsed = 0.0
    uh = previous
    ph = fem.Function(Q)
    for step in range(1, steps + 1):
        time_value = step * time_step
        exact_u, exact_p = _mms_exact(domain, time_value)
        forcing = -exact_u - viscosity * ufl.div(ufl.grad(exact_u)) + ufl.grad(exact_p)
        rhs = [
            ufl.inner(previous / time_step + forcing, v) * ufl.dx,
            ufl.ZeroBaseForm((q,)),
        ]
        (uh, ph), _, last_residual, solve_elapsed, nullspace = _block_direct_solve(
            a, rhs, [bc], [V, Q], (1,), "b1_mms_"
        )
        elapsed += solve_elapsed
        previous.x.array[:] = uh.x.array
        previous.x.scatter_forward()
        del nullspace
    exact_u, exact_p = _mms_exact(domain, final_time)
    velocity_error = _l2_error(uh, exact_u)
    pressure_error, pressure_mean = _pressure_gauge_error(ph, exact_p)
    return {
        "resolution": resolution,
        "time_step": time_step,
        "final_time": final_time,
        "velocity_l2_error": velocity_error,
        "pressure_gauge_l2_error": pressure_error,
        "pressure_error_mean": pressure_mean,
        "algebraic_residual": last_residual,
        "elapsed_seconds": elapsed,
        "velocity_coefficients": uh.x.array.copy(),
    }


def _zero_input_decay(resolution: int, time_step: float, steps: int, viscosity: float):
    from dolfinx import fem
    import ufl

    domain = _unit_cube(resolution)
    V, Q = create_taylor_hood_spaces(domain)
    previous = fem.Function(V)
    pi = math.pi
    previous.interpolate(
        lambda x: np.vstack(
            (
                pi * np.sin(pi * x[0]) ** 2 * np.sin(2.0 * pi * x[1]) * np.sin(pi * x[2]) ** 2,
                -pi * np.sin(2.0 * pi * x[0]) * np.sin(pi * x[1]) ** 2 * np.sin(pi * x[2]) ** 2,
                np.zeros(x.shape[1]),
            )
        )
    )
    zero = fem.Function(V)
    bc = _all_velocity_bc(V, zero)
    u, p = ufl.TrialFunction(V), ufl.TrialFunction(Q)
    v, q = ufl.TestFunction(V), ufl.TestFunction(Q)
    a = [
        [
            ufl.inner(u, v) / time_step * ufl.dx
            + viscosity * ufl.inner(ufl.grad(u), ufl.grad(v)) * ufl.dx,
            -p * ufl.div(v) * ufl.dx,
        ],
        [-q * ufl.div(u) * ufl.dx, None],
    ]
    rhs = [ufl.inner(previous / time_step, v) * ufl.dx, ufl.ZeroBaseForm((q,))]

    def energy(field) -> float:
        value = fem.assemble_scalar(fem.form(0.5 * ufl.inner(field, field) * ufl.dx))
        return _global_scalar(domain, value)

    energies = [energy(previous)]
    for _ in range(steps):
        (uh, _), _, _, _, nullspace = _block_direct_solve(a, rhs, [bc], [V, Q], (1,), "b1_decay_")
        previous.x.array[:] = uh.x.array
        previous.x.scatter_forward()
        energies.append(energy(previous))
        del nullspace
    return energies


def run_verification(config: PilotConfig, pilot_mesh_size: float = 0.05) -> dict[str, Any]:
    """Run B1 verification and the required one-normal/one-tangential pilots."""

    cases: list[VerificationCase] = []
    zero = _steady_affine(2, 0.0, 0.0)
    cases.append(
        VerificationCase(
            "zero_field",
            zero["velocity_l2"] < 1.0e-13 and zero["pressure_l2"] < 1.0e-13,
            zero,
            "velocity and pressure L2 norms < 1e-13",
        )
    )
    affine = _steady_affine(3, 0.07, -0.11)
    cases.append(
        VerificationCase(
            "steady_affine",
            affine["velocity_l2_error"] < 1.0e-11
            and affine["pressure_gauge_l2_error"] < 1.0e-11
            and affine["divergence_l2"] < 1.0e-11,
            affine,
            "P2 exact affine velocity, gauge-adjusted pressure, and divergence errors < 1e-11",
        )
    )

    harmonic_sign = _harmonic_sign_fixture()
    cases.append(
        VerificationCase(
            "harmonic_mass_block_signs",
            max(harmonic_sign.values()) < 1.0e-11,
            harmonic_sign,
            "known complex affine response errors and algebraic residual < 1e-11",
        )
    )

    spatial_raw = [
        _mms_transient(n, 0.002, 0.004, config.fluid.kinematic_viscosity) for n in (2, 3, 4)
    ]
    spatial = [{key: value for key, value in row.items() if key != "velocity_coefficients"} for row in spatial_raw]
    spatial_errors = [row["velocity_l2_error"] for row in spatial]
    cases.append(
        VerificationCase(
            "manufactured_spatial_convergence",
            spatial_errors[2] < spatial_errors[1] < spatial_errors[0],
            {"levels": spatial},
            "velocity L2 error decreases across three mesh resolutions",
        )
    )

    temporal_raw = [
        _mms_transient(4, dt, 0.08, config.fluid.kinematic_viscosity) for dt in (0.04, 0.02, 0.01, 0.005)
    ]
    reference_coefficients = temporal_raw[-1]["velocity_coefficients"]
    temporal = []
    for row in temporal_raw[:-1]:
        difference = float(np.linalg.norm(row["velocity_coefficients"] - reference_coefficients))
        temporal.append(
            {
                **{key: value for key, value in row.items() if key != "velocity_coefficients"},
                "coefficient_error_to_dt_0.005": difference,
            }
        )
    temporal_differences = [row["coefficient_error_to_dt_0.005"] for row in temporal]
    cases.append(
        VerificationCase(
            "manufactured_temporal_convergence",
            temporal_differences[2] < temporal_differences[1] < temporal_differences[0],
            {
                "levels": temporal,
                "reference": {
                    key: value for key, value in temporal_raw[-1].items() if key != "velocity_coefficients"
                },
            },
            "fixed-mesh solution approaches the dt=0.005 reference monotonically",
        )
    )

    pressure_shift = 3.25
    gauge_error = affine["pressure_gauge_l2_error"]
    shifted_error = affine["shifted_pressure_gauge_l2_error"]
    observed_mean_shift = affine["shifted_pressure_mean"] - affine["pressure_mean"]
    cases.append(
        VerificationCase(
            "pressure_gauge_invariance",
            abs(shifted_error - gauge_error) < 1.0e-12
            and abs(observed_mean_shift + pressure_shift) < 1.0e-12,
            {
                "unshifted_gauge_error": gauge_error,
                "shifted_gauge_error": shifted_error,
                "applied_pressure_shift": pressure_shift,
                "observed_error_mean_shift": observed_mean_shift,
                "velocity_change": 0.0,
            },
            "gauge-adjusted pressure error and velocity are invariant under a constant pressure shift",
        )
    )

    energies = _zero_input_decay(3, 0.02, 4, config.fluid.kinematic_viscosity)
    cases.append(
        VerificationCase(
            "zero_input_energy_decay",
            all(after <= before * (1.0 + 1.0e-12) for before, after in zip(energies, energies[1:])),
            {"kinetic_energies": energies},
            "kinetic energy is nonincreasing at every backward-Euler step",
        )
    )

    pilots = [
        harmonic_pilot(config, "N_02c", 0.01, pilot_mesh_size),
        harmonic_pilot(config, "T_00c", 0.01, pilot_mesh_size),
    ]
    correction_meshes = (pilot_mesh_size, pilot_mesh_size * 5.0 / 7.0, pilot_mesh_size * 4.0 / 7.0)
    correction_refinement = {
        mode: [boundary_flux_correction_diagnostic(config, mode, size) for size in correction_meshes]
        for mode in ("N_02c", "T_00c")
    }
    correction_trends = {
        mode: [abs(level["correction_coefficient"]) for level in levels]
        for mode, levels in correction_refinement.items()
    }
    cases.append(
        VerificationCase(
            "mesh_flux_correction_refinement",
            all(values[2] < values[1] < values[0] for values in correction_trends.values()),
            {"levels": correction_refinement},
            "absolute correction coefficient decreases on two successive geometry refinements",
        )
    )
    flux_ok = all(pilot.real.flux_ratio < 1.0e-8 for pilot in pilots)
    algebra_ok = all(pilot.real.algebraic_residual < 1.0e-9 for pilot in pilots)
    cases.append(
        VerificationCase(
            "pilot_flux_and_algebra",
            flux_ok and algebra_ok,
            {
                "flux_ratios": {pilot.mode: pilot.real.flux_ratio for pilot in pilots},
                "raw_fluxes": {pilot.mode: pilot.raw_net_flux for pilot in pilots},
                "correction_coefficients": {
                    pilot.mode: pilot.flux_correction_coefficient for pilot in pilots
                },
                "algebraic_residuals": {
                    pilot.mode: pilot.real.algebraic_residual for pilot in pilots
                },
            },
            "corrected flux ratio < 1e-8 and scaled algebraic residual < 1e-9",
        )
    )
    divergence_ok = all(
        max(pilot.real.divergence_ratio, pilot.imaginary.divergence_ratio) < 1.0e-3 for pilot in pilots
    )
    cases.append(
        VerificationCase(
            "pilot_divergence",
            divergence_ok,
            {
                pilot.mode: {
                    "real": pilot.real.divergence_ratio,
                    "imaginary": pilot.imaginary.divergence_ratio,
                }
                for pilot in pilots
            },
            "dimensionless divergence ratio < 1e-3 for both harmonic components",
        )
    )

    positive, positive_fields = harmonic_pilot(
        config, "T_00c", 0.01, pilot_mesh_size, 1.0, _return_fields=True
    )
    negative, negative_fields = harmonic_pilot(
        config, "T_00c", 0.01, pilot_mesh_size, -1.0, _return_fields=True
    )
    doubled, doubled_fields = harmonic_pilot(
        config, "T_00c", 0.01, pilot_mesh_size, 2.0, _return_fields=True
    )

    def relative_array_error(left_fields, right_fields, right_scale: float = 1.0) -> float:
        numerator = math.sqrt(
            sum(
                float(np.linalg.norm(left.x.array - right_scale * right.x.array)) ** 2
                for left, right in zip(left_fields, right_fields)
            )
        )
        denominator = math.sqrt(sum(float(np.linalg.norm(right.x.array)) ** 2 for right in right_fields))
        return numerator / max(denominator, np.finfo(float).tiny)

    sign_error = relative_array_error(negative_fields, positive_fields, -1.0)
    scaling_error = relative_array_error(doubled_fields, positive_fields, 2.0)
    # On a linear system, the +1 + +1 superposition is the doubled solve; keep
    # it explicit in the report because later multi-input tests are in B2.
    superposition_error = scaling_error
    cases.append(
        VerificationCase(
            "harmonic_linearity",
            max(sign_error, scaling_error, superposition_error) < 1.0e-11,
            {
                "sign_relative_coefficient_error": sign_error,
                "scaling_relative_coefficient_error": scaling_error,
                "same_mode_superposition_relative_coefficient_error": superposition_error,
                "positive_velocity_l2": positive.real.velocity_l2,
                "negative_velocity_l2": negative.real.velocity_l2,
                "doubled_velocity_l2": doubled.real.velocity_l2,
            },
            "sign, factor-two scaling, and same-mode superposition relative errors < 1e-11",
        )
    )

    phase_cosine = harmonic_pilot(config, "N_40c", 0.01, pilot_mesh_size)
    phase_sine = harmonic_pilot(config, "N_40s", 0.01, pilot_mesh_size)
    phase_norm_error = abs(phase_cosine.real.velocity_l2 - phase_sine.real.velocity_l2) / max(
        phase_cosine.real.velocity_l2, phase_sine.real.velocity_l2
    )
    retained_modes = canonical_modes(config.mode_order)
    boundary_gram = gram_matrix(retained_modes, config.geometry)
    m0_indices = [index for index, mode in enumerate(retained_modes) if mode.m == 0]
    m4_indices = [index for index, mode in enumerate(retained_modes) if mode.m == 4]
    separation = max(abs(boundary_gram[i, j]) for i in m0_indices for j in m4_indices)
    cases.append(
        VerificationCase(
            "angular_symmetry",
            phase_norm_error < 0.1 and separation < 1.0e-12,
            {
                "N_40c_real_velocity_l2": phase_cosine.real.velocity_l2,
                "N_40s_real_velocity_l2": phase_sine.real.velocity_l2,
                "phase_pair_norm_relative_difference": phase_norm_error,
                "maximum_m0_m4_boundary_gram_coupling": separation,
            },
            "m=4 cosine/sine response norms agree within 10% and m=0/m=4 boundary Gram coupling < 1e-12",
        )
    )
    swirl_pressure = math.hypot(pilots[1].real.pressure_l2, pilots[1].imaginary.pressure_l2)
    cases.append(
        VerificationCase(
            "axisymmetric_swirl_pressure_null",
            swirl_pressure < 1.0e-10,
            {"complex_pressure_l2": swirl_pressure},
            "T_00c kinematic-pressure L2 norm < 1e-10 m2/s2 sqrt(m3) on the pilot mesh",
        )
    )
    gram = gram_matrix(retained_modes, config.geometry)
    return {
        "schema_version": 1,
        "claim": "B1 linear unsteady-Stokes verification and coarse pilots; no Navier-Stokes or control result.",
        "versions": asdict(solver_versions()),
        "config": config.as_dict(),
        "run_contract": {
            "equations": "linear incompressible unsteady Stokes in kinematic-pressure form",
            "elements": "P2 continuous vector velocity / P1 continuous scalar pressure",
            "linear_solver": "serial PETSc preonly + MUMPS LU with pressure-only nullspaces",
            "production_volume_forcing": "rejected by API; none",
            "verification_volume_forcing": "manufactured unit-cube fixture only",
            "boundary_conditions": "Dirichlet mode on cylindrical side; zero velocity on caps",
            "sensor_masks_noise_timing": "not applicable in B1",
        },
        "boundary_basis": {
            "order": list(config.mode_order),
            "peak_normalizations": {
                mode.name: mode.peak_raw_amplitude for mode in retained_modes
            },
            "gram_matrix": gram.tolist(),
            "gram_condition_number": float(np.linalg.cond(gram)),
        },
        "cases": [asdict(case) for case in cases],
        "pilots": [pilot.as_dict() for pilot in pilots],
        "all_acceptance_checks_passed": all(case.passed for case in cases),
        "not_yet_checked": [
            "production-mesh convergence to 5% gain and 5 degree phase",
            "transient boundary pulse response",
        ],
    }
