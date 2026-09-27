# R271 — Interpretation of the measured angular split

2026-09-27 (America/New_York), PC/WSL `daisy` retains ownership.
**R270 remains INCOMPLETE. The evidence gap identified in R267 is closed;
no corrective source change is justified by the measured split alone.**
All ten allocations remain spent. This review makes no runtime implementation,
gate change, new admission, numerical import or workload launch.

The failed physical budget is a measured difference between the discrete
Dirichlet reaction and the boundary stress, with a smaller return contribution.
Its lateral component contains errors in both the reaction and stress when
compared with the exact manufactured field. It therefore does not identify
an isolated lateral-traction implementation defect. Spatial approximation is
a supported hypothesis to test, not an established sole cause.

## Reconstruction and exact comparison

The [standard-library probe](evidence/r271/probe.py) and
[saved result](evidence/r271/probe.json) recompute R270's raw fixed/free actions,
strict sidecar/numerical aliases, complete physical report and refusal. They
reproduce R267's rational identities and four decomposition controls, and
independently integrate the exact polynomial's lateral and return terms.
No FEM field or matrix is assembled or solved in this review.

Use R267's signs: phi=(-y,x,0), S=int(phi.dtu), B=-int(phi.f_BE),
A_X=int_X(phi.u)(u.n), C_X=-int_X phi.(sigma_h n), and
G_R=-int_R phi.t_prescribed. D is tags1–4; R is tags5–6.
The saved raw residual r and coefficients a give

```text
R_D = sum_fixed a_i r_i,    R_F = sum_free a_i r_i,
T_D = R_D + A_D,            M_D = T_D + C_D,
M_R = C_R - G_R,            delta = M_D + M_R + R_F.
```

T_D is the residual-based lateral traction torque, including the lateral
advection correction. C_D has the opposite physical-torque sign. R_D itself
must not be called the traction torque without accounting for A_D.

| Quantity | Exact field | R270 degree 24 | Discrete minus exact |
|---|---:|---:|---:|
| Lateral advection A_D | 0 | 2.426e-16 | 2.426e-16 |
| Return advection A_R | 300617/58982400 = 0.005096723768446181 | 0.003987486896944465 | -0.001109236871501716 |
| Lateral reaction torque T_D | -521/38400 = -0.013567708333333333 | -0.017385102536982960 | -0.003817394203649628 |
| Negative lateral stress torque C_D | 521/38400 = 0.013567708333333333 | 0.012088241226093310 | -0.001479467107240022 |
| Negative return stress torque C_R | 0 | 0.000151345186883575 | +0.000151345186883575 |
| Negative prescribed return torque G_R | 0 | 0 | 0 |

The exact continuum reaction is T_D*=-C_D*, obtained from the exact
momentum balance. It is not an assertion that the exact degree-seven field
is representable by the saved P2 coefficients.

At degree24, R_D=-0.017385102536983204 and R_F=-1.5973008506142692e-16.
Consequently M_D=-0.005296861310889651 and M_R=+0.00015134518688357518.
Their sum with R_F reconstructs delta=-0.005145516124005005 within the
unchanged 1e-12 identity convention. The physical gate is separately
0.0003759966274385022: the defect is 13.6850060573 times that limit.
The lateral term is 102.9413% of the signed defect; the return term offsets
2.8573% of the lateral magnitude. These percentages are decomposition
arithmetic, not causal percentages or acceptance thresholds.

Degree26 gives M_D=-0.005296861310889460,
M_R=+0.00015134518688357618 and R_F=1.2955131759029292e-15.
All six independently assembled scalar differences between degrees are at
most 2.3593e-16. The raw free-row L2 norms are 3.35585e-15 and 4.05262e-15.
Thus a large final free residual hidden by cancellation in R_F is also absent
in the saved evidence. The scalar identities agree within their recorded
roundoff limits, not necessarily bit for bit.

## What the lateral mismatch does and does not locate

Because the angular gradient is skew, the symmetric convective and viscous
volume contractions vanish; div(phi)=0. The actual conservative residual obeys

```text
R_h(phi) = S + B + A_R + G_R,
T_D - T_D* = (S-S*) + (B-B*) + (A_D-A_D*)
             + (A_R-A_R*) + (G_R-G_R*) - R_F.
```

