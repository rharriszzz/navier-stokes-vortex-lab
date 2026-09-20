# R021 compatibility review and revised matched-trace contract

Recorded 2026-09-20 for [R021](../../REQUEST_LOG.md#r021--2026-09-20--short-continuation-request),
starting from `e96f81b`. This completes the
[R020 saved-data review](B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md#next-bounded-task-review-compatibility-and-specify-a-revised-fixture).
The [evidence index](B2_COMPATIBLE_TRACE_INTEGRATION_EVIDENCE.md) links the
reproducible arithmetic, identity checks and validation.

## Decision

Specify **one future matched-trace comparison with fixed Duffy orders 64 and
96**, retaining the finite 128-term reference, the same facet L2 projection
and weak load, and every R013 acceptance threshold. Require P and both A RHS
compatibilities before any primary solve or factorization. A failed check
ends the attempt. The new orders are a prospective integration prescription;
they do not rescue the failed q=32 result or establish that q=64 is accurate.

Higher fixed quadrature is the selected first experiment because it preserves
the existing, tested projection/load construction. Saved q=64 flux motivates
testing it but supplies neither an assembled compatibility result nor an
output error bound. Order 96 provides a predeclared higher comparison with
2.6 times the old pair's boundary point count, versus 4 times for 64/128.
Neither factor predicts total runtime. No adaptive order selection, third
order or fallback method is permitted after a result.

An alternative based on shared vector-potential edge moments can preserve
closed flux structurally. Its derivation and additional obligations are below.
It is deferred because it introduces new moment evaluation and orientation
code while tangential-load accuracy would still need checking. This decision
changes only a disposable verification fixture, with no production solver,
actuator, reduced-state, sensing or boundary-physics choice.

**No new mesh, FEM assembly/solve, reference evaluation, quadrature evaluation,
toy execution or integration-method implementation occurred in R021.** The
physical B2 gate remains failed and `campaign_ready=false`.

## What the saved moments establish

All 19 pinned production identities and 433 R014–R020 historical evidence
files match the starting commit. R020's standard-library auditor passed with
its output redirected into R021. All 564 facet records were checked: 200 side
and 82 cap facets at each order, identical facet/cell/orientation identifiers
and normals, unit normals, positive saved Gram matrices and exactly zero cap
moments, coefficients and fluxes.

For every real and imaginary saved projection, `M c = m` holds within
`256*eps*(sum_j |M_ij*c_j| + |m_i|)`. The largest residual/tolerance is
0.004412. Both orders' Gram matrices agree within the absolute-contribution
arithmetic screen (maximum difference/tolerance 0.019568). This checks the
six-by-six projection arithmetic; it does not validate the integrals in m.
BDM facet DOFs represent normal polynomial moments, consistent with the
[element definition](https://defelement.org/elements/brezzi-douglas-marini.html).

Using only the saved q=64 Gram matrices gives

```text
||gamma_32 - gamma_64||²_L2(boundary) = sum_F delta_c_F^T M_64,F delta_c_F
```

for each real/imaginary component of normalized velocity. The norms are
`3.7597913613e-10` and `7.1902835500e-13 m`; divided by the corresponding
q=64 norms, the steps are `1.3433188732e-8` and `1.6209118858e-10`.
These describe a change in the discrete normal projection, not its error
against the exact trace or its effect on the central response. No full weak
load vectors were archived, so tangential-load differences cannot be recovered.

Summing the saved SI facet fluxes reproduces the report within the fixed
absolute-contribution scale. There is small rounding from the different order
of SI scaling and summation; q=64's real sum is `-1.16510e-25 m³/s` from
per-facet SI values versus the report's `-1.14895e-25 m³/s`. Relative error
against such a cancelled net sum would be misleading. The sum of absolute
real facet fluxes is about `5.39476e-10 m³/s`. The integrated absolute flux is
larger because a single facet can contain both signs. Integrating its absolute
value is not a polynomial-exact operation even when gamma is polynomial.

The archive does not contain the basis integrals `integral_F psi_j`, so this
review cannot independently reconstruct each signed flux from the saved
moments. The mass equations, flux totals and source path are separate checks.
It also lacks full A RHSs and solution vectors; no new assembled compatibility
or velocity recovery is inferred.

## Why the two compatibility screens differ

Let gamma be the projected normalized normal trace, U=`1e-7 m/s`, and let
Phi be the signed SI boundary flux. R013's two screens are:

```text
|Phi_real| / integral |U gamma_real| dS < 1e-8
|Phi_imag| / integral |U gamma_imag| dS < 1e-8

||b_before - b_after_pressure_projection||_2 <= 256 eps ||b_before||_2
```

The first is a relative closed-flux check. The second limits how much of an
incompatible RHS may be removed as arithmetic noise. Neither replaces the
other, and no fixed equivalence applies across meshes, normalizations or RHSs.

The pinned pressure space is discontinuous P1 Lagrange; its basis sums to one
on each cell. A pressure coefficient vector of ones therefore represents a
constant. The direct helper normalizes that vector in Euclidean coefficient
norm, giving `sqrt(nq)=sqrt(1928)=43.9089968002`, separately in the two pressure
blocks. This is not a volume-weighted pressure norm. With pressure row
`-integral q div(v)`, zero unlifted pressure load and normal extension g,
lifting changes that row to `+integral q div(g)`. Interior normal fluxes cancel
for H(div) functions. Thus, in exact assembly arithmetic,

```text
z_real^T b = Phi_real / (U sqrt(nq))
z_imag^T b = Phi_imag / (U sqrt(nq)).
```

The two normalized pressure vectors have disjoint support and are orthogonal,
so the norm of their removed component is the Euclidean norm of these two
products. The saved removal agrees with that interpretation. In the current
code, `make_lifted_rhs` validates the block vector, loads all four blocks,
applies full lifting, reverse scatters and assigns boundary entries before
checking compatibility. Pressure has no essential DOFs, so boundary assignment
does not discard pressure lifting. The installed-version
[DOLFINx lifting implementation](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/_modules/dolfinx/fem/petsc.html#apply_lifting)
uses block metadata and the complete form array; the R017 oracle already
exercised those couplings.

| Saved A_32 quantity | Real | Imaginary |
|---|---:|---:|
| Signed SI flux (m³/s) | 2.571353564e-19 | 2.336108895e-22 |
| Closed-flux ratio | 3.039618866e-10 | 1.648596316e-12 |
| Flux-predicted pressure product | 5.856097272e-14 | 5.320342219e-17 |
| Measured pressure product | 5.856082051e-14 | 5.322894013e-17 |
| Absolute prediction discrepancy | 1.522111646e-19 | 2.551793757e-20 |

The prediction discrepancies are below the unchanged `256*eps` absolute-flux
arithmetic scales. At A_32's actual `||b||=0.0928905451291`, the arithmetic
limit is `5.28021616498e-15`, equivalent, through the identity above, to a
**combined** SI flux norm of `2.31848994693e-20 m³/s`. The individual ratio
ceilings would be at most `2.74071e-11` and `1.63616e-10`; both components
still share the combined budget. A_32 therefore passes the `1e-8` screen but
needs 11.0906 times the allowed removal. These translated numbers explain this
case; they are not new thresholds for the future RHSs.

Q=64's flux-only predicted products are `-2.616664387e-20` and
`6.244807720e-21`. Its assembled RHS norm, products and required removal
remain unmeasured. Better flux cancellation is a reason for a new fixed
comparison, not permission to bypass that measurement. The evidence supports
finite-order trace integration as the q=32 failure mechanism. It does not
establish a total quadrature error bound or exclude future assembly defects.

## Alternative: preserve flux through shared potential moments

This is a derivation for review, not implemented code. Use R013's c_n, k_n and
lambda_n and define a single smooth potential throughout the polyhedron:

```text
A = a(r,z) e_z
a(r,z) = -sum_(n=0)^127 c_n I_0(lambda_n r)
                         / (lambda_n I_1(lambda_n R)) cos(k_n z).
curl(A) = v_*.
```

The radial derivative uses `d I_0(x)/dx = I_1(x)` from the
[NIST recurrence and derivative identities](https://dlmf.nist.gov/10.29).
Direct differentiation gives `curl(A)=(partial_y a,-partial_x a,0)` and the
same full finite-series swirl, including its regular axis limit. No new
truncation, forcing or boundary return flow is introduced.

For a scalar polynomial phi on an oriented planar facet, Stokes' theorem and
the product rule give the weighted moment identity

```text
integral_F phi (v_* . n) dS
 = integral_boundary(F) phi A . t ds
   - integral_F (grad_F(phi) cross A) . n dS.
```

Choose a P2 moment basis containing phi=1. Its area term is zero. Evaluate each
geometrical edge integral once in a canonical global orientation, and use the
same value with opposite signs in its two boundary facets. The closed-surface
sum of constant moments then cancels algebraically, up to final floating-point
summation. This preserves the divergence-free flux identity even with finite
edge quadrature. It does **not** make individual facet fluxes exact. Caps stay
analytically zero; the potential vanishes there and horizontal edge tangents
have zero z component. Shared edge incidences and orientations require checks.

All six P2 moments, not just a scalar flux total, must be evaluated and mapped
to the oriented physical BDM basis. The other five moments include area terms;
both those terms and the tangential weak load still need independent
integration checks. The polynomial mass system and Nitsche target must use
the resulting same gamma. A global subtraction from gamma or from pressure
rows would be a different, disallowed repair. Altering just one coefficient
to make the sum zero would not implement the weighted identity above.

This route could reduce compatibility failures without very high face orders,
but needs stable scaled I0 evaluation, canonical edge sharing, polynomial
weight derivatives, orientation tests and comparisons of all moments and
loads. Shared cancellation can conceal inaccurate individual integrals, and
the assembled pressure screen is still mandatory. Its added implementation
and error-analysis scope is why it is deferred. Failure of the selected fixed
pair triggers another recorded decision; it does not automatically authorize
this alternative or increasing orders.

## One subsequent experiment contract

**GPT-6 Astra, high reasoning:** implement and validate a new disposable
runner based on the exact R020 sources, then, only if all prerequisites pass,
make at most one physical attempt. Completion is a complete comparison or a
finite refusal report at the first failed check/resource/decision boundary,
followed by evidence audit, continuity update, scoped commit/push and stop.

1. Preserve old evidence and all 19 production/configuration pins. Retain the
   [R013 physical problem, boundary projection and disk contract](B2_MATCHED_TRACE_REVIEW.md),
   its exact 482-cell mesh hash, V/Q DOFs 9522/1928, 22900 real unknowns,
   alpha=96, 500-cell local certificate cap and 3000-free-DOF dense guard.
   Require `C_upper=58.12657123078638` within relative `1e-10` and positive
   guarded beta. No second mesh, changed form, pressure normalization or solver.

2. Replace the old pair by **(64,96)** everywhere in the disposable matched
   load/diagnostic/report path. Use the existing 128-term target, exactly zero
   caps, the same Duffy map and q for both normal projection and weak load,
   six oriented normal coefficients, and `g_h=P_F v_*+gamma_h n_F`.
   Preserve the kernel's polynomial mass calculation and batching of at most
   256 target points. No method changes to the kernel are needed. The kernel
   retains per-facet basis/gradient chunks, so its memory still grows with q²;
   batching the reference evaluator does not bound total memory. Retain only
   needed facet/report data and release completed diagnostic temporaries.

3. Move the complete RHS compatibility barrier into P's direct helper **before
   its first `nullspace.remove(vector)`**, where K, a, b, spaces, offsets and
   normalized pressure vectors already exist, but KSP/factors do not. Use the
   existing source-pinned trace/observer technique with an explicit once-only
   guard; fail if its unique anchor or captured layout differs. Validate P on
   a copy, then build A_64 and A_96 through the actual repaired full lifting
   helper, checking constraint sets, block offsets and matrix digest/state.
   Check both flux ratios and each fully assembled candidate's real/imaginary
   pressure products and removal norm. Stop immediately on the first failure;
   later candidates then remain unmeasured. If all pass, retain the checked A
   vectors and allow the original P helper to proceed. Do not reassemble A
   after P or construct a second bilinear matrix. This avoids spending a P
   solve on a candidate already known to be incompatible.

4. Record raw RHS hashes, norms, products and proposed removal **before**
   applying anything to an accepted RHS. Measure removal on a disposable copy;
   refuse above `256*eps*||b_raw||`. A refused raw candidate remains untouched.
   Only accepted candidates may receive the existing arithmetic-sized
   nullspace removal. Verify orthonormal pressure vectors, zero velocity
   support and the pinned pressure-block normalization; test the pressure
   nullspace against K and its transpose before trusting solvability products.
   No extra factorization/solve is involved. Persist each candidate's layout
   separately. Record completed RHS assemblies, attempted and returned solves,
   corrections, and PETSc factor/solve events separately; a prepared RHS is
   not a returned solve. On a pre-solve refusal factor and solve counts are zero.

5. Before physical execution, retain all five prerequisite phases, correct-
   root execution from a shallow directory, wrong-root refusal, parent refusal
   and synthetic wall/two-process RSS stops. Keep the existing 24 tetrahedron
   permutations and 30 spanning P2 vector traces at their prescribed cheap
   toy orders. Add q=64 and q=96 on all faces of one nondegenerate skew toy
   tetrahedron for two complex polynomial traces: a divergence-free affine
   rotation with nonzero normal data and a quadratic P2 vector trace. Compare
   projection and weak load with the independent polynomial/interpolation/UFL
   oracle at the unchanged `256*eps` absolute-contribution scale. Require the
   target callback to receive at most 256 points; preserve disk/arc/jump and
   tangency/reconstruction checks. No physical reference evaluation on toys.

6. Exercise the **actual pre-solve observer and preparation helper** with the
   pinned harmonic BDM2/DG1 block form on a reference tetrahedron, including
   nonzero complex divergence-free polynomial normal data and the existing
   independent full block lifting oracle. Test compatible P/A/A preparation,
   then a deliberate incompatibility in P, first A, and second A separately;
   inject one normalized pressure component above its computed fixed limit
   into a copy solely for these refusal tests. At the successful pre-solve
   barrier raise a labelled toy sentinel before KSP setup, so no toy PDE solve
   or factorization occurs. Verify the observer fires once, every expected
   layout/matrix invariant, failed raw vectors unchanged, distinct finite
   stages, and zero factor/solve events for all cases. Also retain missing
   metadata, wrong offsets and synthetic lifting-error coverage. Do not use
   a stubbed callback as the only test of this reordered path.

7. The entire prerequisite sequence, including imports and failed launches,
   remains parent-monitored under **60 s / 512 MiB cumulative**. Use the approved
   serial MPI environment with single-thread libraries. The sole physical child
   has **180 s / 1536 MiB active child-tree RSS**, nominal 0.05 s samples, from
   imports through all extraction/reporting. Record observed peak, process
   high-water RSS and maximum sample gap. The old boundary pair used 5120
   points/facet; this pair uses 13312. Existing 59.97 s/757.00 MiB is context,
   not a forecast. No cap increase, retry, extra order or second physical child.

8. On success use the unchanged P harmonic-response call and one common
   factorization for P, A_64, A_96 and exactly one same-factor residual correction
   each: **three primary RHSs, three correction RHSs, one symbolic and one
   numeric factorization, six matrix solves**. Check matrix digest/state and
   factor handle/state throughout. Set essential primary values to their stored
   targets before residual formation; constrained correction RHS entries must
   be exactly zero. Preserve primary/corrected residuals and correction
   self-consistency `<1e-9`, own-target A divergence `<1e-3`, essential residual
   `<1e-14`, pressure/jump/side/cap diagnostics and original P PDE checks.

9. Preserve all R013 output checks: exact-circle cell integration, reconstruction,
   independent arc rules, coefficient-times-moment absolute scale,
   `J(x+dx)-J(x)=J(dx)` at `256*eps*A_out`, both original six-feature polar rules
   (18,18,96) and (96,96,512), and P reproduction within `2.4719806123e-13 1/m`.
   For P and both A fields report uncorrected/corrected gains and correction,
   complex error, relative magnitude and wrapped phase against unchanged
   `G_*=2.0662858857221768e-5 - 6.595106312048072e-5 i 1/m`. Strict magnitude
   `<5%` and phase `<5 degrees` remain physical-reference comparisons. Retain
   `E5=3.4556100991268897e-6 1/m`, output/correction component screens `E5/100`
   and load-step screen `|G_A96-G_A64|<=E5/10`. Report `E_Ah=G_Ah-G_*` and
   `D_h=G_Ph-G_Ah` with the unchanged complex sum-identity screen. A failed
   accuracy/component screen is an outcome, with no added solve or order;
   failed arithmetic/PDE checks stop interpretation immediately.

10. Save sources/hashes, versions, normals, projection moments/coefficients,
    signed/absolute fluxes, raw and accepted RHS hashes, compatibility and
    operator records before solve, exact stage/counts and finite partial JSON
    on failure. Preserve physical-mesh UFL polynomial-load checks, partition
    checks and all units/normalizations. Record fixture sampled speed,
    displacement and acceleration as sampled verification scales. Force/power,
    pressure demand, hardware limits, preparation, sensing and movie flow stay
    unassessed or unresolved. An accurate A result would establish one matched
    output on this discretization, not continuum geometry error, a total FEM
    error floor, campaign readiness or hardware feasibility.

Keep the gate failed. No certificate integration, campaign, B3, refinement,
adjoint, reduced solver, rendering or encoding follows. If implementation
reveals a new scientific choice or an unexplained numerical failure, archive
the refusal and stop before the physical child. An understood mechanical
defect may be fixed within the unexhausted toy budget; preserve every attempt.

## Review completion and model continuity

R021 archived reproducible saved-data arithmetic and reaudited historical
evidence. Validation covers identities, request-history preservation, finite
JSON, script syntax and documentation links. Full application/FEM tests,
numerical prerequisites and the proposed experiment were deliberately skipped.
R012 remains the last complete physical response audit. R020 remains the
latest physical attempt; its P gain and failed A_32 screen are unchanged.

Retain **GPT-6 Astra/high** for the subsequent implementation, prerequisites,
one conditional attempt and interpretation. Recommend **GPT-5.6 Luna/medium**
only if the remaining task becomes a fully specified mechanical fix with
focused checks and a stop before physical interpretation; otherwise retain
Astra/high for the next bounded numerical question. Both models are in the
current session catalog. OpenAI Docs was used to fetch official
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) effort support.
No switch, sub-agent or automation was launched. **Next prompt: Continue.**
