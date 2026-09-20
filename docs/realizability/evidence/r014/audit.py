"""Read-only R014 stored-evidence audit. Standard library; no FEM or integration."""
import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import subprocess

ROOT=Path.cwd()
E=ROOT/'docs/realizability/evidence/r014'
def read(path):
    return json.loads(path.read_text(),parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
manifest=read(E/'archive_manifest.json')
for name,item in manifest.items():
    assert sha(E/name)==item['archived_sha256'],name
    original=Path(item['original_path'])
    if original.exists():
        assert sha(original)==item['original_sha256'],name
        if original.suffix=='.json':assert read(original)==read(E/name)
for p in E.glob('*.py'):ast.parse(p.read_text())
r=read(E/'physical__report.json')
t=read(E/'toy__toy-report.json')
w=read(E/'physical__watch.json')
tw=read(E/'toy__toy-watch.json')
ew=read(E/'physical__extra-toys-watch.json')
assert r['status']=='partial_failed' and r['error']['type']=='ValueError'
assert r['error']['message']=='need at least one array to concatenate'
assert (r['physical_meshes'],r['primary_rhs'],r['correction_rhs'],r['matrix_solves'])==(1,1,0,1)
assert not r['outputs'] and r['campaign_ready'] is r['physical_gate_passed'] is False
assert w['returncode']==1 and w['stop_reason'] is None
assert w['elapsed_seconds']<180 and w['parent_observed_peak_rss_mib']<1536
assert tw['elapsed_seconds']+ew['elapsed_seconds']<60
assert max(tw['parent_observed_peak_rss_mib'],ew['parent_observed_peak_rss_mib'])<512
assert tw['returncode']==ew['returncode']==0 and tw['stop_reason'] is ew['stop_reason'] is None
assert len(r['source_sha256'])==19
for name,digest in r['source_sha256'].items():assert sha(ROOT/name)==digest
for name,digest in r['runner_sha256'].items():assert sha(E/name)==digest
assert sha(E/'toy_runner.py')==t['runner_sha256']
assert sha(E/'kernels.py')==t['kernels_sha256']
assert len(t['load_toys'])==24
assert {tuple(row['permutation']) for row in t['load_toys']}==set(itertools.permutations(range(4)))
bound=read(E/'physical__local_bound.json')
assert len(bound['cell_trace_eigenvalues'])==482 and all(math.isfinite(x) for x in bound['cell_trace_eigenvalues'])
assert bound['C_upper']==58.12657123078638
assert r['certificate']['classification']['beta']==1-math.sqrt(r['certificate']['C_safe']/96)
regions=read(E/'physical__disk_regions.json')
assert len(regions)==11 and len({x['cell'] for x in regions})==11
for i,(expected,tolerance) in enumerate(zip(r['disk_partition']['expected_moments'],r['disk_partition']['arithmetic_tolerances'])):
    total=math.fsum(x['moments']['moments'][i] for x in regions)
    assert total==r['disk_partition']['dimensionless_moments'][i]
    assert abs(total-expected)<=tolerance
assert r['disk_partition']['denominator_m4']==math.pi*.025**4/2
assert not r['coincident_interior_facets']
facet_summary={}
for name in ('A_32','A_64'):
    rows=read(E/('physical__'+name+'_facets.json'))
    assert len(rows)==282 and len({x['facet'] for x in rows})==282
    max_residual=0.
    for row in rows:
        assert abs(math.fsum(x*x for x in row['normal'])-1)<256*math.ulp(1.)
        M=row['mass']; c=list(map(lambda x:complex(*x),row['coefficients']))
        target=list(map(lambda x:complex(*x),row['projection_moments']))
        for i in range(6):
            value=sum(M[i][j]*c[j] for j in range(6))
            scale=sum(abs(M[i][j]*c[j]) for j in range(6))+abs(target[i])
            residual=abs(value-target[i]);max_residual=max(max_residual,residual)
            assert residual<=256*math.ulp(1.)*scale
    signed=[math.fsum(row['signed_flux_si'][i] for row in rows) for i in range(2)]
    absolute=[math.fsum(row['absolute_flux_si'][i] for row in rows) for i in range(2)]
    # Original sums multiplied U after reduction; compare fixed absolute-contribution scale.
    for i in range(2):
        assert abs(signed[i]-r['loads'][name]['signed_flux_si'][i])<=256*math.ulp(1.)*absolute[i]
        assert abs(absolute[i]-r['loads'][name]['absolute_flux_si'][i])<=256*math.ulp(1.)*absolute[i]
        assert r['loads'][name]['flux_ratios'][i]<1e-8
    facet_summary[name]=dict(facets=len(rows),maximum_projection_equation_residual=max_residual,
                            signed_flux_si_fsum=signed,absolute_flux_si_fsum=absolute)
old_text=(ROOT/'docs/realizability/B2_PHYSICAL_RESPONSE_EVIDENCE.md').read_text()
old=json.loads(re.search(r'^## Complete calculation report\n\n```json\n(.*?)^```',old_text,re.M|re.S).group(1))
new=dict(r['P_diagnostics']); previous=dict(old['solver'])
new.pop('elapsed_seconds');previous.pop('elapsed_seconds')
assert new==previous
p=r['P_diagnostics']
assert p['real']['divergence_ratio']<1e-3 and p['imaginary']['divergence_ratio']<1e-3
assert p['corrected_flux_ratio']<1e-8 and p['real']['algebraic_residual']<1e-9
assert max(p['real']['boundary_dof_residual'],p['imaginary']['boundary_dof_residual'])<1e-14
watchdog=read(E/'toy__watchdog__self-check.json')
assert watchdog['timeout']['stop_reason']=='wall_time_limit'
assert watchdog['memory']['stop_reason']=='rss_limit'
assert watchdog['memory']['largest_observed_process_tree']>=2
for item in r['physical_UFL_validation']:
    assert item['maximum_coefficient_difference']<=item['tolerance']
# Every pre-existing evidence appendix remains identical to the starting commit.
prior_evidence=['B2_MATCHED_TRACE_EVIDENCE.md','B2_PHYSICAL_RESPONSE_EVIDENCE.md',
                'B2_ACCURACY_EVIDENCE.md','B2_RESPONSE_COERCIVITY_EVIDENCE.md']
for name in prior_evidence:
    path='docs/realizability/'+name
    assert (ROOT/path).read_bytes()==subprocess.check_output(['git','show','d5a2711:'+path])
result=dict(status='passed',archived_files=len(manifest),source_identities=19,
    vertex_permutations=24,polynomial_vector_traces_per_permutation=30,
    facet_projection_records=facet_summary,local_certificate_values=482,disk_regions=11,
    prior_P_diagnostics_exactly_reproduced_except_timing=True,
    physical_child_seconds=w['elapsed_seconds'],physical_peak_rss_mib=w['parent_observed_peak_rss_mib'],
    toy_total_seconds=tw['elapsed_seconds']+ew['elapsed_seconds'],
    no_FEM_import_mesh_assembly_solve_reference_or_field_integration=True)
(E/'stored_validation.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps(result,indent=2))
