"""Fixture-only owner state and independent workload/helper finalization seam."""
from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Callable

from monitor_core import MonitorError, _validate_cleanup

STATES = ("RESERVED", "OWNED_HELD", "READY", "RUNNING", "STOPPING", "FINALIZED")


@dataclass
class OwnedRun:
    run_id: str
    workload_identities: tuple[tuple[int, int], ...]
    helper_identities: tuple[tuple[int, int], ...]
    state: str = "RESERVED"
    history: list[str] = field(default_factory=lambda: ["RESERVED"])
    failure_latched: bool = False

    def advance(self, target: str) -> None:
        allowed = {"RESERVED": "OWNED_HELD", "OWNED_HELD": "READY",
                   "READY": "RUNNING", "RUNNING": "STOPPING",
                   "STOPPING": "FINALIZED"}
        if self.failure_latched or allowed.get(self.state) != target:
            self.failure_latched = True
            raise MonitorError("owned run state transition refused")
        self.state = target
        self.history.append(target)


def finalize_owned(run: OwnedRun, *, workload: Callable[[], dict],
                   helper: Callable[[], dict], now: Callable[[], float],
                   deadline_seconds: float = 5.0) -> dict:
    """Attempt each owned domain independently and bind observations to IDs."""
    if run.state not in {"RUNNING", "STOPPING"}:
        run.failure_latched = True
        raise MonitorError("finalization requires an owned run")
    if run.state == "RUNNING":
        run.advance("STOPPING")
    started = now()
    results = {}
    for domain, callback, identities in (
            ("workload", workload, run.workload_identities),
            ("helper", helper, run.helper_identities)):
        before = now()
        observed_identities: tuple[tuple[int, int], ...] = ()
        try:
            value = callback()
            normalized = _validate_cleanup({domain: value,
                "helper" if domain == "workload" else "workload": {
                    "confirmed": False, "status": "cleanup_failed", "survivors": [],
                    "errors": ["unused validation slot"], "identities": [[1, 1]],
                    "requested_actions": ["none"]}})[0 if domain == "workload" else 1]
            observed_identities = tuple(tuple(item) for item in normalized["identities"])
            expected_identities = tuple(tuple(item) for item in identities)
            if observed_identities != expected_identities:
                normalized["confirmed"] = False
                normalized["status"] = "cleanup_failed"
                normalized["errors"] = list(normalized["errors"]) + [
                    "cleanup identities do not match owned identity inventory"]
        except BaseException as exc:
            normalized = {"confirmed": False, "status": "cleanup_failed",
                "survivors": [], "errors": [f"{type(exc).__name__}: {exc}"[:1024]],
                "identities": [list(item) for item in identities],
                "requested_actions": ["finalize", "verify"]}
        ended = now()
        within_deadline = ended - started <= deadline_seconds
        results[domain] = {**normalized,
            "identities": [list(item) for item in identities],
            "observed_identities": [list(item) for item in observed_identities],
            "requested_actions": ["finalize", "verify"],
            "elapsed_seconds": max(0.0, ended - before),
            "deadline_confirmed": within_deadline}
        if not within_deadline:
            results[domain]["confirmed"] = False
            results[domain]["status"] = "cleanup_failed"
            results[domain]["errors"] = list(results[domain]["errors"]) + [
                "shared cleanup deadline exceeded"]
    run.advance("FINALIZED")
    clean = all(item["confirmed"] and item["deadline_confirmed"] for item in results.values())
    if not clean:
        run.failure_latched = True
    return {"schema": 1, "run_id": run.run_id, "state": run.state,
            "history": list(run.history), "cleanup_confirmed": clean,
            "workload": results["workload"], "helper": results["helper"]}
