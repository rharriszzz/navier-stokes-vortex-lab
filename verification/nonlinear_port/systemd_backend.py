"""Linux held-worker backend, not whole-task admission.

This configures kernel limits and manager expiry for the worker and descendants.
Independent expiry has not yet been demonstrated by the bounded live probe.
Short systemd command clients run in the caller's scope. Consequently this
backend honestly reports all_task_processes_in_scope=False: supervise_once
refuses a FEM release until that remaining whole-task boundary is resolved.
No default execution entry point or admission is provided.
"""
from pathlib import Path
import re
import subprocess
import time
import uuid

from .handshake import publish, read
from .prototype import Refusal
from .supervision import CAPS


THREAD_ENV = ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
              'NUMEXPR_NUM_THREADS', 'BLIS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS')
PROPERTIES = ('ControlGroup', 'LoadState', 'ActiveState', 'SubState', 'MainPID',
              'ExecMainCode', 'ExecMainStatus', 'Result', 'RuntimeMaxUSec',
              'TimeoutStopUSec', 'KillMode', 'SendSIGKILL', 'Restart')


def command(*args):
    """Finite control client; never a shell or an implicit retry."""
    result = subprocess.run(args, text=True, capture_output=True, timeout=3)
    if result.returncode:
        raise Refusal(f'control command failed: {args[0]}: {result.stderr.strip()}')
    return result.stdout


def seconds(value):
    units = {'min': 60, 's': 1, 'ms': .001, 'us': .000001}
    tokens = re.findall(r'(\d+(?:\.\d+)?)(min|ms|us|s)', value)
    if not tokens or ''.join(n+u for n, u in tokens) != value.replace(' ', ''):
        raise Refusal('unknown manager time format')
    return sum(float(n)*units[u] for n, u in tokens)


class SystemdBackend:
    def __init__(self, working_directory, *, runtime_seconds=149):
        if type(runtime_seconds) is not int or not 1 <= runtime_seconds <= 149:
            raise Refusal('bounded independent runtime required')
        self.root = Path(working_directory).resolve()
        self.runtime = runtime_seconds
        self.active_handle = None

    def start_held(self, argv, directory, caps):
        if caps != CAPS or self.active_handle is not None:
            raise Refusal('frozen caps and one backend invocation required')
        h = Handle(self.root, Path(directory).resolve(), self.runtime)
        # Preserve an addressable unit even if its start/held handshake fails.
        self.active_handle = h
        h.start(argv)
        return h


