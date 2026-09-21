# Session protocol

Read this document before every Continue session or receiving-computer handoff. Root [AGENTS.md](../../AGENTS.md) remains the concise universal entry point.

## Request recording and session continuity

For every new user request in this repository, including follow-up corrections,
append an entry to `REQUEST_LOG.md` before substantive work. Use a sequential
ID, date, the user's wording, interpreted scope, and status. Preserve previous
entries; append dated outcome/validation notes rather than rewriting the request.
Record only requests actually available in the conversation. Context blocks and
automatic continuation messages are not new user requests. Redact credentials
or other secrets and label the redaction; do not copy private session files.

R088's user-supplied session reporting order is: preserve the final “worked for”
message, then `/new`, then `/status`, and send those excerpts for recording.
Record the supplied text with session attribution; the completion message may
belong to the old session while the later status belongs to the new one. Treat
values as user-reported snapshots, redact account details/secrets, and explicitly
note missing excerpts. Do not infer command output or read private session files.

At every session start, perform the read-only machine/ownership checks below
before repository writes or workload execution. For every Continue start and
receiving-computer handoff, perform ownership/status checks and clean
fast-forward synchronization **before** allocating an ID or editing the log.
This ordering exception prevents the log itself from dirtying the checkout
before the pull. If synchronization is blocked, retain the request in the
conversation until shared history is reconciled; do not invent a globally
unique ID from an outdated checkout.

At session start, read `SESSION_HANDOFF.md` and the latest request entries.
Follow its current task and read the linked research documents before acting.
A new user request takes precedence over a stale handoff. Keep a bounded plan,
completion criteria, and explicit stopping conditions. At completion, record
changed files, checks and skips, evidence paths, unresolved decisions, and the
next task in the log and handoff. Keep the handoff opening, owner table and
`Next task` section consistent; completed request/session outcomes take
precedence over a stale task recommendation. Current status/index pages should
link to that single task instead of retaining a competing execution request.
Do not claim an unexecuted check passed.
On compaction/resume, continue the existing entry rather than duplicating it.
The request log is history; do not replay completed requests as new assignments.

When the remaining task becomes routine, recommend a concrete available model
and reasoning effort. Give it an actionable task, checks, a stop condition,
and a rule for recommending the following model/effort. Routine execution is
usually suitable for GPT-5.6 Luna with medium reasoning; numerical-method or
scientific interpretation usually warrants GPT-6 Astra with high reasoning.
Recheck current availability when making the recommendation. Do not claim a
model switch occurred unless it did. A written handoff does not launch another
session or schedule an automation. See `SESSION_HANDOFF.md` for the reusable
continuation request and current recommendation.

Commit/push authorization must come from the user, including the short
continuation request defined below. Record its scope and honor it without
asking again; logging alone does not authorize every future push.

For every `Continue` session, also use the append-only `WORK_SESSIONS.md`
coordination log. After the clean fast-forward pull and request-log entry,
append a `STARTED` record with the request ID, UTC time, human machine label,
hostname/OS/architecture, checkout path, branch/upstream, starting commit and
bounded task. Commit and push this start record before substantive work. If
that publication fails, stop before the task. At task completion, append a
matching `COMPLETED` record with the UTC end time, outcome, changed files,
checks/skips, evidence, next task and release state before staging the scoped
task changes and making the final commit/push. Do not edit the log again in that
completed turn after a successful push; later requests may append new events.
Report the delivery commit in the final response because a commit cannot
contain its own hash. If the same request already has an open `STARTED` record,
resume it rather than adding a duplicate. An open record on another owner
requires the existing handoff/release procedure. These committed records help
coordinate owners but are not a lock and cannot reveal another checkout's
unpublished work or live processes.

Record task completion separately from delivery: a completion prepared before
push must not claim that push has succeeded. A failed/uncertain push leaves
transfer pending and the owner responsible for reconciliation, even if a
COMPLETED event is already committed. Do not mark an interrupted task COMPLETED;
append an INTERRUPTED note with checkpoints/process state and keep its STARTED
record open. `released: no` on a completed task retains the machine as next
owner; it does not mean the old agent should continue running.

## Short continuation request

When the user says **Continue** as a task instruction in this repository
(ignoring capitalization and trailing punctuation), apply this full workflow.
This shorthand replaces the long prompt at the user's request, R003 in
`REQUEST_LOG.md`; it includes authorization to commit and push the scoped work.

