# R073 portable monitor contract

`portable_monitor.py` defines a small, platform-neutral policy loop. It does
not launch, inspect, or terminate operating-system processes. Platform adapters
must supply monotonic timestamps, aggregate process-tree RSS, host available
physical memory, root liveness, and a callback that terminates the full tree.
The validation suite supplies only fake readers and a fake termination callback.

## Policy represented

- Before launch, require a finite, nonnegative host reading no more than 30 s
  old and at least the selected child-tree RSS cap plus 1024 MiB available.
- Request process-tree readings on the nominal 50 ms cadence. Record the
  maximum observed sample gap; do not hide delayed samples in an average.
- Request host-pressure readings at least once per second. Fail closed if a
  reading is missing, nonfinite, stale, future-dated, or more than one second
  after its predecessor (with a 1 ns floating-point comparison allowance).
- During execution, request tree termination when aggregate RSS exceeds its
  selected cap, the deadline is reached, host availability falls below
  1024 MiB, or a required input fails. Preserve the latest reading and partial
  counts in the returned report.
- A normal child exit is complete only when the adapter reports the root dead.

The 180 s / 1536 MiB physical limits in the existing review are unchanged.
This contract does not choose or implement a Windows memory API, Linux `/proc`
adapter, process-group/job-object termination mechanism, sampling thread, or
real clock. The archived R033 Linux `/proc` implementation remains unchanged.
Synthetic validation establishes policy-loop behavior only; it does not
validate live Linux sampling, Windows host-memory semantics, process-tree
coverage, actual termination, sampling latency under load, or a physical run.
Those platform adapters require separate host-specific validation before a
physical launch.
