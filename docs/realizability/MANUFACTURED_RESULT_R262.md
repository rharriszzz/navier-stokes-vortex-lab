# R262 — One-use diagnostic manufactured pilot result

2026-09-26 (America/New_York), PC/WSL `daisy`. Clean launch commit
`8de6ffd1d9c089eead43a804fe59cb65ea789774` was published before launch.

**INCOMPLETE. The separate R261 allocation is spent 1/1.** The exact fixed
caller exited 1 after the reserved, held and released worker exited 1 with
`RecursionError: maximum recursion depth exceeded`. There was one reservation
and one managed worker; no numerical retry or alternate directory. The eleven
raw run files plus caller stdout and empty stderr were copied byte-for-byte
to [evidence](evidence/r262/run/) and inventoried with hashes in
[run_hashes.json](evidence/r262/run_hashes.json). The retained original is
`/tmp/navier-manufactured-r261-once`. The [saved-data audit](evidence/r262/audit.json)
verifies all 13 copied files, their 13,250 total bytes and the spent state.

The new [failure record](evidence/r262/run/failure.json) narrows the failure.
Imports, recorder initialization, mesh/geometry, history/lift and primary forms
completed. `primary_compilation` began but did not complete. The bounded trace
passes through `Assembler.__init__` at `cube_adapter.py:195`, the first
`fem.form(forms['jacobian'])`, then DOLFINx form creation/JIT and repeated UFL
derivative traversal. It is truncated to 32 frames, so the underlying
expression or recursion trigger is not established. This is evidence that FEM
imports and primary form construction completed, not that compilation, assembly
or solve completed. No numerical report or resource snapshot exists; pilot
accuracy, budget and managed resource peaks/events remain unknown.

| Observation | Saved value |
|---|---|
| Reservation / held / release | Present; source commit and nonce agree |
| Worker / caller exit | 1 / 1 |
| Controller, completion, caller, caller completion | INCOMPLETE throughout |
| Failure stage | `primary_compilation`; previous completed `primary_forms` |
| Setup / controller before save / caller after save | 0.147778 / 0.921778 / 1.036549 seconds |
| Cleanup | Empty; unknown children false; manager MainPID 0, ControlGroup empty |
| Recorded PID / cgroup | Both absent at audit |
| Numerical report / resource snapshot / exit receipt | Absent |

The controller reason is `missing, exceeded or unknown cleanup/resource
evidence`; its log also records the earlier worker exit. No finite resource
peak or event count can be inferred. The independent parent wall interval and
final save tails were not observed. R246 and R253 saved PASS, R258 INCOMPLETE,
R242 INCOMPLETE and R229 setup predicate remain unchanged. All seven older
allocations remain spent; R261 makes eight spent allocations total. The R255
scientific and resource gates are unchanged.

**Next:** GPT-6 Astra/high reviews the saved R262 failure, the Jacobian form
and UFL derivative construction using source-only or injected-fake checks,
then publishes a repair contract or precise blocker. Stop before a new
admission, numerical import, manager, worker, assembly or solve. Do not retry
the spent directory. The [single handoff task](../../SESSION_HANDOFF.md#next-task)
has the completion criteria.

Changed: this result and raw/audit evidence, current status/index pages,
request/lifecycle/handoff. Checks: exact saved/original bytes and SHA256,
reservation/source/nonce/status/cleanup/process checks, old saved results,
source/artifact binding, AST/JSON/links/logs and whitespace. Skipped: a second
numerical launch, reimport/reassembly/solve, new admission, full
convergence/tank/B2, physical/render and Mac transfer. Unresolved: precise UFL
recursion trigger, resource peaks/events, manufactured errors/budgets,
convergence/rank, R242 cause and artifact-label origin. PC retains ownership;
Mac released. Delivery commit/result belongs in Git and the final response.
