# B2 response-geometry coercivity result

Completed 2026-09-20 for [R008](../../REQUEST_LOG.md#r008--2026-09-20--short-continuation-request)
against `f7a7e8f`, following the
[R007 acceptance contract](B2_COERCIVITY_INTERPRETATION.md#one-next-task-and-its-acceptance-contract).
Numerical backend source is unchanged. The calculation used the existing
standalone local certificate, with no global operator assembly or PDE solve.
The [evidence appendix](B2_RESPONSE_COERCIVITY_EVIDENCE.md) preserves the exact
runner, configuration, provenance, compact records, and report hashes.

## Result and scope

**Alpha=96 is certified positive on each of the existing 40/30/25 mm
response geometries and the 50 mm control. Alpha=48 remains inconclusive on
all four.** Every cell count and mesh hash matches the recorded inventory.
These are guarded numerical certificates of positive homogeneous SIP
dissipation, with the assumptions in the R005 derivation. No physical gain,
phase, error floor, or boundary-control performance was measured here.

| Mesh | Cells | Maximum local trace eigenvalue | `C_upper` | beta at 48 | beta at 96 |
|---:|---:|---:|---:|---:|---:|
| 50 mm | 482 | 48.9641814136 | 58.1265712308 | -0.1004409271 | +0.2218707581 |
| 40 mm | 873 | 51.1213519451 | 57.9026155132 | -0.0983189382 | +0.2233712309 |
| 30 mm | 1842 | 49.0156233493 | 58.4738571184 | -0.1037234059 | +0.2195496951 |
| 25 mm | 3154 | 50.0952175178 | 59.3021263562 | -0.1115129175 | +0.2140416786 |

The certificate retains `C_safe=C_upper+1e-10*max(1,C_upper)` and
`beta=1-sqrt(C_safe/alpha)>1e-8`. Its bound is
`a(v,v) >= nu*beta*(G+alpha*J)` for the current connected affine tetrahedral
mesh, full SIP form, and constant positive viscosity. It therefore covers the
homogeneous-normal, divergence-free BDM2 subspace of the rest-Stokes system.
Beta is dimensionless and is not a minimum decay rate in 1/s. The positive
sign also applies under constant positive viscosity scaling; it does not
establish nonlinear or physical experimental stability.

An inconclusive bound is not evidence of instability. Each maximum local
trace eigenvalue already exceeds 48, so merely replacing the row-sum estimate
by that eigenvalue would still leave the same sufficient inequality
inconclusive at alpha=48. The earlier dense-positive/inconclusive controls
remain relevant. No constrained eigenvalue or unforced time step was computed
on these response meshes, and no claim is made about alpha=48's actual sign.

This result provides useful stability evidence for alpha=96 as a verification
candidate on the identified geometries. It does not select a production penalty
or retrospectively repair the historical alpha=6 response. Nor does it certify
the alpha=48/96 pair as a whole. A separate sparse method could resolve 48's
sign, but is not required merely to recognize the positive certificate for 96.

The physical B2 gate stays failed and `campaign_ready=false`. Its schema-3
response-stability field remains `not_assessed` because this independent study
is not integrated into the gate. That reporting status should be distinguished
from the new, explicitly scoped alpha=96 evidence here. Physical accuracy,
absolute error floor, and any production penalty decision remain unresolved.

## Resource observations and validation

The four cases ran once each, in fresh serial optional-environment processes,
in the prescribed order. Total experiment time was **2.6918 s**, with a maximum
parent-observed child-tree RSS of **184.5078 MiB**. No cap was reached and no
case was skipped or retried. These are measurements on this environment.

| Mesh | Local bound time (s) | Watched child time (s) | Parent peak RSS (MiB) | Reported process peak RSS (MiB) |
|---:|---:|---:|---:|---:|
| 50 mm | 0.0632 | 0.8039 | 176.1094 | 177.0938 |
| 40 mm | 0.1008 | 0.4837 | 178.2500 | 178.2500 |
| 30 mm | 0.1996 | 0.5925 | 180.7617 | 180.5117 |
| 25 mm | 0.3500 | 0.8089 | 184.5078 | 184.5078 |

The wall budget was 120 s for all four cases; the active child-tree RSS budget
was 1 GiB. The parent sampled every nominal 0.05 s; the largest observed gap
was 0.05561 s, below 0.1 s. It monitored imports, geometry generation,
calculation, and per-case report output. Sampled RSS and the child's reported
peak are separate observations and need not coincide. This watchdog is not an
instantaneous memory guarantee. The 50 mm case retained the 500-cell cap;
the three new cases used the explicitly reviewed per-call 4,000-cell allowance.
The default 500-cell and dense 3,000-free-DOF guards are unchanged.

Validation performed:

- The 50 mm control reproduced its exact recorded C_upper, hash, 482 cells,
  and inconclusive/positive classifications before subsequent cases ran.
- All four source/config identities pinned by R007 matched. The runner
  recorded hashes of all 18 Python files under `realizability/` plus the pilot
  JSON, and required the same provenance in every child.
- The backend applied its affine/connected geometry, positive-volume,
  `volume/diameter^3 > 1e-12`, and facet-coverage guards. Independent report
  checks covered four mesh identities, facet counts, **6,351** finite local
  values, eight beta/classification calculations, configuration, and guards.
- Strict JSON, paired Markdown, false readiness, explicit inconclusive cases,
  and the physical-accuracy blocker were checked. All **22** files listed by
  the report manifest matched their SHA-256 values.
- Synthetic watchdog checks terminated a sleeping process at a 0.15 s wall
  limit and a two-process allocation at a 24 MiB RSS limit. These are runner
  checks, not fluid results. The final runner passed both checks.
- Focused ordinary-interpreter coercivity discovery: **six tests, five passed,
  one optional DOLFINx/UFL skip**. Independent mass/face quadrature, scale and
  permutation invariance, degeneracy, nonfinite classification, and the
  pre-array cell-cap refusal were covered. Runner Python syntax was checked.

The optional UFL calibration and dense/PDE suites were not repeated; no
global matrices were assembled in this task. Harmonic pilots, rendering,
encoding, and the full application suite were skipped because the corresponding
source is unchanged and those checks are outside this study. Documentation
checks cover local links/anchors, fenced Python/JSON, evidence/table consistency,
exact embedded runner bytes, and `git diff --check`.

## Next bounded task: physical accuracy and error-floor investigation

Recommend **GPT-6 Astra, high reasoning** for a quantitative accuracy review
before any new physical harmonic run. The useful certified alpha=96 cases make
this the selected next task; resolving alpha=48 by sparse analysis is deferred.
No production penalty, mesh strategy, or physical threshold is chosen here.

Read this result and appendix, the R005/R007 interpretation, the independent
swirl-reference derivation and report reviews, and the four required root
research documents. Keep R=0.10 m, H=0.15 m, nu=1e-6 m²/s, f=0.01 Hz,
U_probe=1e-7 m/s, the fixed 0.025 m disk, signed features, phasor convention,
and facet-consistent boundary target. Alpha=96 is an available certified
verification candidate on the listed hashes; alpha=48 is still unassessed by
a conclusive stability method.

The next review should deliver one quantitative error budget and one proposed
affordable experiment. Use existing source and stored reports, with bounded
reference/feature-quadrature calculations only. Reproduce the physical complex
gain and response scale; check series and quadrature sensitivity; relate
absolute complex errors to the existing 5% magnitude/5-degree comparison
criteria without silently adding or relaxing an acceptance threshold. Separate
algebraic residual/roundoff, output cancellation/quadrature, boundary-load and
faceted-geometry error, and spatial resolution. Mark quantities that cannot be
bounded from the available evidence as unknown; do not equate a small linear
residual with a small error in the disk observable. Do not equate numerical
resolution with PIV detectability or infer sensor noise that has not been specified.

Compare a targeted error/adjoint diagnostic on the existing certified operator
with a reviewed boundary-layer or symmetry-restricted accuracy investigation.
Choose one proposed follow-up with observable acceptance evidence, source/config
identity requirements, resource caps, and failure conditions. A new method
proposal is not permission to implement a different solver or boundary model
during that review. Account for the historical 25 mm direct-solve peak of
about 6.9 GiB and the failed 20 mm allocation; the present geometry-only cost
does not predict factorization cost.

Limit any new reference calculations to existing 32/64/128-term series and at
most 512-point quadrature in each integrated coordinate, with a parent-enforced
120 s total calculation budget and 1 GiB RSS. Do not generate meshes, assemble
global operators, run harmonic pilots, change physical parameters/thresholds,
or wire the certificate into the gate. Stop on reference inconsistency, a
resource cap, or completion of the accuracy review and one concrete proposed
experiment. Preserve reproducible calculation text and compact evidence.

When that review yields a fully specified mechanical diagnostic/report task,
recommend **GPT-5.6 Luna, medium**, with exact edits, focused checks, and a stop
before interpreting new numerical evidence. If method choice or scientific
interpretation remains, keep Astra/high and define the remaining bounded
question. Availability was rechecked on 2026-09-20 against the session's tool
catalog and the official [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
and [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages;
account/client picker availability may vary. No model switch, delegated
session, or automation was launched.
