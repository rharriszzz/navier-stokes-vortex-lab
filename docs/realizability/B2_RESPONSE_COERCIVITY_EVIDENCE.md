# R008 response-geometry certificate evidence

This appendix accompanies [B2_RESPONSE_COERCIVITY_RESULT.md](B2_RESPONSE_COERCIVITY_RESULT.md).
It preserves the exact disposable runner and compact evidence for the single
bounded 50/40/30/25 mm experiment. No backend source changed. The working tree
at execution differed from `f7a7e8f` only by the appended R008 request entry.
Generated reports remain outside Git.

## Configuration, provenance, and resource record

The provenance hashes all 18 package Python files and the pilot configuration.
The report writer is the pinned local module plus the exact runner below.
All eight classifications were recomputed from the guarded bound: alpha=48
is inconclusive and alpha=96 is certified positive on each mesh. Read the
result document for the certificate's scope and limitations.

```json
{
  "provenance": {
    "repository_commit": "f7a7e8f6bba1708c9ac1abcd417a52085e2c8d9d",
    "repository_dirty": true,
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
    "runner_sha256": "3eed2ee55b1ebce6b7a183b53e8c19e01deb02254d142d63b1aca07bd33686fe",
    "python": "3.12.13 | packaged by conda-forge | (main, Mar  5 2026, 16:50:00) [GCC 14.3.0]"
  },
  "config": {
    "schema_version": 1,
    "geometry": {
      "radius": 0.1,
      "half_height": 0.15
    },
    "fluid": {
      "kinematic_viscosity": 1e-06,
      "density": 1000.0
    },
    "reference": {
      "duration": 100.0,
      "initial_core_radius": 0.01,
      "final_core_radius": 0.003,
      "initial_peak_swirl": 0.01,
      "radial_plateau": 0.04,
      "radial_cutoff": 0.08,
      "axial_plateau": 0.05,
      "axial_cutoff": 0.12
    },
    "probe_velocity": 1e-07,
    "frequencies_hz": [
      0.01,
      0.1,
      1.0,
      30.0
    ],
    "mode_order": [
      "N_02c",
      "T_00c",
      "N_40c",
      "N_40s",
      "T_40c",
      "T_40s"
    ]
  },
  "versions": {
    "dolfinx": "0.10.0",
    "basix": "0.10.0",
    "ufl": "2025.2.1",
    "ffcx": "0.10.0",
    "gmsh": "4.15.2",
    "numpy": "2.5.3",
    "petsc": "3.25.5",
    "petsc_scalar_type": "float64",
    "mpi": "MPICH Version:      5.0.1"
  },
  "limits": {
    "total_wall_seconds": 120.0,
    "active_child_tree_rss_mib": 1024.0,
    "nominal_poll_seconds": 0.05,
    "default_cell_cap": 500,
    "new_geometry_cell_cap": 4000
  },
  "elapsed_seconds": 2.6917815140041057,
  "completed": true,
  "stop_reason": null,
  "campaign_ready": false,
  "unexecuted_mesh_sizes_m": [],
  "checked_cell_values": 6351,
  "checked_penalty_classifications": 8,
  "study_sha256": "58002596fa0d39af578e07dd4cfd3b89fa1c1499cb182a17223979fe36466028",
  "manifest_sha256": "775133bda947fab79018a325128dd5395e672de576182d17443d1e89b338f85e",
  "final_watchdog_self_check_sha256": "6e60009bf6ec004c5435f1e81ce58157628fbb7e5854adc326790c6dd4119d26"
}
```

## Compact numerical records

