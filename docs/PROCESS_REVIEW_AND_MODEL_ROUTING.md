# Process review: model choice, task size and useful stopping points

September 22, 2026. R215/R216; revised for R217–R219. This review follows the updated
[cost-so-far estimate](PROJECT_RESOURCE_AND_COST_ESTIMATE.md), which now records
confirmed $40 credit purchases and the $100 Pro upgrade. The package count is
still two or three. R217 establishes that adequate agent understanding takes priority over document
size; that preference is recorded in AGENTS.md. The remaining model and step
recommendations are proposals, with no change to model settings, execution
permissions or scientific acceptance criteria.

**My assessment is that the clear stopping points were valuable, but some of
our steps were too small in what they accomplished, and some supporting
work did not resolve the questions needed for progress.** Model escalation was often well motivated. We were
less consistent about stepping back down after the difficult question was
settled, and too willing to alternate implementation and review without first
checking whether the specification itself was becoming excessive.

I would retain bounded work and introduce three distinct roles: **GPT-6 Luna
for tightly specified changes, GPT-6 Sol for most implementation and synthesis,
and GPT-6 Astra for difficult scientific decisions and critical reviews.** The
new middle option is especially useful here. A task can require judgment without
requiring our most expensive model throughout.

## What this review can establish

The evidence is the [request history](../REQUEST_LOG.md),
[work intervals](../WORK_SESSIONS.md), linked result documents, and the prior
[overhead-reduction plan](WORKFLOW_OVERHEAD_PLAN.md). I reviewed the progression
from visualization and early numerical checks through cross-computer setup,
supervision, renderer diagnosis, boundary-control analysis and recent essays.
Recommendations in those records are distinguished from actual model banners.
There is no complete per-turn model history or controlled comparison of models
on this project.

Consequently, I can identify weak decision boundaries and suggest improvements.
I cannot establish that a different model would have produced the same result,
that every failed attempt was caused by model choice, or that a specific fraction
of the bill was wasted. User questions, corrections and changes of direction
are part of legitimate collaboration, not automatically inefficient steps.
The criticism below concerns how I organized and executed the work.

## Where the model boundaries worked, and where I would change them

| Work and recorded boundary | Assessment | Better future boundary |
|---|---|---|
| Early numerical prerequisites, R002/R022/R030–R033: Luna/medium for specified harness work, then Astra/high for observer/launch interpretation | Reasonable division where forms and acceptance criteria were fixed. Numerical compatibility and resource failures needed interpretation beyond mechanical editing. | Give Luna a precise implementation contract; use Sol when assembling several interacting components. Escalate changed mathematical meaning, not every test failure. |
| Monitor implementation/review, R073–R088 and R096–R101: repeated repairs followed by stronger reviews | Reviews found real defects, including omitted tests and overclaimed completion. But scope expanded into proving the supervisor's authority and final accounting. Model alternation could not settle an unsettled specification. | Have Astra settle the assurance boundary once, then Sol implement a complete bounded unit with adversarial tests. If the same class of semantic gap returns twice, reconsider the contract before another repair cycle. |
| Overhead cleanup, R092–R096: Astra identifies the problem, Luna implements the specified document reorganization | A good handoff. The brief supplied preserved inputs, targets and checks. | Keep the explicit brief and preservation checks; judge the handoff by whether the next agent understands the work, not its size. Do not add an automatic Astra audit after a mechanical cleanup that passes its relevant checks. |
| Portable trajectory checker and Mac validation, R106–R109: Luna/medium after a scoped design | Good match: concrete input format, six meaningful tests, visible outcome and failure boundary. | Luna remains suitable for a comparably specified reader; Sol should own additional cross-platform behavior if it requires design. The deliverable is a working checker plus its checks. |
| Mac renderer investigation, R109–R136: Luna diagnosis followed by Astra/xhigh at R136 | Basic command and scene checks were appropriate initially. Once a canonical primitive also failed, the problem needed renderer/environment diagnosis, not more project-scene adjustments. R136's build comparison isolated fast-math handling of camera defaults. | Run a small decisive diagnostic set. Escalate a persistent canonical-example failure to Sol/high or Astra/high, depending on source/build ambiguity. Do not repeat scene tweaks after evidence has moved the fault outside the scene. |
| Durable renderer fix and verification, R140–R159 | Source/build choices justified strong reasoning; installation verification became routine once the fix was established. R156/R159 correctly recommended Luna for the remaining checks. | End Astra's role at a tested diagnosis and exact repair recipe. Keep user-authenticated installation and machine ownership explicit; use Luna/Sol for the specified verification. |
| PC renderer failure, R167–R170: escalation to Astra/high, then recommendation to return to Luna | Sensible response to a new crash. The bounded comparison restored useful evidence; the later preview had a clear completed state. | Escalate a new unexplained failure, then return to the specified preview task. Do not imply a completed preview needs a fresh session or rerun just to finish bookkeeping. |
| Boundary-control interpretation, R171–R194 | Astra was justified for forcing versus boundary control, similarity, observability, pressure/heat constraints and mathematical interpretation. Some adjacent calculations could have shared one analysis step. | Astra chooses assumptions and decisive tests; Sol develops the resulting tables, source synthesis and implementation plans. Keep new physical claims subject to focused strong review. |
| Verification source, R195–R196: recorded Astra/medium followed by Astra/high | The higher setting at R196 had a concrete reason: mixed constraints, sparse assembly, energy accounting and execution-admission questions. The tests were useful, but no FEM execution yet supports the adapter. | Use Astra for formulation and a critical admission review, Sol for implementation against fixed equations and oracles. Aim for one complete tiny fixture before expanding the suite. |
| Recent physics essay, clarity edits, README changes and Git delivery, R200–R214 | Scientific analysis justified Astra. Once the content was settled, document consolidation, links, image removal and publication were work for a cheaper model. | Use Sol for a cohesive essay or ambiguous cost reconstruction; Luna for exact edits and authorized publication. Do not require a model switch mid-edit when handing over would cost more than finishing it. |

