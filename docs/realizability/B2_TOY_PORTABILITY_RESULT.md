# R019 toy portability repair: prerequisite checks pass

Recorded 2026-09-20 for [R019](../../REQUEST_LOG.md#r019--2026-09-20--short-continuation-request),
under the unchanged [R013 experiment contract](B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract)
and the [R018 repair contract](B2_MATCHED_TRACE_PREFLIGHT_RESULT.md#next-bounded-task-make-toy-prerequisites-portable).
The [evidence index](B2_TOY_PORTABILITY_EVIDENCE.md) links the disposable source,
all recorded launches, parent refusal probe and audit.

## Outcome

**The toy portability and early-refusal contract passed.** In a shallow
temporary directory, the wrapper toy now takes the repository root from its
working directory, verifies all 19 pinned production identities, and only then
imports DOLFINx/MPI and constructs its reference tetrahedron. An intentional
wrong-root invocation wrote a finite JSON failure at stage `imports`, with
zero meshes, PDE solves, factorizations, primary/correction RHSs and matrix
solves. This also avoids initializing MPI for an invalid working directory.

The parent now checks the toy prerequisite report and records an explicit
`prerequisite_refused` report before any physical launch. A separate synthetic
parent probe confirmed all counts are zero, `child_launched=false`, and no
launch record exists. This probe did not launch a physical child.

The complete parent-monitored prerequisite run passed the wrong-root probe,
synthetic watchdog, kernel fixtures, wrapper fixtures, full block-RHS oracle
and extra disk checks in **5.3787 seconds**, with **140.5117 MiB** maximum
observed child-tree RSS and a **0.056605-second** maximum sample gap. All five
prescribed prerequisite phases returned success. The watchdog wall and
two-process memory stops passed; the kernel phase retained all 24 vertex
permutations and its spanning load/disk checks. Production numerical sources,
fixtures and tolerances were not changed.

Four earlier disposable launch attempts are preserved. One exposed an output
directory collision in the harness; two sandbox runs failed at MPI/UCX startup;
another reached the kernel phase and hit the same sandbox MPI startup problem.
The harness now lets the child create its output directory, and the invalid-root
check runs before DOLFINx/MPI imports. The final complete sequence ran in the
approved MPI environment. Including all four failed attempts, parent-monitored
elapsed time was **6.4805 seconds**; the largest observed RSS across recorded
attempts remained **140.5117 MiB**, below the 60 s/512 MiB limits.

No physical mesh, PDE solve, factorization or matrix solve ran. The paired
physical diagnostic remains incomplete; the B2 gate remains failed and
`campaign_ready=false`. No changed scientific assumption follows from these
toy checks.

## Next task

Recommend **GPT-6 Astra, high reasoning** to review the R013 physical runner and
all prerequisites against the unchanged research contract. If that review
finds no unresolved scientific or numerical decision and all prerequisites
still hold, conduct at most one separate physical attempt with the original
180 s/1.5 GiB caps. Stop on the first failure, cap or unexplained result. Do not
retry, change the trace, tolerances, solver, gate, campaign or B3 scope. If the
review identifies a method, interpretation or acceptance issue, stop before
launch and record the decision. Retain Luna/medium for a later understood
mechanical repair only.

No production source, historical evidence or old artifact was edited. The
physical gate remains failed. See [validation.json](evidence/r019/validation.json)
for source identity, finite-data, resource and archive checks.
