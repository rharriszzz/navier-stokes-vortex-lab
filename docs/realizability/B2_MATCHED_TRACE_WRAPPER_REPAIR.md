# R015 toy-only matched-trace wrapper repair

The separately scoped [R016 attempt](B2_MATCHED_TRACE_LIFTING_RESULT.md) has
since reached P's solve/correction/output checks, then stopped on a block RHS
lifting error. No A solve ran. The next-task section below records the R015
handoff; the current task is R016's toy-only lifting repair.

Completed 2026-09-20 under the R014 handoff contract. This repairs and checks a
disposable copy of the failed R014 wrapper. No physical cylinder, factorization,
PDE solve, or matched-trace retry was run. The physical B2 gate remains failed
and `campaign_ready=false`.

## Repair

The three direct comparisons between C++ boundary-space objects and Python
function-space wrappers are removed. The runner now obtains block spaces from
the assembled forms and uses `fem.bcs_by_block` to collect each constraint
group. Before the original solve helper is called, it checks the group count,
offsets, uniqueness and disjointness of global DOFs, empty pressure groups, and
equality with exterior velocity DOFs located independently on the mesh. The
same groups supply the global essential set, RHS lifting and assignment, and
the real/imaginary essential residual checks.

Returned primary solves now checkpoint the matrix-solve count and PETSc factor
counters immediately after return. P and matched-trace compatibility paths
checkpoint both pressure-constant products, RHS norm, removed norm and the
unchanged tolerance before a possible refusal. The P boundary-constraint and
each primary compatibility check have explicit stages.

The exact disposable runner is [physical.py](evidence/r015/physical.py); the
focused fixture is [wrapper_toys.py](evidence/r015/wrapper_toys.py). No
production source, numerical form, solver, threshold, or guard changed.

## Toy result

One reference tetrahedron used distinct real and imaginary BDM2/DG1 spaces.
Each velocity block had 24 exterior DOFs and six free cell-interior DOFs; both
pressure blocks had zero constrained DOFs. The fixture checked block offsets,
disjoint sets, exact assignment for zero and nonzero complex targets, and
unchanged constraint sets. Missing and wrong-space groups were refused.
Synthetic incompatible-RHS and post-return bookkeeping failures both left
finite partial JSON containing the pre-removal diagnostics and returned solve
and factor counts.

The eight parent-monitored toy attempts used 3.7696 seconds total. Maximum
observed child-tree RSS was 180.5742 MiB and the maximum sample gap was
0.056968 seconds, below the shared 60-second/512-MiB budget. The final run
passed; recorded earlier fixture/API discovery failures are retained alongside
it. All 19 pinned production source/config identities matched. The preserved
R014 archive audit passed for all 27 artifacts.

The [R015 evidence archive](evidence/r015/) contains the exact repaired code,
all attempt reports, the finite final report, source identities, and a
standard-library audit. Its [validation record](evidence/r015/validation.json)
confirms no physical mesh, PDE solve, or factorization occurred.

The staged whitespace check reports one trailing blank line at EOF in the
unchanged, byte-preserved R014 support file `evidence/r015/toy_runner.py`
(line 213). It is retained to preserve the exact imported code; all other
staged files pass `git diff --cached --check`.

## Next task and stopping point

Recommend **GPT-6 Astra, high reasoning** to review this disposable repair and,
in a separately continued task, conduct the single R013 matched-trace attempt
under the original contract in
[B2_MATCHED_TRACE_REVIEW.md](B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract).
Before any physical work, validate the archived runner's scope, grouping and
checkpoint behavior against this toy result. Preserve all original source and
mesh identities, scientific assumptions, thresholds, and resource caps. Stop
on any inconsistency, prerequisite failure, resource limit, PDE/compatibility
failure, or completion. Do not retry, enlarge caps, add a mesh, or reinterpret
the physical gate. The unreached A compatibility path and physical outputs
remain unvalidated merely by this repair.

The official OpenAI model page currently lists GPT-6 Astra and `high` as a
supported reasoning effort; account access can differ. This is a recommendation,
not a model switch or launch. [OpenAI Docs: GPT-6 Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
