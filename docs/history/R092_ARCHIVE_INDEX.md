# R092 archive index

The accompanying `AGENTS_BEFORE_R092_IMPLEMENTATION.md` and
`SESSION_HANDOFF_BEFORE_R092_IMPLEMENTATION.md` are byte-for-byte snapshots of
the pre-edit repository-root files. Their relative links are interpreted from
the repository root where the originals lived, not from this directory. Live
documents link to their current destinations; do not edit the snapshots.

## Previous AGENTS headings → current location

| Original heading | Current location |
|---|---|
| Request recording and session continuity | [Session protocol](../workflow/SESSION_PROTOCOL.md) |
| Short continuation request | [Session protocol](../workflow/SESSION_PROTOCOL.md#short-continuation-request) |
| Switching between the Mac and PC | [Session protocol](../workflow/SESSION_PROTOCOL.md#switching-between-the-mac-and-pc) |
| Project purpose through physical-realizability research track | [Track rules](../workflow/TRACK_RULES.md) |

## Previous handoff headings → current location

| Original heading/content | Current location |
|---|---|
| Current session handoff, owner and current state | [Current handoff](../../SESSION_HANDOFF.md) |
| Next task and deferred R088 acceptance review | [R088 acceptance task](../../R088_ACCEPTANCE_REVIEW_TASK.md) |
| Historical R022/R033/R023/R024/R031/R034/R039/R046/R054/R047/R056/R055/R057/R053 records | [Pre-edit handoff snapshot](SESSION_HANDOFF_BEFORE_R092_IMPLEMENTATION.md); original headings and text retained there |
| Deferred Mac setup check and R035 publication setup | [Pre-edit handoff snapshot](SESSION_HANDOFF_BEFORE_R092_IMPLEMENTATION.md) |

Historical pages that still target `SESSION_HANDOFF.md#r023-resource-clarification`,
`#r053-machine-task-allocation-checkpoint` or `#r055-ffcx-version-discrepancy`
resolve to anchor stubs in the current handoff, which link back to the exact
archived sections. The current `#next-task` remains the sole live task anchor.

## Operative obligation map

| Obligation | Current rule location |
|---|---|
| Actual wording, sequential IDs, supplied excerpts, redaction, no private-session reads | [Session protocol: request recording](../workflow/SESSION_PROTOCOL.md#request-recording-and-session-continuity) |
| Clean fast-forward pull, dirty/unpublished work, stash preservation, same-owner resume | [Session protocol: Continue](../workflow/SESSION_PROTOCOL.md#short-continuation-request) |
| One owner, release/receipt, process cleanup, cross-machine visibility limits | [Session protocol: switching computers](../workflow/SESSION_PROTOCOL.md#switching-between-the-mac-and-pc) |
| Scoped user-authorized commit/push, lifecycle ordering, interruption and publication failure | [Session protocol: lifecycle and publication](../workflow/SESSION_PROTOCOL.md#request-recording-and-session-continuity) |
| Scientific distinctions, thresholds, budgets, evidence, default-deny physical work and validation | [Track rules](../workflow/TRACK_RULES.md) and the linked current task |
| Short request/completion records; no new startup automation or general helper framework | [Session protocol](../workflow/SESSION_PROTOCOL.md) and [R092 plan](../WORKFLOW_OVERHEAD_PLAN.md) |

The protocol was also walked through for same-owner metadata, clean and dirty
Continue starts, a receiving switch without release, interrupted same-owner
resume, failed start/final publication, and a new status addendum. In each case
the copied procedure retains its action and stop rule: metadata stays narrow;
clean Continue pulls and publishes STARTED; dirty state stops for reconciliation;
unreleased ownership stops dependent work; resume keeps the open record and
budget; failed publication stops or leaves transfer pending; supplied status is
recorded as an attributed addendum without invented facts.
