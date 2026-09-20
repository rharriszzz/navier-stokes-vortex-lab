# B2 matched-trace method review: read-only evidence

Recorded 2026-09-20 for [R013](../../REQUEST_LOG.md#r013--2026-09-20--short-continuation-request)
against `568c68b6844f820d49ce4be92ff987e367270fdb`.
Read the [review and proposed experiment](B2_MATCHED_TRACE_REVIEW.md).
**No new physical calculation was executed.** The inventory below describes
future work, not completed solves or measured cost. Its cap-to-prior-RSS ratio
is elementary arithmetic, not a forecast or resource guarantee.

The executed standard-library script checks embedded R012 report/runner hashes,
19 unchanged numerical source/configuration hashes and existing appendix
identities. It computes only elementary penetration, chord and disk scales and
checks the separated equation's coefficient identity. It does not import the
numerical package, evaluate a Bessel function, generate a mesh, reintegrate
stored fields, assemble a system or solve a PDE. The R012 runner is parsed,
not executed. The polynomial dimensions and Green identity are mathematical
properties, not validation of any future integration implementation.

Temporary execution records: `/tmp/navier-b2-method-r013/review_checks.py` and
`review_checks.json`. The exact bytes are preserved below. To repeat these
read-only checks from the repository root, extract the script, create its
`/tmp/navier-b2-method-r013` output directory if absent, and run `python3` on it.
After committing, only the recorded Git HEAD value is expected to differ.
The subsequent documentation check is described in the request log; it also
performs no flow calculation.

Script SHA-256: `764eca71adc53213a4477713b2e74fa8f74b2af8e739efa74c071ed4417ecac1`.

Report SHA-256: `095d452a0ae84bd5d4fc8dc13dc545936baa54c70fc3cfaa8b46ca8926c466e8`.

## Read-only review report

```json
{
  "scope": "R013 source/report identities and elementary arithmetic only",
  "commit": "568c68b6844f820d49ce4be92ff987e367270fdb",
  "source_sha256": {
    "realizability/__init__.py": "197df2cae0b7fcc3908afebfd9359b21244fc8aa0460b0167af04a2f1c7f219c",
    "realizability/backends/__init__.py": "8b40aa33331d5a627dbd4aa1681f9da523a21e31e2b0e71f48203967481f20b2",
    "realizability/backends/b1_verification.py": "287512f423a3c147c009802c2de9d6cf11538d3c80fc3fbc98dffaf586bb1e5c",
    "realizability/backends/b2_coercivity.py": "be10e484ffd5c36aef45962242dea2bcaaaa3cbad37df83e297fcc366bf96bcc",
    "realizability/backends/b2_gate.py": "3151ac8a85de4b242e53b28a3d2815d7ecf5e8e6ed8c654f440aa5a8778a6d05",
    "realizability/backends/b2_stability.py": "18b2e75712255a681a0c22f012d81ab3a129e147c41f3f8974bb46cf6a8df9f1",
    "realizability/backends/b2_verification.py": "42e11041c5f1edbca13737010456247f059d92e874a9398454bf4b6f17498d25",
    "realizability/backends/fem_observables.py": "f5dbc8a47d2f5c61d9228daf49c80ae1011ab542ee12335398a52eaf89ed0a64",
    "realizability/backends/fenicsx_stokes.py": "37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206",
    "realizability/backends/hdiv_stokes.py": "f23b252f91c406e3e279c7e6e7049e301ad604fae232dd0a610a73319864d2e9",
    "realizability/boundary_modes.py": "586d2667b8ac4b6a460d590afc884a05be5f9843484df74de8a4568261f84d18",
    "realizability/cli.py": "c163e6a3dc8e6a2c08c7dc48a7205624947fce938dea1aec3489ef62135bd850",
    "realizability/config.py": "3cb3edbb28e203226056cf4ac5e7832951c33e5f932b13a5ec438de88c786d12",
    "realizability/observables.py": "428fd794b00669593f87b694bca10a94454ccbd9ee012fa656a61c7b30375a05",
    "realizability/reference.py": "7f032634768a3f8b8a7a649e4d83dc45fd6f969a1c1ba679d1628867d2f13305",
    "realizability/response.py": "5318e4d6ea917433909e6e9718c90ed9cf48a5ee4b779b4446b83b3452d71317",
    "realizability/sensors.py": "c93cd68cc902970f27ecdce7deb1d272f146890cfe99b076b87e190222483d9a",
    "realizability/swirl_reference.py": "375e057ff365858cb5dc698e1b397eb34b18a9898d5a82482e2391ea11d81e4a",
    "configs/realizability/pilot.json": "0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0"
  },
  "r012_report_sha256": "16da2b4a410fa08291a86c50454e13f4cfd57f183bc671d0d53e45e313d10b2c",
  "r012_runner_sha256": "fcb8dfedfa4f9049ea6c321f3082ada7666219e90cbcfce234222357901d94bb",
  "source_evidence_sha256": {
    "docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md": "6df3054efca3f4b69114f64688faca9d1ea7ac7be239d5ea50fb1883ed970463",
    "docs/realizability/B2_ACCURACY_EVIDENCE.md": "df4c6d26836448b84a402c0d9a9a59bc6086abea02c58690422f6de68edefcb2",
    "docs/realizability/B2_RESPONSE_COERCIVITY_EVIDENCE.md": "0dd1fc98091a4c0838544d817c38863d2533da11ccd2ed74b78bcf34f159d02d"
  },
  "scales": {
    "omega_per_s": 0.06283185307179587,
    "penetration_depth_m": 0.005641895835477563,
    "radius_minus_disk_over_delta": 13.293403881791372,
    "nominal_h_over_delta": 8.86226925452758,
    "boundary_spacing_heuristic_m": 0.0014104739588693908,
    "illustrative_50mm_chord_sagitta_m": 0.00317541634481458,
    "illustrative_sagitta_over_delta": 0.562827892859492,
    "disk_area_m2": 0.001963495408493621,
    "disk_denominator_m4": 6.135923151542566e-07,
    "reference_magnitude_per_m": 6.911220198253779e-05,
    "five_percent_scale_per_m": 3.4556100991268897e-06,
    "output_component_screen_per_m": 3.4556100991268895e-08,
    "load_component_screen_per_m": 3.4556100991268895e-07,
    "output_component_screen_physical_per_s": 3.4556100991268893e-15,
    "phase_amplitude_reference_pass_conditions": "strict magnitude relative error <0.05 and wrapped phase <5 degrees"
  },
  "proposed_inventory": {
    "meshes": 1,
    "cells": 482,
    "velocity_dofs": 9522,
    "pressure_dofs": 1928,
    "total_real_block_unknowns": 22900,
    "penalty": 96,
    "symbolic_factorizations": 1,
    "numerical_factorizations": 1,
    "primary_rhs": 3,
    "residual_correction_rhs": 3,
    "total_matrix_solves": 6,
    "boundary_duffy_orders": [
      32,
      64
    ],
    "max_reference_terms": 128,
    "max_reference_points_per_batch": 256,
    "reference_complex_array_mib": 0.5,
    "total_watched_wall_seconds": 180,
    "active_child_tree_rss_mib": 1536,
    "nominal_poll_seconds": 0.05
  },
  "comparisons": {
    "measured_r012_wall_seconds": 38.754202111013,
    "measured_r012_peak_mib": 753.05078125,
    "historical_25mm_peak_mib": 6931.1,
    "cap_over_measured_r012_rss": 2.03970308277268,
    "factor_cost_forecast": "none: same-size factorization evidence only; new loading/output cost unmeasured"
  },
  "arithmetic_checks": {
    "moment_count": 10,
    "bdm_cell_dimension": 30,
    "facet_normal_dimension": 6,
    "separated_pde_coefficient_identity": true
  },
  "skipped": [
    "mesh generation",
    "FEM imports",
    "assembly",
    "PDE solves",
    "reference field/series evaluation",
    "stored field reintegration",
    "solver implementation",
    "rendering",
    "encoding"
  ]
}
```

## Exact read-only script

```python
"""R013 read-only identities and elementary scales; no mesh/FEM/reference evaluation."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

root=Path.cwd()
output=Path('/tmp/navier-b2-method-r013')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def block(path,heading,language):
    content=path.read_text()
    return re.search(r'^## '+re.escape(heading)+r'\n\n```'+language+r'\n(.*?)^```',content,re.M|re.S).group(1)
report_path=root/'docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md'
report_text=block(report_path,'Complete calculation report','json')
r=json.loads(report_text)
assert hashlib.sha256(report_text.encode()).hexdigest()=='16da2b4a410fa08291a86c50454e13f4cfd57f183bc671d0d53e45e313d10b2c'
runner=block(report_path,'Exact runner','python')
assert hashlib.sha256(runner.encode()).hexdigest()=='fcb8dfedfa4f9049ea6c321f3082ada7666219e90cbcfce234222357901d94bb'
ast.parse(runner)
assert len(r['provenance']['source_sha256'])==19
for name,digest in r['provenance']['source_sha256'].items(): assert sha(root/name)==digest,name
assert r['mesh']['cells']==482 and r['parameters']['penalty_factor']==96
assert r['status']=='complete' and r['campaign_ready'] is False
R,H,nu,f,U,d,h=.1,.15,1e-6,.01,1e-7,.025,.05
omega=2*math.pi*f
delta=math.sqrt(2*nu/omega)
G=complex(*r['reference']['gain_per_m'])
E5=.05*abs(G)
# An illustrative chord, not a mesh measurement or a generated geometry.
sagitta=R-math.sqrt(R*R-(h/2)**2)
# BDM2 has dim(P2^3)=30; facet normal traces have dim(P2 on triangle)=6.
assert 3*math.comb(2+3,3)==30 and math.comb(2+2,2)==6
# Green moment identity derivative: d/dx [x^(a+1)y^b/(a+1)] = x^a y^b.
moments=[(a,b) for a in range(4) for b in range(4-a)]
assert len(moments)==10
# The separated radial differential equation implies nu*(lambda^2-k^2)=i*omega.
# Check the coefficient identity at a representative mode using elementary arithmetic,
# without evaluating a Bessel function or constructing a reference field.
k=.5*math.pi/H
lambda_squared=complex(k*k,omega/nu)
assert abs(nu*(lambda_squared-k*k)-1j*omega)<1e-16
record=dict(
 scope='R013 source/report identities and elementary arithmetic only',
 commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 source_sha256=r['provenance']['source_sha256'],
 r012_report_sha256=hashlib.sha256(report_text.encode()).hexdigest(),
 r012_runner_sha256=hashlib.sha256(runner.encode()).hexdigest(),
 source_evidence_sha256={str(path.relative_to(root)):sha(path) for path in [
 report_path,root/'docs/realizability/B2_ACCURACY_EVIDENCE.md',
 root/'docs/realizability/B2_RESPONSE_COERCIVITY_EVIDENCE.md']},
 scales=dict(omega_per_s=omega,penetration_depth_m=delta,
 radius_minus_disk_over_delta=(R-d)/delta,nominal_h_over_delta=h/delta,
 boundary_spacing_heuristic_m=delta/4,
 illustrative_50mm_chord_sagitta_m=sagitta,illustrative_sagitta_over_delta=sagitta/delta,
 disk_area_m2=math.pi*d*d,disk_denominator_m4=math.pi*d**4/2,
 reference_magnitude_per_m=abs(G),five_percent_scale_per_m=E5,
 output_component_screen_per_m=E5/100,load_component_screen_per_m=E5/10,
 output_component_screen_physical_per_s=U*E5/100,
 phase_amplitude_reference_pass_conditions='strict magnitude relative error <0.05 and wrapped phase <5 degrees'),
 proposed_inventory=dict(meshes=1,cells=482,velocity_dofs=9522,pressure_dofs=1928,
 total_real_block_unknowns=2*(9522+1928),penalty=96,symbolic_factorizations=1,
 numerical_factorizations=1,primary_rhs=3,residual_correction_rhs=3,
 total_matrix_solves=6,boundary_duffy_orders=[32,64],max_reference_terms=128,
 max_reference_points_per_batch=256,reference_complex_array_mib=128*256*16/1024**2,
 total_watched_wall_seconds=180,active_child_tree_rss_mib=1536,
 nominal_poll_seconds=.05),
 comparisons=dict(measured_r012_wall_seconds=38.754202111013,
 measured_r012_peak_mib=753.05078125,historical_25mm_peak_mib=6931.1,
 cap_over_measured_r012_rss=1536/753.05078125,
 factor_cost_forecast='none: same-size factorization evidence only; new loading/output cost unmeasured'),
 arithmetic_checks=dict(moment_count=len(moments),bdm_cell_dimension=30,
 facet_normal_dimension=6,separated_pde_coefficient_identity=True),
 skipped=['mesh generation','FEM imports','assembly','PDE solves','reference field/series evaluation',
          'stored field reintegration','solver implementation','rendering','encoding'])
(output/'review_checks.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
print(json.dumps({key:record[key] for key in ['scales','proposed_inventory','comparisons','arithmetic_checks']},indent=2))
```
