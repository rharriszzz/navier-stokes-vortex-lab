"""Diagnostics and optional Stokes verification backends for realizability.

B0 provides NumPy-only benchmark diagnostics. Optional DOLFINx B1 and B2
backends run linear Stokes verification cases; B1's strong-divergence check
failed its required tolerance, and the B2 physical-response gate remains
unresolved. Verification fixtures do not validate the physical response or
demonstrate boundary control. This package does not solve the nonlinear
Navier--Stokes target or implement a controller.
"""

from .config import PilotConfig, load_config

__all__ = ["PilotConfig", "load_config"]
