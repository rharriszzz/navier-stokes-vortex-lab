# R258 — One-use manufactured spatial BE pilot result

2026-09-26 (America/New_York), PC/WSL `daisy`. Clean launch source
`c34ecabe5cb9a89687bf4eaa782bd5b76022c1b5`.

**INCOMPLETE. The R257 manufactured allocation is spent 1/1.** The fixed caller
returned exit 1 and INCOMPLETE after the held worker exited 1 with
`RecursionError: maximum recursion depth exceeded`. The worker was reserved,
held, scope checked and released. It did not publish `finished.json`, a
numerical report or a resource snapshot. The saved worker log contains only the
exception type/message, so the failing call and whether FEM imports completed
cannot be identified from this run. No accuracy, convergence, rank or resource
event claim follows. Do not retry this allocation or use another directory.

## Launch and saved evidence

R258's STARTED checkpoint was published before launch. A read-only prelaunch
audit verified all 44 source/test/pin/reference hashes, 11 runtime artifacts,
four library resolutions, archive/interpreter, 74 older raw originals and the
absent fixed directory. The first sandboxed caller invocation stopped at
systemd manager access with `sd-bus operation failed: errno 1` after 0.092366 s.
This was before supervisor invocation, reservation, managed worker or numerical
import; the fixed directory and dangling link were absent afterward. Sandbox
access also prevented a direct manager query. The same clean caller/source was
then invoked with host approval; no source, environment, gate or allocation was
changed. See the [preflight refusal](evidence/r258/preflight_refusal.json).

The host-approved caller created the sole reservation in
`/tmp/navier-manufactured-r257-once`, checked the held scope and released the
worker. The retained directory has ten root files. All ten were copied
byte-for-byte into [run/](evidence/r258/run/) and listed with SHA256 and lengths
in the [raw inventory](evidence/r258/run_hashes.json), totaling 8,062 bytes.
The [saved-data audit](evidence/r258/audit.json) rechecks original bytes,
bindings, spent state, all saved status gates and process absence without FEM
imports or reassembly. The original local directory remains retained.

| Observation | Saved value |
|---|---|
| Reservation / held / release | Present; source commit and nonce agree |
| Worker | Exit 1; `RecursionError: maximum recursion depth exceeded` |
| Controller result / completion | INCOMPLETE / INCOMPLETE |
| Caller / caller completion | INCOMPLETE / INCOMPLETE; caller exit 1 |
| Controller setup | 0.159459 s, below 15 s |
| Controller elapsed before save | 0.980466 s, below 180 s |
| Caller elapsed after save | 1.113717 s, below 180 s |
| Cleanup | Empty; unknown children false; manager MainPID 0, ControlGroup empty |
| Recorded worker PID / cgroup | Both absent at audit |
| Numerical report / resource snapshot / exit receipt | Absent |

The controller's final reason is `missing, exceeded or unknown cleanup/resource
evidence`, because resource evidence could not be captured after the worker
failed before completion. The run log retains the earlier worker failure. The
saved manager result is `exit-code` and `ExecMainStatus=1`. No late marker or
partial write is present. Final completion-save tails and an independent parent
wall interval remain unobserved, as in the admission. The first sandbox refusal
had no reservation and is not counted as the numerical attempt; the
host-approved reservation spent the one-use allowance.

The six historical allowances remain spent. Saved R246 Poiseuille and R253
rotation results remain PASS, R242 remains INCOMPLETE, and R229's setup
predicate remains false. This R258 run produced no manufactured PDE or
diagnostic result. It does not revise the R255 scientific or resource gates.

## Next task

**GPT-6 Astra / high reviews the saved R258 failure and source to locate the
earliest defensible cause or precise blocker, then publishes a source-only repair
contract and stops before any new admission or numerical launch.** Use the raw
files and static or standard-library checks; do not reassemble, retry the spent
directory, change gates, or infer a stack trace from the one-line worker log.
The absence of a numerical report is a hard limit on scientific interpretation.
Follow the [single handoff task](../../SESSION_HANDOFF.md#next-task).

Changed: this result, preflight record, saved ten raw files, hash inventory,
saved-data audit, current status/index pages, request/lifecycle/handoff.
Checks: byte equality and SHA256 of ten originals; reservation/admission/source
and nonce binding; all four INCOMPLETE records; empty cleanup; recorded PID and
cgroup absent; prelaunch 44-file/artifact/history audit; JSON/AST/links,
append-only logs, request IDs and whitespace. Skipped: numerical reimport,
reassembly, solve, new allocation, full convergence/tank/B2, physical/render
and Mac transfer. Unresolved: precise recursion site, import/assembly progress,
resource peaks/events, manufactured errors and budgets, full convergence/rank,
R242 cause and artifact-label origin. PC retains ownership; Mac released.
Completion is prepared for publication; delivery commit/result belongs in Git
and the final response. Next prompt: **Continue**.
