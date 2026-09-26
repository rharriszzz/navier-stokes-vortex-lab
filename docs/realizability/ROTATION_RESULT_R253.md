# R253 — One-use exact-field rotation assembly result

2026-09-26, PC/WSL daisy. Clean launch source
`2e60a7bdc635587b09e3da5f6a03eed2ef3c85c3`.

**PASS under the fixed R251 admission. The rotation allocation is spent 1/1;
no retry or alternate directory.** The fixed caller returned 0 and PASS after
12.771162 seconds. Both degree-24 and degree-26 exact-field assembly reports
pass all 38 target checks; all 38 pair checks pass. All 76 original UFL forms
were compiled through `fem.form` and passed to `fem.assemble_scalar`, including
those whose actual results were zero. The complete schema-1 numerical envelope
passed the strict saved-data validator. This is one exact-field assembly oracle,
not a PDE solve, production weak-form validation or convergence result.

## Fixed launch and preserved evidence

The R253 STARTED record was published before launch. The separate
[R251 admission](ROTATION_ADMISSION_R251.md) bound the clean source, 36-file
inventory, caller, manifest/contract, exact interpreter and runtime artifact
inventory. Read-only prelaunch checks confirmed those hashes, 11 runtime files,
four library resolutions and archive, with 6,500,844 KiB host memory available
and the fixed directory absent. The exact caller then checked the real manager
version and reserved `/tmp/navier-rotation-r251-once` once. No pre-reservation
failure, repair or retry occurred.

The [audit](evidence/r253/audit.json) replays the R250 saved-data audit and the
R246 Poiseuille controller PASS, validates the actual rotation envelope from
saved files, verifies all 76 stage receipts/log pairs, and checks original
bytes. All 14 raw root files were copied byte-for-byte to [run/](evidence/r253/run/)
and listed with SHA256 and byte counts in [run_hashes.json](evidence/r253/run_hashes.json).
Total preserved raw size is 99,218 bytes; the complete numerical envelope is
40,167 bytes, below the 2,000,000-byte cap. No `late.json` or partial `.writing`
file exists. The original local directory is retained.

| Observation | Saved value |
|---|---|
| Worker/caller exit | 0 / 0; manager result success |
| Controller result/completion/caller/caller completion | PROVISIONAL_PASS / PASS / PASS / PASS |
| Controller setup/work/finish | 0.159619 / 12.472294 / 0.025483 s |
| Caller interval after caller completion save | 12.771162 s / 180 s ceiling |
| Managed memory peak | 223,670,272 bytes / 1,610,612,736 cap |
| Managed task peak | 6 / 32 cap |
| memory.max / OOM / OOM-kill / PID-limit events | 0 / 0 / 0 / 0 |
| Effective scope | memory cap 1536 MiB; swap 0; tasks 32; independent expiry 150 s, comprising 149 s runtime plus 1 s stop grace; one rank/thread |
| Cleanup | empty; unknown_children=false; manager MainPID 0, no control group |
| Recorded worker PID and cgroup | PID 162076 and saved cgroup absent at audit |

The resource snapshot ended before final worker handshake/exit; limits remained
active. Final completion-save tails and an independent parent wall interval
remain unobserved. These are the same measurement boundaries disclosed in R251;
no cold-start timing claim follows. R229's earlier setup resource predicate
remains false and is not reclassified by this run.

## Saved numerical outcome

Measured n=2 cube receipt: 48 tetrahedral cells, 27 vertices, 48 exterior
facets with eight tagged facets on each of six faces, and 402 unused P2/P1
mixed-space DOFs. The exact velocity and pressure were coordinate expressions;
the mixed space did not represent the oracle fields. Both degrees saved exactly
38 raw values and 38 assembly receipts. Maximum per-degree absolute-error to
limit ratios were 0.091704 at degree 24 and 0.090150 at degree 26, each from the
volume integral. All five required squared-zero norms, including the local
momentum residual and six-face viscous traction, assembled to 0.0 at both
degrees; no expected zeros were substituted. The nonzero squared velocity,
gradient, pressure and total traction anchors also passed.

This result establishes that the pinned DOLFINx/UFL/FFCx path accepted this
specific set of 76 domain-bound scalar forms and assembled their saved values
within the R247 exact and pair tolerances. It does not independently validate
the viscosity coefficient: rigid rotation has zero symmetric strain. It does
not establish PDE convergence, inf-sup stability, general solver behavior,
manufactured spatial/time accuracy, tank behavior or physical realizability.
The R242 historical INCOMPLETE outcome remains unchanged; R246 Poiseuille
remains PASS under its separate policy. All five prior allowances remain spent.
The accepted SuperLU/FFCx package-label issues remain documented, with no new
artifact identity claim beyond the bound inventory.

## Next task

**GPT-6 Astra / high reviews this fixed PASS and selects the smallest justified
next verification milestone or a precise blocker, then publishes and stops
before implementation or new numerical admission.** Use the saved raw evidence,
source and algebra to distinguish what the exact-field assembly proves from
manufactured/PDE and convergence requirements. Preserve the spent rotation and
five older allocations. Decide whether a manufactured nonzero-strain or
spatial-convergence oracle should be next and state source/admission prerequisites,
validation and stop rules. Do not run extra numerical imports, reassemble,
retry, alter gates, install, or begin tank/B2/physical/render work in that review.
Follow the [single handoff task](../../SESSION_HANDOFF.md#next-task).

Changed: this result, preserved 14 raw files, raw-hash inventory, stdlib audit
and checks, current index/status pages, request/lifecycle/handoff. Checks: saved
rotation payload and 76 receipts/log pairs, all fixed scientific/scope/resource/
exit/cleanup/caller gates, original-byte hashes, R250 audit and R246 replay,
60 older raw originals/five prior reservations with absent recorded PIDs/cgroups,
36 unchanged source hashes, JSON/links, request IDs, append-only records and
whitespace. Skipped: new numerical imports/assembly/solve/rank, fresh artifact
rescan/install, full suite/tank/B2, physical/render and Mac transfer.
Unresolved: general convergence and production weak forms, historical R242
cause, matrix rank and artifact-label origin. PC retains ownership, Mac released.
Completion prepared for publication; delivery commit/result belongs in Git/final
response. Next prompt: **Continue**.
