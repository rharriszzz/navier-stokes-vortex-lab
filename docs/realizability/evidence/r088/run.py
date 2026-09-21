"""One-shot R088 guard; child startup/imports/fixtures/final writes are supervised.

This ordinary fixture subprocess is not the proposed live OS workload guard.
Guard startup and its final receipt write remain explicitly outside measurement;
no all-outer-time certification is claimed. Unknown failures prohibit reuse.
"""
import time
ENTRY = time.monotonic()
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE/'source'))
from primitives import durable_checkpoint
from recorder_policy import classify, LIMIT, AS_LIMIT

INPUTS={
    'r084_attempt_ledger.json': HERE.parent/'r084/attempt_ledger.json',
    'r084_reconciliations.json': HERE.parent/'r084/reconciliations.json',
    'r081_live_suite.json': HERE.parent/'r081/live_suite.json',
    'r085_review.md': ROOT/'docs/realizability/B2_MONITOR_R084_REVIEW.md',
    'session_handoff.md': ROOT/'SESSION_HANDOFF.md',
    'request_log.md': ROOT/'REQUEST_LOG.md',
    'work_sessions.md': ROOT/'WORK_SESSIONS.md',
}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def caps():
    resource.setrlimit(resource.RLIMIT_AS,(AS_LIMIT,AS_LIMIT))
    resource.setrlimit(resource.RLIMIT_CPU,(10,10))
    resource.setrlimit(resource.RLIMIT_FSIZE,(1<<20,1<<20))


def main():
    assert sys.version_info[:3]==(3,12,13)
    # One exclusive directory is both the consumed allowance marker and the
    # partial checkpoint root. No alternate output/attempt ID is accepted.
    attempt=HERE/'attempt_01'
    attempt.mkdir(exist_ok=False)
    started=dict(schema=1,attempt=1,state='STARTED',status='partial',
        started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        budget_seconds=LIMIT,setup_final_reserved_seconds=20.0,
        validator_address_space_bytes=AS_LIMIT,python=sys.version,executable=sys.executable)
    durable_checkpoint(attempt/'started.json',started)
    durable_checkpoint(HERE/'ledger.json',dict(schema=1,attempts=[started]))
    snapshot=attempt/'snapshot'; snapshot.mkdir()
    source=snapshot/'source'; source.mkdir()
    inputs=snapshot/'inputs'; inputs.mkdir()
    for path in sorted((HERE/'source').glob('*.py')):
        shutil.copyfile(path,source/path.name)
    shutil.copyfile(HERE/'run.py',snapshot/'run.py')
    shutil.copyfile(HERE/'contract.md',inputs/'contract.md')
    for name,path in INPUTS.items(): shutil.copyfile(path,inputs/name)
    inventory={p.relative_to(snapshot).as_posix():sha(p) for p in sorted(snapshot.rglob('*')) if p.is_file()}
    manifest=dict(schema=1,files=inventory,external_input_origins={k:str(v.relative_to(ROOT)) for k,v in INPUTS.items()},
                  historical_budgets_reset=False,scope='fixture only')
    durable_checkpoint(snapshot/'inventory.json',manifest)
    durable_checkpoint(attempt/'bound.json',dict(schema=1,state='READY',inventory_sha256=sha(snapshot/'inventory.json'),
        setup_elapsed_seconds=time.monotonic()-ENTRY,source_sha256=inventory))
    # Recheck immediately before child admission; no mutable log input is read by child.
    assert all(sha(snapshot/name)==expected for name,expected in inventory.items())
    child_start=time.monotonic()
    remaining=LIMIT-(child_start-ENTRY)-20.0
    assert remaining>0
    output=attempt/'output'; output.mkdir()
    timeout=False
    with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
        try:
            process=subprocess.run([sys.executable,'-B',str(source/'validate.py'),str(output)],
                cwd=snapshot,stdout=stdout,stderr=stderr,timeout=remaining,preexec_fn=caps)
            code=process.returncode
        except subprocess.TimeoutExpired:
            timeout=True; code=None
        child_end=time.monotonic()
        stdout.seek(0); stderr.seek(0)
        out=stdout.read(16384).decode(errors='replace'); err=stderr.read(16384).decode(errors='replace')
    rss=int(resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024)
    status=classify(code,timeout,err,rss)
    unchanged=all(sha(snapshot/name)==expected for name,expected in inventory.items())
    files={p.name:sha(p) for p in output.glob('*.json')}
    fixture=json.loads((output/'fixtures.json').read_text()) if (output/'fixtures.json').exists() else None
    progress=json.loads((output/'progress.json').read_text()) if (output/'progress.json').exists() else None
    complete=(type(fixture) is dict and type(progress) is dict and
              fixture.get('status')=='passed' and progress.get('status')=='passed' and
              progress.get('state')=='COMPLETED' and fixture.get('checks')==progress.get('checks') and
              [r['name'] for r in progress['checks']]==progress['registered'])
    if not complete or not unchanged:
        status='failed_unknown' if status=='passed' else status
    receipt=dict(schema=1,attempt=1,state='COMPLETED',status=status,returncode=code,
        resource_stop=status=='resource_or_unknown_stop',timed_out=timeout,
        stdout=out,stderr=err,child_lifetime_peak_rss_bytes=rss,
        guarded_child_seconds=child_end-child_start,
        observed_guard_seconds=time.monotonic()-ENTRY,
        inventory_sha256=sha(snapshot/'inventory.json'),output_sha256=files,
        unchanged_snapshot=unchanged,complete_progress=complete,
        coverage=['child interpreter startup/imports','all fixture callbacks','child partial/final fsync','child exit'],
        exclusions=['guard interpreter startup before ENTRY','guard final receipt/ledger fsync and exit'],
        unmeasured_guard_persistence_charge_seconds=5.0,
        live_guard_certified=False)
    receipt['charged_seconds']=time.monotonic()-ENTRY+5.0
    if receipt['charged_seconds']>LIMIT:
        receipt.update(status='resource_or_unknown_stop',resource_stop=True)
    durable_checkpoint(attempt/'receipt.json',receipt)
    row={k:receipt[k] for k in ('schema','state','status','returncode','resource_stop','charged_seconds')}
    row['receipt_sha256']=sha(attempt/'receipt.json')
    durable_checkpoint(HERE/'ledger.json',dict(schema=1,limit_seconds=LIMIT,attempts=[row],
        cumulative_charged_seconds=row['charged_seconds'],unknown_intervals_not_zero=True))
    print(json.dumps(receipt,indent=2))
    return 0 if receipt['status']=='passed' else 1


if __name__=='__main__': raise SystemExit(main())
