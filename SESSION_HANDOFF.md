# Current session handoff

Last updated: 2026-09-20. Latest request:
[R033](REQUEST_LOG.md#r033--2026-09-20--continue-r022-prerequisite-coverage),
completed as the scoped Continue task below. The user permits using the PC
within its capabilities; the former small diagnostic caps are not immutable
user requirements. R023–R032 did not invoke Continue or authorize publication
at the time; their resource and machine continuity is included here where
needed for R033's work. R033 authorizes commit/push of its scoped result. The
last physical checkpoint remains R020; R033 prerequisites passed
without a physical run. The last previously committed checkpoint is
`0190893`.

## User goals

Read [STATUS.md](STATUS.md), including its new overall milestone table. The
user wants to learn whether exterior sensors and actuators can provide an
adequate initial setup for some orders of magnitude of the process, and provide
data for a separate, clear, approximately realistic 3D movie. Initial
preparation and continued driving are distinct. The quantity/range meant by
“orders of magnitude,” preparation tolerances, permitted continued actuation
and adequate sensing remain open. The illustrative movie pipeline is usable;
no physical preparation, attained contraction range or validated movie flow
history is established. We are still verifying numerical boundary responses.

## Reusable continuation request

In a session opened in this repository, say:

> Continue

The [short continuation request in AGENTS.md](AGENTS.md#short-continuation-request)
defines the workflow: log the request, complete the bounded task and checks,
update continuity, commit/push scoped work, and stop. Explicit qualifications
such as “Continue without pushing” override that default. It does not switch
the selected model or schedule another session. No scheduler is installed.

## Latest result: R022 toy memory stop

Read the [R022 result and next contract](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_RESULT.md),
[evidence index](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_EVIDENCE.md),
[derived result](docs/realizability/evidence/r022/result.json),
[validation](docs/realizability/evidence/r022/validation.json), and exact
[advanced toy source](docs/realizability/evidence/r022/advanced_toys.py),
[observer](docs/realizability/evidence/r022/presolve.py),
[physical runner](docs/realizability/evidence/r022/physical.py) and
[parent](docs/realizability/evidence/r022/run_contract.py).
Then read the [R021 contract](docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md),
[R020 physical stop](docs/realizability/B2_MATCHED_TRACE_COMPATIBILITY_RESULT.md),
[R013 original contract](docs/realizability/B2_MATCHED_TRACE_REVIEW.md) and
R016–R019 results linked there. Required research documents remain
`PROJECT_TRACKS.md`, `EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md` and
`CONTROL_RESEARCH_ROADMAP.md`.

R022 preserved all 19 production identities and 440 historical files and
reaudited R021 with writes redirected. The disposable runner implements fixed
q=64/q=96 and a once-only pre-solve observer, checking P and both A candidates
on copies before allowing factorization. Accepted A vectors are retained.
The actual observer path remains unvalidated: its toy cases were not reached.

The first toy attempt exposed a NumPy-Boolean JSON-reporting defect, fixed by
converting `accepted` to built-in bool. Its exact code/reports and 5.239195592 s
are preserved. The second attempt passed wrong-root refusal, all five original
phases, actual parent refusal and 16 high-order polynomial facet checks.
It then hit the 512 MiB child-tree cap at 513.60546875 MiB, before the first
observer case. Cumulative toy time was 16.405468375 s; maximum sample gap was
0.058599793 s. There was no numerical retry after this resource stop.

The final advanced child record is a partial last checkpoint, with all four
trace/order cases and no observer cases. Its 180.66015625 MiB process high-water
value is not the final peak. The parent saw up to four processes. Source order
and a generated C cache artifact suggest compilation contributed, but no
per-process RSS or intervening stage checkpoint identifies the exact cause.
No physical child, factorization, PDE solve or physical trace evaluation ran.

## R033 prerequisite and observer completion

Read the [R033 follow-up result](docs/realizability/B2_COMPATIBLE_TRACE_PREFLIGHT_FOLLOWUP.md),
[saved-data validation](docs/realizability/evidence/r033/validation.json),
[resource readings](docs/realizability/evidence/r033/resources.json), and
[cache accounting](docs/realizability/evidence/r033/cache_metadata.json).
The complete prerequisite suite passed in attempt 4 after four preserved
attempts and 56.251 seconds cumulative. All five original phases, wrong-root
and actual parent refusal, watchdogs, 16 high-order facet checks and all four
observer cases passed. The nine full block-oracle comparisons passed; the
observer ran once per case with zero factor/solve events. The maximum sampled
child-tree RSS across attempts was 571.42 MiB, under the capacity-sized 1536 MiB
cap; the final cache-reuse pass peaked at 171.24 MiB. One attempt exposed a
stale global FFCx cache artifact; another exposed a writable PETSc array access
in the toy. Both fixes were confined to the disposable harness. No global cache
or production source changed, and no physical child, mesh, factorization or PDE
solve ran. The B2 physical accuracy gate remains failed.

The Mac reassessment trigger from R031 has now been reached. The PC completed
this prerequisite comfortably within the selected cap. That does not size the
next physical calculation. The Mac's processor, OS, available RAM and exact
environment compatibility remain unknown, so there is not yet evidence to
recommend transferring the current work. Explicitly compare both machines
against the estimated physical workload before any physical launch; report the
choice then.

## Preserved physical limits

R020 remains the latest physical attempt: one mesh, P solve/correction and
checked outputs, then A_32 compatibility refusal before its solve. Its required
removal was 11.0906 times the unchanged arithmetic limit. The saved q64 flux
is motivation, not acceptance of an assembled candidate. R012 remains the
last complete physical response audit. R020's P gain is
`-1.6734724052233703 - 1.0983702805959774 i 1/m`, amplitude ratio 28,963.4968
and phase error 74.1175 degrees. Its arithmetic/output checks pass; reference
accuracy fails. No physical solution coefficient vector was saved.

Paired comparison, continuum geometry/spatial-error allocation and total FEM
error floor remain unknown. Alpha=48 remains inconclusive; certificates are
not integrated into schema-3 gate reports. The physical B2 gate stays failed
and `campaign_ready=false`. Force/power, pressure demand, hardware feasibility,
preparation, sensing and validated movie flow remain unassessed or unresolved.

## R023 resource clarification

Read [STATUS.md](STATUS.md#what-the-resource-budgets-mean) and the
[resource snapshot](docs/realizability/evidence/r023/resources.json). WSL sees
7.614 GiB RAM and 28 logical CPUs; 6.321 GiB was available when inspected.
This is not a measurement of total Windows-host RAM. Recheck capacity at launch.
The prior caps were local watchdog settings, not monetary or hardware limits.
Cumulative wall time covers all prerequisite phases and attempts within one
bounded task, including imports/compilation/reporting, but not analysis or
editing between launches. Memory is the sampled sum of resident memory of
active test descendants, not accumulated allocations over successive tests.

R023 supersedes the old prohibitions on increasing those conservative caps.
Use **600 seconds cumulative / 2048 MiB active child-tree RSS** for the next
prerequisite task, provided at least **4096 MiB RAM is available inside WSL at
launch**, and Windows also has adequate headroom for the workload (see R024
below). The guest check alone is insufficient. This leaves approximately
2 GiB of WSL headroom. If capacity differs, size the
job accordingly and record the chosen allowance before execution; do not
count swap as extra RAM. Keep runtime/memory watchdogs and stage reports.
Choose any later physical-run allowance from its expected workload and current
capacity when that separately scoped task is reached. A cap adjustment never
changes a scientific acceptance threshold or retroactively validates old data.

## R024 Windows and WSL memory

The [host/guest snapshot](docs/realizability/evidence/r024/resources.json)
records 15.725 GiB usable Windows RAM and 2.148 GiB available physical RAM;
WSL separately reported about 7.6 GiB total and 6.8 GiB available. These are
different views of shared physical resources, not two amounts of free RAM
that can be added. R023 measured only the guest. Check both host and guest
headroom before launching heavier work, and monitor host pressure during it.

Closing unused Chrome tabs/apps is a reasonable way to make room before the
next test; the user reported Chrome using 2.7 GB. No custom configuration file
was found at `C:\Users\rharr\.wslconfig`. The observed WSL capacity is consistent
with Microsoft's default of half the host RAM. Keep the current WSL limit for
the planned 2 GiB test; increasing it would not increase physical RAM. No app
was closed, WSL restarted, or host setting changed. The next scientific task
and all acceptance thresholds remain unchanged.

R025: the user confirms WSL Settings displays **8 GB memory and 2 GB swap**.
These are user-reported settings, consistent with the earlier guest readings.
Retain them for the planned test; swap is disk-backed overflow, not extra RAM.
Chrome Task Manager can identify individual tasks using memory (Shift+Esc on
Windows, or More tools > Task Manager). Advice only; no apps/settings changed.

R026: the user reports six YouTube tabs at about 0.2 GB each (roughly 1.2 GB
combined). Suggested bookmarking/closing unused tabs or enabling Chrome Memory
Saver; active playback can prevent automatic deactivation. No tabs were closed
or settings changed, and no resulting memory recovery was measured.

R027: Chrome Memory Saver was already on Balanced. The user is considering
Maximum; no switch is confirmed. Maximum deactivates eligible unused tabs
sooner, with reloading on return; active playback can still prevent this.
Suggested pausing unused videos and trying Maximum, then checking Windows
available memory. No new memory measurement or setting change was performed.

R028: the user highlights Maximum's "shorter period of time" versus Balanced's
"optimal period of time." Google's cited page supplies no exact timeout.
This describes earlier deactivation of eligible unused tabs, with the same
playback caveat; no setting change or memory recovery has been confirmed.

R029 supersedes the unconfirmed setting in R027/R028: the user switched Chrome
Memory Saver to Maximum and reports 2.6 GB Chrome memory after about one minute.
This is user-reported; no fresh host reading or causal effect was established.
Suggested pausing unused videos, leaving those tabs inactive for several more
minutes, then checking Windows available memory. No exact timeout is promised.

## R031 Mac decision checkpoint

The user has a Mac with **24 GB memory** and asks to be told when transferring
work would be worthwhile. Its chip, available memory, OS and installed tools
have not been inspected. Keep the next 2 GiB prerequisite task on the existing
PC setup if fresh host/guest capacity checks permit it. More installed memory
does not establish faster execution or adequate free memory on the Mac.

**Explicitly revisit and report the machine choice after prerequisite coverage,
before the next physical calculation.** Flag a move sooner if actual Windows
or WSL memory pressure prevents a bounded job from running comfortably after
reasonable headroom adjustments. Also reassess before a larger mesh or batch
whose estimated peak does not fit the PC with headroom. A local watchdog stop
alone is not evidence that another machine is required. Recommend transferring
only after comparing the expected workload with actual Mac capacity and the
cost of reproducing the environment. This is a checkpoint in future project
work, not a scheduled/background reminder or authorization to migrate now.

FEniCSx documents a [macOS installation route](https://fenicsproject.org/download/),
but this project's exact pinned environment has not been tested there.
`environment-b1.yml` pins DOLFINx/PETSc/MPI versions; the current harmonic
backend uses coupled real blocks with a real PETSc build. Preserve that choice.
The archived watchdog reads Linux `/proc`, and RSS reporting must be checked
for the destination platform. At migration, establish the Mac architecture,
recreate compatible dependencies, adapt monitoring in a new copy, and run a
small reference comparison under unchanged scientific tolerances. Preserve
the PC checkpoint and historical evidence; do not copy Linux binaries/JIT
caches as a Mac environment or silently upgrade the numerical stack.

## Next task

Review the now-exercised disposable observer and remaining physical runner
against the unchanged R021/R013 contract before deciding whether to conduct a
separately scoped matched-trace physical comparison. Recommend **GPT-6 Astra
with high reasoning** for this scientific review. Recheck model availability
when handing off. R030 rechecked the official model pages:
[Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) and
[Astra](https://developers.openai.com/api/docs/models/gpt-6-astra).
The review should check the saved P/A/A compatibility logic, the independent
full-block lifting oracle, refusal preservation and no-factorization sentinel;
then inspect physical launch gates, report counts, resource checks and output
validation against the R021 fixed q=64/q=96 experiment and R013 thresholds.
It should state assumptions, alternatives, unresolved numerical risks and
whether a separate physical experiment is warranted. Also compare the Mac and
PC against the estimated physical workload; do not recommend migration from
installed RAM alone.

Completion is a documented review and a separate decision boundary. Stop before
physical execution, solver changes, new meshes/orders, pressure/return-flow
repair, gate integration, campaign, B3, rendering or encoding. If the review
finds only a clearly understood mechanical defect, recommend GPT-5.6 Luna with
medium reasoning for a narrow repair. Retain GPT-6 Astra/high for unexplained
results or any scientific/numerical-method decision. No model switch or
automation occurred. **Next prompt: Continue.**
