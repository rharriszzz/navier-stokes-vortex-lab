"""R018 orchestration of unchanged R017 children with original R013 caps/stops."""
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
        ('watchdog', 'toy_runner.py', '--self-check', 'self-check.json'),
        ('kernels', 'toy_runner.py', '--toy-child', 'toy-report.json'),
        ('wrapper', 'wrapper_toys.py', None, 'toy-repair-report.json'),
        ('block-rhs', 'block_rhs_toys.py', None, 'block-rhs-report.json'),
        ('disk', 'physical.py', '--extra-toys', 'extra-toys.json'),
    ]
    for name, filename, flag, report_name in phases:
        destination = output / name
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
        child = support.read_json(destination / report_name)
        if name == 'watchdog':
            assert child['timeout']['stop_reason'] == 'wall_time_limit'
            assert child['memory']['stop_reason'] == 'rss_limit'
            assert child['memory']['largest_observed_process_tree'] >= 2
        else:
            assert child['status'] == 'passed'
    else:
        record['status'] = 'passed'
    record['elapsed_seconds'] = time.monotonic() - started
    support.write_json(output / 'report.json', record)
    print(json.dumps(record, indent=2), flush=True)


def physical():
    toy_path = HERE / 'toys/report.json'
    toy = support.read_json(toy_path)
    assert toy['status'] == 'passed' and toy['elapsed_seconds'] < 60.0
    assert len(toy['watches']) == 5
    assert all(w['returncode'] == 0 and w['stop_reason'] is None
               and w['parent_observed_peak_rss_mib'] < 512 for w in toy['watches'].values())
    output = HERE / 'physical'
    output.mkdir(exist_ok=False)
    support.write_json(output / 'launch.json', dict(
        physical_attempt=1, wall_limit_seconds=180.0, rss_limit_mib=1536.0,
        runner_sha256=support.sha(HERE / 'physical.py'),
        parent_sha256=support.sha(Path(__file__)), toy_report_sha256=support.sha(toy_path)))
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