The monitor review found substantive faults, not merely stylistic disagreements;
see the [R083 findings](realizability/B2_MONITOR_R082_REVIEW.md). R103/R104 later
made the needed course correction explicit: practical supervision and useful
work should take precedence over an elaborate infrastructure project. I should
have raised that scope question earlier, before the repeated repair/review loop.

Likewise, the [renderer diagnosis](rendering/POVRAY_MAC_BUILD_DIAGNOSIS.md) is
strong evidence for a useful escalation: it tested unchanged examples and
isolated the parser/compiler behavior. It does not prove that Astra alone could
have found the problem. The lesson is to escalate the kind of uncertainty and
improve the diagnostic experiment, rather than equating all debugging with a
particular model.

Today's GPT-6 Sol and Luna are prospective options. I am not treating their
availability now as something we should have known or used in earlier sessions.

## Current model prices and the proposed roles

Official OpenAI documentation describes Sol as the balance for complex coding
and agentic workflows and Luna as the efficient option for focused work. Its
selection guidance recommends choosing model and effort together, then checking
whether the result meets the task's quality bar. The routing below is my
project-specific judgment, not a benchmark result.
[OpenAI model selection](https://developers.openai.com/api/docs/guides/model-selection).

Prices checked September 22, 2026. The following API rates are standard text
input, cache-read and output prices per million tokens; cache-write, tool and
applicable request/speed surcharges are excluded.

| Model | Input USD / million | Cached input USD / million | Output USD / million | Proposed starting role |
|---|---:|---:|---:|---|
| GPT-6 Astra | $10.00 | $1.00 | $50.00 | High for novel science or critical semantics; medium for a bounded broad assessment |
| GPT-6 Sol | $2.00 | $0.20 | $10.00 | Medium for implementation, synthesis and everyday technical judgment; high for difficult integration |
| GPT-6 Luna | $0.10 | $0.01 | $0.50 | Low for exact edits/extraction; medium for coordinated but specified work |

Sources: [Astra](https://developers.openai.com/api/docs/models/gpt-6-astra),
[Sol](https://developers.openai.com/api/docs/models/gpt-6-sol),
[Luna](https://developers.openai.com/api/docs/models/gpt-6-luna).

Codex has a separate published credit rate card. Standard credits per million
input / cached input / output tokens are **250 / 25 / 1,250 for Astra**,
**50 / 5 / 250 for Sol**, and **2.5 / 0.25 / 12.5 for Luna**. These are rates
when valuing usage in credits, not extra charges on every subscription message.
Codex Fast mode currently uses 2.5 times the standard credit rate for these
models where available; API speed pricing is a separate schedule.
[Codex pricing](https://learn.chatgpt.com/docs/pricing).

For the same hypothetical task traffic—150,000 input, 2 million cached input
and 20,000 output tokens—the standard API equivalents are **$4.50 Astra,
$0.90 Sol and $0.045 Luna**. The matching Codex rate-card amounts are
**112.5, 22.5 and 1.125 credits**. This illustrates the price difference only;
models may use different tokens, need different numbers of attempts, and produce
different quality. It is not a forecast that Luna can do all our science for
one hundredth of Astra's cost.

The new models appear in this session's available model catalog, and the official
Codex changelog announces their rollout. That does not independently verify
every model/setting in the user's picker. No switch has been made here.
[Codex rollout notes](https://learn.chatgpt.com/docs/changelog).

For future work, stay with the least expensive model that reliably completes
the whole accepted task. Increasing reasoning effort can help with a bounded
problem; it cannot make an unclear requirement precise. A scientific uncertainty
can go straight to Astra rather than first exhausting Luna and Sol. Conversely,
a typo, known shell mistake or broken relative link does not warrant escalation.

## Were the work steps the right size?

Some were. The trajectory checker, renderer comparison and finite momentum
calculation each had a concrete result a reader could assess. Separating
unreviewed source from numerical execution was also appropriate: passing
algebraic tests cannot authorize or validate an unrun FEM solve.

The weak pattern was treating “write a contract,” “implement a piece,” “review
the contract,” and “prepare the next handoff” as repeated endpoints without a
nearby usable result. In the timestamped sample, the monitor phase R073–R101
accounts for **14 intervals totaling 186.5 minutes**, about **54% of the 345.2
recorded minutes**. This is a partial sample, not 54% of the project's total
cost. It nevertheless identifies a phase worth examining for scope growth.

The remaining sampled intervals are 60.7 minutes across ten visualization
entries and 98.1 minutes across ten later physics/source entries. Many longer
conversations have no complete timing. These figures do not support a universal
ideal step length or a dollar cost per step.

I recommend defining a step by **one accepted capability or one resolved
question**, with a short chain of dependent actions inside it:

| Kind of step | Appropriate unit of work | Clear ending point |
|---|---|---|
| Routine documentation | Requested edits, affected links, concise record and relevant checks | The requested document is ready; publication completes too if already authorized |
| Implementation | One useful feature plus necessary integration, tests and interpretation | The feature works within its stated scope, or one specific blocker is evidenced |
| Scientific analysis | One question, assumptions, calculation or source comparison, uncertainty and conclusion | A decision or explicit inconclusive result that determines the next experiment |
| Diagnosis | One bounded hypothesis set with decisive comparisons | Cause isolated or evidence narrows the next question; no unbounded retry loop |
| Numerical execution | One admitted fixture/run with predeclared limits and complete results | Results accepted, rejected or inconclusive; cleanup and actual resource use recorded |

As planning estimates, many routine steps might take 5–15 minutes, implementation
steps 15–40 minutes, and difficult analysis 20–45 minutes. These are conversation
planning ranges, not deadlines, minimum durations or new workload allowances.
A correct two-minute edit should end after two minutes. A tool's existing hard
runtime/memory cap is not enlarged by a longer discussion step.

We should combine adjacent low-risk actions already in scope, while retaining
boundaries for changed scientific assumptions, machine transfer, user-controlled
installation, purchases or execution admission. We should also distinguish a
small code commit from a complete work step: one capability may reasonably need
several commits. Current Continue start/completion publication remains required;
this review proposes grouping the useful work inside a bounded task, not
silently bypassing that protocol.

A fresh conversation is useful at a real phase change or when accumulated context
has become costly to navigate. It is not required after every progress update,
commit or completed calculation. Before recommending a model handoff, compare
the remaining work with the cost of transferring context. A short authorized
publication at the end of a difficult analysis is usually worth finishing in
place; a new batch of routine edits is a better point to switch.

## Give the next agent enough context to work correctly

**R219 sets the present priority: make good progress at each step. Do not reduce
word count if that might impair an agent's progress.** When the value of context
is uncertain, retain it. Model choice, step size and documentation should support
useful results with clear completion points; brevity is not a competing objective.

R217 corrects my emphasis on the old document-size target. **The user values
agents understanding what they are doing more than meeting a word count.**
A longer handoff can be the right choice if it prevents repeated mistakes,
lost assumptions or confident work on the wrong problem. The R092 size target
is historical, not a current acceptance criterion. Length alone does not show
that a document is inefficient, and shortening it is not a project objective.

R218 also distinguishes the proposed optimization from evidence that it worked.
R092/R096 measured a reduction in document length; they did not demonstrate
better task completion, lower cost per accepted result, or shorter completion
time. The subsequent records mix different tasks, models, context histories,
resets and other-project usage. They cannot isolate the effect of shorter
instructions. I should not have treated growth beyond the old target as proof
of a performance regression.

Testing is possible in principle, although a reliable comparison would cost
work and might not generalize. Use the same representative tasks and repository
starting state with alternative handoffs, keep model/settings/tools comparable,
and repeat runs to account for variation. Check correctness, retained constraints,
missed context, rework, token usage and time through an accepted result; balance
or record cache conditions. Saving tokens in the opening read is not sufficient
if the agent later searches more, repeats a mistake or needs correction. No such
comparison has been run, and none is proposed as a prerequisite to useful work.
The cost audit supplies partial observations, not this causal test.

A useful handoff should make the scientific goal, current result and limitations,
reasons for important choices, known failures, applicable constraints and next
step understandable. It should include enough evidence and concrete completion
criteria for the next agent to distinguish success from a plausible-looking
result. Links are useful when the agent follows them before dependent work;
they are not a substitute for understanding a requirement.

The process problem to address is contradictory or stale guidance, repeated
work whose answer is already established, and checks unrelated to the current
change. I have sometimes repeated outcomes across records and retrieved broad
history without first identifying the question it needed to answer. The remedy
is purposeful reading and coherent instructions. Necessary background should
remain accessible and be read even when it is long. Some repetition is useful
when it puts an essential limitation beside the action it governs.

Before a handoff, the agent should be able to explain what it is trying to
establish, why the chosen method is appropriate, what earlier evidence rules
out, and what would count as completion or failure. Missing answers require
more context or investigation. A short document that cannot support those
answers is inadequate; a long one that can may be entirely appropriate.
This can be part of normal task preparation, without a separate cleanup phase.

Proportional verification still matters. A README edit needs its diff,
requested-content/link check and whitespace review. Scientific code needs its
meaningful tests and prescribed evidence checks. Neither should be made weaker
to save tokens, or more elaborate merely to create another checkpoint.

## A concrete trial for the next phase

I would use the following sequence when the user chooses to resume work:

1. **GPT-6 Sol/high: one complete tiny fixture driver and supervision source
   increment**. First read and explain the R195/R196 equations, oracles,
   known limitations and practical supervision policy; resolve missing context
   before dependent edits. Connect the existing pieces and test the source's
   success/refusal behavior. End before FEM execution, with a concrete admission
   question. If a mathematical constraint or supervision promise remains unclear,
   stop that dependent work and bring the question to Astra.
2. **GPT-6 Astra/high: one focused formulation/admission review.** Check the
   conservation/constraint logic, numerical acceptance gates and actual launch
   boundary. End with an explicit decision and, if appropriate, one bounded
   later execution task. Do not turn the review into another general monitor
   redesign. Model review alone is not permission to run it.

The [R196 adapter note](realizability/CUBE_ADAPTER_R196.md) identifies what is
implemented and what remains untested. These proposed model assignments would
replace the current deferred Astra-only implementation recommendation only
when the workflow is adopted. They do not resume paused implementation now.

For the first three useful tasks after adoption, record the model/effort,
accepted deliverable, token summary when available, elapsed work interval and
whether a substantive correction was needed. Use ordinary work rather than a
separate paid benchmark campaign. A missed mathematical condition or repeated
semantic repair is evidence to strengthen the assignment. Accurate completion
without substantive rework supports retaining the cheaper model. A model's
confidence or a low token count does not establish correctness.

Success means more accepted scientific or implementation progress per task,
well-informed agents and fewer repeated repairs. Lower token-equivalent
cost would be welcome, but the $100 subscription remains $100 while retained;
the first benefits may be greater included capacity and fewer $40 top-ups.
No specific percentage saving can be established from the available records.
