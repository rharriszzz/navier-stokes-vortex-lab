"""Exclusive R097 fake-fixture attempt; actual timing exclusions are explicit."""
import time
ENTRY = time.monotonic()
from pathlib import Path
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('w') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    fd=os.open(path.parent,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)


def caps():
    resource.setrlimit(resource.RLIMIT_AS,(256<<20,256<<20))
    resource.setrlimit(resource.RLIMIT_CPU,(10,10))
    resource.setrlimit(resource.RLIMIT_FSIZE,(1<<20,1<<20))


def main():
    assert sys.version_info[:3]==(3,12,13)
    out=HERE/'attempt_01'; out.mkdir(exist_ok=False)
    save(out/'started.json',dict(schema=1,request='R097',attempt=1,state='STARTED',
        total_reservation_seconds=120,setup_final_reserved_seconds=20,
        child_wall_limit_seconds=60,child_address_space_bytes=256<<20,
        python=sys.version,historical_allowances_reset=False))
    snapshot=out/'snapshot'; snapshot.mkdir()
    paths=list((HERE/'source').glob('*.py'))+[HERE/'run.py',HERE/'contract.md']
    inventory={}
    origins={}
    for path in paths:
        name=str(path.relative_to(HERE)); target=snapshot/name
        target.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(path,target)
        inventory[name]=sha(target); origins[name]=str(path.relative_to(ROOT))
    for name,rel in {'r096_review.md':'docs/realizability/B2_MONITOR_R088_REVIEW.md',
                     'handoff.md':'SESSION_HANDOFF.md'}.items():
        target=snapshot/name; shutil.copyfile(ROOT/rel,target)
        inventory[name]=sha(target); origins[name]=rel
    save(snapshot/'inventory.json',dict(schema=1,files=inventory,origins=origins))
    save(out/'bound.json',dict(schema=1,request='R097',attempt=1,
        inventory_sha256=sha(snapshot/'inventory.json'),started_sha256=sha(out/'started.json')))
    start=time.monotonic(); code=None; timed_out=False; error=None
    remaining=120-(start-ENTRY)-20
    try:
        if remaining<=0: raise RuntimeError('setup exhausted child reservation')
        with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
            proc=subprocess.run([sys.executable,'-B',str(snapshot/'source/validate.py'),str(out/'output')],
                stdout=stdout,stderr=stderr,timeout=min(60,remaining),preexec_fn=caps)
            code=proc.returncode
    except subprocess.TimeoutExpired:
        timed_out=True
    except BaseException as exc:
        error=f'{type(exc).__name__}: {exc}'
    end=time.monotonic()
    unchanged=all(sha(snapshot/n)==h and sha(ROOT/origins[n])==h for n,h in inventory.items())
    rss=int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024)
    observed=time.monotonic()-ENTRY
    charged=observed+5
    status='passed' if type(code) is int and code==0 and not timed_out and not error and unchanged and charged<=120 and rss<=256<<20 else 'STOP_REVIEW_REQUIRED'
    result=dict(schema=1,request='R097',attempt=1,state='COMPLETED',status=status,
        returncode=code,timed_out=timed_out,error=error,child_seconds=end-start,
        child_lifetime_peak_rss_bytes=rss,unchanged_inputs=unchanged,
        output_sha256={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()},
        observed_guard_seconds=observed,unmeasured_final_reserve_seconds=5,
        charged_seconds=charged,total_reservation_seconds=120,
        exclusions=['guard interpreter startup before ENTRY','guard final receipt/ledger persistence and exit'],
        whole_recorder_certified=False,live_enabled=False)
    save(out/'receipt.json',result)
    save(HERE/'ledger.json',dict(schema=1,request='R097',attempts=[dict(attempt=1,state='COMPLETED',
        status=status,charged_seconds=charged,receipt_sha256=sha(out/'receipt.json'))],
        total_charged_seconds=charged,total_reservation_seconds=120,retry_enabled=False))
    print(json.dumps(result,indent=2))
    return 0 if status=='passed' else 1


if __name__=='__main__': raise SystemExit(main())
