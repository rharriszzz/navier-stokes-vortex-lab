# R256 — Manufactured spatial BE pilot source integration

2026-09-26; PC/WSL `daisy` retains ownership. The fixed [R255
contract](VERIFICATION_MILESTONE_R255.md) now has a reviewable source path for
one n=2, t=dt=1/8 manufactured backward-Euler pilot. **This is source and
fake-test evidence only. No numerical attempt, caller or execution admission
was created.** The [source audit](evidence/r256/audit.json) and [test
result](evidence/r256/tests.json) give the reproducible checks. Follow the
[single next task](../../SESSION_HANDOFF.md#next-task).

The new `future_manufactured.json` is byte-identical to R255's non-executable
proposal and is checked canonically against it. `manufactured_policy.py`
keeps the 30-key, 17 signed-floor, 12 nonnegative policy separate from the old
Poiseuille/rotation policies. The injected `manufactured_driver.py` uses the
existing cube adapter's exact polynomial history and corrected BE load in the
residual and in both degree-24/26 diagnostics. It fixes the exact lateral lift,
perturbs the lowest free velocity DOF, uses frozen row scales, records a latest
405-DOF sparse system before each correction and retains all 60 scalar
form/assemble receipts, including zero returns. It measures geometry, fluxes,
targets, three-row Gram/condition, return samples and signed budgets.

The pure reducer independently recomputes the exact-target comparisons,
quadrature policy, both degree reports, finite coarse errors, nonlinear and
each linear-correction gate, flux/gauge/eta/backflow gates, signed rates,
BE storage identities and endpoint interval balances. It uses R255's rational
nonzero return totals for report errors. A failed numerical gate is retained
as a complete finite report but cannot pass the controller. Malformed, cached,
missing, extra, nonfinite and bool-as-number records refuse. The held worker
checks reservation/source/cgroup/thread state before pinned imports and writes
the bounded report; fixture-locked supervisor/backend dispatch retains the
existing one-attempt cleanup and resource lifecycle. It still requires a
separate source-bound admission before reservation.

**103 standard-library/injected-fake tests passed under pinned Python 3.12.13
with no numerical modules loaded.** The added tests cover the rational
reference/negative controls, two-degree routing with exact history/corrected
load sentinels, actual Newton callback and evidence-before-solve order,
nonzero return and multiplier propagation, pair/step/budget/identity failures,
strict envelope and cached-decision mutations, held-before-import and
incomplete supervisor outcomes. Saved R246 Poiseuille and R253 rotation
validators both replayed PASS with the new source loaded. The audit confirms
33 of 36 prior bound source/test/pin files unchanged, the three intended
shared dispatch/linear-evidence edits, seven added fixture files, and the
unchanged R255 exact reference and 512-DOF recorder cap. No old manifest,
policy, scientific gate, solver option, historical evidence or allocation was
changed.

The source has **not** imported UFL/DOLFINx, JIT compiled a form, assembled a
real matrix, solved, connected to the manager or measured a manufactured
numerical result. Actual form simplification/API behavior, runtime/cost,
nonlinear convergence, pair/budget outcomes, coarse approximation errors and
full operator rank remain unknown. R246/R253 remain saved PASS, R242 remains
INCOMPLETE and R229's setup predicate remains false. All six old allowances
remain spent; this task grants zero new attempts. No convergence or physical
realizability claim follows from these source checks.

Next: Astra/high reviews R256's source and evidence against R255, then
publishes a separate fresh, source/interpreter/artifact-bound one-use admission
and finite caller, or a precise blocker. Stop before numerical launch. If the
review fixes an implementation detail without changing scientific gates, Sol/high
can make that bounded source repair; a scientific/gate revision belongs to
Astra/high. A later admitted launch would use Sol/high and return its result to
Astra/high for interpretation.
The [official OpenAI Astra model page](https://developers.openai.com/api/docs/models/gpt-6-astra)
lists high reasoning support; this recommendation is a task-fit judgment, not
an account-specific availability check or an agent model switch.
