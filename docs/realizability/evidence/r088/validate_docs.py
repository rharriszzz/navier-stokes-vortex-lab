"""R088 read-only preservation/evidence/docs validation; never reruns a fixture."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess
import unicodedata
from urllib.parse import unquote

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
BASE='3c281981ea370bd3841aa0bf19f1dd07d4d4e4f2'
START='ab41139'
DOCS=['AGENTS.md','REQUEST_LOG.md','WORK_SESSIONS.md','SESSION_HANDOFF.md','STATUS.md',
      'PROJECT_TRACKS.md','docs/realizability/B2_NEXT_STEPS.md',
      'docs/realizability/B2_MONITOR_ADAPTER_REVIEW.md',
      'docs/realizability/B2_MONITOR_LIVE_VALIDATION_CONTRACT.md',
      'docs/realizability/evidence/r088/README.md','docs/realizability/evidence/r088/contract.md']


def git(*args): return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path): return json.loads(path.read_text())


def headings(path):
    result=set(); counts={}
    for line in path.read_text().splitlines():
        match=re.match(r'^#{1,6}\s+(.+?)\s*#*\s*$',line)
        if not match: continue
        title=re.sub(r'\[([^]]+)\]\([^)]*\)',r'\1',match.group(1)).replace('`','')
        slug=re.sub(r'[^\w -]','',unicodedata.normalize('NFKD',title).lower())
        slug=re.sub(r'\s','-',slug.strip())
        n=counts.get(slug,0);counts[slug]=n+1
        result.add(slug if n==0 else f'{slug}-{n}')
    return result


def main():
    preserved=evidence=0
    for record in git('ls-tree','-r','-z',BASE).split(b'\0'):
        if not record: continue
        meta,name=record.split(b'\t',1); name=name.decode()
        if name in DOCS: continue
        payload=(ROOT/name).read_bytes()
        actual=hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()
        assert actual==meta.split()[2].decode(),name
        preserved+=1; evidence+=name.startswith('docs/realizability/evidence/')
    for name in ('REQUEST_LOG.md','WORK_SESSIONS.md'):
        assert (ROOT/name).read_bytes().startswith(git('show',f'{START}:{name}'))
    log=(ROOT/'REQUEST_LOG.md').read_text()
    ids=re.findall(r'^## R(\d+)\b',log,re.M)
    assert len(ids)==len(set(ids)) and max(map(int,ids))==88
    assert 'Token usage: total=167,449 input=143,953 (+ 3,693,184 cached) output=23,496 (reasoning 2,328)' in log
    assert '01a0c579-9ed4-7393-8006-ef2c95fc1b5d' in log
    session=(ROOT/'WORK_SESSIONS.md').read_text().split('## R088 —',1)[1]
    assert session.count('STARTED |')==1 and session.count('COMPLETED |')==1
    handoff=(ROOT/'SESSION_HANDOFF.md').read_text()
    assert handoff.count('## Next task')==1
    assert 'R088 fixture composition complete' in handoff
    assert 'acceptance review of' in handoff and 'outer measurement boundary' in handoff
    links=fragments=0
    for name in DOCS:
        doc=ROOT/name
        for target in re.findall(r'(?<!!)\[[^\]]*\]\(([^)]+)\)',doc.read_text()):
            target=target.split()[0].strip('<>')
            if '://' in target or target.startswith('mailto:'): continue
            filename,_,fragment=target.partition('#')
            dest=(doc.parent/unquote(filename)).resolve() if filename else doc
            assert dest.exists() or dest==HERE/'documentation_validation.json',(name,target)
            links+=1
            if fragment:
                assert fragment in headings(dest),(name,target)
                fragments+=1
    syntax=finite=0
    for path in HERE.rglob('*.py'):
        ast.parse(path.read_text());syntax+=1
    for path in HERE.rglob('*.json'):
        if path.name=='documentation_validation.json':continue
        json.dumps(read(path),allow_nan=False);finite+=1
    snapshot=HERE/'attempt_01/snapshot'
    inventory=read(snapshot/'inventory.json')
    for name,expected in inventory['files'].items():
        assert sha(snapshot/name)==expected,name
    assert set(inventory['files'])=={p.relative_to(snapshot).as_posix() for p in snapshot.rglob('*') if p.is_file() and p.name!='inventory.json'}
    for path in (HERE/'source').glob('*.py'):
        assert path.read_bytes()==(snapshot/'source'/path.name).read_bytes(),path
    assert (HERE/'run.py').read_bytes()==(snapshot/'run.py').read_bytes()
    assert (HERE/'source/r070_legacy.py').read_bytes()==(HERE.parent/'r084/source/r070_copy/launch_guard.py').read_bytes()
    assert (HERE/'contract.md').read_bytes()==(snapshot/'inputs/contract.md').read_bytes()
    receipt=read(HERE/'attempt_01/receipt.json')
    assert receipt['inventory_sha256']==sha(snapshot/'inventory.json')
    assert receipt['status']=='passed' and type(receipt['returncode']) is int and receipt['returncode']==0
    assert receipt['resource_stop'] is False and receipt['timed_out'] is False
    assert receipt['charged_seconds']<120 and receipt['child_lifetime_peak_rss_bytes']<256<<20
    assert receipt['live_guard_certified'] is False and len(receipt['exclusions'])==2
    for name,expected in receipt['output_sha256'].items():
        assert sha(HERE/'attempt_01/output'/name)==expected
    ledger=read(HERE/'ledger.json');row=ledger['attempts'][0]
    assert len(ledger['attempts'])==1 and row['receipt_sha256']==sha(HERE/'attempt_01/receipt.json')
    assert row['charged_seconds']==ledger['cumulative_charged_seconds']==receipt['charged_seconds']
    progress=read(HERE/'attempt_01/output/progress.json')
    fixtures=read(HERE/'attempt_01/output/fixtures.json')
    functions=sorted(n.name for n in ast.parse((HERE/'source/validate.py').read_text()).body
                     if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    assert functions==progress['registered']==[r['name'] for r in fixtures['checks']]
    assert len(functions)==14 and progress['checks']==fixtures['checks']
    assert all(r['status']=='passed' for r in fixtures['checks'])
    assert fixtures['examples']['positive']['result']['status']=='complete'
    assert fixtures['examples']['cleanup_write_overrun']['receipt']['status']=='refused'
    assert fixtures['examples']['fake_guard']['result']['receipt']['status']=='refused'
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    staged = subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,capture_output=True,text=True)
    expected = {
        'docs/realizability/evidence/r088/source/primitives.py:226: new blank line at EOF.',
        'docs/realizability/evidence/r088/attempt_01/snapshot/source/primitives.py:226: new blank line at EOF.'}
    assert set(staged.stdout.splitlines()) == expected and not staged.stderr
    assert staged.returncode != 0
    result=dict(status='passed_with_preserved_source_whitespace_exception',base_commit=BASE,published_start=START,
        staged_whitespace_findings=sorted(expected),
        preserved_files=preserved,preserved_evidence_files=evidence,append_only_logs=2,
        request_ids=len(ids),local_links=links,heading_fragments=fragments,
        python_syntax_files=syntax,finite_json_files=finite,snapshot_bound_files=len(inventory['files']),
        fixture_groups=14,fixture_attempts=1,live_or_physical_runs=0,
        checker_sha256=sha(Path(__file__)),
        limitations='guard startup/final persistence exclusions remain; fixture evidence only',
        delivery_state='completion prepared; actual delivery reported after push')
    (HERE/'documentation_validation.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
