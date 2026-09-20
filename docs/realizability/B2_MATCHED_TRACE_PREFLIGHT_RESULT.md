# R018 matched-trace prerequisites: stop before physical execution

Recorded 2026-09-20 for [R018](../../REQUEST_LOG.md#r018--2026-09-20--short-continuation-request)
against `bd4945b`, under the [R013 contract](B2_MATCHED_TRACE_REVIEW.md#one-executable-next-task-contract)
and the [R017 review handoff](B2_BLOCK_RHS_TOY_REPAIR_RESULT.md#limits-and-next-task).
The [evidence index](B2_MATCHED_TRACE_PREFLIGHT_EVIDENCE.md) links the exact
code, prerequisite records, traceback and stored-data audit.

## Outcome

**No physical child was launched.** The fresh prerequisite sequence passed its
synthetic watchdog and kernel checks, then stopped on a path assumption in the
wrapper toy. Copying the exact R017 files into `/tmp/navier-b2-matched-r018/`
made `wrapper_toys.py:22` fail at
`repository_root = Path(__file__).resolve().parents[4]` with `IndexError: 4`.
That file has only three parents in the disposable directory. In the repository
archive, the same expression resolves to the repository root.

R018's preparation overlooked this dependency on the script's location. The
failure is a launch-context defect; it does not invalidate the recorded R017
toy arithmetic. Root discovery occurs after FEM imports but before construction
of the report, its first checkpoint, and the exception handler. Consequently
there is no wrapper child JSON. The parent retained its nonzero return code,
traceback, finite aggregate report and watchdog record. The failed wrapper did
not reach source verification, tetrahedron creation or its numerical assertions.

The handoff requires stopping before physical execution if any prerequisite
fails. No path patch, toy retry or physical launch followed. There were zero
physical meshes, PDE solves, factorizations and matrix solves. The paired
experiment remains incomplete; the physical B2 gate remains failed and
`campaign_ready=false`.

## Review and completed checks

The standard-library preflight byte-compared **266 prior evidence files**
with the starting commit and verified **all 19 production identities**.
The R016 and R017 stored-data auditors were re-executed with their writes
redirected to the new work directory, preserving the historical files and
manifests. R016's P measurements and R017's toy repair evidence still pass their
stored-data checks. Six child/support sources were copied byte for byte from
R017, including the repaired physical runner.

Static review covered A constraint grouping, block layout, loading and lifting,
pressure compatibility, essential assignment, primary/correction inventory,
matrix/factor invariance, own-target diagnostics, output arithmetic, component
screens and stop behavior. Those observations are in
[preflight.json](evidence/r018/preflight.json). Its `status=passed` refers to
that review and source checks, with fresh toys explicitly pending; it is not a
claim that all launch prerequisites passed. In particular, A's physical
pressure compatibility remains unmeasured. Passing its earlier closed-flux
ratios does not imply passing `256*eps*norm(b)` after lifting.

| Fresh phase | Result | Wall time | Observed child-tree peak RSS |
|---|---|---:|---:|
| Synthetic watchdog | Wall stop and two-process RSS stop behaved as required | 0.2786 s | 70.99 MiB |
| Kernel toys | Passed 24 vertex permutations, spanning P2 vector loads, circle moments, arc checks, jumps and tangencies | 4.0754 s | 141.57 MiB |
| Wrapper toys | Failed during repository-root discovery | 0.4482 s | 129.51 MiB |
| Block RHS and extra disk toys | Not launched after refusal | — | — |

Cumulative parent-monitored time was **4.8031 s**, including the failed child
and parent overhead, below 60 s. Maximum observed child-tree RSS was
**141.5703 MiB**, below 512 MiB; maximum sample gap was 0.057983 s at nominal
0.05 s sampling. The kernel child recorded 141.3203 MiB process high-water RSS;
the wrapper produced no high-water report. Sampling is not an instantaneous
memory bound. Execution used the approved MPI environment, serial and with
single-thread numerical libraries; no sandbox MPI failure occurred this time.

No new P or A field, physical pressure-compatibility record, accuracy comparison
or boundary-sensitivity result exists. R016 remains the latest P-only physical
diagnostic, and R012 remains the last complete physical response audit. Their
failed physical comparison is unchanged. Full application, dense/calibration/
refinement suites, production changes, gate integration, campaign, B3, rendering
and encoding were skipped. Physical preparation, sensing, force/power, pressure
demand and validated movie flow remain unresolved.

## Next bounded task: make toy prerequisites portable

Recommend **GPT-5.6 Luna, medium reasoning** for this mechanical repair only.

1. Preserve R014–R018 evidence and production identities. Use a new disposable
   copy of the R017/R018 sources. Replace the wrapper toy's fixed ancestor
   index with the documented repository-root working directory (`Path.cwd()`),
   checked against the pinned source identities. The other runner entry points
   already require execution from the repository root. Do not change scientific
   forms, traces, parameters, tolerances or the physical runner's numerical path.
2. Put repository-root validation inside the reporting/exception boundary so
   a wrong working directory leaves finite stage/error/count JSON before refusal.
   Check source/root assumptions in every child used by the parent, including
   output-directory and sibling-import handling. Check the parent's refusal
   path without invoking a physical child.
3. Under one cumulative **60 s/512 MiB** toy budget, including failed attempts
   and imports, run the full five-phase prerequisite sequence from the repository
   root with scripts in a shallow temporary directory. Confirm correct-root
   success and intentional wrong-root refusal with a saved report. Keep the
   watchdog, 24-permutation/load/disk fixtures, grouping/compatibility/reporting
   fixtures, full block RHS oracle and extra disk checks. Use the approved MPI
   environment. No physical cylinder, PDE solve or factorization is permitted.
4. Archive exact sources, finite success/refusal records, resource totals and
   source identities; audit evidence and documentation, update continuity,
   commit/push under the next Continue, then stop. This task completes when the
   actual disposable invocation works and early failures report correctly, or
   stops on a resource limit, unexplained numerical result or scientific choice.

An alternative is to execute toys from a new archive-depth repository directory,
which satisfies the old assumption. Prefer explicit root handling because it
also supports the required disposable invocation and explains invalid launches.
Neither choice changes the scientific contract. After passing, recommend
**GPT-6 Astra, high reasoning** for review and at most one separately scoped
R013 physical attempt under its original caps. Keep Luna/medium only for an
understood mechanical defect; use Astra/high for method, tolerance or scientific
interpretation decisions. Do not automatically run the physical case after a
toy repair.

Both models are listed in the current session catalog. OpenAI Docs confirms
[Luna's medium effort](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
and [Astra's high effort and research role](https://developers.openai.com/api/docs/models/gpt-6-astra).
No model switch, delegation or automation occurred. **Next prompt: Continue.**
