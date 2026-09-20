# B2 pre-campaign numerical gate

## Current report contract (schema 3)

Gate reports preserve `all_numerical_gates_passed` as the legacy aggregate of
bounded-fixture stability, affine verification, pilot PDE diagnostics, and the
two-pilot mesh, penalty, and quadrature checks. It does not include stability
on the requested response meshes or agreement with the smooth-cylinder
reference. Reports therefore set `campaign_ready` to `false` and list both
items in `campaign_blockers`, even when the legacy aggregate passes.

Completed reports compare every existing `T_00c` pilot and penalty-comparison
gain with the independent disk-rotation reference at the configured cylinder
dimensions and viscosity, 0.01 Hz, and a 0.025 m disk. The reference reports
its complex gain, units, `exp(i*2*pi*f*t)` convention, and 64-to-128-term
series difference. Comparisons include absolute complex error, relative
complex error, relative magnitude error, and wrapped phase difference. They
are diagnostics, not a campaign gate or a proven discretization-error bound;
no additional harmonic solves are made.

Mesh, penalty, and quadrature comparisons now include absolute complex change
alongside the existing relative-magnitude and phase tests. These are observed
sensitivities, not error bounds. Undefined phase and invalid arithmetic are
reported as JSON `null` with validity flags and reasons; they fail the existing
comparison acceptance. A zero response retains a valid absolute difference
where calculable, but has no phase. Early stability rejection reports mark
later work as not run and do not evaluate the optional SciPy reference.

The physical-pilot gate remains failed. A synthetic reference match or a
passing legacy aggregate does not establish actual response-mesh stability,
physical accuracy, or campaign readiness.

The [scalable stability review](B2_SCALABLE_STABILITY_REVIEW.md) now specifies
a separate sufficient coercivity diagnostic, calibrated on the existing small
cylinders and compared with sparse inertia counts. The standalone diagnostic
has run on the 100/70/50 mm fixtures and, in the
[R008 response-geometry study](B2_RESPONSE_COERCIVITY_RESULT.md), the exact
40/30/25 mm physical-pilot geometries. Alpha=96 has a positive certificate on
all four 50/40/30/25 mm meshes; alpha=48 is inconclusive on all four. This is
scoped homogeneous-operator evidence, not a physical-accuracy result or a
production penalty choice. The diagnostic remains separate from this gate, so
schema-3 reports still say response-mesh stability is `not_assessed`; that
field has not incorporated the R008 evidence. An inconclusive certificate must
not be interpreted as an unstable operator. The completed
[R009 accuracy review](B2_ACCURACY_REVIEW.md) quantifies reference sensitivity
and the absolute comparison scale. Its subsequent
[R012 physical audit](B2_PHYSICAL_RESPONSE_AUDIT.md) completed the one 50 mm
alpha=96 response and same-factor residual correction. Existing PDE/arithmetic
checks pass, but the finest-rule response amplitude is 28962.69 times the
reference with a 74.12-degree phase discrepancy. The observed algebraic
correction is tiny, while feature quadrature remains unresolved at the reference
error scale. This is failed physical-accuracy evidence for one mesh, not a
convergence study or gate integration. This gate's code and thresholds are unchanged.

This package is deliberately incomplete: the six-input response campaign was
not launched because the numerical acceptance gates did not all pass.

## Why B1's divergence check failed

The B1 P2/P1 Taylor--Hood solve is weakly divergence-free.  On its 70 mm smoke
mesh, the strong diagnostic
`R ||div(u)||_L2 / ||u||_L2` is order one or larger.  Uniform refinement through
20 mm and p-refinement did not approach the required `1e-3` within a practical
memory envelope.  Grad-div stabilization plateaued above the threshold because
the discrete trace and continuous Taylor--Hood space do not provide an exactly
divergence-free velocity.

