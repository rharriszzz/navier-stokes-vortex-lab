# R226 — Whole-task launcher and benign host validation

The finite Linux launcher now covers newly spawned task processes under the
R103 trust boundary. The clean-exit and independent-expiry checks both passed
in **5.418188160 seconds** through the final summary save. **FEM remains
unadmitted, with zero attempts**: the exact pinned environment is absent and
actual numerical behavior remains unmeasured. This completes the R225 launcher
prerequisite, not the Poiseuille numerical verification.

## Source and trust boundary

`systemd_bus.py` calls installed libsystemd through fixed ctypes signatures.
It connects directly to the existing user's private manager socket, verifies
peer credentials, frees reply/error objects and applies finite call timeouts.
There is no spawned systemctl, systemd-run, guard or reporter. The finite outer
caller and existing OS manager are explicitly the ordinary trusted control
path accepted by [R103](B2_MONITOR_PRACTICAL_SUPERVISION_POLICY.md). Their memory
and OS service costs are not claimed as cgroup measurements; elapsed waits for
the manager are included. No recursive observer or broader platform rewrite.

The held worker, its source-check Git children, and all subsequent workload/JIT
children inherit the service cgroup. Before release, `source_binding.py` verifies
the actual clean checkout against the reserved commit, working directory and
interpreter. The controller compares the observed binding, including the actual
resolved executable's SHA-256, to its pre-start expectation. The owner must keep
the checkout unchanged during execution; this is not hostile-writer protection.
Actual package/library versions remain a separate worker gate after admission.

Effective observed limits are 1,610,612,736 bytes memory (1536 MiB), no swap,
32 tasks and one held worker with one-thread environment settings. The default
numerical unit still requests 149 s runtime plus 1 s stop grace; the existing
180 s observed total / 15 s setup / 150 s work / 15 s finish caps are unchanged.
This task exercised shorter independent expiry, not a 150-second runtime test.

Systemd retains the actual exit record with RemainAfterExit. A completed worker
waits while the caller saves available kernel counters, then actually exits.
Stop waits for an observed stopped/empty unit, not merely an accepted stop job.
The peak/counter snapshot excludes the final handshake/exit tail; kernel limits
remain active through that tail. There is no claim of an exact final peak.

Primary implementation references read: systemd v249's
[sd-bus ABI](https://raw.githubusercontent.com/systemd/systemd/v249/src/systemd/sd-bus.h),
[direct user-manager connection](https://raw.githubusercontent.com/systemd/systemd/v249/src/shared/bus-util.c)
and [transient execution properties](https://raw.githubusercontent.com/systemd/systemd/v249/src/core/dbus-execute.c).
The first read-only session-bus attempt failed: sandbox EPERM, then the host's
session-bus socket was absent. The existing private socket worked and reported
systemd 249.11-0ubuntu3.22; neither connection check started a unit.

## Bounded live evidence

R226 STARTED was published as dd27c10 after the required clean pull of dc3cadd.
An intermediate source/allocation checkpoint was published as
`b07dbdc68ba46659a4548786278fc46a5210bc13`, and both workers independently verified
that exact clean revision. No behavioral source changed after that live check.
The [check record](evidence/r226/checks.json) binds source and retained artifacts.

The allocation was recorded before launch: one clean case (8+1 s expiry), then
one expiry case (4+1 s), at most 30 s observed cumulative setup/work/cleanup/save,
no retries on unexpected failure. The output directory was exclusively created
at `/tmp/navier-r226-host-probe-01`. All runtime messages and the
[summary](evidence/r226/host_probe/summary.json) are preserved in the repository.

| Case | Observed result |
|---|---|
| Clean | Actual exit 0 / manager success, then empty removed cgroup. Snapshot: 40,218,624 bytes memory peak, 5 tasks peak including contained source checks, zero max/OOM/PID-limit events. |
| Expiry | Worker and child both ignored SIGTERM. The child published readiness only after installing its handler. Both were observed in the same cgroup. Without a controller stop, the manager reported timeout, signal 9, MainPID 0 and empty ControlGroup. |
| Cleanup | Both groups absent, unknown_children=false. The failed expiry unit retains inert failure metadata; no live process remains. Later read-only check also found worker PIDs 124284/124291 and child 124298 absent. |

The probe timer starts before directory/reservation setup. Cumulative interval
through clean cleanup before its record save: 0.228508770 s; through expiry
cleanup before its record save: 5.409311383 s. The persisted summary observes
5.415262515 s before saving itself; stdout observes **5.418188160 s after its
save**. Final stdout/return and later repository evidence copying are outside
that measured interval, not asserted to take zero time. The finite caller's
last bookkeeping follows R103. The expiry case has no completion snapshot and
claims no peak measurement. It is an expected timeout check, never a numerical
success record.

R225's failed evidence and charges are unchanged: 0.800626675 s capability probe,
0.173068943 s to failed exit-metadata collection, and unknown total elapsed
through later manual reconciliation. R226 is a separately declared benign
allocation, not a retry that erases those observations.

## Checks and remaining execution decision

49 standard-library tests pass across six modules; no NumPy, DOLFINx, Basix,
UFL, FFCx, PETSc or MPI modules were imported. New regressions cover exact
source/interpreter binding, dirty/untracked/wrong source refusal, failed Git
checks, precise missing-unit versus connection-error treatment, asynchronous
stop completion and sd-bus error cleanup. Existing driver/acceptance, scope,
resource-event and late-save tests remain passing. All 21 Python files parse.
Live tests additionally exercise real D-Bus encoding and retained exit behavior.
A two-case benign sample is not a reliability estimate or a FEM result.

`/tmp/navier-fenicsx` is absent. Project Python 3.12.14 cannot substitute for the
frozen Python 3.12.13 environment. No packages were installed and no FEM import,
JIT, mesh, assembly or solve ran. Production sources, environment pins,
future_fem.json, numerical gates and R225 evidence are unchanged. B2 remains
failed, q64/q96 unused, R021 deferred. PC/WSL daisy retains ownership; no Mac
transfer, model/session switch or delegation occurred.

Next: restore the exact environment and verify its package metadata/interpreter,
without FEM imports or numerical execution. Follow the single
[handoff task](../../SESSION_HANDOFF.md#next-task). GPT-6 Sol/high is the
recommended implementation model now that this containment choice is settled.
[Official OpenAI documentation](https://developers.openai.com/api/docs/models/gpt-6-sol)
was searched and opened on 2026-09-26 and confirms its coding role/high setting;
this task-fit choice is judgment, not a check of account-specific access. Return
to Astra/high for a scientific/pin/containment policy decision or the later
explicit single-fixture admission; do not alter the frozen contract to make an
environment install succeed.
