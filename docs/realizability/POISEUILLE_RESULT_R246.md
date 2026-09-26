# R246 — R244-policy Poiseuille single-fixture result

2026-09-26, PC/WSL daisy. Base `8de00a4`; published clean launch source
`65ab4bf108c941cbc9a549b20c5bce50883cdd5e`.

**PASS under the R245 contract. Allocation spent 1/1; no retry.**
The exact [R245 caller/admission](POISEUILLE_ADMISSION_R245.md) ran once.
Three serial SuperLU corrections passed true-residual checks and Newton
converged. All 30 degree-24/26 comparisons and physical checks at both degrees
passed under the explicit R244 policy. Worker and caller exited 0.
This is one fixed n=2 oracle result; it does not establish mesh/time convergence,
general mixed-operator stability, tank behavior or physical realizability.
All four older allocations remain spent and their outcomes unchanged;
**R242 remains INCOMPLETE** under its original contract.

## Launch and retained evidence

The clean STARTED publication preceded execution. Prelaunch checks verified
29 source/test/pin hashes, caller/manifest/policy/artifact-inventory digests,
seven runtime artifacts, four library resolutions, exact interpreter and cached
SuperLU archive. The fixed directory was absent, including dangling links.
The caller refreshed capacity (6,526,440 KiB available) and systemd manager
version 249.11-0ubuntu3.22; reservation occurred at 21:44:43 UTC.
The exact environment and checkout remained unchanged through execution.
No pre-reservation caller failure, repair or retry occurred in R246.

[Execution receipt](evidence/r246/execution.json),
[prelaunch verification record](evidence/r246/prelaunch.json),
[postrun checks](evidence/r246/checks.json) and
[raw-file inventory](evidence/r246/run_hashes.json) retain provenance.
The prelaunch record was written after execution from observed tool checks and
caller evidence; it does not invent a prelaunch timestamp.
All 15 raw root files from `/tmp/navier-poiseuille-r245-once` are copied
byte-for-byte under [run/](evidence/r246/run/). No partial `.writing` or late
marker exists. The saved result is deliberately `PROVISIONAL_PASS`;
controller completion and both caller records are `PASS`, with actual exit 0.
No raw status was rewritten.

| Observation | Saved value |
|---|---|
| Caller interval after caller save | 2.897688477009069 s / 180 s cap |
| Controller setup / work / observed finish | 0.143371 / 2.676307 / 0.009091 s |
| Worker exit / caller exit | 0 (manager success) / 0 |
| Memory peak | 319,332,352 bytes / 1,610,612,736 cap |
| Task peak | 5 / 32 cap |
| memory.max / OOM / OOM-kill / PID-limit events | 0 / 0 / 0 / 0 |
| Cleanup | empty; unknown_children=false; inactive/not-found/MainPID 0 |
| Recorded PID / cgroup | PID 157349 and saved cgroup absent on postrun check |

Resource data end **before final worker handshake/exit**; limits remained
active. Final completion-save tails are unobserved. The parent wall interval
was not independently measured. PASS refers to the existing bounded contract,
not complete accounting beyond these measurement boundaries. R229's earlier
setup resource predicate remains false. Prior cache state was not reset or
prewarmed; this elapsed time is not a cold-start performance claim.

## Saved numerical outcome

The [schema-2 report](evidence/r246/run/numerical.json) records one n=2,
dt=0.125 BE step, 402 mixed / 405 global unknowns, 240 fixed velocity DOFs,
and a perturbed free-velocity initial guess. It contains the exact
`poiseuille_signed_accuracy_v1` policy and degree-24 backflow sampling claim.

Newton residual history: 0.014886035070117069, 3.416928913535827e-05,
1.449690234409104e-10, 1.5160682224468997e-15. The three linear true residuals:
1.2839311693647426e-17, 4.644630596411413e-20, 2.7329637786591138e-25.

The controller accepted verified correction, step gates, exact velocity/pressure,
divergence, multipliers, return traction, physical endpoint budgets and
quadrature agreement. Each degree's retained physical checks passes, and all
30 pair comparisons pass. The controller recomputed the report using the
shared deterministic helper; this is not an independent physics implementation.
The 17 signed-key target is the prospective accuracy budget reviewed in R243
and implemented before admission; no acceptance threshold changed in this run.
It is not proof of a rounding-error bound or of the cause of R242 discrepancies.

## Latest system and preservation checks

[linear_system.json](evidence/r246/run/linear_system.json) contains the actual
lifted/scaled 405-by-405 CSR/RHS before correction 3 factorization, with 6,909
stored entries, state, row scales, 240 fixed indices/values and exact source/
solver settings. Size 186,809 bytes; SHA256
`25be7abc311a8cfc6ce0e3fe4cf960a456a7a170d2caf5bff85793e3d00038eb`.
The final receipt and held/controller source binding match. Earlier matrices
were overwritten as designed; their digest receipts remain. This is not the
final converged matrix. No rank, SVD, alternate factorization or additional
solve was performed. Rank and factor permutation remain unestablished.

All 45 older raw files still match their originals; four older reservations
persist and their recorded PIDs/cgroups are absent. All 29 source/test/pin files
are unchanged. R244's 77 tests and R245's caller/nine focused tests are reused,
not rerun. This task checks raw integrity, source/policy bindings, saved
acceptance/cleanup, JSON/links, append-only records and publication scope.
The exact SuperLU package/embedded-label discrepancy remains as accepted in R245.

## Next task and stop

**Astra/high reviews the saved PASS against the verification roadmap and defines
the smallest justified next verification milestone, or a precise blocker.**
Use saved evidence and source/algebra only. Separate what this fixed oracle
establishes from remaining manufactured-solution, mesh/time convergence and
boundary-response requirements. Specify necessary implementation/admission
changes, checks and stop rules; publish the review and stop before implementation,
new allocation or numerical execution. All five allocations are spent.
Follow the [single next task](../../SESSION_HANDOFF.md#next-task).
[Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was searched/opened for high support; task fit is judgment. No model/session
switch or /new required. PC retains ownership; Mac remains released.

Skipped: rerun, extra assembly/solve/rank analysis, install, full suite/rotation/
tank/B2, rendering/physical work and Mac transfer. Outstanding decisions concern
next verification scope and evidence needed beyond this single fixed oracle;
historical discrepancy cause and exact artifact-label origin remain unresolved.
