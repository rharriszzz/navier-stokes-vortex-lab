"""R014 matched-trace prerequisite checks; run from repository root. Disposable instrumentation."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

POLL_S = 0.05
WALL_S = 180.0
RSS_MIB = 1536.0
def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    temporary = Path(str(path) + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)

def read_json(path):
    def reject(value):
        raise ValueError('Nonfinite JSON constant: ' + value)
    return json.loads(Path(path).read_text(), parse_constant=reject)

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

def monitor(command, deadline, rss_limit, log_prefix, cwd=None):
    started = time.monotonic()
    peak = 0.0
    samples = 0
    max_gap = 0.0
    largest_tree = 0
    previous = started
    reason = None
    with Path(str(log_prefix) + '.stdout').open('w') as stdout, Path(str(log_prefix) + '.stderr').open('w') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr,
                                   start_new_session=True, cwd=cwd)
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


EXPECTED_SOURCES = {'realizability/__init__.py': '197df2cae0b7fcc3908afebfd9359b21244fc8aa0460b0167af04a2f1c7f219c', 'realizability/backends/__init__.py': '8b40aa33331d5a627dbd4aa1681f9da523a21e31e2b0e71f48203967481f20b2', 'realizability/backends/b1_verification.py': '287512f423a3c147c009802c2de9d6cf11538d3c80fc3fbc98dffaf586bb1e5c', 'realizability/backends/b2_coercivity.py': 'be10e484ffd5c36aef45962242dea2bcaaaa3cbad37df83e297fcc366bf96bcc', 'realizability/backends/b2_gate.py': '3151ac8a85de4b242e53b28a3d2815d7ecf5e8e6ed8c654f440aa5a8778a6d05', 'realizability/backends/b2_stability.py': '18b2e75712255a681a0c22f012d81ab3a129e147c41f3f8974bb46cf6a8df9f1', 'realizability/backends/b2_verification.py': '42e11041c5f1edbca13737010456247f059d92e874a9398454bf4b6f17498d25', 'realizability/backends/fem_observables.py': 'f5dbc8a47d2f5c61d9228daf49c80ae1011ab542ee12335398a52eaf89ed0a64', 'realizability/backends/fenicsx_stokes.py': '37ecd62121553e13f273fb99c7bc2649f51d9cea57658f4bce8069c4ac80a206', 'realizability/backends/hdiv_stokes.py': 'f23b252f91c406e3e279c7e6e7049e301ad604fae232dd0a610a73319864d2e9', 'realizability/boundary_modes.py': '586d2667b8ac4b6a460d590afc884a05be5f9843484df74de8a4568261f84d18', 'realizability/cli.py': 'c163e6a3dc8e6a2c08c7dc48a7205624947fce938dea1aec3489ef62135bd850', 'realizability/config.py': '3cb3edbb28e203226056cf4ac5e7832951c33e5f932b13a5ec438de88c786d12', 'realizability/observables.py': '428fd794b00669593f87b694bca10a94454ccbd9ee012fa656a61c7b30375a05', 'realizability/reference.py': '7f032634768a3f8b8a7a649e4d83dc45fd6f969a1c1ba679d1628867d2f13305', 'realizability/response.py': '5318e4d6ea917433909e6e9718c90ed9cf48a5ee4b779b4446b83b3452d71317', 'realizability/sensors.py': 'c93cd68cc902970f27ecdce7deb1d272f146890cfe99b076b87e190222483d9a', 'realizability/swirl_reference.py': '375e057ff365858cb5dc698e1b397eb34b18a9898d5a82482e2391ea11d81e4a', 'configs/realizability/pilot.json': '0e60a6ee85063f5d86b84db5af053f2166126249255edeafae4b4e6242db10d0'}

def verify_sources():
    actual = {path: sha(path) for path in EXPECTED_SOURCES}
    if actual != EXPECTED_SOURCES:
        raise RuntimeError('Pinned source/config identity mismatch')
    return actual


def capture_return(function, captured, *args, **kwargs):
    """Observe the unchanged helper's return frame; no assembly/BC edits."""
    if sys.getprofile() is not None:
        raise RuntimeError('An existing profiler would be overwritten')
    returns = []
    def observer(frame, event, value):
        if frame.f_code is function.__code__ and event == 'return':
            captured.update(frame.f_locals)
            returns.append(value)
    sys.setprofile(observer)
    try:
        result = function(*args, **kwargs)
    finally:
        sys.setprofile(None)
    if len(returns) != 1 or returns[0] is not result:
        raise RuntimeError('Helper capture count/return identity mismatch')
    return result


def toy_child(output):
    sys.path.insert(0,str(Path.cwd()))
    started=time.monotonic()
    record=dict(status='partial',stage='imports',campaign_ready=False,
                physical_gate_passed=False,physical_meshes=0,primary_rhs=0,
                correction_rhs=0,matrix_solves=0,source_sha256=verify_sources(),
                runner_sha256=sha(__file__),kernels_sha256=sha(Path(__file__).with_name('kernels.py')),
                limits=dict(total_wall_seconds=60.,active_child_tree_rss_mib=512.,
                            nominal_poll_seconds=POLL_S))
    def checkpoint(stage):
        record['stage']=stage
        record['elapsed_child_seconds']=time.monotonic()-started
        record['process_peak_rss_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
        write_json(output/'toy-report.json',record)
    checkpoint('imports')
    try:
        import kernels
        import dolfinx,basix,numpy,ufl
        record['versions']={m.__name__:m.__version__ for m in (dolfinx,basix,numpy,ufl)}
        checkpoint('disk_toys')
        record['disk_toys']=kernels.disk_toys()
        checkpoint('load_toys')
        def progress(rows):
            record['load_toys']=rows
            checkpoint('load_toys')
        record['load_toys']=kernels.load_toys(progress)
        record['status']='passed'
        checkpoint('toy_checks_complete')
    except Exception as error:
        record['status']='partial_failed'
        record['error']=dict(type=type(error).__name__,message=str(error))
        checkpoint(record['stage'])
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--toy-child',action='store_true')
    parser.add_argument('--self-check',action='store_true')
    args=parser.parse_args()
    if args.self_check:
        verify_sources()
        self_check(args.output)
    elif args.toy_child:
        toy_child(args.output)
    else:
        verify_sources()
        args.output.mkdir(parents=True,exist_ok=False)
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
            os.environ[key]='1'
        self_check(args.output/'watchdog')
        watch=monitor([sys.executable,str(Path(__file__).resolve()),'--toy-child',
                       '--output',str(args.output)],time.monotonic()+60.,512.,args.output/'toy')
        write_json(args.output/'toy-watch.json',watch)
        report=read_json(args.output/'toy-report.json')
        if watch['stop_reason'] or watch['returncode']!=0:
            report['parent_stop']=watch
            if watch['stop_reason']:
                report['status']='partial_resource_or_process_stop'
            write_json(args.output/'toy-report.json',report)
        write_json(args.output/'manifest.json',{str(p.relative_to(args.output)):sha(p)
            for p in sorted(args.output.rglob('*')) if p.is_file() and p.name!='manifest.json'})
        print(json.dumps(dict(status=report['status'],stage=report['stage'],watch=watch),indent=2))
