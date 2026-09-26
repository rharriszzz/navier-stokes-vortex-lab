# Repository agent instructions

## Every session

- Prioritize good progress at each step (R217–R219). Do not reduce word count if doing so might impair an agent's progress. Preserve enough rationale, constraints, known failures, evidence and completion criteria for informed work; when unsure whether context is needed, retain it. Judge steps by useful results and clear completion points, not document length. Historical size-reduction targets are superseded by this preference.
- Check identity, ownership, Git status/branch/upstream and stashes before writes or workload launches. Read [SESSION_HANDOFF.md](SESSION_HANDOFF.md), the latest request entries, and the applicable task inputs. A new user request overrides a stale recommendation.
- Append each actual user request to `REQUEST_LOG.md` before substantive work, with the next sequential ID, date, wording, scope and status. Preserve prior entries; append outcomes. Record only supplied text, redact secrets and label missing excerpts. Never inspect private session files or infer command output.
- Keep one active repository owner across machines. Treat local Git as unable to reveal another checkout's unpublished work or live processes. Resolve dirty work, ownership conflicts and incomplete transfers before dependent work.
- For a bounded workload, distinguish a recoverable caller/preflight error from a spent attempt. If the error occurred before reservation and before any managed worker or numerical import, preserve its evidence, verify the fixed directory and manager have no new task process, fix and test the cause, then continue within the authorized scope after restoring a clean source binding. Do not consume or reset the one-use allocation by inference. Once reservation or partial worker start occurs, preserve the result and obey the attempt stop rule; never relax scientific or resource gates to obtain a pass.
- At completion record changed files, checks/skips, evidence, unresolved decisions and one concrete next task in the log and handoff. Keep the handoff opening, owner table and Next task consistent; current status pages link to that task. Never claim an unrun check passed.
- Do not commit or push without user authorization. Preserve user work and Git history; never force, reset, rebase, or delete user data without explicit authorization.

## Conditional instructions

- Before every **Continue** task or receiving-computer handoff, follow [the full session protocol](docs/workflow/SESSION_PROTOCOL.md), including clean fast-forward synchronization, ownership checks and lifecycle publication rules. The exact word **Continue** as a task instruction carries its recorded scoped commit/push authorization; a qualification overrides it.
- Before trajectory, rendering, encoding or realizability work, follow [track rules](docs/workflow/TRACK_RULES.md). Read the research documents listed there before substantial physical-realizability work.
- For a metadata-only request, read the compact handoff, relevant latest log entries and supplied text; do not load research history without a task-specific link.

## Current task

Follow [the current handoff](SESSION_HANDOFF.md#next-task). Historical full instructions and handoff are preserved byte-for-byte in [`docs/history/AGENTS_BEFORE_R092_IMPLEMENTATION.md`](docs/history/AGENTS_BEFORE_R092_IMPLEMENTATION.md) and [`docs/history/SESSION_HANDOFF_BEFORE_R092_IMPLEMENTATION.md`](docs/history/SESSION_HANDOFF_BEFORE_R092_IMPLEMENTATION.md). See [the archive index](docs/history/R092_ARCHIVE_INDEX.md) for original link context and heading locations.
