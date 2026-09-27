# R264 — Balanced symbolic polynomial evaluation integration

2026-09-26 (America/New_York), PC/WSL `daisy`. **Source integration is complete;
R262 remains INCOMPLETE.** All eight numerical allocations are spent and this
task admits zero new attempts. Follow the [single next task](../../SESSION_HANDOFF.md#next-task).

## Source change

The [R263 contract](MANUFACTURED_DEPTH_REVIEW_R263.md) identified linear-depth
symbolic addition as a sufficient mechanism for the saved recursion failure.
`Poly.evaluate_balanced` now constructs each monomial in the original insertion
order, with the same coefficient-to-float conversion and coordinate/exponent
operations as `Poly.evaluate`. It reduces adjacent pairs iteratively, carrying
an odd last term unchanged. Empty and singleton results retain their specified
forms. The original `evaluate` source and numeric interpolation call are unchanged.

The five symbolic evaluation sites in `cube_adapter.py` now use the balanced
method: the `exact_data` vector helper, targets, pressures, scalar pressure,
and `step_forms` continuous-time derivative. The helper covers field, force,
history and traction-offset vectors. Both degree24 and degree26 routes retain
the exact backward-Euler load correction and automatic Jacobian. Fixture
algebra, signs, coefficients, solver and scientific/resource gates are unchanged.
Reassociation can change floating-point summation order; later real acceptance
thresholds remain unchanged.

## Verification and limits

The [118-test run](evidence/r264/tests.json) uses Python 3.12.13 with a guard
against numerical imports. It includes all prior 114 source/fake tests and four
new tests. The new tests cover all 28 field/force fixture graphs, exact monomial
signatures, independent rational samples, empty/single/even/odd cases, omitted
tail and flipped-sign controls, logarithmic depth, the extracted fake derivative
traversal, and symbolic routing through injected `exact_data` and degree24/26
`step_forms`. A source AST pin and injected interpolation verify the unchanged
legacy numeric path. The extracted traversal still reports recursion for the
old 221/222-term left folds and completes at depth 12 for the balanced forms.
This is a fake-operand source test; it does not certify actual UFL compilation.

The run also replays saved R246/R253 validators as PASS and rederives the R255
exact rational reference. The [R264 audit](evidence/r264/audit.json) binds 47
source/test/pin/reference files: 44 old hashes unchanged, two runtime source
files changed, and one new test file. It verifies eleven runtime artifacts,
four library resolutions, archive/interpreter identity, all 97 raw files against
their retained originals and Git index, eight spent reservations and absent
recorded PIDs/cgroups. The full [source inventory](evidence/r264/source_inventory.json)
and [test transcript](evidence/r264/tests.txt) are retained.

No numerical library import, real JIT, assembly, solve, manager, worker,
reservation, caller, admission, or new runtime attempt occurred. The saved R262
trace does not identify the exact expression; real compiler success, resource
behavior, manufactured error/budgets, convergence/rank and R242 cause remain
unknown. Full convergence, tank/B2, rendering and Mac transfer are outside this
source integration.

Next: **Astra/high reviews source and test coverage, especially symbolic
floating-point reassociation.** If accepted, that review separately decides
whether to bind a fresh one-use admission and finite caller, stopping before
launch. The implementation here grants no attempt. A new chat is recommended
at this published source/review boundary; no model or session switch occurred.
