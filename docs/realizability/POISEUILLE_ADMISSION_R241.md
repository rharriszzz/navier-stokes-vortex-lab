# R241 — Bounded matrix evidence and one later SuperLU fixture

2026-09-26, PC/WSL daisy. Base `14a402a`, STARTED `afcd53f`.
**GO for one NEW later n=2 Poiseuille fixture, 0/1 spent.** Exclusive directory:
`/tmp/navier-poiseuille-r241-once`. This review creates no reservation or worker.
The three older allocations R232/R235/R238 remain INCOMPLETE and spent 1/1.
Execution requires a later **Continue** and normal clean start publication.

## Why this bounded attempt is justified

[R239](POISEUILLE_PIVOT_REVIEW_R239.md) showed that a full-rank gauged toy can
fail without numerical pivoting. [R240](POISEUILLE_SUPERLU_REVIEW_R240.md)
implemented reviewed serial SuperLU controls with no operator regularization,
fallback or acceptance relaxation. The actual R238 matrix was never saved,
so its rank and suitability for a different factorization remain unknown.

This allocation tests the explicit pivoting backend on the same exact fixture
and preserves the actual system before factorization. It can yield either a
checked correction followed by the unchanged scientific gates, or a refusal
with a sparse system available for later analysis. Neither outcome is predicted.
No extra assembly, alternate solve or retry is authorized. An earlier import,
API, resource or evidence-write failure still spends the attempt and may leave
no matrix; preserve that result and stop.

## Exact artifact decision

**Accept the existing exact conda artifact for this one bounded fixture.**
[artifacts.json](evidence/r241/artifacts.json) records package
`superlu 7.0.1 h8f6e6c4_0`, archive SHA256
`4e748f877553c7ed42290420ba1e9aa0e80cf72b23b463f12dbb7927c16f0437`.
The retained `.conda` archive matches that digest. Installed header, CMake
metadata and shared library match the package's own file hashes, including
their **7.0.0** labels. They have not been silently upgraded or relabelled.

The mismatch's upstream cause remains unresolved. The accepted identity is
the exact packaged artifact, not a claim that it equals the current upstream
v7.0.1 tag or that a 7.0.0 version string independently satisfies a 7.0.1 pin.
R229 already verified this unchanged package/environment transaction; R240
reviewed the interface, options and pivot policy, and the new caller binds
the actual PETSc/SuperLU files and library-link resolutions. Under the existing
ordinary package/OS trust boundary this is sufficient to test capability once.
It does not demonstrate loaded-library identity, API compatibility, numerical
stability or accuracy. Any changed artifact refuses before reservation.
No install, alternate package, changed dependency pin or broad environment
rescan is needed or authorized. R229's setup memory-event predicate stays false.

## Latest-system evidence implementation

[linear_evidence.py](../../verification/nonlinear_port/linear_evidence.py)
uses standard-library JSON, file operations and hashing. The worker supplies
the required writer to the fixture driver. Immediately before every sparse
solve, the driver passes the same lifted/scaled CSR and RHS it will give to
SuperLU, together with the last evaluated Newton state, frozen scales, fixed
indices/values, step and attempted correction number. A writer exception stops
the driver before the solve. It performs no numerical import or assembly.

| Evidence requirement | Implementation |
|---|---|
| Dimension / storage caps | At most 512 global unknowns and 65,536 CSR entries |
| Output cap | At most 4 MiB serialized JSON, including final newline |
| Loop bound | Step 1 only, consecutive corrections 1–12 |
| Contents | CSR, RHS, state, fixed values/indices, row scales, shape, mixed count, dt, fixture, source/interpreter binding and backend settings |
| Publication | Exclusive `.writing` file, flush/fsync, atomic replace of `linear_system.json` |
| Failure | Preserve previous complete file and any partial `.writing`; no solve after failed save |
| Integrity | Flushed log receipt with filename, correction, bytes and SHA256 |
| Unavailable values | Factor permutation and pivot coordinate explicitly null |

The n=2 source produces 48 tetrahedra with 34 local P2/P1 unknowns. Even a
conservative count of 48 times 34 squared local entries plus three global
rows/columns is below 65,536 for the observed 405-dimensional system. The
caps leave room for sparse zero diagonals while refusing unexpected expansion;
the matrix has not been reassembled to check its actual nonzero count here.
These diagnostic caps tighten the existing 20,000 mixed-DOF ceiling for this
particular tiny case; they do not admit a larger mesh.

