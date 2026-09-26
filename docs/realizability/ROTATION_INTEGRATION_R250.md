# R250 — Rotation supervised integration source

2026-09-26, PC/WSL daisy. Base `65dc366`; STARTED `5f81c6b`.
**The R249 fixture-specific integration source is implemented and tested without
numerical execution. Rotation admission still grants zero attempts.** R246
Poiseuille remains PASS; R242 remains INCOMPLETE. All five old allocations remain
spent. No FEM import, JIT, assembly, managed worker, run directory or caller
was launched in this task.

## Implemented boundary

The new [rotation proposal](../../verification/nonlinear_port/future_rotation.json)
and [validator](../../verification/nonlinear_port/rotation_manifest.py) freeze
schema 1, exact R248 contract, existing nine package pins, 180-second/1536-MiB
caps, 2-MB report cap and zero admitted attempts. They reject changed/missing/
extra fields and type drift. The separate admission validator requires a fresh
absolute run directory, exact source commit, manifest/contract digests,
interpreter path and executable hash, artifact-inventory digest, one attempt,
fixture/mode/kind and worker schema. This source contains **no admission record**
and no executable caller.

The [injected driver](../../verification/nonlinear_port/rotation_driver.py)
reuses the existing n=2 cube adapter and reports measured cell/vertex/exterior
facet/tag counts plus the disclosed unused 402-DOF P2/P1 setup space. It does
not interpolate that space, solve a PDE or construct a matrix. For each of 38
keys at degrees 24 and 26 it requires an ordinary domain-bound rank-zero UFL
Form with the correct cell or tagged-face integrals, calls `fem.form` and
`fem.assemble_scalar`, and keeps the actual finite real result. Every key,
including expected zeros, goes through assembly. Unsupported `ZeroBaseForm`,
wrong domain/rank/tag, skipped face, JIT error and nonreal/nonfinite values
refuse with degree/key progress in the worker log. Expected target values are
used only by the independent pure reducer.

The [rotation worker](../../verification/nonlinear_port/rotation_worker.py)
validates its strict proposal, reservation/admission, executable and source,
then reaches the held handshake before importing numerical packages. It reuses
the existing pinned module/artifact loader after release. It saves an exclusive
fsynced, serialized 2-MB-bounded numerical envelope containing exact context,
source binding, measured geometry, all 76 raw scalars and assembly receipts,
recomputed R248 oracle report, times and version/FFCx artifact identity. A
complete finite report is saved even if exact-target gates fail; controller
acceptance is separate. Exceptions before a complete report leave progress/error
evidence and the spent reservation, not a synthetic numerical report.

The new `supervise_rotation_once` entry in
[supervision.py](../../verification/nonlinear_port/supervision.py) uses a literal
rotation worker module and strict loader/validator. The old public
`supervise_once` remains Poiseuille-only with its original manifest, diagnostic
policy, schema-2, Newton, flux, compatibility and CSR gates. Both wrappers
share the same private finite reservation, held release, exit, resource,
cleanup and persistence sequence. The backend only allows Poiseuille/rotation
unit prefixes; its actual caps and manager behavior are unchanged. The
rotation controller recomputes every raw target/zero/pair decision, verifies
exact geometry, receipts, binding and versions, and refuses altered cached
flags. No rotation report is routed through Poiseuille's validator.

The source still relies on the frozen R249 conditional zero-form rule. Reading
DOLFINx source had shown that its scalar `ZeroBaseForm` path may lack an
argument-space mesh; no real UFL/FFCx path was exercised here. The driver
refuses that form and never substitutes a zero. Rotation's D=0 cannot by
itself validate viscosity coefficients or production weak forms. This source
and fake tests establish neither numerical assembly success nor resource cost,
mesh/time convergence, tank behavior or physical control.

## Evidence and checks

The [R250 runner](evidence/r250/test_runner.py),
[transcript](evidence/r250/tests.txt) and [summary](evidence/r250/tests.json)
record **93 passing standard-library tests**: the R248 85 plus eight new
rotation integration tests. The import audit found no NumPy, DOLFINx, Basix,
UFL, FFCx, PETSc4py, MPI4py or SciPy modules. New fakes cover:

- exact proposal/admission/contract/executable binding and malformed/duplicate
  JSON; cross-fixture and no-admission refusal before reservation;
- measured n=2 geometry, both degrees and 76 form/assembly calls, including
  zero-valued results; bad domain, tags, rank, scalar type and JIT refusal;
- raw/cached/envelope/receipt/geometry/version tampering, actual byte cap and
  exclusive/partial persistence;
- held-before-import ordering, bad nonce/cgroup/thread refusal and saving a
  complete numerically rejected report;
- rotation dispatch, one-use reservation, partial start, bad held limits,
  nonzero/late worker, resource/PID events, unknown counters, cleanup, final
  save failure and late completion.

The [source/saved-data audit](evidence/r250/audit.py) and
[output](evidence/r250/audit.json) replay the actual saved R246 controller
report under its unchanged policy, verify 60 original old raw files, all five
retained reservations and absent recorded PIDs/cgroups, and confirm 29 older
source/test/pin files unchanged. The two intentional existing-source changes
are supervision and backend; five new source/test/manifest files make a
36-file inventory. Historical run evidence and Poiseuille manifest/policy,
worker/driver/source binding/loader remain unchanged. Checks also cover AST,
JSON, local links, append-only logs and whitespace.

No real UFL/JIT/assembly, managed backend connection, package install/artifact
rescan, full numerical suite/tank/B2, rendering/physical task or Mac transfer
occurred. The R229 setup resource predicate remains false. The prior 180-second
and 1536-MiB budget is a later admission proposal, not a measurement of this
unrun workload. Final save tails and matrix rank remain unmeasured.

## Next task

**GPT-6 Astra / high reviews this integration and decides separate admission
or a precise blocker, then stops before launch.** Verify the exact 36-file
inventory, saved-test/audit evidence, fixed contract and admission/caller
requirements from [R249](ROTATION_INTEGRATION_REVIEW_R249.md). Confirm the new
manifest/envelope/source/artifact binding and zero-form refusal rule against
reviewed source. If acceptable, publish a narrowly bound fresh one-use
rotation admission and finite caller for a later Continue; do not consume it
in the admission review. Recheck the installed DOLFINx `forms.py` and runtime
artifact hashes, independent expiry/cgroup and live host capacity at launch.
If real API feasibility or containment requires changing a scientific gate,
report the precise blocker instead of relaxing it. All five historical
allowances stay spent; R250 created no rotation attempt directory.

The [official Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra)
was searched and opened for high support; task fit is judgment. No model or
session switch occurred here. PC retains ownership and Mac remains released.
Next prompt: **Continue**.
