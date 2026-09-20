"""R022 conditional q64/q96 experiment under the R021 contract and fixed caps."""
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
        ('parent-refusal', 'run_contract.py', 'parent-refusal', 'parent-report.json'),
        ('advanced', 'advanced_toys.py', None, 'advanced-report.json'),
    ]
    wrong_root = output / 'wrong-root'
    wrong_root_cwd = output / 'invalid-working-directory'
    wrong_root_cwd.mkdir()
    wrong_root_watch = support.monitor(
        [sys.executable, str(HERE / 'wrapper_toys.py'), '--output', str(wrong_root)],
        deadline, 512.0, output / 'wrong-root', cwd=wrong_root_cwd)
    record['watches']['wrong_root'] = wrong_root_watch
    record['elapsed_seconds'] = time.monotonic() - started
    if (wrong_root_watch['stop_reason'] or wrong_root_watch['returncode'] == 0
            or not (wrong_root / 'toy-repair-report.json').exists()):
        record.update(status='prerequisite_refused', failed_phase='wrong_root_refusal')
        support.write_json(output / 'report.json', record)
        print(json.dumps(record, indent=2), flush=True)
        return
    refusal = support.read_json(wrong_root / 'toy-repair-report.json')
    counts = ('physical_meshes', 'pde_solves', 'matrix_factorizations',
              'primary_rhs', 'returned_primary_solves', 'correction_rhs', 'matrix_solves')
    assert refusal['status'] == 'partial_failed'
    assert refusal['stage'] == 'imports' and refusal['error']['type']
    assert all(refusal[key] == 0 for key in counts)
    record['wrong_root_refusal'] = dict(status=refusal['status'], stage=refusal['stage'],
        error=refusal['error'], counts={key: refusal[key] for key in counts},
        report_sha256=support.sha(wrong_root / 'toy-repair-report.json'))
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


def physical(toy_path=None, output=None):
    verify()
    toy_path = toy_path or HERE / 'toys/report.json'
    output = output or HERE / 'physical'
    output.mkdir(exist_ok=False)
    toy = support.read_json(toy_path) if toy_path.exists() else dict(status='missing')
    prerequisites_passed = (
        toy.get('status') == 'passed' and toy.get('elapsed_seconds', 60.0) < 60.0
        and set(toy.get('watches', {})) == {
            'wrong_root', 'watchdog', 'kernels', 'wrapper', 'block-rhs', 'disk',
            'parent-refusal', 'advanced'}
        and toy.get('wrong_root_refusal', {}).get('status') == 'partial_failed'
        and all(w.get('returncode') == 0 and w.get('stop_reason') is None
                and w.get('parent_observed_peak_rss_mib', 512.0) < 512
                for name, w in toy.get('watches', {}).items() if name != 'wrong_root')
        and toy['watches']['wrong_root'].get('returncode') != 0
        and toy['watches']['wrong_root'].get('stop_reason') is None)
    if not prerequisites_passed:
        report = dict(status='prerequisite_refused', stage='toy_prerequisites',
                      error=dict(type='RuntimeError',
                                 message='Toy prerequisite report missing, failed, or incomplete'),
                      physical_meshes=0, primary_rhs=0, returned_primary_solves=0,
                      correction_rhs=0, matrix_factorizations=0, matrix_solves=0,
                      campaign_ready=False, physical_gate_passed=False,
                      child_launched=False)
        support.write_json(output / 'report.json', report)
        print(json.dumps(report, indent=2), flush=True)
        return
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
    print(json.dumps(dict(status=report['status'], stage=report.get('stage'),
        error=report.get('error'), watch=watch,
        counts={key: report.get(key) for key in
                ('physical_meshes', 'primary_rhs', 'returned_primary_solves',
                 'correction_rhs', 'matrix_solves')}), indent=2), flush=True)


def parent_refusal(output):
    """Run the actual parent's failed-prerequisite branch, with no child."""
    output.mkdir(parents=True, exist_ok=False)
    input_path = output / 'input-report.json'
    support.write_json(input_path, dict(status='synthetic_failed_prerequisite'))
    refused = output / 'refused'
    physical(input_path, refused)
    report = support.read_json(refused / 'report.json')
    assert report['status'] == 'prerequisite_refused' and not report['child_launched']
    assert not (refused / 'launch.json').exists()
    counts = ('physical_meshes', 'primary_rhs', 'returned_primary_solves',
              'correction_rhs', 'matrix_factorizations', 'matrix_solves')
    assert all(report[key] == 0 for key in counts)
    support.write_json(output / 'parent-report.json', dict(status='passed',
        actual_parent_refusal=True, child_launched=False,
        counts={key: report[key] for key in counts}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('toys', 'physical', 'parent-refusal'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
        os.environ[key] = '1'
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    verify()
    if args.phase == 'parent-refusal':
        parent_refusal(args.output)
    else:
        {'toys': toys, 'physical': physical}[args.phase]()
