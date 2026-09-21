"""Single-path, default-deny parent for the disposable physical runner."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import launch_guard as guard

HERE = Path(__file__).resolve().parent


def verify():
    return guard.verify_source_manifest(HERE, HERE / 'source_manifest.json')


def physical(output: Path):
    # The reusable API and CLI both default to disabled. A later launch review
    # must deliberately replace this deny before any real child is available.
    return guard.guarded_launch(output, enabled=False, source_check=verify)


def parent_refusal(output: Path):
    output.mkdir(parents=True, exist_ok=False)
    report = guard.initial_report()
    result = guard.refuse(report, 'synthetic_prerequisite_refusal',
                          'saved negative-path contract')
    guard.write_json(output / 'report.json', result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('verify', 'physical', 'parent-refusal'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.phase == 'verify':
        verify()
        print(json.dumps({'status': 'source_manifest_verified'}))
    elif args.phase == 'physical':
        if args.output is None:
            parser.error('--output is required for physical phase')
        print(json.dumps(physical(args.output), indent=2))
    else:
        verify()
        print(json.dumps(parent_refusal(args.output), indent=2))


if __name__ == '__main__':
    main()
