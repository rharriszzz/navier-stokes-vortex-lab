# Current session handoff

Last updated: 2026-09-20. Workflow: [R008](REQUEST_LOG.md#r008--2026-09-20--short-continuation-request).
Last completed B2 task: [R008](REQUEST_LOG.md#r008--2026-09-20--short-continuation-request).

## Reusable continuation request

In a session opened in this repository, say:

> Continue

The [short continuation request in AGENTS.md](AGENTS.md#short-continuation-request)
defines the full workflow: log the request, complete the bounded task and its
checks, update Markdown and the next model's handoff, commit, push, and stop.
An explicit qualification overrides the default, such as “Continue without
pushing.” The selected model is unchanged by the prompt; choose the recommended
model/effort when starting the session. No scheduler is installed.

## Next task

**GPT-6 Astra, high reasoning:** complete the bounded physical-response
accuracy/error-floor investigation specified in the
[R008 next-task contract](docs/realizability/B2_RESPONSE_COERCIVITY_RESULT.md#next-bounded-task-physical-accuracy-and-error-floor-investigation).
Read that result and its exact-runner appendix, the R005/R007 method and
interpretation, the independent swirl-reference derivation, prior report
reviews, and the four root research documents (`PROJECT_TRACKS.md`,
`EXPERIMENT.md`, `PHYSICAL_REALIZABILITY_PLAN.md`, `CONTROL_RESEARCH_ROADMAP.md`).

Use existing source and stored reports plus bounded reference/feature-quadrature
calculations. Reproduce the physical complex disk gain and response scale;
quantify series/quadrature sensitivity and relate absolute complex error to the
existing 5% magnitude/5-degree comparisons without changing thresholds.
Distinguish algebraic residual/roundoff, cancellation/quadrature, boundary-load
and geometry error, and spatial resolution; explicitly identify unknowns.
Alpha=96 is a certified verification candidate only on the recorded geometries;
alpha=48 remains inconclusive, and no production penalty has been selected.

Compare a targeted error/adjoint diagnostic with a boundary-layer or
symmetry-restricted accuracy investigation. Select one proposed affordable
experiment with observable acceptance evidence, identity checks, measured or
conservative resource limits, and failure conditions. The 2.69 s geometry
study does not estimate global factorization cost; retain the historical
25 mm direct-solve peak near 6.9 GiB and failed 20 mm allocation as constraints.

**Limits:** retain R/H/nu/f/U_probe/disk, signed features, phasor convention,
facet-consistent target, and all physical thresholds. New calculations may
use only the existing 32/64/128-term reference and at most 512-point quadrature
per integrated coordinate, under a parent-enforced 120 s total calculation /
1 GiB RSS budget. Do not generate meshes, assemble global operators, factorize,
run harmonic pilots, integrate the certificate into the gate, or start campaigns
or B3. Default 500-cell and dense 3,000-free-DOF guards remain unchanged.

**Completion and stop:** preserve the quantitative error budget, reproducible
calculation text, compact evidence/provenance, checks/skips, and one concrete
proposed experiment. Commit and push under `Continue`, then stop at the review
boundary. Stop earlier on reference inconsistency or a resource cap, recording
the evidence. Keep the physical B2 gate failed and `campaign_ready=false`.

**Following recommendation:** if the review produces a fully specified
mechanical diagnostic/report package, recommend GPT-5.6 Luna, medium, with
exact edits, focused checks, and a stop before scientific interpretation.
If a numerical-method choice or interpretation remains, retain Astra/high and
state the bounded unresolved question. Do not start that following task here.

**Availability:** checked 2026-09-20 in this session's model tool catalog and
the official [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra)
and [Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna) pages.
Both named models/efforts are listed; the user's picker can depend on account
and client. No model switch, delegated session, or automation was launched.

## Last completed work

R008 evaluated the existing local certificate on 50/40/30/25 mm in four fresh
serial processes, once per mesh. Every identity matched. Alpha=96 was certified
positive on all four; alpha=48 remained inconclusive. C_upper values were
58.1265712308/57.9026155132/58.4738571184/59.3021263562. Total time was 2.6918 s,
with maximum parent-observed child-tree RSS 184.5078 MiB and maximum sample gap
0.05561 s, within the 120 s/1 GiB caps and 0.1 s monitoring requirement.

Checks: four mesh identities, geometry/facet guards, 6,351 finite local values,
eight classifications, 19 package/config hashes, strict JSON/Markdown and
22-file manifest integrity. Synthetic wall/RSS watchdog checks passed.
Focused ordinary coercivity tests: six discovered, five passed, one optional
DOLFINx/UFL skip. No global matrices, dense/PDE checks, harmonic responses,
rendering, encoding, or full suite were run. Numerical source, defaults,
physical thresholds, and gate behavior are unchanged; schema-3 still reports
response stability `not_assessed` because the independent evidence is not
integrated. Physical accuracy and alpha=48's actual stability remain unresolved.

Evidence is in `/tmp/navier-b2-response-coercivity-r008/`, with the exact runner,
compact numerical records, config/provenance, and hashes preserved in
[B2_RESPONSE_COERCIVITY_EVIDENCE.md](docs/realizability/B2_RESPONSE_COERCIVITY_EVIDENCE.md).
The [result](docs/realizability/B2_RESPONSE_COERCIVITY_RESULT.md) records scope,
checks/skips, costs, and the next-task contract. Documentation checks include
links/anchors, fenced syntax, table/evidence consistency, exact runner bytes,
and `git diff --check`.
