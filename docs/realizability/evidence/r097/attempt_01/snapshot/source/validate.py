"""Deterministic R097 composed fixtures; imported only in the bounded recorder child."""
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
from certificate import Admission, TerminalWitness
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
        ownership = Ownership('r097-fake', 1, 'nonce-r097', r070_legacy.sha(self.manifest),
                              Domain(((10,7),), 'linux-unit/workload', (11,9)),
                              Domain(((20,8),), 'native-job', (21,10)))
        self.admission = Admission(digest(ownership.record()), Policy(1536,10), 0.0, 15.0, 17.0,
                                   'fake-monotonic', 'recorder', 'observer', 'backstop')
        self.owner = Owner(ownership, self.admission)
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
        self.outer, self.witness = self.proof(self.monitor, self.child, self.saved)
        return self.accept()

    def proof(self, monitor, child, saved):
        receipt = dict(schema=1, state='COMPLETED', admission_sha256=self.admission.sha256(),
            owner_sha256=digest(self.owner.ownership.record()),
            source_manifest_sha256=self.owner.ownership.manifest_sha256,
            monitor_sha256=digest(monitor), child_sha256=digest(child),
            candidate_sha256=digest(saved), inner_receipt_sha256=digest(monitor['finalization']['receipt']),
            recorder='recorder', observer='observer', clock_domain='fake-monotonic',
            observer_started_at=0.0, recorder_started_at=0.0,
            last_output_durable_at=self.time, recorder_exited_at=self.time,
            receipt_write_started_at=self.time, returncode=0, timed_out=False, resource_stop=False)
        witness = TerminalWitness(digest(receipt), 'observer', 'backstop', 'fake-monotonic',
            0.0, 17.0, self.time, self.time, 0, True, False, False)
        return receipt, witness

    def accept(self, monitor=None, child=None, saved=None, outer=None, witness=None):
        return accept_sentinel(self.owner.ownership, self.monitor if monitor is None else monitor,
            self.child if child is None else child, source_root=self.directory,
            source_manifest_path=self.manifest, persisted_candidate=self.saved if saved is None else saved,
            admission=self.admission, outer_receipt=self.outer if outer is None else outer,
            terminal_witness=self.witness if witness is None else witness)

    def rebound(self, monitor=None, child=None, saved=None):
        m = self.monitor if monitor is None else monitor
        c = self.child if child is None else child
        p = self.saved if saved is None else saved
        outer, witness = self.proof(m, c, p)
        return self.accept(monitor=m, child=c, saved=p, outer=outer, witness=witness)


def fixture():
    # Deterministic content; disposable path is not used as a scientific input.
    return Fixture(tempfile.mkdtemp(prefix='case-', dir=SCRATCH))



def refused(result):
    assert result['status'] == 'partial_failed', result
    assert all(v is None for v in result['counts'].values())


def test_positive_composed_and_physical_deny():
    f=fixture(); result=f.run()
    assert result['status']=='complete' and result['counts']=={k:0 for k in COUNTS}
    assert result['whole_recorder_certified'] is False and result['live_enabled'] is False
    assert all(v is None for v in f.monitor['counts'].values())
    assert f.calls==['release','stop:workload','stop:helper','observe:workload','observe:helper','persist']
    throws(lambda: physical(enabled=True))
    launched=[]
    assert r070_legacy.guarded_launch(f.directory/'disabled', enabled=True,
        child_launcher=lambda:launched.append(True))['status']=='prerequisite_refused'
    assert not launched
    SAVED['positive']=dict(monitor=f.monitor,child=f.child,candidate=f.saved,outer=f.outer,
                          witness=__import__('dataclasses').asdict(f.witness),result=result)


def test_j01_independent_durable_types():
    f=fixture(); assert f.run()['status']=='complete'
    for value in (5.0,True,None):
        saved=deepcopy(f.saved); saved['schema']=value
        refused(f.rebound(saved=saved))
    saved=deepcopy(f.saved); saved['ownership']['attempt']=1.0
    refused(f.rebound(saved=saved))
    saved=deepcopy(f.saved); saved['extra']=0
    refused(f.rebound(saved=saved))
    m=deepcopy(f.monitor); m['finalization']['candidate']['schema']=5.0
    m['finalization']['receipt']['candidate_sha256']=digest(m['finalization']['candidate'])
    refused(f.rebound(monitor=m,saved=m['finalization']['candidate']))


