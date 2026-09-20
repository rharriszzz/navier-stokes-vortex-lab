# B2 continuation review: reference evidence and report contract

Prepared 2026-09-20 for [request R001](../../REQUEST_LOG.md), against source
commit `705b89f`. Only documentation changed during this review. It follows the
completed [acceptance repair](B2_GATE_REVIEW.md#2026-09-20-implementation-result).

## Decision and bounded plan

The repaired rejection path and small-cylinder energy checks reproduce their
recorded results. The next implementation should make physical-reference
discrepancies and campaign blockers explicit in machine-readable reports, and
repair undefined gain comparisons. This bounded diagnostic/report package
precedes selecting an affordable method to audit actual response operators.

Retain the rest Stokes operating point, BDM2/DG1 formulation, facet-consistent
boundary target, physical viscosity/frequency, signed features, and existing
5%/5-degree refinement criteria. The smooth-cylinder series remains an
independent symmetry-restricted reference. No production solver, mesh, penalty
certificate, actuator, or sensor design is selected here.

Alternatives for the subsequent research review include sparse constrained
eigenanalysis and a sufficient coercivity certificate for the assembled viscous
form. Positivity on the whole homogeneous-normal velocity space would imply
positivity on its divergence-free subspace; a negative direction outside that
subspace would not by itself prove constrained instability. A sparse calculation
must establish which part of the spectrum it tests and report residuals. A
positive eigenvalue near a chosen shift does not establish a positive minimum.
These are method-review requirements, not implementation instructions for the
cheaper coding model.

## Repaired checks reproduced

- Ordinary discovery: **41 tests, 29 passed, 12 optional DOLFINx skips**.
- Optional B2 discovery: **18 tests passed**, including numerical fixtures.
- The real alpha=6/48 rejection command wrote strict JSON and Markdown,
  retained a false gate, and reported downstream stages as not run. Its report
  has no pilot records. The command exits successfully because it produced a
  report; exit status zero does not mean the scientific gate passed.

| Mesh (m) | Penalty | Minimum decay rate (1/s) | Spectral check | Independent step |
|---:|---:|---:|:---:|:---|
| 0.10 | 6 | -0.0838845803371 | fail | not run |
| 0.10 | 48 | +0.00185910664480 | pass | not run |
| 0.07 | 6 | -0.0341772362200 | fail | prediction agreement passes; energy grows |
| 0.07 | 48 | +0.00168736418397 | pass | prediction agreement passes; energy decays |

The 70 mm measured energy ratios were 1.072025523823309 and
0.996633794049131, with step residuals below 1.9e-15. Agreement for the unstable
case correctly does not make its overall stability decision pass. The audit
took 11.12 s and peaked at 759.84 MiB RSS in this run; costs depend on caches
and environment. These results concern only the stated small fixtures.

## Actual mesh inventory rules out extending the dense audit

Created the existing cylinder meshes and finite-element spaces, counted DOFs,
and calculated storage estimates. No PDE matrix or new production response
was assembled for this inventory.

| Mesh (m) | Cells | Total velocity DOFs | Free velocity DOFs | Pressure DOFs | One dense free-velocity matrix (GiB) |
|---:|---:|---:|---:|---:|---:|
| 0.050 | 482 | 9,522 | 7,830 | 1,928 | 0.457 |
| 0.040 | 873 | 17,028 | 14,400 | 3,492 | 1.545 |
| 0.030 | 1,842 | 35,226 | 31,086 | 7,368 | 7.200 |
| 0.025 | 3,154 | 59,904 | 53,640 | 12,616 | 21.437 |

The storage column is `8*n_free**2/1024**3`, not a peak-memory estimate.
The implementation first assembles dense matrices with all velocity DOFs,
then constructs additional nullspace and projected matrices. Its actual memory
demand would be greater. Even the 50 mm verification fixture exceeds the
existing 3,000-free-DOF guard. Keep that guard.

Mesh SHA-256 values, in the same order:

```text
0.050: 423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4
0.040: a7006604f0da3df5c8b9f92aaf0e8f1eaae8522554c4378e1e9ce1369a85e59b
0.030: 9096deae45c24dcdb028082e2b971fb197657574e1b43af71a9ec036dc2ff7bf
0.025: 42fa3aac5c2bc762514c5cadb642edc2a1a8acfdf81ea9df7df992b696a04895
```

## Physical reference confirms the historical discrepancy

Using `disk_rotation_gain` with R=0.10 m, H=0.15 m, disk radius=0.025 m,
nu=1e-6 m²/s, and f=0.01 Hz gives

```text
G_ref = 2.0662858857221785e-5 - 6.595106312048072e-5 i  [1/m]
|G_ref| = 6.911220198253779e-5  [1/m]
|Omega| at U_probe=1e-7 m/s = 6.911220198253779e-12  [1/s].
```

The 32-, 64-, and 128-term results agree at the precision returned in this
run. This is a series-convergence observation, not a rigorous zero-error bound.

Compared with the stored historical alpha=6 pilot:

| Mesh (m) | Absolute complex error (1/m) | Complex error / reference magnitude |
|---:|---:|---:|
| 0.040 | 0.0758341200955 | 1097.261 |
| 0.030 | 0.0207099217756 | 299.657 |
| 0.025 | 0.0182041133724 | 263.399 |

These are dimensionless ratios, not percentages. Complex error differs from
the magnitude ratios in the original reference review. The historical report
predates the boundary and penalty repairs; this table cannot diagnose the
current backend or isolate geometry, loading, stability, and resolution errors.

The stored artifact is ignored generated data, not required for a fresh clone.
Its SHA-256 is
`b3f1ebde3577fb400ea56ecf3bab0e36b9dbc4d889135bf915c2c42e5017d2bd`.
It records commit `ab268b2` with a dirty tree and an incomplete source-hash set;
do not relabel it as a new run. New unit checks must use explicit synthetic
inputs and the independent reference without depending on this local file.

## Additional report defect reproduced without CFD

`b2_gate._comparison(0j, 0j)` returns an infinite phase difference.
A nonfinite input returns NaN diagnostics. Both correctly fail the Boolean
comparison, but `json.dumps(..., allow_nan=False)` raises `ValueError`.
This prevents an unresolved comparison from being written as a strict report.
A valid equal nonzero pair serializes normally. Reproduce with ordinary Python:

```bash
python3 - <<'PY'
import json
from realizability.backends.b2_gate import _comparison
for left, right in [(0j, 0j), (complex(float('nan'), 0), 1+0j), (1+0j, 1+0j)]:
    result = _comparison(left, right)
    print(result)
    try:
        json.dumps(result, allow_nan=False)
    except ValueError as error:
        print(type(error).__name__, str(error))
PY
```

Source inspection also shows that a passing legacy aggregate produces
`campaign_blocked_reason=null` even though actual response-mesh stability and
physical-reference accuracy are unassessed. Markdown limitations alone do not
give an automated reader explicit remaining blockers. No campaign launcher exists.

## Next package: routine diagnostic implementation

Recommended model: **GPT-5.6 Luna, medium reasoning**. This recommendation is
for the explicit contract below. The
[official model guidance](https://learn.chatgpt.com/docs/models) describes Luna
as suitable for clear, repeatable tasks and explains model/effort selection.
Use the available model picker or CLI `/model`; these files do not switch it.

1. Repair scalar gain comparisons and affected Markdown formatting. Preserve
   the existing finite, nonzero 5%/5-degree behavior. Represent undefined phase
   or invalid numbers with JSON null plus validity flags and reasons; those
   inputs must fail acceptance. Zero response can have valid absolute error
   but no phase. Cover zero/zero, one zero, nonfinite real or imaginary parts,
   and arithmetic overflow with strict JSON regressions. Apply the same policy
   to the gate's complex feature records. Do not invent a small-response cutoff
   or turn undefined phase into zero.
2. Add an independent physical-reference diagnostic to completed B2 gate
   reports, using existing `disk_rotation_gain`, actual config R/H/nu,
   f=0.01 Hz, and the existing fixed 0.025 m disk. Record units, harmonic
   convention, series terms, 64-to-128-term difference, and complex gain.
   Compare every existing T_00c pilot and penalty-comparison gain against it:
   absolute complex error, relative complex error, relative magnitude error,
   and wrapped phase difference where defined. Add no harmonic solves. A
   shared helper may serve the changed-parameter verification fixture, which
   must retain its separate label and parameters. Keep SciPy optional for B0
   and for the early stability-rejection branch.
3. Record absolute complex changes for existing mesh, penalty, and quadrature
   comparisons. They are observed sensitivities, not proven error bounds.
   Do not assert phase or small responses are resolved because adjacent meshes
   agree or because the reference series converges.
4. Add `campaign_ready=false` and a nonempty `campaign_blockers` list to
   rejected and completed reports. Record actual response-mesh stability as
   `not_assessed`, including requested meshes/penalties, and retain physical
   accuracy/error-floor review as a blocker. Preserve the legacy
   `all_numerical_gates_passed` definition and label which existing checks it
   aggregates. A passing legacy aggregate must not clear
   `campaign_blocked_reason` while blockers remain. Bump the gate schema and
   document new fields. This package has no path to set campaign readiness true.
5. Add dependency-free tests with synthetic results for a completed gate.
   Show that mutually agreeing gains far from the reference expose the error
   and remain blocked; no extra harmonic solves are requested; a synthetic
   reference match still lacks production-stability evidence; and rejection
   calls neither harmonic solves nor the SciPy reference. Test absolute-error
   calculations independently. Retain real small-mesh regressions and the
   rejection report check. Synthetic results are not CFD evidence. Tests must
   run in a fresh clone without ignored reports.
6. Append implementation evidence here and update `B2_GATE.md`,
   `PROJECT_TRACKS.md`, `SESSION_HANDOFF.md`, and `REQUEST_LOG.md`. Run the
   commands below. Stop once this package and its checks are complete.

Complete provenance remains a separate follow-up. Include newly used source
modules in the existing gate hash list without expanding into a general
metadata rewrite. No production sweep, default successful `b2-gate` run,
`b2-verify` refinement, B3 work, or physical threshold change belongs here.

Recommend **GPT-6 Astra, high reasoning**, next to review the diagnostics and
choose a bounded, scalable test of actual response-operator stability. That
review must specify method, calibration against dense small fixtures,
memory/runtime budget, convergence evidence, and failure conditions before
implementation. Stop earlier with evidence if numerical results contradict
this review or progress requires a scientific change. An understood coding
defect may be fixed within this package. Recheck model availability when
handing off; do not substitute silently.

## Validation commands and evidence

From the repository root:

```bash
python3 -W error -m unittest discover -s tests/realizability -v
python3 -m realizability.cli --help
# Optional environment from B1_SETUP.md; this path is machine-local.
/tmp/navier-fenicsx/bin/python -m unittest discover \
  -s tests/realizability -p 'test_b2*.py' -v
/tmp/navier-fenicsx/bin/python -m realizability.cli b2-gate \
  --config configs/realizability/pilot.json --mesh-sizes 0.10 0.07 \
  --penalty-factor 6 --comparison-penalty-factor 48 \
  --output-dir /tmp/navier-b2-next-diagnostic-rejection
git diff --check
```

Check contents, not just exit status: strict JSON and Markdown must exist;
stability and readiness must remain false; later solves must be not run.
If the optional environment is absent, record skips and the pending PDE check
rather than claiming success or changing backend. Use a fresh output directory.

This review's temporary evidence is in
`/tmp/navier-b2-continuation-rejection-20260920/gate.{json,md}` and
`/tmp/navier-b2-continuation-mesh-inventory.json`. Reproduction does not depend
on those paths surviving. Runtime: DOLFINx/Basix/FFCx 0.10.0, UFL 2025.2.1,
Gmsh 4.15.2, PETSc 3.25.5 real float64, MPICH 5.0.1, NumPy 2.5.3, SciPy 1.18.1.
Portable setup is in [B1_SETUP.md](B1_SETUP.md).

Reproduce the mesh inventory in the optional environment with:

```python
import numpy as np
from dolfinx import fem, mesh as dmesh
from realizability.config import PilotConfig
from realizability.backends.fenicsx_stokes import create_cylinder, _mesh_sha256
from realizability.backends.hdiv_stokes import create_hdiv_spaces

for size in (0.05, 0.04, 0.03, 0.025):
    domain, _, _ = create_cylinder(PilotConfig(), size)
    V, Q = create_hdiv_spaces(domain)
    domain.topology.create_connectivity(2, 3)
    boundary = fem.locate_dofs_topological(V, 2, dmesh.exterior_facet_indices(domain.topology))
    total = V.dofmap.index_map.size_global * V.dofmap.index_map_bs
    free = total - len(np.unique(boundary))
    print(size, domain.topology.index_map(3).size_global, total, free,
          Q.dofmap.index_map.size_global, 8*free**2/1024**3, _mesh_sha256(domain))
```
