"""Pure fail-closed validation for the cumulative R082 attempt ledger."""
from __future__ import annotations

import math


def prior_elapsed(attempts: list[dict], *, limit_seconds: float = 120.0,
                  address_space_limit_bytes: int = 256 * 1024 * 1024,
                  reconciliations: list[dict] | None = None) -> float:
    if not isinstance(attempts, list):
        raise ValueError("attempt inventory must be a list")
    reconciled = {}
    for event in reconciliations or []:
        number = event.get("attempt")
        if (type(number) is not int or number in reconciled or
                event.get("classification") != "resolved_fixture_assertion" or
                event.get("resource_stop") is not False or
                event.get("retry_authorized_within_existing_budget") is not True or
                not isinstance(event.get("reason"), str) or not event["reason"] or
                not isinstance(event.get("source_sha256"), dict) or not event["source_sha256"]):
            raise ValueError("invalid attempt reconciliation")
        reconciled[number] = event
    elapsed_total = 0.0
    for expected, row in enumerate(attempts, 1):
        if not isinstance(row, dict) or row.get("attempt") != expected:
            raise ValueError("attempt sequence is incomplete or duplicated")
        if row.get("state") != "COMPLETED":
            raise ValueError("open attempt; no retry")
        elapsed = row.get("outer_elapsed_seconds")
        rss = row.get("child_lifetime_peak_rss_bytes")
        if (type(elapsed) not in (int, float) or not math.isfinite(elapsed) or elapsed < 0 or
                type(rss) is not int or rss < 0 or rss > address_space_limit_bytes or
                row.get("timed_out") is not False or
                row.get("resource_stop") is not None):
            raise ValueError("unknown duration or failed resource/validator evidence; no retry")
        if row.get("status") == "passed":
            if row.get("validator_returncode") != 0:
                raise ValueError("passed attempt has a failed return code")
        elif row.get("status") == "failed":
            event = reconciled.get(expected)
            stderr = row.get("stderr", "")
            if (event is None or row.get("validator_returncode") == 0 or
                    not isinstance(stderr, str) or "AssertionError" not in stderr or
                    event.get("source_sha256") != row.get("source_sha256_after")):
                raise ValueError("failed or unexplained attempt; no retry")
        else:
            raise ValueError("unknown attempt status; no retry")
        elapsed_total += elapsed
    if not math.isfinite(elapsed_total) or elapsed_total > limit_seconds:
        raise ValueError("cumulative wall allowance exhausted")
    return elapsed_total
