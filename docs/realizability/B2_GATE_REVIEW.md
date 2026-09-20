# B2 acceptance-logic review and bounded repair handoff

Prepared 2026-09-20 against clean commit
`5a7bd5b830baa26bf27b936bc4fed8e56bf5062b`.

## Decision

Repair the rejection report and the energy-check acceptance logic before another
response study. The new implementation reproduces the previous small-cylinder
spectral and energy results, but its report can crash on rejection and its
stability decision ignores the independently computed time step.

This review completes an audit of the B2 acceptance path. It does not select a
production mesh, penalty, solver, boundary interpretation, or new physical
acceptance threshold. Keep the existing Stokes model, facet-consistent target,
features, and physical pilot parameters. The historical physical-pilot gate
remains failed. The resolved swirl fixture and production meshes were not rerun.

## 1. Rejected stability checks crash the Markdown report

In `realizability/backends/b2_gate.py`, `run_b2_gate` correctly returns early
when the small-cylinder audit rejects a penalty. That result omits the affine,
PDE, mesh, penalty-sensitivity, and quadrature stage results because those
stages did not run.

`format_b2_gate` accesses those missing keys while constructing its initial
table, before reaching its rejection branch. This was reproduced with the real
optional solver, using the known unstable penalty:

```bash
python -m realizability.cli b2-gate \
  --config configs/realizability/pilot.json \
  --mesh-sizes 0.10 0.07 \
  --penalty-factor 6 --comparison-penalty-factor 48 \
  --output-dir /tmp/navier-b2-review-rejected-gate
```

The command exited with status 1 and
`KeyError: 'affine_verification_passed'` at `b2_gate.py:261`.
It wrote a strict `gate.json` containing an explicit failed stability gate, but
did not write `gate.md`. No harmonic pilot was launched. If an output directory
already contains Markdown from an earlier run, that old file can remain beside
the newly written JSON.

Render the rejection branch before accessing later-stage results. Display
unexecuted stages as **not run**, preserving the distinction between rejection
and an unexecuted check. Include the blocking reason and audited mesh/penalty
scope. Do not fabricate passing or failing values for unexecuted PDE solves.

## 2. The energy time step cannot currently fail the stability decision

`realizability/backends/b2_stability.py` records the measured energy ratio,
eigenvalue prediction, and step algebraic residual. None contributes to
`stability_checks_passed` or `all_requested_cases_stable`.

A controlled fault injection confirmed this. On the real 100 mm, alpha=48
spectral fixture, only `_backward_euler_step` was replaced with a function that
returns twice the initial velocity, a 1 s time step, and residual 1.0. The
result was:

| Diagnostic | Result |
|---|---:|
| Minimum decay rate | +0.0018591066448038727 /s |
| Predicted energy ratio | 0.9962921299001846 |
| Injected measured energy ratio | 4.0 |
| Injected step algebraic residual | 1.0 |
| `stability_checks_passed` | **true** |
| `all_requested_cases_stable` | **true** |

This is evidence of an acceptance-logic defect, not observed energy growth at
alpha=48. The spectral calculation was unmodified; the step result was
deliberately invalid.

For an eigenmode with decay rate lambda, backward Euler predicts
`E_after/E_before = (1 + dt*lambda)^(-2)`. Whenever the independent step runs,
its finite values, algebraic residual, agreement with that prediction, and
absence of energy growth for a stable case must affect the aggregate decision.
Keep a skipped step explicitly marked as unexecuted; do not claim it passed.

For this bounded repair, use the existing `1e-9` algebraic-residual ceiling and
explicit dimensionless comparison tolerances `rtol=1e-9`, `atol=1e-12` for the
energy ratio. Allow at most `1e-12` above one in the non-growth check. These are
numerical self-consistency tolerances for this fixture, specified here for
review; they do not replace the physical pilot's 5%/5-degree criteria. Record
the tolerances and individual results. Do not loosen them if a real fixture
fails: return the evidence for further numerical review.

The negative-lambda regression should continue to demonstrate the known
failure. Agreement between its growing step and its eigenvalue prediction is
useful verification, while its scientific stability status remains false.

## 3. Small-fixture success still does not establish campaign readiness

Two remaining scientific limitations follow directly from the current code:

- `run_b2_gate` audits the fixed 100/70 mm fixtures, independently of the
  requested response meshes. It does not establish stability of the 50 mm
  swirl fixture or the 40/30/25 mm physical-pilot operators. Do not remove the
  dense size guard to try to obtain that evidence.
- The gate compares successive meshes, penalties, and feature quadratures,
  but never compares the physical `T_00c` gain with `disk_rotation_gain`.
  Thus its current `all_numerical_gates_passed` cannot establish agreement
  with the independent physical reference. Reference comparison in
  `b2-verify` uses deliberately changed viscosity/frequency and does not fill
  that gap. Absolute error floors and resolved phase remain to be assessed.

The next numerical-method review must address stability on the actual response
meshes and physical-reference accuracy before choosing an affordable refinement
strategy. The current formatter's successful disposition should describe the
checks it performed and retain these limitations, without inviting a campaign.
No campaign launcher exists in this gate, and none should be added here.

There is also a routine default mismatch: `run_b2_gate` defaults to alpha=6/12,
whereas its CLI wrapper defaults to 48/96. Align the gate API with those already
documented CLI candidates. This is not a universal penalty certificate; the
lower-level `harmonic_response` default and known-instability fixtures are
outside this repair.

