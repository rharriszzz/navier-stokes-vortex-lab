"""Portable resource-monitor contract with injected process and host readers.

This module deliberately does not launch a child. Platform adapters supply
process-tree and host-pressure readings; tests use only synthetic records.
"""
from dataclasses import dataclass
import math

POLL_SECONDS = 0.05
HOST_POLL_SECONDS = 1.0
MINIMUM_HOST_AVAILABLE_MIB = 1024.0
LAUNCH_SAMPLE_MAX_AGE_SECONDS = 30.0


@dataclass(frozen=True)
class TreeReading:
    timestamp: float
    rss_mib: float
    process_count: int
    root_alive: bool


@dataclass(frozen=True)
class HostReading:
    timestamp: float
    available_mib: float


class MonitorInputError(ValueError):
    pass


def _finite_nonnegative(label, value):
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise MonitorInputError(f"{label} must be finite and nonnegative")


def validate_launch_reading(reading, now, child_tree_cap_mib):
    """Enforce the R067 prelaunch host-headroom rule on one fresh reading."""
    if reading is None:
        raise MonitorInputError("missing launch host reading")
    _finite_nonnegative("launch host availability", reading.available_mib)
    _finite_nonnegative("launch host timestamp", reading.timestamp)
    age = now - reading.timestamp
    if not math.isfinite(age) or age < 0 or age > LAUNCH_SAMPLE_MAX_AGE_SECONDS:
        raise MonitorInputError("stale or future launch host reading")
    if reading.available_mib < child_tree_cap_mib + 1024.0:
        raise MonitorInputError("insufficient launch host headroom")
    return {"age_seconds": age, "available_mib": reading.available_mib,
            "required_mib": child_tree_cap_mib + 1024.0}


def run_monitor(*, tree_reader, host_reader, now, deadline, tree_cap_mib,
                launch_host_reading, terminate, poll_seconds=POLL_SECONDS,
                host_poll_seconds=HOST_POLL_SECONDS):
    """Consume readings until child exit or a fail-closed stop condition.

    `tree_reader` and `host_reader` are zero-argument callables. `now` is an
    injected monotonic clock. `terminate` is a callback for the platform adapter
    to stop the process tree; this function never signals a real process itself.
    """
    _finite_nonnegative("tree cap", tree_cap_mib)
    _finite_nonnegative("poll interval", poll_seconds)
    _finite_nonnegative("host poll interval", host_poll_seconds)
    started = now()
    validate_launch_reading(launch_host_reading, started, tree_cap_mib)
    previous_tree_time = started
    next_host_time = started
    last_host = launch_host_reading
    max_tree_gap = 0.0
    max_host_gap = 0.0
    tree_samples = 0
    host_samples = 0
    peak_rss = 0.0
    largest_process_count = 0
    stop_reason = None
    last_tree = None
    try:
        while True:
            current = now()
            if not math.isfinite(current) or current < previous_tree_time:
                raise MonitorInputError("nonmonotonic monitor clock")
            if current >= next_host_time:
                observed = host_reader()
                if observed is None:
                    raise MonitorInputError("missing runtime host reading")
                _finite_nonnegative("host availability", observed.available_mib)
                _finite_nonnegative("host timestamp", observed.timestamp)
                age = current - observed.timestamp
                if not math.isfinite(age) or age < 0 or age > host_poll_seconds:
                    raise MonitorInputError("stale or future runtime host reading")
                if observed.timestamp - last_host.timestamp > host_poll_seconds + 1e-9:
                    raise MonitorInputError("runtime host sampling gap exceeded one second")
                max_host_gap = max(max_host_gap, observed.timestamp - last_host.timestamp)
                last_host = observed
                host_samples += 1
                next_host_time = current + host_poll_seconds
                if observed.available_mib < MINIMUM_HOST_AVAILABLE_MIB:
                    stop_reason = "host_pressure_limit"

            reading = tree_reader()
            if reading is None:
                raise MonitorInputError("missing process-tree reading")
            _finite_nonnegative("tree rss", reading.rss_mib)
            _finite_nonnegative("tree timestamp", reading.timestamp)
            if not isinstance(reading.process_count, int) or reading.process_count < 0:
                raise MonitorInputError("invalid process count")
            tree_gap = reading.timestamp - previous_tree_time
            if not math.isfinite(tree_gap) or tree_gap < 0:
                raise MonitorInputError("nonmonotonic process-tree timestamp")
            max_tree_gap = max(max_tree_gap, tree_gap)
            # The adapter captures its timestamp after this loop's clock read;
            # allow bounded read latency while still rejecting old samples.
            if reading.timestamp - current > host_poll_seconds or current - reading.timestamp > poll_seconds:
                raise MonitorInputError("stale or future process-tree reading")
            previous_tree_time = reading.timestamp
            last_tree = reading
            tree_samples += 1
            peak_rss = max(peak_rss, reading.rss_mib)
            largest_process_count = max(largest_process_count, reading.process_count)

            if stop_reason is None and reading.rss_mib > tree_cap_mib:
                stop_reason = "tree_rss_limit"
            if stop_reason is None and now() >= deadline:
                stop_reason = "wall_time_limit"
            if stop_reason is not None:
                terminate()
                break
            if not reading.root_alive:
                break
    except BaseException as error:
        # A launched process is assumed live when its state cannot be read;
        # failing closed must still ask the platform adapter to stop it.
        terminate()
        return {
            "status": "partial", "stop_reason": "monitor_input_failure",
            "error_type": type(error).__name__, "error": str(error),
            "tree_samples": tree_samples, "host_samples": host_samples,
            "maximum_tree_sample_gap_seconds": max_tree_gap,
            "maximum_host_sample_gap_seconds": max_host_gap,
            "peak_tree_rss_mib": peak_rss,
            "largest_process_count": largest_process_count,
            "last_tree_reading": last_tree.__dict__ if last_tree else None,
            "termination_requested": True,
        }
    return {
        "status": "stopped" if stop_reason else "completed",
        "stop_reason": stop_reason, "tree_samples": tree_samples,
        "host_samples": host_samples,
        "maximum_tree_sample_gap_seconds": max_tree_gap,
        "maximum_host_sample_gap_seconds": max_host_gap,
        "peak_tree_rss_mib": peak_rss,
        "largest_process_count": largest_process_count,
        "last_tree_reading": last_tree.__dict__ if last_tree else None,
        "termination_requested": bool(stop_reason),
    }
