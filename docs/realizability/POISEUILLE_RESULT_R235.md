# R235 — Repaired-source n=2 Poiseuille attempt incomplete at sparse solve

**The new R234 allocation is spent 1/1 and INCOMPLETE.** R235 used the one
admitted `/tmp/navier-poiseuille-r234-once` directory exactly once, bound to
clean launch commit `f7ac56519a1bf4c99efae21ce8ba9510ed5113ea` and the
pinned interpreter. The worker reached the sparse linear solve and printed
`Refusal: sparse linear solve failed`, then exited 1. No second numerical
command, alternate directory, source repair or threshold change followed.
The older R232 allocation remains separately INCOMPLETE and spent 1/1.

The [raw evidence](evidence/r235/run/) contains ten byte-exact files copied
from the retained fixed `/tmp` directory. Their [hash ledger](evidence/r235/run_hashes.json)
verifies 5,537 copied bytes against the originals. The
[execution record](evidence/r235/execution.json) records the single command,
actual caller exit 1, saved status and later PID/cgroup absence. The R234
[admission contract](POISEUILLE_ADMISSION_R234.md) and R233
[source repair](POISEUILLE_SPARSE_REVIEW_R233.md) remain unchanged.

| Boundary | Observed result |
|---|---|
| Before reservation | Source HEAD `f7ac565...` was clean and equal to upstream. The prepared caller hash, all 25 R233 source hashes, frozen manifest and pinned interpreter hash matched. R234 directory was absent; the older R232 reservation remained present. One initial read-only prelaunch script stopped on an incorrectly guessed full commit string; its corrected check passed before any caller/manager/reservation. |
| Caller preflight | Manager `249.11-0ubuntu3.22`, host MemAvailable 6,505,060 KiB, clean source and matching executable SHA-256 `5f083df3...75c27a3`. This capacity observation is not a worker footprint. |
| Reservation and held scope | At `2026-09-26T17:06:03Z`, the exclusive directory was reserved with attempt 1. Held worker verified source/interpreter, one rank/thread, memory.max 1,610,612,736 bytes (1536 MiB), swap.max 0, pids.max 32 and 150 s independent expiry. Setup before release: 0.140517766 s. |
| Worker failure | `worker.log`: `Refusal: sparse linear solve failed`. Source reaches that refusal only after `ksp.solve` returns and `answer` is read, when the KSP convergence reason is nonpositive **or** an answer value is nonfinite. The log does not distinguish those branches; the reason code, answer and matrix were not saved. This is not evidence of a successful factorization or correction. |
| Controller and caller | Manager recorded actual worker exit 1. Controller and caller saved `INCOMPLETE`; caller process exited 1. Controller result/log save observed at 1.499145865 s; outer caller after-save observed at 1.584184013 s. Final caller-return/save tail remains unmeasured. |
| Cleanup | Manager final MainPID 0, empty ControlGroup; controller `cleanup.empty=true`, `unknown_children=false`. Later read-only checks found worker PID 147714 and its cgroup absent. |
| Missing data | No `numerical.json`, `finished.json` or `resource_snapshot.json`. Actual memory peak/max/OOM/PID events, matrix rank, KSP reason, correction, degree-24/26 diagnostics, accuracy and budgets remain unmeasured. The controller's generic final reason flags missing resource evidence; the worker log gives the immediate sparse-solve refusal. |

The saved error differs from R232's PETSc exception about missing diagonal
entries. The repaired CSR path reached the KSP post-solve status/answer check
without that exception, but the observations cannot establish why this solve
was refused. `sparse_solve` applies the existing preonly/LU method, checks the
KSP reason and answer finiteness, then would check the true residual. It did
not reach a saved correction or residual result. The one-use stop rule applies
because the directory was reserved and worker released. No repair-and-rerun is
admitted from this result.

The R229 environment setup result remains false because of its 303 memory.max
events. R235's effective held limits were observed, but its absent pre-exit
snapshot cannot establish whether this numerical worker touched a resource
limit. No numerical or resource PASS is claimed. Full convergence suite,
rotation, tank/B2, physical and rendering work remain unadmitted.

Next: **Astra/high reviews the saved KSP refusal and exact source path without
FEM or a new allocation.** It should identify the smallest diagnostic needed to
distinguish a nonpositive KSP reason from a nonfinite answer, and assess whether
source instrumentation can preserve that evidence on a later separately
reviewed run without changing the solver, operator or gates. Stop before
execution, installation or retry. See the single
[handoff task](../../SESSION_HANDOFF.md#next-task). PC/WSL daisy retains
ownership; Mac remains released.
