"""Sufficient local energy certificate for the B2 affine-tetrahedron SIP form.

This NumPy calculation never assembles a global finite-element operator. An
inconclusive bound says only that this sufficient certificate did not apply.
"""

from __future__ import annotations

from dataclasses import asdict
import itertools
import math
import resource
import time
from typing import Any

import numpy as np

from ..config import PilotConfig
from .fenicsx_stokes import _mesh_sha256, create_cylinder, solver_versions


CELL_LIMIT = 500


def p1_mass_matrix(volume: float) -> np.ndarray:
    """Analytic consistent P1 mass matrix on a tetrahedron."""
    if not math.isfinite(volume) or volume <= 0.0:
        raise ValueError("Cell volume must be finite and positive.")
    return (volume / 20.0) * (np.ones((4, 4)) + np.eye(4))


def face_trace_matrix(area: float, local_vertices: tuple[int, int, int]) -> np.ndarray:
    """Analytic integral of the P1 basis products on one triangular face."""
    if not math.isfinite(area) or area <= 0.0:
        raise ValueError("Face area must be finite and positive.")
    if len(set(local_vertices)) != 3 or any(i not in range(4) for i in local_vertices):
        raise ValueError("A tetrahedron face must contain three distinct local vertices.")
    result = np.zeros((4, 4), dtype=float)
    result[np.ix_(local_vertices, local_vertices)] = (area / 12.0) * (np.ones((3, 3)) + np.eye(3))
    return result


def _cell_geometry(vertices: np.ndarray) -> tuple[float, float]:
    volume = abs(float(np.linalg.det(vertices[1:] - vertices[:1]))) / 6.0
    diameter = max(float(np.linalg.norm(vertices[i] - vertices[j])) for i, j in itertools.combinations(range(4), 2))
    return volume, diameter


def _validate_connected(faces: dict[tuple[int, ...], list[tuple[int, tuple[int, int, int]]]], cells: int) -> None:
    adjacency = [set() for _ in range(cells)]
    for owners in faces.values():
        if len(owners) not in (1, 2):
            raise ValueError("Invalid face adjacency: every face must have one or two incident cells.")
        if len(owners) == 2:
            left, right = owners[0][0], owners[1][0]
            adjacency[left].add(right)
            adjacency[right].add(left)
    reached = {0}
    todo = [0]
    while todo:
        for other in adjacency[todo.pop()]:
            if other not in reached:
                reached.add(other)
                todo.append(other)
    if len(reached) != cells:
        raise ValueError("The coercivity certificate requires a connected mesh.")


