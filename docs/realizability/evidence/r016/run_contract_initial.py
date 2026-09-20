"""R016 parent orchestration; exact R015 child code, one physical launch only."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

import toy_runner as support

HERE = Path(__file__).resolve().parent


def verify():
    preflight = support.read_json(HERE / 'preflight.json')
    assert preflight['status'] == 'passed'
    assert support.verify_sources() == preflight['source_sha256']
    for name, digest in preflight['runner_sha256'].items():
        assert support.sha(HERE / name) == digest, name


def toys():
    output = HERE / 'toys'
    output.mkdir(exist_ok=False)
    started = time.monotonic()
    deadline = started + 60.0
    record = dict(status='partial', wall_limit_seconds=60.0, rss_limit_mib=512.0,
                  physical_meshes=0, matrix_solves=0, watches={})
    phases = [
        ('watchdog', 'toy_runner.py', '--self-check', output / 'watchdog'),
        ('kernels', 'toy_runner.py', '--toy-child', output / 'kernels'),
        ('wrapper', 'wrapper_toys.py', None, output / 'wrapper'),
        ('disk', 'physical.py', '--extra-toys', output / 'disk'),
    ]
    for name, filename, flag, destination in phases:
        if name in ('kernels', 'disk'):
            destination.mkdir()
        command = [sys.executable, str(HERE / filename)]
        if flag:
            command.append(flag)
        command += ['--output', str(destination)]
        watch = support.monitor(command, deadline, 512.0, output / name)
        record['watches'][name] = watch
        record['elapsed_seconds'] = time.monotonic() - started
        support.write_json(output / 'report.json', record)
        if watch['stop_reason'] or watch['returncode'] != 0:
            record['status'] = 'prerequisite_refused'
            record['failed_phase'] = name
            break
    else:
        assert support.read_json(output / 'kernels/toy-report.json')['status'] == 'passed'
        assert support.read_json(output / 'wrapper/toy-repair-report.json')['status'] == 'passed'
        assert support.read_json(output / 'disk/extra-toys.json')['status'] == 'passed'
        check = support.read_json(output / 'watchdog/self-check.json')
        assert check['timeout']['stop_reason'] == 'wall_time_limit'
        assert check['memory']['stop_reason'] == 'rss_limit'
        assert check['memory']['largest_observed_process_tree'] >= 2
        record['status'] = 'passed'
    record['elapsed_seconds'] = time.monotonic() - started
    support.write_json(output / 'report.json', record)
    print(json.dumps(record, indent=2), flush=True)


def physical():
    toy = support.read_json(HERE / 'toys/report.json')
    assert toy['status'] == 'passed' and toy['elapsed_seconds'] < 60.0
    output = HERE / 'physical'
    output.mkdir(exist_ok=False)  # A second invocation refuses before launching.
    support.write_json(output / 'launch.json', dict(
        physical_attempt=1, wall_limit_seconds=180.0, rss_limit_mib=1536.0,
        runner_sha256=support.sha(HERE / 'physical.py'),
        parent_sha256=support.sha(Path(__file__)), toy_report_sha256=support.sha(HERE / 'toys/report.json')))
    watch = support.monitor(
        [sys.executable, str(HERE / 'physical.py'), '--child', '--output', str(output)],
        time.monotonic() + 180.0, 1536.0, output / 'physical')
    support.write_json(output / 'watch.json', watch)
    path = output / 'report.json'
    report = support.read_json(path) if path.exists() else dict(status='partial_no_child_report')
    if watch['stop_reason'] or watch['returncode'] != 0:
        report['parent_stop'] = watch
        if watch['stop_reason']:
            report['status'] = 'partial_resource_or_process_stop'
        support.write_json(path, report)
    verify()
    print(json.dumps(dict(status=report['status'], stage=report.get('stage'),
        error=report.get('error'), watch=watch,
        counts={key: report.get(key) for key in
                ('physical_meshes', 'primary_rhs', 'returned_primary_solves',
                 'correction_rhs', 'matrix_solves')}), indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('toys', 'physical'))
    args = parser.parse_args()
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    verify()
    {'toys': toys, 'physical': physical}[args.phase]()
