# Lower-overhead workflow plan — R092

Planning is complete; implementation is assigned to a future **GPT-5.6 Luna,
medium reasoning** session on PC/WSL `daisy`. No agent has been launched or
model switched. The user reports a reset; the subsequent supplied snapshot
shows main 5h/weekly limits at 100%, 283 credits, and Luna Reserve still at 1%.
These are snapshots, not guaranteed capacity for the next task.

## Problem and target

At planning start, `wc -w` measured AGENTS.md at 3,409 words,
SESSION_HANDOFF.md at 7,195, REQUEST_LOG.md at 37,016, WORK_SESSIONS.md at
2,888, STATUS.md at 4,014, and PROJECT_TRACKS.md at 1,482. These are file
sizes, not measured billed tokens. Broad reads of historical text, repeated
summaries and bespoke documentation checks add avoidable work. The latest
status reports 94.4K context used even in this metadata/planning session.

Reduce the default AGENTS plus handoff reading from about 10,600 words to
**at most 2,800 words combined**: root AGENTS target 1,600; current handoff
target 1,200. Extra instructions remain mandatory when their task applies.
This is a reproducible text-size target, not a promised quota saving.

## One bounded documentation implementation

1. **Separate current state from history.** Copy the entire pre-edit handoff
   byte-for-byte into `docs/history/SESSION_HANDOFF_BEFORE_R092_IMPLEMENTATION.md`.
   Rewrite the current handoff around identity/ownership, pending delivery,
   latest scientific result and limitations, required input/evidence links,
   consumed budgets, one next task, checks and stopping conditions. Preserve
   the deferred R088 acceptance task verbatim in a linked task document.
   Move historical incoming fragment links to the archived headings. Keep the
   snapshot bytes intact: its original relative links are interpreted from the
   original repository-root location, documented in a companion archive index.
   Resolve relocated links in live documents, not by rewriting the snapshot.
   Do not delete history to meet the target.
   If an immutable evidence file links to an old handoff fragment, retain a
   short anchor/link stub in the current handoff instead of editing evidence.

2. **Make instructions conditional on task.** Preserve a byte-identical
   pre-edit AGENTS snapshot in `docs/history/AGENTS_BEFORE_R092_IMPLEMENTATION.md`.
   Keep concise universal rules and explicit routing in root AGENTS. Put the
   full Continue/transfer procedure in `docs/workflow/SESSION_PROTOCOL.md`,
   required before every Continue or receiving handoff; put trajectory,
   rendering, encoding and realizability requirements in
   `docs/workflow/TRACK_RULES.md`, required before relevant work. Metadata
   requests read only current ownership, relevant latest entries and the
   supplied text; they do not trigger research-document reads. Keep identity,
   owner-mismatch detection, dirty-tree protection and redaction universal.
   Produce a short old-heading → new-location map. Consolidation must retain
   every operative obligation, including user authorization and exceptions.
   Instructions pasted into an already-open conversation will still occupy
   that conversation; benefit from the smaller files is mainly in future starts.

3. **Read narrow slices once.** At a fresh session run identity/status checks
   once, then read the compact handoff, last three request entries and any
   referenced open lifecycle/request entry. Find maximum request ID across all
   headings (entries can be out of order); never infer it from the last entry.
   Read older material only through a specific reference needed for the task.
   Reuse reads during the same session; refresh after pull, actual changes,
   new owner information or a new launch requiring live capacity. Read-only
   shell commands may process whole files to return compact results. Avoid
   sending whole history files to the model. No new startup automation needed.

4. **Keep future records short.** Existing REQUEST_LOG.md and WORK_SESSIONS.md
   remain append-only and in place. Routine request entries target 150 words
   or less excluding supplied excerpts; record wording, scope, outcome,
   checks/skips, files, ownership and next task. Longer records are justified
   for new scientific decisions or failures. Continue still publishes STARTED
   before substantive work and COMPLETED before final delivery; mandatory
   fields stay present. Put detailed results in one task document and link to
   it from logs/status instead of reproducing them. Same-session status pastes
   are addenda when they supply the requested context, not invented new tasks.

5. **Validate to match the change.** Routine metadata edits need a diff,
   redaction/attribution check and whitespace check. Moved docs additionally
   need changed-link/fragment checks. Scientific/code changes retain all
   applicable prescribed tests and evidence bindings. Run each relevant check
   once after edits settle; rerun only after a relevant change or failure.
   Do not execute archived fixture/recorder mains to validate documentation.
   Do not introduce a general workflow framework, helper daemon, generated
   evidence bundle or standalone test suite for this documentation task.

6. **Route models deliberately.** Use Luna/medium for metadata, documentation
   and settled mechanical tasks. Use Astra/high for the preserved acceptance
   review, scientific interpretation or unresolved contract decisions. Both
   are in the current session catalog; R090 opened official pricing/model
   guidance. Recheck availability at implementation start. Do not change
   models or speed settings automatically. Do not infer that 1% Luna Reserve
   means the fresh main allowance is unavailable; verify with actual UI if
   there is a capacity refusal.

## Safeguards and validation

The implementation must preserve, without relaxing:

- Every-request logging, actual supplied text/redaction/session attribution,
  no private-session reads, and no invented usage or output.
- Clean fast-forward synchronization, explicit dirty/unpublished reconciliation,
  no reset/rebase/autostash/force, stash preservation and same-owner resume.
- Single writing owner, release/receipt and process cleanup, no inference that
  local Git proves remote inactivity, and no reset of once-only attempt budgets.
- Authorized scoped commit/push, start-before-work publication, separate
  completion/delivery, interruption semantics and no post-delivery log edit.
- All scientific distinctions, thresholds, resource caps, default-deny physical
  execution, evidence provenance and task-specific testing requirements.

Before changing docs, record the baseline commit and scoped dirty inventory;
preserve all prior pending metadata. At completion check snapshot byte equality,
both append-only log prefixes, maximum/unique request IDs, moved/current links
and required anchors, and a heading-to-obligation mapping for the rules above.
Check the Git diff contains only planned documentation and coordination files;
source, pins and historical evidence must have no changes. Count words and
report before/after. Use standard-library Python 3.12 and existing tools;
keep any temporary checking script local rather than creating another framework.

Walk through these cases as a documentation review: same-owner metadata;
clean Continue; dirty Continue; receiving switch without release; interrupted
same-owner resume; failed start/final publication; new status addendum. Each
must retain the original required action and stop condition. This is a semantic
review of instructions, not an OS/research experiment or claimed automated proof.

## Delivery, next task and stop

This planning request authorizes no publication. On the next user **Continue**,
first inspect the known R089–R092 pending documentation and upstream state.
Use that new authorization to reconcile and publish the scoped pending plan
and metadata before the clean-pull/new-ID/STARTED sequence. If incoming changes
conflict or authorization is qualified, follow the existing protocol; never
pull over these edits or manufacture a clean start. Do not publish them now.

Luna completes the six documentation changes and listed checks, records a short
outcome with measured word counts, restores the preserved Astra/high R088
acceptance review as the single next task, and delivers under that session's
authorization. Stop after this documentation task; do not begin the review.
Stop earlier for missing historical content, an unresolved semantic rule change,
ownership/publication conflict or an unmet safety requirement. If a size target
conflicts with preserving a rule, retain the rule and report the target miss.
Recommend Astra/high only for a concrete unresolved semantics/scientific issue
or the already-pending research review; no extra Astra audit of this mechanical
cleanup is required when the stated checks pass.
