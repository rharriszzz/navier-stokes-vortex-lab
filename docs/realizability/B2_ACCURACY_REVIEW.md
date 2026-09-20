# B2 physical-response accuracy and error-floor review

Completed 2026-09-20 for [R009](../../REQUEST_LOG.md#r009--2026-09-20--short-continuation-request)
against `f7f522b`, following the [R008 contract](B2_RESPONSE_COERCIVITY_RESULT.md#next-bounded-task-physical-accuracy-and-error-floor-investigation).
The [evidence appendix](B2_ACCURACY_EVIDENCE.md) preserves the exact calculation,
compact results, source identities, and watchdog records. No numerical source,
configuration, physical threshold, or gate changed; no mesh or PDE was computed.

## Result and decision

**The smooth-cylinder reference is numerically reproducible far below the
physical comparison scale. The current three-dimensional response error floor
is still unknown.** Small reference quadrature differences do not bound the
error of a piecewise-polynomial FEM field, its boundary loading, or its geometry.
The historical alpha=6 response cannot establish the repaired backend's accuracy.

Select one proposed follow-up: a **single 50 mm, alpha=96 physical T_00c
response audit**, with feature-quadrature sensitivity and one algebraic residual
correction using the same factors. Its purpose is to measure the repaired
operator's discrepancy and distinguish observable algebraic/quadrature effects
from the remaining combined geometry/loading/spatial error. It is a diagnostic
fixture, not a refinement sequence or a production penalty selection. The
[bounded contract below](#one-proposed-experiment-and-next-task) is the next task;
no harmonic response was run in R009.

Retain R=0.10 m, H=0.15 m, nu=1e-6 m²/s, f=0.01 Hz, U_probe=1e-7 m/s,
the signed features and fixed 0.025 m disk, exp(i omega t), and the current
facet-consistent target. The physical B2 gate remains failed and
`campaign_ready=false`. Alpha=96 has only the mesh-specific R008 stability
certificates; alpha=48 remains inconclusive. The default 500-cell local guard
and 3,000-free-DOF dense guard are unchanged.

## Response scale and comparison geometry

The [independent derivation](B2_NEXT_STEPS.md#independent-reference-for-the-tangential-pilot)
reduces the axisymmetric, periodic, rest-Stokes swirl to a cosine/Bessel series.
For d=0.025 m, its signed disk feature is

```text
G = Omega_hat/U = (4/d^4) integral_0^d r^2 v(r,0)/U dr   [1/m]
G = 2.0662858857221768e-5 - 6.595106312048072e-5 i        [1/m]
|G| = 6.911220198253779e-5                               [1/m]
arg(G) = -72.60391709725774 degrees
|Omega_hat| = U_probe |G| = 6.911220198253778e-12         [1/s]
```

The Bessel-integral identity follows from the modified-Bessel derivative
relations in [NIST DLMF](https://dlmf.nist.gov/10.29). The implementation uses
[SciPy's scaled `ive`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.special.ive.html)
with the real exponential scale restored in each ratio. Unscaled `iv` is also
finite for this bounded 128-term case and provides an evaluation cross-check;
both use SciPy special functions, so they are not independent libraries.

The disk fit is not solid-body motion. Its equivalent edge speed d|Omega| is
`1.727805049563445e-13 m/s`, while the actual reference |v(d,0)| is
`3.20648574939432e-13 m/s`. Neither is a PIV detection threshold. No sensor
noise, exposure time, estimator uncertainty, or physical detectability is
inferred. Phase is wrapped and does not give an unwrapped transport delay.

For a nonzero reference G and e=G_h-G, elementary complex geometry gives

```text
||G_h|-|G|| <= |e|
|arg(G_h/G)| <= asin(|e|/|G|), when |e| < |G|.
```

Thus a proven |e| below `0.05 |G| = 3.4556100991268897e-6 1/m` would
suffice for both existing comparisons: magnitude error below 5% and phase
below 2.865984°, hence below 5°. At the physical command this error scale is
`3.4556100991268893e-13 1/s`. The phase-only sufficient scale is
`sin(5°)|G| = 6.023525296714254e-6 1/m`.

These are implications, **not a replacement complex-error acceptance rule**.
The existing test separately requires strict magnitude error <5% and phase
error <5°. A pair approaching both allowed limits can have complex error
approaching `7.0789027735646575e-6 1/m` (10.2426% of |G|), so the
5%-complex-error ball is sufficient but not necessary. For mesh/quadrature
comparisons the current code divides by the second/finer gain's magnitude;
reference comparisons divide by |G|. Agreement between approximations does
not certify agreement with G. No new near-zero cutoff is introduced.

## Measured reference sensitivity

All calculations used only 32/64/128 terms and at most 512 points in each
integrated coordinate. The polar checks reuse `_polar_rule`, `fitted_rotation`,
and the signed annular Fourier helper with analytic swirl values; they do
not invoke FEM point location or evaluate a FEM field.

| Check | Observed absolute difference or ratio |
|---|---:|
| 32 → 64 → 128 disk series | 0 at returned float64 precision |
| 128 coefficients versus 512-point independent integration | 2.88658e-15 maximum coefficient difference |
| Disk gain using integrated rather than closed-form coefficients | 2.18948e-19 1/m |
| Scaled versus unscaled Bessel evaluation | 1.10310e-19 1/m |
| Radial integration, orders 12/18/24/64/128/256/512, all three term counts | at most 1.37363e-18 1/m |
| Existing low/default/high polar rules: 12×64 / 18×96 / 24×128 | at most 2.99385e-19 1/m |
| Extended polar rules 64×256 / 128×512 | at most 1.09508e-18 1/m |
| Sum of absolute series terms / magnitude of sum | 1.052330785 |
| Absolute radial integral / magnitude of integral, 512 points | 1.172881659 |
| Spurious annular m=4 tangential feature, all polar rules | at most 3.68878e-22, dimensionless |

The reference's smallness is mainly spatial attenuation, not severe cancellation
in these two sums. Reverse-order and `math.fsum` series reductions gave the same
returned gain here. The largest observed integration difference is about
`1.99e-14 |G|`, or `3.98e-13` of the 5% absolute scale. Higher quadrature order
is not monotonically more accurate once roundoff dominates. These are observed
sensitivities, not interval bounds on Bessel evaluation, quadrature, or the
infinite tail. All methods share the series model; agreement cannot validate
the faceted 3D boundary problem. The 128-term sidewall value at z=0 differs
from its exact unit target by about 1.23e-7, despite the much smaller central
disk sensitivity; boundary and central truncation errors are distinct.

## Quantitative error budget and unknowns

A useful accounting identity inserts intermediate problems:

```text
G_report - G_smooth =
  (G_report - G_h_exact_output)          algebraic and output evaluation effects
  + (G_h_exact_output - G_faceted)       FEM/load-integration discretization
  + (G_faceted - G_smooth)               geometry and declared boundary-model difference.
```

Here G_h_exact_output means exact integration of the exact solution of the
assembled discrete equations; G_faceted means the continuum solution with the
current facet-projected command on that polyhedron. Neither intermediate is
available in the stored evidence. This decomposition supplies no numerical
upper bound, and the terms need not have the same complex phase.

| Contribution | Evidence and absolute scale | What remains unknown |
|---|---|---|
| Smooth reference truncation/evaluation | 0 series change; up to 1.374e-18 1/m observed cross-check spread | Rigorous total reference bound, including common special-function error |
| Algebraic residual and roundoff | Historical T_00c relative residuals 8.16e-13 to 2.71e-12; unit command solved before physical scaling | Current alpha=96 residual, output conditioning, and absolute disk error; machine epsilon alone is no bound |
| Observable cancellation and quadrature | Smooth-field cancellation ratios 1.052/1.173; smooth feature checks above | Actual FEM quadrature error, cancellation, cell-location effects and tangential jumps across disk cuts |
| Boundary load integration/enforcement | Current source projects the symbolic smooth command onto each planar facet, with zero essential normal trace for T_00c | Load integration error and weak tangential mismatch at the physical frequency; trace norms alone do not bound disk error |
| Faceted geometry and target change | G_smooth and G_faceted solve different boundary problems | Absolute disk error from faceting/projection; R008 hashes identify meshes but do not quantify shape error |
| Spatial resolution | delta=5.641896 mm; nominal h/delta=8.862/7.090/5.317/4.431 for 50/40/30/25 mm | Boundary-normal spacing, phase/amplitude dispersion, and output convergence of the repaired solver |
| Total current physical-response error | No repaired physical alpha=96 response has been measured | No defensible numerical floor or resolved phase yet |

The harmonic solver first solves for a unit boundary velocity and then multiplies
all fields by U_probe. Feature gains divide by U_probe again. The physical
`~1e-12 /s` response does not itself imply loss of representability in float64.
The residual reported by `_block_direct_solve` is `||b-Kx||/||b||` after pressure
nullspace projection, in coefficient Euclidean norms for a mixed system. For a
scalar observable row l and compatible inverse, its algebraic error is
`l^T K^(-1) r`; a small relative residual alone says nothing quantitative about
that absolute output without the inverse action or an appropriate bound.
Coercivity beta is not that output bound, a condition number, or a decay rate.

FEM polar integration crosses piecewise-polynomial cells and tangential jumps.
Smooth analytic quadrature convergence therefore cannot be transferred to it.
A refined polar sum may measure sensitivity without proving the integral is
accurate. Likewise, a boundary trace norm can be large where the central
observable has little sensitivity, or small while a sensitive error remains.
An adjoint or controlled refinement would be needed to weight these effects.

For scale interpretation, delta=sqrt(2 nu/omega)=5.641895835 mm, and R-d
spans 13.2934 penetration lengths. The previously proposed delta/4 spacing is
1.410474 mm; this is a mesh-design heuristic, not convergence evidence. The
nominal h values are not measured boundary-normal cell widths. The smooth
profile at R-delta and R-2delta has normalized magnitudes 0.377943 and
0.143086, respectively. Transmission through many penetration lengths makes
accumulated spatial error a plausible concern, not a demonstrated diagnosis.

The historical artifact is explicitly the pre-repair alpha=6, dirty-`ab268b2`
run (hash retained in the appendix), not evidence from the current form:

| Mesh | Absolute complex error (1/m) | Error / abs(G) | Error / (0.05 abs(G)) |
|---:|---:|---:|---:|
| 40 mm | 0.07583412009549 | 1097.260946 | 21945.21891 |
| 30 mm | 0.02070992177556 | 299.656518 | 5993.13035 |
| 25 mm | 0.01820411337240 | 263.399412 | 5267.98824 |

These total discrepancies are vastly larger than reference sensitivity. They
cannot be split into independent error terms or attributed to current alpha=96
stability, geometry, or loading. The historical physical gate stays failed.

## Alternatives considered

| Experiment | Useful evidence | Limitation and decision |
|---|---|---|
| One certified 50 mm primal solve, feature sweep and residual correction | Current total reference discrepancy; observed quadrature and algebraic output changes; same existing equations and factors | Selected below; cannot separate continuum geometry from spatial error or prove refinement convergence |
| Discrete adjoint on the same certified operator | `K^T z=l` gives output-weighted residual and load sensitivity; transpose solves are supported by [PETSc](https://petsc.org/release/manualpages/KSP/KSPSolveTranspose/) | Requires correct FEM observation rows, block layout, constraints and pressure gauges; a same-space adjoint alone cannot estimate missing discretization error. Defer pending the simpler audit |
| Boundary-layer mesh with the current 3D form | Directly investigates resolution and geometry, retaining the full physical mode space | New anisotropy changes trace bounds; needs mesh identities, new certificates and factor-memory measurements. Do not infer cost from geometry-only R008 |
| Axisymmetric r-z or separated radial boundary-layer discretization | Affordable smooth-cylinder accuracy study at physical nu/f, isolating radial attenuation | A new diagnostic method; pure swirl omits faceted geometry/projection and general modes. Existing analytic reference already settles smooth response scale. Defer as a possible later cross-check, not a replacement backend |

The historical 25 mm direct run peaked at 6931.1 MiB and the 20 mm allocation
failed. R008's 2.6918 s/184.5 MiB geometry study gives no factorization estimate.
The 50 mm inventory has 9,522 velocity and 1,928 pressure DOFs per phasor part,
or 22,900 total block unknowns before essential constraints; that is a size
inventory, not a prediction of LU fill. A refusal under the cap below is a valid
result and does not justify increasing it or moving to 40 mm.

## One proposed experiment and next task

Recommend **GPT-6 Astra, high reasoning** to implement, run once, and interpret
this single-case diagnostic in a disposable runner. Numerical interpretation
and correct capture of the mixed residual still warrant this effort. Preserve
its exact text and compact evidence in the repository afterward. This contract
is a proposal for the next continuation, not work executed in R009.

1. Pin the 19 package/config hashes in the R009 appendix and the current SIP,
   mesh, boundary and feature implementations. Read the four root research
   documents, this review, R008 and the R005 method assumptions. Generate only
   the existing 50 mm geometry. Before global assembly require 482 cells,
   9,522/1,928 V/Q DOFs and hash
   `423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4`.
   Recheck `calculate_local_bound(domain, max_cells=500)` and the existing
   classification helper, with
   C_upper=58.12657123078638 (relative agreement <=1e-10), and positive alpha=96
   beta. Ensure the identity-checked mesh is the one subsequently assembled.
2. Use exactly `harmonic_response(config, 'T_00c', 0.01, 0.05,
   penalty_factor=96, _return_fields=True)`. Do not call `b2-gate`, alter its
   defaults, add comparison penalties, normal modes, or any other mesh. Retain
   the physical command and symbolic facet-consistent load. Record all existing
   PDE, boundary, jump and actuator diagnostics. A disposable mesh-generator
   wrapper must return the already checked domain/tags for exactly this config
   and size, so the harmonic call cannot silently regenerate an unchecked mesh.
   Force/power and pressure demand
   remain unassessed unless measured by existing diagnostics.
3. Instrument the existing direct-solve helper in the disposable process,
   preserving its assembled K, projected b, unscaled x, and exact factorization.
   An in-memory instrumented copy or narrowly scoped temporary wrapper is
   acceptable; check its assembly/BC/nullspace lines against the pinned helper.
   Do not create a second form, dense matrix, new solver, or persistent backend
   API. Save the original `r=b-Kx`, its absolute norm and `||r||/||b||` before
   changing anything. Check compatibility against both pressure constants;
   record any nullspace projection of the correction RHS rather than hiding it.
4. With the **same** factors, perform exactly one residual-correction solve
   `K dx = projected(r)`. Record convergence reason, residual compatibility,
   correction-equation residual and corrected primal residual. Convert dx to
   fields using the existing DOLFINx block assignment convention. Record disk
   `delta G=J(dx)` and J(x+dx)-J(x) at the same quadrature, accounting explicitly
   for physical scaling. This is an observed algebraic correction, not a
   rigorous upper bound on the remaining error. No adjoint, iterative refinement
   loop, new factorization, or gauge change is authorized by this package.
5. On the original fields evaluate the existing signed features at
   (plane,radial,angular) orders (12,12,64), (18,18,96), (24,24,128),
   (48,48,256), and (96,96,512). Report all six complex features and absolute
   primary changes. At the finest rule also report correction and corrected
   features, numerator absolute-sum/cancellation diagnostics, denominator, and
   any failed cell location. Compare each original primary gain with the same
   128-term reference: absolute complex, relative complex, magnitude and wrapped
   phase errors. Keep nonfinite/undefined outcomes explicit and strict JSON.
6. Enforce **180 s total child-tree wall time and 1.5 GiB active child-tree RSS**,
   from imports/mesh/JIT through factorization, correction, extraction and report
   output, using a parent watchdog sampling nominally every 0.05 s. Record maximum
   sample gap, peak observed RSS and process high-water RSS. These are conservative
   allocation limits, not measured promises of success. Retain the pre-array
   500-cell and dense 3,000-free-DOF guards. Run synthetic wall/RSS watchdog checks
   before the physical attempt. Stop on a cap; do not retry or raise limits.
7. Acceptance evidence is a complete finite, identity-matched report or an
   explicit partial/refused report. Evaluate the existing `_pde_diagnostics_passed`
   conditions unchanged, including `1e-9` primal residual, and report the same
   residual ceiling for correction self-consistency. A failed numerical check
   stops interpretation; preserve the data. Require field/block reconstruction
   and the J(dx) identity to agree within `256*eps*S`, where S is the sum of
   the absolute weighted disk-numerator contributions from x, dx, and x+dx,
   divided by the positive disk denominator (and by U_probe for physically
   scaled fields). Record S and the tolerance in gain units; never tune it to
   force a pass. This is an arithmetic self-check, not a physical threshold.
   Compare observed algebraic and quadrature changes with the `3.455610099e-6 1/m` scale without converting them
   into certified error bars or adding a physical threshold. Report existing
   5%/5-degree reference comparisons regardless of whether they pass.
8. Stop after that single case and interpretation, including a resource refusal,
   failed comparison, or unresolved floor. A small correction does not remove
   geometry/spatial error, and one mesh cannot establish refinement or penalty
   robustness. Preserve the failed physical gate and `campaign_ready=false`.
   Commit/push the scoped evidence under `Continue`, and propose one next task.
   No 40/30/25 mm solve, boundary-layer implementation, campaign, B3, or gate
   integration follows automatically.

If the result exposes a fully understood mechanical reporting/instrumentation
fix, recommend **GPT-5.6 Luna, medium** with exact edits, focused checks and a
stop before interpretation. Otherwise retain Astra/high for the bounded
remaining numerical question. Availability was checked 2026-09-20 in the
session's model catalog and official [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
and [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) documentation;
account/client access can differ. No model switch, delegation or automation ran.

## Validation and execution limits

The final reference child took 0.3690 s; both executed reference passes totalled
0.8442 s, with the second deadline reduced by the first measured duration.
Maximum parent-observed RSS across both was 66.9063 MiB; final process high-water
RSS was 71.7813 MiB. Maximum observed sampling gap was 0.05342 s. All were below
120 s/1 GiB. RSS is sampled, not an instantaneous bound.

The initial watchdog CLI self-check encountered a directory-creation error
before launching its synthetic children. That wrapper defect was corrected;
the final exact runner passed both synthetic wall and two-process RSS checks.
The reference calculation was repeated under the remaining cumulative budget
so final provenance identifies the corrected runner. No numerical/reference
inconsistency or resource stop occurred.

Validation includes assertions for config, known reference, series agreement,
128 independently integrated coefficients, 21 radial and five polar comparisons,
three historical gains with the pinned report identity, unchanged source hashes,
strict JSON, manifest integrity, exact embedded runner bytes, Markdown links,
fenced syntax, table consistency, and `git diff --check`. No application suite,
FEM/PDE/UFL/dense check, mesh, harmonic pilot, rendering or encoding was run.
Existing reference tests containing disallowed 16-term/changed-parameter cases
were not run; the bounded checks above cover this task's actual calculations.
