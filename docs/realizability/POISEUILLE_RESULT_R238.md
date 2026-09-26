# R238 — Instrumented n=2 Poiseuille attempt incomplete at numeric LU pivot

**The R237 allocation is spent 1/1 and INCOMPLETE.** The held worker reached
PETSc's sparse solve and saved:

```text
Refusal: sparse linear solve failed: ksp_reason=-11; nonfinite_answer_entries=405; pc_failed_reason=2
```

The new information identifies a failed preconditioner with a reported
**numeric zero pivot**. It does not identify the pivot row, prove the assembled
mixed matrix is singular, establish a suitable solver change, or measure
numerical accuracy. The worker exited 1. No retry or alternate directory was
used after reservation. Both older R232 and R235 allocations remain separately
INCOMPLETE and spent 1/1.

The [ten raw files](evidence/r238/run/) are byte-exact copies of the retained
`/tmp/navier-poiseuille-r237-once` files (5,604 bytes), verified against the
[hash ledger](evidence/r238/run_hashes.json) and local originals. The
[execution record](evidence/r238/execution.json) and
[checks](evidence/r238/checks.json) preserve source/interpreter binding,
actual exit, diagnostic, missing reports and cleanup. The historical
[admission](POISEUILLE_ADMISSION_R237.md), frozen manifest and numerical/
resource gates remain unchanged.

## Boundary and result

An initial exact caller command at clean `6625a894b3fd57f797241acd3e7c68aaa0b8c86a`
exited 1 during the manager preflight with `sd-bus operation failed: errno 1`.
The sandbox also denied read-only `systemctl --user`; the fixed R237 directory
and reservation were absent, and no managed worker or numerical import began.
An approved host read-only manager check found only three earlier failed units
(R232, R235 and R226 host probe), each with MainPID 0/empty ControlGroup and
none targeting R237. The failure, exact command, caller-observed 0.049598098 s
and missing counters are saved in [prelaunch.json](evidence/r238/prelaunch.json).
It did not spend the allowance. That evidence was published at `cd3cc5e` to
restore a clean source binding. The unchanged caller then ran outside the
sandbox with that exact full commit. No solver, threshold or fixture change
was made between commands.

| Boundary | Observed result |
|---|---|
| Clean binding | Launch HEAD `cd3cc5e31fa7225d23310a4f06fa557e20e88947` matched upstream. All 25 R236 source hashes, R237 caller digest, frozen manifest and R229 interpreter digest matched. Old allocations remained spent; R237 directory was absent before launch. |
| Caller preflight | User manager version `249.11-0ubuntu3.22`; host MemAvailable 6,527,400 KiB. That host capacity is not a worker peak or resource PASS. |
| Reservation and held scope | `/tmp/navier-poiseuille-r237-once` reserved attempt 1 at `2026-09-26T17:33:29Z`, consuming R237. Held worker verified clean source/interpreter, 1536 MiB memory.max, swap.max 0, pids.max 32, one rank/thread, and 150 s independent expiry. Setup before release took 0.143022389 s. |
| Worker failure | `ksp.solve` returned and the instrumented status/answer check refused: reason -11, 405 nonfinite answer entries, PC reason 2. No correction or true residual was saved. |
| Controller and caller | Actual worker exit 1; both saved INCOMPLETE and caller process exited 1. Controller result/log save: 1.206304849 s after reservation; caller after-save: 1.264677333 s. Final return/save tails remain unmeasured. |
| Cleanup | Manager final MainPID 0/empty ControlGroup, controller `cleanup.empty=true`, `unknown_children=false`; read-only checks found worker PID 149905 and its cgroup absent. |
| Missing data | No `numerical.json`, `finished.json` or `resource_snapshot.json`. Matrix/pivot row, rank and conditioning, accuracy, quadrature, memory peak/events and final tails remain unmeasured. |

The observed `-11` corresponds to
[PETSc `KSP_DIVERGED_PC_FAILED`](https://petsc.org/release/manualpages/KSP/KSP_DIVERGED_PC_FAILED/)
for the pinned PETSc 3.25.5 release; `2` is
[`PC_FACTOR_NUMERIC_ZEROPIVOT`](https://petsc.org/release/manualpages/PC/PCFailedReason/).
Those are the library's reported status categories. The 405 nonfinite entries
are an observed consequence in the answer vector, not an independent proof of
why the factorization failed. R233's structural-zero diagonal correction
prevented the earlier missing-diagonal exception; this result isolates a
numeric factorization refusal in the current direct LU path. A small
three-constraint Gram check does not certify the entire bordered mixed matrix.
No observed KSP iteration count, numeric pivot location or matrix dump exists.

The controller's generic final reason, `missing, exceeded or unknown
cleanup/resource evidence`, reflects absent resource evidence after the worker
failed; it is not the immediate numerical cause. Actual resource events cannot
be inferred from the PC reason or the short elapsed time. R229's 303-event
environment setup refusal remains false. No numerical or resource PASS, full
suite/tank/B2 admission or physical feasibility claim follows from this run.

Next: **Astra/high reviews the numeric zero-pivot result and exact mixed
operator/source using only saved evidence and import-free analysis.** Identify
the smallest discriminating source/algebra check or a concrete blocker before
considering any new solver or allocation. Preserve all three spent charges,
old directories and gates. Do not launch FEM, change the solver/pivot tolerance,
or infer singularity from this code alone. Follow the
[single handoff task](../../SESSION_HANDOFF.md#next-task). PC/WSL daisy retains
ownership; Mac remains released.
