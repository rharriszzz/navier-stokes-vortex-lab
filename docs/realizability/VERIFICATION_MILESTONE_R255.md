# R255 — Rotation review and manufactured spatial pilot contract

2026-09-26; PC/WSL `daisy` retains ownership. **The saved R253 rotation PASS
is reproduced. The next source task is one n=2 manufactured backward-Euler
pilot through the production weak forms, solver and diagnostics.** This review
grants **zero numerical attempts** and makes no runtime-source change.
The [fixed proposal](evidence/r255/proposal.json), [rational/saved-data
audit](evidence/r255/audit.py) and [result](evidence/r255/audit.json) accompany
this contract. Follow the [single next task](../../SESSION_HANDOFF.md#next-task).

## Saved result and limits

The audit calls the saved R253 validator without rewriting historical records
and reproduces its full audit object. It independently reconstructs all 38
rotation targets using rational polynomials and compares them with R247 and
the admitted contract. R253's 76 raw scalars/assembly receipts and log pairs,
both-degree target decisions and 38 pair decisions pass. Measured geometry is
48 tetrahedra, 27 vertices, 48 exterior facets, eight per tag and 402 unused
mixed-space DOFs. The largest target error/limit ratio remains 0.091705.

All 74 original raw files across six spent allocations match their retained
copies; reservations remain retained and recorded PIDs/cgroups absent. The
36 source/test/pin hashes remain unchanged. R251 caller/inventory bindings,
eleven exact runtime artifacts, four library resolutions, cached archive and
interpreter hashes verify by reading bytes without loading libraries. This
reuses the accepted exact artifact identity, including the disclosed SuperLU
package 7.0.1 / embedded 7.0.0 discrepancy; it does not resolve its origin.
R246 remains PASS, R242 INCOMPLETE and R229's setup predicate false.

Saved worker/caller exit 0, manager success, empty cleanup and zero memory.max,
OOM, OOM-kill and PID-limit events pass the R251 gates. Peak managed memory
was 223,670,272 bytes and peak tasks six. The saved caller interval was
12.77116161599406 s; its precise endpoint is **after saving caller.json**, before
the caller-completion record save. R253's table phrase “after caller completion
save” is imprecise; raw evidence is unchanged. The final save tail and independent
parent wall interval remain unobserved, and resource sampling ends before final
handshake/exit. No cold-cache or future manufactured-runtime prediction follows.

Rotation has D(u)=0. It detects a nonsymmetric stress/gradient-dissipation
mistake, geometry/orientation errors and centrifugal-pressure mistakes under
the fixed oracle, but any multiplier of the correct zero strain also yields
zero. It never called production `build_forms`, Newton or sparse solve. R246
already exercised a nonzero-shear, exactly representable steady solve; neither
result supplies manufactured spatial convergence, transient verification,
general rank/stability or a physical tank result.

## Choice of next milestone

| Option | New evidence | Decision |
|---|---|---|
| Exact manufactured-field assembly | Nonzero strain, body torque/power and rational budgets through diagnostic forms | Useful algebra checks below, but another standalone assembly would still bypass the production residual and solve. |
| One n=2 manufactured spatial BE pilot | Production nonzero-strain/load/return path, exact-history isolation, nonlinear correction, coarse approximation errors and discrete budgets | **Implement this source contract next.** Any later runtime PASS is pilot consistency only. |
| Full n=2/4/8 spatial and affine-time studies | Rates and finest-level errors specified by R195 | Premature: generalized driver/report routing and resource admission are absent; larger saved systems exceed the present recorder cap. |

The n=2 pilot has 402 mixed and 405 bordered unknowns. The same mesh family
would have 2,312/2,315 at n=4 and 15,468/15,471 at n=8 (mixed/bordered counts
from 3(2n+1)^3+(n+1)^3, plus three scalar unknowns). Both exceed
`linear_evidence.MAX_DOFS=512`. The broad 20,000 mixed-DOF proposal does not
override that recorder limit. Do not enlarge it during this pilot implementation.
Later convergence needs a reviewed evidence-size/resource strategy, one defined
budget for all levels, and actual rates; the pilot cannot grant that admission.

## Exact reference and discrete time meaning

Use the existing R195 manufactured fixture unchanged: rho=1, mu=1/10,
dimensionless affine unit cube, lateral exact Dirichlet velocity and separate
z=0/1 return totals with exact traction offsets. Fix **n=2, step=1,
time=dt=1/8**, one BE spatial-isolation solve, primary degree24 and diagnostic
degree26. Preserve P2/P1, conservative convection, physical symmetric stress,
full-pressure/eta/gauge border and both positive pressure columns.

The independently constructed polynomial agrees with `fixtures.manufactured`,
has zero divergence/pressure mean and an exactly affine lateral trace. At 1/8:

| Quantity | Exact rational value |
|---|---:|
| A, C, E, H | 577/512, 5/8, 521/512, 9/8 |
| Q minus, Q plus, Q lateral | 5/8, 417/256, -577/256 |
| P minus, P plus | -1057/1280, 383/1280 |
| Integral D:D | 305946379/40140800 |
| Viscous dissipation 2mu integral D:D | 305946379/200704000 |
| Initial kinetic energy K0 | 165383/264600 |
| Initial angular momentum L0 | 1/450 |

The return offsets are `g_s=-(9/8)(x²+y²-2/3)n_s`, with zero normal area mean
and zero tangential components. Both prescribed outward cap velocities are
strictly positive. Their sum exactly balances the lateral lift; do not replace
the targets or expected multipliers by Poiseuille's zeros.

Use `f_BE=f_continuous+(u_exact(1/8)-u_exact(0))/dt-u_exact,t(1/8)` and **exact
polynomial u_exact(0)** in both residual and diagnostics. `cube_adapter.step_forms`
already returns the corrected `context['force']` and `context['history']`.
The new driver must consume those expressions. Interpolated previous Functions
may satisfy the existing API but must not become the spatial residual/diagnostic
history. For degree26 change the integration measures while retaining the same
exact history and corrected load; do not copy Poiseuille's use of
`U.split(previous)[0]` or `exact_degree['force']`.

The rational audit independently derives the forcing in advective form,
checks it against the source's conservative construction, verifies return
tractions and all six-face energy/angular terms, and obtains exactly zero
signed defects. Saved [reference values](evidence/r255/audit.json) include all
terms and endpoints. These are **exact-field references**, not expected zero
approximation errors for the nonrepresentable n=2 solution.

Negative controls yield nonzero defects: continuous forcing used in this BE
problem gives residual squared norm 331/169344; half viscosity gives
271441/430080000; dropping body torque/power or the BE energy contribution also
fails the rational identities. These establish sensitivity of the algebra;
they do not establish sensitivity or accuracy of an unrun discretization.

## Required implementation

Implement and test the following as one source-only task, then stop for
Astra/high source/admission review. Names below define the intended separation;
minor internal factoring is permitted if the public fixture bindings and
old behavior remain fixed.

1. Add `manufactured_policy.py`, `manufactured_manifest.py` and
   `future_manufactured.json`. The strict non-executable manifest incorporates
   the fixed [proposal](evidence/r255/proposal.json), pinned versions, caps,
   policy, reference/time semantics and report limit; canonical validation
   rejects unknown/missing/changed fields and bool-as-number substitutions.
   It always says execution_admitted=false and attempts_granted=0. Preserve
   `future_fem.json`, `future_rotation.json` and both old numerical policies.
2. Add an injected `manufactured_driver.py`. Build only this cube/step using
   `create_cube`, `step_forms`, `Assembler`, frozen `row_scales`, `newton` and
   the existing unshifted serial SuperLU path/options. Install the exact lateral
   lift at t=1/8 before residual evaluation. Start from its nodal mixed
   interpolation with +0.05 at the lowest free velocity DOF, zero initial
   P_minus/P_plus/eta, and preserve all fixed velocity entries. Require at
   least one checked correction. Record perturbed DOF and fixed inventory.
3. Before Newton, assemble prescribed lateral flux and its absolute integral,
   both nonzero return targets and the existing three constraint-row Gram
   matrix after excluding fixed increments. Recompute its condition method
   and compatibility. Compare measured targets with the rational totals within
   1e-12, then use the **fixed rational totals** for report flux errors so a
   perturbed target cannot redefine success. Preserve the arithmetic
   compatibility bound 128*epsilon*condition*absolute_term_sum, condition<=1e6.
   This is a three-row condition screen, not a full matrix-rank certificate.
4. Solve at degree24; install the final accepted state before diagnostics.
   Assemble every one of the 30 raw diagnostic keys at both degrees, using
   exact history/corrected load. Save an ordered receipt and form/assemble log
   marker for each of these 60 scalar assemblies, including returned zeros.
   Do not substitute exact expected values for measurements. Sample both caps
   at degree24 using the existing positive triangle rule; retain sample counts
   and minimum. Measure n=2 geometry (48/27/48, eight facets/tag, 402 mixed DOFs,
   no ghosts, 405 bordered DOFs); do not emit a constant as measured geometry.
5. Add a pure reducer/strict saved-payload validator (within the new driver or
   a separate report module). Recompute both degree reports, signed budgets,
   pair gates, endpoint identities, compatibility/condition and every linear
   correction gate from finite raw records. Bind source, manifest, contract,
   interpreter/artifacts, versions and reference values. Recompute cached
   decisions/aliases and refuse any disagreement, even a cached false flag
   on otherwise passing raw data. Reject unknown/missing raw keys, bad numeric
   types/nonfinite values and negative required nonnegative quantities.
6. Add a held `manufactured_worker.py` and fixture-locked
   `supervise_manufactured_once` wrapper. Extend only the private finite
   lifecycle dispatch and backend fixture allowlist needed for the new worker.
   Reuse the existing held/source/thread/import handshake and cleanup state
   machine, explicit artifact-bound pin loading, finite JSON loader/writer
   behavior and fixed cap enforcement. Preserve Poiseuille/rotation public
   validation exactly; regression-test both saved PASS reports. The new
   wrapper must require a separate explicit admission before reservation.
   No default admission/backend, new executable caller or allocation yet.
7. Retain `LatestSystem(directory,binding)` immediately before each sparse
   correction, with its existing 512-DOF/size limits and atomic persistence.
   Retain finite complete numerical evidence even if a scientific gate is
   false; the controller must refuse PASS. Partial/failed work still preserves
   available linear/log/exit/cleanup evidence. Do not invent missing scalars.

The new envelope must include fixture/kind/mode/schema, manifest/contract hashes,
source binding, geometry, raw_by_degree, 60 receipts, multipliers/eta,
condition/compatibility inputs and decisions, nonlinear history and all linear
corrections, sample counts/minimum, perturbation/fixed-DOF records, phase timing,
worker intervals, actual versions/artifact, and both-degree recomputed reports.
Use the existing four Poiseuille phase meanings and two worker-interval meanings;
all times must be finite/nonnegative. Limit the serialized numerical envelope
to 2,000,000 bytes and reject duplicate JSON keys/nonfinite constants.
Source bindings must be checked in held and numerical records. Unknown schema,
fixture, mode, source, geometry or time/load semantics refuse before acceptance.

## Numerical report and gates

### Quadrature policy

Use the separate `manufactured_spatial_pilot_accuracy_v1` policy in the proposal.
It freezes 30 raw keys, 17 signed-floor keys and 12 nonnegative keys; angular
momentum is signed but is outside the signed-floor set, matching the explicit
inventory. Pair limits are `1e-8*max(1e-10,abs(degree24))`, with a `1e-14`
absolute floor **only** on those 17 keys. Both degrees must independently pass
their applicable step/identity/budget gates.

This prospectively selects the same signed accuracy budget used for R246,
under a distinct fixture policy. The 1e-14 floor is 10,000 times below the
1e-10 constraint/budget floor; it is a stated nondimensional accuracy budget,
not a proven floating-point bound. It avoids making the signed near-zero test
effectively 1e-18. It never retroactively changes R242 or weakens nonnegative
norm-pair checks. Runtime behavior at the fixed degrees remains unknown.

### Step and approximation evidence

Keep unit volume and both unit cap areas within 1e-12; both flux errors,
pressure mean and eta <=1e-10 in absolute value; minimum sampled normal
velocity >=-1e-8; nonlinear residual <=max(1e-12,1e-10*initial residual);
each true linear residual <=max(1e-13,1e-8*rhs_norm). Require full 2..13-entry
nonlinear history, one correction per transition, maximum 12 Newton iterations
and eight backtracks, and unchanged fixed initial row scaling. Refuse missing
or malformed evidence and failed intermediate corrections.

Report u L2, u H1 seminorm error, mean-zero p L2, div u L2, physical return
traction L2 error and both multiplier errors at both degrees. Retain the
existing pressure-variance cancellation check and reject materially negative
variance; report the signed integral and squared integral used. **No 1e-9
Poiseuille error gate, no finest-level .01/.02 threshold and no convergence
rate apply to this coarse pilot.** Approximation norms must be finite and
nonnegative; multiplier errors finite. A pilot PASS means this one discrete
solve passes the stated solver/constraint/budget checks. Accuracy remains an
open question for the later refinement study.

### Budgets and independent endpoints

Keep all four signed angular terms and all seven signed energy terms from
`field_forms`, including body work/torque, conservative-divergence and
pressure-divergence work, six-face traction/advection and symmetric dissipation.
Each signed rate defect is bounded by max(1e-10,.01*sum_abs_terms).
Use the existing BE storage identity bound max(1e-12,128*epsilon*sum_abs_terms).

Independently compute final-minus-initial inventories using measured
`kinetic_energy`/`angular_momentum` and rational K0/L0 above, separately at each
degree. Require agreement of `(Lh-L0)/dt` with angular.storage and
`(Kh-K0)/dt` with energy_identity_storage and kinetic_discrete_derivative;
use max(1e-12,128*epsilon*sum of absolute compared values) for each identity.
Also retain these complete signed interval terms:

```text
angular: Lh-L0 + dt*(advective+traction+body)
energy:  Kh-K0 + dt*(BE_dissipation+advective+traction+body+dissipation
                    +conservative_divergence+pressure_divergence)
```

For each interval use max(1e-10,.01*sum_abs_interval_terms), record defect,
limit and decision, and require acceptance. BE_dissipation is the assembled
energy_identity_dissipation, not a fitted correction. Label all of these
`discrete_manufactured_BE` and record dt/time/history/load semantics. They are
discrete forced balances; do not label them unforced continuum evolution,
use Poiseuille's stationary endpoints, or omit the BE contribution. For exact
fields that omission alone gives interval defect -647107/80281600.

## Source checks and stopping rules

Use standard-library rational checks and injected fakes without importing FEM.
At minimum prove the following meaningful failure boundaries:

- Rational reference values/returns, nonzero strain, both balances and all five
  supplied negative controls. Wrong continuous load, interpolated diagnostic
  history or wrong expected zero cap totals must be caught by routing/reference
  tests; fakes must distinguish these expressions rather than all returning 0.
- The driver builds only n=2/step1, retains the lateral lift, performs a real
  callback correction, supplies corrected load/exact history at both degrees,
  routes all 60 scalar calls, keeps zero receipts and samples both caps.
- Nonzero cap totals and multipliers reach the reducer; a finite coarse error
  above Poiseuille's 1e-9 is not rejected solely as an exactness failure.
  Independently fail flux/gauge/eta, nonlinear/each linear correction, backflow,
  condition, budget, BE/endpoint identity and both-degree quadrature gates.
- Reject extra/missing/duplicate keys, bools, nonfinite/negative squares,
  wrong policies/schema/time/history/load/source/artifact/geometry, mutated
  cached decisions and any skipped assembly receipt. Test both sides of the
  frozen signed floor, without importing/generalizing Poiseuille's policy.
- Held-before-import and no-admission-before-reservation; fake manager failures,
  exceeded caps/events/expiry, missing reports, worker nonzero exit and uncertain
  cleanup cannot produce PASS. Preserve R246/R253 saved replay and old tests.

The next implementation may change only the new fixture modules/tests/proposal
and necessary shared dispatch/geometry factoring, with explicit regression
evidence. Do not alter fixture mathematics, solver/options, general gates,
evidence-size limits, old manifests/policies, historical evidence or allocations.
If a required scientific contract change is discovered, report the precise
blocker for Astra/high; do not tune a tolerance or silently expand scope.

Later admission must bind the reviewed source/test hashes, manifest/contract,
exact interpreter and artifacts, and a **fresh absent** one-use directory.
Retain 180s overall / 15s setup / 150s work / 15s finish, 1536MiB, no swap,
32 tasks, rank/thread1 and complete exit/resource/cleanup gates. Real JIT cost,
nonlinear convergence, coarse diagnostic budgets and pair behavior are explicit
unmeasured risks. No new caller, reservation, manager access, numerical import,
assembly or solve is admitted now. All six prior allowances remain spent.
Future pre-reservation caller failures and spent-attempt stop rules follow the
session protocol; never repair/retry a numerical refusal under a spent allowance.

## Review checks and next action

The R255 audit passes under `/tmp/navier-fenicsx-r229/bin/python -B`, loading no
numerical modules. An initial system `python3` audit call stopped because its
older stdlib lacks `hashlib.file_digest`; no reservation, worker or numerical
import occurred. Rerunning the read-only audit with the pinned 3.12 interpreter
succeeded. No runtime repair or allocation change was involved. Existing tests
are reused because all 36 bound source/test/pin files are unchanged; new source
tests belong to the implementation task. JSON/AST/links, append-only records,
historical integrity and whitespace checks accompany completion evidence.

**Next: GPT-6 Sol / high implements this fixed source contract and tests, then
publishes and stops for Astra/high source/admission review.** Availability/high
support was searched and checked on the [official model page](https://developers.openai.com/api/docs/models/gpt-6-sol);
task suitability is our judgment. No model/session switch is claimed.
Continue on PC/WSL `daisy`; Mac remains released. No Chrome restart or numerical
execution is required for this source task. Full convergence, matrix stability,
R242 discrepancy cause, artifact-label origin and physical realizability remain
unresolved.
