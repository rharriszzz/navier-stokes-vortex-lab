"""Injectable Linux /proc and delegated-membership decoding helpers.

No filesystem, cgroup write, signal or process is touched by importing this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from monitor_core import MonitorError, ProcessMember


@dataclass(frozen=True)
class ProcStat:
    pid: int
    comm: str
    state: str
    ppid: int
    pgrp: int
    session: int
    start_ticks: int
    rss_pages: int


def parse_proc_stat(expected_pid: int, text: str) -> ProcStat:
    """Parse /proc/PID/stat using the final ')' so comm may contain ')' or spaces."""
    if isinstance(expected_pid, bool) or not isinstance(expected_pid, int) or expected_pid <= 0:
        raise MonitorError("PID must be a positive integer")
    if not isinstance(text, str):
        raise MonitorError("stat text must be a string")
    left = text.find(" (")
    right = text.rfind(")")
    if left <= 0 or right <= left + 1:
        raise MonitorError("malformed proc stat command field")
    try:
        pid = int(text[:left])
        fields = text[right + 1:].split()
        # fields begins at kernel stat field 3 (state).
        state = fields[0]
        ppid, pgrp, session = (int(fields[i]) for i in (1, 2, 3))
        start_ticks = int(fields[19])
        rss_pages = int(fields[21])
    except (ValueError, IndexError) as exc:
        raise MonitorError("malformed proc stat numeric fields") from exc
    if pid != expected_pid or state not in {"R", "S", "D", "T", "t", "Z", "X", "I"}:
        raise MonitorError("PID identity or process state invalid")
    if min(ppid, pgrp, session, start_ticks, rss_pages) < 0 or start_ticks == 0:
        raise MonitorError("negative or missing proc identity/RSS")
    return ProcStat(pid, text[left + 2:right], state, ppid, pgrp, session,
                    start_ticks, rss_pages)


def make_membership_reading(*, cgroup_pids: set[int], proc_text: dict[int, str],
                            root: tuple[int, int], page_size: int) -> tuple[ProcessMember, ...]:
    """Convert a complete injected cgroup-v2 PID inventory into identity/RSS records.

    Caller must recheck cgroup membership around reads on a live host. This pure
    helper rejects disappearance/mismatch rather than treating it as zero RSS.
    """
    if not isinstance(cgroup_pids, set) or any(
            isinstance(pid, bool) or not isinstance(pid, int) or pid <= 0 for pid in cgroup_pids):
        raise MonitorError("cgroup PID inventory invalid")
    if isinstance(page_size, bool) or not isinstance(page_size, int) or page_size <= 0:
        raise MonitorError("page size invalid")
    if set(proc_text) != cgroup_pids:
        raise MonitorError("proc/cgroup membership inventory differs")
    members = []
    identities = set()
    for pid in sorted(cgroup_pids):
        stat = parse_proc_stat(pid, proc_text[pid])
        identity = (pid, stat.start_ticks)
        if identity in identities:
            raise MonitorError("duplicate process identity")
        identities.add(identity)
        members.append(ProcessMember(pid, stat.start_ticks, stat.state,
                                     stat.rss_pages * page_size))
    # Root identity is checked at launch; a reaped root may be absent later.
    return tuple(members)


def verify_launch_root(*, root: tuple[int, int], members: tuple[ProcessMember, ...]) -> None:
    if (not isinstance(root, tuple) or len(root) != 2 or
            any(type(part) is not int or part <= 0 for part in root) or
            not any((member.pid, member.start_ticks) == root for member in members)):
        raise MonitorError("launch root identity is absent from initial membership")


def classify_cleanup(*, kill_error: str | None, child_reaped: bool,
                     cgroup_populated: bool | None, survivors: list[tuple[int, int]] | None) -> dict:
    """Pure cleanup result classification; operations and verification are injected."""
    if kill_error is not None and (not isinstance(kill_error, str) or not kill_error):
        return {"confirmed": False, "status": "cleanup_unknown", "errors": ["invalid kill error"],
                "survivors": None}
    if type(child_reaped) is not bool:
        return {"confirmed": False, "status": "cleanup_unknown", "errors": ["invalid reaping flag"],
                "survivors": None}
    if cgroup_populated is not None and type(cgroup_populated) is not bool:
        return {"confirmed": False, "status": "cleanup_unknown", "errors": ["invalid populated flag"],
                "survivors": None}
    if survivors is not None and (not isinstance(survivors, list) or any(
            not isinstance(item, tuple) or len(item) != 2 or
            any(type(part) is not int or part <= 0 for part in item) for item in survivors)):
        return {"confirmed": False, "status": "cleanup_unknown", "errors": ["invalid survivor inventory"],
                "survivors": None}
    if kill_error is not None:
        return {"confirmed": False, "status": "cleanup_failed", "errors": [kill_error],
                "survivors": survivors}
    if cgroup_populated is None or not child_reaped or survivors is None:
        return {"confirmed": False, "status": "cleanup_unknown", "errors": [],
                "survivors": survivors}
    if cgroup_populated or survivors:
        return {"confirmed": False, "status": "cleanup_failed", "errors": [],
                "survivors": survivors}
    return {"confirmed": True, "status": "cleanup_confirmed", "errors": [],
            "survivors": []}