Only one complete latest record is retained. During replacement, old complete
and new temporary files can coexist, each bounded by 4 MiB. Complete input
arrays remain sparse. Time, copies, hashing and disk writes are inside the
same worker's existing limits. A killed/failed writer need not have a receipt;
re-hash retained complete bytes and label missing/partial data. Atomic rename
provides complete-file visibility, not a claim of crash-proof disk durability.
The last record may belong to an earlier completed correction when a later
save fails; use its correction number and log, never infer latest state.

## Frozen allocation and caller

[allocation.json](evidence/r241/allocation.json) binds the new charge, all
three old charges, [caller](evidence/r241/run_once.py), 27-file source/pin
inventory, interpreter, artifact inventory and unchanged numerical/resource
gates. The manifest remains non-executable by itself.

- One n=2 Poiseuille BE step, dt=0.125, exact history/lateral trace and a
  non-exact free-velocity guess requiring a checked correction.
- PREONLY/LU/serial SuperLU with R240's fixed settings: COLAMD, threshold 1,
  no shift, tiny-pivot replacement, extra equilibration/refinement or fallback.
- Actual clean launch HEAD bound in admission/reservation/held worker.
  All 27 source hashes and seven runtime artifact hashes must match; library
  resolutions must match. Artifact hashing streams through a bounded buffer.
- `/tmp/navier-fenicsx-r229/bin/python`, executable SHA256
  `5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3`.
- 180 s observed outer interval; 15 s setup / 150 s worker / 15 s finish;
  independent worker runtime 149 s plus 1 s stop grace.
- 1536 MiB, no swap, 32 tasks, one rank/thread. Zero memory.max, OOM, OOM-kill
  or PID-limit events, finite saved resource evidence, actual exit and empty
  cleanup are still required for a run PASS.
- Unchanged compatibility/Gram, true residual, Newton, eta/gauge/both fluxes,
  degree-24/26 comparison, return sampling, exact oracle and endpoint budgets.
  A saved matrix or successful LU alone accepts none of those conditions.

The caller checks source/artifacts/directory/capacity before reservation and
refreshes manager availability. No FEM import or prewarming is permitted
outside supervised release. Publish STARTED, obtain the exact full launch HEAD,
then invoke the prepared caller once with that commit. Keep checkout and
environment unchanged throughout. The source-only invalid-commit test in this
review exited before manager connection or reservation and spent no attempt.

## Consumption and stopping rules

Directory/reservation creation or partial worker start spends the new allowance,
including INCOMPLETE results and missing evidence. Retain the directory and
all raw files, including `linear_system.json`, any `.writing` and worker logs.
Preserve status, actual elapsed/exit/cleanup and gaps; publish spent 1/1, stop.
No second attempt, alternate directory, pivot adjustment or solver/gate change.

Only a demonstrated caller/preflight error before reservation, worker and
numerical import may be repaired within the same unspent contract. Preserve
its evidence, verify absent fixed directory and no new manager task, fix/test
the cause, publish a clean binding, then continue. Uncertain process state
requires review; no charge is reset by inference or by a missing directory.

## Checks and handoff

All **69 standard-library tests pass**, with no numerical modules loaded.
Four new serialization tests cover exact sparse round trip/latest replacement,
invalid values/indices/caps, preserved prior evidence on failed replacement,
and malformed CSR/nonfinite RHS. The real driver/Newton path with fake FEM
boundaries checks capture-before-solve and no solve after save failure.
These tests do not validate actual FEM or SuperLU behavior.

The new caller checks passed with synthetic Git answers for source/artifact
and existing/dangling-directory refusals, outside-directory import and timer
ordering. An unmocked invalid-commit CLI check using the pinned interpreter
exited 1 before manager/reservation (caller 0.026281637 s, parent 0.067080642 s).
Thirty old raw files match retained originals; reservations persist and saved
PIDs/cgroups are absent. Seventeen R229 evidence hashes, unchanged conda history
and interpreter digest were verified. No numerical work, manager connection,
live scope, installation, full suite/rotation/tank/B2, physical/render or Mac
work occurred. [Checks](evidence/r241/checks.json) preserve these bindings.

Next: **Sol/high** executes the prepared caller once after Continue, preserves
all evidence, publishes and stops. Astra/high interprets the result or changes
method/admission choices. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched/opened for high support; task fit is judgment, no account check
or model switch. No /new required. Follow the
[single next task](../../SESSION_HANDOFF.md#next-task).
