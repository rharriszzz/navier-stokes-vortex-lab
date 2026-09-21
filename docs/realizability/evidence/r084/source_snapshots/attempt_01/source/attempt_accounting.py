"""Strict all-attempt accounting for a single bounded R084 fixture run."""
from __future__ import annotations

import math


def prior_elapsed(attempts: list[dict], *, limit_seconds: float = 120.0,
                  address_space_limit_bytes: int = 256 * 1024 * 1024) -> float:
    if not isinstance(attempts, list):
        raise ValueError("attempt inventory must be a list")
    elapsed_total = 0.0
    for expected, row in enumerate(attempts, 1):
        if not isinstance(row, dict) or type(row.get("attempt")) is not int or row["attempt"] != expected:
            raise ValueError("attempt sequence is incomplete or duplicated")
        if row.get("state") != "COMPLETED":
            raise ValueError("open attempt; no retry")
        elapsed = row.get("outer_elapsed_seconds")
        rss = row.get("child_lifetime_peak_rss_bytes")
        before, after, archived = (row.get(key) for key in
            ("source_sha256_before", "source_sha256_after", "source_archive_sha256"))
        intervals = row.get("timing_intervals_seconds")
        if (row.get("status") != "passed" or row.get("timed_out") is not False or
                row.get("resource_stop") is not False or row.get("validator_returncode") != 0):
            raise ValueError("failed, timed out or resource-stopped attempt; no retry")
        if (type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0 or
                type(rss) is not int or rss < 0 or rss > address_space_limit_bytes):
            raise ValueError("unknown duration or resource evidence")
        if (not isinstance(before, dict) or not before or before != after or
                not isinstance(archived, dict) or archived != before):
            raise ValueError("source bodies/hashes are incomplete or changed during attempt")
        if any(type(value) is not str or len(value) != 64 or
               any(char not in "0123456789abcdef" for char in value)
               for value in before.values()):
            raise ValueError("source SHA-256 inventory is malformed")
        if (not isinstance(intervals, dict) or set(intervals) !=
                {"setup_and_snapshot", "validator_child", "finalization"} or
                any(type(value) not in (int, float) or not math.isfinite(value) or value < 0
                    for value in intervals.values()) or
                sum(intervals.values()) > elapsed + 1e-9):
            raise ValueError("attempt timing intervals are incomplete or inconsistent")
        if not isinstance(row.get("uncovered_measurement_scope"), list):
            raise ValueError("measurement exclusions must be explicit")
        elapsed_total += elapsed
    if not math.isfinite(elapsed_total) or elapsed_total > limit_seconds:
        raise ValueError("cumulative wall allowance exhausted")
    return elapsed_total
