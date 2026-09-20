# B2 scalable stability method review

Prepared 2026-09-20 for [R005](../../REQUEST_LOG.md), against source commit
`21676b96ced6c2372fc8ca350c9650a90960fe3a`. This completes the method review
requested by the [diagnostic handoff](B2_CONTINUATION_REVIEW.md#2026-09-20-implementation-result).
Only documentation changes are delivered. Calibration used disposable scripts
and the existing backend on the 100 and 70 mm fixtures.

## Decision and scope

Implement a **sufficient local coercivity diagnostic** as the next bounded
package. It can establish positive dissipation without a global eigenproblem.
Its failure means **inconclusive**, not unstable. Retain sparse constrained
eigenanalysis with inertia counts as a reviewed alternative when this
sufficient bound is inconclusive; its larger-mesh cost and numerical safeguards
need a separate review before implementation.

Keep the current rest Stokes model, BDM2/DG1 spaces, affine tetrahedra,
facet-consistent loads, physical viscosity/frequency, and existing acceptance
thresholds. No production linear solver, penalty, mesh, or actuator design is
selected. The physical B2 gate remains failed, actual response-mesh stability
remains `not_assessed` in the gate, and `campaign_ready` remains false. Preserve
the dense audit's 3,000-free-velocity-DOF guard.

## Mathematical target

Use the matrices assembled by the current `sip_viscosity_form`, with all
homogeneous exterior normal-trace velocity DOFs eliminated. Let M be the
positive velocity mass matrix, A the real symmetric viscous matrix including
nu, and B the divergence matrix. The target is

```text
lambda_min = min { v^T A v / (v^T M v) : v != 0, B v = 0 }  [1/s].
E_kinetic = 0.5 v^T M v
dE_kinetic/dt = -v^T A v
```

Strict positivity gives exponential energy decay for the homogeneous,
semidiscrete rest-Stokes problem. It does not certify physical response
accuracy, load consistency, continuum convergence, nonlinear stability, or
reachability. Each mesh/operator needs its own evidence. Boundary commands
change the lift and right-hand side; this diagnostic addresses the homogeneous
operator shared by those commands.

The sufficient method below establishes positivity on the entire broken P2
velocity space, hence also on its homogeneous-normal, divergence-free
subspace. It returns an energy-norm coercivity margin, **not a numerical lower
bound on lambda_min in 1/s**. Obtaining such a rate would additionally require
a mass-to-energy bound. A negative unconstrained velocity direction alone
would not prove constrained Stokes instability.

## Sufficient certificate from four-by-four cell matrices

This derivation applies to the exact form in
[`hdiv_stokes.py`](../../realizability/backends/hdiv_stokes.py). On affine
tetrahedra, BDM2 velocities are vector P2 polynomials and their gradients are
P1. The formulation and element pairing are consistent with the
[DOLFINx reference](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_navier-stokes.html).
The following bound is derived here for this repository's diameter weights.

Write the homogeneous form as `a(v,v)/nu = G - 2 C + alpha J`, where

```text
G = sum_K integral_K |grad(v)|^2
J = sum_interior_F (1/h_F) integral_F |jump(v)|^2
    + sum_boundary_F (1/h_K) integral_F |v tensor n|^2
C = sum_interior_F integral_F avg(grad(v)) : jump(v)
    + sum_boundary_F integral_F grad(v) : (v tensor n)
h_K = cell diameter; h_F = (h_Kplus + h_Kminus)/2.
```

The weighted Cauchy inequality gives `|C| <= sqrt(D J)`, with
`D = sum_interior h_F ||avg(grad(v))||_F^2 + sum_boundary h_K ||grad(v)||_F^2`.
Using `|avg(X)|^2 <= (|Xplus|^2 + |Xminus|^2)/2` assigns weight `h_F/2`
to each interior cell trace and weight `h_K` to each exterior trace.

For the four barycentric P1 basis functions on cell K, form

```text
M_K = volume(K)/20 * (I_4 + ones_4x4)
T_K = sum_faces_of_K weight(K,F) * S_KF
S_KF[i,j] = area(F)/12 * (1 + delta_ij) if both vertices lie on F,
           0 otherwise.
c_K = lambda_max(T_K, M_K).
```

Thus `D <= C_tr G`, where `C_tr = max_K c_K`; the scalar trace inequality
applies separately to every gradient component. These are dimensionless
constants. Uniform length scaling leaves them unchanged.

For a conservative bound without a local iterative solver, define

```text
P = I_4 - (1 - 1/sqrt(5))/4 * ones_4x4
W_K = (20/volume(K)) * P T_K P
C_upper = max_K max_i sum_j abs(W_K[i,j]).
```

P is the inverse square root of `I + ones`, so W_K is a symmetric whitening
of the generalized problem. Its maximum absolute row sum bounds its largest
eigenvalue. This proves `C_tr <= C_upper` in exact arithmetic. If
`alpha > C_upper`, then

```text
beta = 1 - sqrt(C_upper/alpha) > 0
a(v,v) >= nu * beta * (G + alpha J).
```

To see this, set `x=sqrt(G)`, `y=sqrt(alpha*J)` and apply
`2*x*y <= x*x + y*y`. On a connected mesh with all exterior facets penalized,
`G + alpha J` vanishes only for v=0: G forces cellwise constants, interior
jumps match those constants, and the exterior term removes the remaining
constant. This establishes strict positivity without constructing B or Z.

The proof requires every facet, including the caps; the actual arithmetic
mean of adjacent **cell diameters**, not a facet diameter; positive volumes;
affine geometry; constant positive nu; and the current full SIP form.
Changing any of these requires another review. An implementation must reject
unsupported geometry/forms instead of applying this formula by analogy.

## Calibration against existing dense fixtures

All ten dense cases and the five targeted 70 mm backward-Euler steps were
rerun. The mesh hashes match the older review. Rates reproduce the recorded
values to the digits shown; there is no contradictory calibration result.

| Mesh (m) | alpha | Dense minimum rate (1/s) | Sufficient bound |
|---:|---:|---:|:---|
| 0.100 | 6 | -0.0838845803371 | inconclusive |
| 0.100 | 12 | -0.0559664829022 | inconclusive |
| 0.100 | 24 | -0.00312520956158 | inconclusive |
| 0.100 | 48 | +0.00185910664480 | inconclusive |
| 0.100 | 96 | +0.00200938619304 | positive |
| 0.070 | 6 | -0.0341772362200 | inconclusive |
| 0.070 | 12 | -0.000917893895442 | inconclusive |
| 0.070 | 24 | +0.00163460031658 | inconclusive |
| 0.070 | 48 | +0.00168736418397 | positive |
| 0.070 | 96 | +0.00175832058384 | positive |

| Mesh | Cells | max c_K | C_upper | beta at 48 | beta at 96 |
|---:|---:|---:|---:|---:|---:|
| 100 mm | 82 | 49.2511028937 | 56.0371901177 | no certificate | 0.2359838154 |
| 70 mm | 171 | 31.0969737326 | 36.7200957987 | 0.1253560748 | 0.3815333494 |

The 100 mm alpha=48 and 70 mm alpha=24 cases demonstrate conservatism:
positive dense spectra can coexist with an inconclusive bound. Do not raise
alpha merely to make this diagnostic pass.

Every cell's analytic trace constant was compared with independently
assembled DG1 mass/trace forms using UFL CellDiameter and facet integration.
The maximum relative discrepancy was `5.24e-15`; the largest local generalized
eigenpair residual was `6.09e-16`. This checks geometry, face incidence,
diameter averaging, and the interior factor of one half.

Across the dense cases, maxima were `4.33e-12` for projected eigenpair
residual, `7.30e-16` for projected symmetry error, `1.83e-14` for dimensionless
divergence, `7.34e-15` for exterior normal L2 trace, and `1.48e-15 /s` for
direct Rayleigh-quotient discrepancy. All five independent steps met the
existing prediction/residual checks. At alpha=6 the measured energy ratio
was `1.072025523823309`; at alpha=48 it was `0.996633794049131`.
Agreement for the growing mode is verification evidence of instability.

The full calibration took 46.86 s and peaked at 796.06 MiB RSS. A separate
process measuring only mesh creation and local calibration with warm caches
took 0.117 s inside the script and peaked at 196.74 MiB. Imports and cold JIT
can add time. These are measurements on this environment, not guarantees.

## Sparse constrained eigenanalysis and spectrum coverage

The competing method retains the exact constrained target. After checking the
constant-pressure nullspace, remove one dependent pressure row to give a
full-row-rank B_r of rank m, then use

```text
K(sigma) = [ A - sigma M   B_r^T ]
           [ B_r              0 ]
n_negative(K(sigma)) = m + number of constrained eigenvalues below sigma.
```

This identity follows by splitting velocity into a basis of ker(B_r) and
a complementary space: the constraint/complement block contributes m positive
and m negative directions. It requires full row rank and shifts away from
eigenvalues. A pressure gauge removes redundancy; it must not relax the
divergence constraint. Check the full B residual after reconstructing a mode.

A sparse symmetric indefinite factorization at sigma=0 can count **all**
negative constrained eigenvalues. Zero pivots, singularity, pivot
perturbations, unexpected rank, or sensitivity to scaling/tolerances make the
result inconclusive. Once zero negative directions and no null directions
are established, positive shifts can bracket the first eigenvalue. For an
unstable operator, expand a negative bracket until its lower endpoint counts
zero eigenvalues; then bisect the first change in count. A few eigenpairs
near zero alone cannot provide this coverage: shift-invert changes spectral
ordering, as described by [SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.eigsh.html).
The full saddle pencil has a singular pressure mass block and must not be
treated as an ordinary positive-mass generalized eigenproblem.

Small-fixture calibration used PETSc's symmetric MUMPS factorization and
[MatGetInertia](https://petsc.org/release/manualpages/Mat/MatGetInertia/).
It set `ICNTL(13)=1` and enabled null-pivot detection with `ICNTL(24)=1`.
The [MUMPS FAQ](https://www.mumps-solver.org/index.php?page=faq) explains why
parallel root processing can otherwise undercount negative pivots. This is
calibration of an alternative diagnostic, not selection of a response solver.

On the 100 mm fixture, n_free=1,260 and m=327. At alpha=6, the factorization
returned inertia `(394, 0, 1193)`, hence **67 negative constrained modes**,
matching the complete dense spectrum. At alpha=48 it returned
`(327, 0, 1260)`, hence none. For each penalty, shifts `lambda_min +/- 1e-7 /s`
changed the constrained count from zero to one, also matching the dense
spectrum. Six counts agreed; factorization calls took 0.035–0.554 s each.
No 70 mm sparse count or response-mesh factorization was run.

Before a future sparse result could certify a new mesh, require repeat counts
under pressure-gauge choice, diagonal congruence scaling, and tighter pivot
settings, with all solver diagnostics recorded. Reconstructed modes must meet
the existing `1e-9` eigenpair/solve residual, `1e-10` divergence/normal trace,
and `1e-10 /s` direct quadratic-form checks. For the mixed eigenpair use
`||Av+B_r^T p-lambda Mv||/(||Av||+||B_r^T p||+|lambda| ||Mv||)` and report
full-B compatibility separately. Retain the targeted unforced step.
Those safeguards and larger-mesh costs have not been calibrated here.

## Resource budget and interpretation

The chosen local method requires O(cells + facets) geometry storage and fixed
four-by-four work per cell; it requires neither a global velocity matrix nor
a dense divergence nullspace. The existing response inventory contains
482/873/1,842/3,154 cells at 50/40/30/25 mm. Linear extrapolation of the warm
171-cell calibration suggests roughly 0.14/0.24/0.51/0.88 s for the local
calculation, with geometry/import/JIT overhead additional. A conservative
planning estimate is **under 10 s warm and 0.5 GiB total RSS** at those sizes.
This is an estimate; those meshes were not evaluated in R005.

For the next implementation, run only 100, 70, and 50 mm meshes. Impose a
500-cell limit, a 120 s wall-time limit, and a 1 GiB RSS stop limit in the
verification runner. Stop and record incomplete evidence if any cap is hit;
do not increase limits automatically. Check the cell limit before building
per-cell diagnostic arrays. The optional dense regression remains separate,
with its existing 3,000-DOF guard, a 180 s/1.5 GiB verification budget, and
no dense call at 50 mm. Use a parent-process watchdog for wall time/RSS;
post-run RSS reporting alone does not enforce a cap.

Sparse factorization can have substantial fill and pivoting costs. The small
factorization times above do not provide a defensible production peak-memory
estimate. The 25 mm gauge-reduced saddle matrix would already have 66,255
unknowns. A future sparse proposal must measure symbolic estimates and a
bounded smaller-mesh factorization before allocating larger factors. This
uncertainty is another reason to try the local sufficient bound first.

## Bounded follow-on implementation

Recommend **GPT-5.6 Luna, medium reasoning** to package the explicit local
calculation above. Availability was rechecked in the
[official model guide](https://learn.chatgpt.com/docs/models) on 2026-09-20;
Luna and Astra are listed for Codex, subject to client/account access. The
effort recommendation is this project's judgment. No model switch occurred.

1. Add a separate optional `b2-coercivity` diagnostic and JSON/Markdown report;
   do not wire it into `b2-gate` in this package. Use the existing cylinder
   generator, alpha=48/96 defaults, and 100/70/50 mm evaluation under the caps
   above. Keep numerical geometry helpers NumPy-only where possible and
   DOLFINx imports optional. No new heavy dependency is needed.
2. Implement M_K, T_K, W_K and the absolute-row-sum bound exactly as specified.
   Require finite positive inputs, affine tetrahedra, valid face adjacency,
   a connected mesh, and all exterior facets. Reject cells with
   `volume/diameter^3 <= 1e-12` as unsupported numerical geometry. Use
   `C_safe = C_upper + 1e-10*max(1, C_upper)` and accept only
   `1-sqrt(C_safe/alpha) > 1e-8`. These are conservative arithmetic guards for
   a new diagnostic, not changes to physical B2 thresholds. Record them.
   Floating-point evaluation is a numerical certificate under these guards,
   not a rigorous interval-arithmetic proof.
3. Report `certified_positive`, `inconclusive`, `invalid`, or `resource_limit`
   with reasons. For inconclusive cases, stability is unknown: do not emit
   `unstable=true`, invent a decay rate, or automatically change alpha.
   Record the tested mesh hash, config, form/source hashes, dependency versions,
   cell/facet counts, worst cell, C_upper/C_safe, beta, units, timings, and
   peak RSS. Preserve strict JSON; invalid numeric fields become null.
   Include `campaign_ready=false` and the independent physical-accuracy blocker.
4. Validate analytic P1 masses against independent quadrature, uniform scale
   invariance, vertex permutations, interior/boundary weights, invalid and
   nearly degenerate cells, and refusal before allocating over-cap arrays.
   Independently compare every cell's trace eigenvalue with UFL assembly on
   100/70 mm (`<=1e-12` relative disagreement). Reproduce this review's
   positive/inconclusive classifications at alpha=6/12/24/48/96. Preserve the
   negative dense control and the stable-but-inconclusive counterexamples.
   The sufficient bound has no iterative convergence test; full four-by-four
   spectra, assembly comparison, and existing dense residuals supply the
   calibration. Finer mesh agreement is not its acceptance criterion.
5. Run ordinary realizability discovery, optional B2 discovery, CLI help, and
   the new three-mesh diagnostic. Check report contents, strict JSON, resource
   refusals, and unchanged gate/readiness semantics. Record optional dependency
   skips honestly. No harmonic pilot, physical reference rerun, production
   factorization, or new dense response-mesh solve belongs to this task.
6. Update the log, this review's implementation-result section, project status,
   and handoff; commit/push under the next `Continue` authorization. **Stop**
   after the diagnostic and checks. Recommend **GPT-6 Astra, high reasoning**
   to interpret the 50 mm result and decide the next actual-mesh stability or
   physical-accuracy task. If only an understood mechanical defect remains,
   recommend Luna/medium with that exact fix and a check/stop condition.

Stop earlier if independent calibration contradicts the bound, prerequisites
do not hold, or progress requires a form, boundary, physical-parameter, or
threshold change. A 50 mm inconclusive result is a valid deliverable; record it
for research review rather than expanding this package into sparse analysis.

## Evidence and reproducibility

The [calibration appendix](B2_SCALABLE_STABILITY_CALIBRATION.md) preserves the
exact disposable script, numerical records, source hashes, and reproduction
instructions. Local full evidence is in
`/tmp/navier-b2-stability-method-r005/{dense,local,local_cost,provenance}.json`.
Those temporary paths are not needed by a fresh clone. No production response
operator was assembled; sparse matrices above are small calibration fixtures.

For this documentation review, checks comprise the ten dense cases, five
targeted steps, 253 independently assembled local trace comparisons, six sparse
inertia comparisons, strict-JSON/evidence consistency, local links/anchors,
fenced-block syntax, and `git diff --check`. Ordinary application suites,
rendering, and encoding checks are not rerun because their source is unchanged.
