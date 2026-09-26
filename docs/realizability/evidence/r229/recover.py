"""One R229 offline recovery transaction; no numerical imports or retries."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from verification.nonlinear_port.handshake import held, completed, publish, read
from verification.nonlinear_port.source_binding import verify_source
from verification.nonlinear_port.systemd_backend import SystemdBackend
from verification.nonlinear_port.supervision import CAPS, verify_held_scope
from verification.nonlinear_port.worker import _cgroup_path

PRIOR = ROOT/'docs/realizability/evidence/r227'
RUN = Path('/tmp/navier-r229-recovery')
PREFIX = Path('/tmp/navier-fenicsx-r229')
MANAGER = Path('/tmp/navier-r227-restore/bin/micromamba')
CACHE = Path('/home/rharris/.local/share/mamba/pkgs')
SPEC = PRIOR/'run/install/explicit.txt'


def digest(path, algorithm='sha256'):
    h = hashlib.new(algorithm)
    with path.open('rb') as stream:
        while block := stream.read(1024*1024):
            h.update(block)
    return h.hexdigest()


def recover():
    started = time.monotonic()
    if PREFIX.exists():
        raise RuntimeError('new prefix already exists')
    expected_manager = read(PRIOR/'run/bootstrap/manager.json')['executable_sha256']
    if digest(MANAGER) != expected_manager:
        raise RuntimeError('manager executable changed')
    packages = json.loads((PRIOR/'installed_records.json').read_text())
    specification = SPEC.read_text().splitlines()
    if set(specification) != {'@EXPLICIT', *(p['url']+'#'+p['md5'] for p in packages)}:
        raise RuntimeError('explicit transaction differs from recorded packages')
    for p in packages:
        if not p['url'].startswith('https://conda.anaconda.org/conda-forge/'):
            raise RuntimeError('unexpected package origin')
        archive = CACHE/'https'/unquote(p['url'].removeprefix('https://'))
        if digest(archive) != p['sha256'] or digest(archive, 'md5') != p['md5']:
            raise RuntimeError('cached artifact digest mismatch: '+p['name'])
    publish(RUN/'cache_verified.json', dict(package_count=len(packages),
        sha256_and_md5=True, manager_sha256=expected_manager,
        explicit_sha256=digest(SPEC), elapsed_seconds=time.monotonic()-started))
    env = dict(os.environ, MAMBA_ROOT_PREFIX=str(RUN/'mamba-root'),
        CONDA_PKGS_DIRS=str(CACHE), MAMBA_REMOTE_MAX_RETRIES='0',
        MAMBA_EXTRACT_THREADS='2', MAMBA_DOWNLOAD_THREADS='1', MAMBA_OFFLINE='true')
    command = list(map(str, [MANAGER, '--no-rc', 'create', '--offline', '--no-pyc',
                            '--prefix', PREFIX, '--yes', '--json', '--file', SPEC]))
    publish(RUN/'command.json', dict(argv=command, timeout_seconds=125))
    install_start = time.monotonic()
    with (RUN/'install.stdout').open('x') as out, (RUN/'install.stderr').open('x') as err:
        installed = subprocess.run(command, stdout=out, stderr=err, env=env,
                                   timeout=125, cwd=ROOT)
    install_seconds = time.monotonic()-install_start
    publish(RUN/'installer_exit.json', dict(returncode=installed.returncode,
                                            elapsed_seconds=install_seconds))
    if installed.returncode:
        raise RuntimeError('offline installer failed')
    records = [json.loads(p.read_text()) for p in sorted((PREFIX/'conda-meta').glob('*.json'))]
    actual = {p['name']:p for p in records}
    if set(actual) != {p['name'] for p in packages}:
        raise RuntimeError('installed package inventory differs')
    for p in packages:
        if any(actual[p['name']].get(k) != p[k] for k in ('version','build','sha256','md5')):
            raise RuntimeError('installed artifact differs: '+p['name'])
    history = PREFIX/'conda-meta/history'
    if history.stat().st_size == 0:
        raise RuntimeError('transaction history not committed')
    optional_missing, checked = 0, 0
    for p in records:
        for name in p.get('files', []):
            checked += 1
            if not (PREFIX/name).exists():
                if name.endswith('.pyc'):
                    optional_missing += 1
                else:
                    raise RuntimeError('required file missing: '+name)
    code = ('import json,sys; print(json.dumps(dict(executable=sys.executable,'
            'version=".".join(map(str,sys.version_info[:3])),prefix=sys.prefix)))')
    checked_python = subprocess.run([str(PREFIX/'bin/python'), '-I', '-S', '-c', code],
                                    capture_output=True, text=True, timeout=5, check=True)
    python = json.loads(checked_python.stdout)
    if python['version'] != '3.12.13' or python['executable'] != str(PREFIX/'bin/python'):
        raise RuntimeError('actual interpreter identity mismatch')
    publish(RUN/'verification.json', dict(status='METADATA_AND_INTERPRETER_VERIFIED',
        prefix=str(PREFIX), python=python, executable_sha256=digest((PREFIX/'bin/python').resolve()),
        package_count=len(records), version_build_sha256_md5_match=True,
        file_entries_checked=checked, missing_required_files=0,
        missing_optional_bytecode=optional_missing, eager_bytecode_disabled=True,
        history_bytes=history.stat().st_size, history_sha256=digest(history),
        install_seconds=install_seconds, worker_seconds=time.monotonic()-started,
        numerical_imports_requested=False, fem_attempts=0))
    (RUN/'history.txt').write_bytes(history.read_bytes())


def worker():
    reservation = read(RUN/'reservation.json')
    held(RUN, reservation, _cgroup_path(), verify_source(reservation))
    try:
        recover()
        publish(RUN/'task.json', dict(success=True))
    except Exception as exc:
        publish(RUN/'task.json', dict(success=False, error=f'{type(exc).__name__}: {exc}'))
    completed(RUN, reservation)


def controller(commit):
    start = time.monotonic()
    RUN.mkdir(exist_ok=False)
    publish(RUN/'reservation.json', dict(source_commit=commit, interpreter=sys.executable,
                                         release_nonce='r229-offline'))
    backend, handle = SystemdBackend(ROOT), None
    result = dict(success=False, numerical_attempts=0, monotonic_start=start)
    try:
        handle = backend.start_held([sys.executable, str(Path(__file__).resolve()), '--worker'],RUN,CAPS)
        result['held_scope'] = verify_held_scope(handle.facts(),handle.scope_id)
        handle.release()
        result['exit'] = handle.wait(152)
        result['task'] = read(RUN/'task.json')
        result['success'] = result['exit']['exit_code']==0 and result['task']['success']
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
    finally:
        handle = handle or backend.active_handle
        if handle:
            try:
                handle.stop()
                result['cleanup'] = handle.cleanup()
                c = result['cleanup']
                if (not c['empty'] or c.get('memory_events',{}).get('max',1)!=0
                        or c.get('memory_events',{}).get('oom',1)!=0
                        or c.get('pids_events',{}).get('max',1)!=0):
                    result['success'] = False
            except Exception as exc:
                result['cleanup_error'] = str(exc)
                result['success'] = False
        result['elapsed_before_save'] = time.monotonic()-start
        if result['elapsed_before_save']>180:
            result['success'] = False
        publish(RUN/'result.json',result)
    elapsed = time.monotonic()-start
    if elapsed>180:
        publish(RUN/'late.json',dict(elapsed_seconds=elapsed))
        result['success']=False
    print(json.dumps(dict(result=result,elapsed_after_save=elapsed),indent=2))
    return 0 if result['success'] else 1


if __name__=='__main__':
    if len(sys.argv)==2 and sys.argv[1]=='--worker':
        worker()
    elif len(sys.argv)==2 and len(sys.argv[1])==40:
        raise SystemExit(controller(sys.argv[1]))
    else:
        raise SystemExit('usage: recover.py EXPECTED_COMMIT')
