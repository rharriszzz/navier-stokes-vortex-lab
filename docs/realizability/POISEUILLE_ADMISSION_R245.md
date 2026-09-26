# R245 — One later fixture under the explicit R244 policy

2026-09-26, PC/WSL daisy. Base `4449b1a`, STARTED `4c6b9ae`.
**GO for one NEW later n=2 Poiseuille fixture, 0/1 spent.**
Exclusive directory: `/tmp/navier-poiseuille-r245-once` (absent at review).
All four older allocations remain spent 1/1 and their results unchanged.
Execution requires a later **Continue** and clean STARTED publication.
No reservation, worker, numerical import or live manager connection occurred.

## Admission decision

[R243](POISEUILLE_QUADRATURE_REVIEW_R243.md) justified a prospective accuracy
budget; [R244](POISEUILLE_POLICY_IMPLEMENTATION_R244.md) implemented it with
explicit fixture/policy binding, strict raw inventory and physical validation
at both degrees. Source review confirms worker and controller recomputation,
unchanged squared-error gates, unchanged degree-24 backflow sampling, and
refusal of missing policy/schema. Nine focused policy/driver tests pass here;
all 29 source/pin hashes match R244, so its 77-test full result is reused.
No new runtime change is needed for this admission.

The separate attempt tests the complete worker/report/resource path under that
new contract. An explicitly constructed saved-data replay is insufficient to
accept a run: R242's original contract still refused, and remains INCOMPLETE.
The 1e-14 signed target is an accuracy budget, not proof that its earlier
failure was solely rounding. No threshold is changed in R245 or after a future
refusal. A single successful oracle would not establish convergence, mixed
operator stability, a tank model or physical realizability.

## Exact bindings

[Allocation](evidence/r245/allocation.json), [caller](evidence/r245/run_once.py),
[checks/source inventory](evidence/r245/checks.json) and
[artifact inventory](evidence/r245/artifacts.json) bind:

| Input | Binding |
|---|---|
| Source | Actual full clean launch HEAD; 29 code/test/pin hashes |
| Manifest SHA256 | `061962ccc9fc26aa71c5c77d232e28591a0807e63b942e13e7255330245da0ca` |
| Policy SHA256 | `cdfaceeffc892f8b2243131e5fd3eded02cdb5a6d2d4f9e85972a04461b2e8f5` |
| Numerical contract | schema 2; `poiseuille_signed_accuracy_v1`, policy schema 1 |
| Caller SHA256 | `5003f99cd79abac979ef26496638563ee8518f4b2d2f69dcdaa6c4288ab9e873` |
| Interpreter | `/tmp/navier-fenicsx-r229/bin/python` |
| Interpreter SHA256 | `5f083df36ec986d5cd13d2549ca6cfe1ddaf658509f9e419b454b2fb375c27a3` |

Policy digest uses `json.dumps(policy, sort_keys=True, allow_nan=False).encode()`.
The new caller derives from R241, with new fixed directory/source inventory,
manifest and explicit policy digest. It refreshes capacity/manager facts before
reservation, under its existing 180-second timer. Imports remain standard
library/project source until the supervised worker is released.

Seven runtime file hashes, four library resolutions and the cached SuperLU
archive still match R241. **Accept the same exact packaged artifact for this
new bounded attempt**, retaining package 7.0.1 versus embedded 7.0.0 labels and
ordinary package/OS trust. No tag-equivalence claim, relabel, installation or
broad rescan. R242's three verified corrections support prior capability on
this host, not guaranteed future correctness or loaded-file identity.
R229's setup resource predicate remains false.

## Frozen work and acceptance

- One n=2 Poiseuille BE step, dt=0.125, exact history/lateral trace and non-exact
  free-velocity initial guess requiring a verified correction.
- Serial PREONLY/LU/SuperLU, R240's explicit controls, no shift, replacement,
  fallback or additional solve. Newton, true residual, compatibility/Gram,
  gauge/eta/both fluxes, exact errors and physical budgets stay fixed.
- R244 comparison: 17 signed keys use max(old limit,1e-14); other 13 retain
  old limits. Both degrees must pass physical checks; backflow samples are
  degree 24 only. Missing, nonfinite, inconsistent or false evidence refuses.
- 180 s total, 15/150/15 setup/work/finish, 149 s independent runtime plus
  1 s stop grace. 1536 MiB, no swap, 32 tasks, one rank/thread. Zero memory.max,
  OOM, OOM-kill and PID-limit events, finite saved peak, actual exit and empty
  cleanup remain necessary. Preserve pre-exit and final-save measurement gaps.
- Latest-system evidence unchanged: at most 512 global unknowns, 65,536 stored
  CSR entries, 4 MiB per record, 12 corrections; capture actual lifted/scaled
  system before solve. Retain complete/partial records and digest receipts.
  Numerical report cap remains 2,000,000 bytes.

## Checks and attempt boundary

[Caller checks](evidence/r245/check_caller.py) exercise outside-directory import,
timer before imports/preflight, dirty/wrong commit, changed source/policy/
interpreter/artifact/library resolution, existing directory and dangling-link
refusals. All stop before a manager connection or reservation. Focused tests
and import audit are in [tests.json](evidence/r245/tests.json) and
[tests.txt](evidence/r245/tests.txt).

The [intentional invalid-commit CLI test](evidence/r245/invalid_commit_check.json)
used the pinned interpreter from `/tmp`, returned 1 before manager/reservation,
and left the directory absent. Caller interval 0.042153463 s, parent interval
0.089880544 s. It is not a numerical attempt. Forty-five old raw files match
retained originals; all four reservations persist and recorded PIDs/cgroups
are absent. Historical sources/callers/evidence are unchanged.

Directory/reservation creation or partial worker start spends the new allowance,
even on INCOMPLETE. Save every raw result/log/matrix/partial file, record actual
exit/elapsed/cleanup and spent 1/1, publish and stop. No retry, alternate directory,
extra analysis/solve or gate adjustment in the execution step.

Only a demonstrated caller/preflight error before reservation, worker and
numerical import is recoverable in the same unspent contract: preserve its
command/failure/timing gaps, verify absent fixed directory and no new manager
task, fix/test the cause, publish a clean binding, then continue. Uncertain
process state stops for review; never reset a charge by inference.

## Next task

**Sol/high** executes the exact caller once after the next Continue, using that
turn's actual clean published launch HEAD, preserves all raw evidence and
cleanup/spent state, publishes and stops. Astra/high then interprets the result
or any method/admission change. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched/opened for high support; task fit is judgment. No model/session
switch or /new required. Follow the [single next task](../../SESSION_HANDOFF.md#next-task).

Skipped: FEM/JIT/assembly/solve, live manager/scope, rank/alternative factors,
install/full rescan, full suite/rotation/tank/B2, physical/render and Mac transfer.
Actual future resource events/accuracy and target attainability are unmeasured.
PC retains ownership; Mac remains released.
