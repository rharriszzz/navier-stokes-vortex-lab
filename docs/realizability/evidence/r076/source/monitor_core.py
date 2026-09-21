"""Versioned, platform-neutral monitor policy; operating-system effects inject."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import math
from typing import Callable, Iterable

SCHEMA_VERSION = 2
TREE_INTERVAL_S = 0.05
HOST_REQUEST_INTERVAL_S = 0.5
HOST_MAX_GAP_S = 1.0
LAUNCH_MAX_AGE_S = 30.0
HOST_MINIMUM_MIB = 1024


class MonitorError(ValueError):
    pass


def _number(name: str, value: object, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MonitorError(f"{name} must be numeric")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise MonitorError(f"{name} is outside its finite range") from exc
    if not math.isfinite(result) or (result <= 0 if positive else result < 0):
        raise MonitorError(f"{name} is outside its finite range")
    return result


def _integer(name: str, value: object, *, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise MonitorError(f"{name} must be an integer >= {minimum}")
    return value


def finite_json(value: object) -> str:
    """Serialize reports with unknown values as null and reject NaN/Infinity."""
    try:
        return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))
    except (TypeError, ValueError) as exc:
        raise MonitorError(f"report is not finite JSON: {exc}") from exc


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
        if self.schema != SCHEMA_VERSION or isinstance(self.schema, bool):
            raise MonitorError("unsupported policy schema")
        _number("tree cap", self.tree_cap_mib, positive=True)
        _number("deadline", self.deadline, positive=True)
        _number("tree interval", self.tree_interval_s, positive=True)
        _number("host interval", self.host_interval_s, positive=True)
        _number("host minimum", self.host_minimum_mib)
        _number("cleanup limit", self.cleanup_limit_s, positive=True)
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


def validate_launch(*, now: float, policy: Policy, guest: GuestReading,
                    host: HostReading) -> dict:
    """Check independent guest and Windows host gates; this function cannot launch."""
    policy.validate()
    current = _number("launch clock", now)
    _guest_seq, _guest_start, guest_end = _bracket(
        "guest launch", guest.sequence, guest.start, guest.end, current, 0)
    if guest.status != "ok" or not guest.machine or guest.error is not None:
        raise MonitorError("guest launch reading failed")
    guest_bytes = _integer("guest available bytes", guest.available_bytes)
    guest = guest_bytes / (1 << 20)
    guest_age = current - guest_end
    if guest_age < 0 or guest_age > LAUNCH_MAX_AGE_S or guest_bytes < (4096 << 20):
        raise MonitorError("guest launch gate failed or is stale")
    _bracket("host launch", host.sequence, host.start, host.end, current, 0)
    if host.status != "ok" or not host.machine or host.error is not None:
        raise MonitorError("host launch reading failed")
    available = _integer("host available bytes", host.available_bytes)
    total = _integer("host total bytes", host.total_bytes, minimum=1)
    required = int((policy.tree_cap_mib + 1024) * (1 << 20))
    age = current - host.end
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
    seen: set[tuple[int, int]] = set()
    rss = 0
    for member in reading.members:
        pid = _integer("member pid", member.pid, minimum=1)
        start_ticks = _integer("member start identity", member.start_ticks, minimum=1)
        if (pid, start_ticks) in seen:
            raise MonitorError("duplicate process identity")
        seen.add((pid, start_ticks))
        if member.state not in {"R", "S", "D", "T", "t", "Z", "X", "I"}:
            raise MonitorError("invalid process state")
        rss += _integer("member RSS bytes", member.rss_bytes)
    rss_mib = rss / (1 << 20)
    root_code = reading.root_returncode
    if not reading.root_alive and (isinstance(root_code, bool) or not isinstance(root_code, int)):
        raise MonitorError("exited root requires integer return code")
    return seq, start, end, rss_mib


def supervise(*, policy: Policy, tree_reader: Callable[[], TreeReading],
              host_poll: Callable[[], HostReading | None], host_request: Callable[[int, float], None],
              clock: Callable[[], float], wait: Callable[[float], None],
              cleanup: Callable[[float], dict], report_sink: Callable[[dict], None] | None = None,
              run_nonce: str = "fixture") -> dict:
    """Supervise already-owned work. Every exit path requests/records cleanup as needed."""
    report = {"schema": SCHEMA_VERSION, "status": "partial", "primary_reasons": [],
              "secondary_errors": [], "tree_samples": 0, "host_samples": 0,
              "peak_tree_rss_mib": 0.0, "maximum_tree_gap_s": 0.0,
              "maximum_host_gap_s": 0.0, "maximum_tree_acquisition_s": 0.0,
              "maximum_host_response_s": 0.0, "maximum_decision_delay_s": 0.0,
              "peak_process_rss_bytes": {}, "returncode": None,
              "membership_complete": False, "cleanup_requested": False,
              "cleanup_confirmed": False, "cleanup_errors": [], "survivors": None,
              "last_tree": None, "last_host": None, "run_nonce": run_nonce,
              "elapsed_seconds": {"setup": 0.0, "run": 0.0, "cleanup": 0.0, "report": 0.0}}
    started = None
    previous_tree_end = None
    previous_host_request = None
    last_host_end = None
    tree_seq = host_seq = 0
    next_tree = next_host = None
    pending_host = False
    cleanup_started_at = None
    last_clock = None

    def read_clock() -> float:
        nonlocal last_clock
        current = _number("clock", clock())
        if last_clock is not None and current < last_clock:
            raise MonitorError("monotonic clock regressed")
        last_clock = current
        return current

    try:
        policy.validate()
        started = read_clock()
        next_tree = started
        next_host = started
        while True:
            now = read_clock()
            if now >= policy.deadline:
                report["primary_reasons"].append("wall_time_limit")
            if pending_host and previous_host_request is not None and \
                    now >= previous_host_request + policy.host_interval_s:
                report["primary_reasons"].append("host_response_timeout")
            if report["primary_reasons"]:
                break
            if now >= next_host and not pending_host:
                host_request(host_seq + 1, now)
                previous_host_request = now
                pending_host = True
                next_host = now + policy.host_interval_s
            response = host_poll()
            if response is not None:
                seq, _hs, he = _bracket("host", response.sequence, response.start,
                                        response.end, read_clock(), host_seq)
                if response.status != "ok" or response.error is not None or not response.machine:
                    raise MonitorError("host provider/API failed")
                available = _integer("host available bytes", response.available_bytes)
                total = _integer("host total bytes", response.total_bytes, minimum=1)
                if available > total or previous_host_request is None or response.start < previous_host_request:
                    raise MonitorError("host response bounds or units invalid")
                response_received = read_clock()
                if response_received >= policy.deadline:
                    report["primary_reasons"].append("wall_time_limit")
                request_deadline = previous_host_request + policy.host_interval_s
                if last_host_end is not None:
                    request_deadline = min(request_deadline, last_host_end + HOST_MAX_GAP_S)
                latency = response_received - previous_host_request
                if latency < 0 or response.end > request_deadline or latency >= policy.host_interval_s:
                    raise MonitorError("host reply exceeded its bounded request deadline")
                report["maximum_host_response_s"] = max(report["maximum_host_response_s"], latency)
                if last_host_end is not None:
                    gap = response.end - last_host_end
                    if gap < 0 or gap > HOST_MAX_GAP_S:
                        raise MonitorError("host acquisition gap exceeded one second")
                    report["maximum_host_gap_s"] = max(report["maximum_host_gap_s"], gap)
                host_seq, last_host_end = seq, he
                pending_host = False
                report["host_samples"] += 1
                report["last_host"] = asdict(response)
                if available / (1 << 20) < policy.host_minimum_mib:
                    report["primary_reasons"].append("host_pressure_limit")
            if report["primary_reasons"]:
                break
            if now >= next_tree and not (pending_host and report["host_samples"] == 0):
                tree = tree_reader()
                captured_now = read_clock()
                seq, _ts, end, rss_mib = _validate_tree(
                    tree, captured_now, tree_seq,
                    previous_tree_end if previous_tree_end is not None else started)
                tree_seq, previous_tree_end = seq, end
                report["tree_samples"] += 1
                report["maximum_tree_acquisition_s"] = max(
                    report["maximum_tree_acquisition_s"], end - _ts)
                report["maximum_decision_delay_s"] = max(
                    report["maximum_decision_delay_s"], captured_now - end)
                report["maximum_tree_gap_s"] = max(
                    report["maximum_tree_gap_s"], end - (started if report["tree_samples"] == 1 else report["last_tree"]["end"]))
                report["peak_tree_rss_mib"] = max(report["peak_tree_rss_mib"], rss_mib)
                for member in tree.members:
                    key = f"{member.pid}@{member.start_ticks}"
                    report["peak_process_rss_bytes"][key] = max(
                        report["peak_process_rss_bytes"].get(key, 0), member.rss_bytes)
                report["membership_complete"] = tree.membership_complete
                report["last_tree"] = {**asdict(tree), "rss_mib": rss_mib}
                if rss_mib > policy.tree_cap_mib:
                    report["primary_reasons"].append("tree_rss_limit")
                if captured_now >= policy.deadline:
                    report["primary_reasons"].append("wall_time_limit")
                if not tree.root_alive:
                    report["returncode"] = tree.root_returncode
                    if tree.members or not tree.membership_complete or tree.root_returncode != 0:
                        report["primary_reasons"].append("abnormal_root_exit_or_remaining_members")
                    elif not report["primary_reasons"]:
                        report["status"] = "completed"
                        report["cleanup_confirmed"] = True
                        break
                next_tree += policy.tree_interval_s
                if next_tree <= captured_now:
                    next_tree = captured_now + policy.tree_interval_s
                now = captured_now
            if report["primary_reasons"]:
                break
            scheduled_tree = next_tree
            if pending_host and report["host_samples"] == 0:
                scheduled_tree = max(next_tree, now + policy.tree_interval_s)
            target = min(scheduled_tree, next_host, policy.deadline,
                         previous_host_request + policy.host_interval_s
                         if pending_host and previous_host_request is not None else policy.deadline)
            delay = target - read_clock()
            if delay > 0:
                wait(delay)
    except BaseException as exc:
        report["primary_reasons"].append("monitor_input_failure")
        report["secondary_errors"].append({"type": type(exc).__name__, "message": str(exc)})

    def safe_time() -> float | None:
        try:
            return read_clock()
        except BaseException as exc:
            report["secondary_errors"].append({"type": type(exc).__name__,
                "message": str(exc), "stage": "clock_during_cleanup_or_reporting"})
            return last_clock

    if report["primary_reasons"]:
        report["status"] = "stopped_partial"
        report["cleanup_requested"] = True
        cleanup_started_at = safe_time()
        if started is not None and cleanup_started_at is not None:
            report["elapsed_seconds"]["run"] = max(0.0, cleanup_started_at - started)
        try:
            cleanup_result = cleanup(policy.cleanup_limit_s)
            if not isinstance(cleanup_result, dict):
                raise MonitorError("cleanup result must be an object")
            report["cleanup_confirmed"] = cleanup_result.get("confirmed") is True
            report["survivors"] = cleanup_result.get("survivors")
            report["cleanup_errors"].extend(cleanup_result.get("errors", []))
        except BaseException as exc:
            report["cleanup_errors"].append({"type": type(exc).__name__, "message": str(exc)})
            report["cleanup_confirmed"] = False
        cleanup_ended_at = safe_time()
        if cleanup_started_at is not None and cleanup_ended_at is not None:
            report["elapsed_seconds"]["cleanup"] = max(0.0, cleanup_ended_at - cleanup_started_at)
    elif started is not None:
        run_ended_at = safe_time()
        if run_ended_at is not None:
            report["elapsed_seconds"]["run"] = max(0.0, run_ended_at - started)
    report_started_at = safe_time()
    try:
        finite_json(report)
        if report_sink is not None:
            report_sink(report)
    except BaseException as exc:
        report["secondary_errors"].append({"type": type(exc).__name__, "message": str(exc),
                                          "stage": "reporting"})
        report["status"] = "partial_report_failure"
    report_ended_at = safe_time()
    if report_started_at is not None and report_ended_at is not None:
        report["elapsed_seconds"]["report"] = max(0.0, report_ended_at - report_started_at)
    if started is not None and report_ended_at is not None:
        report["elapsed_seconds"]["total"] = max(0.0, report_ended_at - started)
    finite_json(report)
    return report
