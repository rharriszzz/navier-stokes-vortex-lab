# R242 — Single serial SuperLU Poiseuille result

2026-09-26, PC/WSL daisy. Base `a118ee2`; clean published launch source
`8622c8af8481ec4c4c11194dbc7d41571aa38ad8`.

**INCOMPLETE. R241 allocation spent 1/1; no retry or new allocation.**
The exact [R241 caller/admission](POISEUILLE_ADMISSION_R241.md) ran once.
Three SuperLU corrections passed true-residual checks and Newton converged,
but the unchanged degree-24/26 comparison rejected 12 diagnostic entries.
The controller refused with `Refusal: failed or inconsistent numerical evidence`.
Worker exit 0 is not numerical acceptance; caller exit 1 preserves the refusal.

## Launch, evidence and cleanup

The published STARTED record preceded launch. Preflight verified all 27 source/
pin hashes, caller and artifact-inventory digests, seven runtime artifact hashes,
four library resolutions and the exact R229 interpreter. The fixed directory
was absent. The caller refreshed host memory (6,540,840 KiB available) and
manager version 249.11-0ubuntu3.22 before reservation at 21:01:59 UTC.
Checkout and environment remained unchanged through the single host-manager
invocation. No pre-reservation failure or recovery occurred in R242.

[Execution receipt](evidence/r242/execution.json),
[prelaunch checks](evidence/r242/prelaunch.json),
[postrun checks](evidence/r242/checks.json) and
[raw-file inventory](evidence/r242/run_hashes.json) retain the provenance.
All 15 raw files from `/tmp/navier-poiseuille-r241-once` are copied byte-for-byte
under [run/](evidence/r242/run/), including numerical/resource reports and logs.
No raw root file is omitted; no `.writing` record exists.

| Observation | Saved value |
|---|---|
| Caller interval after caller save | 22.424088505998952 s / 180 s cap |
| Controller setup / work / observed finish | 0.153480 / 22.178038 / 0.007526 s |
| Worker exit / caller exit | 0 (manager success) / 1 |
| Memory peak | 280,064,000 bytes / 1,610,612,736 cap |
| Task peak | 6 / 32 cap |
| memory.max / OOM / OOM-kill / PID-limit events | 0 / 0 / 0 / 0 |
| Cleanup | empty; unknown_children=false; manager inactive/not-found/MainPID 0 |
| Recorded PID / cgroup | PID 154443 and saved cgroup absent on postrun check |

Resource data end **before final worker handshake/exit**; limits remained
active. Final completion-save tails were not observed, and the external parent
wall interval was not separately measured. The records support these bounded
observations, not complete-accounting claims or an overall PASS. R229's earlier
setup resource predicate remains false.

## Numerical report, without changing acceptance

The [raw numerical report](evidence/r242/run/numerical.json) records n=2,
402 mixed / 405 global unknowns, 240 fixed velocity DOFs, one dt=0.125 BE step,
and a perturbed free-velocity initial guess. Newton residual history is
0.014886035070117069, 3.416928913535827e-05, 1.449690234409104e-10,
1.5160682224468997e-15. Three linear true residuals are
1.2839311693647426e-17, 4.644630596411413e-20 and 2.7329637786591138e-25.

The report marks verified correction, step gates, exact velocity/pressure,
divergence, multipliers, return traction and physical endpoint budgets true.
The sole false top-level check is `quadrature_24_26`; `numerical_accepted=false`.
These are the saved run's checks, not general solver validation or a convergence
study. The failed entries below all retain their original limit of 1e-18.
No threshold was changed or result reclassified.

| Degree-26 minus degree-24 entry | Difference |
|---|---:|
| `angular.advective` | -1.7729416025569231e-16 |
| `angular.storage` | 1.7990144820356351e-18 |
| `angular.traction` | 6.7680348583096126e-16 |
| `energy.advective` | -1.4006536815797108e-16 |
| `energy.conservative_divergence` | 3.9119972611677399e-17 |
| `energy.pressure_divergence` | 1.0854822010059886e-17 |
| `energy.storage` | -6.2285671464058356e-18 |
| `energy_identity_storage` | -6.2016359633783808e-18 |
| `kinetic_discrete_derivative` | -6.2016359633783808e-18 |
| `lateral_flux` | -2.2204460492503131e-16 |
| `p_error_integral` | 8.133738142217297e-18 |
| `pressure_mean` | 4.5215573401231283e-16 |

The source/roundoff/normalization interpretation of these failures is the next
review; no cause is asserted here. There was no rank, SVD, alternative-factor
analysis, extra assembly or solve after the attempt.

## Retained latest system

[linear_system.json](evidence/r242/run/linear_system.json) is the actual
lifted/scaled 405-by-405 CSR/RHS before **correction 3** factorization, with
6,909 stored entries, state, row scales, 240 fixed indices/values, source binding
and explicit SuperLU settings. Size 186,809 bytes; SHA256
`76bd07d6cde88cf6693c1e2cc6bfc2892137f8cd93ddda4a318799a3fd113c23`.
Its digest/size/correction match the final flushed receipt. Source binding
matches the held worker and controller. Records for corrections 1 and 2 were
overwritten as designed; their digest receipts remain in worker.log. The saved
matrix is not the final converged state. Rank, factor permutation and pivot
coordinate are not established (the latter two remain null).

## Completion and next task

All four allocations remain spent 1/1. Thirty older raw files still match their
retained originals; all three older reservations persist and saved PIDs/cgroups
are absent. Runtime source and pins are unchanged. R241's 69 standard-library
tests were reused, not rerun. New checks cover evidence integrity, bindings,
cleanup, JSON/links, append-only records and publication scope. Skips include
rerun/rank analysis, installation, full suite/rotation/tank/B2, rendering,
physical work and Mac transfer. The exact SuperLU package/embedded version
label discrepancy remains accepted only as specified in R241.

Next: **GPT-6 Astra / high** reviews the saved quadrature refusal and acceptance
scales, with source/algebra evidence only, then publishes a justified method
proposal or precise blocker. No new workload or retroactive PASS. Follow the
[single next task](../../SESSION_HANDOFF.md#next-task).
[Official model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra)
was rechecked for high support; task fit is judgment. No model/session switch
or /new is required. PC retains ownership; Mac remains released.