## Evidence and reproduction scope

The real rejection command above reproduced:

| Mesh | alpha=6 minimum rate (/s) | alpha=48 minimum rate (/s) |
|---:|---:|---:|
| 100 mm | -0.08388458033713793 | +0.0018591066448038727 |
| 70 mm | -0.03417723621999698 | +0.0016873641839741 |

On the 70 mm mesh, the unmodified measured/predicted energy ratios were
1.072025523823309 / 1.0720255238233112 for alpha=6 and
0.996633794049131 / 0.9966337940491317 for alpha=48. Step algebraic residuals
were below `1.9e-15`. The two audits took about 4.20 s in total with a warm
cache; process peak RSS was about 759 MiB. These timings are not guarantees.

Mesh hashes match the previous review:

```text
100 mm: 97e8d99450223ab6d448dac3c484152b7590aa00ad5fa3fb3f8a4d3a8475ac78
 70 mm: 8d2ffd3d7e7f563035ee6099e54f7e602135d7c3f2d63d81d124bd6bf4d10e5a
```

The optional interpreter used was `/tmp/navier-fenicsx/bin/python`, with
DOLFINx/Basix/FFCx 0.10.0, UFL 2025.2.1, Gmsh 4.15.2, PETSc 3.25.5 real
float64, MPICH 5.0.1, NumPy 2.5.3, and SciPy 1.18.1. Portable environment
instructions remain in [B1_SETUP.md](B1_SETUP.md).

Machine-local evidence is in `/tmp/navier-b2-review-rejected-gate/gate.json`
and `/tmp/navier-b2-review-injected-step.json`. The latter explicitly labels
the injected fault. These temporary files are not required for implementation;
the command and fault description above specify the reproductions. The existing
`results/realizability/b2/gate.*` physical-pilot artifacts were not overwritten.

Source inspection also found incomplete report provenance: the source-hash
lists omit contributing modules such as `config.py`, `boundary_modes.py`, and
`observables.py`; the verification-fixture report omits runtime dependency
versions. The gate already embeds configuration/versions in its stability
subreport, so those are not wholly missing there. Complete provenance is a
separate routine follow-up, not evidence that the numerical gates pass.

## Handoff: cheaper model, bounded task, explicit stop

Switch to **GPT-5.6 Luna, medium reasoning**, for the implementation below.
This is a task-specific recommendation: [the official model page](https://developers.openai.com/api/docs/models/gpt-5.6-luna)
describes Luna as suited to cost-sensitive work and supports medium effort.

1. Read `AGENTS.md`, this review, and the implementation-results section of
   [B2_STABILITY_REVIEW.md](B2_STABILITY_REVIEW.md). Check `git status` and
   preserve the review documents and any other user changes.
2. Fix the rejected-report branch and align the gate API defaults with the
   existing CLI candidates. Make the successful report's limitations explicit
   as described above. Keep the physical-pilot aggregate's existing meaning;
   do not silently invent a new production-stability certificate.
3. Make executed backward-Euler checks contribute to the stability decision
   using the contract in section 2. Report separate spectral/step outcomes
   and explicit skipped-step status. Preserve strict JSON with `allow_nan=False`.
   Invalid diagnostic values must produce an explicit failed check and valid
   JSON, not be silently accepted or serialized as NaN/Infinity.
4. Add focused regressions. Test the early rejection and normal formatter
   branches without optional CFD dependencies; assert that rejection never
   calls `harmonic_response`. Cover matching API/CLI candidates and a
   synthetic report with completed gates. Test the energy-decision helper
   independently with correct decay, growth, wrong prediction, excessive
   residual, nonfinite values, and a skipped step. Clearly distinguish test
   doubles from PDE evidence. Retain the real known-unstable regression.
5. Run NumPy-only discovery and the optional B2 suite. Rerun the real rejection
   command above into a fresh temporary directory: both report formats must
   be written, the gate must remain false, and there must be no traceback or
   harmonic solve. Run a bounded real energy audit at 100/70 mm with alpha=6/48
   to verify the new step checks against the measurements above. Do not launch
   default `b2-gate` at 48/96, a production harmonic solve, or a new mesh sweep.
6. Append a concise implementation result here with changed files, commands,
   test counts/skips, and remaining limitations. Do not commit or push unless
   the user asks.

Suggested validation commands from the repository root:

```bash
python3 -W error -m unittest discover -s tests/realizability -v
/tmp/navier-fenicsx/bin/python -m unittest discover \
  -s tests/realizability -p 'test_b2*.py' -v
/tmp/navier-fenicsx/bin/python -m realizability.cli b2-stability \
  --config configs/realizability/pilot.json --mesh-sizes 0.10 0.07 \
  --penalty-factors 6 48 --output-dir /tmp/navier-b2-repair-stability
git diff --check
```

**Stop after this repair and its checks.** Do not continue into provenance
cleanup, production mesh/solver selection, the six-input campaign, B3, or
changes to physical assumptions, observables, or acceptance thresholds.
Recommend **GPT-6 Astra, high reasoning**, for reviewing the repaired evidence
and deciding how to verify the actual response operators and physical
reference agreement. Stop earlier and request that model if real numerical
results contradict this review or passing requires changing a scientific
assumption. Routine coding errors with an understood fix can be repaired
within this package.
