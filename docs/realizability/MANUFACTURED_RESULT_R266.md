# R266 — One-use balanced manufactured pilot result

2026-09-26 (America/New_York), PC/WSL `daisy`. The clean, published launch
commit was `d5b42eb0433c81c663810ab2858b67f6b4c8c789`.

**INCOMPLETE. The separate R265 allocation is spent 1/1.** The fixed caller
reserved, held and released one worker. The worker exited 0 and saved its
numerical report and linear-system snapshot, but the saved report explicitly
rejects the manufactured diagnostics. The controller, completion, caller and
caller completion all say `INCOMPLETE`. No second numerical launch or alternate
directory occurred. The eight older allocations remain spent.

The first sandboxed invocation stopped at the manager-version query before
reservation, directory creation, worker or numerical import. It exited 1 in
0.080958 seconds of caller-observed time with `sd-bus operation failed: errno 1`.
The fixed directory was absent afterward. The host manager showed only two
previously recorded failed manufactured units and no new task process. The same
published, clean caller then ran with host manager access and consumed the new
allocation. The [preflight record](evidence/r266/preflight.json) and both exact
caller output pairs retain this boundary; the outer shell interval for the
sandbox refusal was not measured.

The [numerical report](evidence/r266/run/numerical.json) records both degree 24
and 26 failing the **angular budget** and its interval form. At degree 24 the
signed angular defect is `-0.005145516124005005` against limit
`0.0003759966274385022`; the interval defect is
`-0.0006431895155006188` against `0.000046999578429812716`.
Degree 26 gives essentially the same defects and limits. Compatibility,
constraint conditioning, target data, quadrature comparison, verified
corrections, and all other per-degree recorded checks pass. The nonlinear
residual history ends at `3.903967951178561e-15`. These are saved discrete
observations, not a validated manufactured solve or evidence for changing a
threshold. The source of the angular mismatch remains unresolved.

| Observation | Saved value |
|---|---|
| Reservation / held / release | Present; source commit and nonce agree |
| Worker / host caller exit | 0 / 1 |
| Worker result / controller / caller | numerical rejected / INCOMPLETE / INCOMPLETE |
| Numerical report / linear system | Both present; 60 scalar diagnostic receipts |
| Host caller observed after save | 17.680936 seconds, below 180-second cap |
| Measured memory peak | 304,533,504 bytes, below 1,536 MiB cap |
| Measured PID peak / resource events | 6 / zero memory.max, OOM, OOM-kill and pids.max events |
| Cleanup | Empty; unknown children false; manager MainPID 0 and ControlGroup empty |
| Recorded worker PID / cgroup | Both absent at saved-data audit |

The resource measurement ends before the final worker handshake/exit; final
save tails and the independent parent wall interval remain unobserved, as in
the admission. The controller's reason is `Refusal: failed or inconsistent
manufactured evidence`. Its refusal follows the fixed numerical gate, despite
the clean worker exit and resource snapshot. No scientific or resource gate was
relaxed. R229's setup resource predicate remains false.

All 15 original run files and four caller outputs were copied byte-for-byte to
[R266 evidence](evidence/r266/), totaling 256,896 bytes. The
[hash inventory](evidence/r266/run_hashes.json) records each SHA-256 and source
path; the [saved-data audit](evidence/r266/audit.json) verifies every copied
byte against its retained `/tmp` original, source/artifact bindings, reservation,
nonce, statuses, limits, cleanup, 97 older raw originals, eight older spent
allocations and saved R246/R253 PASS. Raw `worker.log` and `run.log` are included
explicitly in Git. The original run directory remains
`/tmp/navier-manufactured-r265-once` and is spent.

**Next:** GPT-6 Astra/high reviews the saved angular terms, exact reference
and discrete source without a new numerical import, manager, worker or
reservation. Publish a source-only explanation and bounded repair contract or
a precise blocker, then stop before implementation or new admission. See the
[single handoff task](../../SESSION_HANDOFF.md#next-task). No full
convergence/tank/B2, physical, rendering or Mac work is admitted.

Changed: this result, R266 raw/hash/preflight/audit evidence, current
status/index pages, request/lifecycle/handoff. Checks: exact original and hash
replay, source/artifact/old-result audit, status/nonce/resource/cleanup checks,
AST/JSON/links/logs/IDs/whitespace at publication. Skipped: retry, new
admission, full convergence/tank/B2, physical/render
and Mac transfer. Unknown: why angular budgets disagree with the discrete
solution; whether a future source repair is justified; convergence, physical
reachability, R242's cause and artifact-label origin. PC retains ownership;
Mac released. Delivery commit belongs in Git and the final response.
