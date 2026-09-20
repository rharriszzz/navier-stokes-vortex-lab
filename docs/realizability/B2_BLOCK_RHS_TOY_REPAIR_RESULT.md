# R017 block RHS lifting repair: toy result

The subsequent [R018 review and prerequisite attempt](B2_MATCHED_TRACE_PREFLIGHT_RESULT.md)
stopped before physical execution on a toy repository-root path assumption.
The result below is preserved; its next-task section is historical. R019
completed portability repair, and the [R020 attempt](B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md)
then reached A_32 lifting and stopped at pressure compatibility. The completed
[R021 review](B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md) specifies the revised
q=64/q=96 comparison and compatibility barrier before any primary solve.

Recorded 2026-09-20 for [R017](../../REQUEST_LOG.md#r017--2026-09-20--short-continuation-request).
The scope was the toy-only block-vector repair specified by the
[R016 contract](B2_MATCHED_TRACE_LIFTING_RESULT.md#next-bounded-task-exercise-and-repair-block-rhs-lifting-on-toys).
The [evidence index](B2_BLOCK_RHS_TOY_REPAIR_EVIDENCE.md) links the exact
disposable source, every finite attempt report and the stored-data audit.

## Outcome

**The block RHS repair contract passed on toys.** A reference tetrahedron with
distinct real/imaginary BDM2/DG1 spaces reproduced the R016 failure mechanism:
PETSc `copy()` and `duplicate()` kept the vector sizes, ownership range and
array length but lost DOLFINx's `_blocks` metadata. A replacement created with
`dolfinx.fem.petsc.create_vector(spaces, kind=reference.getType())` retained the
required block layout. The helper records and validates PETSc type, local and
global sizes, ownership range, owned offsets, ghost offsets and array size
before loading or lifting.

For this serial toy, the block sizes were `[30, 4, 30, 4]`, with owned offsets
`[0, 30, 34, 64, 68]` and ghost offsets `[68, 68, 68, 68, 68]`. The 68 by 68
unconstrained operator included nonzero velocity-pressure and real-imaginary
coupling blocks. Its PETSc state stayed at 19 through RHS construction. The
actual helper performed manual block loading, blocked `apply_lifting`, reverse
ghost scatter and grouped boundary assignment.

With zero boundary targets, all unconstrained entries remained exactly equal
to the loaded RHS. For targets `[0.125, -0.375]`, the maximum difference from
independent dense operator arithmetic was `1.7763568394e-15`, below the
`2.1996161616e-11` absolute-contribution tolerance. Constrained entries matched
exactly, and pressure-row lifting had norm `1.6593400361`. The required
velocity real/imaginary and pressure/velocity toy coupling block norms were
all nonzero. The dense oracle was used only on this toy operator.

Wrong offsets and missing `_blocks` metadata were refused at the
`rhs_layout_validation` stage, before lifting, with layout and zero solve-count
records. A synthetic lifting error was recorded at `rhs_lifting`. Compatible
and incompatible pressure fixtures passed their respective accept/refuse
checks; no pressure products were removed. The R015 grouping, exact assignment,
wrong-space, incompatible-pressure and returned-solve reporting fixtures also
passed.

The parent-monitored cumulative toy work, including all seven recorded
attempts and failed attempts, took **8.5013 seconds**. The largest observed
child-tree peak was **183.2071 MiB**, below the unchanged 60 second/512 MiB
limits. The final attempt completed in 0.7592 seconds after the prior
7.7421-second cumulative checkpoint. All production source identities matched
the pinned 19-file set. The stored-data audit separately passed for the
original R016 archive; R017 carries only the three unchanged support sources
it needs alongside its repaired runner, so the historical payload is not
duplicated.

## Limits and next task

This confirms the vector metadata loss and repairs the wrapper operation on one
toy mesh. It does not test the physical cylinder, either A pressure
compatibility condition, a physical solve, matched-trace response accuracy,
boundary sensitivity or continuum geometry error. No production numerical
source or configuration changed. The B2 physical gate remains failed and
`campaign_ready=false`.

The next bounded task is for **GPT-6 Astra, high reasoning**: review the
repaired disposable runner's remaining A path against the original R013
contract, including source identities, preserved P results, constraints,
pressure compatibility, solve/factor counts, output checks and resource stops.
If all recorded prerequisites and unchanged caps still hold and no scientific
choice is needed, conduct at most one separate R013 physical attempt under its
original 180 second/1.5 GiB limits. Otherwise stop before physical execution
and record the specific unresolved decision. Do not retry, enlarge limits,
alter tolerances, integrate a gate, start a campaign, run B3, render or encode a
movie. Stop on a resource limit, unexplained inconsistency or research decision.

Retain GPT-5.6 Luna, medium reasoning, for another fully understood mechanical
repair. Recommend Astra/high whenever interpretation, acceptance thresholds,
method selection or physical claims are involved. This availability
recommendation was rechecked against the session model catalog and official
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages using
OpenAI Docs. No model switch or future session was launched.

**Next prompt: Continue.**
