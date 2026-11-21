"""Dimensional estimates for Gaussian-vorticity water profiles, in SI units."""

from dataclasses import asdict, dataclass
import json
import math

# Positive root of exp(x) = 1 + 2x, where swirl speed is maximal.
PEAK_X = 1.2564312086261697
DENSITY = 998.0  # kg/m^3
VISCOSITY = 1.0e-6  # kinematic, m^2/s
SOUND_SPEED = 1480.0  # m/s


@dataclass(frozen=True)
class Scales:
    peak_radius_m: float
    peak_speed_m_s: float
    gaussian_width_m: float
    circulation_m2_s: float
    reynolds: float
    mach: float
    viscous_time_s: float
    dynamic_pressure_pa: float
    center_deficit_pa: float
    velocity_gradient_s_inv: float
    burgers_axial_strain_s_inv: float


def scales(peak_radius_m: float, peak_speed_m_s: float) -> Scales:
    """Use peak radius and speed magnitude. Pressure is relative to infinity."""
    if not math.isfinite(peak_radius_m) or peak_radius_m <= 0:
        raise ValueError("peak radius must be positive and finite")
    if not math.isfinite(peak_speed_m_s) or peak_speed_m_s < 0:
        raise ValueError("peak speed must be nonnegative and finite")

    width = peak_radius_m / math.sqrt(PEAK_X)
    circulation_over_2pi = peak_radius_m * peak_speed_m_s / -math.expm1(-PEAK_X)
    return Scales(
        peak_radius_m=peak_radius_m,
        peak_speed_m_s=peak_speed_m_s,
        gaussian_width_m=width,
        circulation_m2_s=2 * math.pi * circulation_over_2pi,
        reynolds=peak_speed_m_s * peak_radius_m / VISCOSITY,
        mach=peak_speed_m_s / SOUND_SPEED,
        viscous_time_s=peak_radius_m**2 / VISCOSITY,
        dynamic_pressure_pa=0.5 * DENSITY * peak_speed_m_s**2,
        center_deficit_pa=DENSITY * (circulation_over_2pi / width)**2 * math.log(2),
        velocity_gradient_s_inv=peak_speed_m_s / peak_radius_m,
        burgers_axial_strain_s_inv=4 * VISCOSITY / width**2,
    )


if __name__ == "__main__":
    # Compare profiles at fixed circulation. No time or contraction law is assumed.
    speed_radius_product = 0.1 * 0.010
    rows = [scales(r, speed_radius_product / r) for r in (0.010, 0.003, 0.001)]
    print(json.dumps([asdict(row) for row in rows], indent=2, allow_nan=False))
