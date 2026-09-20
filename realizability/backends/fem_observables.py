"""Fixed physical quadrature for extracting B2 features from FEM fields."""

from __future__ import annotations

import numpy as np

from ..observables import linear_features


def evaluate_function(function, points: np.ndarray) -> np.ndarray:
    """Evaluate a serial DOLFINx function at physical points inside its mesh."""

    from dolfinx import geometry

    points = np.asarray(points, dtype=function.function_space.mesh.geometry.x.dtype)
    mesh = function.function_space.mesh
    if mesh.comm.size != 1:
        raise RuntimeError("B2 point evaluation is currently implemented only in serial.")
    tree = geometry.bb_tree(mesh, mesh.topology.dim)
    candidates = geometry.compute_collisions_points(tree, points)
    colliding = geometry.compute_colliding_cells(mesh, candidates, points)
    cells = np.full(points.shape[0], -1, dtype=np.int32)
    for index in range(points.shape[0]):
        links = colliding.links(index)
        if links.size:
            cells[index] = links[0]
    if np.any(cells < 0):
        missing = int(np.count_nonzero(cells < 0))
        raise RuntimeError(f"Could not locate {missing} diagnostic quadrature points in the mesh.")
    return np.asarray(function.eval(points, cells))


def _interval_rule(lower: float, upper: float, order: int) -> tuple[np.ndarray, np.ndarray]:
    points, weights = np.polynomial.legendre.leggauss(order)
    scale = 0.5 * (upper - lower)
    return 0.5 * (lower + upper) + scale * points, scale * weights


def _polar_rule(
    inner_radius: float, outer_radius: float, radial_order: int, angular_order: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    radius, radial_weights = _interval_rule(inner_radius, outer_radius, radial_order)
    theta = 2.0 * np.pi * np.arange(angular_order) / angular_order
    radius_grid, theta_grid = np.meshgrid(radius, theta, indexing="ij")
    weights = (
        radial_weights[:, np.newaxis]
        * radius_grid
        * (2.0 * np.pi / angular_order)
        * np.ones((1, angular_order))
    )
    points = np.column_stack(
        (
            (radius_grid * np.cos(theta_grid)).ravel(),
            (radius_grid * np.sin(theta_grid)).ravel(),
            np.zeros(radius_grid.size),
        )
    )
    return points, theta_grid.ravel(), weights.ravel(), radius_grid.ravel()


def extract_linear_features(
    velocity,
    *,
    plane_order: int = 18,
    radial_order: int = 18,
    angular_order: int = 96,
) -> np.ndarray:
    """Extract the six signed B2 features using fixed laboratory coordinates."""

    if plane_order < 2 or radial_order < 2 or angular_order < 16:
        raise ValueError("Diagnostic quadrature orders are too small.")

    x_values, x_weights = _interval_rule(-0.025, 0.025, plane_order)
    z_values, z_weights = _interval_rule(-0.025, 0.025, plane_order)
    x_grid, z_grid = np.meshgrid(x_values, z_values, indexing="ij")
    vertical_points = np.column_stack(
        (x_grid.ravel(), np.zeros(x_grid.size), z_grid.ravel())
    )
    vertical_values = evaluate_function(velocity, vertical_points)
    vertical_weights = np.outer(x_weights, z_weights).ravel()

    disk_points, _, disk_weights, _ = _polar_rule(
        0.0, 0.025, radial_order, angular_order
    )
    disk_values = evaluate_function(velocity, disk_points)

    annulus_points, annulus_theta, annulus_weights, _ = _polar_rule(
        0.015, 0.025, radial_order, angular_order
    )
    annulus_values = evaluate_function(velocity, annulus_points)
    cosine = np.cos(annulus_theta)
    sine = np.sin(annulus_theta)
    annulus_u_r = annulus_values[:, 0] * cosine + annulus_values[:, 1] * sine
    annulus_u_theta = -annulus_values[:, 0] * sine + annulus_values[:, 1] * cosine

    return linear_features(
        z_grid.ravel(),
        vertical_values[:, 2],
        vertical_weights,
        disk_points[:, 0],
        disk_points[:, 1],
        disk_values[:, 0],
        disk_values[:, 1],
        disk_weights,
        annulus_theta,
        annulus_u_r,
        annulus_u_theta,
        annulus_weights,
    )


def extract_complex_linear_features(fields: tuple[object, ...], **quadrature) -> np.ndarray:
    """Return complex features from a harmonic real/imaginary field tuple."""

    real_velocity, _, imaginary_velocity, *_ = fields
    return extract_linear_features(real_velocity, **quadrature) + 1j * extract_linear_features(
        imaginary_velocity, **quadrature
    )
