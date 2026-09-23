# Single Poiseuille driver and finite supervision source — R222

2026-09-22; owner PC/WSL `daisy`. This increment joins the existing R195/R196
source for **one n=2 plane Poiseuille oracle** and adds finite task-specific
reservation, worker and result handling. Thirty-three standard-library tests
pass. The test result is an import-free source check; no FEM package was
imported, no UFL form/JIT/mesh/assembly/solve or scope was launched, and no
numerical convergence or runtime cost has been measured. Follow the single
[next task](../../SESSION_HANDOFF.md#next-task).

## Driver and numerical gate

[`fixture_driver.py`](../../verification/nonlinear_port/fixture_driver.py)
creates the frozen affine n=2 tetrahedral cube through the existing adapter,
retains exact historical velocity, installs the current lateral trace and
perturbs one **free velocity DOF**. It rejects a missing free DOF or changed
trace. It assembles all raw constraint rows, removes fixed columns for the
three-row Gram condition bound, and obtains the lateral and return
compatibility terms from degree-24 boundary integration. It freezes row scales
once, runs the bounded Newton kernel with sparse LU, retains each true linear
residual and requires at least one checked correction.

After convergence, the driver assembles all R196 field diagnostics at degrees
24 and 26, compares their raw inventories with the frozen relative rule,
and evaluates numerical normal velocity at triangle quadrature points on
**both tagged returns**. The Poiseuille decision checks u/p errors <=1e-9,
divergence and traction at the same oracle scale, separate multiplier errors,
flux/gauge/eta, backflow, energy identity and both signed budgets. The driver
returns `numerical_accepted`; it never accepts a process or the n=2/4/8 suite.
Installed library behavior, exact facet mapping, actual assembled rank and
finite-element error are still untested. An apparent import-free numerical pass
cannot substitute for a later tiny execution and critical review.

## Worker, reservation and supervision

[`worker.py`](../../verification/nonlinear_port/worker.py) is the held worker
source. It compares the exclusive reservation, separate admission and manifest
hash; reports its own cgroup path; waits for a matching release nonce and
cgroup identity; checks one-thread environment; and only then imports the
frozen Python/FEM stack. It records actual versions and phase intervals with
the numerical payload. There is no standalone unsupervised launch path.

[`supervision.py`](../../verification/nonlinear_port/supervision.py) reserves a
new directory before setup, binds source commit, manifest hash, interpreter,
owner and monotonic start, and refuses an existing reservation. An injected
host backend must create a held scope and report **effective** memory <=1536
MiB, swap 0, PIDs <=32, one rank/thread, independent expiry <=150 s and the
actual non-root cgroup identity before release. The controller observes a
15 s setup, <=150 s managed worker and <=15 s cleanup/reporting subdivision
inside the unchanged 180 s total. It checks exit, complete numerical payload,
cgroup memory peak/events, PID peak and confirmed empty cleanup. It persists
reservation, admission, worker result, result/log and a separate completion
record. Missing, failed, late or unknown evidence produces an incomplete
record. A provisional result file alone cannot pass; completion and absence
of a late marker are required. The final completion-save tail is disclosed
under the R103 ordinary-software trust boundary, not recursively certified.

This source has **no live host backend**. The mocked backend tests exercise
release/refusal, missing numerical result, failed exit, overlong worker,
unknown cleanup and duplicate reservation. They do not establish cgroup
containment, independent expiry, cleanup or real success. The worker has never
been started.

## Read-only host observation and admission decision

The restricted namespace showed `/proc/1/comm=codex`,
`/proc/self/cgroup=0::/`, and no visible root `memory.max`/`pids.max` files.
Its `systemctl --user is-system-running` failed with `Operation not permitted`.
The authorized outside-sandbox read-only check reported the user systemd
manager **running**, with manager control group
`/user.slice/user-1000.slice/user@1000.service`. This establishes that a user
manager is reachable there; it does **not** verify that a held task scope can
be created, enforce the proposed limits, retain memory/PID observations or
clean up every child. No systemd unit or cgroup was created or changed.

**Execution decision: not admitted; attempts granted remain zero.** The
manifest stays non-executable and unchanged. A later review must supply and
audit a concrete host backend, reconcile the pinned 3.12.13 FEM environment
(not available at its earlier `/tmp/navier-fenicsx` path here), check source
and method issues, and decide explicitly whether to grant **one standalone
tiny fixture**. If any safeguard is missing, refuse that launch. Do not infer
admission of the full convergence suite, retry, tank/controller, physical
apparatus or production B1/B2. B2 accuracy remains failed; q64/q96 unused;
R021 integration deferred. No scientific tolerance, cap or dependency pin was
changed.

## Checks and next review

The three standard-library test groups passed 33 checks under project Python
3.12.14, including existing exact oracles, sparse lifting/rank, budgets and
new mocked driver/supervisor refusal paths. `git diff --check` passed.
The pinned FEM interpreter and libraries were absent at the previously
recorded temporary path; no install or runtime attempt was made. The official
[DOLFINx 0.10 Function evaluation](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.fem.html),
[mesh geometry](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.mesh.html)
and [Basix 0.10 quadrature](https://docs.fenicsproject.org/basix/v0.10.0.post0/python/_autosummary/basix.html)
interfaces were read for source design; they do not validate this adapter.

Next: GPT-6 Astra/high on this PC critically review the assembled formulation,
driver, worker, persistence and scope backend contract; implement/verify the
smallest concrete host backend only if its effective limits and held worker
can be established without a FEM launch. End with an explicit single-attempt
admission or refusal and no actual FEM execution. Recommend Sol/high for later
mechanical fixes after the science/assurance questions settle; recheck current
availability then. PC retains ownership.
