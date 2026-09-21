# R103 practical supervision policy

The user supports simplifying requirements that impose excessive implementation
cost or materially reduce reliability. This selects the practical direction of
[R101 option B](B2_MONITOR_MANAGER_CAPABILITY_DECISION.md#exact-policy-choice-for-user-review)
for documentation and future design. It authorizes no execution or publication.

The purpose is to prevent runaway calculations and reject incomplete results,
while keeping supervision small enough to implement and test. No live failure
rate has been measured. Difficulty proving a guarantee does not establish that
failures occur frequently, or that they are safely negligible.

## Keep the practical safeguards

- Preserve existing experiment time/memory limits and the independent mechanisms
  intended to stop task processes when the inner calculation or monitor hangs.
- Establish process ownership, containment and effective limits before releasing
  workload. Confirm Linux and Windows cleanup separately; an unknown survivor
  blocks another attempt. Never stop unrelated processes to simplify cleanup.
- Count setup, monitoring, failed attempts, cleanup and report saving in observed
  elapsed time. Keep the cumulative ledger; do not reset an allowance after a failure.
- Preserve source/run identity, actual exit status, available measurements and
  usable saved results. Missing, malformed, late or unconfirmed evidence cannot
  become a successful result. Keep partial evidence and explain the failure.
- Preserve numerical accuracy requirements and the disabled physical entry.
  A supervision improvement cannot turn failed B2 accuracy into scientific acceptance.

The future benign monitor suite still has a 180 s cumulative success ceiling:
30 setup + ten 12 s cases + 30 final reporting; each case keeps 5 active,
5 cleanup and 2 evidence seconds. Linux whole-unit limits remain 768 MiB,
no swap and 32 PIDs; sampled workload RSS remains 512 MiB. Native aggregate
working set remains <=128 MiB. Physical limits remain 180 s / 1536 MiB;
q64/q96 remain unused. None of these numbers grants an attempt.

## Replace excessive proof requirements

| Earlier requirement | Current policy |
|---|---|
| Manager-owned atomic reservation before all setup | A trusted launch/control path may reserve the attempt and record its start before task setup. It must preserve prior-attempt exclusion and conservatively retain an interrupted reservation. The OS manager need not implement an application ledger. |
| Independently enforce every part of manager setup and final bookkeeping | Enforce task-process limits; observe end-to-end setup, cleanup and saving time with ordinary trusted supervision. Do not claim an independent hard deadline for every infrastructure operation. |
| Manager-authenticated immutable Admission before creating any process identity | Reserve first, create held resources within the charged setup interval, bind their actual identities, then release workload. Freeze policy and ownership before release. No retroactive identity substitution. |
| Manager commits a durable certificate after the last observer exits, with its own bounded commit proved again | Accept independently observed process exits and successful ordinary persistence of validated results. Trust the finite launch/control path to report its observations. Do not recursively add another observer to certify that reporter's own final bookkeeping. |
| Attribute and enforce every task-specific byte/operation inside systemd, the message bus and journal | Keep all task-created processes in the declared measured/enforced scope. Disclose shared OS infrastructure costs as outside per-task attribution/enforcement. Elapsed waits for those services still consume observed time. |
| Whole-recorder certification as a prerequisite | Claim only the process limits actually enforced and the complete intervals actually observed. Label the trust assumptions and remaining gaps. Whole-recorder certification is not a goal of this policy. |

The finite trust boundary consists of the pre-existing OS services and the
explicitly identified launch/control path. This accepts ordinary software/OS
trust; it is not protection against a malicious owner falsifying its records.
Task-created guards, native launchers, recorders and validators remain task work,
even if placed outside the inner workload. Renaming one as infrastructure does
not exempt its resource use or lifetime.

## Timing, persistence and recovery

Use a consistent clock and record the observed interval from before setup through
the final result save and required exit/cleanup observations. A successful result
requires that interval to fit the unchanged ceiling. The report must distinguish
that observed interval from the scope of independent process enforcement.
The trusted caller's own last bookkeeping is explicitly outside recursive
certification; any unobserved tail must be disclosed, not reported as zero.

Use normal checked persistence and bounded waits where available. A save/query
that hangs, fails or finishes late produces an incomplete or failed run; it does
not justify a fresh budget or automatic retry. A missing completion record means
the attempt is unresolved. Later reconciliation may establish stopped processes,
recover evidence and charge known elapsed time without declaring the original
attempt successful. Unmeasured elapsed time remains unknown and its reservation
unavailable until deliberately reconciled. Necessary cleanup after expiry is
reported honestly; it does not extend the success ceiling.

We do not demand guaranteed successful disk persistence or OS recovery within a
deadline under every fault. Conversely, we do not waive an observed hang or
resource breach on the assumption that it is rare. Future bounded benign tests
must assess normal operation, injected failures and cleanup; report failures,
overhead and any nuisance stops without extrapolating a tiny sample into a
reliability guarantee. Do not add extra live trials without a new bounded scope.

## Compatibility and next step

### R104 Mac usability and incremental delivery

Mac usability is an explicit product requirement. Keep the user workflow and
result format shared where practical, with small platform-specific operations
only where needed. Do not make systemd, Linux cgroups or Windows helpers a
requirement of the common interface. Equivalent practical outcomes matter more
than identical mechanisms or measurements; disclose each platform's supported
checks and limits. Mac support remains unverified until checked on the Mac under
the normal ownership/handoff rules. No platform switch is implied here.

Infrastructure improvements must serve a named useful task. Each increment
should deliver the smallest necessary capability, test it meaningfully and
return to that task. Prefer existing tools and a small amount of explicit code;
add abstraction or new dependencies only to resolve a demonstrated need. Defer
general-purpose scheduling, dashboards, comprehensive benchmark matrices and
extra certification layers unless a concrete task requires them.

Each planning step must name the useful task that its proposed implementation
unblocks, include an early bounded Mac check in the delivery path, and list what
is deferred. Keep its output to a concise implementation checklist in the handoff;
do not create another standalone design contract or an open-ended sequence of
infrastructure reviews. A complete PC/Mac performance comparison is optional
later work, not a prerequisite for every useful calculation or visualization.
Refuse only tasks that lack their necessary safeguards; incomplete optional
features must not block unrelated work. Existing physical/numerical gates and
per-workload execution authorization remain in force.

This policy supersedes the stronger authority/accounting requirements in
[R099](B2_MONITOR_TRUSTED_ADAPTER_CONTRACT.md) and the current-choice refusal in
[R101](B2_MONITOR_MANAGER_CAPABILITY_DECISION.md) only as specified above.
Those documents and saved evidence remain historical and unchanged.
[R081](B2_MONITOR_LIVE_VALIDATION_CONTRACT.md#5-frozen-future-pc-suite) and
[R083](B2_MONITOR_R082_REVIEW.md#missing-harness-implementation-boundary) retain
their process containment, cleanup, cases, caps and observed accounting. Their
outer-boundary interpretation now follows this policy. R097's frozen fake
interface and historical charges are not retroactively upgraded or rewritten.

The former requirement for a manager-certified whole transaction no longer blocks
design work. This is not an assertion that the existing harness is implemented
or validated. R105 completed the small planning step and selected a portable
trajectory output checker as the first useful increment. It checks saved data
before rendering; it needs no changes to R097, OS adapters or runtime guarantees.
The [handoff](../../SESSION_HANDOFF.md#next-task) contains its file/check scope
and early Mac verification path. Practical process supervision and the full
PC/Mac benchmark remain deferred. The checker must not certify runtime safety
or physical correctness. No workload is launched by this policy document.
