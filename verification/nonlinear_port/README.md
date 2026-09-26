# Isolated nonlinear port verification source — R195/R196/R222/R225

**Source and algebra evidence, not a validated FEM solver.** The
[R195 fixture review](../../docs/realizability/NONLINEAR_VERIFICATION_R195.md)
derives the exact data. The [R196 adapter review](../../docs/realizability/CUBE_ADAPTER_R196.md)
records the adapter implementation. The [R225 critical review](../../docs/realizability/POISEUILLE_REVIEW_R225.md)
repairs driver wiring/acceptance and records the current execution refusal. No production B1/B2
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
- `fixture_driver.py`: one n=2 Poiseuille BE step, measured compatibility and
  constraint rows, a non-exact free velocity guess, frozen scales, checked
  correction, degree-24/26 diagnostics and return quadrature samples. All FEM
  modules are injected after a supervised release.
- `worker.py`: held worker entry point; checks reservation, admission, own
  cgroup and one-thread settings before importing pinned FEM packages.
- `supervision.py`: exclusive reservation, held-scope fact checks, finite
  timing/cleanup/result records and refusal of missing evidence. The concrete worker backend below remains refused for whole-task execution;
  the current manifest admits zero attempts.
- `handshake.py`, `systemd_backend.py`: atomic held/completed messages and a
  Linux worker-scope backend. It reports incomplete whole-task coverage honestly:
  newly spawned control clients are outside the worker scope. No FEM release.
- `probe_systemd.py`: explicit benign host checks only; no FEM admission. R225's
  clean case failed exit metadata collection and stopped before expiry testing.
  Source repairs have mocked evidence only. Do not rerun without a bounded scope.
- Five `test_*.py` modules: 43 standard-library tests, including complete driver
  wiring with fake FEM boundaries and raw-evidence corruption refusals; no FEM import.

```sh
.venv/bin/python -m unittest verification.nonlinear_port.test_algebra verification.nonlinear_port.test_adapter verification.nonlinear_port.test_driver_supervision verification.nonlinear_port.test_driver_wiring verification.nonlinear_port.test_host_protocol -v
```

A future admitted host backend must create and verify the held whole-task
scope, release `worker.py`, observe its exit and confirm cleanup. The source
joins the existing adapter and diagnostics for a single oracle, but no FEM
package was imported and no mesh, form or solver was run. R225 ran a benign
standard-library worker and reconciled its cleanup; its failed live check does
not validate the corrected backend or independent expiry.
The [R222 review](../../docs/realizability/POISEUILLE_DRIVER_R222.md) records
the exact source boundary and the remaining execution-admission decision.
The sparse and analytical checks do not establish UFL validity, actual mesh
rank, inf-sup stability, sparse factorization success or convergence. No tank
entry exists. Follow the single [handoff task](../../SESSION_HANDOFF.md#next-task).
