# R272 — Bounded n=4 manufactured comparison design

2026-09-27, PC/WSL `daisy` retains ownership.
**The source implementation contract is fixed; execution remains unadmitted.**
A separate n=4 route can preserve the full sparse-system evidence and both
angular residual vectors within explicit new evidence caps. No evidence needs
to be discarded to bypass the old 512-DOF recorder. Runtime memory, compilation,
factorization and elapsed-time fit remain unmeasured and require a separate
admission review after implementation. R270 remains INCOMPLETE; all ten
allocations remain spent. No runtime source or acceptance gate changed here.

This follows [R271's question](MANUFACTURED_ANGULAR_INTERPRETATION_R271.md#precise-blocker-and-next-bounded-task):
does halving spatial mesh spacing reduce the exact-field errors and the signed
reaction/stress mismatch? Two levels test sensitivity; they do not establish
asymptotic convergence, a unique error cause, or a physical tank solution.

The non-executable [proposal](evidence/r272/proposal.json) fixes the inherited
physics, gates, caps and 18 baseline hashes. The [design probe](evidence/r272/probe.py)
and [result](evidence/r272/probe.json) reproduce the saved R271 analysis and
verify the dimension/storage arithmetic without numerical imports. The proposal
is not an allocation, executable manifest, admission or caller.

## Frozen experiment and evidence separation

Only mesh subdivision changes in the numerical problem: n=2 to n=4. Use the
same affine unit cube, tetrahedral P2 velocity/P1 pressure, manufactured fixture,
rho=1, mu=0.1, t=dt=1/8, step1, exact polynomial history at t=0, corrected BE
load, lateral lift, two return constraints, pressure gauge, conservative
residual and automatic Jacobian. Keep exact-interpolation initial guess plus
the existing deterministic 0.05 free-velocity perturbation, zero initial
border, frozen row scales, Newton/backtracking rules and unchanged serial
SuperLU options. The selected perturbation index can differ with mesh ordering;
retain its actual index and value. No n=2 rerun, n=8, time-step study, alternate
stress recovery, reaction substitution or different discretization is included.

Keep degree24 for the solve/backflow samples and degree24/26 for all 30 original
diagnostics plus both angular records. Keep every original numerical check,
including energy, angular rate and interval budgets. The angular rate limit is
still `max(1e-10, .01*sum(abs(original four terms)))`, evaluated on each level's
own terms. **The rule is unchanged; the numerical limit is not frozen to the
n=2 value 0.0003759966274385022.** Never loosen the limit after seeing n=4.
Approximation-error norms remain reported quantities without a new pass gate.

Use separate strict identities: outer fixture `manufactured_n4`, physics fixture
`manufactured`, kind `manufactured_spatial_comparison`, mode `single_be_n4`,
worker schema2; new manifest and evidence schema2. Historical n=2 schema1,
manifest, validators and routes keep their exact acceptance domains and limits.
A renamed or resized old payload must refuse in both directions. Source and
artifact hashes will necessarily differ for the new route; inherited scientific
constants are compared by value to the bound R255/R269 contracts.

| Inventory | Saved n=2 | Required n=4 |
|---|---:|---:|
| Cells / vertices | 48 / 27 | 384 / 125 |
| Exterior facets / each face tag | 48 / 8 | 192 / 32 |
| P2 velocity nodes / scalar components | 125 / 375 | 729 / 2,187 |
| P1 pressure entries | 27 | 125 |
| Mixed / bordered entries | 402 / 405 | 2,312 / 2,315 |
| Fixed lateral velocity components | 240 | 864 |

These counts follow the current uniform cube family; require measured geometry,
zero ghosts, parent maps and node-coordinate receipts to agree before proceeding.
Do not derive array ordering from the counts. Each of the 729 velocity nodes
must be within 1e-14 of a unique eighth-grid point, collectively covering the
9-by-9-by-9 grid. Derive the 864 fixed indices from actual velocity parent maps
and nodes with x or y equal to 0 or 1 after that grid check. Validate the exact
lateral trace using the original 1e-12 identity floor; reject pressure entries
in the fixed set, duplicate nodes/maps, and missing/extra fixed components.
This checks evidence geometry, without changing physical tolerances.

## Separate bounded evidence route

Retain `numerical.json`, `linear_system.json`, `angular_audit.json` within a
future separately reserved directory. New schema2 includes kind, manifest and
contract digests, exact clean source/interpreter binding and measured geometry.
Bind the sidecar bytes by hash/size in the new numerical envelope; the latest
linear record remains bound by the correction receipt. The final sidecar and
latest matrix have deliberately different state semantics.

| Evidence | Existing n=2 cap | New n=4 design cap |
|---|---:|---:|
| Latest sparse system | 512 DOFs; 65,536 entries; 4 MiB | Exactly 2,315 DOFs; 524,288 entries; 16 MiB |
| Angular sidecar, both degrees together | 262,144 bytes | 1,048,576 bytes |
| Numerical envelope | 2,000,000 bytes | 2,000,000 bytes |
| Saved-only comparison | Absent | 262,144 bytes |

These are **explicit prospective evidence-policy changes for the new route**,
not increases to the existing recorder or whole-task resource allowance.
Require bounded reads (cap+1), strict finite JSON, exact keys and dimensions,
no duplicate keys, no bool-as-number, and sorted unique CSR columns. Normalize
floating entries to finite binary64 values; integer indices remain bounded
integers. Reject nonfinite conversion or oversized tokens before persistence.
Serialize incrementally under the cap without dense matrices; preserve the
existing exclusive `.writing` then atomic replacement convention for the latest
system. Keep a previous complete record and partial write on failure; do not
solve after recorder refusal. Angular/numerical outputs use exclusive creation.
Persist finite records with failed comparisons; malformed records or failed
writes refuse and retain any partial evidence.

The entry bound uses 30 velocity plus four pressure local basis entries per
tetrahedron. Even a full local 34-by-34 clique, summed with duplicates over
384 cells, plus every mixed/scalar border entry in both directions and every
diagonal, is `384*34^2 + 6*2312 + 2315 = 460091`, below 524,288. Exterior-facet
couplings are contained in incident cell cliques; this bound relies on the
unchanged local forms (no interior/nonlocal operator). Elimination only removes
entries, and structural zero diagonals are already counted. It is a conservative
source bound, not a measured assembled nnz or LU fill estimate.

For the new compact JSON schema reserve at most 65,536 bytes per record for all
keys, punctuation/brackets, bindings, scalar receipts and other metadata outside
the counted arrays. Enforce that metadata bound; implementation must demonstrate
it, not merely assume it. With float tokens <=25 bytes, four-digit column/fixed
indices and six-digit CSR pointers, including separators, the probe bounds:

- Latest record at the **full entry cap**: 16,542,030 bytes, below 16,777,216.
  Count CSR values/indices/pointers, three 2,315-entry vectors (rhs, state,
  scales), 864 fixed values/indices and metadata.
- Angular record: 461,458 bytes, below 1,048,576. Count final 2,315 state,
  2,312 phi, 2,187 coordinates, 864 fixed values, **two** 2,312 raw residuals,
  2,315 final scaled residual, both maps/fixed indices and metadata.

Actual values generally encode more compactly. Neither bound covers in-memory
Python containers, JIT workspaces, matrix copies or factorization fill. The
streaming writer and bounded readers must still enforce actual bytes; a violated
assumption refuses instead of increasing a limit.

### Latest system and final residual provenance

The new latest-system writer preserves the complete pre-factorization lifted,
row-scaled CSR, rhs, current pre-correction state, frozen scales, fixed values,
correction sequence (1 through at most 12), solver settings and source binding.
It never labels this matrix/state as the final accepted state. Its new validator
checks full structure, receipt hash/bytes, fixed/scales aliases, source/manifest,
correction index and rhs norm. Do not reconstruct or solve that matrix during
comparison, store just a hash instead of its contents, or remove the recorder.

The final angular sidecar retains all R267 fields and six independent scalar
assemblies per degree: A_D, A_R, C_D, C_R, G_R and action(original residual,Phi).
Use the final 2,315 state, 2,312 phi coefficients, 2,187/125 parent maps,
729 coordinate rows, 864 fixed values/indices and both unscaled/uneliminated
2,312 raw residual vectors. Install final P_minus/P_plus/eta in both degree
contexts before assembly. Retain the original receipts and five identities
per degree; all use the original `max(1e-12,128*epsilon*sum_abs_terms)` rule.

Also retain the **final degree24 scaled bordered residual**, using the result
of the driver's existing final `assembler(state)` and the already frozen scales.
No extra solve or Jacobian assembly is needed beyond that existing call. Save
all 2,315 values. Validate fixed components are zero; independently compare
free mixed entries to `scales[i]*raw_degree24[i]` using the original identity
rule, and check the norm against final Newton history and its unchanged
absolute/relative stop criterion. Border entries retain the assembler's final
constraint residuals; compare them to independently reported flux/gauge
residuals with the same signs and scaling. From `prototype.build_forms`, the
unscaled border is `(flux_0 - (5/8)*volume, flux_1 - (417/256)*volume,
pressure_mean)` using degree24 raw values (`pressure_mean` stores the pressure
integral). Multiply each by its corresponding frozen border scale; account for
measured volume instead of assuming its floating-point value is exactly one.
These are residuals, not the P_minus/P_plus/eta multiplier values.

Recompute free raw L2 norm, maximum absolute free residual, R_D and R_F at
**both** degrees. Degree26 is an integration cross-check on the same final
solution, never a second solved state. Its raw norm has no invented n=2-derived
threshold. Nonzero norms/actions remain visible; the original quadrature,
constraint and identity checks determine whether interpretation is trustworthy.
Preserve numerical and angular evidence when the physical report fails, as
R270 did. A finite inconsistent angular sidecar cannot earn diagnostic completion
or outer PASS, even if its numerical report passes.

## Comparison and interpretation contract

A pure saved-data `spatial_comparison.py` reads the bound R270 files and the new
n=4 outputs after supervision. It imports no numerical package and launches
nothing. Preserve R270's historical source identity; never rewrite it to the
new HEAD or rerun the baseline. The proposal binds all 16 R270 raw files plus
R271's derived probe and the R255 reference. Rebuild raw reports, sidecar
reductions and rational reference, comparing derived caches rather than trusting
them. Use repository copies for the baseline; historical `/tmp` originals are
an audit convenience, not a prerequisite for the future comparison.

Validate evidence integrity separately from numerical acceptance, so the known
n=2 physical refusal is usable. Missing files, malformed records, changed
hashes, incomplete geometry/history/degree inventories or inconsistent identities
yield an INCOMPLETE comparison with reasons. Never catch an arbitrary refusal
and reinterpret it as the expected physical-budget failure. Validate the latest
record independently even when the numerical acceptance validator would stop
earlier on a physical refusal.

For each degree retain signed n=2/n=4 values, exact reference where defined,
errors, signed change and absolute-error ratio for the following finite rows:

| Rows | Required meaning |
|---|---|
| Four original angular terms, their sum, rate limit and defect/limit | Retain storage and advection errors as well as stress; limits use each level's own terms |
| Angular endpoint and interval defect/limit | Check endpoint/storage identity and interval = dt times rate defect within existing identity bound |
| A_D, A_R, C_D, C_R, G_R, independent residual action | Exact parts from R271; exact action = -521/38400 |
| R_D, R_F, reaction torque, lateral and return mismatch | Exact reaction/R_D = -521/38400; exact R_F and mismatches zero |
| Reaction error minus (storage error + body error + return-advection error + G_R error - R_F + A_D error) | Preserve the independently measured reaction-error identity |
| u L2, u H1 seminorm, mean-zero p L2, div u L2, return-traction L2 | Original exact-field error measures; no new norm acceptance gate |
| Free raw residual L2/max, final scaled residual/history, linear true residuals, multipliers/eta and constraints | Solver/evidence checks alongside approximation errors; never compare DOF arrays by index across meshes |
| All energy terms/budgets, quadrature differences, original acceptance flags | Keep complete original physical decision; no angular-only promotion |

For an error e use `abs(e4)/abs(e2)` only when the denominator exceeds the
existing identity-resolution floor `max(1e-12,128*epsilon*(abs(e2)+abs(e4)))`.
Otherwise write JSON null with reason `baseline_at_identity_floor`, never an
infinite ratio or artificial zero. This is a display/interpretation rule, not
an accuracy gate or statistical uncertainty estimate. For signed terms report
sign changes. Label magnitude shrinking, unresolved/unchanged, or growing using
`abs(e4)-abs(e2)` against that floor. Do not claim a rate from a log2 ratio.
No automatic favorable verdict based on only the total defect is permitted.

| Observed outcome | Permitted conclusion and stop |
|---|---|
| Valid evidence; errors and both lateral contributions shrink; defect shrinks | Supports spatial sensitivity for this pair; sole cause and convergence remain unknown |
| Valid evidence; total defect shrinks while components/errors do not | Report cancellation/mixed response; no claim of general accuracy improvement |
| Changes at the identity floor | Unresolved at that arithmetic scale; no proof of mesh independence |
| Errors/defects grow or change sign | Report full component table; spatial explanation remains inconclusive; stop for scientific review |
| Physical gate still fails but evidence is consistent | Diagnostic comparison can be COMPLETE; n=4 numerical result is INCOMPLETE |
| Every n=4 original gate passes and evidence/resource checks pass | A passing n=4 single-level result only; R270 stays INCOMPLETE and two-level convergence unproved |
| Source/baseline mismatch, residual/identity/quadrature inconsistency, missing output or resource refusal | No trustworthy discrimination; preserve partial rows marked unavailable and stop without retry |

Report `comparison_status`, both independent `numerical_status` values and
`interpretation_status` separately. COMPLETE means finite consistent evidence
and non-budget solver/constraint/quadrature checks, even if a physical budget
fails. Failed non-budget prerequisites keep comparison INCOMPLETE with finite
available values retained. Full implementation must specify these status keys
exactly in its schema/tests; it must not invent acceptance thresholds.

## Fixed source implementation task

Add sibling modules under `verification/nonlinear_port/`:

1. `spatial_manifest.py` and `future_manufactured_n4.json`: strict non-executable
   schema2 proposal, exact n=4 counts, inherited gates and new evidence caps.
   Both retain `execution_admitted=false`, `attempts_granted=0`. Bind the R272
   proposal and baseline hashes. Never patch the old proposal in place.
2. `spatial_driver.py`, `spatial_report.py`: new fixed n=4 driver/envelope,
   reservation/admission validation and pure report replay. Adapt the reviewed
   manufactured routes only for identity, dimensions and new recorder receipts;
   reuse unchanged adapter/diagnostics/sparse/Newton/physics helpers. The report
   must preserve all original formulas, finite checks, receipt sequence and
   acceptance logic while accepting the separate manifest and 16-MiB receipt.
   Do not pass a fake n=2 manifest to an old validator to launder new evidence.
3. `spatial_linear_evidence.py`, `spatial_angular.py`: separate schema2 writers,
   assembly helper and strict validators implementing the contract above. Small
   pure helper reuse is allowed; no global monkeypatching or dimension inference
   from untrusted payloads. Existing n=2 public validators remain unchanged.
4. `spatial_worker.py`: held/released worker with both mandatory recorders,
   final-state capture, new source/manifest hashes and finite failure persistence.
   Reuse existing handshake, imports, stage tracker and resource machinery.
5. `spatial_comparison.py`: bounded saved-only reducer/validator and exact
   comparison table, exercised with synthetic evidence and saved baseline.
   Integration into a future caller is specified and fake-tested, but no live
   caller/allocation is published during implementation.
6. Add `supervise_spatial_once` to `supervision.py`, with a fixed dispatch pair
   `manufactured_n4` / `verification.nonlinear_port.spatial_worker` and new
   strict validation. Extend only the private dispatch allowlist/reservation
   identity-copy branch. Retain all existing wrappers and CAPS unchanged.
   No generic arbitrary-worker dispatch. This source wrapper is inert without
   a separate future explicit admission; fake tests must establish that fact.

Separate modules deliberately avoid widening historical validation domains.
The duplication risk is controlled by golden saved replay, shared unchanged
physics/reduction primitives where appropriate, and explicit formula comparison
in the later review. Do not undertake unrelated architectural refactoring.
Publish the exact new schemas, public helper APIs, modified/new source inventory
and test results. The only planned existing runtime source edit is the additive
supervision dispatch/wrapper; if another shared edit is necessary, explain and
prove preserved old behavior before considering the implementation complete.

Required guarded tests include all 127 existing source/fake tests and eight
historical fake-caller tests, saved R246/R253 PASS and R266/R270 refusal, exact
R255 reference/R267 controls, and these focused controls:

- Exact n=4 geometry/maps/fixed set; n=2/n=8 and cross-schema refusal; wrong
  shape/block/map/coordinate, bool, duplicate, nonfinite and oversized inputs.
- Complete sparse vectors/scales, bounds at/above caps, structural zero
  diagonals, malformed/sorted CSR, wrong correction/hash/state aliases, failed
  replacement retaining previous/partial evidence and preventing factorization.
- Both independent raw/scalar action paths, nontrivial map order, distinct
  final degree26 Constants, nonzero fixed/free actions, changed signs and
  missing lateral/free terms; final versus pre-correction state and residual.
- Driver/worker ordering, mandatory output, physical INCOMPLETE persistence,
  valid sidecar not promoting failed physics, missing/inconsistent sidecar
  defeating outer PASS and refusing comparison completion.
- Missing/wrong admission, fixed dispatch, capped fake resource outcomes and
  old route behavior; no real manager or fixed run directory creation.
- Saved-only table controls: shrinking, cancellation, unchanged, growing,
  sign reversal, near-zero denominator, altered baseline, false cached flags,
  mixed degree/state/source, failed non-budget gate and missing partial output.
- Full-cap serializer size checks including both degrees, all metadata and
  the final scaled residual; no unbounded JSON encode followed by size check.

## Resources, admission boundary and preservation

Keep the existing 1,536-MiB whole-task cap, no swap, 32 tasks, one MPI rank,
one numerical thread/library, 20,000 mixed-DOF ceiling, 15/150/15-second phases,
180-second observed total, independent 149-second expiry plus one-second grace,
and zero memory-max/OOM/OOM-kill/PID-limit events. New writing/reading/comparison
cost must be included in the unchanged appropriate work/outer timing scope;
no unmonitored helper solve, warmup, JIT probe or test mesh is allowed.

The largest proposed files total under 20 MiB, but neither that fact nor R270's
486,866,944-byte n=2 peak proves n=4 runtime fit. LU fill, quadrature/JIT cost,
container duplication and actual time remain unknown. The next implementation
may use pure source/fake tests only. After it is published, Astra/high must
review all bindings, caps, finite caller timing and acceptable measurement risk
before admitting any new one-use experiment. A resource/evidence refusal is a
valid spent outcome. No resource increase, recovery solve or new directory is
implicitly authorized. R229's setup predicate remains false; final save tails
and an independent parent wall interval remain unresolved.

For a later admitted launch, retain the session recovery rule only for proven
caller faults before reservation, managed worker and numerical import: preserve
error/timing evidence, verify fixed directory and manager absence, repair/test
and publish a clean binding before proceeding. Reservation, partial start or
uncertain state stops without retry/reset. All ten old allocations stay spent.

The [audit](evidence/r272/audit.json) verifies 132 retained raw/caller files
against original and Git-index bytes, 1,860 historical evidence files unchanged,
50 source bindings, 15 runtime artifacts/four resolutions/archive/interpreter,
all ten spent reservations and absent recorded PIDs/cgroups. No manager query
or numerical import occurred. The design probe reproduced R271, original
validators and the exact reference; prior 127 source/fake and eight caller tests
are reused, not rerun, because runtime source is unchanged. [Publication
checks](evidence/r272/checks.json) cover schema arithmetic, AST/JSON, local links,
append-only logs/lifecycle, sequential requests, allowed scope and whitespace.
The first publication check found its own not-yet-created `checks.json` link;
bootstrap handling was corrected, followed by a full link check after creation.
This was a documentation-check error, with no runtime or allocation activity.

Changed: this design/proposal/probe/audit/check evidence, seven current pages,
request/lifecycle logs and handoff. Skipped: runtime implementation, admission,
manager/worker/reservation, numerical import/JIT/assembly/solve, full convergence,
tank/B2, physical/render and Mac transfer. Unknown: actual n=4 errors/resource
fit, sole cause, convergence, lateral pressure/shear split, R242 cause and
artifact-label origin. The source/evidence design blocker is resolved; these
runtime/scientific questions are not.

**Use `/new`, select GPT-6 Sol/high, then Continue** for the fixed source and
fake-test implementation above, publishing before Astra/high source/admission
review. This is a saved design boundary; no current context percentage was
supplied. [Official OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-sol)
confirms high reasoning support; account availability is unverified, and no
model/session switch occurred. Return to Astra/high for unresolved scientific,
resource or evidence-policy choices. Follow the [single current handoff
task](../../SESSION_HANDOFF.md#next-task).