```json
[
  {"mesh_size_m": 0.05, "mesh_sha256": "423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4", "cells": 482, "facets": 1105, "exterior_facets": 282, "interior_facets": 823, "C_upper": 58.12657123078638, "C_safe": 58.12657123659904, "maximum_local_trace_eigenvalue": 48.96418141363834, "worst_cell": 320, "beta_at_48": -0.1004409271268556, "beta_at_96": 0.22187075813338908, "local_seconds": 0.06323542799509596, "watched_seconds": 0.8039188499969896, "parent_peak_rss_mib": 176.109375, "process_peak_rss_mib": 177.09375, "maximum_sample_gap_seconds": 0.053971735993400216},
  {"mesh_size_m": 0.04, "mesh_sha256": "a7006604f0da3df5c8b9f92aaf0e8f1eaae8522554c4378e1e9ce1369a85e59b", "cells": 873, "facets": 1965, "exterior_facets": 438, "interior_facets": 1527, "C_upper": 57.902615513171966, "C_safe": 57.90261551896223, "maximum_local_trace_eigenvalue": 51.12135194509739, "worst_cell": 329, "beta_at_48": -0.09831893818616266, "beta_at_96": 0.22337123090295585, "local_seconds": 0.10079423600109294, "watched_seconds": 0.48365268199995626, "parent_peak_rss_mib": 178.25, "process_peak_rss_mib": 178.25, "maximum_sample_gap_seconds": 0.053903692998574115},
  {"mesh_size_m": 0.03, "mesh_sha256": "9096deae45c24dcdb028082e2b971fb197657574e1b43af71a9ec036dc2ff7bf", "cells": 1842, "facets": 4029, "exterior_facets": 690, "interior_facets": 3339, "C_upper": 58.47385711840445, "C_safe": 58.473857124251836, "maximum_local_trace_eigenvalue": 49.01562334933836, "worst_cell": 1276, "beta_at_48": -0.10372340591075924, "beta_at_96": 0.21954969512618983, "local_seconds": 0.19960120601172093, "watched_seconds": 0.5924837109923828, "parent_peak_rss_mib": 180.76171875, "process_peak_rss_mib": 180.51171875, "maximum_sample_gap_seconds": 0.05462356100906618},
  {"mesh_size_m": 0.025, "mesh_sha256": "42fa3aac5c2bc762514c5cadb642edc2a1a8acfdf81ea9df7df992b696a04895", "cells": 3154, "facets": 6830, "exterior_facets": 1044, "interior_facets": 5786, "C_upper": 59.302126356205726, "C_safe": 59.30212636213594, "maximum_local_trace_eigenvalue": 50.095217517844745, "worst_cell": 2408, "beta_at_48": -0.11151291754879389, "beta_at_96": 0.21404167862480394, "local_seconds": 0.3499823119927896, "watched_seconds": 0.8089201569964644, "parent_peak_rss_mib": 184.5078125, "process_peak_rss_mib": 184.5078125, "maximum_sample_gap_seconds": 0.05560065100144129}
]
```

## Generated-report manifest

All 22 listed files were read and their hashes checked. These hashes identify
the recorded run, not future timings or bitwise output on another environment.

```json
{
  "025mm.json": "f166b13ffb56749a01cfbc96f6ad9af7a9e88853006b3407941c89aaa5136f64",
  "025mm.md": "1ae6ac4aea16bcc017d3543305b6f431d93bc87be3d00b8faf59346a5a4e206e",
  "025mm.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "025mm.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "025mm.watch.json": "143442dbd457baae7a2ae17a57b1dff73466fc8085abd7780111ba7f5e636966",
  "030mm.json": "874d132de8d0502410c98c5b1ec6ef2b62078de538ed263f223289d885b7b75f",
  "030mm.md": "435deb420c83a2d88032c5b3464e481cf3d6c7ac2e1d595d6e3d2a70f9e289ed",
  "030mm.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "030mm.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "030mm.watch.json": "ebd183fa979a29ac6960f0943590aaa5eba5386fd078ad91cbe01f01a189fa59",
  "040mm.json": "c55b1762dfdfef6137d3199ef1fbc9c175601319bafcb5c8886da3b912a6d71f",
  "040mm.md": "1abfbd1a3c2b2d5ce4bb1f489225e5f90a30c2c76b8b54944f2af40d2dd24372",
  "040mm.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "040mm.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "040mm.watch.json": "1ccc437274daaafa1526dbf8b405c79a7066025fb59dd3b6e15f166880e5f66c",
  "050mm.json": "767c5bc7cd66ab9f70a071fd8c558913c169252235d51a312845720a2bb8902b",
  "050mm.md": "0a91a0e3bdc72714cb2c46756fc63f9e5c18245d0c9d28a9863aec48deaf4cd1",
  "050mm.stderr": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "050mm.stdout": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "050mm.watch.json": "5fba3eb3f754def29d51dce5fe386ca947e401c79f65a5f1cc1fc66ca87726b8",
  "study.json": "58002596fa0d39af578e07dd4cfd3b89fa1c1499cb182a17223979fe36466028",
  "study.md": "22e5f1749fd39e6152c4b0c18c63ca816c663c1159f27a2d7dec684249d69eee"
}
```

