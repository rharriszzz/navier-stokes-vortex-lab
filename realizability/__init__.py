"""NumPy-only contracts for the physical-realizability research track.

This package contains reference fixtures and diagnostics only.  It does not
solve the Navier--Stokes equations or implement a controller.
"""

from .config import PilotConfig, load_config

__all__ = ["PilotConfig", "load_config"]