B2 therefore retains B1 unchanged as a cross-check and adds a separate
BDM2/DG1 divergence-conforming symmetric interior-penalty (SIP) Stokes
discretization.  This follows the mass-conserving formulation demonstrated in
the [official DOLFINx divergence-conforming Navier--Stokes example](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/demos/demo_navier-stokes.html).
Normal
traces are imposed strongly; tangential traces are imposed by symmetric Nitsche
terms.  Manufactured volume forcing appears only in an affine reaction
verification fixture, never in a boundary-response run.

## Reproduce

Use the isolated DOLFINx environment described in `B1_SETUP.md`:

```bash
python -m unittest discover -s tests/realizability -p 'test_b2_hdiv.py'
python -m realizability.cli b2-gate \
  --config configs/realizability/pilot.json \
  --mesh-sizes 0.04 0.03 0.025
```

The current command first runs the bounded cylinder energy audit at its
explicit alpha=48 and alpha=96 defaults.  It writes an explicit failed gate
and skips all harmonic pilots if either candidate adds energy on those small
fixtures.  These settings are verification candidates, not a certification for
the listed response meshes; use `b2-stability` and `b2-verify` from
`B2_STABILITY_REVIEW.md` for their separate reports.

The command writes `results/realizability/b2/gate.{json,md}` and never launches
the six-mode campaign.  It checks only the two prerequisite pilots,
`N_02c` and `T_00c`, at 0.01 Hz.

## Current result

The run on 2026-09-19 produced:

| Gate | Result |
|---|:---:|
| affine reaction verification | pass |
| corrected flux, algebraic residual, strong divergence | pass |
| primary-feature quadrature convergence | pass |
| primary gain/phase mesh convergence | **fail** |
| SIP-penalty sensitivity | **fail** |

Across all six production pilot solves, the strong-divergence ratios were
`4.37e-12` to `2.60e-10`, corrected flux ratios were at most `4.58e-16`, and
scaled algebraic residuals were at most `1.14e-11`.  This resolves the B1
strong-divergence failure for the new B2 discretization; it does not relabel the
coarse B1 Taylor--Hood result as passing.

For the primary symmetry-matched features:

| Mode → feature | Meshes (m) | Gain change | Phase change | Result |
|---|---:|---:|---:|:---:|
| `N_02c → a_z` | 0.040 → 0.030 | 0.587% | 0.703° | pass |
| `N_02c → a_z` | 0.030 → 0.025 | 0.904% | 0.468° | pass |
| `T_00c → Omega` | 0.040 → 0.030 | 267.163% | 42.865° | fail |
| `T_00c → Omega` | 0.030 → 0.025 | 13.829% | 40.790° | fail |

At 25 mm, changing the SIP penalty factor from 6 to 12 changed the normal
primary gain by 0.568% and 3.036°, but changed the tangential primary gain by
117.716% and 137.652°.  The tangential response is therefore unresolved; its
phase must not be interpreted.

The final gate process peaked at 6931.1 MiB RSS.  A 20 mm uniform BDM2/DG1 direct
solve exceeded the available memory, so simply adding another uniform level is
not currently reproducible on this machine.  A scalable iterative block solver,
anisotropic boundary-layer mesh, or reviewed Fourier-separated formulation is
needed before retrying the gate.  This is a numerical limitation, not evidence
that the physical tangential response is zero.

## Disposition

Do not run the six-mode response matrix, higher frequencies, pulse histories,
or B3 sensing work from this state.  The next work remains within B2: make the
tangential pilot affordable and demonstrate less than 5% gain and 5° phase
change across refinement and acceptable SIP-penalty sensitivity.

A subsequent source and numerical audit derived an independent smooth-cylinder
reference for the tangential pilot. See [B2_NEXT_STEPS.md](B2_NEXT_STEPS.md) for
the derivation, discrepancy with the stored results, and the stability checks
to perform before another large refinement run. The failed gate above remains
unchanged.

The subsequent [cylinder stability review](B2_STABILITY_REVIEW.md) finds
negative viscous dissipation at the current default penalty on small cylinder
meshes and confirms unforced energy growth. Stabilization and consistent
boundary data must be checked before choosing the next refinement strategy;
the cube audit alone cannot certify a cylinder penalty. No stored gate result
is reclassified by that review.
