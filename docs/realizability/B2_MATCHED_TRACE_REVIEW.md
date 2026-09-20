# B2 geometry and resolution discrimination review

Completed 2026-09-20 for [R013](../../REQUEST_LOG.md#r013--2026-09-20--short-continuation-request)
against `568c68b`, following the [R012 method-review contract](B2_PHYSICAL_RESPONSE_AUDIT.md#next-bounded-task-design-a-geometry-and-boundary-layer-accuracy-test).
This is a method selection and experiment specification. **No new mesh, field
integration, reference evaluation, assembly or PDE solve was performed.** The
[evidence appendix](B2_MATCHED_TRACE_EVIDENCE.md) preserves source/report checks
and elementary scale calculations; it contains no new flow result.

## Decision and scope

Select **one fixed-polyhedron matched-trace experiment** on the existing 50 mm,
alpha=96 operator. Compare the current projected T_00c boundary command with
the full boundary trace of the known 128-term smooth-cylinder solution,
restricted to that same polyhedron. Evaluate the latter load at two prescribed
facet quadrature orders. Reuse one factorization, and integrate the disk
observable separately on each intersected cell.

The matched problem has a known continuum solution even on the faceted vessel.
Failure there would expose numerical approximation error without the continuum
boundary mismatch of the current reference comparison. The difference between
the two computed responses measures sensitivity to the boundary-data change
**at this discretization**. It is not, by itself, the continuum geometry error.
The distinction and possible cancellation are explicit below.

This fixture is a new, declared verification boundary condition. It is not a
replacement actuator, production solver or experimental command. Retain the
existing rest-Stokes equations, SIP form, spaces, physical parameters, signed
features, disk, phasor convention and acceptance thresholds. No volume force
is needed. The physical B2 gate remains failed and `campaign_ready=false`.
The selected experiment is **proposed, not executed**, and stops after this one
mesh or a failed prerequisite. A larger mesh is not a fallback.

## Three boundary problems

Write the physical complex velocity as U times a normalized field v. Use
R=0.10 m, H=0.15 m, nu=1e-6 m²/s, f=0.01 Hz, U=1e-7 m/s,
omega=2 pi f, and time dependence `exp(i omega t)`. All three problems obey

```text
i omega v - nu Laplacian(v) + grad(p) = 0
 div(v) = 0.
```

Pressure here is normalized kinematic pressure; a physical field is recovered
with the same U scaling as the existing backend. It is not an actuator pressure
demand estimate.

**S: smooth cylinder.** On r=R prescribe `v=w(z) e_theta`, where
`w(z)=(1-(z/H)^2)^2`; prescribe zero velocity on z=±H. Regularity at r=0
selects the nonsingular swirl. The independent infinite-series solution is
axisymmetric pure swirl, with constant pressure. The disk gain is the signed
linear feature

```text
J(v) = integral_D (x v_y - y v_x) dA / D0,
D = {z=0, x^2+y^2 <= d^2}, d=0.025 m,
D0 = integral_D (x^2+y^2) dA = pi d^4 / 2.
```

**P: current faceted vessel.** On each planar side facet F with normal n_F,
let `P_F=I-n_F n_F^T`. The declared continuum data are
`v=P_F[w(z)e_theta]`, with zero caps. Thus `v·n_F=0`. The discrete backend
imposes that normal condition strongly and the tangential data weakly. The
load is symbolic and facet-consistent, as documented in
[hdiv_stokes.py](../../realizability/backends/hdiv_stokes.py).

These are different boundary problems. On the interior of an inscribed facet,
r generally differs from R, `e_theta·n_F` need not vanish, and the smooth
solution's trace has a complex phase. The trace is not obtained by merely
replacing a radial normal with a facet normal. In particular, assigning only
`P_F v_S` while keeping zero normal trace does **not** make S an exact solution
on the polyhedron.

A refinement claim from P to S needs a sequence whose surface approaches the
cylinder, normals and boundary data approach the intended trace in an
appropriate norm, and discretization/load/output errors are separately
controlled. Refining the interior of a fixed polyhedron approaches its own
boundary problem. Regenerating a Gmsh cylinder at another nominal size changes
both geometry and discretization and does not isolate either error.

**A: matched trace on the same polyhedron.** Define v_* by the existing
**finite 128-term** reference, with no new truncation sweep:

```text
a_n = (n+1/2) pi,  k_n = a_n/H,
c_n = 16 (-1)^n (3-a_n^2)/a_n^5,
lambda_n^2 = k_n^2 + i omega/nu,
s_N(r,z) = sum_{n=0}^{127} c_n I_1(lambda_n r)/I_1(lambda_n R) cos(k_n z),
v_*(x,y,z) = s_N(r,z) (-y/r, x/r, 0),
v_*(0,0,z)=0,  p_*=0.
```

Use the scaled-Bessel evaluation already in
[swirl_reference.py](../../realizability/swirl_reference.py). The modified
Bessel equation gives
`(d_rr + r^-1 d_r - r^-2) I_1(lambda r)=lambda^2 I_1(lambda r)`;
therefore `nu*(lambda_n^2-k_n^2)=i omega`. Each term solves the homogeneous
Stokes equations, and the finite sum does too. This restriction argument is a
derivation here, using the [NIST Bessel equation](https://dlmf.nist.gov/10.25.E1).
There is no manufactured volume force or discrete residual forcing.

On **every exterior facet** prescribe the actual trace `v=v_*`. Caps are
analytically zero and should be set to zero exactly. Side facets generally
require both normal and tangential velocity, and both real and imaginary data.
Global flux is zero by divergence freedom. The exact disk remains inside the
polyhedron and has exactly the finite-series gain

```text
G_* = 2.0662858857221768e-5 - 6.595106312048072e-5 i  [1/m].
```

This is an exact continuum verification solution for the specified finite
series, not a claim that 128 terms give the infinite sidewall data exactly.
R009 found a sidewall truncation discrepancy around 1.23e-7 at z=0 despite
negligible observed central-gain sensitivity. Do not replace the fixture trace
with `w(z)e_theta`, its radial projection, or a zero-normal version.

## What the experiment can distinguish

Let G_P be the unknown continuum gain for P, and let G_Ph and G_Ah be the
computed gains using the same cell-aware disk functional. Apart from recorded
algebraic/output effects, the following complex identities hold:

```text
G_Ph - G_* = D_h + E_Ah,
D_h = G_Ph - G_Ah,
E_Ah = G_Ah - G_*,
D_h = (G_P - G_*) + E_Ph - E_Ah,
E_Ph = G_Ph - G_P.
```

E_Ah measures approximation error on a boundary problem with a known solution.
It includes the finite-element space, discrete normal-trace approximation,
load integration and remaining algebraic/output error. It is not purely an
interior interpolation error. D_h is a discrete response to changed boundary
data. Without control of E_Ph and E_Ah, D_h cannot be labelled the continuum
boundary-model error. Large terms can cancel, so report complex values and
magnitudes rather than percentages assigned to supposed independent causes.

A failed A comparison, after the loading/output checks, establishes that the
50 mm discretization is insufficient even with matched continuum boundary data.
A passing A comparison combined with a large D_h strengthens the reason to
investigate the declared boundary data, but does not prove that geometry alone
caused the original discrepancy. One successful output can result from
cancellation; no mesh convergence or production validation is inferred.

## Alternatives and resource reasoning

| Option | What it would test | Decision and limitation |
|---|---|---|
| Existing 3D form on a boundary-layer mesh | Spatial transmission at the physical frequency, retaining the full mode space | Defer. First separate fixed-surface refinement from improved cylindrical geometry; anisotropic cells require a new certificate and unknown LU memory. |
| Separate axisymmetric or radial diagnostic | Resolution of the smooth rest-swirl boundary layer without faceting | Affordable candidate for a later study, but a new discrete method; a pass would not explain the existing 3D operator or its projected boundary data. |
| Output-weighted residual/adjoint | Sensitivity of the chosen discrete disk gain to residuals and specified load changes | Defer. A same-space adjoint cannot estimate missing spatial/geometry error without enrichment or additional analysis, and still needs a reliable observation row. |
| Same 3D operator with matched boundary trace | Whether the existing space and boundary treatment reproduce a known physical-frequency solution on this exact polyhedron | Selected. Known operator size and homogeneous certificate; no continuum error allocation or refinement claim from one mesh. |

For the symmetry-restricted alternative the scalar equation would be
`i omega s = nu*(s_rr + s_r/r + s_zz - s/r^2)`, with `s=O(r)` on the axis,
zero caps and s(R,z)=w(z). Its weighted viscous energy contains
`integral (r*|grad s|^2 + |s|^2/r) dr dz`. A suitable conforming discretization
could retain positive dissipation directly, but would need its own derivation,
axis treatment and convergence evidence. The 3D mesh certificates would not
apply. Implementing that alternative now would not isolate P's model error.

For an adjoint of the existing real block system, `K^T z=l` yields
`l^T K^-1 delta_b=z^T delta_b` on compatible constrained vectors; real and
imaginary outputs require their appropriate rows. Essential lifts and pressure
nullspaces must be included. [PETSc supports transpose solves](https://petsc.org/release/manualpages/KSP/KSPSolveTranspose/),
but that capability alone supplies no continuous error estimate. R012 already
found the observed primal correction tiny; another algebraic residual calculation
alone has limited diagnostic value.

Elementary scales are delta=`5.641895835 mm`, (R-d)/delta=`13.29340388`, and
nominal h/delta=`8.86226925`. A delta/4 boundary spacing would be `1.410473959 mm`;
that is a design heuristic, not an accuracy guarantee. An illustrative 50 mm
straight chord in a 100 mm circle has sagitta `3.175416345 mm`, or 0.562828 delta.
This is **not a measurement of the Gmsh surface**, nor a bound on disk error.
It shows why nominal element length alone does not describe the geometry error
at this penetration scale. No chord geometry or mesh was generated in R013.

R012 measured 753.0508 MiB peak RSS and 38.7542 s for its complete audit;
its one factor/solve took 1.20193 s. The historical 25 mm run reached 6931.1 MiB
and 20 mm failed. None is a memory forecast for a refined or anisotropic mesh.
The selected fixture keeps the same 22,900 real block unknowns and factor
structure; only loads, prescribed values and observation evaluation change.
New facet integration and clipping cost is unmeasured, so a capped refusal is
an acceptable outcome. Do not increase the cap to make the fixture finish.

## Boundary discretization contract

This section specifies the new verification load only. Production code and P's
current symbolic RHS stay unchanged. The existing SIP bilinear form, mass terms,
pressure blocks and essential DOF **sets** are identical for P and A, so the
constrained matrix can be assembled/factored once. Nonzero essential values
change the lifting and RHS, including its pressure rows; they must not change K.
The [DOLFINx formulation](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_navier-stokes.html)
provides the strong normal trace and weak tangential treatment used here.

On each planar side triangle use the L2 projection of `v_*·n_F` into P2(F).
BDM2 has six normal-trace DOFs on a triangular facet; their moments and Piola
mapping are described by [DefElement](https://defelement.org/elements/brezzi-douglas-marini.html).
For physical normal traces psi_j of the six oriented facet basis functions,
solve the local six-by-six system

```text
sum_j [integral_F psi_i psi_j] c_j = integral_F psi_i (v_*·n_F).
```

This is boundary data projection, not a new global PDE or solver choice.
Apply the actual element DOF transformations and global facet orientation;
normal moments are not Cartesian nodal values. Interior velocity DOFs are not
prescribed. Use real and imaginary coefficients separately, zero caps, and
retain the projected normal trace gamma_h in the Nitsche target

```text
g_h = P_F v_* + gamma_h n_F,
L_F(test) = nu * integral_F [- (g_h tensor n_F):grad(test)
                          + alpha/h_K * (g_h tensor n_F):(test tensor n_F)].
```

The difference between gamma_h and the exact normal trace is a documented
boundary approximation in E_Ah. Never substitute the usual fixed interpolation
sampling for this projection without measuring its error. Do not interpolate
v_* into the trial space and manufacture `K*x_*` as a load: that would make the
check tautological.

Use tensor Gauss–Legendre orders **q=32 and q=64** on each triangle with the
Duffy map `x=A+xi*(B-A)+(1-xi)*eta*(C-A)`, xi,eta in [0,1], physical Jacobian
`|(B-A) cross (C-A)|*(1-xi)`. Apply that same rule to the projection RHS and
the weak load. Polynomial facet mass matrices can be integrated exactly at a
sufficient lower order. Evaluate only the existing 128 terms, in batches of
at most 256 physical points; one 128×256 complex128 array is 0.5 MiB, not a
bound on total process memory. Do not allocate all facets×points×terms together.

Both orders define loads on the same matrix; their output difference measures
load-quadrature sensitivity, not a certified boundary error bound. Before the
primal attempts, check each real/imaginary prescribed normal field's closed
flux ratio against the existing `1e-8` ceiling, with denominator the integrated
absolute normal flux (zero-over-zero is zero). Record the signed flux in SI.
Capture both pressure-constant RHS products **before** nullspace removal and
the removed vector norm. Require that removal changes the primal RHS by at most
`256*eps*||b||`; this is an arithmetic compatibility check, not a relaxed mass
balance condition. If either check fails, stop. No return-flow repair, pressure
forcing or changed trace is allowed to hide a fixture compatibility failure.

Before using the new local load code, verify its Piola/DOF orientation treatment
on all 24 vertex permutations of a reference tetrahedron and polynomial vector
traces spanning P2^3. On the checked physical mesh, compare representative
polynomial loads with ordinary UFL boundary assembly at `256*eps` times the
sum of absolute assembled contributions. This is RHS assembly validation only;
no extra PDE solves or factorization are permitted. Record all checks, including
any refusal before the physical attempt.

## Disk integration contract

The R012 last polar-rule change was 84.37 times the 5% reference scale. Merely
reusing that rule would leave the new comparison ambiguous. Keep the same
physical signed disk functional and add a separate cell-aware evaluation;
do not change `fem_observables.py` or the gate's default extractor.

On each affine tetrahedron, BDM2 velocity is a Cartesian vector polynomial of
degree two. On z=0, `x*v_y-y*v_x` is therefore a polynomial of degree at most
three. Intersect each tetrahedron with the plane and then with the **exact
circle**, retaining circular arcs. Integrate this polynomial on each resulting
region and sum. Do not replace the disk with a polygon, change its radius, or
sample across tangential jumps with a smooth-rule assumption.

Use dimensionless X=x/d, Y=y/d for the moment calculation. For a counterclockwise
region boundary and a+b≤3, Green's formula gives

```text
integral_region X^a Y^b dX dY
  = 1/(a+1) integral_boundary X^(a+1) Y^b dY.
```

Straight edges have polynomial integrands of degree at most four and admit
exact three-point Gauss integration. On a unit-circle arc, X=cos(theta),
Y=sin(theta), the integrand is `cos(theta)^(a+2) sin(theta)^b/(a+1)`.
Use analytic trigonometric moments, independently cross-checked with 16- and
32-point Gauss rules on arc pieces of length at most pi/4. These rules integrate
smooth **cell-boundary** functions; they do not cross a field jump. In exact
arithmetic this method integrates the discrete numerator exactly. Floating
point geometry, reconstruction and summation still require the checks below.

Recover each local polynomial from the element mapping or the fixed ten-point
quadratic tetrahedral stencil; do not fit to an arbitrarily thin plane cut.
Use DOLFINx evaluation with the known cell ID to check reconstruction at
additional cell-interior points. Verify area and moments through degree three
against the complete disk, and denominator `D0=pi*d^4/2`. Validate full disk,
quarter/half disk, known triangles, arc segments, polynomial rotation/strain,
a two-region polynomial jump, and vertex/edge tangencies before accepting data.
Check partition coverage, orientation, duplicate regions and all missing cells.

A plane coincident with an interior facet over positive area can have two
BDM tangential traces. Detect that case before assembly and **refuse** this
experiment if it intersects the disk; do not silently choose or average a trace
instead of the existing point evaluator's convention. Do not snap mesh vertices,
discard small cuts, move the disk or alter the geometry to avoid a degeneracy.
Unresolved clipping or polynomial-reconstruction inconsistency is a stop.

For each output, preserve the sum A_out of absolute coefficient×moment
contributions in gain units, reconstruction discrepancies and independent
arc-evaluation differences. Require arithmetic identities to agree within
`256*eps*A_out`, and require both this arithmetic scale and the independent
output difference to be no greater than `E5/100`, where
`E5=0.05*|G_*|=3.4556100991268897e-6 1/m`. The latter is a **diagnostic component
screen** (`3.4556100991e-8 1/m`), not a new physical acceptance threshold or a
rigorous error bar. No cancellation-adjusted tolerance may be tuned after seeing
a result. Preserve numerator/denominator and coordinate/U scaling explicitly.

Continue to report all six original signed features using the existing
(18,18,96) and (96,96,512) rules for each primary field, with both rule names.
Use the new disk integral as an additional diagnostic, not a silent replacement
of recorded values. For P, reproduce R012's default and finest disk gains with
their unchanged rules within its fixed arithmetic tolerance `2.4719806123e-13
1/m`; a mismatch stops the experiment before interpreting A.

## One executable next-task contract

Recommend **GPT-6 Astra, high reasoning** to implement a disposable runner and
execute this single experiment once. It includes numerical boundary loading,
cell-aware output integration and interpretation; it is not routine reporting.
Preserve the exact runner and compact evidence in the repository afterward.
No persistent backend, solver, form, mesh generator or gate API is changed.

1. Pin all 19 package/config hashes from the R012 appendix. Generate only the
   existing 50 mm mesh and verify hash
   `423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4`,
   482 cells, 9,522/1,928 V/Q DOFs and 22,900 real block unknowns. Recompute
   `calculate_local_bound(...,max_cells=500)`, require C_upper
   `58.12657123078638` within relative `1e-10` and positive guarded beta at 96.
   Preserve the 3,000-free-DOF dense guard; no dense global audit. This certificate
   covers the common homogeneous operator after lifting; it does not certify
   the accuracy of nonzero boundary data. Any changed mesh/form invalidates it.
2. Validate the watchdog with synthetic wall and two-process RSS tests. Validate
   the local load and disk kernels above before the physical attempt. Toy
   geometry/polynomial checks use no new physical mesh or PDE. Keep their parent-
   monitored execution within 60 s/512 MiB total; record that separate budget.
   All checks using the physical mesh belong to the physical-child budget below.
3. The physical child is parent-monitored from imports through all mesh checks,
   physical-mesh RHS validation, reference loading, solves, extraction and output:
   **180 s total wall time, 1.5 GiB active child-tree RSS**, nominal 0.05 s samples.
   Keep single-thread numerical libraries and the serial environment. Record peak
   observed RSS, process high-water RSS and maximum sample gap. These are stop
   limits, not a prediction of completion. No retry, cap increase or second mesh.
4. Use the unchanged `harmonic_response(config,'T_00c',0.01,0.05,
   penalty_factor=96,_return_fields=True)` for P, with the checked mesh returned
   by a disposable wrapper as in R012. Retain its K, forms, DOF sets, nullspaces,
   solver and factors. Assemble A_32 and A_64 **RHSs only**, with complete real/
   imaginary lifting and boundary values as specified above. Hash the matrix
   CSR/values, block layout and constrained sets before/after; require identical
   K and unchanged factor handle/state. No second bilinear form or factorization.
5. The successful-case inventory is exactly **three primary RHSs** (P, A_32,
   A_64), each followed by exactly **one same-factor residual correction**:
   one symbolic factorization, one numeric factorization, six matrix solves.
   Corrections have homogeneous essential increments because primary prescribed
   DOFs are explicitly set to their exact stored values before residual formation;
   require the constrained residual entries to be zero. Record this enforcement.
   Preserve uncorrected and corrected outputs; no refinement loop or extra solve.
   Use the R012 pressure compatibility, residual, block assignment, field scaling
   and `J(x+dx)-J(x)=J(dx)` checks. Preserve all PDE diagnostics, including the
   `1e-9` algebraic ceiling and the same correction self-consistency ceiling.
   For A, evaluate essential-normal residuals against its own real/imaginary
   projected traces, and weak tangential mismatches against its own complex
   target. Do not reuse P's zero-imaginary or zero-normal target diagnostics.
   Preserve the existing normalization and acceptance ceilings; identify every
   diagnostic's target explicitly in the report.
6. Compare uncorrected cell-integrated gains from both A rules with the same
   128-term G_*. Report absolute/relative complex error, relative magnitude error,
   wrapped phase error and the **unchanged strict 5%/5-degree** comparisons.
   Also report P against G_* as the still-mismatched physical comparison.
   An expected failed accuracy comparison is an outcome, not permission to run
   another case. Internal inconsistency or failed PDE checks stop interpretation.
7. Report `E_Ah`, `D_h` and their complex sum for both A rules. Require the sum
   identity at `256*eps` times the absolute-contribution scale. Record the load
   step `|G_A64-G_A32|` against `E5/10=3.4556100991e-7 1/m`, and each observed
   correction against E5/100. These additional component screens qualify the
   interpretation, not the physical gate. If one fails, report the diagnostic
   as unresolved; do not add quadrature orders, RHSs or corrective solves.
8. Preserve normals, normal-projection moments/fluxes, side/cap tangential
   mismatch, divergence, jumps and all six feature values with units. Record
   sampled boundary speed and displacement/acceleration scales for the fixture,
   clearly labelled as verification data; sampled maxima are not certified
   global bounds. P's physical actuator diagnostics remain those of the existing
   command. Force/power, pressure demand and hardware feasibility stay unassessed.
9. Write a strict finite JSON report and human interpretation, or an explicit
   partial/refused report with stage, completed counts, error and skipped work.
   Preserve source/mesh/matrix/runner hashes, versions, caps, timers, factor
   counters, validation fixtures and the fixed tolerances. Finish with one
   concrete next task, commit/push under `Continue`, and stop. No boundary-layer
   mesh, different penalty, adjoint, new reduced solver, gate integration,
   campaign, B3 or movie export follows automatically.

## Interpretation and stop table

| Observed outcome | Supported interpretation | Required stop |
|---|---|---|
| Identity, flux, orientation, clipping, arithmetic, PDE or resource check fails | The attempted diagnostic is incomplete or inconsistent | Preserve partial evidence; no automatic retry or method substitution. |
| Load/output/correction component screen fails | The comparison lacks the planned diagnostic precision | Report all available gains and failed screens, without allocating physical error. |
| A fails reference magnitude/phase with component screens met | Numerical approximation fails on this matched-boundary problem at physical nu/f | Investigate resolution/discrete trace error; do not blame continuum geometry alone. |
| A passes while P remains far from the reference | The discrete response is strongly sensitive to the boundary-data change | Review continuum model mismatch and convergence; do not declare geometry the sole cause. |
| Both pass | One mesh and two related boundary fixtures agree at the measured output | No campaign readiness, refinement, penalty robustness or hardware claim. |

The normal-trace projection error and a rigorous bound on the remaining
quadrature/algebraic error remain unknown even if the component screens pass.
The proposal is a discriminating test, not a promised complete error budget.
The exterior preparation/sensing and realistic-movie goals in
[STATUS.md](../../STATUS.md) still require later validated flow calculations.

## R013 validation and model continuity

R013 only checked the embedded R012 report/runner hashes, all 19 unchanged
source/config identities, existing evidence provenance and elementary scales.
It derived the restriction, error identities and polynomial moment formula;
no proposed kernel, trace projection, disk integration or solve was implemented
or executed. Documentation checks cover links/anchors, fenced Python/JSON,
source immutability, stored scalar consistency and `git diff --check`. The full
application, optional FEM/dense tests, simulations, rendering and encoding are
outside this review and were not run.

The next task retains Astra/high. If it later exposes an understood mechanical
instrumentation fix, recommend **GPT-5.6 Luna, medium**, with exact edits,
focused checks and a stop before numerical interpretation; otherwise retain
Astra/high for one bounded scientific question. Availability was rechecked on
2026-09-20 in the session catalog and fetched
[official Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages using the
OpenAI Docs skill. Account/client access can differ. No switch, delegation or
automation occurred. R013 stops at this specification; the next prompt is
**Continue**.
