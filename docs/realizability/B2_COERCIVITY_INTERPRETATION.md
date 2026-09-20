# B2 coercivity interpretation and response-mesh follow-up

The bounded follow-up below was completed in R008. Read the
[response-geometry result](B2_RESPONSE_COERCIVITY_RESULT.md) for the new
40/30/25 mm evidence and current next task; retain this review as its contract.

Prepared 2026-09-20 for [R007](../../REQUEST_LOG.md#r007--2026-09-20--short-continuation-request)
against `14896cd` (the R006 implementation is `ae31af2`). This is a review of
existing evidence and source. No mesh, PDE matrix, eigenproblem, or harmonic
response was computed during R007. The [R005 derivation](B2_SCALABLE_STABILITY_REVIEW.md)
and [calibration appendix](B2_SCALABLE_STABILITY_CALIBRATION.md) remain the
method specification; [R006](B2_SCALABLE_STABILITY_REVIEW.md#2026-09-20-implementation-result-r006)
records its implementation and numerical checks.

## Decision

The 50 mm result establishes positive dissipation at alpha=96 for the stated
mesh and homogeneous SIP form, subject to the diagnostic's numerical guards.
It leaves alpha=48 inconclusive. It supplies no certificate for the distinct
40/30/25 mm physical-pilot meshes. Neither result establishes physical
response accuracy or selects a production penalty.

Select one next task: **apply the existing local certificate to the existing
40/30/25 mm response geometries**, with a 50 mm reproducibility control and a
reviewed, explicit resource budget. This needs a bounded research runner using
the existing API, not a new stability method. Stop after documenting the
mesh-specific classifications, including inconclusive results. Sparse
factorization and physical-accuracy investigations remain later alternatives.

The physical B2 gate stays failed, `campaign_ready=false`, and the gate's
actual-response-mesh field stays `not_assessed`. This separate research evidence
does not update that field. Preserve the 3,000-free-DOF dense guard, default
500-cell local guard, physical parameters, boundary interpretation, and
acceptance thresholds. Do not integrate this diagnostic into `b2-gate`.

## What the stored numbers establish

The table is extracted from the R006 strict JSON, with arithmetic recomputed
from its stored numbers. `C_tr` is the maximum recorded local trace eigenvalue;
it is not an eigenvalue of the Stokes operator. The guarded certificate uses
`C_safe = C_upper + 1e-10*max(1, C_upper)` and requires
`beta = 1-sqrt(C_safe/alpha) > 1e-8`.

| Mesh | Cells | `C_tr` | `C_upper` | beta at 48 | beta at 96 |
|---:|---:|---:|---:|---:|---:|
| 100 mm | 82 | 49.2511028937 | 56.0371901177 | -0.0804820502 | +0.2359838153 |
| 70 mm | 171 | 31.0969737326 | 36.7200957987 | +0.1253560748 | +0.3815333494 |
| 50 mm | 482 | 48.9641814136 | 58.1265712308 | -0.1004409271 | +0.2218707581 |

At 50 mm, `C_safe=58.12657123659904`, and therefore alpha=96 gives

```text
a(v,v) >= nu * 0.22187075813338908 * (G + 96 J).
```

Here G and J are the gradient and weighted jump/boundary terms defined in the
R005 derivation. On the connected affine mesh with every exterior facet
penalized, this energy norm vanishes only for zero velocity. Positivity on
the broken P2 space implies positivity on its homogeneous-normal,
divergence-free BDM2 subspace. With positive mass, the unforced semidiscrete
rest-Stokes system dissipates energy. Beta is dimensionless; it does not
give a decay rate in 1/s, a settling time, a gain error bound, or a conditioning
estimate. This is a guarded floating-point certificate, not an interval proof.

The negative beta at alpha=48 is a nonpositive **lower bound**, not a negative
Rayleigh quotient. Even replacing the conservative row sum by the computed
local eigenvalue would give `1-sqrt(48.96418141363834/48)=-0.009993620170014816`.
Thus simply tightening that last algebraic estimate cannot certify 48 through
this same inequality. A sharper trace argument or a constrained global method
would be new research; changing the diagnostic threshold would not resolve it.

Existing dense controls demonstrate the interpretation: 100 mm at alpha=48
has minimum rate `+0.00185910664480 /s` despite its inconclusive local bound;
70 mm at alpha=24 similarly has `+0.00163460031658 /s`. Alpha=6 has negative
dense rates on both fixtures, also with inconclusive local bounds. R007 checked
these stored records and their matching mesh hashes; it did not rerun them.

## Transfer to a response operator

The [shared source](../../realizability/backends/hdiv_stokes.py) confirms that
the harmonic backend uses the same full SIP form, cell-diameter weights, and
BDM2/DG1 spaces. All exterior normal traces are prescribed and the full exterior
SIP penalty includes the caps. The certificate concerns perturbations with
homogeneous boundary commands; prescribed input changes the lift and load.
The official [DOLFINx formulation example](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_navier-stokes.html)
provides formulation context, while the mesh-specific bound comes from R005.

The 50 mm SHA-256 is
`423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4`, matching
the earlier response-mesh inventory. On exactly this geometry and form,
alpha=96 positivity transfers to any constant positive nu because nu multiplies
the whole form. Frequency changes the harmonic mass term and does not change
this dissipation sign. Thus the certificate also supports homogeneous stability
of the 50 mm alpha=96 changed-viscosity swirl comparison, conditional on the
same mesh/form. It does not certify its alpha=48 baseline or the accuracy of
either gain. No new backward-Euler or assembled-operator check at 50 mm is
claimed.

Mesh size alone is insufficient identification. The trace bounds depend on
cell shapes, adjacent diameters, and exterior facets. Their nonmonotonic values
at 100/70/50 mm already rule out extrapolating a uniform safe penalty from this
sequence. Remeshing, curved geometry, a different SIP form or degree, variable
viscosity, and convection require new evidence. No conclusion transfers to a
nonlinear vortex or to laboratory control from this rest-Stokes calculation.

Physical accuracy remains independently unresolved. The earlier physical
reference has magnitude `6.911220198253779e-5 1/m` at 0.01 Hz and nu=1e-6 m²/s;
the historical 25 mm alpha=6 complex discrepancy was `0.0182041133724 1/m`.
Those [historical comparisons](B2_CONTINUATION_REVIEW.md#physical-reference-confirms-the-historical-discrepancy)
precede the boundary/penalty repair and cannot diagnose the present backend.
The changed-parameter swirl fixture, series convergence, and energy positivity
do not establish an absolute error floor or a resolved physical response phase.

## Alternatives and why the next task is bounded geometry evaluation

| Candidate next action | Information gained | Decision |
|---|---|---|
| Existing local certificate on 40/30/25 mm | Direct sufficient evidence on the requested response geometries, with no global operator allocation | Selected under the limits below |
| Constrained sparse inertia/eigenanalysis | Can resolve cases where the sufficient bound fails and count negative constrained modes | Defer: pressure rank/gauge, scaling, pivot diagnostics, and factor memory still need calibration |
| Physical-accuracy/error-floor study | Can separate gain errors, cancellation, boundary geometry, and resolution requirements | Defer: remains necessary even if every certificate is positive; no repaired physical response data yet |
| Increase alpha or refine until a report passes | Changes the numerical experiment without isolating its accuracy | Not selected; no automatic penalty/mesh changes |

The local diagnostic has already been implemented and independently calibrated.
Its cost depends on cells/facets and four-by-four arrays, rather than the
free-velocity DOF count that prevents dense analysis. R006 measured 0.51 s and
179.56 MiB for 100/70/50 mm together. These measurements support a bounded
attempt on the inventoried geometries, but do not guarantee its cost or result.
There is no need to design another implementation before taking that evidence.

## One next task and its acceptance contract

Recommend **GPT-6 Astra, high reasoning** to run and interpret this bounded
actual-response-geometry study. Keep source defaults intact and use a disposable
runner, preserving its exact text in a versioned evidence appendix afterward.
Read this review, R005/R006, and the four root research documents first.

1. Load `configs/realizability/pilot.json`. Confirm the shared form and geometry
   generator still match this review's provenance. Evaluate 50 mm first with
   `run_b2_coercivity(config, (0.05,), (48.0, 96.0), max_cells=500)`.
   Require the recorded hash/482 cells, statuses, and C_upper within `1e-10`
   relative to `58.12657123078638`. Stop on mismatch; do not substitute a new
   mesh and call it the same case.
2. In fresh serial child processes, evaluate 40, 30, and 25 mm in that order,
   once each at alpha=48/96 using the same API with **`max_cells=4000`**.
   This explicit per-call limit is a reviewed resource allowance for this
   next experiment only. Do not edit `CELL_LIMIT=500`, add a CLI override,
   or bypass the pre-array guard. Check the existing inventory before accepting
   a classification:

   | Mesh | Expected cells | Expected SHA-256 |
   |---:|---:|---|
   | 40 mm | 873 | `a7006604f0da3df5c8b9f92aaf0e8f1eaae8522554c4378e1e9ce1369a85e59b` |
   | 30 mm | 1842 | `9096deae45c24dcdb028082e2b971fb197657574e1b43af71a9ec036dc2ff7bf` |
   | 25 mm | 3154 | `42fa3aac5c2bc762514c5cadb642edc2a1a8acfdf81ea9df7df992b696a04895` |

3. Enforce **120 s total wall time for the complete four-mesh experiment and
   1 GiB RSS for the active child process tree**, using a parent watchdog from
   process launch through imports, mesh generation, calculation, and output.
   Poll at most 0.1 s apart; terminate the child tree when either cap is
   observed and record partial evidence and monitoring granularity. A watchdog
   is a sampled stop mechanism, not an instantaneous memory guarantee.
   Record parent-observed peak RSS as well as the report's process peak.
   Do not raise caps, retry automatically, or proceed to smaller mesh sizes
   after a limit or invalid case. The 4,000-cell guard is per mesh; it does not
   cap Gmsh allocation before the mesh exists, hence the external watchdog.
4. Require finite positive volumes and valid affine connected tetrahedral
   geometry, complete facet coverage, `volume/diameter^3 > 1e-12`, and the
   unchanged `1e-10` padding/`1e-8` beta guard. Check one finite trace eigenvalue
   per cell, `max(c_K) <= C_upper` to arithmetic tolerance, facet counts, and
   independently recomputed beta/classification for every reported penalty.
   Use the existing focused coercivity tests if executable runner work needs
   validation; no new PDE regression or full suite is required for unchanged
   numerical source. Record tests actually run and optional dependency skips.
5. Write strict JSON and Markdown containing config, versions, mesh identities,
   limits, C_upper/C_safe, dimensionless beta, classifications, reasons, timings,
   and RSS. Add the exact runner hash, source hashes for config/mesh/form/local
   helpers and the report writer, and repository commit/dirty state. Hash the
   reports in a manifest. Retain `campaign_ready=false` and separately list
   inconclusive stability cases and physical-accuracy blockers; a positive
   subset must not become an all-mesh claim or a passing gate.
6. Preserve a compact table, provenance, exact runner, and results/limits in
   Markdown so the conclusion survives loss of `/tmp`. Interpret the evidence,
   update the log and handoff, commit/push under the next `Continue` request,
   and **stop at this experiment's result**. An inconclusive case is a valid
   outcome and does not trigger sparse analysis within this task.

Completion is the bounded report and its checked scope, even if some cases
remain inconclusive or are explicitly unexecuted after a stop. No global
velocity/divergence/mass assembly, factorization, eigenmode solve, harmonic
pilot, larger mesh sweep, gate integration, physical parameter/threshold
change, six-input campaign, or B3 work belongs to this follow-up. The dense
3,000-free-DOF guard has no exception.

If useful response cases are certified, the following handoff should recommend
Astra/high for an absolute physical-accuracy/error-floor investigation. If
certificates are inconclusive, use Astra/high to decide whether a bounded
constrained sparse study is worth its resource cost. A known mechanical
reporting/runner defect can instead be handed to **GPT-5.6 Luna, medium** with
the exact fix, focused check, and a stop before interpretation. These are
future handoff rules, not additional work in the selected task.

Availability was rechecked on 2026-09-20: this session's tool catalog lists both
models and efforts; the official [Astra page](https://developers.openai.com/api/docs/models/gpt-6-astra)
supports research work and high effort, and the [Luna page](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
lists medium effort. Selecting high for this interpretation is project judgment.
The user's model picker may depend on account/client access. No model switch,
delegated session, or automation was launched.

## Evidence audit and reproducibility

R007 read the R006 report at
`/tmp/navier-b2-coercivity-r006-final2/coercivity.json`, SHA-256
`83530949284b50c3cd4e9b22e9cbb88c47c0f0d9667ee752f4065d3ba8e9454f`.
Its recorded commit is `ec9d5c5` with a dirty tree because it preceded the R006
implementation commit. All six recorded config/source hashes match the current
files, including the shared SIP form and local diagnostic. Configuration equals
the current pilot JSON. This establishes the checked source identity without
pretending the earlier run came from a clean commit or a complete provenance
list. R007 also records hashes of config.py, boundary_modes.py, observables.py,
the stability/gate/verification modules, and swirl_reference.py in its audit.

Key source identities, unchanged in this review:

```text
realizability/backends/b2_coercivity.py
  be10e484ffd5c36aef45962242dea2bcaaaa3cbad37df83e297fcc366bf96bcc
realizability/backends/hdiv_stokes.py
  f23b252f91c406e3e279c7e6e7049e301ad604fae232dd0a610a73319864d2e9
realizability/backends/fenicsx_stokes.py
  37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206
configs/realizability/pilot.json
  0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0
```

The read-only audit is `/tmp/navier-b2-interpretation-r007/audit.py`; its strict
output is `audit.json` in the same directory. It checks 735 stored local values,
15 penalty classifications, all three facet-count identities, six source hashes,
four dense sign/conservatism controls, matching fixture hashes, and the stored
failed schema-3 rejection/readiness status. The interpretation above preserves
the new decision-relevant values independently of these temporary files.
To reproduce the underlying small-fixture report in a fresh clone, use the
existing `b2-coercivity` command at 100/70/50 mm with penalties 6/12/24/48/96
under the R006 120 s/1 GiB limits; the optional setup and calibration are linked
above. That reproduction was not rerun in R007.

Documentation validation covers local links/anchors, fenced Python/JSON syntax
where present, numerical table consistency, and `git diff --check`. Application
suites, optional PDE/UFL/dense checks, rendering, and encoding are skipped:
their source is unchanged and this request stops at the research decision.