## Reproduction and validation

Use the optional environment in [B1_SETUP.md](B1_SETUP.md). Extract the Python
block below byte-for-byte to a temporary `runner.py`, and run from the repository
root using that environment's interpreter. Both output directories must be
new; the runner refuses existing directories. The script uses Linux `/proc`
for the parent watchdog and starts each case in a fresh process/session.
Ordinary imports/cache creation need the optional environment's usual access.

```bash
python /tmp/runner.py --self-check --output /tmp/b2-r008-watchdog-check
python /tmp/runner.py --output /tmp/b2-r008-evidence
```

The self-check uses synthetic sleeping/allocation children and has independent,
deliberately small limits. It does not generate meshes or change the 120 s /
1 GiB experiment limits. In the final check, the wall-limited child was killed
after 0.15354 s and the two-process RSS case after 0.05343 s; the observed memory
peak was 49.35547 MiB against its deliberately low 24 MiB cap. Maximum sample
gaps were below 0.1 s. SIGKILL return codes are expected for these self-checks.
The study itself had four zero child exit codes and no watchdog stop.

The runner's embedded source hashes intentionally stop reproduction if the
reviewed numerical source differs. Compare sources before interpreting new
results; do not remove that check to label another operator as this one. The
nominal polling period is 0.05 s. Observed gaps and sampled RSS are recorded;
the watchdog cannot prevent a memory overshoot between samples. Small differences
between sampled RSS and the process's own peak are preserved in the records.

The bounded run was launched once using `/tmp/navier-fenicsx/bin/python` on
2026-09-20. Results are in `/tmp/navier-b2-response-coercivity-r008/evidence/`;
synthetic watchdog checks are in the sibling `watchdog-check-final/` directory.
The exact runner SHA-256 is
`3eed2ee55b1ebce6b7a183b53e8c19e01deb02254d142d63b1aca07bd33686fe`.

## Exact runner

