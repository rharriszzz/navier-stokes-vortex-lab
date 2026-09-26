# Poiseuille source review and execution decision — R225

2026-09-25–26, PC/WSL `daisy`. **One tiny FEM test remains unadmitted;
zero FEM attempts granted or spent.** The review found and repaired a driver
state-size defect and several result-acceptance gaps. Forty-three standard-library
tests pass. A concrete Linux worker backend now exists, but its live completion
check failed, and it does not cover newly spawned control clients. The pinned
FEM environment is absent. These are explicit blockers, not numerical results.
Follow the single [next task](../../SESSION_HANDOFF.md#next-task).

## Formulation and corrections

The R195/R196 mathematical contract is retained: P2/P1 on an affine unit cube,
physical symmetric stress, conservative convection, exact lateral trace, two
independent z-return flux constraints, and the joint pressure gauge enforced
with eta. For plane Poiseuille, both return totals and pressure means are zero;
the spatially varying normal traction offsets remain necessary. The velocity
and pressure are exactly representable. The return surfaces are not no-slip
walls. Full pressure plus eta does not remove the need for compatibility and
an independent eta check. The three-row Gram condition is not a full mixed
operator inf-sup or stability certificate.

Source review confirms the positive return-pressure columns, all residual rows
retained during lift installation, zero constrained increments, conservative
return derivative, and both signed energy/divergence terms. The retained exact
rational tests check forcing, gauge, flux, physical stress and balances. The
[DOLFINx 0.10 mesh documentation](https://docs.fenicsproject.org/dolfinx/v0.10.0/python/generated/dolfinx.mesh.html)
was read for the affine facet geometry interface. No library call was executed;
UFL construction, compiled kernels, actual rank, PETSc LU, facet evaluation
and accuracy remain unverified.

Repairs in this increment:

- The driver supplied N mixed velocity/pressure values to an assembler requiring
  N+3 values. It now appends P-minus, P-plus and eta after assigning the mixed
  Function and reports both dimensions correctly. A regression executes the
  real driver/Newton path with fake FEM boundaries and requires a nonzero
  correction. This checks the connection, not FEM validity.
- Result validation now recomputes norms, budgets, degree-24/26 comparisons,
  nonlinear/linear decisions, compatibility and the three-row condition bound
  from recorded values. Cached true flags cannot hide altered raw terms,
  nonfinite data, missing corrections, absent scalar results or missing timing.
- The steady oracle now includes physical endpoint budgets. Exact initial
  kinetic energy is 4/15, angular momentum is -1/3 and viscous power is 8/15;
  rational-polynomial tests independently verify these constants. Trapezoidal
  transport/work with actual final inventories is separate from BE time-work.
  This establishes neither a time-convergence rate nor a physical experiment.
- A separate admission must bind one absolute run directory; changing directory
  cannot reuse that admission. An existing/interrupted directory stays reserved.
  Partial backend-start failures retain the handle for cleanup. Memory/PID
  limit events and a late final save beyond the 15-second finish interval refuse
  acceptance, even without an OOM kill or breach of the overall 180 seconds.

The manifest, thresholds, FEM pins and production B1/B2 sources are unchanged.
The stringent near-zero quadrature denominator is retained; no unobserved
roundoff behavior is grounds to relax it. A later launch/control path must
also verify that the supplied source identity actually describes the clean
executed checkout; recording a caller-supplied hash alone does not establish it.

## Concrete host evidence and remaining boundary

The host user manager reports systemd 249 running. The kernel exposes memory
and PID controllers. A first finite capability probe ran `/bin/sleep 0.5` under
64 MiB/no swap/4 tasks with a 5-second runtime setting and explicit cleanup.
The service reported active/exited with actual exit status zero, but its
ControlGroup was already empty. Thus RemainAfterExit retains the service record,
not the completed cgroup counters. Observed interval: 0.800626675 seconds.

The new `handshake.py`, `systemd_backend.py` and `probe_systemd.py` implement
atomic held/release and finished/exit messages. The worker waits before FEM
imports and again after saving its numerical report. The controller samples
kernel counters before acknowledging final exit. Those measurements explicitly
exclude the small final handshake/exit tail; the configured kernel limits
remain in force during it. Ordinary software/OS trust remains the R103 boundary.
This does not claim an exact final memory peak or recursive reporter certification.

One bounded benign backend case launched a standard-library worker, **not the
FEM worker**. It observed the actual matching cgroup and one held process,
1536 MiB memory.max, swap.max=0, pids.max=32 and the reported one-thread settings.
It correctly refused whole-task admission. After explicit benign release, the
worker completed its handshake, but the manager discarded its actual exit
record. The backend returned -1 and its stop query found the service unloaded.
The probe failed and stopped; the planned independent-expiry case never ran.
Observed interval to that failure: 0.173068943 seconds. The later manual
cleanup reconciliation was outside this timer; the complete start-through-
reconciliation interval is unknown, not zero or a claimed 30-second success.
Raw failure evidence is
[retained](evidence/r225/host_probe_failed.json), without relabelling it a pass.

Read-only reconciliation confirmed the exact unit not-found/inactive, MainPID=0,
empty ControlGroup, absent cgroup directory and absent worker PID 121650. No
unknown survivor or task process remains. Source now uses RemainAfterExit and
recognizes active/exited as a terminal process state; it also handles a confirmed
unloaded service during cleanup and systemd's `2min 29s` duration format. Mocked
regressions pass. **The corrected live path and independent expiry have not been
retested.** No automatic retry or additional live case was launched.

This backend deliberately reports `all_task_processes_in_scope=False` because
its short `systemctl`/`systemd-run` children execute in the caller's scope.
They are newly spawned task work, not shared OS services. The finite trusted
caller and pre-existing manager are distinguished from those clients. Do not
exempt the clients by relabelling them as infrastructure. The current controller
therefore refuses this backend before any FEM release. Closing that boundary
requires a small concrete change, such as an encompassing capped task scope or
an in-process manager interface, followed by an actual bounded check.
No general scheduler, cross-platform monitor or R021 machinery is needed.

Default worker expiry is configured as 149 seconds plus at most one second
stop grace, under the existing 150-second worker ceiling; setup/finish and
whole-task 180-second limits remain. The benign worker used a shorter runtime.
Configured expiry is not demonstrated expiry. Installed systemd 249 service and
resource-control manuals were inspected for Type=exec, RuntimeMaxSec,
TimeoutStopSec, MemorySwapMax and TasksMax; online systemd manual fetches failed.

## Evidence and decision

[Check record](evidence/r225/checks.json): 43 tests pass under project Python
3.12.14, including existing analytical/sparse tests, the stitched driver path,
corrupted numerical records, atomic messages, retained exits, partial-start
cleanup, cap-event refusals and late completion saving. No NumPy, DOLFINx,
Basix, UFL, FFCx, PETSc or MPI modules were imported. An initial `unittest discover`
invocation failed because this is a namespace package; explicit module loading
ran all five test modules successfully. Syntax, links, log preservation and
whitespace are checked before publication. These are not live/FEM pass claims.

**Admission refused for one standalone n=2 Poiseuille test.** No admission file
is issued; the frozen non-executable manifest remains unchanged. Required:

1. Whole-task coverage for the newly spawned control clients and verified clean
   source/interpreter binding at the actual launch boundary.
2. A bounded successful check of the corrected exit/counter path and independent
   expiry/descendant cleanup, preserving this failed check's evidence and charge.
3. Availability and validation of the exact pinned Python 3.12.13 FEM stack.
   `/tmp/navier-fenicsx` is absent; the visualization Python 3.12.14 is not a
   substitute. No dependency installation or FEM import was attempted here.

Next complete the finite whole-task launcher and its two benign checks, stopping
before dependencies or FEM execution. A fresh bounded diagnostic allocation must
be stated before those cases; R225's two observed probe intervals remain in the
ledger. Resolve source binding in that same launcher. Record the pinned-environment
restoration as the subsequent prerequisite once the launcher works. Preserve
180 seconds/1536 MiB/no swap/32 tasks and no automatic retries. Early Mac work
is portable algebra only after normal ownership handoff; no transfer now.

Retain Astra/high on PC/WSL daisy while the containment boundary needs review.
[OpenAI Docs](https://developers.openai.com/api/docs/models/gpt-6-astra) was
searched/opened and confirms high support; model fit is judgment. Recommend
Sol/high only when the remaining work is mechanical, after rechecking availability.
No model switch, delegation, tank, physical/optical, rendering or production
solver work occurred. B2 accuracy remains failed, q64/q96 unused and R021 deferred.