1. Perform the read-only identity, ownership, Git status/branch/upstream and
   stash checks. Read `SESSION_HANDOFF.md`, the latest request entries and any
   open `WORK_SESSIONS.md` record. Do not pull over staged, unstaged or
   untracked work; inspect/fetch upstream read-only if needed, then stop to
   reconcile local work deliberately. On a clean intended branch, always run
   `git pull --ff-only --no-rebase --no-autostash` against its configured
   upstream, for same-owner continuations as well as receiving handoffs. If it
   fails, conflicts, or histories diverge, stop and reconcile explicitly; do
   not reset, rebase, force, or enable autostash. Review incoming commits and
   reread the updated handoff/log, and recheck ownership/open records against
   the pulled history before writes. Confirm HEAD equals the fetched upstream;
   clean local-only commits still require deliberate reconciliation. Then
   append the actual user request to `REQUEST_LOG.md`, identify the bounded
   task, and append/commit/push its
   `STARTED` record in `WORK_SESSIONS.md` before substantive work. Resume an
   unfinished same-owner task rather than starting the next listed task. A
   new user Continue still gets a request entry, linked to the existing open
   session; append a RESUMED note under that session and publish the note before
   substantive work, without a duplicate STARTED or reset experiment budget.
   Compaction/automatic resume adds no request or lifecycle event. Existing
   dirty work or unpublished commits must first be deliberately reconciled
   within their authorization; never pull over them or log a fresh start to
   bypass a pending start/completion publication.
2. Carry out that task and its prescribed checks through completion. Preserve
   user work, scientific assumptions, acceptance thresholds, and recorded stop
   conditions. Fix understood implementation errors within the task's scope.
3. At completion or a research-decision boundary, record evidence, changed
   files, checks/skips, and unresolved questions. Update the request log,
   relevant Markdown, `SESSION_HANDOFF.md`, and the matching completion entry
   in `WORK_SESSIONS.md` with one concrete next task, model/effort
   recommendation, completion criteria, stopping conditions, and owner release
   state. Explain when the next model should recommend a different
   model/effort. Append the completion entry before final staging/commit/push.
4. Stage only the task's changes, commit, and push to the current branch's
   configured upstream. Honor this authorization without asking the user to
   repeat it. Preserve unrelated changes and Git history; do not force-push.
   Report any actual permission, remote, or publication blocker accurately.
   Do not make a post-push log edit.
5. Stop at the bounded task's recorded stopping point. Report the result,
   checks, commit/push outcome, and recommended next model/effort concisely.
   Give **Continue** as the next prompt instead of another long instruction.

An explicit qualification in the user's message overrides the default workflow
(for example, “Continue without pushing”). Quoted examples and mentions of the
word in a question do not invoke it. The shorthand does not itself change the
selected model or schedule another session.
If publication is explicitly excluded, retain local lifecycle records and
honor the excluded commit/push steps; mark transfer pending and keep ownership
on this machine. The mandatory start-publication rule does not override that
user qualification.

## Switching between the Mac and PC

Treat a computer switch as a handoff between task owners. Default to **one
active writing/execution session for this repository across both machines**:
even separate tasks share `REQUEST_LOG.md` and `SESSION_HANDOFF.md`. A clean
checkout or successful pull does not prove the other session has stopped.
Establish release from the outgoing handoff and any current user clarification;
record receipt on the new owner before substantive work. These records are
coordination notes, not an automatic lock or a remote process check.

An independent user-managed software build outside the shared project files
(for example, POV-Ray installation on the Mac) may continue while the PC owns
the repository review. Record it as ongoing and distinguish it from this task's
processes. It does not itself transfer repository ownership or require a machine
switch; do not stop or restart it without an applicable user instruction.

### Catch an unannounced switch

At each session start, even when the user does not mention switching, read the
current OS/architecture, hostname and checkout path (for example with Python's
`platform.system()`, `platform.machine()`, `platform.node()` and `Path.cwd()`).
Compare them with the outgoing/current owner and intended receiving machine in
`SESSION_HANDOFF.md`. Use a human label such as Mac or PC/WSL plus those local
identity fields; a changed checkout path alone can be a second checkout on the
same machine. Inspect Git status, branch/upstream and pending transfer records.
If the local handoff may be stale, fetch the configured upstream and inspect
its committed handoff/log before deciding that ownership is uncertain; this
updates remote-tracking refs without merging into the working tree. Do not
apply incoming changes over local work. A failed fetch leaves freshness unknown.