The probe checks this second equation independently against the raw-array
reaction. The -0.00381739420365 reaction error is accounted for by storage
error -0.002708157332148085 and return-advection error
-0.001109236871501716, with the other terms at roundoff. The additional
-0.001479467107240022 lateral stress error produces M_D. R267's total traction
error -0.001328121920355432 is the lateral stress error plus the positive
return error. The sidecar therefore refines and agrees with R267's original
storage/advection/traction decomposition; it does not move all errors to a
single boundary formula.

As arithmetic controls, setting only M_R to zero leaves -0.00529686131;
replacing only C_D by its exact value leaves -0.00366604902; replacing only
T_D by its exact value leaves -0.00132812192. Each exceeds the original
recorded limit. These are diagnostic substitutions, not solutions of a
modified problem or recomputed acceptance decisions.

The source and saved arrays further establish:

- The angular test is exactly representable in P2 but is nonzero on the
  Dirichlet faces. Its fixed components are excluded from the homogeneous
  Newton test space. A converged eliminated residual need not give zero
  R_h(phi) or zero surface-stress defect. The raw-vector/scalar-action
  agreement now measures this distinction directly.
- The 240 fixed velocity indices agree with the lateral-node coordinates,
  and their final values agree with the exact affine lateral trace to
  8.89e-16. Node coordinates are checked against the n=2 quarter grid within
  1e-14 before boundary classification, because tabulation contains ulp-sized
  deviations from zero and one. This is a saved-coordinate check, not a new
  physical tolerance. Correct trace values do not enforce correct normal
  velocity derivatives or pressure stress on those faces.
- The exact velocity has spatial degrees (7,7,1) and pressure degree 2.
  P2/P1 cannot represent this pair exactly on any finite affine mesh. The
  maximum free velocity nodal error here is 0.01002059511, and the degree24
  angular endpoint error is -0.0003385196665185038. These corroborate nonzero
  approximation error; they do not prove a refinement rate or a source bug's
  absence. An exact affine trace does not remove interior approximation error.
- Both prescribed return tractions are normal. Since phi_z=0, G_R vanishes
  independently of P_minus/P_plus. Pressure also contributes zero to C_R;
  its measured nonzero torque is viscous shear. Changing a return pressure
  multiplier cannot directly correct this torque. Lateral stress still
  combines pressure and viscous terms; the sidecar does not separately
  measure them or individual lateral faces.
- R266 and R270 have identical saved raw diagnostics, multipliers and nonlinear
  histories. This supports treating the sidecar as observational for these
  runs. Degree agreement checks the same discrete state at two quadratures;
  it is not a mesh study or independent discretization validation.

The source review covers [the residual](../../verification/nonlinear_port/prototype.py),
[diagnostics](../../verification/nonlinear_port/diagnostics.py),
[final-state driver](../../verification/nonlinear_port/manufactured_driver.py),
[sidecar](../../verification/nonlinear_port/manufactured_angular.py) and
[exact fixtures](../../verification/nonlinear_port/fixtures.py).
No missing angular divergence correction, wrong traction sign, wrong face
partition, stale final state or erased-row reconstruction is demonstrated.
The existing tests and identities cannot exclude every shared source or
assembly error. No change of viscosity, load/history, residual definition,
solver, stress recovery or scientific gate follows from this result.

The distinction between stress integration and residual virtual-work reactions
also appears in the author's [FEniCSx reaction-force example](https://bleyerj.github.io/comet-fenicsx/tips/computing_reactions/computing_reactions.html).
That elasticity example is supporting numerical-method context. The fluid
identities and measured conclusions above come from this repository's source
and data, including boundary advection; the example does not validate R270.

## Precise blocker and next bounded task

**Blocker:** one coarse spatial solution with two integration rules does not
distinguish ordinary spatial stress/solution error from a common implementation
error, nor demonstrate that refinement meets the fixed physical budget.
R267's missing raw-residual/signed-partition blocker is resolved. Repeating the
same n=2 diagnostic or collecting another identical split would not answer
the new question. Replacing C_D by a reaction value would enforce the tested
identity by construction and discard the physical-stress question.

The next task is a **source-only design of a separate bounded n=4 spatial
comparison against the saved n=2 baseline**, with a precise implementation
contract or a concrete resource/evidence blocker. Retain Astra/high because
evidence architecture and the prospective scientific interpretation need review.
This is a proposed discriminator, not a claim that n=4 will pass or an admission
to run it. Do not implement it in this task.

