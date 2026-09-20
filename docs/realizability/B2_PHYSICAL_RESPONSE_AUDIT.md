# B2 single physical response audit

Completed 2026-09-20 for [R012](../../REQUEST_LOG.md#r012--2026-09-20--short-continuation-request)
against `339b3ee`, following the [R009 contract](B2_ACCURACY_REVIEW.md#one-proposed-experiment-and-next-task).
The [evidence appendix](B2_PHYSICAL_RESPONSE_EVIDENCE.md) preserves the exact
runner, complete numerical report, provenance, watchdog checks and validation.
No package source, configuration, solver, form or acceptance threshold changed.

## Result

**The certified 50 mm, alpha=96 calculation passes the existing PDE checks but
fails the physical reference comparison by a very large margin.** At the finest
requested feature rule, its disk-rotation gain is

```text
G_h = -1.6734039795256472 - 1.0983726070219908 i  [1/m]
G_ref = 2.0662858857221768e-5 - 6.595106312048072e-5 i  [1/m]
|G_h| / |G_ref| = 28962.6875822
|G_h - G_ref| = 2.0016562003159444  [1/m]
wrapped phase discrepancy = 74.1163789199 degrees
```

All five rules fail the unchanged 5% magnitude and 5-degree comparisons. The
physical amplitude inferred from this unvalidated field is `2.0016751141e-7 /s`,
versus the smooth reference's `6.9112201983e-12 /s`, for the same `1e-7 m/s`
command. The computed amplitude is **not trustworthy physical-response data**.
This is a numerical verification failure, not a finding about whether exterior
hardware can prepare the desired vortex or support the user's eventual movie.

The single residual correction changes the disk gain by only
`2.2498932366e-14 1/m`. This measured correction does not explain the discrepancy.
Feature quadrature is also unresolved at the reference's absolute comparison
scale: the last two rules differ by `2.9156584710e-4 1/m`, about **84.37 times**
`0.05 |G_ref| = 3.4556100991e-6 1/m`. That quadrature change is small relative
to the computed gain, but that is the wrong scale for establishing agreement
with this tiny reference. Neither sensitivity is a certified total error bound.

Stop after this one case. The physical B2 gate remains failed and
`campaign_ready=false`. Alpha=96 remains a verification candidate on its
certified meshes, not a production penalty selection. Alpha=48 is inconclusive.
No finer mesh, different penalty, campaign, B3 sensing or movie export ran.

## What was held fixed

The calculation retains resting water, R=0.10 m, H=0.15 m, nu=1e-6 m²/s,
f=0.01 Hz, U_probe=1e-7 m/s, the fixed 0.025 m disk and six signed features,
`exp(i omega t)`, zero essential normal trace, and the existing symbolic
facet-consistent tangential load. No volumetric source was added.

All 19 source/configuration hashes matched R009 before and after calculation.
Before global assembly, the runner checked the existing 50 mm mesh hash
`423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4`,
482 cells, and 9,522/1,928 velocity/pressure DOFs per phasor part. It reproduced
`C_upper=58.12657123078638` and guarded beta `0.22187075813338908` at alpha=96
using the unchanged local diagnostic and 500-cell guard. The wrapper returned
that same domain and tags to the harmonic call exactly once. The dense
3,000-free-DOF guard remains unchanged and no dense audit ran.

A Python return-frame observer captured the **unchanged** direct helper's
matrix, projected RHS, unit-command solution, pressure constants and KSP.
The helper source was preserved and checked byte for byte. The 22,900-square
mixed system was neither rescaled nor rebuilt. The one correction RHS used
the same MUMPS factors and KSP, with unchanged matrix state and factor handle.
PETSc counters recorded one symbolic factorization, one numerical factorization,
and one then two matrix solves. The counter instrumentation uses
[PETSc event performance records](https://petsc.org/release/petsc4py/reference/petsc4py.PETSc.LogEvent.html#petsc4py.PETSc.LogEvent.getPerfInfo).

Unit-command vectors were assigned to fields using the existing DOLFINx block
convention, then multiplied by U_probe; features were divided by U_probe to
report gains. Three block/field round trips were exact, and the reconstructed
original physical coefficients equalled the returned harmonic fields exactly.
No pressure gauge, solver option, form, boundary target or backend API changed.

## Algebraic and boundary evidence

| Quantity | Original | After one correction |
|---|---:|---:|
| Primal absolute coefficient residual | 8.8220437132e-16 | 1.2052300692e-16 |
| Primal residual / projected RHS norm | 8.5034294457e-15 | 1.1617023439e-15 |
| Correction equation absolute residual | — | 2.9894172368e-28 |
| Correction equation residual / correction RHS norm | — | 3.3885767741e-13 |
| PETSc convergence reason | 4 | 4 |

The projected original RHS norm is `0.10374689140977104`; its two pressure
constant products are zero. Before correction projection the residual products
are `2.7993915229e-21` and `5.4894639945e-20`. Removing the two constants changes
the RHS by norm `5.4965972088e-20`, or `6.2305259275e-5` of the residual norm.
After projection the products are zero and `1.2031184681e-35`. The appendix also
records left/right pressure-nullspace matrix products and corrected compatibility.
These are mixed coefficient norms, not physical output error estimates.

The unchanged `_pde_diagnostics_passed` check passes. Real/imaginary divergence
ratios are `1.61723e-14` and `2.21477e-14`; corrected flux ratio and essential
boundary DOF residuals are zero. Both primal residuals and the correction
self-consistency residual are below the prescribed `1e-9` ceiling.

| Trace diagnostic, normalized by command speed | Real | Imaginary |
|---|---:|---:|
| Side tangential mismatch | 0.0779399 | 0.1506122 |
| Cap tangential mismatch | 0.00466746 | 0.00425991 |
| Smooth-target normal mismatch | 0.0761195 | 0 |
| Actual side normal trace | 8.06180e-17 | 3.13382e-17 |
| Actual cap normal trace | 2.71689e-17 | 6.71967e-18 |
| Interior tangential jump | 0.0415061 | 0.0245122 |

These trace measurements have no new acceptance threshold. In particular,
zero essential normal trace does not make the smooth-cylinder target identical
to its tangential projection on the planar facets. The trace norms do not
quantify their effect on the central gain.

Existing input diagnostics give peak target speed `1e-7 m/s`, side RMS speed
`6.3717914521e-8 m/s`, zero inward volume-flow amplitude, displacement amplitude
`1.5915494309e-6 m`, and acceleration amplitude `6.2831853072e-9 m/s²` at 0.01 Hz.
Pressure demand and force/power remain unassessed. No hardware limits or
sensor detectability are inferred from these ideal prescribed commands.

## Signed-feature integration and arithmetic checks

Each row uses the original fields. Orders are (plane, radial, angular); all
six complex features, with their units, are in the appendix.

| Orders | Disk gain real (1/m) | Disk gain imaginary (1/m) | Absolute complex error (1/m) | Relative magnitude error | Phase error (degrees) |
|---|---:|---:|---:|---:|---:|
| 12,12,64 | -1.6876065556 | -1.1007239034 | 2.0148284186 | 29152.276589 | 74.282099 |
| 18,18,96 | -1.6699089264 | -1.0978815291 | 1.9984653803 | 28915.519615 | 74.073166 |
| 24,24,128 | -1.6717362954 | -1.0976824424 | 1.9998833189 | 28936.035525 | 74.106692 |
| 48,48,256 | -1.6736953515 | -1.0983832366 | 2.0019056313 | 28965.296583 | 74.120701 |
| 96,96,512 | -1.6734039795 | -1.0983726070 | 2.0016562003 | 28961.687582 | 74.116379 |

Relative errors in this table are ratios, not percentages. The default-to-finest
difference is `0.0035293843494 1/m`, or 1021.35 times the 5% absolute scale.
The largest pairwise rule difference is `0.0179244294096 1/m`. The sampled gains
remain far from the reference throughout, but this sweep does not prove a
quadrature error bound or monotone convergence of the cut-cell integral.
No requested point location failed and all recorded quantities are finite.

At the finest rule the disk denominator is `6.135923151542543e-7 m^4`.
The sum of absolute combined complex numerator terms divided by the absolute
numerator is 1.053827 for the original field, 2.095579 for the correction and
1.053827 for the corrected field. The original disk reduction therefore shows
little cancellation. The more conservative split-component sums, treating
`w*x*u_y` and `-w*y*u_x` as separate contributions, give the required gain-unit
arithmetic scale

```text
S = sum_{x, dx, x+dx} sum_q (|w*x*u_y| + |w*y*u_x|) / (D*U_probe)
  = 4.348754282901129  [1/m]
tolerance = 256 * eps * S = 2.4719806122568166e-13  [1/m]
|J(x+dx) - J(x) - J(dx)| = 2.1698718487761074e-16  [1/m]
```

The field-reconstruction disk difference is zero; the largest independent
direct-reduction discrepancy is `3.1401849174e-16 1/m`. All arithmetic checks
pass at the fixed tolerance. This tolerance checks arithmetic on the computed
field; it is not a bound on the physical calculation. The correction is only
`6.5108422886e-9` of the 5% reference scale, with physical rotation correction
`2.2498932366e-21 /s`. A single small correction does not prove the remaining
algebraic error is bounded by it.

## Interpretation and limits

This audit establishes that a stable homogeneous discretization and small
linear residual can coexist with an unacceptable driven physical response.
The observed correction and sampled quadrature changes do not account for
the roughly `2 1/m` reference discrepancy. A rigorous allocation of that error
between spatial discretization, load integration, boundary-model/geometry
change and unmeasured output-integration error is still unavailable.

The nominal h/delta ratio is 8.862 for delta=5.641896 mm. Boundary-layer
under-resolution is a plausible contributor, but nominal element size is not
a measured boundary-normal spacing and this run does not isolate the cause.
Facet projection changes the continuum boundary problem; pressure-mediated
or symmetry-breaking responses are possibilities to investigate, not diagnoses
established by this result. The nonzero auxiliary features alone do not separate
mesh, geometry and load effects. Historical alpha=6 values came from different
meshes and the earlier form and cannot be used as a controlled comparison here.

The experiment measured a discrepancy for **one** mesh and penalty. It does not
establish refinement convergence, penalty robustness, a universal error floor,
a feasible preparation protocol, or a physically supported time history for the
movie. The [project status](../../STATUS.md) retains those distinctions.

## Resources and validation

The one monitored physical child took **38.7542 s**, including imports, mesh,
local certificate, assembly/JIT, one primal solve, one same-factor correction,
features and report output. The helper's original solve time was 1.20193 s.
Maximum parent-observed RSS and the child's process high-water RSS were both
**753.0508 MiB**. There were 718 parent samples at nominal 0.05 s, with maximum
gap 0.08138 s. No 180 s/1.5 GiB cap was reached. Sampled RSS is not an
instantaneous memory guarantee; this cost is not a prediction for other meshes.

Both ordinary-interpreter and final optional-interpreter synthetic wall/RSS
checks passed before the physical run; the latter killed a two-process allocation
at a 24 MiB test limit. The capture wrapper also passed a return-identity check.
The physical attempt ran exactly once and was not retried.

The read-only evidence audit checked eight manifest files, 19 source/config
identities, 482 local trace values, eight finite 22,900-entry coefficient arrays,
30 complex original features, three sets of 49,152 saved disk samples, residual
norms, factor counts, reference comparisons, block addition, and independent
`math.fsum` disk reductions. Strict JSON, exact embedded runner/report records,
Markdown links/anchors and fences, table structure, and `git diff --check` were
also checked. No full application, UFL calibration, dense, changed-parameter or
mesh-refinement suite ran; no rendering or encoding ran. Those would add physics
cases or exercise unchanged components outside this contract.

## Next bounded task: design a geometry and boundary-layer accuracy test

Recommend **GPT-6 Astra, high reasoning**, for one method review that specifies
an affordable accuracy experiment able to distinguish spatial resolution from
faceted-boundary model error. The concrete deliverable is one selected test
contract, with equations, physical boundary data, mesh/output checks, independent
reference, explicit resource caps and a failure interpretation. Do not launch
another harmonic solve merely because this coarse one was affordable.

Read this audit and appendix, R009's error decomposition, the R005 assumptions,
R008 certificates, `STATUS.md`, and the four root research documents. Use source
inspection, existing reports and elementary scale/cost calculations only; no
new mesh, assembly, PDE solve, reference sweep or field reintegration is part
of the review. Preserve all physical parameters, signed features, phasor and
thresholds. The review must:

1. State the distinct smooth-cylinder and faceted/projection boundary problems,
   including why their solutions need not have the same exponentially attenuated
   disk response. Identify a consistency check before claiming either converges
   to the other.
2. Compare a boundary-layer mesh using the existing 3D form with a separate
   symmetry-restricted diagnostic and with an output-weighted residual approach.
   State what each would isolate and what it would leave unresolved. A new
   diagnostic would not silently replace the production backend or validate
   general boundary modes. Changing the target to the smooth reference trace
   would be a separate verification fixture, not experimental actuation.
3. Select **one** proposed experiment with a reproducible identity/configuration
   contract, checks appropriate to the actual boundary problem, an output
   integration rule adequate to test the tiny response, and a conservative
   parent-enforced budget. Address the 753 MiB coarse result and historical
   6931 MiB 25 mm result without extrapolating an LU cost guarantee. A changed
   geometry needs its own stability assessment; R008 certificates do not transfer.
4. Keep unknowns explicit. If the evidence cannot support an affordable test,
   record that limitation and the specific missing decision. No hardware
   feasibility, sensing sufficiency or movie trajectory claim follows.

Stop after the reviewed experiment contract, or an explicit unresolved method
choice. No new solver/form implementation, boundary-model change, global solve,
mesh sweep, adjoint, gate integration, campaign or B3 is authorized by this
review task. The physical B2 gate remains failed and `campaign_ready=false`.
On a later `Continue`, publish the scoped review and stop before its proposed
experiment. This is a written handoff, not a scheduled or delegated session.

If the review yields fully specified mechanical work, recommend **GPT-5.6 Luna,
medium**, with exact edits, focused checks and a stop before interpretation.
Retain Astra/high when method choice or numerical interpretation remains.
Availability was rechecked on 2026-09-20 in the session catalog and fetched
[official Astra](https://developers.openai.com/api/docs/models/gpt-6-astra) and
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages using the
OpenAI Docs skill. Account/client access may differ; no model switch occurred.
