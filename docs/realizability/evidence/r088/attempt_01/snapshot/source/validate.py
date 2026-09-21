"""Deterministic R088 composed fixtures; imported only in the bounded recorder child."""
from __future__ import annotations
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import hashlib
import json
import sys
import tempfile
import traceback

from integration import (SCHEMA, COUNTS, Domain, Ownership, Owner, Clock, finalize,
    supervise, accept_sentinel, digest, physical)
from primitives import (Policy, GuestReading, TreeReading, ProcessMember, MonitorError,
                        durable_checkpoint)
from host_protocol import HostProtocol
from attempt_accounting import prior_elapsed
import r070_legacy

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else None
INPUT = Path(__file__).resolve().parents[1] / 'inputs'
SAVED = {}


def read(path):
    return json.loads(path.read_text())


def throws(callback):
    try:
        callback()
    except (MonitorError, ValueError, FrozenInstanceError, TypeError, AttributeError):
        return
    raise AssertionError('operation unexpectedly accepted')


def observation(domain, name):
    return dict(schema=SCHEMA, domain=name, container=domain.container,
                identities=[list(v) for v in domain.identities], reaper=list(domain.reaper),
                errors=[], survivors=[], members=[], membership_complete=True,
                root_reaped=True if name == 'workload' else None,
                populated=False if name == 'workload' else None,
                job_active_count=0 if name == 'helper' else None,
                launcher_exited=True if name == 'helper' else None)


class Fixture:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        (self.directory/'input.txt').write_text('deterministic sentinel source\n')
        (self.directory/'evidence.json').write_text('{}\n')
        self.manifest = self.directory/'source_manifest.json'
        durable_checkpoint(self.manifest, dict(schema=1,
            files={'input.txt': r070_legacy.sha(self.directory/'input.txt')},
            evidence_files={'evidence.json': r070_legacy.sha(self.directory/'evidence.json')}))
        ownership = Ownership('r088-fake', 1, 'nonce-r088', r070_legacy.sha(self.manifest),
                              Domain(((10,7),), 'linux-unit/workload', (11,9)),
                              Domain(((20,8),), 'native-job', (21,10)))
        self.owner = Owner(ownership)
        self.time = 0.0
        self.calls = []
        self.queue = []
        self.seq = 0
        self.running_samples = 0
        self.tree_delay = 0.0
        self.persist_delay = 0.0
        self.persist_error = False
        self.verify_delay = {'workload': 0.0, 'helper': 0.0}
        self.fail_stop = None
        self.fail_observe = None
        self.cleanup_mutation = None
        self.guest_delay = 0.0
        self.guest_bytes = 8 << 30
        self.host_bytes = 8 << 30
        self.member_bytes = 0
        self.saved = None

    def now(self):
        return self.time

    def wait(self, delay):
        self.time += delay

    def send(self, data):
        request = json.loads(data)
        self.queue.append((json.dumps(dict(schema=1, sequence=request['sequence'],
            nonce=request['nonce'], status='ok', available_bytes=self.host_bytes,
            total_bytes=16 << 30, error=None, provider_pid=20, provider_created=8))+'\n').encode())

    def poll(self):
        return self.queue.pop(0) if self.queue else None

    def guest(self):
        start = self.time
        self.time += self.guest_delay
        return GuestReading(1, start, self.time, 'linux', 'ok', self.guest_bytes)

    def tree(self):
        start = self.time
        self.time += self.tree_delay
        self.seq += 1
        alive = self.seq <= self.running_samples
        members = (ProcessMember(10,7,'S',self.member_bytes),) if alive else ()
        return TreeReading(self.seq, start, self.time, 'linux', 'ok', members, True, alive,
                           None if alive else 0)

    def release(self, ownership):
        self.calls.append('release')
        assert ownership is self.owner.ownership

    def stop(self, name, domain):
        self.calls.append('stop:'+name)
        assert domain is getattr(self.owner.ownership, name)
        if self.fail_stop == name:
            raise RuntimeError('injected dispatch failure')

    def observe(self, name, domain):
        self.calls.append('observe:'+name)
        self.time += self.verify_delay[name]
        if self.fail_observe == name:
            raise RuntimeError('injected verification failure')
        value = observation(domain, name)
        if self.cleanup_mutation:
            self.cleanup_mutation(name, value)
        return value

    def persist(self, value):
        self.calls.append('persist')
        durable_checkpoint(self.directory/'candidate.json', value)
        self.saved = read(self.directory/'candidate.json')
        self.time += self.persist_delay
        if self.persist_error:
            raise OSError('injected persistence error after write')
        return digest(self.saved)

    def callbacks(self):
        return dict(stop={n: (lambda d, n=n: self.stop(n,d)) for n in ('workload','helper')},
                    observe={n: (lambda d, n=n: self.observe(n,d)) for n in ('workload','helper')},
                    persist=self.persist)

    def run(self, **changes):
        arguments = dict(policy=Policy(1536,10), outer_deadline=15.0, now=self.now,
            guest=self.guest, transport_send=self.send, transport_poll=self.poll,
            tree=self.tree, wait=self.wait, release=self.release, **self.callbacks())
        arguments.update(changes)
        self.monitor = supervise(self.owner, **arguments)
        self.child = dict(schema=SCHEMA, ownership=self.owner.ownership.record(),
            counts={key:0 for key in COUNTS}, cleanup=deepcopy(self.monitor['finalization']['candidate']['cleanup']),
            source_manifest_sha256=self.owner.ownership.manifest_sha256, status='sentinel_complete')
        return self.accept()

    def accept(self, monitor=None, child=None, saved=None):
        return accept_sentinel(self.owner.ownership, self.monitor if monitor is None else monitor,
            self.child if child is None else child, source_root=self.directory,
            source_manifest_path=self.manifest, persisted_candidate=self.saved if saved is None else saved)


