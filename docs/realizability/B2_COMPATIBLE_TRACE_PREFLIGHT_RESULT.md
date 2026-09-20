# R022 compatible-trace prerequisites: memory stop before observer tests

Recorded 2026-09-20 for
[R022](../../REQUEST_LOG.md#r022--2026-09-20--continue-with-overall-progress-in-statusmd),
starting from `eebc69d`, under the
[R021 experiment contract](B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md#one-subsequent-experiment-contract).
The [evidence index](B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md) links exact
sources, both attempts, resource records and the saved-data audit.

## Outcome and stop

**No physical child ran.** All five original prerequisite phases and the
wrong-root/parent refusals passed. The new high-order polynomial checks also
completed: two complex polynomial traces, four faces each, at q=64 and q=96.
The advanced child then exceeded the **512 MiB active child-tree RSS cap**, at
**513.60546875 MiB**, and the parent killed it. No actual pre-solve observer
case was reached. The disposable implementation is not validated for physical
execution; its physical P/A comparison remains incomplete.

Two toy attempts consumed **16.405468375 seconds cumulative**, below the 60 s
wall limit. The memory limit, not the remaining wall allowance, required the
stop. No numerical retry, cap increase, physical mesh, factorization or PDE
solve followed. The physical B2 gate remains failed and `campaign_ready=false`.

## Implementation and completed coverage

The new disposable `physical.py` and `presolve.py` implement the fixed 64/96
pair without changing production code or the local projection/load kernel.
The observer targets the source-pinned direct helper's unique first
`nullspace.remove(vector)` line. Its intended sequence checks block layout,
constraint sets, pressure-vector normalization and both right and left
nullspaces, checks raw P, builds both A candidates through the repaired full
lifting helper, and retains accepted A vectors before permitting KSP setup.
Matrix digest/state and separate assembly/attempt/return/factor counters are
recorded. These observer operations are **implemented but not exercised by
R022**, since the resource stop occurred before their toy cases.

The compatibility helper now measures removal on a copy, records raw and
proposed hashes, and refuses without modifying the input vector. Only accepted
A candidates receive the existing arithmetic-sized removal; P's helper keeps
its own removal. The existing wrapper's simple compatible/incompatible pressure
fixtures passed after a JSON conversion repair. Those small fixtures do not
substitute for testing the complete reordered harmonic path.

The virtual transpose in the observer follows the
[PETSc transpose interface](https://petsc.org/release/petsc4py/reference/petsc4py.PETSc.Mat.html#petsc4py.PETSc.Mat.createTranspose);
the complete blocked lifting path retains the installed
[DOLFINx implementation](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/_modules/dolfinx/fem/petsc.html#apply_lifting).
These API references support the implementation choice, not an executed test
of the new observer.

The five unchanged R020 support sources are `toy_runner.py`, `kernels.py`,
`disk.py`, `wrapper_toys.py` and `block_rhs_toys.py`. Fresh checks retained the
24 tetrahedron permutations and spanning P2 vector traces, disk/arc/jump/
tangency fixtures, BC grouping and refusal fixtures, metadata-loss and full
block-lifting oracle, and synthetic wall/two-process RSS watchdog stops.
The parent-refusal test used the actual parent function with a synthetic failed
prerequisite report and confirmed zero counts with no physical launch record.

The new polynomial tests use a nondegenerate skew tetrahedron, a complex
divergence-free affine rotation with nonzero normal data, and a complex
quadratic P2 vector trace. At both orders, normal projection agrees with
independent DOLFINx interpolation, weak loads agree with independent low-order
polynomial integration, and the sum agrees with UFL assembly. All comparisons
use the prescribed `256*eps` absolute-contribution scales.

| Completed high-order check | Saved result |
|---|---:|
| Trace/order cases | 4 |
| Facet projection and weak-load checks | 16 |
| Maximum projection error / tolerance | 0.0097195850 |
| Maximum weak-load error / tolerance | 0.0069660330 |
| Maximum UFL assembly error / tolerance | 0.0073547438 |
| Maximum target callback size | 256 points |

These are polynomial checks only. No physical 128-term trace was evaluated;
no physical flux or assembled A compatibility was measured.

## Attempts and resource evidence

The first attempt passed root refusal, watchdog and kernel phases, then failed
in the wrapper's compatible-pressure reporting fixture. The new comparison
produced a NumPy Boolean, which the standard JSON encoder refused. The exact
error is `TypeError: Object of type bool is not JSON serializable`. Converting
only `accepted` to built-in `bool` fixed this understood reporting defect.
The initial sources/reports are preserved; its **5.239195592 s** counts against
the shared budget. The second parent explicitly deducted that time from 60 s.

The second attempt took **11.166272783 s**, including **5.316470743 s** in the
advanced child. That child returned `-9` after the RSS stop; its largest
observed process tree contained four processes. The maximum sample gap across
both attempts was **0.058599793 s**, at nominal 0.05 s sampling. Sampling is
not an instantaneous memory bound.

The last finite advanced checkpoint is `high_order_polynomial`, at child
elapsed **3.293822137 s**, with **180.66015625 MiB** recorded process high-water
RSS. It contains all four completed high-order cases and an empty
`observer_cases` list. This is a last checkpoint, not the failed operation or
the final process high-water measurement; SIGKILL prevented a final child
report. Parent and child memory figures cover different scopes/times.

After that checkpoint, source execution constructs the reference tetrahedron,
harmonic forms and unconstrained UFL lifting oracle before appending an
observer case. A read-only cache metadata record includes a newly generated
1,372,986-byte C file without a recorded completed module in that snapshot.
Together with the four-process tree, this makes compiler memory a plausible
contributor. The exact operation and per-process memory attribution are
**unresolved**: the watchdog did not save individual process RSS or another
stage checkpoint there. It would be incorrect to label the event a failed
compatibility check or to claim that high-order polynomial arithmetic failed.

## Scientific limits and validation

All 19 production/configuration pins and 440 R014–R021 evidence files were
verified against the starting commit. R021's saved-data auditor passed with
its write redirected into R022. The archive maps 86 exact execution artifacts
to 79 files, sharing seven identical initial support files instead of copying
them twice. No old evidence changed. The new saved-data audit checks identities,
source syntax, finite JSON, resource arithmetic, completed polynomial screens,
absence of observer/physical results, and documentation links.

R020 remains the latest physical attempt; R012 remains the last complete
physical response audit. P's reference-accuracy failure is unchanged. A_64 and
A_96 physical compatibility, paired gains, load sensitivity, geometry allocation
and a total FEM error floor remain unknown. Stability certificates have not
been integrated into schema-3 gate reports. Preparation, sensing, actuator
force/power and pressure demand, hardware feasibility and a validated movie
trajectory remain unassessed or unresolved.

Skipped after the stop: observer acceptance and three injected refusal cases,
all physical work, physical output/PDE checks and interpretation. Full
application, dense/calibration/refinement suites, production changes, gate
integration, campaign, B3, rendering and encoding were outside scope. No
physical solution coefficients or time-dependent dataset were produced.

## Next bounded task: isolate toy processes and finish observer coverage

Recommend **GPT-5.6 Luna, medium reasoning** for this mechanical fixture and
reporting task. It changes process lifetime and observability of resource use,
preserving the numerical method. A lower peak is a hypothesis to test, not a
promised pass.

1. Preserve R022 and all older evidence and the 19 pins. In a new disposable
   copy, split the existing high-order polynomial checks and harmonic observer
   checks into separate, sequential child processes. Let process exit release
   the high-order fixtures before harmonic-form construction. Preserve the
   exact traces, q=64/q=96 orders, forms, full lifting oracle and thresholds;
   do not simplify the oracle, change compiler options or reduce test coverage.
2. Add finite checkpoints before and after reference-tetrahedron construction,
   form compilation, unconstrained oracle assembly, and each actual observer
   case. Extend parent resource reporting with per-process RSS and executable
   names at the peak/stop, without saving full environments. Record final
   child-tree totals separately from last child high-water checkpoints.
3. Run the five original phases, root and parent refusals, the two separated
   new phases and watchdog tests under one cumulative **60 s/512 MiB** toy
   budget, including imports, all compilation and any failed attempts. Use the
   approved serial MPI environment and single-thread libraries. Record cache
   reuse; do not prewarm compilation outside the budget, edit a global cache to
   hide this failure, or retry after a resource cap.
4. Require all 16 high-order facet checks and the actual pinned harmonic
   observer's compatible P/A/A sentinel and incompatible P/first-A/second-A
   cases. Check the independent full block oracle, pressure support and
   normalization, matrix/layout invariants, once-only observation, unchanged
   refused raw vectors and zero factor/solve events. Keep missing-metadata,
   wrong-offset and synthetic lifting-error coverage.
5. Completion is a full audited prerequisite pass or a finite refusal at the
   first cap, unexplained numerical result or scientific decision. Archive
   exact sources and every attempt, update `STATUS.md`, request history and
   handoff, commit/push under Continue, and **stop before physical execution**.
   No changed method, tolerance, trace, cap, new physical mesh, gate, campaign,
   B3, rendering or encoding is included.

If this passes, recommend **GPT-6 Astra/high** to review the now-exercised
observer and remaining physical path before a separately scoped conditional
R021 experiment. If it still exceeds the cap or reveals a numerical/method
choice, recommend Astra/high for one bounded diagnosis using the improved
evidence; do not choose another method or resource limit automatically. Retain
Luna/medium only for another fully understood mechanical defect.

Both models are available in the current session catalog. OpenAI Docs was used
to fetch supported effort levels for
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
No model switch, sub-agent or automation was launched. **Next prompt: Continue.**
