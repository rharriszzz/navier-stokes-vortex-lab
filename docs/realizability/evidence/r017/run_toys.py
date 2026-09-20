"""R017 parent watchdog for serial block RHS toys; no physical execution."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

import toy_runner as support


HERE = Path(__file__).resolve().parent


def run(output, prior_seconds=0.0):
    output.mkdir(parents=True, exist_ok=False)
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    started = time.monotonic()
    deadline = started + max(0.0, 60.0 - prior_seconds)
    report = dict(status='partial', wall_limit_seconds=60.0, rss_limit_mib=512.0,
                  physical_meshes=0, pde_solves=0, matrix_factorizations=0,
                  matrix_solves=0, prior_attempt_seconds=prior_seconds, phases=[])
    support.verify_sources()
    phases = (
        ('R015_grouping_and_failure_fixtures', 'wrapper_toys.py', 'wrapper'),
        ('block_rhs_metadata_lifting_and_oracle', 'block_rhs_toys.py', 'block-rhs'),
    )
    for name, script, stem in phases:
        destination = output / stem
        watch = support.monitor([sys.executable, str(HERE / script), '--output', str(destination)],
                                deadline, 512.0, output / stem)
        phase = dict(name=name, watch=watch)
        report['phases'].append(phase)
        report['elapsed_seconds'] = prior_seconds + time.monotonic() - started
        support.write_json(output / 'report.json', report)
        if watch['stop_reason'] or watch['returncode'] != 0:
            report['status'] = 'partial_resource_or_execution_stop'
            report['failed_phase'] = name
            break
        child_name = 'toy-repair-report.json' if stem == 'wrapper' else 'block-rhs-report.json'
        child = support.read_json(destination / child_name)
        phase['child_status'] = child['status']
        if child['status'] != 'passed':
            report['status'] = 'partial_toy_failure'
            report['failed_phase'] = name
            break
    else:
        report['status'] = 'passed'
    report['elapsed_seconds'] = prior_seconds + time.monotonic() - started
    support.write_json(output / 'report.json', report)
    support.write_json(output / 'manifest.json', {
        str(path.relative_to(output)): support.sha(path)
        for path in sorted(output.rglob('*')) if path.is_file() and path.name != 'manifest.json'})
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prior-seconds', type=float, default=0.0)
    args = parser.parse_args()
    run(args.output, args.prior_seconds)
