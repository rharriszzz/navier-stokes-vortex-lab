# R268 — Manufactured angular evidence sidecar

2026-09-26 (America/New_York), PC/WSL `daisy` retains ownership.
R267's bounded evidence contract is integrated in source. No numerical import,
assembly, solve, manager, worker, admission or allocation occurred in R268.
R266 remains INCOMPLETE; all nine allocations remain spent. The original four
physical angular terms, 30 diagnostics, gates, manifest, numerical envelope,
validators, solver and `linear_system.json` recorder are unchanged.

## Source path and semantics

The worker constructs `AngularAudit(directory, source_binding)` after source
verification and the held release, then passes it to the driver's optional
`angular_evidence` callback. The driver installs the accepted 405-value state,
computes all original degree-24/26 diagnostics and report, then invokes the
callback before returning the unchanged numerical envelope. Stage markers
record `angular_evidence` after `return_sampling_and_report`. The sidecar
writer exclusively creates `angular_audit.json` in the reserved run directory;
it never overwrites an earlier record. A physical-budget failure can still
produce the sidecar and unchanged INCOMPLETE numerical result.

`manufactured_angular.py` builds mixed `Phi=(−y,x,0)` from the collapsed
velocity interpolation and parent map, with all pressure weights zero. For
each degree it installs the final two return multipliers and eta in that
degree's Constants. It assembles the original residual vector through
`fem_petsc.assemble_vector` and reverse ghost update, before lifting, fixed-row
elimination or scaling. It independently assembles six rank-zero forms:
lateral/return advection `A_D/A_R`, lateral/return physical stress `C_D/C_R`,
prescribed return weak traction `G_R`, and UFL action of the original residual
on `Phi`. Each form is checked for domain, rank, measure and exact face tags.
There is no second Jacobian assembly or solve.

## Schema 1

The strict JSON object has exactly these top-level keys:
`schema`, `fixture`, `stage`, `source_binding`, `geometry`, `step`, `time`,
`dt`, `state`, `fixed_indices`, `fixed_values`, `phi`, and `degrees`.
`stage` is `final_accepted_state_after_newton`; the geometry is the original
n=2 mesh receipt. `state` has 405 values. The sorted fixed indices and values
cover the 240 lateral velocity entries and must agree with that state.
`phi` holds all 402 mixed coefficients, the velocity and pressure parent
maps, velocity interpolation-node coordinates and vector block size 3.
The maps partition the 402 mixed entries; coordinates and coefficients check
the angular interpolation, and pressure entries must be zero.

`degrees` has exactly `24` and `26`. Each entry has `raw_residual` (402
unscaled, uneliminated entries), `raw_receipt`, `scalar` (the six measured
forms), `scalar_receipts`, `original` (the four unchanged physical angular
terms and their defect), final three `multipliers`, `reductions` and
`comparisons`. Receipts specify assembly method, rank and every cell/face
integral. Measured zeros are retained. The pure validator refuses unknown or
missing keys, invalid dimensions/maps/coordinates, bool or nonfinite numbers,
altered fixed/state/multiplier aliases, receipts or cached reductions.
The JSON reader refuses duplicate keys; the writer uses finite JSON,
exclusive creation, fsync and a 262,144-byte cap.

The reducer uses `fsum` to compute fixed action `R_D`, nonfixed action `R_F`,
`reaction_torque_D=R_D+A_D`, `lateral_mismatch=reaction_torque_D+C_D`,
`return_mismatch=C_R−G_R`, and their reconstruction including `R_F`.
Five independent comparisons check advection, traction, raw-vector versus
scalar action, scalar action versus storage/body/return terms, and the
reconstructed versus original physical defect. Each saves terms, defect,
limit and accepted flag, using `max(1e−12,128*epsilon*sum_abs_terms)`.
Failed comparisons are retained as evidence; they do not replace the original
physical decision or change an acceptance threshold.

## Verification and limits

The [guarded result](evidence/r268/tests.json) records 123 passing source/fake
tests with no numerical modules loaded: 118 prior tests and five focused
sidecar tests. They check nontrivial maps, final constants, fixed/free actions,
scalar/vector disagreement, wrong signs and omitted terms, strict data and
exclusive persistence, callback timing, stage sequencing, and sidecar
persistence on a physical INCOMPLETE path. Saved R246/R253 validators replay
PASS; R266's validator still refuses; R267's four algebra controls reproduce.
The [preservation audit](evidence/r268/audit.json) verifies 42 unchanged old
source bindings, five intentional edits, two new source files, eleven pinned
artifacts, all 116 old raw/caller originals and Git-index bytes, 1,807 older
evidence files, nine spent reservations and recorded PID/cgroup absence.

Actual DOLFINx compilation, assembly, sidecar size/time and the signed
reaction/traction split remain unmeasured. A separate Astra/high review must
decide whether a new source/artifact-bound one-use diagnostic admission and
finite caller are justified under the original physical and resource gates.
No new attempt is admitted here.