class Handle:
    def __init__(self, root, directory, runtime):
        self.root, self.directory, self.runtime = root, directory, runtime
        self.unit = 'navier-poiseuille-'+uuid.uuid4().hex+'.service'
        self.scope_id = None
        self.resource_snapshot = None
        self.stopped = False
        self.pid = None
        self.reservation = read(directory/'reservation.json')

    def show(self):
        output = command('systemctl', '--user', 'show', self.unit,
                         '--property='+','.join(PROPERTIES))
        return dict(line.split('=', 1) for line in output.splitlines() if '=' in line)

    def start(self, argv):
        if not argv or not Path(argv[0]).is_absolute():
            raise Refusal('absolute worker executable required')
        command('systemd-run', '--user', '--unit='+self.unit,
                '--property=Type=exec', '--property=Restart=no',
                '--property=RemainAfterExit=yes',
                '--property=MemoryMax=1610612736', '--property=MemorySwapMax=0',
                '--property=TasksMax=32', '--property=MemoryAccounting=yes',
                '--property=TasksAccounting=yes', '--property=KillMode=control-group',
                '--property=SendSIGKILL=yes', '--property=TimeoutStopSec=1',
                '--property=RuntimeMaxSec='+str(self.runtime),
                '--property=WorkingDirectory='+str(self.root),
                '--property=StandardOutput=append:'+str(self.directory/'worker.log'),
                '--property=StandardError=append:'+str(self.directory/'worker.log'),
                *('--setenv='+k+'=1' for k in THREAD_ENV),
                '--', *map(str, argv))
        deadline = time.monotonic()+5
        while not (self.directory/'held.json').exists():
            if time.monotonic() >= deadline:
                raise Refusal('worker did not reach held state')
            time.sleep(.02)
        self.hello = read(self.directory/'held.json')
        self.pid = self.hello.get('pid')
        props = self.show()
        self.scope_id = props.get('ControlGroup')
        if (not self.scope_id or self.scope_id == '/'
                or not self.scope_id.endswith('/'+self.unit)
                or self.hello.get('cgroup') != self.scope_id
                or self.hello.get('nonce') != self.reservation['release_nonce']
                or type(self.pid) is not int or self.pid <= 0
                or props.get('MainPID') != str(self.pid)
                or props.get('ActiveState') != 'active'):
            raise Refusal('held worker and manager identity disagree')
        self.group = Path('/sys/fs/cgroup')/self.scope_id.lstrip('/')

    def integer(self, name):
        value = (self.group/name).read_text().strip()
        if not value.isdecimal():
            raise Refusal('unresolved finite cgroup counter: '+name)
        return int(value)

    def events(self, name):
        return {key: int(value) for key, value in
                (line.split() for line in (self.group/name).read_text().splitlines())}

    def pids(self):
        # No delegated subgroups are permitted in this finite backend.
        if any(p.is_dir() for p in self.group.iterdir()):
            raise Refusal('unexpected task sub-cgroup')
        return [int(v) for v in (self.group/'cgroup.procs').read_text().split()]

    def facts(self):
        props = self.show()
        if (props['KillMode'] != 'control-group' or props['SendSIGKILL'] != 'yes'
                or props['Restart'] != 'no' or props['MainPID'] != str(self.pid)
                or props['ControlGroup'] != self.scope_id):
            raise Refusal('manager expiry or ownership settings changed')
        if self.pids() != [self.pid] or self.integer('pids.current') != 1:
            raise Refusal('unexpected processes in held scope')
        threads = self.hello.get('threads', {})
        if set(threads) != set(THREAD_ENV[:4]) or any(v != '1' for v in threads.values()):
            raise Refusal('worker thread settings not observed')
        return dict(cgroup_path=self.scope_id,
                    memory_max_bytes=self.integer('memory.max'),
                    swap_max_bytes=self.integer('memory.swap.max'),
                    pids_max=self.integer('pids.max'),
                    independent_expiry_seconds=seconds(props['RuntimeMaxUSec'])
                                               +seconds(props['TimeoutStopUSec']),
                    worker_held=not (self.directory/'release.json').exists(),
                    all_task_processes_in_scope=False,
                    worker_descendants_in_scope=True, mpi_ranks=1, threads=1,
                    control_clients_in_worker_scope=False)

    def release(self):
        publish(self.directory/'release.json', dict(nonce=self.reservation['release_nonce'],
                                                    cgroup=self.scope_id))

    def snapshot(self):
        if self.pids() != [self.pid]:
            raise Refusal('worker completed with unconfirmed descendants')
        return dict(memory_peak_bytes=self.integer('memory.peak'),
                    memory_events=self.events('memory.events'),
                    pids_peak=self.integer('pids.peak'),
                    pids_events=self.events('pids.events'),
                    sampled_pids=[self.pid],
                    measurement_boundary='before final worker handshake/exit; limits remain active')

    def wait(self, timeout):
        deadline = time.monotonic()+timeout
        while time.monotonic() < deadline:
            if (self.directory/'finished.json').exists():
                finished = read(self.directory/'finished.json')
                if finished != dict(nonce=self.reservation['release_nonce']):
                    raise Refusal('worker completion nonce mismatch')
                self.resource_snapshot = self.snapshot()
                publish(self.directory/'resource_snapshot.json', self.resource_snapshot)
                publish(self.directory/'exit.json', finished)
                break
            props = self.show()
            if props['ActiveState'] in ('failed', 'inactive'):
                raise Refusal('worker failed before completion: '+props.get('Result', 'unknown'))
            time.sleep(.05)
        else:
            raise Refusal('worker wait deadline exceeded')
        while time.monotonic() < deadline:
            props = self.show()
            if (props['ActiveState'] in ('inactive', 'failed')
                    or (props['ActiveState'] == 'active' and props['SubState'] == 'exited')):
                if props.get('MainPID') != '0':
                    raise Refusal('worker exit not established')
                return dict(exit_code=int(props['ExecMainStatus'])
                            if props.get('ExecMainCode') == '1' else -1,
                            manager_result=props['Result'], unit=self.unit)
            time.sleep(.02)
        raise Refusal('actual worker exit deadline exceeded')

    def stop(self):
        props = self.show()
        if props.get('LoadState') != 'not-found':
            command('systemctl', '--user', 'stop', self.unit)
        self.stopped = True

    def cleanup(self):
        props = self.show()
        empty = (self.stopped and (props.get('MainPID') == '0'
                                  or props.get('LoadState') == 'not-found')
                 and props.get('ActiveState') in ('inactive', 'failed')
                 and not props.get('ControlGroup'))
        if self.scope_id:
            path = Path('/sys/fs/cgroup')/self.scope_id.lstrip('/')
            empty = empty and not path.exists()
        return dict(self.resource_snapshot or {}, empty=empty,
                    unknown_children=not empty, unit=self.unit,
                    manager_final=props,
                    resource_snapshot_complete=self.resource_snapshot is not None)
