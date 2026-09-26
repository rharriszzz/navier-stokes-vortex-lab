# R232 — Single n=2 Poiseuille attempt stopped in PETSc LU

**The one admitted numerical allocation is spent and incomplete.** R232
corrected R231's pre-reservation import error, published a clean caller at
`980ef7fb85941d31fab7951be4a1a7105846e840`, then launched exactly once in
the fixed `/tmp/navier-poiseuille-r230-once` directory. The worker reached its
held state, verified clean source/interpreter binding and effective cgroup
limits, was released, and exited 1 during the first sparse LU solve. No second
fixture command or alternate directory was used. The full manufactured suite,
rotation, tank/B2 and physical/render workloads remain unadmitted.

The [raw directory](evidence/r232/run/) contains the byte-exact reservation,
admission, held/release messages, worker/run logs, controller result/completion
and outer caller records. [Hashes](evidence/r232/run_hashes.json) verify all ten
copied files against the retained `/tmp` originals. The [R232 caller review](POISEUILLE_CALLER_REVIEW_R232.md)
records the corrected import and prelaunch checks. The R231 failure remains
separate historical evidence.

| Boundary | Observed result |
|---|---|
| Binding | Source commit `980ef7f...`, clean checkout, `/tmp/navier-fenicsx-r229/bin/python` resolving to the binary with SHA-256 `5f083df3...75c27a3`; manifest SHA-256 `7a8bda9...f52fa558`. All 25 reviewed file hashes matched inside caller preflight. |
| Held scope | One worker, one MPI rank/thread, effective memory.max 1,610,612,736 bytes (1536 MiB), swap.max 0, pids.max 32, independent expiry 150 s. Setup before release 0.188602503 s. |
| Worker failure | PETSc error code 73 at `MatLUFactorSymbolic_SeqAIJ` / LU setup: **“Matrix is missing diagonal entries.”** The worker exited 1. The exact missing row and underlying assembly cause are not saved. |
| Controller | `INCOMPLETE`; `run.log` says worker failed before completion. The final `result.json` reason is “missing, exceeded or unknown cleanup/resource evidence” because the failed worker left no pre-exit resource snapshot. This does not supersede the worker log's LU error. |
| Cleanup | Manager final state failed/exit-code, ExecMainStatus 1, MainPID 0, empty ControlGroup; `cleanup.empty=true`, `unknown_children=false`. A later read-only check found worker PID 144212 and its cgroup path absent. |
| Time | 5.998947526 s through controller result/log save; 6.051312914 s through outer caller save. Final caller-completion save/return tail remains unmeasured. Both saved statuses are `INCOMPLETE`. |
| Missing evidence | No `numerical.json`, `resource_snapshot.json` or finished handshake. Actual memory peak/max/OOM/PID events, mixed DOFs, rank/condition, linear residual, degree-24/26 diagnostics, error and physical budgets were not measured. No numerical or resource PASS is claimed. |

The failure occurred after reservation and worker release, so the R230 single
fixture allowance is consumed **1 of 1**. R229's setup resource predicate
remains false with 303 memory.max events; no prior result is reclassified.
The enforced kernel limits were observed before release, but absent completion
counters cannot show whether this particular worker touched a resource limit.
The PETSc log identifies the immediate failure during symbolic factorization;
it does not prove which assembled row lacks a structural diagonal entry or why.

Next: Astra/high performs a source-and-evidence review of the sparse border,
Dirichlet lifting and PETSc CSR construction around the first LU. Use the saved
failure and import-free algebra tests to identify a minimal correction or a
specific blocker. Stop before any numerical import, FEM/JIT/solve or new
allocation. A future run would need a separate explicit admission and cannot
reuse `/tmp/navier-poiseuille-r230-once` as a retry. The numerical fixture has
not established rank, accuracy, convergence or physical realizability.