The design must fix the following before recommending Sol/high implementation:

1. Keep t=dt=1/8, exact polynomial history, corrected BE forcing, fixture,
   P2/P1 spaces, conservative residual, boundary data, viscosity, quadrature
   pair, solver and physical gates fixed; change only spatial resolution in
   a separately versioned route. Compare original four-term budgets, errors
   against the exact reference and signed reaction/stress/return components.
   Separate a complete diagnostic comparison from a numerical PASS.
2. Specify a finite comparison table and interpretation for shrinking,
   unchanged, growing and inconsistent defects, including storage and
   advection errors. Two levels can test sensitivity and give one observed
   ratio; they cannot establish an asymptotic convergence rate. A later n=8
   point remains outside this proposed task and requires its own decision.
3. Resolve evidence scaling explicitly. n=4 has 2,315 bordered DOFs versus
   n=2's 405, exceeding the current latest-system 512-DOF bound. The existing
   driver, manifest/envelope and sidecar hard-code n=2 sizes (402 mixed,
   375/27 maps, 125 coordinates). Do not weaken those historical validators,
   silently omit a recorder, or merely change subdivisions. Specify a
   separately reviewed bounded evidence format and refusal tests that retain
   final-state provenance, free residual checks and independent angular
   actions. Source-only byte/entry estimates must include both quadratures.
4. Keep the existing whole-task memory/time/PID/thread/swap limits as the
   initial design constraints. R270's 486,866,944-byte peak and 9.22-second
   observed interval are n=2 observations, not n=4 resource guarantees.
   n=4 is below the 20,000 mixed-DOF ceiling, but that alone does not establish
   feasibility. A required cap or evidence-policy change must be explicit
   and justified for later review; retain a blocker if it cannot be justified.
5. Publish exact source changes, tests, evidence and stop rules needed for
   implementation. No manager, worker, numerical import/JIT/assembly/solve,
   admission, retry, full convergence/tank/B2, physical/render or Mac work.
   All ten allocations remain spent; any future launch needs a separate new
   source-reviewed admission after implementation and tests.

This provides a concrete way to investigate the remaining ambiguity without
inventing a repair. Alternate discretizations or equilibrated stresses would
change the numerical-method question and require separate justification.

## Preservation and validation

The [audit](evidence/r271/audit.json) verifies all 132 retained raw/caller files
against originals and Git-index bytes (116 older plus R270's 16), all 1,854
prior tracked evidence files unchanged, all 50 source bindings, 15 runtime
artifacts, four library resolutions and the archive/interpreter identity.
All ten reservations remain spent and their recorded PIDs/cgroups are absent.
No manager was contacted. R270's saved cleanup/resource record remains intact;
final save tails and independent parent wall interval remain unobserved, and
R229's setup resource predicate remains false.

The probe reproduces R246/R253 validator PASS and R266/R270 refusal under an
import guard with pinned Python 3.12.13. The 127 unchanged source/fake tests
and eight caller tests are reused from R269, not rerun. Two initial probe-only
errors were corrected: a missing binding argument to the alias validator,
then exact floating-point endpoint comparison during node classification.
The latter was fixed by verifying quarter-grid proximity before classifying
nodes. Neither error involved a reservation, manager, numerical import or
runtime source change. [Publication checks](evidence/r271/checks.json) record
AST/JSON, local links, append-only logs, sequential IDs, scope and whitespace.

Changed: this review and its probe/audit/check evidence, seven current status
pages, request/lifecycle logs and handoff. Unresolved: sole cause, spatial/time
convergence, lateral pressure/shear split, n=4 evidence/resource design, R242
cause and artifact-label origin. No validated manufactured solution or
physical-control result is claimed.

**Use `/new` before the next task**, because this interpretation and its
evidence are saved at a publication boundary. Select GPT-6 Astra/high, then
**Continue** for the design above. [Official OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-astra)
confirms high reasoning support; account availability is unverified and no
model/session switch occurred. Recommend Sol/high only once a narrow source
implementation contract is fixed; retain Astra/high for scientific or resource
policy decisions. Follow the [single handoff task](../../SESSION_HANDOFF.md#next-task).
