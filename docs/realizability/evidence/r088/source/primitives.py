"""Versioned, platform-neutral monitor policy; operating-system effects inject."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Callable, Iterable

SCHEMA_VERSION = 3
TREE_INTERVAL_S = 0.05
HOST_REQUEST_INTERVAL_S = 0.5
HOST_MAX_GAP_S = 1.0
LAUNCH_MAX_AGE_S = 30.0
HOST_MINIMUM_MIB = 1024
MAX_CHECKPOINT_BYTES = 1 << 20


class MonitorError(ValueError):
    pass


def _number(name: str, value: object, *, positive: bool = False) -> float:
    if type(value) not in (int, float):
        raise MonitorError(f"{name} must be numeric")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise MonitorError(f"{name} is outside its finite range") from exc
    if not math.isfinite(result) or (result <= 0 if positive else result < 0):
        raise MonitorError(f"{name} is outside its finite range")
    return result


def _integer(name: str, value: object, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise MonitorError(f"{name} must be an integer >= {minimum}")
    return value


def finite_json(value: object) -> str:
    """Serialize reports with unknown values as null and reject NaN/Infinity."""
    try:
        return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise MonitorError(f"report is not finite JSON: {exc}") from exc


def durable_checkpoint(path: Path, report: dict) -> None:
    """Atomically persist one bounded, finite report and sync file plus directory."""
    path = Path(path)
    payload = (finite_json(report) + "\n").encode("utf-8")
    if len(payload) > MAX_CHECKPOINT_BYTES:
        raise MonitorError("checkpoint exceeds the one MiB schema bound")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


@dataclass(frozen=True)
class Policy:
    tree_cap_mib: float
    deadline: float
    tree_interval_s: float = TREE_INTERVAL_S
    host_interval_s: float = HOST_REQUEST_INTERVAL_S
    host_minimum_mib: float = HOST_MINIMUM_MIB
    cleanup_limit_s: float = 5.0
    schema: int = SCHEMA_VERSION

    def validate(self) -> None:
        if type(self.schema) is not int or self.schema != SCHEMA_VERSION:
            raise MonitorError("unsupported policy schema")
        _number("tree cap", self.tree_cap_mib, positive=True)
        _number("deadline", self.deadline, positive=True)
        _number("tree interval", self.tree_interval_s, positive=True)
        _number("host interval", self.host_interval_s, positive=True)
        _number("host minimum", self.host_minimum_mib)
        _number("cleanup limit", self.cleanup_limit_s, positive=True)
        if (self.tree_interval_s != TREE_INTERVAL_S or
                self.host_interval_s != HOST_REQUEST_INTERVAL_S or
                self.host_minimum_mib != HOST_MINIMUM_MIB or self.cleanup_limit_s != 5.0):
            raise MonitorError("fixed monitor cadence/floors/cleanup policy cannot be relaxed")
        if self.host_interval_s > HOST_MAX_GAP_S:
            raise MonitorError("host request interval exceeds maximum host gap")


@dataclass(frozen=True)
class GuestReading:
    sequence: int
    start: float
    end: float
    machine: str
    status: str
    available_bytes: int | None
    error: str | None = None


@dataclass(frozen=True)
class HostReading:
    sequence: int
    start: float
    end: float
    machine: str
    status: str
    available_bytes: int | None
    total_bytes: int | None
    error: str | None = None
    nonce: str = "fixture"
    provider_pid: int = 1
    provider_created: int = 1


@dataclass(frozen=True)
class ProcessMember:
    pid: int
    start_ticks: int
    state: str
    rss_bytes: int


@dataclass(frozen=True)
class TreeReading:
    sequence: int
    start: float
    end: float
    machine: str
    status: str
    members: tuple[ProcessMember, ...]
    membership_complete: bool
    root_alive: bool
    root_returncode: int | None
    error: str | None = None


def _bracket(label: str, seq: object, start: object, end: object, now: float,
             previous: int) -> tuple[int, float, float]:
    sequence = _integer(f"{label} sequence", seq, minimum=1)
    first = _number(f"{label} start", start)
    last = _number(f"{label} end", end)
    current = _number("clock", now)
    if sequence <= previous or first > last or last > current:
        raise MonitorError(f"invalid {label} acquisition bracket/order")
    return sequence, first, last


def _require_previous_host_fresh(now: float, previous_accepted_send: float | None) -> None:
    if previous_accepted_send is not None and now - previous_accepted_send > HOST_MAX_GAP_S:
        raise MonitorError("previous host baseline expired before replacement")


def validate_launch(*, now: float, policy: Policy, guest: GuestReading,
                    host: HostReading) -> dict:
    """Check independent guest and Windows host gates; this function cannot launch."""
    policy.validate()
    current = _number("launch clock", now)
    _guest_seq, guest_start, _guest_end = _bracket(
        "guest launch", guest.sequence, guest.start, guest.end, current, 0)
    if guest.status != "ok" or not guest.machine or guest.error is not None:
        raise MonitorError("guest launch reading failed")
    guest_bytes = _integer("guest available bytes", guest.available_bytes)
    guest = guest_bytes / (1 << 20)
    guest_age = current - guest_start
    if guest_age < 0 or guest_age > LAUNCH_MAX_AGE_S or guest_bytes < (4096 << 20):
        raise MonitorError("guest launch gate failed or is stale")
    _bracket("host launch", host.sequence, host.start, host.end, current, 0)
    if host.status != "ok" or not host.machine or host.error is not None:
        raise MonitorError("host launch reading failed")
    available = _integer("host available bytes", host.available_bytes)
    total = _integer("host total bytes", host.total_bytes, minimum=1)
    required = int((policy.tree_cap_mib + 1024) * (1 << 20))
    age = current - host.start
    if age < 0 or age > LAUNCH_MAX_AGE_S or available < required or available > total:
        raise MonitorError("Windows host launch headroom gate failed")
    return {"status": "passed", "guest_available_mib": guest,
            "guest_age_seconds": guest_age, "host_available_bytes": available,
            "host_required_bytes": required, "host_age_seconds": age}


def _validate_tree(reading: TreeReading, now: float, previous_seq: int,
                   previous_end: float) -> tuple[int, float, float, float]:
    seq, start, end = _bracket("tree", reading.sequence, reading.start,
                               reading.end, now, previous_seq)
    if reading.status != "ok" or not reading.machine or reading.error is not None:
        raise MonitorError("tree provider failed")
    if type(reading.membership_complete) is not bool or type(reading.root_alive) is not bool:
        raise MonitorError("tree flags must be Boolean")
    if not reading.membership_complete:
        raise MonitorError("tree membership coverage is incomplete")
    if start < previous_end:
        raise MonitorError("tree acquisition brackets overlap or regress")
    seen: set[tuple[int, int]] = set()
    seen_pids: set[int] = set()
    rss = 0
    for member in reading.members:
        pid = _integer("member pid", member.pid, minimum=1)
        start_ticks = _integer("member start identity", member.start_ticks, minimum=1)
        if (pid, start_ticks) in seen or pid in seen_pids:
            raise MonitorError("duplicate process identity")
        seen.add((pid, start_ticks))
        seen_pids.add(pid)
        if member.state not in {"R", "S", "D", "T", "t", "Z", "X", "I"}:
            raise MonitorError("invalid process state")
        rss += _integer("member RSS bytes", member.rss_bytes)
    rss_mib = rss / (1 << 20)
    root_code = reading.root_returncode
    if not reading.root_alive and (isinstance(root_code, bool) or not isinstance(root_code, int)):
        raise MonitorError("exited root requires integer return code")
    return seq, start, end, rss_mib

