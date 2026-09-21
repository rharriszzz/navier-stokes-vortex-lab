# R074 session-coordination review

Reviewed the R072 process change in commit `172cd70`, its first completed use
in R073 and the current R074 start. The underlying pull/start/completion
workflow is sound. Changes are confined to clarification and stale-task fixes.
This is a manual workflow review, not a simulated cross-machine lock test.

| Situation | Finding and final rule |
|---|---|
| Clean same-owner Continue | R074 ran the required flagged pull, checked HEAD/upstream equality, logged R074 and published STARTED as `6e85003` before substantive work. Retain this order. |
| Log-before-work general rule | The opening previously called receiving a handoff the sole pull-before-log exception, conflicting with every-Continue pull. Include both cases. |
| Incoming owner/start change | Recheck ownership/open records after pull before writes; clean local-only commits require reconciliation even if pull reports up to date. |
| Interrupted same-owner session | Log a new actual Continue request, link it to the open session and publish a RESUMED note; do not create a second STARTED or reset attempts. Automatic compaction creates neither. |
| Dirty/unpublished work | Reconcile deliberately within existing authorization before the clean pull. Do not erase, autostash, force or bypass an unpublished start. |
| Interrupted work | Append INTERRUPTED with checkpoints/processes; leave STARTED open instead of claiming completion. |
| Completion written before push | Describe prepared completion, with actual delivery reported after push. Failed/uncertain publication keeps transfer pending. |
| Retained PC owner | A completed `released: no` record reserves the next machine; the old task/agent still stops. |
| Explicit Continue without publication | User qualification governs the start and final publication steps too; local records remain, transfer is pending. |
| Append-only log | No edits after the successful final push in that turn; later requests may append. Preserve prior events byte-for-byte. |
| Stale next task | R073's completed outcome and handoff opening assigned adapter review, while the Next task section repeated R073. Replace it and align the opening/table; point current index pages to the handoff. |

The single-owner release checks, dirty-tree refusal, flagged fast-forward pull,
scoped commit/push authorization and no-force rule remain. Records cannot reveal
unpublished work or live processes on another machine. No remote Mac inspection,
background watcher, automation or model switch was performed.

Old R072/R073 request entries and session records retain their original wording.
In particular, R073's pre-push completion wording is historical; R074 clarifies
how future prepared-completion records should be written. R074 also documents
the limits of R073 resource accounting in the
[adapter review](../../B2_MONITOR_ADAPTER_REVIEW.md#findings-in-the-saved-implementations)
without editing its saved ledger or reports.
