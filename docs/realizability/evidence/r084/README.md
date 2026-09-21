# R084 fixture-only monitor repair

R084 implements the G01–G07 repairs in a new copy under `source/`. The R082
archive and its three attempts are unchanged. The copied legacy recorder is
inert, and the copied R070 physical CLI/API stays hard-disabled. Validation
uses deterministic fixtures, saved text evidence and injected callbacks only.

The one-shot recorder is [`run_r084.py`](run_r084.py). It binds and snapshots
the complete executable/input tree before starting the child, records exclusive
attempt and checkpoint states, applies the 120 s cumulative reservation and
256 MiB child address-space / 10 s CPU limits, caps each output stream, charges
a conservative five-second persistence reserve, and refuses open, unknown or
resource-stopped history. A non-resource fixture assertion is reusable only
after its failed and corrected source hashes are explicitly reconciled within
the same cumulative allowance. The validator test registry asserts every
`test_*` function runs exactly once. Source bodies are retained under
[`source_snapshots`](source_snapshots/attempt_03/) with before/archive/after
hash maps in the attempt record.

The fixture bundle covers incomplete membership and provider freshness, exact
cleanup deadline behavior, absolute 50 ms phase retention, strict nested zero
counts and report schemas, terminal bounded incremental host framing, owner
state transitions and independent workload/helper cleanup, source-binding and
all-attempt consistency. R070 child report hashes are recomputed after semantic
mutations so those cases test content validation rather than stale hashes.

The [attempt ledger](attempt_ledger.json), [reconciliations](reconciliations.json),
[final result](result.json),
[fixture report](fixture_results_attempt_03.json),
[source manifest](source_manifest.json),
[documentation validation](documentation_validation.json) and durable
[checkpoint](checkpoints/latest.json) record the completed run. The attempt
excludes interpreter startup/imports and conservatively charges five seconds
for final persistence without timing that reserve; it does not claim complete
outer-process resource measurement. Attempts 1 and 2 were non-resource fixture
assertions, each preserved at full charge with a source-bound correction before
attempt 3; their tracebacks and partial records remain in the ledger. Total
charged time is 15.690793 s of 120 s and maximum validator lifetime RSS is
30,060,544 B of 268,435,456 B. Attempt 3 passed all 22 registered functions
exactly once.

No native source/build/startup, live OS/cgroup operation, signal, workload,
FEM/MPI/JIT, mesh/solve, render, encode or physical attempt occurred. The
180 s / 1536 MiB physical limits and unused q64/q96 allowance are unchanged.
The result does not validate a live monitor or authorize the separate OS
harness. The next step is Astra/high review of acceptance, ownership and
provenance before that harness is considered.
