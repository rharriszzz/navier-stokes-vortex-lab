# Isolated nonlinear port verification source — R195/R196/R222/R225/R226

**Source and algebra evidence, not a validated FEM solver.** The
[R195 fixture review](../../docs/realizability/NONLINEAR_VERIFICATION_R195.md)
derives the exact data. The [R196 adapter review](../../docs/realizability/CUBE_ADAPTER_R196.md)
records the adapter implementation. The [R225 critical review](../../docs/realizability/POISEUILLE_REVIEW_R225.md)
repairs driver wiring/acceptance. The [R226 launcher review](../../docs/realizability/POISEUILLE_LAUNCHER_R226.md)
records passed benign host checks; the [R227 partial environment](../../docs/realizability/ENVIRONMENT_RESTORE_R227.md)
remains unvalidated after an installation timeout, preventing FEM admission. No production B1/B2
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
  cgroup, clean source/interpreter binding and one-thread settings before importing pinned FEM packages.
- `supervision.py`: exclusive reservation, held-scope fact checks, finite
  timing/cleanup/result records and refusal of missing evidence. The Linux backend
  now passes benign whole-task checks; the current manifest admits zero attempts.
- `handshake.py`, `systemd_backend.py`, `systemd_bus.py`: atomic held/completed
  messages and in-process Linux manager calls, with no spawned control clients.
  The finite caller and OS manager remain the explicit R103 trusted boundary.
- `source_binding.py`: clean Git revision/root checks inside the held scope and
  actual executable identity/hash binding before release.
- `probe_systemd.py`: explicit benign host checks only. R226's separately bounded
  clean-exit and independent-expiry/child-cleanup pair passed in 5.418188160 s.
  R225 failure evidence is retained; do not rerun without a new bounded scope.
- Six `test_*.py` modules: 49 standard-library tests, including complete driver
  wiring with fake FEM boundaries, raw-evidence corruption, source binding and
  manager-failure refusals; no FEM import.

```sh
.venv/bin/python -m unittest verification.nonlinear_port.test_algebra verification.nonlinear_port.test_adapter verification.nonlinear_port.test_driver_supervision verification.nonlinear_port.test_driver_wiring verification.nonlinear_port.test_host_protocol verification.nonlinear_port.test_source_bus -v
```

The host backend creates and verifies a held task scope, observes actual exit
and confirms cleanup; a separate execution admission is still required before
releasing `worker.py` for FEM. No FEM package was imported and no mesh, form or
solver ran. R226 validates benign behavior under the disclosed R103 boundary;
it does not validate the numerical fixture. See its review for measurement tails,
shortened probe deadlines, exact source revision and saved evidence.
The [R222 review](../../docs/realizability/POISEUILLE_DRIVER_R222.md) records
the exact source boundary and the remaining execution-admission decision.
The sparse and analytical checks do not establish UFL validity, actual mesh
rank, inf-sup stability, sparse factorization success or convergence. No tank
entry exists. Follow the single [handoff task](../../SESSION_HANDOFF.md#next-task).