def fixture():
    # Deterministic content; disposable path is not used as a scientific input.
    return Fixture(tempfile.mkdtemp(prefix='case-', dir=SCRATCH))


def test_positive_composition_and_physical_deny():
    f=fixture(); result=f.run()
    assert result['status']=='complete' and result['counts']=={k:0 for k in COUNTS}
    assert f.calls==['release','stop:workload','stop:helper','observe:workload','observe:helper','persist']
    assert f.saved['status']=='candidate'
    throws(lambda: physical(enabled=True, child_launcher=lambda: (_ for _ in ()).throw(AssertionError())))
    launched=[]
    refused=r070_legacy.guarded_launch(f.directory/'disabled', enabled=True,
                                      child_launcher=lambda: launched.append(True))
    assert refused['status']=='prerequisite_refused' and not launched
    assert not (f.directory/'physical-attempt.json').exists()
    SAVED['positive']={'monitor': f.monitor, 'child': f.child, 'candidate': f.saved, 'result': result}


def test_every_acquired_state_and_idempotency():
    for state in ('RESERVED','OWNED_HELD','READY','RUNNING'):
        for domains in ('both','workload','helper','none'):
            f=fixture()
            ownership=replace(f.owner.ownership,
                workload=f.owner.ownership.workload if domains in ('both','workload') else None,
                helper=f.owner.ownership.helper if domains in ('both','helper') else None)
            f.owner=Owner(ownership)
            for target in ('OWNED_HELD','READY','RUNNING'):
                if f.owner.state==state: break
                f.owner.advance(target)
            f.owner.fail('injected prior failure')
            first=finalize(f.owner,clock=Clock(f.now),outer_deadline=15,**f.callbacks())
            calls=list(f.calls)
            second=finalize(f.owner,clock=Clock(lambda: (_ for _ in ()).throw(AssertionError())),
                            outer_deadline=15,**f.callbacks())
            assert first==second and f.calls==calls and first['receipt']['status']=='refused'
            assert ('stop:workload' in calls)==(ownership.workload is not None)
            assert ('stop:helper' in calls)==(ownership.helper is not None)


def test_cleanup_failure_orders():
    for field in ('fail_stop','fail_observe'):
        for domain in ('workload','helper'):
            f=fixture(); setattr(f,field,domain)
            assert f.run()['status']=='partial_failed'
            assert f.calls.index('stop:workload') < f.calls.index('observe:workload')
            assert f.calls.index('stop:helper') < f.calls.index('observe:workload')
            assert 'observe:helper' in f.calls
    f=fixture(); f.cleanup_mutation=lambda n,v:v.update(launcher_exited=False) if n=='helper' else None
    assert f.run()['status']=='partial_failed'


