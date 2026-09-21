# R082 fixture-only monitor repair evidence

R082 repairs the R081 findings in a new copy of the R076 fixture bundle. The
R076/R070/R073 archives remain unchanged. The copied R070 `physical.py` and
CLI/API remain hard-disabled, and the test sentinel cannot claim an attempt.
All checks use fakes or saved data; no live process/cgroup/signal, native helper,
workload, FEM/MPI/JIT, render, encode, or physical execution ran.

## Implemented repairs

- Immediate refusal for incomplete tree membership; host/guest launch age uses
  the conservative acquisition start; deadlines and host freshness are checked
  after provider work; tree call brackets must be ordered and nonoverlapping.
- Core host responses require a pending request, the expected sequence and
  nonce, a stable provider/machine identity, and validated physical-byte values.
  The JSON-line parser rejects duplicate keys, nonfinite constants, extra fields
  or frames, contradictory API results, wrong identities and oversized input.
- Every normal or failed exit finalizes workload and helper independently.
  Cleanup fields use exact Boolean/schema checks and typed identity inventories;
  inconsistent status, survivors or errors cannot certify completion.
- Reports replace invalid numbers with JSON `null`, bound diagnostic text and
  secondary errors, and support atomic, size-limited file and directory-fsynced
  checkpoints during supervision and cleanup.
- Linux membership allows an already reaped root to be absent while preserving
  a separate initial-root identity check; duplicate PIDs are rejected even if
  start ticks differ.
- The copied R070 acceptance requires schema versions, zero sentinel event
  counts, no primary/secondary errors, exact count keys, source bindings, and
  separately clean workload/helper evidence. Fixed monitor cadence, memory
  floors and cleanup duration cannot be relaxed through `Policy` fields.
- A durable outer recorder creates exclusive attempt files and a lock, saves
  `STARTED`/`COMPLETED` evidence atomically, reserves final persistence time,
  and caps validator address space/CPU. Unknown/open/resource-stopped attempts
  refuse continuation. A known fixture-only assertion can continue only after a
  source-bound explicit reconciliation; its time and failure stay in the ledger.

## Recorded attempts and limits

`attempt_ledger.json` preserves all attempts and the R082 reconciliation.
Attempt 1 passed 17 groups. Attempt 2 failed at the expected-good R070 fixture
because that fixture omitted the now-required cleanup status field; this was
classified as a resolved fixture assertion, with no resource stop. Attempt 3
passed 17 groups after the fixture was corrected. No earlier attempt was
rewritten or removed.

Across all three attempts, validator wall time was 0.194446 s; conservative
outer charge was 45.247480 s of the 120 s cumulative ceiling. The 15 s
finalization reserve is charged per attempt. Maximum child lifetime high-water
RSS was 24,367,104 bytes under the 268,435,456-byte address-space limit. The
exact per-attempt validator source hashes, Python version, stdout/stderr,
resource values and durations are in the ledger. The final outer-runner and
accounting source hashes are in `outer_source_manifest.json`.

| Artifact | Contents |
|---|---|
| [result.json](result.json) | Final status, attempts, aggregate charged time/RSS, hard-disabled and skipped-scope declarations. |
| [attempt_ledger.json](attempt_ledger.json) | Append-preserving all-attempt records and the explicit attempt 2 reconciliation. |
| [fixture_results_attempt_01.json](fixture_results_attempt_01.json) | First passed fixture set. |
| Attempt 2 | No fixture result file was produced; its failure remains in the ledger. |
| [fixture_results_attempt_03.json](fixture_results_attempt_03.json) | Final 19-group pass. |
| [source_manifest.json](source_manifest.json) | Version/hash map for the complete copied monitor, Linux, protocol, R070/R073 input tree. |
| [documentation_validation.json](documentation_validation.json) | Final repository link, archive, request/session, manifest, ledger and whitespace checks. |
| [checkpoints](checkpoints/latest.json) | Durable outer STARTED/COMPLETED checkpoint for the final attempt. |
| [outer_source_manifest.json](outer_source_manifest.json) | Hashes of the final outer recorder/accounting sources; historical attempt-specific outer hashes were not captured. |

The outer source hash limitation is explicit: the ledger binds each validator
source version, but not the changing wrapper/accounting code per attempt. The
current wrapper/accounting hashes are recorded separately. This does not change
the fixture result; Astra's next review should decide whether this provenance
gap needs a repair before any future live suite.

The implementation is fixture coverage only. It does not implement the Linux
delegated-unit guard, native Windows collector/launcher, live containment, or
the frozen ten-case suite. The physical 180 s / 1536 MiB limits, failed B2 gate,
and unused q64/q96 allowance are unchanged. See the
[R081 live-validation contract](../../B2_MONITOR_LIVE_VALIDATION_CONTRACT.md)
for the later harness requirements and prohibitions.
