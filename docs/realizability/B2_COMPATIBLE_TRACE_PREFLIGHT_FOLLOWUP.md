# R033 compatible-trace prerequisite and observer completion

Recorded 2026-09-20 for the repository's short **Continue** request, using
the R022/R021 preserved contract. The [evidence index](B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md)
still explains the earlier R022 memory stop; this document records its bounded
follow-up. Exact R033 sources, four attempts, reports, resource snapshots and
cache accounting are under [`evidence/r033`](evidence/r033/).

## Result

The full prerequisite suite passed in attempt 4. All five original fixture
phases, the wrong-root refusal, actual parent refusal, synthetic time/RSS
watchdogs, 16 high-order facet checks, metadata/offset/lifting refusals, and
the actual pinned harmonic observer acceptance/refusal cases passed. The
cumulative task time was **56.2513 s** against the selected **600 s** limit.
No physical child, mesh, factorization, matrix solve or PDE solve ran.

The capacity check before the first launch showed approximately 2.66 GiB free
on Windows and 6.94 GiB available inside WSL. The 600 s wall allowance was
retained and the active child-tree cap was sized down from 2048 to **1536 MiB**
to leave roughly 1 GiB of host-reported headroom. Capacity was rechecked before
later attempts; Windows availability rose to 6.29 GiB and WSL availability was
about 6.77 GiB before the final pass. These are distinct views of shared
physical memory and are not additive. The selected cap remained unchanged.

Across all attempts, the maximum sampled active child-tree RSS was **571.42
MiB** during form compilation, with `cc1` at 405.75 MiB and Python at 163.24
MiB. The final cache-reuse pass peaked at 171.24 MiB. Parent totals are sampled
tree RSS; each child report separately records that process's own high-water
RSS. The successful final report retains 118 stage checkpoints, including
before and after reference-mesh construction, harmonic form compilation,
oracle matrix/load assembly, and each observer case.

The two complex polynomial traces passed at q=64 and q=96 on all four faces:
four trace/order cases and 16 facet projection/weak-load checks. All nine
independent full block-oracle comparisons passed within the recorded
`256*eps` absolute-contribution thresholds. Pressure lifting was nonzero where
expected, essential values were exact, and target batches stayed at or below
256 points.

For the actual harmonic path, compatible P, A_64 and A_96 passed the full
lifting oracle and reached the pre-KSP sentinel. The incompatible P, first-A
and second-A injections each refused at the declared compatibility boundary,
and each refused raw vector remained unchanged. The pre-solve observer ran
once for each of the four cases. Block layout and matrix digest/state remained
consistent; both pressure nullspaces passed right- and transpose-nullspace
checks. Every case recorded zero factorization and solve events. Missing block
metadata, wrong offsets and synthetic lifting failure retained their expected
refusal coverage.

## Attempts and cache handling

All four attempts and their exact source copies are preserved. Attempt 1
stopped before form compilation because the default global FFCx cache contained
a C file without its compiled module. Attempt 2 used a new isolated cache and
compiled the forms; the observer exposed a PETSc read-only vector access bug in
the disposable check. The check was corrected to use the read-only array
accessor. Attempt 3 then passed all fixtures, but the final report overwrote
intermediate checkpoint history. Attempt 4 persisted the full checkpoint
sequence and passed while reusing the cache compiled during attempt 3.

No cache was prewarmed outside the measured task, no global cache file was
changed, and the solver/compiler options, production code, traces, quadrature
orders and acceptance thresholds were preserved. The understood fixture fixes
are included only in the archived disposable R033 runner. No production source
or configuration changed.

Run the saved-data audit from the repository root with:

```bash
python docs/realizability/evidence/r033/audit.py
```

The recorded audit passed and confirms the 19 pinned production identities,
attempt/source hashes, prerequisite coverage, observer assertions, zero
physical counts, resource limits and checkpoint stages. See
[`validation.json`](evidence/r033/validation.json),
[`resources.json`](evidence/r033/resources.json) and
[`cache_metadata.json`](evidence/r033/cache_metadata.json).

## Scientific boundary and next task

This pass validates only prerequisite fixtures and the disposable pre-solve
observer. It does not evaluate a physical 128-term trace, measure assembled
physical flux compatibility, factor a physical matrix, establish an A_64/A_96
response, validate the Stokes result, or change `campaign_ready=false`. R020
remains the latest physical attempt and the B2 physical accuracy gate remains
failed.

Recommend **GPT-6 Astra with high reasoning** for the next bounded task: review
the R033 observer implementation and evidence against the unchanged R021/R013
contract, then inspect the remaining physical runner's refusal, count,
resource and output gates. State whether the recorded prerequisites support a
separately scoped conditional R021 physical comparison, identify any required
changes or unresolved choices, and stop before launching it. Do not change the
trace, quadrature, solver, accuracy thresholds, physical method or gates during
the review. If the review finds only a clearly understood mechanical defect,
recommend GPT-5.6 Luna/medium for that narrow repair; retain Astra/high for any
unexplained numerical behavior or scientific/method decision. Model availability
was rechecked in the current session catalog; no switch occurred.

**Next prompt: Continue.**