def test_owned_identity_and_schema_refusals():
    f=fixture(); assert f.run()['status']=='complete'
    throws(lambda:setattr(f.owner.ownership,'attempt',2))
    throws(lambda:setattr(f.owner,'ownership',replace(f.owner.ownership,attempt=2)))
    for change in ({'attempt':True},{'run_id':''},{'manifest_sha256':'bad'}):
        throws(lambda change=change:Owner(replace(f.owner.ownership,**change)))
    mutations=[lambda v:v['ownership'].update(attempt=2),
               lambda v:v['ownership'].update(attempt=True),
               lambda v:v['cleanup']['workload'].update(identities=[[999,999]]),
               lambda v:v['cleanup']['helper'].update(job_active_count=False),
               lambda v:v['cleanup']['helper'].update(launcher_exited=False),
               lambda v:v['cleanup']['workload'].update(populated=True),
               lambda v:v['cleanup']['workload'].update(root_reaped=False),
               lambda v:v.update(schema=4.0)]
    for mutate in mutations:
        m=deepcopy(f.monitor); c=deepcopy(f.child)
        candidate=m['finalization']['candidate']; mutate(candidate)
        m['finalization']['receipt']['candidate_sha256']=digest(candidate)
        c['cleanup']=deepcopy(candidate['cleanup'])
        assert f.accept(m,c,candidate)['status']=='partial_failed'
    for value in (False,0.0,None,1):
        c=deepcopy(f.child); c['counts'][COUNTS[0]]=value
        assert f.accept(child=c)['status']=='partial_failed'
    c=deepcopy(f.child); c['physical_meshes']=0
    assert f.accept(child=c)['status']=='partial_failed'
    c=deepcopy(f.child); c['cleanup']['workload']['identities']=[[999,999]]
    assert f.accept(child=c)['status']=='partial_failed'


def test_deadline_cleanup_and_persistence_boundaries():
    for kind in ('verify','persist'):
        for elapsed, expected in ((5.0,'complete'),(5.001,'partial_failed')):
            f=fixture()
            if kind=='verify': f.verify_delay['helper']=elapsed
            else: f.persist_delay=elapsed
            assert f.run()['status']==expected
    f=fixture(); f.verify_delay={'workload':3.0,'helper':2.001}
    assert f.run()['status']=='partial_failed'
    f=fixture(); f.persist_error=True
    assert f.run()['status']=='partial_failed' and f.saved['status']=='candidate'
    f=fixture(); f.persist_delay=6
    assert f.run()['status']=='partial_failed'
    SAVED['cleanup_write_overrun']={'candidate':f.saved,'receipt':f.monitor['finalization']['receipt']}


def test_clock_faults_and_policy_types():
    for value in (float('nan'),-1.0,True):
        f=fixture()
        assert f.run(now=lambda:value)['status']=='partial_failed'
        assert 'stop:workload' in f.calls and 'stop:helper' in f.calls
    for field,value in (('schema',3.0),('schema',True),('cleanup_limit_s',6),('host_interval_s',1)):
        f=fixture(); assert f.run(policy=replace(Policy(1536,10),**{field:value}))['status']=='partial_failed'
        assert 'release' not in f.calls and 'observe:helper' in f.calls
    f=fixture(); calls=[0]
    def fail_clock():
        if 'stop:workload' in f.calls: raise RuntimeError('clock disappeared')
        return f.time
    assert f.run(now=fail_clock)['status']=='partial_failed'
    assert 'observe:helper' in f.calls
    f=fixture(); f.time=1.0
    f.cleanup_mutation=lambda n,v:setattr(f,'time',0.0)
    assert f.run()['status']=='partial_failed'


def test_early_launch_and_callback_refusals():
    for field,value in (('guest_bytes',4096*(1<<20)-1),('host_bytes',2560*(1<<20)-1),('guest_delay',1.001)):
        f=fixture(); setattr(f,field,value)
        assert f.run()['status']=='partial_failed' and 'release' not in f.calls
        assert f.monitor['counts']=={k:0 for k in COUNTS}
    f=fixture()
    def release_then_fail(_):
        raise RuntimeError('released but callback failed')
    assert f.run(release=release_then_fail)['status']=='partial_failed'
    assert all(v is None for v in f.monitor['counts'].values())
    f=fixture(); assert f.run(outer_deadline=14.999)['status']=='partial_failed'
    assert 'release' not in f.calls


