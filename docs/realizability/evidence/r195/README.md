# R195 retained evidence

[Review and limits](../../NONLINEAR_VERIFICATION_R195.md).
[Source and reproduction command](../../../../verification/nonlinear_port/README.md).

`algebra_checks.txt` retains all fifteen named checks and observed test duration.
`checks.json` identifies the interpreter and scope. Python 3.12.14 ran only
standard-library algebra/schema/syntax checks; no FEM stack import/JIT, mesh,
assembly or PDE solve occurred. No physical/tank/campaign attempt was consumed.

The exact polynomial balances, Poiseuille/rotation and structural rank checks
are continuum/algebra evidence. Newton and time-loop checks use small scalar
algebra/ODE fixtures, not assembled Navier–Stokes equations. The source review
caught and removed an impossible single-mesh P1 pressure-exactness requirement
for rigid rotation before any FEM execution. Its pressure is quadratic.

Current source contains UFL/FEM builders with injected libraries; these remain
unconstructed and unvalidated. `launch()` refuses and the future manifest grants
zero attempts. No runtime, convergence, hardware or attainable-contraction claim.
