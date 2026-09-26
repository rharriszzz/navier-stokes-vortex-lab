"""Read-only metadata reconciliation; never execute the partial interpreter."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path('/tmp/navier-r227-restore')
PREFIX = Path('/tmp/navier-fenicsx')
OUT = Path(__file__).parent
plan_file = BASE/'install/plan.stdout'
plan = json.loads(plan_file.read_text())
planned = {p['name']:p for p in plan['actions']['LINK']}
records = [json.loads(p.read_text()) for p in sorted((PREFIX/'conda-meta').glob('*.json'))]
installed = {p['name']:p for p in records}
pins = dict(line.strip()[2:].split('=',1) for line in (ROOT/'environment-b1.yml').read_text().splitlines()
            if line.strip().startswith('- ') and '=' in line)
metadata = {}
for p in PREFIX.glob('lib/python3.12/site-packages/*ffcx*.dist-info/METADATA'):
    metadata[str(p.relative_to(PREFIX))] = [line for line in p.read_text().splitlines()
                                           if line.startswith(('Name:', 'Version:'))]
missing_files = []
file_count = 0
for package in records:
    for name in package.get('files', []):
        file_count += 1
        path = PREFIX/name
        if not path.exists() and not path.is_symlink():
            missing_files.append(dict(package=package['name'], path=name))
result = dict(status='PARTIAL_UNVALIDATED', prefix=str(PREFIX),
    planned_package_count=len(planned), installed_record_count=len(installed),
    planned_without_record=sorted(set(planned)-set(installed)),
    unexpected_records=sorted(set(installed)-set(planned)),
    version_build_mismatches=[name for name,p in planned.items() if name in installed and
        (p['version'],p.get('build_string',p.get('build'))) !=
        (installed[name]['version'],installed[name]['build'])],
    pins={name:dict(required=version, installed=installed.get(name,{}).get('version'),
                   build=installed.get(name,{}).get('build')) for name,version in pins.items()},
    metadata_file_entries_checked=file_count, missing_file_count=len(missing_files),
    missing_files=missing_files,
    missing_nonbytecode_file_count=sum(not x['path'].endswith('.pyc') for x in missing_files),
    conda_history_bytes=(PREFIX/'conda-meta/history').stat().st_size,
    plan_fetch_count=len(plan['actions'].get('FETCH',[])),
    plan_fetch_bytes=sum(p.get('size',0) for p in plan['actions'].get('FETCH',[])),
    distribution_metadata=metadata,
    standalone_interpreter_check_executed=False, inspector_numerical_imports=False,
    executable_sha256=hashlib.sha256((PREFIX/'bin/python').resolve().read_bytes()).hexdigest(),
    raw_plan_sha256=hashlib.sha256(plan_file.read_bytes()).hexdigest(),
    missing_completion_evidence=[name for name in ('verification.json','packages.json','resource_snapshot.json')
                                 if not (BASE/'install'/name).exists()],
    later_cleanup_observation={mode:dict(
        cgroup_absent=not (Path('/sys/fs/cgroup')/json.loads((BASE/mode/'held.json').read_text())['cgroup'].lstrip('/')).exists(),
        worker_pid_absent=not Path('/proc',str(json.loads((BASE/mode/'held.json').read_text())['pid'])).exists())
        for mode in ('bootstrap','install')})
(OUT/'partial_metadata.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
fields=('name','version','build','subdir','url','sha256','md5')
(OUT/'installed_records.json').write_text(json.dumps([{k:p.get(k) for k in fields} for p in records],indent=2,sort_keys=True)+'\n')
print(json.dumps({k:result[k] for k in ['status','planned_package_count','installed_record_count','planned_without_record',
    'version_build_mismatches','metadata_file_entries_checked','missing_file_count','conda_history_bytes',
    'later_cleanup_observation']},indent=2))