A machine/owner mismatch, absent identity, incomplete release or conflicting
task record is a **possible unannounced switch**. Say what was detected before
edits, request-ID allocation, package changes or workload launches. If the
record already establishes release and transfer, proceed with receiving checks
without asking again. Otherwise ask the user to confirm the former session and
task processes have stopped and whether unpublished changes/results remain.
Keep dependent work stopped until that uncertainty is resolved; read-only
inspection can continue. Reconcile any undelivered work before claiming ownership.

Local Git and a successful pull cannot see another machine's dirty worktree,
unpublished commits or live agents/processes. Do not claim guaranteed detection
or silently inspect the other machine. This is a check when a session starts,
not a background watcher. If the same hostname/owner record is stale, a switch
may still require the user's clarification.

At the end of a bounded step on the sending computer:

1. Finish or safely stop this task's child processes, including detached
   render/compiler/MPI workers, and record the cleanup result. End the old
   agent's task; do not leave it continuing edits after handoff. Record the
   request, outgoing machine, intended receiving machine, ownership/release
   state, branch/upstream, source commit, changed files, checks/skips, evidence,
   and one next task with model/effort, completion criteria and stopping condition
   in `REQUEST_LOG.md` and `SESSION_HANDOFF.md`. For an interrupted run, record
   consumed attempts/budgets and partial results; switching never resets a
   once-only attempt allowance or authorizes retry after a stop.
2. Keep large generated outputs and machine-specific environments local. Put
   only the small evidence needed to interpret a result in the repository;
   never transfer compiled binaries or JIT caches between macOS and Linux.
   List any ignored/untracked input required by the next task, its checksum,
   location and transfer or deterministic regeneration method. `/tmp` paths
   are local and disposable. Verify required artifacts on receipt; if an
   irreplaceable input is missing, stop rather than rerunning a once-only case.
3. If the user authorized publication for this step, commit only its scoped
   changes and push the current branch. Otherwise do not publish implicitly:
   leave a clear patch/handoff and do not start overlapping edits on the other
   checkout until the user chooses how to transfer them. Include new untracked
   source/evidence files in any patch transfer; a plain `git diff` omits them.
   If publication is authorized, check the push result and final `git status`,
   and report the exact **delivery commit** after committing. A handoff file
   cannot contain the hash of its own commit: label earlier hashes as source
   or base commits and use the final report/Git history for the delivery hash.
   Publication failure leaves transfer pending. Stop after successful delivery;
   do not make an uncommitted delivery-note edit after the final push.

Before the other computer starts:

1. Read the local handoff as possibly stale (inspect the fetched upstream
   handoff if needed), establish that the sending owner
   released the task, and check `git status --short --branch`,
   `git branch --show-current`, `git rev-parse --abbrev-ref '@{upstream}'` and
   `git stash list`. Do not pull over staged, unstaged or untracked work; first
   preserve and reconcile it deliberately. Inspect existing stashes as possible
   undelivered work; never auto-apply/drop them. Stop for detached HEAD, the
   wrong branch/upstream, or unresolved merge/rebase state.
2. On a clean checkout of the intended branch, record the old HEAD and run
   `git pull --ff-only --no-rebase --no-autostash` against its configured
   upstream. These flags prevent inherited rebase/autostash settings from
   silently changing the handoff procedure. If it fails or histories diverge,
   stop and reconcile explicitly; do not force, reset or retry with autostash.
   Review incoming commits/files and reread the updated handoff/log. Confirm
   HEAD equals the fetched upstream tip and includes the reported delivery
   commit; if HEAD is later, review the intervening changes. Treat a recorded
   source/base commit as an ancestor, not an equality requirement with HEAD.
   A locally cached `origin/main` alone is not evidence of a successful push.
3. Allocate the next request ID as one greater than the largest recorded ID
   (entries can be out of order), append the user's actual request and receiving
   machine/commit, and claim ownership in the handoff. Confirm that the task's
   required inputs and evidence arrived. For an explicit patch transfer, record
   its base, file inventory and reconciliation instead of claiming a Git push.
4. Verify the receiving machine's own package builds, architecture, executable
   paths and applicable resource-monitor behavior before running. Reuse recorded
   checks only while their environment/monitor remains unchanged; refresh live
   capacity at launch. Never copy the PC's `/tmp` environment path as a Mac
   command. Do not assume a successful import on one OS validates the other.
   Never launch the same once-only experiment on both machines.

If a pull creates an autostash or a conflict, preserve both histories, resolve
the request-ID collision explicitly, and drop the stash only after confirming
all of its unique content is present in the worktree or committed history.
