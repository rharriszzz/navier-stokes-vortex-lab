# R267 — Manufactured angular balance source review

2026-09-26 (America/New_York), PC/WSL `daisy` retains ownership.
**R266 remains INCOMPLETE; all nine allocations remain spent. No corrective
change to the PDE, solver or acceptance threshold is justified by this review.**
The saved failure is a genuine failure of the prescribed surface-stress budget.
It is compatible with a converged coarse Galerkin solve: the angular virtual
velocity is excluded by the homogeneous lateral test boundary condition, and
the solved equations do not enforce this surface-stress balance exactly.
This explains why the small Newton residual is not contradictory. It does
not prove that approximation error is the sole runtime cause.

The remaining blocker is specific: saved evidence cannot separate lateral
reaction/stress mismatch from return traction mismatch or independently check
the final uneliminated angular residual. A bounded evidence repair is specified
below. No runtime source is changed and no new attempt is admitted here.

## Saved arithmetic and exact reference

The [probe](evidence/r267/probe.py) and [result](evidence/r267/probe.json)
rederive R255's rational reference, rebuild the entire R266 report from its
raw inputs, reproduce the validator refusal, and validate the latest saved
linear system without importing numerical libraries.

| Signed rate term | Exact field | R266 degree 24 | Discrete minus exact |
|---|---:|---:|---:|
| Storage | 0.0003125 | -0.002395657332148085 | -0.002708157332148085 |
| Advection | 0.005096723768446181 | 0.003987486896944711 | -0.001109236871501470 |
| Traction | 0.013567708333333333 | 0.012239586412977900 | -0.001328121920355432 |
| Body | -0.018976932101779514 | -0.018976932101779531 | -1.7347e-17 |

The exact sum is zero. The discrete sum is **-0.005145516124005005**,
13.6850060573 times the unchanged 0.0003759966274385022 limit. The four
term errors reproduce that defect. Storage error alone exceeds the gate;
the observed defect is not localized solely to traction by this table.
Degree 26 gives -0.005145516124007139; the largest individual degree difference
is 2.329733628236852e-15. Pair agreement tests integration consistency, not
coarse solution accuracy or absence of common errors.

The independent angular endpoint identity passes. The interval defect is
-0.0006431895155006188 = dt times the rate defect to 6.84e-18 at degree24;
degree26 agrees to 1.66e-17. Both failures express the same imbalance, not
two independent fault mechanisms. R266's u L2 error is 0.00294019303,
H1 seminorm error 0.04201093401, div u L2 0.02876423357 and return traction
L2 error 0.07768475243. R255 intentionally imposed no coarse approximation
error gate, but retained the 1% signed budget gate. These errors never imply
a budget PASS, convergence, or physical attainability.

## Source identities and the excluded test

Write phi=(-y,x,0), S=int(phi.dtu), B=-int(phi.f_BE),
A_X=int_X(phi.u)(u.n), and C_X=-int_X phi.(sigma_h n).
D denotes the four lateral Dirichlet faces and R the two returns. Let
G_R=-int_R phi.t_prescribed with t_prescribed=-P_s n+g_s.
All signs follow the actual source, so positive C means negative physical
torque. The physical diagnostic is

```text
delta = S + B + A_D + A_R + C_D + C_R.
```

In [build_forms](../../verification/nonlinear_port/prototype.py), momentum
uses conservative convection, symmetric stress, corrected BE load and exact
polynomial history. Its raw, unscaled, uneliminated residual evaluated on
the mixed test (phi,0) satisfies

```text
R_h(phi) = S + B + A_R + G_R,
delta   = R_h(phi) + A_D + C_D + C_R - G_R.
```

The volume convection contraction vanishes because u tensor u is symmetric
and grad(phi) is skew. The viscous contraction and div(phi) vanish too.
This holds even when div(u_h) is nonzero. The exact rational non-solenoidal
control u=(xy,yz,zx), p=x+y+z closes the conservative angular identity;
adding an angular divergence term introduces -5/72. Thus the observed nonzero
divergence is not evidence of an omitted angular divergence term. Energy has
different contractions and already includes its two divergence terms.

[field_forms](../../verification/nonlinear_port/diagnostics.py) implements
all four angular terms with these signs and physical sigma=-pI+0.2D(u).
[step_forms](../../verification/nonlinear_port/cube_adapter.py) and
[run_manufactured](../../verification/nonlinear_port/manufactured_driver.py)
route the exact history/corrected load to both degrees and install the final
accepted state before diagnostics. Body torque's agreement with the exact
reference supports this routing. R264's balanced evaluation has not been
shown to cause the discrepancy; no counterfactual compiled run was made.

