# R236 — Preserve the sparse-solve refusal diagnostic

**The R235 cause remains unmeasured. A minimal diagnostic is implemented and
passes 62 standard-library tests, without numerical imports or a new attempt.**
Both R232 and R235 remain INCOMPLETE and spent 1/1. No third allocation is
admitted. Follow the [single next task](../../SESSION_HANDOFF.md#next-task)
for a separate decision about one later diagnostic fixture.

## What the retained evidence establishes

The [R235 worker log](evidence/r235/run/worker.log) contains only
`Refusal: sparse linear solve failed`. Its clean source binding uses the R233
structural-diagonal repair. In that source, this message follows returned
`ksp.solve`, successful array extraction, and either a nonpositive convergence
reason or a nonfinite answer. The old `or` short circuit also means answer
finiteness was not evaluated if the reason was nonpositive. Neither quantity
was persisted. A successful return from the API is therefore insufficient to
establish successful numerical factorization. The failed correction never
reached the adapter's true-residual check or Newton's correction check.
The log does not identify which Newton correction failed; earlier successful
corrections, if any, existed only in memory.

The controller's generic reason refers to missing resource/cleanup evidence
required by its aggregate gate; saved cleanup itself is empty. No numerical,
finished or resource snapshot file exists. The saved worker exit is 1. No exact
KSP code, pivot, rank, accuracy or memory-event result can be reconstructed.
All 20 raw files across R232/R235 match their ledgers and retained originals.
Both reservations remain present, and both recorded worker PIDs and cgroups
are absent. No manager connection or new task process was needed for this review.

## PETSc and Newton interpretation

The configured method remains serial `preonly` / `lu` / `petsc`, with no
`setFromOptions`. PETSc's published 3.25.5
[PREONLY source](https://petsc.org/release/src/ksp/ksp/impls/preonly/preonly.c.html)
applies the PC once, reads its failure reason and sets the KSP status accordingly.
It can return with `KSP_DIVERGED_PC_FAILED`; success uses `KSP_CONVERGED_ITS`.
Its KSP iteration/tolerance settings do not control iterative convergence.
Thus increasing KSP iteration limits would not address this configured path.
This is a source interpretation, not an observed R235 status.

The [PC failure enum](https://petsc.org/release/manualpages/PC/PCFailedReason/)
distinguishes structural pivot (1), numeric pivot (2), factor memory (3), other
factor failure (4), and additional cases. A numeric pivot is plausible after
structural repair but unproven. Even that code would not alone establish matrix
singularity or identify a suitable solver change. The actual assembled matrix
and its rank/conditioning remain unavailable. A three-row constraint Gram check
is not a mixed-operator stability test. Do not infer a cap event from a PC memory
code or vice versa; cgroup evidence remains independently required.

The non-exact *nonlinear* initial guess belongs to Newton's state. It is not a
nonzero KSP correction guess. Each correction gets a fresh vector and KSP;
no nonzero linear guess is configured. Newton still checks the returned linear
defect before line search, enforces residual convergence and stops on a refusal.
The driver still freezes scales before Newton and cannot emit its numerical
report until the solve and all later diagnostics finish. No gauge, flux row,
lift, CSR coefficient, backend, tolerance or resource cap changed.

## Smallest useful diagnostic and its limits

[cube_adapter.py](../../verification/nonlinear_port/cube_adapter.py) now retains
the integer KSP reason and counts nonfinite answer entries. The same refusal
predicate includes these two values in its exception message. On that failure
path only, it also queries
[PC.getFailedReason](https://petsc.org/release/petsc4py/reference/petsc4py.PETSc.PC.html#petsc4py.PETSc.PC.getFailedReason).
If this optional query raises, the message records `unavailable:<exception type>`
and keeps the primary refusal. Codes are reported directly, without guessing
their interpretation at runtime. Answer values, a matrix dump and extra solves
are unnecessary to discriminate these branches.

The unchanged worker exception handler prints the exception type/message to
stderr with `flush=True`, exits 1, and the existing backend retains worker.log.
No new persistence path or acceptance record was added. As before, a solve/API
exception before the status check follows the ordinary worker exception path;
this diagnostic does not claim to instrument every failure. Abrupt termination
or a cleanup exception can still prevent this message reaching the log. It
cannot supply missing resource snapshots or make an incomplete run pass.

Three new test methods exercise the real adapter with scripted Python objects:
negative/zero reason with finite answer; positive reason with NaN; negative
reason with both infinities; unavailable optional PC query; successful answer;
true-residual rejection; and propagation of the original solve exception.
They check the fixed method/backend, single solve and reverse destruction of
KSP/vectors/matrix. These objects do not perform a factorization. Before the
change, the two diagnostic tests produced five assertion failures; the behavior
preservation test already passed. Afterwards all 62 tests across seven modules
passed in 0.566796244 s under project Python 3.12.14. The module audit found no
NumPy, PETSc, MPI, DOLFINx, Basix, UFL or FFCx imports.
[Retained test output and checks](evidence/r236/) distinguish scripted evidence
from an unexecuted PETSc diagnostic.

## Later decision

A later Astra/high review should decide whether this specific information gain
justifies one new bounded n=2 Poiseuille allocation on the instrumented source.
It must state that the solver is unchanged, so another refusal is expected to
be informative rather than evidence of a repair. If admitted, bind all reviewed
source hashes and the exact R229 interpreter to a future clean launch commit,
choose a new exclusive directory, preserve both spent charges and every gate,
and specify how the three diagnostic fields will be interpreted. Stop before
reservation, numerical imports or any live scope. Otherwise state the concrete
blocker. Do not rerun either historical caller or change its ledgers.

R229's 303-event setup refusal remains false. Full suite, rotation, tank/B2,
physical/render work and installation remain unadmitted. No actual numerical
rank, accuracy, return quadrature or worker resource footprint was measured here.
PC/WSL daisy retains ownership, Mac remains released.

[Official OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-astra)
was searched and opened for Astra/high support. Retaining that model for the
admission decision is task-fit judgment; no account check or agent-initiated
model/session switch occurred. No new chat is necessary for the connected review.
