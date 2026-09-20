"""Versioned SI-unit configuration for the B0 boundary-control benchmark."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GeometryConfig:
    """Fixed cylindrical tank dimensions in metres."""

    radius: float = 0.10
    half_height: float = 0.15

    def __post_init__(self) -> None:
        if self.radius <= 0.0 or self.half_height <= 0.0:
            raise ValueError("Cylinder radius and half_height must be positive.")


@dataclass(frozen=True)
class FluidConfig:
    """Nominal water properties in SI units, not measured sample properties."""

    kinematic_viscosity: float = 1.0e-6
    density: float = 1000.0

    def __post_init__(self) -> None:
        if self.kinematic_viscosity <= 0.0 or self.density <= 0.0:
            raise ValueError("Fluid viscosity and density must be positive.")


@dataclass(frozen=True)
class ReferenceConfig:
    """Finite Gaussian-vorticity reference fixture in SI units."""

    duration: float = 100.0
    initial_core_radius: float = 0.010
    final_core_radius: float = 0.003
    initial_peak_swirl: float = 0.010
    radial_plateau: float = 0.040
    radial_cutoff: float = 0.080
    axial_plateau: float = 0.050
    axial_cutoff: float = 0.120

    def __post_init__(self) -> None:
        if self.duration <= 0.0:
            raise ValueError("Reference duration must be positive.")
        if min(self.initial_core_radius, self.final_core_radius) <= 0.0:
            raise ValueError("Reference core radii must be positive.")
        if not 0.0 < self.radial_plateau < self.radial_cutoff:
            raise ValueError("Radial cutoff values must satisfy 0 < plateau < cutoff.")
        if not 0.0 < self.axial_plateau < self.axial_cutoff:
            raise ValueError("Axial cutoff values must satisfy 0 < plateau < cutoff.")


@dataclass(frozen=True)
class PilotConfig:
    """B0 configuration.  Values are SI unless named otherwise."""

    schema_version: int = 1
    geometry: GeometryConfig = field(default_factory=GeometryConfig)
    fluid: FluidConfig = field(default_factory=FluidConfig)
    reference: ReferenceConfig = field(default_factory=ReferenceConfig)
    probe_velocity: float = 1.0e-7
    frequencies_hz: tuple[float, ...] = (0.01, 0.1, 1.0, 30.0)
    mode_order: tuple[str, ...] = (
        "N_02c",
        "T_00c",
        "N_40c",
        "N_40s",
        "T_40c",
        "T_40s",
    )

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError(f"Unsupported schema_version {self.schema_version}.")
        if self.probe_velocity <= 0.0:
            raise ValueError("probe_velocity must be positive.")
        if not self.frequencies_hz or any(frequency <= 0.0 for frequency in self.frequencies_hz):
            raise ValueError("frequencies_hz must contain positive values.")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _tuple_values(mapping: dict[str, Any], name: str) -> tuple[Any, ...]:
    value = mapping.get(name)
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array.")
    return tuple(value)


def load_config(path: Path) -> PilotConfig:
    """Load and validate a B0 JSON configuration without optional dependencies."""

    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("The configuration root must be an object.")
    try:
        return PilotConfig(
            schema_version=int(data.get("schema_version", 1)),
            geometry=GeometryConfig(**data.get("geometry", {})),
            fluid=FluidConfig(**data.get("fluid", {})),
            reference=ReferenceConfig(**data.get("reference", {})),
            probe_velocity=float(data.get("probe_velocity", 1.0e-7)),
            frequencies_hz=tuple(float(value) for value in _tuple_values(data, "frequencies_hz")),
            mode_order=tuple(str(value) for value in _tuple_values(data, "mode_order")),
        )
    except TypeError as error:
        raise ValueError(f"Invalid configuration structure: {error}") from error
