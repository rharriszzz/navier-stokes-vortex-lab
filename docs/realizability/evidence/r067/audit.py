"""R067 saved-data/static audit. Never imports a solver or launches a workload.

Run from the repository root with Python 3.12. Writes only review.json here.
Use --environment /path/to/environment for optional read-only local provenance.
"""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = '73416243fb9857c834d6663cca2235a116253537'
ARCHIVE = REPO / 'docs/realizability/evidence/r033'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def refuse(value):
        raise ValueError('Nonfinite JSON: ' + value)
    value = json.loads(path.read_text(), parse_constant=refuse)
    def finite(item):
        if isinstance(item, float):
            assert math.isfinite(item), path
        elif isinstance(item, dict):
            for child in item.values():
                finite(child)
        elif isinstance(item, list):
            for child in item:
                finite(child)
    finite(value)
    return value


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--environment', type=Path)
    args = parser.parse_args()
    preflight = read(ARCHIVE / 'source/preflight.json')
    for name, digest in preflight['source_sha256'].items():
        assert sha(REPO / name) == digest, name
    for name, digest in preflight['runner_sha256'].items():
        assert sha(ARCHIVE / 'source' / name) == digest, name
    # Compare every previously committed evidence file, including unmanifested
    # documentation, against the source commit; never rewrite an old audit.
    old = subprocess.check_output(['git', 'ls-tree', '-r', BASE,
        '--', 'docs/realizability/evidence'], cwd=REPO, text=True)
    preserved = 0
    for line in old.splitlines():
        meta, name = line.split('\t', 1)
        blob = meta.split()[2]
        actual = subprocess.check_output(['git', 'hash-object', '--', name],
                                         cwd=REPO, text=True).strip()
        assert actual == blob, name
        preserved += 1
    attempts = [read(ARCHIVE / f'attempts/attempt-{i:02d}/toys/report.json')
                for i in range(1, 5)]
    for i, report in enumerate(attempts, 1):
        sources = ARCHIVE / f'attempts/attempt-{i:02d}/source'
        for name, digest in read(sources / 'preflight.json')['runner_sha256'].items():
            assert sha(sources / name) == digest, (i, name)
        assert report['physical_meshes'] == report['matrix_solves'] == 0
    final = ARCHIVE / 'attempts/attempt-04/toys'
    advanced = read(final / 'advanced/advanced-report.json')
    assert advanced['status'] == 'passed'
    cases = advanced['observer_cases']
    assert len(cases) == 4
    oracles = [row for case in cases for row in case['oracle_checks']]
    assert len(oracles) == 9
    for row in oracles:
        assert row['maximum_error'] <= row['tolerance']
        assert row['pressure_lifting_norm'] > 0 and row['exact_essential']
    for case, count in zip(cases, (3, 1, 2, 3)):
        assert case['completed_rhs_assemblies'] == count
        assert case['pre_solve_observer']['calls'] == 1
        assert case['matrix_solves'] == case['attempted_primary_solves'] == 0
        assert all(v == 0 for v in case['factor_counts'].values())
        assert case['pre_solve_nullspace']['right_test_passed']
        assert case['pre_solve_nullspace']['transpose_test_passed']
    assert cases[0]['status'] == 'passed_toy_sentinel'
    assert all(c['failed_raw_unchanged'] for c in cases[1:])
    assert len(advanced['high_order']) == 4
    assert sum(len(r['facets']) for r in advanced['high_order']) == 16
    assert max(r['maximum_target_batch'] for r in advanced['high_order']) <= 256
    # Evaluate only the exact pure predicate AST, never its launch function.
    parent = ast.parse((ARCHIVE / 'source/run_contract.py').read_text())
    predicate = next(n.value for n in ast.walk(parent) if isinstance(n, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == 'prerequisites_passed'
                             for t in n.targets))
    code = compile(ast.Expression(predicate), '<archived pure predicate>', 'eval')
    accepted = lambda toy: bool(eval(code, {'toy': toy}))
    synthetic = json.loads(json.dumps(attempts[3]))
    synthetic['elapsed_seconds'] = 61.0
    stale_wall_refusal = not accepted(synthetic)
    synthetic['elapsed_seconds'] = 56.0
    synthetic['watches']['advanced']['parent_observed_peak_rss_mib'] = 600.0
    stale_rss_refusal = not accepted(synthetic)
    assert stale_wall_refusal and stale_rss_refusal and accepted(attempts[3])
    peak = max(w['parent_observed_peak_rss_mib'] for a in attempts
               for w in a['watches'].values())
    result = dict(status='review_checks_passed', physical_launch_ready=False,
        source_commit=BASE, python=sys.version.split()[0], executable=sys.executable,
        machine=dict(system=platform.system(), machine=platform.machine(),
                     hostname=platform.node(), checkout=str(REPO)),
        pinned_production_files=len(preflight['source_sha256']),
        historical_evidence_files_preserved=preserved,
        archived_observer=dict(cases=4, oracle_comparisons=9,
            high_order_facet_checks=16, all_refusals_preserve_raw=True,
            all_factor_solve_events_zero=True),
        archived_resources=dict(cumulative_seconds=attempts[3]['elapsed_seconds'],
            maximum_tree_rss_mib=peak),
        parent_predicate=dict(final_R033_report_accepted=accepted(attempts[3]),
            valid_61_second_report_refused=stale_wall_refusal,
            valid_600_mib_report_refused=stale_rss_refusal,
            scope='Pure saved/synthetic dictionary evaluation; no launch'),
        physical_sizing=dict(cells=482, velocity_dofs=9522, pressure_dofs=1928,
            real_unknowns=22900, old_points_per_facet=32**2+64**2,
            proposed_points_per_facet=64**2+96**2,
            q96_retained_basis_gradient_mib=96**2*30*(3+9)*8/1024**2,
            meaning='Array subtotal, not a process peak or LU forecast'),
        skips=['FEM mesh generation', 'quadrature evaluation', 'JIT/C compilation',
               'FEM assembly', 'factorization', 'PDE solve', 'synthetic process launches',
               'rendering', 'encoding', 'installation', 'remote Mac inspection'])
    if args.environment:
        prefix = args.environment
        package_path = next((prefix / 'conda-meta').glob('fenics-ffcx-*.json'))
        package = read(package_path)
        saved = read(REPO / 'docs/realizability/evidence/r056/ffcx_pc_environment.json')
        assert package['sha256'] == saved['conda_package_record']['sha256']
        names = ('ffcx/ir/representation.py', 'ffcx/naming.py',
                 'ffcx/codegeneration/jit.py', 'ffcx/codegeneration/ufcx.h')
        files = {}
        for row in package['paths_data']['paths']:
            if row['_path'].endswith(names):
                digest = sha(prefix / row['_path'])
                assert digest == row['sha256_in_prefix'], row['_path']
                files[row['_path']] = digest
        assert len(files) == 4
        representation = prefix / 'lib/python3.12/site-packages/ffcx/ir/representation.py'
        text = representation.read_text()
        assert 'grouped_integrands[cell_type][rule].append(integral.integrand())' in text
        assert 'integrands_summed = sorted_expr_sum(integrands)' in text
        caches = read(ARCHIVE / 'cache_metadata.json')['attempts']
        cache_checks = {}
        for attempt in ('attempt-02', 'attempt-03'):
            entry = caches[attempt]
            cache_path = Path(entry['cache_path'])
            present = [(cache_path / r['path'], r['sha256']) for r in entry['files_after_run']]
            available = all(p.exists() for p, _ in present)
            if available:
                assert all(sha(p) == digest for p, digest in present)
            cache_checks[attempt] = dict(available=available, recorded_files=len(present),
                                         all_hashes_match=available)
        global_cache = Path.home() / '.cache/fenics'
        entries = [p for p in global_cache.glob('*') if p.is_file()]
        result['environment'] = dict(prefix=str(prefix),
            ffcx={k: package[k] for k in ('version', 'build', 'url', 'sha256')},
            package_files_verified=files, patched_accumulation_present=True,
            local_task_caches=cache_checks,
            global_cache=dict(files=len(entries),
                earliest_mtime_utc=datetime.fromtimestamp(min(p.stat().st_mtime for p in entries),
                    timezone.utc).isoformat() if entries else None,
                limitation='Timestamps do not bind a loaded binary to a historical solve'))
    (HERE / 'review.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