def calculate_local_bound(domain: Any, *, max_cells: int = CELL_LIMIT) -> dict[str, Any]:
    """Compute the conservative local trace bound on a serial affine tetra mesh."""
    started = time.perf_counter()
    if max_cells < 1:
        raise ValueError("max_cells must be positive.")
    if domain.comm.size != 1:
        raise ValueError("The local coercivity diagnostic is serial only.")
    if domain.topology.dim != 3 or domain.geometry.dofmap.shape[1] != 4:
        raise ValueError("Only tetrahedral geometry is supported.")
    if getattr(domain.geometry.cmap, "degree", None) != 1:
        raise ValueError("Only affine tetrahedral geometry is supported.")
    cell_count = int(domain.topology.index_map(3).size_global)
    if cell_count > max_cells:
        raise OverflowError(f"Mesh has {cell_count} cells; local diagnostic limit is {max_cells}.")

    dofmap = np.asarray(domain.geometry.dofmap, dtype=np.int64)
    coordinates = np.asarray(domain.geometry.x, dtype=float)
    xyz = coordinates[dofmap, :3]
    if not np.isfinite(xyz).all():
        raise ValueError("Mesh coordinates must be finite.")
    volumes = np.empty(cell_count)
    diameters = np.empty(cell_count)
    for cell in range(cell_count):
        volumes[cell], diameters[cell] = _cell_geometry(xyz[cell])
        ratio = volumes[cell] / diameters[cell] ** 3 if diameters[cell] > 0 else 0.0
        if not math.isfinite(ratio) or ratio <= 1.0e-12:
            raise ValueError(f"Cell {cell} has unsupported volume/diameter^3 ratio {ratio!r}.")

    faces: dict[tuple[int, ...], list[tuple[int, tuple[int, int, int]]]] = {}
    for cell, nodes in enumerate(dofmap):
        for local in itertools.combinations(range(4), 3):
            key = tuple(sorted(int(nodes[i]) for i in local))
            faces.setdefault(key, []).append((cell, local))
    _validate_connected(faces, cell_count)
    domain.topology.create_connectivity(2, 3)
    face_to_cells = domain.topology.connectivity(2, 3)
    exterior_count = int(np.count_nonzero(np.asarray([len(face_to_cells.links(i)) == 1 for i in range(face_to_cells.num_nodes)], dtype=bool)))
    derived_exterior = sum(len(owners) == 1 for owners in faces.values())
    if exterior_count != derived_exterior or sum(len(owners) == 2 for owners in faces.values()) * 2 + exterior_count != 4 * cell_count:
        raise ValueError("Face incidence does not cover all exterior and interior tetrahedron facets.")

    trace = np.zeros((cell_count, 4, 4), dtype=float)
    for owners in faces.values():
        h_face = sum(diameters[cell] for cell, _ in owners) / len(owners)
        weight = 1.0 if len(owners) == 1 else 0.5
        for cell, local in owners:
            tri = xyz[cell, list(local)]
            area = float(np.linalg.norm(np.cross(tri[1] - tri[0], tri[2] - tri[0]))) / 2.0
            trace[cell] += weight * h_face * face_trace_matrix(area, local)

    ones = np.ones((4, 4))
    whitening = np.eye(4) - (1.0 - 1.0 / math.sqrt(5.0)) * ones / 4.0
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        whitened = (20.0 / volumes[:, None, None]) * (whitening @ trace @ whitening)
    if not np.isfinite(whitened).all():
        raise ValueError("Local trace calculation produced nonfinite values.")
    row_bounds = np.sum(np.abs(whitened), axis=2)
    if not np.isfinite(row_bounds).all():
        raise ValueError("Local row-sum bound produced nonfinite values.")
    cell_bounds = np.max(row_bounds, axis=1)
    worst = int(np.argmax(cell_bounds))
    exact_trace_max = float(max(np.linalg.eigvalsh(item)[-1] for item in whitened))
    cell_trace_eigenvalues = [float(np.linalg.eigvalsh(item)[-1]) for item in whitened]
    c_upper = float(cell_bounds[worst])
    c_safe = c_upper + 1.0e-10 * max(1.0, c_upper)
    if not math.isfinite(c_safe):
        raise ValueError("Guarded coercivity bound is nonfinite.")
    return {
        "cell_count": cell_count,
        "facet_count": len(faces),
        "exterior_facet_count": exterior_count,
        "interior_facet_count": len(faces) - exterior_count,
        "minimum_cell_volume_m3": float(np.min(volumes)),
        "minimum_cell_diameter_m": float(np.min(diameters)),
        "worst_cell": worst,
        "worst_cell_trace_eigenvalue": exact_trace_max,
        "cell_trace_eigenvalues": cell_trace_eigenvalues,
        "C_upper": c_upper,
        "C_safe": c_safe,
        "elapsed_seconds": time.perf_counter() - started,
    }


def _classify(c_upper: float, alpha: float) -> dict[str, Any]:
    safe = c_upper + 1.0e-10 * max(1.0, c_upper)
    ratio = safe / alpha
    if not math.isfinite(safe) or not math.isfinite(ratio):
        return {"penalty_factor": alpha, "status": "invalid", "beta": None,
                "reason": "guarded coercivity calculation produced a nonfinite value"}
    beta = 1.0 - math.sqrt(ratio)
    if not math.isfinite(beta):
        return {"penalty_factor": alpha, "status": "invalid", "beta": None,
                "reason": "guarded coercivity margin is nonfinite"}
    if beta > 1.0e-8:
        return {"penalty_factor": alpha, "status": "certified_positive", "beta": beta, "reason": None}
    return {"penalty_factor": alpha, "status": "inconclusive", "beta": beta, "reason": "sufficient guarded coercivity margin is not above 1e-8"}


