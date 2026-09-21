# R076 fixture-only monitor implementation

R076 implements the versioned monitor policy and validation interfaces
specified in [R074](../../B2_MONITOR_ADAPTER_REVIEW.md). The runnable source
bundle is in [`source/`](source/); it contains byte-preserved R073 sources,
reports and ledger, the original R070 bundle, and a separate R070 validation copy. The R070 copy
keeps physical execution hard-disabled and uses a separate test-sentinel
entry point.

## Implemented surfaces

- `monitor_core.py` validates finite policy and reading values, independent
  guest/Windows launch gates, sequenced acquisition brackets, explicit
  deadline-based waits, 50 ms tree polling, 0.5 s host requests, response
  timeouts, 1 s host freshness, sampled aggregate/per-process RSS, process
  completion, primary and secondary failures, cleanup results, partial
  reports and finite JSON. OS effects are injected callables.
- `linux_adapter.py` parses `/proc/PID/stat` around the final closing
  parenthesis, binds PIDs to start-time identities, converts RSS pages using
  an injected page size and classifies confirmed, failed or unknown cleanup.
  It performs no `/proc` read, cgroup operation or signal.
- `host_protocol.py` validates one outstanding bounded JSON-line request,
  sequence and nonce matching, reply framing/size, physical-byte units,
  request/receipt timing and API failures. It does not launch or connect to a
  Windows helper.
- `r070_copy/launch_guard.py` verifies the source manifest, binds the child
  report digest into the monitor report, and requires successful monitor
  status, exact integer return code zero, complete membership, confirmed
  cleanup, complete child evidence and scientific checks before completion. Its guarded
  launch refuses regardless of the `enabled` argument; test sentinels cannot
  claim the real attempt record. The integration copy has its own updated
  source manifest; the archived R070 manifest remains byte-preserved.

## Validation and limits

[`attempt_ledger.json`](attempt_ledger.json) preserves every attempt, including
the diagnosed initial failures. The final run passed 16 fixture and continuity
groups. Exact cumulative subprocess time and maximum child-process lifetime
high-water RSS are recorded in [`result.json`](result.json); the run remained
within the 120 s / 256 MiB limits, including Python startup/imports and
validator result reporting. The later ledger entries capture commands directly;
earlier invocation details are append-only reconciliations from the observed
exec calls, without rewriting the original attempt records. Per-attempt source
hashes and manifest bindings are recorded in the ledger and
[`source_manifest.json`](source_manifest.json).

These results validate deterministic fixtures only. No real process, cgroup,
signal, Windows API/helper, native process handle, workload, FEM/MPI/JIT,
physical attempt, render or encoder ran. The adapters do not certify live
containment, permissions, latency, watchdog independence or cleanup. The
180 s / 1536 MiB physical limits remain unchanged and R070 still defaults to
deny. This bundle is not ready for physical execution.