def wire(sequence=1,nonce='n',**changes):
    value=dict(schema=1,sequence=sequence,nonce=nonce,status='ok',available_bytes=8<<30,
               total_bytes=16<<30,error=None,provider_pid=20,provider_created=8)
    value.update(changes)
    return (json.dumps(value)+'\n').encode()


def test_protocol_terminal_request_and_order():
    p=HostProtocol(nonce='n',clock=lambda:0); p.request(1,0)
    throws(lambda:p.request(2,.1)); throws(lambda:p.reply(wire(),.2))
    for invalid in (True,1.0,0):
        p=HostProtocol(nonce='n',clock=lambda:0)
        throws(lambda:p.request(invalid,0)); throws(lambda:p.request(1,0))
    p=HostProtocol(nonce='n',clock=lambda:0); p.request(1,0); p.reply(wire(),.2)
    throws(lambda:p.request(2,.05)); throws(lambda:p.reply(wire(2),.1))
    throws(lambda:HostProtocol(nonce='n',clock=lambda:0,max_line_bytes=8192))


def test_protocol_framing_timeout_and_exact_types():
    for data in (wire()+b'x',wire()*2,b'x'*4097,wire(schema=1.0),wire(sequence=True),
                 wire(available_bytes=True),wire(nonce='wrong'),wire(status='error',available_bytes=None,total_bytes=None,error='API')):
        p=HostProtocol(nonce='n',clock=lambda:0); p.request(1,0)
        try: p.feed(data,.1)
        except MonitorError: pass
        assert p.terminal_error is not None
        throws(lambda:p.request(2,.5))
    p=HostProtocol(nonce='n',clock=lambda:0); p.request(1,0)
    line=wire(); assert p.feed(line[:10],.1) is None
    assert p.feed(line[10:],.2).status=='ok'
    p.request(2,.5); assert p.expired(1.0)
    throws(lambda:p.feed(wire(2),1.0))
    p=HostProtocol(nonce='n',clock=lambda:0); p.request(1,0)
    throws(lambda:p.feed(b'',.1,eof=True))
    p=HostProtocol(nonce='n',clock=lambda:0); p.request(1,0)
    throws(lambda:p.reply(wire(),.5))
    p=HostProtocol(nonce='n',clock=lambda:0); p.request(1,0); p.reply(wire(),.1)
    p.request(2,.9); throws(lambda:p.reply(wire(2),1.001))


def test_runtime_boundaries_and_simultaneous_stops():
    f=fixture(); f.running_samples=2; f.member_bytes=1536<<20
    assert f.run()['status']=='complete'  # RSS equality passes.
    f=fixture(); f.running_samples=1; f.member_bytes=(1536<<20)+1; f.tree_delay=10
    assert f.run()['status']=='partial_failed'
    assert {'tree_rss_limit','wall_time_limit','host_deadline_or_terminal'} <= set(f.monitor['reasons'])
    f=fixture(); f.tree_delay=10
    assert f.run()['status']=='partial_failed' and 'wall_time_limit' in f.monitor['reasons']
    f=fixture(); f.running_samples=1; f.tree_delay=1.001
    assert f.run()['status']=='partial_failed'
    f=fixture()
    def wrong_host(): return wire(nonce='nonce-r088',provider_pid=999)
    assert f.run(transport_poll=wrong_host)['status']=='partial_failed'


def test_absolute_scheduler_and_tree_refusals():
    f=fixture(); f.running_samples=2; f.tree_delay=.13
    assert f.run()['status']=='complete'
    starts=[row['start'] for row in f.monitor['samples']]
    assert all(abs(a-b)<1e-12 for a,b in zip(starts,[0,.15,.3]))
    for change in ({'membership_complete':False},{'root_returncode':False},
                   {'root_returncode':7},{'members':(ProcessMember(10,7,'S',0),)}):
        f=fixture()
        reading=TreeReading(1,0,0,'linux','ok',(),True,False,0)
        assert f.run(tree=lambda change=change:replace(reading,**change))['status']=='partial_failed'