Although phi is exactly representable in P2, it is nonzero on every lateral
face and is not in the homogeneous velocity test space. The solver enforces
the free rows. [border_and_lift](../../verification/nonlinear_port/sparse.py)
replaces 240 fixed rows with identities and sets their residuals to zero.
Consequently 3.903967951178561e-15 is the norm of the **scaled, eliminated**
residual. It does not bound R_h(phi) or the physical surface-stress defect.
The probe gives two different raw fixed-row residuals with the same retained
system, proving that this information is lost by elimination.

This is the familiar distinction between a reaction calculated from residual
virtual work and one integrated from the computed stress. The author's
[FEniCSx reaction-force example](https://bleyerj.github.io/comet-fenicsx/tips/computing_reactions/computing_reactions.html)
demonstrates it in elasticity. The fluid identities above are derived from
this repository's conservative residual, including boundary advection;
the elasticity example is supporting context, not validation of this run.
The pinned [DOLFINx 0.10 PETSc assembly API](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.fem.petsc.html)
provides vector assembly separately from boundary-condition application.

For this fixture, the exactly affine lateral lift gives A_D=0 after all four
faces are summed. The prescribed return traction is purely normal and phi_z=0,
so G_R=0 regardless of the two pressure multipliers. These are source/rational
facts, not newly assembled measurements. Therefore the saved moments imply
R_h(phi) approximately -0.017385102536982906 at degree24, whereas total
physical torque is -0.012239586412977900. Their difference is delta. This
inferred action is **not** an independent residual measurement.

The return traction norm supplies only the Cauchy bound
abs(C_R-G_R) <= sqrt(4/3)*traction_L2_returns = 0.08970262546.
It exceeds the whole defect and gives no signed split. The raw latest-system
state is before correction 3, not the final state; its fixed rows are already
eliminated, and mesh/DOF coordinates and raw final residual are not saved.
Do not solve that matrix again, identify its state as final, or invent a
reaction split from this record. A source bug elsewhere is not ruled out.

## Fixed next source contract: record the missing angular evidence

The next task is an evidence-only implementation, **not a numerical-method
repair or a proposal to replace the failed gate with a tautological reaction
balance**. Keep the current four physical angular terms, original 30 diagnostics,
all gates, manifest, numerical envelope and old validators unchanged. Implement
the following bounded sidecar and source/fake tests, then stop for Astra/high
review before any new admission. Minor helper factoring is allowed.

1. Add an injected `manufactured_angular.py` helper and pure reducer/validator.
   Use the existing final accepted state, same n=2 mesh, P2/P1 ordering,
   exact history/load, degrees24/26 and original residual form. Assemble raw
   residual vectors directly through the existing vector assembly machinery,
   before lifting, row elimination or scaling. Do not instantiate another
   Jacobian assembler or call a solver. For degree26 explicitly install the
   final P_minus/P_plus/eta in its newly created Constants before assembling
   its residual; the existing diagnostic forms do not use those Constants.
2. Build a mixed Function Phi=(phi,0), using the collapsed velocity space and
   its parent map to interpolate (-y,x,0), with pressure entries zero. Never
   guess interleaved DOF ordering or apply the solution's fixed trace to Phi.
   Save its complete 402 coefficients, velocity/pressure parent maps and
   velocity interpolation-node coordinates sufficient to verify Phi, the
   final 405 state values, sorted fixed indices/values, and both raw 402-entry
   residual vectors. Preserve the existing source binding, mesh receipt,
   degrees, dt, step, time and precise final-state semantics in the sidecar.
3. At each degree independently assemble six scalar forms: A_D, A_R, C_D,
   C_R, G_R and `residual_action=action(original_residual,Phi)`. C uses
   sigma_h from the final field; G uses the prescribed offsets and installed
   multipliers. Sum exactly tags1–4 or5–6 as specified. Retain form/assembly
   receipts and log markers, including measured zeros. Do not substitute the
   rational zeros for A_D or G_R. No interior-facet or alternate-stress method
   is required by this contract.
4. With a_i=Phi_i and raw r_i, recompute R_D=sum_fixed(a_i r_i) and
   R_F=sum_nonfixed(a_i r_i) using `fsum`. Pressure weights are zero. Save
   all raw inputs and these derived quantities:

   ```text
   reaction_torque_D = R_D + A_D
   lateral_mismatch = reaction_torque_D + C_D
   return_mismatch = C_R - G_R
   reconstructed_defect = lateral_mismatch + return_mismatch + R_F
   ```

   Independently compare (i) A_D+A_R with original angular.advective,
   (ii) C_D+C_R with original angular.traction, (iii) R_D+R_F with assembled
   residual_action, (iv) residual_action with S+B+A_R+G_R, and
   (v) reconstructed_defect with the original physical defect. Use the existing
   identity convention max(1e-12,128*epsilon*sum_abs_terms) for each equality;
   record inputs, defect, limit and result. These are evidence-consistency
   checks, not new scientific acceptance thresholds. Record R_F at both
   degrees without assuming it is zero; only degree24 was solved. A nonzero
   mismatch is useful evidence and must not be corrected or discarded.
5. Add an optional injected sidecar recorder callback to `run_manufactured`
   for source-test compatibility. The actual manufactured worker must supply
   it, bound to its run directory/source identity. Assemble and save the
   sidecar after the final state and the existing diagnostics are available,
   before returning the numerical envelope. Use `angular_audit.json`, schema1,
   strict finite JSON, exclusive creation, and a 262,144-byte cap. Unknown or
   missing keys, bool-as-number, duplicate keys, nonfinite values, wrong sizes,
   maps/coordinates/fixed values/state/multiplier aliases, altered cached
   reductions or receipts must refuse. Save finite measured evidence even
   when consistency or physical checks fail; record the failure. Do not let
   a sidecar success change the original numerical decision. Keep the old
   `linear_system.json` recorder intact. Do not modify historical envelopes
   to pretend they contain this evidence.
6. Focused injected-fake tests must distinguish raw/scaled/eliminated vectors,
   nonzero fixed/free angular contributions, prescribed/physical traction,
   cap/lateral partitions and final/pre-correction states. Include degree26
   constants with distinct nonzero final values, nontrivial parent maps,
   two independent scalar/vector action paths, wrong sign/omitted A_D or R_F
   controls, failure/size/duplicate/finite JSON cases, callback ordering and
   worker persistence on the existing physical INCOMPLETE path. Reuse R267's
   exact identities and four decomposition controls. R246/R253 saved PASS and
   R266 saved refusal must reproduce; run the existing 118 source/fake tests
   under the numerical import guard plus the new focused tests.

The sidecar's exact schema, helper API and checks must be published with tests.
The subsequent Astra/high source review must decide how a **new, separate**
diagnostic admission binds and requires it, with the original outer/resource
caps and original physical gates. There is no caller/allocation in the next
implementation. Extra JIT/runtime cost and whether the new evidence separates
the cause remain unmeasured. A failed old physical budget remains INCOMPLETE
even if all new consistency identities pass. Any proposed threshold, mesh,
residual/stress definition or acceptance change requires a later explicit
scientific decision; no such change is selected here.

## Preservation, checks and handoff

The [audit](evidence/r267/audit.json) verifies all 19 R266 originals and Git
index copies, 97 older originals/index copies, 47 unchanged source bindings,
eleven artifacts/four resolutions/archive/interpreter, nine spent reservations
and absent recorded worker PIDs/cgroups. All 1,801 previously tracked evidence
files remain unchanged. Saved R246/R253 validators replay PASS; R266's full
report rebuilds and refuses. R255's reference and negative controls reproduce.
The source probe additionally checks the excluded test, conservative identity,
information loss and four decomposition negative controls. No numerical module
was loaded. Existing 118 tests are reused from R265 because runtime source is
unchanged; they were not rerun. Publication checks cover AST/JSON/local links,
append-only logs, request/lifecycle IDs, scoped files, index inclusion and
whitespace. No manager, worker, new attempt, JIT, assembly, solve, full
convergence/tank/B2, physical/render work or Mac transfer occurred.

**Next: use `/new`, select GPT-6 Sol / high, then Continue** for the fixed
evidence-only source implementation above. The review and source contract are
saved at a bounded task boundary; no current context percentage was supplied.
Recommend Astra/high afterward for review and a separate admission decision,
or immediately if a scientific choice is encountered. [Official OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-sol)
confirms Sol supports high reasoning; account access is unverified and no
model/session switch is claimed. Follow the [single handoff task](../../SESSION_HANDOFF.md#next-task).
