# Isolated nonlinear port verification source — R195/R196

**Source and algebra evidence, not a validated FEM solver.** The
[R195 fixture review](../../docs/realizability/NONLINEAR_VERIFICATION_R195.md)
derives the exact data. The [R196 adapter review](../../docs/realizability/CUBE_ADAPTER_R196.md)
records implementation, tests and the execution refusal. No production B1/B2
module imports this directory; no dependency pins changed.

- `polynomial.py`, `fixtures.py`: exact rational manufactured fields and
  independent Poiseuille/rigid-rotation oracles.
- `prototype.py`: injected P2/P1 weak forms, damped Newton and BE/BDF2 kernels;
  dense toy and sparse CSR paths. `launch()` always refuses.
- `cube_adapter.py`: injected serial tetrahedral cube/tagging, exact fixture
  loads, boundary-value extraction, mixed-plus-three-scalar assembly and sparse
  PETSc LU source. No external imports, CLI or supervised driver.
- `sparse.py`: CSR bordering, retained lifting rows, fixed step scaling and
  a three-constraint Gram rank/condition screen.
- `diagnostics.py`: unassembled field/error/budget forms, signed reductions,
  numerical step gates, refinement/quadrature checks and physical endpoint
  versus discrete time-integrated balances. It cannot accept a whole run.
- `future_fem.json`, `manifest.py`: frozen **non-executable** proposal; zero
  granted attempts. The 180 s / 1536 MiB one-suite caps remain proposals.
- `test_algebra.py`, `test_adapter.py`: 24 standard-library tests; no FEM imports.

```sh
.venv/bin/python -m unittest verification.nonlinear_port.test_algebra verification.nonlinear_port.test_adapter -v
```

A future driver must inject the pinned modules under admitted supervision,
verify actual geometry/pins, install the current trace before all residual
rows, screen assembled compatibility/rank, freeze scales, and retain historical
velocities. It must sample both returns at the actual quadrature points,
collect/validate every diagnostic, reject failures before advancing history,
and record process exit/cleanup. None of that orchestration has run.
The sparse and analytical checks do not establish UFL validity, actual mesh
rank, inf-sup stability, sparse factorization success or convergence. No tank
entry exists. Follow the single [handoff task](../../SESSION_HANDOFF.md#next-task).
