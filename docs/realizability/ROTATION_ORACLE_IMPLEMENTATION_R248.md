# R248 — Rotation exact-field oracle source

2026-09-26, PC/WSL daisy. Base `1facbf5`; STARTED `c0f86b2`.
**The R247 source contract is implemented and tested. No rotation assembly or
numerical execution occurred.** All five allocations remain spent; R246 stays
PASS under its fixed Poiseuille contract, while R242 remains INCOMPLETE.

## Source and decision boundary

[rotation_oracle.py](../../verification/nonlinear_port/rotation_oracle.py)
provides three independent entry points:

- `rotation_forms(U, domain, tags, degree)` builds 38 scalar forms for exact
  coordinate rotation and quadratic pressure, using injected UFL operations.
  It forms `grad(u)`, its symmetric part, `2 mu D`, physical stress,
  conservative convection, pressure gradient and the squared local momentum
  residual. It integrates full six-face traction and each tagged face's area
  and three normal components. It returns expressions only; it does not import
  UFL/DOLFINx or assemble a form.
- `contract_record()` and `validate_contract()` give a strict JSON-native
  fixture/schema/context/target/tolerance binding. The 38 rational targets,
  five zero norm keys, geometry keys and nonnegative keys match the
  [R247 proposal](evidence/r247/rotation_proposal.json). Boolean versus integer,
  tuple versus list, unknown/missing keys and nonfinite values refuse.
- `build_report(raw_by_degree, contract)` checks complete finite native scalar
  inventories for degrees 24 and 26, nonnegative squared values, independent
  exact-target decisions, derived zero norms and all 38 pair differences.
  `validate_report()` recomputes the entire record from raw values and refuses
  altered cached decisions. This is **numerical-only** acceptance; it has no
  authority to grant or report a supervised workload PASS. The prospective
  serialized report is capped at 2,000,000 bytes.

Both degrees use R247's geometry tolerance 1e-12, five zero squared-norm
limits 1e-20 (norms <=1e-10), other absolute target tolerance 1e-10 and
pair difference tolerance 1e-10. Each degree must satisfy exact targets;
a common-mode error cannot pass by pair agreement. No Poiseuille or legacy
threshold was changed. Exact velocity and quadratic pressure are coordinate
expressions; no P1 pressure interpolation or PDE solve was added.

## Checks

[Eight focused tests](../../verification/nonlinear_port/test_rotation_oracle.py)
pass. They compare the source record against the independently published R247
proposal and exercise the source form expressions using injected symbolic
recorders. Wiring checks require the positive pressure-gradient term, symmetric
stress and all six tagged faces; the audit's omitted-pressure, reversed-sign,
nonsymmetric-stress, cap-only and zero-output cases motivate negative report
controls. Other controls reject common-mode and one-degree errors, geometry
orientation/tag errors, missing/extra/nonfinite/bool/negative values, contract
or schema drift, missing degree records and corrupted cached decisions.

The [complete 85-test standard-library suite](evidence/r248/tests.json) passes:
R244's 77 plus the eight new tests. The [test transcript](evidence/r248/tests.txt)
records each case. Its import audit found no NumPy, DOLFINx, Basix, UFL,
FFCx, PETSc4py, MPI4py or SciPy modules. The runner itself is retained in
[evidence/r248/test_runner.py](evidence/r248/test_runner.py).
The [R248 checks/source inventory](evidence/r248/checks.json) records all 29
previous source/test/pin hashes unchanged and the two added files. Historical
run files, callers, allocations, pins and the non-executable manifest are
unchanged.

Symbolic recorders confirm expression wiring, not actual UFL compilation or
assembly. In particular, an exact zero form may simplify before JIT; its
library behavior remains unmeasured. Rotation's zero strain cannot validate
the scalar viscosity coefficient or a hard-coded zero stress on its own.
Neither this source contract nor R246's single Poiseuille solve establishes
mesh/time convergence, inf-sup stability, tank accuracy or physical control.

## Next task

**Astra/high reviews integration and admission prerequisites**, using this
source and R247's exact audit. Decide the smallest fixture-specific supervised
worker/controller dispatch and report contract, check how real zero forms and
all-face tags will be validated, and identify resource/attempt boundaries.
Publish an implementation-ready integration plan or precise blocker, then stop
before implementation, FEM import/JIT/assembly or new numerical allocation.
Keep five spent allowances spent; do not reuse directories or old callers.
Recommend Sol/high only when integration requirements are fixed.
[Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was searched and opened for high support; task fit is judgment. No model/session
switch or /new was performed by this task. PC retains ownership; Mac released.