def test_fake_independent_guard_event_order():
    f=fixture()
    for state in ('OWNED_HELD','READY','RUNNING'): f.owner.advance(state)
    f.owner.released=True
    # A deterministic blocked inner task yields forever. The separate guard
    # event advances independently; this launches no threads or live signals.
    def blocked_inner():
        yield 'blocked_provider'
        raise AssertionError('blocked inner task must never resume')
    inner=blocked_inner(); assert next(inner)=='blocked_provider'
    f.time=.25; f.owner.fail('independent_guard_deadline')
    result=finalize(f.owner,clock=Clock(f.now),outer_deadline=7,**f.callbacks())
    assert result['receipt']['status']=='refused' and 'observe:helper' in f.calls
    inner.close()
    SAVED['fake_guard']={'events':['inner_blocked','guard_deadline',*f.calls], 'result':result,
                        'scope':'pure event model, not a live independent guard'}


def test_accounting_exact_returncode_and_history():
    ledger=read(INPUT/'r084_attempt_ledger.json')['attempts']
    reconciliations=read(INPUT/'r084_reconciliations.json')['reconciliations']
    total=prior_elapsed(ledger,reconciliations=reconciliations)
    assert total==15.69079346198123
    for value in (False,0.0,None):
        changed=deepcopy(ledger); changed[-1]['validator_returncode']=value
        throws(lambda:prior_elapsed(changed,reconciliations=reconciliations))
    for field,value in (('state','STARTED'),('resource_stop',True),('timed_out',True),
                        ('outer_elapsed_seconds',None),('child_lifetime_peak_rss_bytes',True)):
        changed=deepcopy(ledger); changed[-1][field]=value
        throws(lambda:prior_elapsed(changed,reconciliations=reconciliations))
    from recorder_policy import classify, admit
    for code,timeout,error in ((-9,False,''),(-24,False,''),(1,False,'MemoryError'),(None,True,'')):
        assert classify(code,timeout,error,0)!='passed'
    for history in ([{'state':'STARTED'}],[{'state':'COMPLETED','status':'failed'}],None):
        throws(lambda:admit(history))
    throws(lambda:admit([dict(schema=1,state='COMPLETED',status='passed',returncode=False,
        charged_seconds=1,resource_stop=False,receipt_sha256='a'*64)]))


def test_source_and_saved_evidence_bindings():
    manifest=read(Path(__file__).resolve().parents[1]/'inventory.json')
    root=Path(__file__).resolve().parents[1]
    for name, expected in manifest['files'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected
    f=fixture(); assert f.run()['status']=='complete'
    (f.directory/'input.txt').write_text('changed\n')
    assert f.accept()['status']=='partial_failed'
    f=fixture(); assert f.run()['status']=='complete'
    changed=deepcopy(f.monitor); changed['finalization']['receipt']['observed_at']=6
    assert f.accept(monitor=changed)['status']=='partial_failed'


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    global SCRATCH
    scratch_owner = tempfile.TemporaryDirectory(prefix='r088-fixtures-')
    SCRATCH = Path(scratch_owner.name)
    tests=sorted((name,fn) for name,fn in globals().items() if name.startswith('test_') and callable(fn))
    progress=dict(schema=1,attempt=1,state='STARTED',registered=[n for n,_ in tests],checks=[])
    durable_checkpoint(OUT/'progress.json',progress)
    try:
        for name,fn in tests:
            progress['active']=name
            durable_checkpoint(OUT/'progress.json',progress)
            fn()
            progress['checks'].append(dict(name=name,status='passed'))
            durable_checkpoint(OUT/'progress.json',progress)
        progress.update(state='COMPLETED',active=None,status='passed')
    except BaseException as exc:
        progress.update(state='COMPLETED',status='failed',exception=type(exc).__name__,
                        traceback=traceback.format_exc())
        durable_checkpoint(OUT/'progress.json',progress)
        raise
    durable_checkpoint(OUT/'progress.json',progress)
    durable_checkpoint(OUT/'fixtures.json',dict(schema=1,status='passed',attempt=1,
        checks=progress['checks'],examples=SAVED,physical_enabled=False))
    scratch_owner.cleanup()
    print(json.dumps(dict(status='passed',groups=len(tests))))


if __name__=='__main__': main()
