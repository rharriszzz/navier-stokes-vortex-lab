"""R227 finite environment setup, not a numerical or general-purpose runner."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from verification.nonlinear_port.handshake import held, completed, publish, read
from verification.nonlinear_port.source_binding import verify_source
from verification.nonlinear_port.systemd_backend import SystemdBackend
from verification.nonlinear_port.supervision import CAPS, verify_held_scope
from verification.nonlinear_port.worker import _cgroup_path

BASE = Path('/tmp/navier-r227-restore')
PREFIX = Path('/tmp/navier-fenicsx')
MANAGER = BASE/'bin/micromamba'
CACHE = Path('/home/rharris/.local/share/mamba/pkgs')
PINS = dict(line.strip()[2:].split('=', 1) for line in (ROOT/'environment-b1.yml').read_text().splitlines()
            if line.strip().startswith('- ') and '=' in line)


def run(argv, name, directory, timeout=100, env=None):
    with (directory/(name+'.stdout')).open('x') as out, (directory/(name+'.stderr')).open('x') as err:
        result = subprocess.run(list(map(str, argv)), stdout=out, stderr=err,
                                timeout=timeout, env=env, cwd=ROOT)
    if result.returncode:
        raise RuntimeError(f'{name} failed with exit {result.returncode}')
    return (directory/(name+'.stdout')).read_text()


def bootstrap(directory):
    url = 'https://micro.mamba.pm/api/micromamba/linux-64/latest'
    archive = BASE/'micromamba.tar.bz2'
    with urllib.request.urlopen(url, timeout=25) as response, archive.open('xb') as out:
        total = 0
        while block := response.read(1024*1024):
            total += len(block)
            if total > 30*1024**2:
                raise RuntimeError('manager archive exceeds 30 MiB')
            out.write(block)
    MANAGER.parent.mkdir()
    with tarfile.open(archive) as tar:
        member = tar.getmember('bin/micromamba')
        if not member.isfile() or member.size > 40*1024**2:
            raise RuntimeError('unexpected manager executable')
        with tar.extractfile(member) as src, MANAGER.open('xb') as dst:
            dst.write(src.read())
    MANAGER.chmod(0o755)
    version = run([MANAGER, '--version'], 'version', directory, 5).strip()
    run([MANAGER, 'create', '--help'], 'create-help', directory, 5)
    publish(directory/'manager.json', dict(url=url, version=version,
            archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
            executable_sha256=hashlib.sha256(MANAGER.read_bytes()).hexdigest()))


def install(directory):
    if PREFIX.exists():
        raise RuntimeError('refusing existing environment prefix')
    env = dict(os.environ, MAMBA_ROOT_PREFIX=str(BASE/'mamba-root'),
               CONDA_PKGS_DIRS=str(CACHE), MAMBA_REMOTE_MAX_RETRIES='0',
               MAMBA_DOWNLOAD_THREADS='2', MAMBA_EXTRACT_THREADS='2')
    common = [MANAGER, '--no-rc', 'create', '--prefix', PREFIX, '--yes', '--json']
    plan_text = run([*common, '--file', ROOT/'environment-b1.yml', '--dry-run'],
                    'plan', directory, 75, env)
    plan = json.loads(plan_text)
    if plan.get('success') is not True:
        raise RuntimeError('package solve did not succeed')
    packages = plan['actions']['LINK']
    by_name = {p['name']: p for p in packages}
    if any(by_name.get(k, {}).get('version') != v for k,v in PINS.items()):
        raise RuntimeError('solver changed a frozen version')
    if not by_name['petsc'].get('build_string', by_name['petsc'].get('build', '')).startswith('real_'):
        raise RuntimeError('real PETSc required')
    spec = directory/'explicit.txt'
    urls = []
    for p in packages:
        url = p.get('url')
        if not url or not url.startswith('https://conda.anaconda.org/conda-forge/'):
            raise RuntimeError('unexpected package provenance')
        digest = p.get('md5')
        if not digest:
            raise RuntimeError('missing package digest')
        urls.append(url+'#'+digest)
    spec.write_text('@EXPLICIT\n'+'\n'.join(urls)+'\n')
    run([*common, '--file', spec], 'install', directory, 65, env)
    verify(directory)


def verify(directory):
    packages = [json.loads(p.read_text()) for p in sorted((PREFIX/'conda-meta').glob('*.json'))]
    by_name = {p['name']:p for p in packages}
    mismatches = {k:by_name.get(k,{}).get('version') for k,v in PINS.items()
                  if by_name.get(k,{}).get('version') != v}
    if mismatches:
        raise RuntimeError('installed pin mismatch: '+repr(mismatches))
    code = 'import json,sys; print(json.dumps(dict(executable=sys.executable,version=".".join(map(str,sys.version_info[:3])))))'
    python = json.loads(run([PREFIX/'bin/python', '-I', '-S', '-c', code], 'python', directory, 5))
    if python['version'] != PINS['python']:
        raise RuntimeError('actual interpreter version mismatch')
    metadata = {}
    for pattern in ['ffcx-*.dist-info/METADATA','fenics_ffcx-*.dist-info/METADATA','petsc4py-*.dist-info/METADATA']:
        for p in (PREFIX/'lib/python3.12/site-packages').glob(pattern):
            metadata[str(p.relative_to(PREFIX))] = [line for line in p.read_text().splitlines()
                                                   if line.startswith(('Name:','Version:','Requires-Python:'))]
    publish(directory/'verification.json', dict(pins=PINS, python=python,
            executable_sha256=hashlib.sha256((PREFIX/'bin/python').resolve().read_bytes()).hexdigest(),
            package_count=len(packages), distribution_metadata=metadata,
            numerical_imports=False))
    (directory/'packages.json').write_text(json.dumps(packages,indent=2,sort_keys=True)+'\n')


def worker(directory, mode):
    reservation = read(directory/'reservation.json')
    held(directory, reservation, _cgroup_path(), verify_source(reservation))
    try:
        (bootstrap if mode == 'bootstrap' else install)(directory)
        publish(directory/'task.json', dict(success=True))
    except Exception as exc:
        publish(directory/'task.json', dict(success=False, error=f'{type(exc).__name__}: {exc}'))
    completed(directory, reservation)


def controller(mode, commit):
    start = time.monotonic()
    if mode == 'bootstrap':
        BASE.mkdir(exist_ok=False)
    if mode == 'install' and start-read(BASE/'bootstrap/result.json')['monotonic_start'] > 720:
        raise RuntimeError('insufficient remaining setup wall allocation')
    directory = BASE/mode
    directory.mkdir(exist_ok=False)
    publish(directory/'reservation.json', dict(source_commit=commit, interpreter=sys.executable,
                                               release_nonce=mode))
    backend = SystemdBackend(ROOT, runtime_seconds=49 if mode == 'bootstrap' else 149)
    handle = None
    record = dict(mode=mode, success=False, fem_attempts=0, monotonic_start=start)
    try:
        handle = backend.start_held([sys.executable, str(Path(__file__).resolve()),
                                    '--worker', str(directory), mode], directory, CAPS)
        record['held_facts'] = verify_held_scope(handle.facts(), handle.scope_id)
        handle.release()
        record['exit'] = handle.wait(52 if mode == 'bootstrap' else 152)
        record['task'] = read(directory/'task.json')
        record['success'] = record['exit']['exit_code'] == 0 and record['task']['success']
    except Exception as exc:
        record['error'] = f'{type(exc).__name__}: {exc}'
    finally:
        handle = handle or backend.active_handle
        if handle:
            try:
                handle.stop()
                record['cleanup'] = handle.cleanup()
                if (not record['cleanup']['empty']
                        or record['cleanup'].get('memory_events', {}).get('max', 1) != 0
                        or record['cleanup'].get('pids_events', {}).get('max', 1) != 0):
                    record['success'] = False
            except Exception as exc:
                record['cleanup_error'] = str(exc)
                record['success'] = False
        record['elapsed_before_save'] = time.monotonic()-start
        if record['elapsed_before_save'] > (60 if mode == 'bootstrap' else 180):
            record['success'] = False
        publish(directory/'result.json',record)
    elapsed = time.monotonic()-start
    if elapsed > (60 if mode == 'bootstrap' else 180):
        publish(directory/'late.json', dict(elapsed=elapsed))
        record['success'] = False
    print(json.dumps(dict(result=record,elapsed_after_result_save=elapsed),indent=2))
    return 0 if record['success'] else 1


if __name__ == '__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--worker':
        worker(Path(sys.argv[2]),sys.argv[3])
    elif len(sys.argv)==3 and sys.argv[1] in ('bootstrap','install'):
        raise SystemExit(controller(sys.argv[1],sys.argv[2]))
    else:
        raise SystemExit('usage: restore.py bootstrap|install COMMIT')
