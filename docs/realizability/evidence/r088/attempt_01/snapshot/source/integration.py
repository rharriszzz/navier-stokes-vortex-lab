"""R088 fixture-only composition. No OS acquisition, process launch or physical API.

Effects are injected. Stop dispatch must be nonblocking; an independent owner
must drive finalization if an inner callback does not return (tested with a
fake event scheduler). This module does not claim to implement that OS guard.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from copy import deepcopy
import hashlib
import math
from typing import Callable

from primitives import (MonitorError, Policy, GuestReading, TreeReading,
                        _number, _integer, _validate_tree, finite_json, validate_launch)
from host_protocol import HostProtocol
import r070_legacy

SCHEMA = 4
COUNTS = r070_legacy.COUNT_KEYS
DOMAINS = ('workload', 'helper')
TRANSITIONS = {'RESERVED': ('OWNED_HELD', 'STOPPING'),
               'OWNED_HELD': ('READY', 'STOPPING'), 'READY': ('RUNNING', 'STOPPING'),
               'RUNNING': ('STOPPING',), 'STOPPING': ('FINALIZED',), 'FINALIZED': ()}


def digest(value):
    return hashlib.sha256(finite_json(value).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise MonitorError(message)


def identity(value):
    require(type(value) is tuple and len(value) == 2 and
            all(type(part) is int and part > 0 for part in value), 'invalid immutable identity')


@dataclass(frozen=True)
class Domain:
    """Identity tokens stand for future owned handles, never paths to open here."""
    identities: tuple[tuple[int, int], ...]
    container: str
    reaper: tuple[int, int]

    def validate(self):
        require(type(self.identities) is tuple and bool(self.identities), 'missing identities')
        for item in self.identities:
            identity(item)
        require(len(set(self.identities)) == len(self.identities), 'duplicate identities')
        identity(self.reaper)
        require(type(self.container) is str and bool(self.container), 'missing container token')


@dataclass(frozen=True)
class Ownership:
    run_id: str
    attempt: int
    nonce: str
    manifest_sha256: str
    workload: Domain | None
    helper: Domain | None

    def validate(self):
        for value in (self.run_id, self.nonce):
            require(type(value) is str and bool(value), 'missing run identity')
        _integer('attempt', self.attempt, minimum=1)
        require(type(self.manifest_sha256) is str and len(self.manifest_sha256) == 64 and
                all(c in '0123456789abcdef' for c in self.manifest_sha256), 'invalid manifest hash')
        for name in DOMAINS:
            value = getattr(self, name)
            require(value is None or type(value) is Domain, 'domain must be immutable')
            if value is not None:
                value.validate()

    def record(self):
        # Normalize tuples for byte-for-byte comparison across saved JSON.
        import json
        return json.loads(finite_json(asdict(self)))


class Owner:
    def __init__(self, ownership: Ownership):
        require(type(ownership) is Ownership, 'invalid ownership schema')
        ownership.validate()
        self._ownership = ownership
        self.state = 'RESERVED'
        self.history = [self.state]
        self.errors = []
        self.released = False
        self.cleanup = None
        self.final_result = None
        self.finalizing = False

    @property
    def ownership(self):
        return self._ownership

    def fail(self, error):
        self.errors.append(str(error)[:1024])

    def advance(self, target):
        if target not in TRANSITIONS[self.state] or (self.errors and target != 'STOPPING'):
            self.fail('state transition refused')
            raise MonitorError('state transition refused')
        self.state = target
        self.history.append(target)


class Clock:
    def __init__(self, provider):
        self.provider = provider
        self.last = None

    def read(self):
        value = _number('monotonic clock', self.provider())
        require(self.last is None or value >= self.last, 'monotonic clock regressed')
        self.last = value
        return value


def cleanup_observation(domain: Domain, name: str, value):
    expected = {'schema', 'domain', 'container', 'identities', 'reaper', 'errors',
                'survivors', 'members', 'membership_complete', 'root_reaped',
                'populated', 'job_active_count', 'launcher_exited'}
    require(type(value) is dict and set(value) == expected, 'cleanup schema differs')
    require(type(value['schema']) is int and value['schema'] == SCHEMA, 'cleanup schema type')
    require(value['domain'] == name and value['container'] == domain.container and
            value['identities'] == [list(item) for item in domain.identities] and
            value['reaper'] == list(domain.reaper), 'cleanup owner mismatch')
    for item in value['identities'] + [value['reaper']]:
        require(type(item) is list, 'wire identity must be a list')
        identity(tuple(item))
    require(value['errors'] == [] and type(value['errors']) is list and
            value['survivors'] == [] and type(value['survivors']) is list and
            value['members'] == [] and type(value['members']) is list and
            value['membership_complete'] is True, 'cleanup failed or unknown')
    if name == 'workload':
        require(value['root_reaped'] is True and value['populated'] is False and
                value['job_active_count'] is None and value['launcher_exited'] is None,
                'Linux cleanup lacks reaping/empty-group evidence')
    else:
        require(value['root_reaped'] is None and value['populated'] is None and
                type(value['job_active_count']) is int and value['job_active_count'] == 0 and
                value['launcher_exited'] is True, 'native cleanup lacks Job/launcher evidence')
    return deepcopy(value)


def finalize(owner: Owner, *, clock: Clock, outer_deadline: float,
             stop: dict[str, Callable], observe: dict[str, Callable],
             persist: Callable[[dict], str]) -> dict:
    """All owned states, even latched failures. Re-entry returns the saved result.

    A stop callback dispatches only; it must never wait for native completion.
    Independent guard ownership is necessary for a blocked callback.
    """
    if owner.final_result is not None:
        return deepcopy(owner.final_result)
    require(not owner.finalizing, 'concurrent finalization needs the independent guard')
    owner.finalizing = True
    owner.state = 'STOPPING'
    owner.history.append('STOPPING')
    start = None
    end = None
    try:
        start = clock.read()
    except BaseException as exc:
        owner.fail(exc)
    try:
        _number('outer deadline', outer_deadline, positive=True)
    except BaseException as exc:
        owner.fail(exc)
        outer_deadline = 0.0
    deadline = min(start + 5.0, outer_deadline) if start is not None else 0.0
    requested = {}
    observations = {}

    def boundary():
        nonlocal end
        try:
            end = clock.read()
            require(start is not None and end <= deadline, 'cleanup/persistence deadline exceeded')
        except BaseException as exc:
            owner.fail(exc)

    # No clock or verification callback can interrupt dispatch to the second domain.
    for name in DOMAINS:
        domain = getattr(owner.ownership, name)
        if domain is None:
            requested[name] = 'not_acquired'
            observations[name] = None
            continue
        requested[name] = 'stop_requested'
        try:
            stop[name](domain)
        except BaseException as exc:
            owner.fail(f'{name} stop: {type(exc).__name__}: {exc}')
    boundary()
    for name in DOMAINS:
        domain = getattr(owner.ownership, name)
        if domain is None:
            continue
        try:
            observations[name] = cleanup_observation(domain, name, observe[name](domain))
        except BaseException as exc:
            observations[name] = None
            owner.fail(f'{name} verification: {type(exc).__name__}: {exc}')
        boundary()
    owner.cleanup = observations
    owner.state = 'FINALIZED'
    owner.history.append('FINALIZED')
    candidate = {'schema': SCHEMA, 'status': 'candidate', 'ownership': owner.ownership.record(),
                 'history': list(owner.history), 'released': owner.released,
                 'requested': requested, 'cleanup': observations, 'errors': list(owner.errors),
                 'cleanup_started': start, 'cleanup_observed': end,
                 'cleanup_deadline': deadline}
    saved_hash = None
    try:
        saved_hash = persist(deepcopy(candidate))
        require(type(saved_hash) is str and saved_hash == digest(candidate), 'persistence digest mismatch')
    except BaseException as exc:
        owner.fail(f'persistence: {type(exc).__name__}: {exc}')
    boundary()
    # Candidate on disk is never itself an acceptance certificate. This receipt
    # observes the write's return, with monotonic time and the independent guard
    # left responsible for persistence of the receipt and enclosing lifetime.
    receipt = {'schema': SCHEMA, 'status': 'accepted' if not owner.errors else 'refused',
               'candidate_sha256': saved_hash, 'observed_at': end,
               'errors': list(owner.errors)}
    owner.final_result = {'candidate': candidate, 'receipt': receipt}
    owner.finalizing = False
    return deepcopy(owner.final_result)


def supervise(owner: Owner, *, policy: Policy, outer_deadline: float, now,
              guest, transport_send, transport_poll, tree, wait, release,
              stop, observe, persist) -> dict:
    """One authoritative host protocol and ownership path; injected operations only."""
    clock = Clock(now)
    protocol = HostProtocol(nonce=owner.ownership.nonce, clock=now)
    root_code = None
    report = {'schema': SCHEMA, 'returncode': None, 'samples': [], 'reasons': [],
              'protocol_terminal': None, 'counts': {k: 0 for k in COUNTS}}
    try:
        policy.validate()
        _number('outer deadline', outer_deadline, positive=True)
        require(outer_deadline >= policy.deadline + 5.0,
                'cleanup reserve missing before release')
        require(not owner.errors and owner.state == 'RESERVED', 'owner already stopped or used')
        require(owner.ownership.workload is not None and owner.ownership.helper is not None,
                'both owned domains required before release')
        owner.advance('OWNED_HELD')
        started = clock.read()
        phase = started
        next_tree = started
        next_host = started
        host = None
        prior_tree_end = started
        tree_seq = 0

        def active_boundary():
            current = clock.read()
            if current >= policy.deadline:
                report['reasons'].append('wall_time_limit')
            if protocol.expired(current):
                report['reasons'].append('host_deadline_or_terminal')
            require(not report['reasons'], 'active deadline or host failure')
            return current

        while True:
            current = active_boundary()
            if protocol.pending is None and current >= next_host:
                wire = protocol.request(protocol.last_sequence + 1, current)
                transport_send(wire)
                active_boundary()
                # Absolute cadence; skip missed slots without shifting the phase.
                next_host = phase + (math.floor((current - phase) / 0.5) + 1) * 0.5
            chunk = transport_poll()
            current = active_boundary()  # checks previous send before accepting replacement
            if chunk is not None:
                host = protocol.feed(chunk, current)
                active_boundary()
                if host is not None:
                    expected = owner.ownership.helper.identities[0]
                    require((host.provider_pid, host.provider_created) == expected,
                            'host provider differs from owned helper')
                    require(host.available_bytes >= 1024 << 20, 'host_pressure_limit')
            if not owner.released and host is not None:
                g = guest()
                current = active_boundary()
                validate_launch(now=current, policy=policy, guest=g, host=host)
                owner.advance('READY')
                # Recheck the independent gates immediately before the held release.
                current = active_boundary()
                validate_launch(now=current, policy=policy, guest=g, host=host)
                owner.advance('RUNNING')
                owner.released = True  # callback may release then fail; counts become unknown
                report['counts'] = {k: None for k in COUNTS}
                release(owner.ownership)
                active_boundary()
            if owner.released and current >= next_tree:
                call_start = clock.read()
                reading = tree()
                captured = clock.read()
                seq, begin, end, rss = _validate_tree(reading, captured, tree_seq, prior_tree_end)
                require(begin >= call_start, 'tree reading predates callback')
                if rss > policy.tree_cap_mib:
                    report['reasons'].append('tree_rss_limit')
                if captured >= policy.deadline:
                    report['reasons'].append('wall_time_limit')
                if protocol.expired(captured):
                    report['reasons'].append('host_deadline_or_terminal')
                tree_seq, prior_tree_end = seq, end
                report['samples'].append({'sequence': seq, 'start': begin, 'end': end,
                                          'decision': captured, 'rss_mib': rss})
                require(not report['reasons'], 'runtime stop')
                if not reading.root_alive:
                    root_code = reading.root_returncode
                    require(type(root_code) is int and root_code == 0 and not reading.members,
                            'abnormal root exit or remaining members')
                    break
                next_tree = phase + (math.floor((captured - phase) / 0.05) + 1) * 0.05
                current = captured
            target = min(next_tree if owner.released else current + 0.05,
                         next_host, policy.deadline,
                         protocol.pending[1] + 0.5 if protocol.pending else policy.deadline)
            delay = max(0.0, target - clock.read())
            wait(delay)
            active_boundary()
    except BaseException as exc:
        owner.fail(f'{type(exc).__name__}: {exc}')
    report['protocol_terminal'] = protocol.terminal_error
    report['returncode'] = root_code
    report['finalization'] = finalize(owner, clock=clock, outer_deadline=outer_deadline,
                                      stop=stop, observe=observe, persist=persist)
    report['status'] = 'completed' if (not owner.errors and type(root_code) is int and root_code == 0) else 'stopped_partial'
    return report


def accept_sentinel(owner: Ownership, monitor: dict, child: dict, *, source_root,
                    source_manifest_path, persisted_candidate: dict) -> dict:
    """R070 acceptance adapter; the child cannot nominate its cleanup owner.

    Reuses archived R070 semantic checks only after the composed v4 proof has
    passed strict ownership/receipt checks. No physical entry is enabled.
    """
    failed = {'schema': SCHEMA, 'status': 'partial_failed', 'counts': {k: None for k in COUNTS}}
    try:
        owner.validate()
        require(type(monitor) is dict and set(monitor) == {'schema', 'status', 'returncode',
            'samples', 'reasons', 'protocol_terminal', 'counts', 'finalization'}, 'monitor fields')
        require(type(monitor['schema']) is int and monitor['schema'] == SCHEMA and
                monitor['status'] == 'completed' and monitor['reasons'] == [] and
                monitor['protocol_terminal'] is None and type(monitor['returncode']) is int and
                monitor['returncode'] == 0, 'monitor stopped or malformed')
        final = monitor['finalization']
        require(type(final) is dict and set(final) == {'candidate', 'receipt'}, 'finalization fields')
        candidate, receipt = final['candidate'], final['receipt']
        require(type(candidate) is dict and set(candidate) == {'schema', 'status', 'ownership',
            'history', 'released', 'requested', 'cleanup', 'errors', 'cleanup_started',
            'cleanup_observed', 'cleanup_deadline'}, 'candidate fields')
        require(type(receipt) is dict and set(receipt) == {'schema', 'status',
            'candidate_sha256', 'observed_at', 'errors'}, 'receipt fields')
        require(type(candidate['schema']) is int and candidate['schema'] == SCHEMA and
                type(receipt['schema']) is int and receipt['schema'] == SCHEMA and
                candidate['status'] == 'candidate' and receipt['status'] == 'accepted' and
                candidate['errors'] == [] and receipt['errors'] == [], 'candidate/receipt refused')
        require(candidate == persisted_candidate and receipt['candidate_sha256'] == digest(candidate),
                'durable candidate binding differs')
        require(candidate['ownership'] == owner.record() and child['ownership'] == owner.record(),
                'run/attempt/owner mismatch')
        # Canonical bytes also reject Python bool/int and float/int equality aliases.
        require(digest(candidate['ownership']) == digest(owner.record()) and
                digest(child['ownership']) == digest(owner.record()), 'owner type mismatch')
        require(candidate['released'] is True and candidate['history'] ==
                ['RESERVED', 'OWNED_HELD', 'READY', 'RUNNING', 'STOPPING', 'FINALIZED'] and
                candidate['requested'] == {name: 'stop_requested' for name in DOMAINS}, 'lifecycle mismatch')
        start = _number('cleanup start', candidate['cleanup_started'])
        observed = _number('cleanup observed', candidate['cleanup_observed'])
        deadline = _number('cleanup deadline', candidate['cleanup_deadline'])
        received = _number('receipt time', receipt['observed_at'])
        require(start <= observed <= received <= deadline <= start + 5.0, 'cleanup time bounds')
        require(type(candidate['cleanup']) is dict and set(candidate['cleanup']) == set(DOMAINS),
                'cleanup domains differ')
        require(type(child) is dict and set(child) == {'schema', 'ownership', 'counts', 'cleanup',
                'source_manifest_sha256', 'status'}, 'child schema fields')
        require(type(child['schema']) is int and child['schema'] == SCHEMA and
                child['status'] == 'sentinel_complete', 'child schema/status')
        require(digest(child['cleanup']) == digest(candidate['cleanup']), 'child cleanup differs')
        require(type(child['counts']) is dict and set(child['counts']) == set(COUNTS) and
                all(type(v) is int and v == 0 for v in child['counts'].values()), 'six exact sentinel zeros required')
        manifest = r070_legacy.read_json(source_manifest_path)
        require(type(manifest.get('schema')) is int and manifest['schema'] == 1, 'manifest schema type')
        require(child['source_manifest_sha256'] == owner.manifest_sha256 and
                r070_legacy.sha(source_manifest_path) == owner.manifest_sha256, 'manifest binding')
        legacy_cleanup = {}
        for name in DOMAINS:
            domain = getattr(owner, name)
            require(domain is not None, 'missing owned domain')
            value = cleanup_observation(domain, name, candidate['cleanup'][name])
            legacy_cleanup[name] = {'confirmed': True, 'status': 'cleanup_confirmed',
                'survivors': [], 'errors': [], 'identities': value['identities'],
                'requested_actions': ['stop', 'verify']}
        legacy_child = dict(schema=2, status='complete', stage='fixture', evidence_complete=True,
            primary_reasons=[], errors=[], counts=child['counts'],
            workload_cleanup=legacy_cleanup['workload'], helper_cleanup=legacy_cleanup['helper'],
            scientific_checks_passed=True, source_manifest_sha256=owner.manifest_sha256)
        legacy_watch = dict(schema=3, status='completed', stop_reason=None, returncode=0,
            membership_complete=True, cleanup_confirmed=True, primary_reasons=[], secondary_errors=[],
            workload_cleanup=legacy_cleanup['workload'], helper_cleanup=legacy_cleanup['helper'],
            source_manifest_sha256=owner.manifest_sha256, cleanup_errors=[], survivors=[],
            child_report_sha256=digest(legacy_child))
        result = r070_legacy.finalize_child(r070_legacy.initial_report(), legacy_watch, legacy_child,
                       source_root=source_root, source_manifest_path=source_manifest_path)
        require(result['status'] == 'complete', 'R070 evidence/source acceptance refused')
        return {'schema': SCHEMA, 'status': 'complete', 'counts': deepcopy(child['counts']),
                'ownership': owner.record(), 'receipt_sha256': digest(receipt)}
    except (ValueError, TypeError, KeyError, AttributeError, r070_legacy.Refusal) as exc:
        failed['error'] = f'{type(exc).__name__}: {exc}'
        return failed


def physical(*args, **kwargs):
    raise MonitorError('physical CLI/API hard-disabled; fixture-only composition')


if __name__ == '__main__':
    physical()