```python
"""R008 bounded geometry-only study. Run from the repository root on Linux."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

CASES = (
    (0.050, 482, 500, '423ab057c5738ae3e2dcef6e82c238ee7e61bc1d0af7f1e212d04b8a2cd6bfb4'),
    (0.040, 873, 4000, 'a7006604f0da3df5c8b9f92aaf0e8f1eaae8522554c4378e1e9ce1369a85e59b'),
    (0.030, 1842, 4000, '9096deae45c24dcdb028082e2b971fb197657574e1b43af71a9ec036dc2ff7bf'),
    (0.025, 3154, 4000, '42fa3aac5c2bc762514c5cadb642edc2a1a8acfdf81ea9df7df992b696a04895'),
)
PINNED = {
    'realizability/backends/b2_coercivity.py': 'be10e484ffd5c36aef45962242dea2bcaaaa3cbad37df83e297fcc366bf96bcc',
    'realizability/backends/hdiv_stokes.py': 'f23b252f91c406e3e279c7e6e7049e301ad604fae232dd0a610a73319864d2e9',
    'realizability/backends/fenicsx_stokes.py': '37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206',
    'configs/realizability/pilot.json': '0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0',
}
POLL_S = 0.05
WALL_S = 120.0
RSS_MIB = 1024.0

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

def read_json(path):
    def reject(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_text(), parse_constant=reject)

def provenance():
    paths = sorted(Path('realizability').rglob('*.py')) + [Path('configs/realizability/pilot.json')]
    hashes = {str(p): sha(p) for p in paths}
    for path, expected in PINNED.items():
        assert hashes[path] == expected, ('source mismatch', path)
    return dict(repository_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        repository_dirty=bool(subprocess.check_output(['git', 'status', '--porcelain'], text=True)),
        source_sha256=hashes, runner_sha256=sha(__file__), python=sys.version)

def process_tree_sample(root_pid):
    """Include descendants and the child's entire new session, including orphans."""
    records = {}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            fields = (entry / 'stat').read_text().rsplit(')', 1)[1].split()
            records[int(entry.name)] = (int(fields[1]), int(fields[3]), int(fields[21]))
        except (FileNotFoundError, ProcessLookupError):
            continue
    included = {pid for pid, (_, session, _) in records.items() if session == root_pid}
    included.add(root_pid)
    while True:
        expanded = included | {pid for pid, (parent, _, _) in records.items() if parent in included}
        if expanded == included:
            break
        included = expanded
    rss_pages = sum(max(0, records[pid][2]) for pid in included if pid in records)
    return rss_pages * os.sysconf('SC_PAGE_SIZE') / 1024**2, included

def terminate_tree(process, pids):
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    for pid in pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=5)

def monitor(command, deadline, rss_limit, log_prefix):
    started = time.monotonic()
    peak = 0.0
    samples = 0
    max_gap = 0.0
    largest_tree = 0
    previous = started
    reason = None
    with Path(str(log_prefix) + '.stdout').open('w') as stdout, Path(str(log_prefix) + '.stderr').open('w') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
        pids = {process.pid}
        try:
            while True:
                now = time.monotonic()
                max_gap = max(max_gap, now - previous)
                previous = now
                rss, pids = process_tree_sample(process.pid)
                samples += 1
                peak = max(peak, rss)
                largest_tree = max(largest_tree, len(pids))
                if now >= deadline:
                    reason = 'wall_time_limit'
                elif rss > rss_limit:
                    reason = 'rss_limit'
                if reason:
                    terminate_tree(process, pids)
                    break
                if process.poll() is not None:
                    # A successful child must not leave a live descendant behind.
                    remaining_rss, remaining_pids = process_tree_sample(process.pid)
                    if remaining_rss > 0:
                        reason = 'child_left_live_descendants'
                        terminate_tree(process, remaining_pids)
                    break
                time.sleep(min(POLL_S, max(0, deadline-time.monotonic())))
        except BaseException:
            terminate_tree(process, pids)
            raise
    return dict(command=command, returncode=process.returncode,
        elapsed_seconds=time.monotonic()-started, parent_observed_peak_rss_mib=peak,
        samples=samples, nominal_poll_seconds=POLL_S, maximum_sample_gap_seconds=max_gap,
        largest_observed_process_tree=largest_tree, stop_reason=reason)

def check_report(report, index):
    size, cells, cap, expected_hash = CASES[index]
    assert report['campaign_ready'] is False
    assert json.loads(json.dumps(report['config'])) == read_json('configs/realizability/pilot.json')
    assert report['guards'] == dict(max_cells=cap, minimum_volume_over_diameter_cubed=1e-12,
        C_safe_relative_pad=1e-10, minimum_beta_exclusive=1e-8)
    assert len(report['mesh_results']) == 1
    row = report['mesh_results'][0]
    assert row['status'] == 'evaluated', row
    assert row['mesh_size_m'] == size and row['mesh_sha256'] == expected_hash
    bound = row['bound']
    assert bound['cell_count'] == cells
    assert bound['facet_count'] == bound['interior_facet_count'] + bound['exterior_facet_count']
    assert 4*cells == 2*bound['interior_facet_count'] + bound['exterior_facet_count']
    for field in ('minimum_cell_volume_m3', 'minimum_cell_diameter_m', 'C_upper', 'C_safe'):
        assert math.isfinite(bound[field]) and bound[field] > 0, field
    values = bound['cell_trace_eigenvalues']
    assert len(values) == cells and all(math.isfinite(x) and x > 0 for x in values)
    assert max(values) <= bound['C_upper'] + 1e-12*max(1, bound['C_upper'])
    assert bound['C_safe'] == bound['C_upper'] + 1e-10*max(1, bound['C_upper'])
    assert [x['penalty_factor'] for x in row['penalty_cases']] == [48.0, 96.0]
    for case in row['penalty_cases']:
        beta = 1-math.sqrt(bound['C_safe']/case['penalty_factor'])
        assert math.isclose(case['beta'], beta, rel_tol=1e-14, abs_tol=1e-14)
        assert case['status'] == ('certified_positive' if beta > 1e-8 else 'inconclusive')
    if index == 0:
        assert math.isclose(bound['C_upper'], 58.12657123078638, rel_tol=1e-10)
        assert [x['status'] for x in row['penalty_cases']] == ['inconclusive', 'certified_positive']
    return dict(identity_passed=True, geometry_guards_passed=True, facet_counts_passed=True,
        checked_cell_values=cells, checked_classifications=2, arithmetic_passed=True)

def child(index, output):
    sys.path.insert(0, str(Path.cwd()))
    from realizability.config import load_config
    from realizability.backends.b2_coercivity import CELL_LIMIT, run_b2_coercivity, format_b2_coercivity
    assert CELL_LIMIT == 500
    origin = provenance()
    size, _, cap, _ = CASES[index]
    report = run_b2_coercivity(load_config(Path('configs/realizability/pilot.json')),
        (size,), (48.0, 96.0), max_cells=cap)
    report['provenance'] = origin
    report['research_scope'] = 'R008 standalone geometry-only certificate; gate unchanged'
    inconclusive = [dict(mesh_size_m=size, penalty_factor=c['penalty_factor'])
        for c in report['mesh_results'][0]['penalty_cases'] if c['status'] == 'inconclusive']
    report['unresolved_stability_cases'] = inconclusive
    if inconclusive:
        report['campaign_blockers'].append('listed mesh/penalty cases have inconclusive stability certificates')
    path = output / f'{round(size*1000):03d}mm.json'
    write_json(path, report)  # Preserve an invalid/resource result before checking it.
    try:
        report['research_checks'] = check_report(report, index)
    except (AssertionError, KeyError, ValueError) as error:
        report['research_checks'] = dict(passed=False, error=str(error))
        write_json(path, report)
        raise
    write_json(path, report)
    markdown = format_b2_coercivity(report) + '\n## Research metadata\n\n```json\n'
    markdown += json.dumps({k: v for k, v in report.items() if k != 'mesh_results'}, indent=2, allow_nan=False)
    markdown += '\n```\n\n## Geometry and bound\n\n```json\n'
    markdown += json.dumps({k: v for k, v in report['mesh_results'][0]['bound'].items()
        if k != 'cell_trace_eigenvalues'}, indent=2, allow_nan=False) + '\n```\n'
    path.with_suffix('.md').write_text(markdown)

