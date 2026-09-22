# R192 operating-point arithmetic evidence

[Design and limitations](../../FIXED_CORE_OPERATING_POINT_R192.md).
`check_operating_point.py` is a standard-library arithmetic/check script, not a
solver, controller or hardware model. Run from the repository root:

```bash
.venv/bin/python docs/realizability/evidence/r192/check_operating_point.py
```

It regenerates `operating_point.json` beside itself. Python 3.12.14 completed
16 check groups: peak condition, signed steady central budget, volume balance,
four phase-pattern balances, positive port flow, branch Reynolds screen,
independent phase quadrature, quadrature-phase null, both cap integration weights,
uncertainty allocations, harmonic diffusion identity/sensitivity and the
noise-only effective-sample threshold. All values are conditional design scales.
The common line uses an assumed Darcy-factor range, not laminar branch friction.

No measured response, optical uncertainty, pump curve, true wall torque or
finite-tank solution is present. No dependencies or production code changed.