def test_j02_counts_and_samples():
    f=fixture(); f.running_samples=2; assert f.run()['status']=='complete'
    for value in (7,False,0.0,-1,'0'):
        m=deepcopy(f.monitor); m['counts']={k:value for k in COUNTS}
        refused(f.rebound(monitor=m))
    m=deepcopy(f.monitor); m['counts']={k:0 for k in COUNTS}
    assert f.rebound(monitor=m)['status']=='complete'
    m=deepcopy(f.monitor); m['samples']=[]; refused(f.rebound(monitor=m))
    for key,value in [('sequence',True),('sequence',2),('start',-1),('end',-1),
                      ('decision',10),('rss_mib',1536.001),('membership_complete',False),
                      ('root_alive',0),('root_returncode',0),('member_count',False)]:
        m=deepcopy(f.monitor); m['samples'][0][key]=value; refused(f.rebound(monitor=m))
    for key,value in [('root_alive',True),('root_returncode',False),('member_count',1)]:
        m=deepcopy(f.monitor); m['samples'][-1][key]=value; refused(f.rebound(monitor=m))
    m=deepcopy(f.monitor); m['samples'].reverse(); refused(f.rebound(monitor=m))
    m=deepcopy(f.monitor); m['samples'][0]['extra']=0; refused(f.rebound(monitor=m))


def test_j03_rebased_cleanup_and_admission():
    f=fixture(); assert f.run()['status']=='complete'
    m=deepcopy(f.monitor); candidate=m['finalization']['candidate']; receipt=m['finalization']['receipt']
    candidate.update(cleanup_started=20.0,cleanup_observed=20.0,cleanup_deadline=25.0)
    receipt.update(observed_at=20.0,candidate_sha256=digest(candidate))
    refused(f.rebound(monitor=m,saved=candidate))
    throws(lambda:setattr(f.admission,'recorder_deadline',25))
    throws(lambda:Owner(f.owner.ownership,replace(f.admission,owner_sha256='0'*64)))
    for changes in ({'outer_deadline':25.0},{'policy':Policy(1536,20)}):
        f=fixture(); refused(f.run(**changes)); assert 'release' not in f.calls
        assert 'observe:workload' in f.calls and 'observe:helper' in f.calls


def test_exact_active_cleanup_and_enclosing_boundaries():
    for delay,expected in ((5.0,'complete'),(5.001,'partial_failed')):
        f=fixture(); f.persist_delay=delay; assert f.run()['status']==expected
    f=fixture(); f.tree_delay=10.0; refused(f.run())
    f=fixture(); assert f.run()['status']=='complete'
    outer=deepcopy(f.outer); outer.update(last_output_durable_at=15.0,recorder_exited_at=15.0,
                                         receipt_write_started_at=15.0)
    witness=replace(f.witness,receipt_sha256=digest(outer),receipt_durable_at=17.0,observer_exited_at=17.0)
    assert f.accept(outer=outer,witness=witness)['status']=='complete'
    refused(f.accept(outer=outer,witness=replace(witness,observer_exited_at=17.001)))
    outer['recorder_exited_at']=15.001; outer['receipt_write_started_at']=15.001
    refused(f.accept(outer=outer,witness=replace(witness,receipt_sha256=digest(outer))))


def test_outer_missing_mismatched_open_or_stopped():
    f=fixture(); assert f.run()['status']=='complete'
    refused(f.accept(outer={}))
    refused(f.accept(witness={}))
    for key,value in [('schema',1.0),('state','STARTED'),('admission_sha256','0'*64),
        ('owner_sha256','0'*64),('source_manifest_sha256','0'*64),('monitor_sha256','0'*64),
        ('child_sha256','0'*64),('candidate_sha256','0'*64),('inner_receipt_sha256','0'*64),
        ('observer','recorder'),('recorder','wrong'),('clock_domain','other'),
        ('returncode',False),('timed_out',True),('resource_stop',True),('recorder_started_at',1.0)]:
        outer=deepcopy(f.outer); outer[key]=value
        refused(f.accept(outer=outer,witness=replace(f.witness,receipt_sha256=digest(outer))))