def self_check(output):
    output.mkdir(parents=True, exist_ok=False)
    timeout_case = monitor([sys.executable, '-c', 'import time; time.sleep(3)'],
        time.monotonic()+0.15, RSS_MIB, output/'timeout')
    grandchild = 'import time; data=bytearray(32*1024**2); time.sleep(3)'
    parent = f'import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",{grandchild!r}]); time.sleep(3)'
    rss_case = monitor([sys.executable, '-c', parent], time.monotonic()+3, 24.0, output/'memory')
    result = dict(scope='synthetic watchdog validation; no mesh/PDE work', timeout=timeout_case, memory=rss_case)
    write_json(output/'self-check.json', result)
    assert timeout_case['stop_reason'] == 'wall_time_limit'
    assert rss_case['stop_reason'] == 'rss_limit' and rss_case['largest_observed_process_tree'] >= 2
    assert max(timeout_case['maximum_sample_gap_seconds'], rss_case['maximum_sample_gap_seconds']) <= 0.1
    print(json.dumps(result, indent=2), flush=True)

def study(output):
    origin = provenance()
    output.mkdir(parents=True, exist_ok=False)
    summary = dict(scope='R008 standalone geometry-only certificates; no global PDE assembly or solve',
        limits=dict(total_wall_seconds=WALL_S, active_child_tree_rss_mib=RSS_MIB,
            nominal_poll_seconds=POLL_S, default_cell_cap=500, new_geometry_cell_cap=4000),
        provenance=origin, campaign_ready=False, records=[], stop_reason=None)
    started = time.monotonic()
    deadline = started + WALL_S
    for index, (size, _, _, _) in enumerate(CASES):
        if time.monotonic() >= deadline:
            summary['stop_reason'] = 'wall_time_limit_before_next_case'
            break
        prefix = output / f'{round(size*1000):03d}mm'
        watch = monitor([sys.executable, str(Path(__file__).resolve()), '--child', str(index),
            '--output', str(output.resolve())], deadline, RSS_MIB, prefix)
        write_json(prefix.with_suffix('.watch.json'), watch)
        record = dict(mesh_size_m=size, watchdog=watch)
        summary['records'].append(record)
        if watch['stop_reason'] or watch['returncode'] != 0:
            summary['stop_reason'] = watch['stop_reason'] or 'child_failed'
        else:
            try:
                report = read_json(prefix.with_suffix('.json'))
                record['checks'] = check_report(report, index)
                record['result'] = report['mesh_results'][0]
                record['process_peak_rss_mib'] = report['process_peak_rss_mib']
                assert report['provenance'] == origin
                assert watch['maximum_sample_gap_seconds'] <= 0.1
            except (AssertionError, KeyError, ValueError) as error:
                summary['stop_reason'] = 'report_or_monitoring_check_failed'
                record['error'] = str(error)
        if summary['stop_reason']:
            break
        print(f'Completed {size:g} m: ' + ', '.join(c['status'] for c in record['result']['penalty_cases']), flush=True)
    summary['elapsed_seconds'] = time.monotonic()-started
    if summary['elapsed_seconds'] > WALL_S and summary['stop_reason'] is None:
        summary['stop_reason'] = 'wall_time_limit'
    summary['unexecuted_mesh_sizes_m'] = [row[0] for row in CASES[len(summary['records']):]]
    summary['completed'] = summary['stop_reason'] is None and len(summary['records']) == len(CASES)
    write_json(output/'study.json', summary)
    lines = ['# R008 response-geometry certificate study', '', 'Campaign ready: **false**', '',
        '| Mesh (m) | C_upper | alpha=48 | alpha=96 |', '|---:|---:|---|---|']
    for record in summary['records']:
        row = record.get('result')
        if row:
            lines.append(f"| {record['mesh_size_m']:g} | {row['bound']['C_upper']:.12g} | "
                + ' | '.join(c['status'] for c in row['penalty_cases']) + ' |')
    lines += ['', f"Stop reason: {summary['stop_reason']}. Unexecuted: {summary['unexecuted_mesh_sizes_m']}.", '',
        'Inconclusive does not imply instability. Physical accuracy remains unresolved.', '',
        'Full configuration/provenance/bound data and guards are in each per-mesh JSON/Markdown pair.',
        'Parent watchdog timings and RSS are in the associated watch.json files.', '']
    (output/'study.md').write_text('\n'.join(lines))
    write_json(output/'manifest.json', {p.name: sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps({k: v for k, v in summary.items() if k not in ('records', 'provenance')}, indent=2), flush=True)
    if not summary['completed']:
        raise SystemExit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--child', type=int, choices=range(len(CASES)))
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.child is not None:
        child(args.child, args.output)
    elif args.self_check:
        self_check(args.output)
    else:
        study(args.output)
```