def run_b2_coercivity(config: PilotConfig, mesh_sizes: tuple[float, ...] = (0.10, 0.07, 0.05),
                      penalty_factors: tuple[float, ...] = (48.0, 96.0), *, max_cells: int = CELL_LIMIT) -> dict[str, Any]:
    """Build bounded cylinder fixtures and evaluate the separate sufficient certificate."""
    if not mesh_sizes or not penalty_factors or any(not math.isfinite(x) or x <= 0 for x in (*mesh_sizes, *penalty_factors)):
        raise ValueError("Mesh sizes and penalty factors must be finite, positive, and nonempty.")
    if not math.isfinite(config.fluid.kinematic_viscosity) or config.fluid.kinematic_viscosity <= 0:
        raise ValueError("Kinematic viscosity must be finite and positive.")
    started = time.perf_counter()
    records = []
    for mesh_size in mesh_sizes:
        domain, _, _ = create_cylinder(config, mesh_size)
        try:
            bound = calculate_local_bound(domain, max_cells=max_cells)
            records.append({
                "mesh_size_m": mesh_size,
                "mesh_sha256": _mesh_sha256(domain),
                "status": "evaluated",
                "bound": bound,
                "penalty_cases": [_classify(bound["C_upper"], alpha) for alpha in penalty_factors],
            })
        except OverflowError as error:
            records.append({"mesh_size_m": mesh_size, "mesh_sha256": _mesh_sha256(domain),
                            "status": "resource_limit", "reason": str(error), "penalty_cases": []})
        except (ValueError, FloatingPointError) as error:
            records.append({"mesh_size_m": mesh_size, "mesh_sha256": _mesh_sha256(domain),
                            "status": "invalid", "reason": str(error), "penalty_cases": []})
    return {
        "schema_version": 1,
        "diagnostic": "B2 sufficient local coercivity certificate",
        "claim": "Positive local certificate proves dissipation of the homogeneous semidiscrete SIP form; inconclusive does not mean unstable.",
        "formulation": "BDM2/DG1 symmetric interior-penalty viscosity on affine tetrahedra",
        "config": config.as_dict(),
        "kinematic_viscosity_m2_per_s": config.fluid.kinematic_viscosity,
        "energy_bound_units": "dimensionless energy-norm margin beta; not a decay rate",
        "guards": {"max_cells": max_cells, "minimum_volume_over_diameter_cubed": 1.0e-12,
                   "C_safe_relative_pad": 1.0e-10, "minimum_beta_exclusive": 1.0e-8},
        "campaign_ready": False,
        "campaign_blockers": ["physical response accuracy and error floor remain unreviewed"],
        "mesh_results": records,
        "elapsed_seconds": time.perf_counter() - started,
        "process_peak_rss_mib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0,
        "versions": asdict(solver_versions()),
    }


def format_b2_coercivity(report: dict[str, Any]) -> str:
    lines = ["# B2 local coercivity diagnostic", "", report["claim"], "",
             f"Campaign ready: **{report['campaign_ready']}**", "",
             "| Mesh (m) | Cells | Mesh SHA-256 | C upper | Penalty | Status | beta |",
             "|---:|---:|---|---:|---:|---|---:|"]
    for record in report["mesh_results"]:
        bound = record.get("bound", {})
        for case in record.get("penalty_cases", [{}]):
            lines.append(f"| {record['mesh_size_m']:g} | {bound.get('cell_count', '—')} | `{record.get('mesh_sha256', '—')}` | {bound.get('C_upper', float('nan')):.8g} | {case.get('penalty_factor', '—')} | {case.get('status', record['status'])} | {case.get('beta', float('nan')):.8g} |")
    lines.extend(["", "Inconclusive means this sufficient bound did not certify positivity; it does not indicate instability.", "",
                  "## Campaign blockers", "", *[f"- {item}" for item in report["campaign_blockers"]], ""])
    notes = []
    for record in report["mesh_results"]:
        if record["status"] != "evaluated":
            notes.append(f"- {record['mesh_size_m']:g} m: **{record['status']}** — {record.get('reason', 'no reason recorded')}.")
        else:
            notes.extend(
                f"- {record['mesh_size_m']:g} m, alpha={case['penalty_factor']:g}: {case['reason']}."
                for case in record["penalty_cases"] if case["status"] == "inconclusive"
            )
    lines.extend(["## Diagnostic notes", "", *(notes or ["- No inconclusive, invalid, or resource-limited cases."]), ""])
    return "\n".join(lines)