def test_witness_unpersisted_late_unconfirmed():
    f=fixture(); f.persist_delay=1; assert f.run()['status']=='complete'
    for changes in (dict(receipt_sha256='0'*64),dict(observer='recorder'),dict(backstop='wrong'),
        dict(clock_domain='other'),dict(armed_at=0.001),dict(armed_deadline=18.0),
        dict(receipt_durable_at=0.5),dict(observer_exited_at=0.5),dict(observer_exited_at=17.001),
        dict(exit_code=False),dict(terminal_confirmed=False),dict(timed_out=True),dict(resource_stop=True)):
        refused(f.accept(witness=replace(f.witness,**changes)))


def test_partial_cleanup_both_domains_and_unknown_counts():
    for field in ('fail_stop','fail_observe'):
        for domain in ('workload','helper'):
            f=fixture(); setattr(f,field,domain); result=f.run(); refused(result)
            assert all('stop:'+n in f.calls and 'observe:'+n in f.calls for n in ('workload','helper'))
            assert all(v is None for v in f.monitor['counts'].values())
            old=list(f.calls)
            assert finalize(f.owner,clock=Clock(f.now),outer_deadline=15,**f.callbacks())==f.monitor['finalization']
            assert old==f.calls
            SAVED[field+'_'+domain]=dict(monitor=f.monitor,result=result)
    f=fixture(); f.persist_error=True; refused(f.run())
    assert f.saved['status']=='candidate'
    SAVED['persist_failure']=dict(monitor=f.monitor,candidate=f.saved)


def test_sources_registry_and_owner_binding():
    root=Path(__file__).resolve().parents[1]
    inventory=read(root/'inventory.json')
    for name,expected in inventory['files'].items():
        assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected
    f=fixture(); assert f.run()['status']=='complete'
    (f.directory/'input.txt').write_text('changed\n'); refused(f.accept())
    f=fixture(); assert f.run()['status']=='complete'
    m=deepcopy(f.monitor); candidate=m['finalization']['candidate']
    candidate['cleanup']['helper']['reaper']=[999,10]
    m['finalization']['receipt']['candidate_sha256']=digest(candidate)
    child=deepcopy(f.child); child['cleanup']=deepcopy(candidate['cleanup'])
    refused(f.rebound(monitor=m,child=child,saved=candidate))


REGISTRY = [test_positive_composed_and_physical_deny, test_j01_independent_durable_types,
    test_j02_counts_and_samples, test_j03_rebased_cleanup_and_admission,
    test_exact_active_cleanup_and_enclosing_boundaries, test_outer_missing_mismatched_open_or_stopped,
    test_witness_unpersisted_late_unconfirmed, test_partial_cleanup_both_domains_and_unknown_counts,
    test_sources_registry_and_owner_binding]


def main():
    global SCRATCH
    OUT.mkdir(parents=True,exist_ok=True)
    names=[f.__name__ for f in REGISTRY]
    assert len(names)==len(set(names)) and set(names)=={n for n,f in globals().items() if n.startswith('test_') and callable(f)}
    progress=dict(schema=1,attempt=1,state='STARTED',registered=names,checks=[])
    durable_checkpoint(OUT/'progress.json',progress)
    with tempfile.TemporaryDirectory(prefix='r097-fixtures-') as scratch:
        SCRATCH=Path(scratch)
        try:
            for fn in REGISTRY:
                progress['active']=fn.__name__; durable_checkpoint(OUT/'progress.json',progress)
                fn(); progress['checks'].append(dict(name=fn.__name__,status='passed'))
                durable_checkpoint(OUT/'progress.json',progress)
            progress.update(state='COMPLETED',active=None,status='passed')
        except BaseException:
            progress.update(state='COMPLETED',status='failed',traceback=traceback.format_exc())
            durable_checkpoint(OUT/'progress.json',progress)
            durable_checkpoint(OUT/'partial.json',dict(progress=progress,examples=SAVED))
            raise
    durable_checkpoint(OUT/'progress.json',progress)
    durable_checkpoint(OUT/'fixtures.json',dict(schema=1,attempt=1,status='passed',checks=progress['checks'],examples=SAVED))
    print(json.dumps(dict(status='passed',groups=len(REGISTRY))))


if __name__=='__main__': main()
