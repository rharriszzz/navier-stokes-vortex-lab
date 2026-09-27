# R263 — Primary compilation failure and balanced-expression repair contract

2026-09-26 (America/New_York), PC/WSL `daisy`. **Implement a balanced symbolic
polynomial evaluator next. R262 remains INCOMPLETE; all eight allocations are
spent and zero new attempts are admitted.** This review changes no runtime
source. Follow the [single next task](../../SESSION_HANDOFF.md#next-task).

## Evidence and diagnosis

R262's [failure record](evidence/r262/run/failure.json) establishes completed
imports, geometry, lift/history and primary form construction. The failure is
inside the first `fem.form(forms['jacobian'])` at `cube_adapter.py:195`, before
the `primary_compilation` end marker. DOLFINx form creation enters JIT; the
retained tail repeatedly visits UFL's `GateauxDerivativeRuleset.process`,
`DAGTraverser.__call__` and its postorder wrapper. The bounded 32-frame trace
omits the middle and expression objects. It does not identify the exact
offending expression. No successful compilation, assembly or solve is observed.

The repository's `Poly.evaluate` builds every monomial with the original
coefficient converted to float, then adds it to a running total. Its addition
tree grows linearly with term count. The manufactured continuous force has
221, 222 and 11 terms. `step_forms` uses that force plus the exact BE load
correction; `build_forms` differentiates the whole residual, which still
contains the coordinate-dependent prescribed load and exact history.
Independence of these terms from the mixed unknown makes their derivative zero
mathematically, but does not itself remove the derivative traversal.

Read-only inspection of the installed UFL source shows binary `Sum` operands
with zero/constant simplifications and operand sorting, without flattening or
balancing the sum tree. The postorder wrapper recursively visits operands
before the sum rule adds the resulting derivatives. Official
[UFL sum source](https://docs.fenicsproject.org/ufl/2025.2.0.post0/_modules/ufl/algebra.html)
and [traverser source](https://docs.fenicsproject.org/ufl/2025.2.0.post0/_modules/ufl/corealg/dag_traverser.html)
provide supporting context. Those pages are labelled 2025.2.0.post0; the
installed 2025.2.1 files, hashed in the [probe](evidence/r263/probe.json), are
the evidence used here. No installed library was imported or modified.

The [dependency-free probe](evidence/r263/probe.py) executes selected installed
AST for the traverser, derivative dispatch fallback and sum rule with fake
scalar expression objects. It runs the real repository polynomial evaluator
on those operands and compares an evidence-only adjacent-pair reducer. Fake
product/power/leaf rules traverse children and return zero; identity hashes
deliberately avoid modeling UFL hashing and equality. No UFL graph, compiler,
residual, FEM module, manager or worker runs.

| Manufactured load component | Terms | Existing modeled depth | Balanced depth | Extracted traversal |
|---|---:|---:|---:|---|
| x | 221 | 224 | 12 | Existing RecursionError; balanced completes |
| y | 222 | 224 | 12 | Existing RecursionError; balanced completes |
| z | 11 | 12 | 6 | Both complete |

The interpreter recursion limit stays 1000. All 28 velocity/pressure/force
cases across manufactured, Poiseuille, rotation and affine-time fixtures retain
the same nonconstant monomial/factor multiset and exact rational sum of their
binary-float constant contributions. All balanced cases traverse successfully.
Five empty/singleton/odd-length checks pass. Negative controls preserve the two
original long-chain failures and detect an omitted odd tail and a flipped
coefficient. The initial probe's stricter raw-summand comparison rejected
legitimate constant folding in two axial-force cases; the final comparison
explicitly sums those constants as exact rationals. No physical tolerance was
used or changed to make that check pass.

This demonstrates a sufficient depth mechanism and supports the proposed
repair. It does **not** prove that the saved worker failed on either particular
force component, exclude every UFL issue, or establish that the repaired real
compiler will succeed. The runtime failure must retain that uncertainty.

## Fixed next source implementation

Make one source-only change set, then publish and stop for separate source and
admission review. Runtime edits are limited to `polynomial.py` and the five
symbolic evaluation expressions in `cube_adapter.py`, plus focused tests.

1. Add `Poly.evaluate_balanced(coordinates)`. Generate monomials in the existing
   dictionary insertion order with exactly the current `float(coefficient)`,
   coordinate order and exponent operations. Combine adjacent pairs into a
   new list each round and carry an odd final term unchanged. Return integer
   zero for no terms and the sole term for a singleton. The tree adds at most
   `ceil(log2(number_of_terms))` levels above the deepest monomial. Use iterative
   Python list reduction; no UFL/NumPy import, recursion, `math.fsum`, coefficient
   pruning, term sorting, Horner conversion, or polynomial/time substitution.
2. Keep `Poly.evaluate` and its arithmetic order unchanged. Numeric nodal
   interpolation in `interpolate_state` continues to call it. This avoids
   changing the initial lift and perturbation through a numeric evaluation
   refactor. No new default dispatch or type detection is needed.
3. In `exact_data`, route the vector helper, scalar pressure, return targets
   and return pressures through `evaluate_balanced`. The vector helper also
   covers manufactured force and traction offsets. In `step_forms`, route the
   manufactured continuous-time derivative vector through the same method.
   Thus exact current/history/load/offset expressions and diagnostics share
   the bounded-depth path; both degree24 and degree26 use it. The four fixtures
   retain their existing algebra, and the scalar/nodal default path is preserved.
4. Keep the automatic Jacobian of the complete residual. Preserve corrected
   BE forcing, exact expression history, all coefficients/signs, pressure/flux
   constraints, lift, quadrature, solver options, diagnostics and their 60
   assembly receipts. Do not omit prescribed terms from the residual, insert
   an analytic or synthetic Jacobian, raise the recursion limit, patch UFL,
   install packages, change artifacts, or relax scientific/resource gates.
   Reassociation changes floating-point evaluation order on the symbolic path;
   the existing acceptance thresholds still apply to any later real run.

## Required implementation checks

- Test that the new production method preserves every generated monomial,
  coefficient, factor and multiplicity under independent fake symbolic
  operands, including negative coefficients, repeated cancellations, zero,
  singleton, even and odd counts. Check deterministic association and the
  logarithmic depth bound. Deliberately losing an odd term, changing a sign,
  or reverting to sequential accumulation must fail the relevant check.
- Exercise all four fixture field/force families and manufactured exact history
  and corrected load at t=dt=1/8 with fake scalar operands. Compare algebraic
  values with exact rational fixture evaluation, distinguishing the existing
  coefficient-to-float conversion from changes to polynomial coefficients.
  Do not demand bitwise equality from reassociated floating-point sums.
- Exercise injected `exact_data` and the `step_forms` routing at degrees24/26.
  Make symbolic calls to the legacy `evaluate` fail in the test so that an
  overlooked deep force/history/offset/continuous-derivative path is detected.
  Separately verify default numeric `evaluate` remains byte-for-byte unchanged
  (or equivalently prove its exact existing operation sequence), and that
  numeric interpolation still uses it. The fake test cannot certify real UFL.
- Carry the depth probe as a test of the production method, retaining its
  limitations. Verify no recursion-limit change, numerical imports, worker,
  manager or allocation. Portable tree-depth and algebra checks must not depend
  on an incidental interpreter failure threshold; the extracted 3.12.13
  traversal failure is recorded evidence, not a new universal numerical gate.
- Run all 114 current standard-library/injected-fake tests plus additions.
  Replay saved R246 and R253 validators, reproduce the R255 rational reference
  and negative controls, and verify all 97 retained evidence files/eight spent
  reservations. Publish the changed source inventory and results for review.

The following review must assess source/test coverage and floating-point
reassociation, then separately decide whether to bind a fresh one-use admission
and finite caller. This implementation creates no caller, allocation or real
UFL/FEM check. A later runtime refusal still spends its separately admitted
attempt. Full convergence, tank, B2, rendering and Mac transfer remain outside
this task.

## Evidence publication correction and verification

R262's local audit checked copied files but did not check Git inclusion.
Its `run.log` and `worker.log` were omitted from delivery by `*.log`; the same
audit found two older R235 logs omitted. All four already existed locally and
match both the retained originals and their historical hash inventories.
R263 explicitly stages those unchanged files, totaling 781 bytes. No raw file
or old inventory is rewritten. The [new audit](evidence/r263/audit.json) records
the four base-commit omissions and verifies all 97 raw files are now in the
Git index with matching bytes. This closes the evidence-transfer gap without
rerunning any allocation. Future publication checks must verify Git inclusion,
in addition to filesystem existence and hashes.

The audit also verifies 46 unchanged source/test/pin/reference hashes, eleven
runtime artifacts/four resolutions/archive/interpreter, eight spent
reservations and absent recorded PIDs/cgroups; it actually replays R246/R253
validators and reproduces the R255 rational reference. R242/R258/R262 remain
INCOMPLETE and R229 setup predicate remains false. Existing 114 tests are
reused as prior evidence because runtime source is unchanged. Current checks
cover the probe, saved-data audit, AST/JSON/links, append-only records, request
IDs, Git evidence coverage and whitespace.

Next: **GPT-6 Sol/high implements only the contract above**, publishes and
stops for Astra/high source/admission review. Continue in this chat because
the diagnosis and implementation are directly connected; no new context
percentage was supplied. [Official OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-sol)
confirm high reasoning support; task fit is project judgment and account
availability is unverified. No model/session switch occurred. PC retains
ownership; Mac remains released.
