"""Pure completion admission. Witness authority is injected, never OS-certified."""
from dataclasses import asdict, dataclass
import hashlib
from primitives import Policy, MonitorError, finite_json, _number, _integer


def need(condition, message):
    if not condition:
        raise MonitorError(message)


def digest(value):
    return hashlib.sha256(finite_json(value).encode()).hexdigest()


def token(value):
    need(type(value) is str and bool(value), 'missing identity token')


@dataclass(frozen=True)
class Admission:
    owner_sha256: str
    policy: Policy
    reserved_at: float
    recorder_deadline: float
    enclosing_deadline: float
    clock_domain: str
    recorder: str
    observer: str
    backstop: str

    def validate(self, owner):
        need(type(self.policy) is Policy, 'policy must be frozen Policy')
        self.policy.validate()
        need(self.owner_sha256 == digest(owner.record()), 'admission owner mismatch')
        for value in (self.clock_domain, self.recorder, self.observer, self.backstop):
            token(value)
        need(len({self.recorder, self.observer, self.backstop}) == 3, 'observer not independent')
        begin = _number('reservation start', self.reserved_at)
        end = _number('recorder deadline', self.recorder_deadline)
        enclosing = _number('enclosing deadline', self.enclosing_deadline)
        need(begin < self.policy.deadline and self.policy.deadline + 5 <= end < enclosing,
             'insufficient admitted reservation')

    def sha256(self):
        return digest(asdict(self))


@dataclass(frozen=True)
class TerminalWitness:
    """Trusted external facts in one admitted clock domain; fake adapter only."""
    receipt_sha256: str
    observer: str
    backstop: str
    clock_domain: str
    armed_at: float
    armed_deadline: float
    receipt_durable_at: float
    observer_exited_at: float
    exit_code: int
    terminal_confirmed: bool
    timed_out: bool
    resource_stop: bool


def validate_monitor(monitor, child, admission, keys):
    need(type(monitor) is dict and type(child) is dict, 'monitor/child object required')
    counts = monitor['counts']
    need(type(counts) is dict and set(counts) == set(keys), 'monitor count fields')
    child_counts = child['counts']
    need(type(child_counts) is dict and set(child_counts) == set(keys), 'child count fields')
    for key, value in counts.items():
        need(type(child_counts[key]) is int and child_counts[key] == 0, 'child sentinel count')
        if value is not None:
            _integer('known monitor count', value)
            need(value == child_counts[key], 'contradictory known monitor count')
    rows = monitor['samples']
    need(type(rows) is list and bool(rows), 'missing runtime sample evidence')
    prior = admission.reserved_at
    for index, row in enumerate(rows, 1):
        need(type(row) is dict and set(row) == {'sequence', 'start', 'end', 'decision',
             'rss_mib', 'root_alive', 'root_returncode', 'member_count', 'membership_complete'},
             'runtime sample fields')
        _integer('sample sequence', row['sequence'], minimum=1)
        need(row['sequence'] == index, 'sample sequence gap or repetition')
        start = _number('sample start', row['start'])
        end = _number('sample end', row['end'])
        decision = _number('sample decision', row['decision'])
        rss = _number('sample rss', row['rss_mib'])
        need(prior <= start <= end <= decision < admission.policy.deadline,
             'sample ordering/absolute deadline')
        need(rss <= admission.policy.tree_cap_mib, 'sample RSS stop')
        need(row['membership_complete'] is True and type(row['root_alive']) is bool,
             'unknown membership or root state')
        _integer('member count', row['member_count'])
        if index < len(rows):
            need(row['root_alive'] is True and row['root_returncode'] is None and
                 row['member_count'] > 0, 'sample after terminal or missing live root')
        else:
            need(row['root_alive'] is False and type(row['root_returncode']) is int and
                 row['root_returncode'] == 0 and row['member_count'] == 0,
                 'missing terminal root/empty membership')
        prior = decision
    need(prior <= _number('cleanup start', monitor['finalization']['candidate']['cleanup_started']),
         'cleanup precedes last runtime sample')


def validate_outer(receipt, witness, admission, owner, monitor, child, candidate):
    need(type(receipt) is dict and set(receipt) == {'schema', 'state', 'admission_sha256',
         'owner_sha256', 'source_manifest_sha256', 'monitor_sha256', 'child_sha256',
         'candidate_sha256', 'inner_receipt_sha256', 'recorder', 'observer', 'clock_domain',
         'observer_started_at', 'recorder_started_at', 'last_output_durable_at',
         'recorder_exited_at', 'receipt_write_started_at', 'returncode', 'timed_out',
         'resource_stop'}, 'outer receipt fields')
    need(type(receipt['schema']) is int and receipt['schema'] == 1 and
         receipt['state'] == 'COMPLETED', 'outer open/schema')
    bindings = dict(admission_sha256=admission.sha256(), owner_sha256=digest(owner.record()),
         source_manifest_sha256=owner.manifest_sha256, monitor_sha256=digest(monitor),
         child_sha256=digest(child), candidate_sha256=digest(candidate),
         inner_receipt_sha256=digest(monitor['finalization']['receipt']),
         recorder=admission.recorder, observer=admission.observer, clock_domain=admission.clock_domain)
    need(all(type(receipt[k]) is str and receipt[k] == v for k, v in bindings.items()),
         'outer identity/content mismatch')
    need(type(receipt['returncode']) is int and receipt['returncode'] == 0 and
         receipt['timed_out'] is False and receipt['resource_stop'] is False, 'outer stop')
    observer, recorder, durable, exited, write = [_number(k, receipt[k]) for k in
         ('observer_started_at', 'recorder_started_at', 'last_output_durable_at',
          'recorder_exited_at', 'receipt_write_started_at')]
    inner = _number('inner receipt', monitor['finalization']['receipt']['observed_at'])
    first = monitor['samples'][0]['start']
    need(admission.reserved_at <= observer <= recorder <= first <= inner <= durable <= exited
         <= admission.recorder_deadline and exited <= write, 'outer chronology/deadline')
    need(type(witness) is TerminalWitness, 'missing independent terminal witness')
    need(witness.receipt_sha256 == digest(receipt) and witness.observer == admission.observer and
         witness.backstop == admission.backstop and witness.clock_domain == admission.clock_domain,
         'terminal witness binding')
    armed = _number('armed at', witness.armed_at)
    bound = _number('armed deadline', witness.armed_deadline)
    persisted = _number('receipt durable at', witness.receipt_durable_at)
    terminal = _number('observer exited at', witness.observer_exited_at)
    need(armed <= observer and bound == admission.enclosing_deadline and
         write <= persisted <= terminal <= bound, 'unpersisted/late/unarmed observer')
    need(type(witness.exit_code) is int and witness.exit_code == 0 and
         witness.terminal_confirmed is True and witness.timed_out is False and
         witness.resource_stop is False, 'unconfirmed outer terminal event')
