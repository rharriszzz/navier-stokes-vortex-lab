# R265 — Balanced symbolic source review and one-use admission

2026-09-26 (America/New_York), PC/WSL `daisy`. **Accept R264's source change
and admit one NEW later manufactured spatial BE pilot. Zero new attempts are
spent in this review.** R262 remains INCOMPLETE; all eight older allocations
remain spent. Follow the [single next task](../../SESSION_HANDOFF.md#next-task).

## Source decision

The [R264 integration](MANUFACTURED_BALANCED_INTEGRATION_R264.md) implements
the [R263 contract](MANUFACTURED_DEPTH_REVIEW_R263.md). Each monomial retains
its coefficient-to-float conversion, insertion order, coordinate order and
exponent operations. Iterative adjacent-pair sums retain an odd tail and give
logarithmic addition depth. Empty and singleton cases match the contract.
The five symbolic routes cover current/history velocity, force, pressure,
return targets, return pressures, traction offsets and continuous derivative.
Legacy numeric interpolation remains byte-for-byte unchanged. Automatic
Jacobian construction, corrected BE forcing/history, solver, diagnostics and
scientific/resource policies are unchanged. This review edits no runtime source.

The [118 source/fake tests](evidence/r265/tests.json) pass under Python 3.12.13
with numerical imports prohibited. They include all four fixture families,
28 monomial/depth comparisons, sign/odd-tail controls, both degree24/26
manufactured routes, corrected load/history and legacy interpolation.
R264's legacy AST pin and old-walk RecursionError assertions are specific to
the pinned interpreter; they do not define a portable runtime acceptance gate.
The extracted fake traversal still does not reproduce a real compiler.

The additional [review probe](evidence/r265/reassociation.py) checks production
tree shape against an independent recursive power-of-two split oracle for
sizes 0–33, including odd tails and a repeated-cancellation control. It checks
28 graphs with all four coordinates symbolic, and 56 exact rational evaluations
of `exact_data` with symbolic time at t=0 and t=1/8. Thus the review also covers
Constant-like time graph construction. Coefficients are compared as the exact
rational values of their existing binary-float conversions; original rational
coefficients are separately used for the arithmetic sample reference.

## Floating-point reassociation

The [arithmetic evidence](evidence/r265/reassociation.json) evaluates 28
polynomials at 64 points each: cube corners/midpoints, five additional dyadic
or non-dyadic interior points, and t=0/1/8. References evaluate the original
rational polynomial exactly at each binary64 input coordinate. Across 1,792
samples, the maximum old/new difference is 1.2434497875801753e-14. Maximum
absolute error against that reference is 1.4210854715202004e-14 for balanced
sums and 1.2434497875801753e-14 for the old sums. Balancing does not guarantee
smaller error on every sample.

For the same already-rounded monomial values, a term crosses at most
h=ceil(log2(n)) additions. Under normal binary64 arithmetic without underflow
or overflow, multiplying those rounding factors gives the addition-only
bound gamma_h times the sum of absolute monomial values, where
 gamma_h = h*2^-53/(1-h*2^-53).
The probe checks that bound using exact fractions for all samples. It does
not bound power/coefficient rounding, generated compiler transformations,
quadrature, cancellation in assembled constraints, conditioning or solution
error over the whole domain.

The observed difference is comparable to the signed diagnostic floor 1e-14;
it cannot be used as proof of passing that gate. The relative diagnostic gate
1e-8, identity floor 1e-12, compatibility multiplier 128, nonlinear/linear
residual gates and all other thresholds remain fixed. Reassociation is accepted
as a measured-risk source repair because it preserves polynomial contributions
and removes the demonstrated fake-tree depth mechanism. The later actual
compiler/solver/diagnostic result must decide acceptance. No tolerance increase,
recursion-limit change, library patch or synthetic diagnostic is authorized.

## Separate allocation and retained evidence

The [allocation](evidence/r265/allocation.json),
[finite caller](evidence/r265/run_once.py),
[47-file source inventory](evidence/r265/source_inventory.json) and
[artifact inventory](evidence/r265/artifacts.json) bind the later execution.
The caller is byte-identical to R261 after replacing only request/owner/path
identity with R265. Its source/artifact inventories, manifest/contract,
interpreter and caller hashes are checked before manager access/reservation.
The [six caller checks](evidence/r265/caller_tests.json) use a fake manager and
supervisor and verify valid dispatch, source/artifact/contract refusals,
spent-directory refusal, capacity/controller/version refusal, outer timer and
exclusive persistence. No real manager connection occurred.

The [audit](evidence/r265/audit.json) verifies all 47 source hashes unchanged,
eleven runtime artifacts, four library resolutions, archive/interpreter,
97 raw originals against their historical hashes and Git-index bytes, eight
spent reservations and absent recorded PIDs/cgroups. All 1,760 previously
tracked evidence files are byte-identical to R264 delivery. Saved R246/R253
validators replay PASS; R255's exact rational reference including negative
controls reproduces. R242/R258/R262 remain INCOMPLETE and R229's setup resource
predicate remains false. The fresh fixed run directory and dangling link
`/tmp/navier-manufactured-r265-once` are absent.

## Later execution boundary

A later Continue must synchronize cleanly and publish its STARTED record first.
Pass that exact clean launch HEAD to the fixed R265 caller using
`/tmp/navier-fenicsx-r229/bin/python`. Keep the checkout unchanged during the
attempt. Recheck source/artifacts and fresh directory; the caller refreshes
host capacity/controllers and reviewed manager version. There is no standalone
FEM import, compiler prewarming or reuse of a spent directory.

The unchanged single pilot is n=2, t=dt=1/8, 402 mixed / 405 bordered DOFs,
degree24/26 and 60 assembled scalar receipts. Caps remain 180 seconds outer,
15/150/15 seconds setup/work/finish, independent 149-second worker expiry plus
one-second grace, 1536 MiB/no swap, 32 tasks, one rank/thread, 2,000,000-byte
numerical report and latest sparse system <=512 DOFs/4 MiB/65,536 entries.
Memory-max/OOM/OOM-kill/PID-limit events refuse acceptance.

Reservation/directory creation or partial worker start spends this new 1/1
allowance even on INCOMPLETE. Preserve every raw file, bounded failure record,
caller output, resource receipt and cleanup result; verify Git inclusion of
raw `.log` files. Stop after one outcome for Astra/high interpretation. A
proven pre-reservation/pre-worker/pre-import caller error follows the repository
recovery protocol: preserve error/timing gaps, verify the fixed directory and
manager contain no new task process, repair/test and publish a clean binding
before continuing the same unspent allocation. Uncertain state stops. No
alternate directory, retry, inferred reset or scientific/resource gate change.

The exact R262 failing expression, actual balanced UFL/JIT behavior, pilot
errors/budgets, resource peaks/events, convergence/rank, R242 cause and artifact
label origin remain unknown. Resource sampling before handshake/exit and
unobserved final save tails remain measurement limitations. Even PASS would
establish only one-level discrete solve/diagnostic consistency, not convergence,
tank control, B2 readiness or physical realization.

Next: **use `/new`, select GPT-6 Sol / high, then Continue** on PC/WSL `daisy`
to execute only the fixed R265 caller once, preserve/publish evidence and stop
for Astra/high interpretation. This is a saved source/admission boundary;
no current context percentage was supplied. [Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol)
confirms high reasoning support; task fit is judgment, account availability
unverified, and no model/session switch occurred here. PC retains ownership;
Mac remains released.
