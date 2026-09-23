# Project resource use and AI cost: a retrospective estimate

September 22, 2026. Prepared for R213/R214; updated for R215 from repository records through
commit `18a372c`, including the user's clarification that they upgraded from Plus
to the **$100/month Pro plan** on September 21. Dollar amounts are USD before
tax. This is an estimate of work already undertaken, separate from the
[future water-apparatus budget](realizability/WATER_EXPERIMENT_FEASIBILITY_AND_COST.md).

**My working estimate is about $200–240 of subscription and credit purchases,
including two or three confirmed $40 packages, one Plus month and one Pro
month.** The package count remains uncertain. An upgrade credit could reduce
that to roughly $180–240; the actual upgrade invoice is unconfirmed.
For a simple allocation of those purchases to this project, I would provisionally
use **about $150**, with a scenario range of **$85–185**. That allocation assumes
this project accounts for 50–80% of the relevant account spending, subtracts the
last recorded unused credit balance, and still includes subscription time
available for future work. It is not a measured cost of resources consumed so far.

The resource records support **4.33 million reported input/output tokens plus
95.84 million cached input tokens**, across 25 distinct summaries. They cover
only part of the project. My broader, low-confidence estimate is **6.5–15 million
input/output tokens, plus 144–335 million cached tokens**, and **12–25 hours of
agent-assisted work intervals**. These ranges are judgment, not statistical
confidence intervals. The missing early sessions make precise totals impossible.

## What the records establish

The repository begins on September 19, 2026. At this review it has 158 commits
and requests R001–R212 covering visualization, renderer repair, mathematical
analysis, numerical verification, control-system feasibility, documentation and
workflow maintenance. A request or commit is not a unit of model consumption:
several requests can belong to one conversation, and one task can have separate
start and completion commits.

I used [REQUEST_LOG.md](../REQUEST_LOG.md) as the canonical source for supplied
token and account snapshots, and [WORK_SESSIONS.md](../WORK_SESSIONS.md) for
explicit work-interval timestamps. Repeated summaries in the handoff, status
pages and historical archives were not added again. No private session files,
account dashboard, invoices or payment information were accessed.

| Resource recorded in 25 token summaries | Partial total |
|---|---:|
| Input, as reported outside the separate cached count | 3,673,699 |
| Cached input | 95,840,896 |
| Output | 652,898 |
| Reported total: input + output | 4,326,597 |
| Reasoning, already included in output | 144,837 |
| Input + cached input + output | 100,167,493 |

Every row satisfies input + output = reported total. Reasoning is not added
again. About 95.7% of the combined token traffic is cached input; this represents
repeated processing of context, not 96 million newly written tokens. A displayed
session total is also not its context-window size.

Twenty-four summaries retain distinct prior-session identifiers; R165 retains
its numerical summary but omits the identifier. No duplicate numerical record
was found. That is useful evidence against double counting, although it is not
an independent audit of the underlying telemetry. Some summaries reflect a
conversation containing multiple tasks or model changes. The full September 19–20
history, parts of September 21, and the present essay/editing discussion lack
complete token summaries.

Thirty-four STARTED/COMPLETED pairs have explicit UTC timestamps. Their intervals
do not overlap and total **20,714 seconds: 5 hours, 45 minutes, 14 seconds**.
Fourteen other lifecycle entries lack a pair in that exact timestamp form.
These intervals include some thinking, tools, checks and coordination; they omit
work before STARTED and after COMPLETED. I did not add the overlapping user
“Worked for” excerpts on top. Neither measure is a GPU-hour or CPU-hour total.

## Reconstructing subscription and credit spending

The user remembers two or three extra credit purchases and one usage-limit
reset. R214 confirms the $100 Pro upgrade. Official OpenAI documentation lists
Plus at $20/month and Pro starting at $100/month; included allowances and
purchased credits are separate ways to fund usage.
[OpenAI pricing](https://learn.chatgpt.com/docs/pricing).

R215 confirms that every purchased package cost **$40**. The remembered two or
three purchases therefore cost **$80–120**. For one Plus month and one $100 Pro
month:

| Purchased item | Two-package case | Three-package case |
|---|---:|---:|
| One Plus month | $20 | $20 |
| One Pro month | $100 | $100 |
| Confirmed $40 packages | $80 | $120 |
| **Gross purchases before adjustments and tax** | **$200** | **$240** |

The package's credit quantity was not supplied. An official offer equates
2,500 ChatGPT credits to $100, giving a nominal $0.04 per credit for the
balance-value illustrations below; it does not establish the exact terms of
the user's purchases.
[OpenAI credit-value example](https://developers.openai.com/community/students).

The $180–240 working range allows an illustrative $0–20 adjustment to the
$200–240 scenario for remaining Plus subscription value. No refund, credit or
proration is claimed to have occurred. Each additional Plus month actually
included in a wider spending history adds $20 before adjustments. Months before
this project began should not automatically be charged to this project.

There is enough historical evidence to explain why receipts and percentages
need separate treatment:

| Repository observation | Interpretation |
|---|---|
| R085 addenda: 373 credits, weekly remaining 22% then 15% | Account balances at supplied snapshots; earlier purchases/consumption are missing. |
| R089: 334 credits, weekly 7%, five-hour 0% | A net drop of 39 credits since the preceding balance. |
| R092: user reports a reset; weekly and five-hour both return to 100%; credits 283 | Another net drop of 51 credits; the excerpts do not show that the reset charged those credits. |
| R098 → R099: weekly 86% → 99%, with a different reset time; reserve 1% → 100% | An allowance discontinuity. The precise cause is not recorded. |
| R136: account label “Pro Lite”; later excerpts say “Plus” | Historical labels conflict. The user's current confirmation establishes the $100 Pro purchase; old labels cannot establish the billing transition. |
| R092 through R197: repeated credit balance of 283 | No net credit depletion is visible between these sampled balances; included allowance can still be consumed. |
| R194 → R195: weekly 75% → 66% | R195 explicitly says another project contributed; R196 also reports concurrent work elsewhere. |

The observed 373 → 283 decline is **90 credits**, nominally **$3.60** at the
conversion above. It is account-wide net change over a partial interval, not
the whole project's credit cost. Likewise, the last **283 credits** represent
about **$11.32** of nominal unused purchasing value at that historical snapshot,
not a verified current balance or a cash refund.

I assign the reported reset **$0 additional cash in the working budget** because
no separate payment is recorded. Its restored capacity had value, but it is not
a purchased package or an extra subscription month. If a receipt later shows a
charge, add it once. The 51-credit decline around the reset is not evidence of
a reset fee. Weekly percentages cannot be summed across resets or an upgrade.

## How much belongs to this project?

There are three useful amounts, and adding them together would double count.

**Cash purchased** is the money spent on subscriptions and packages: roughly
$180–240 under the working assumptions. It includes resources that may still be
available, plus use by other projects.

**Allocated project spending** is a budgeting choice. This repository appears
to have occupied a substantial share of the recent activity, but no measurement
establishes the share. Using 50–80%, and provisionally subtracting the last unused
credit value, gives:

`50% × ($180 − $11.32) = $84.34`

`80% × ($240 − $11.32) = $182.94`

That motivates a rounded **$85–185 range and $150 working allocation**. The
fraction is an assumption, not inferred from account percentages. At 25% the
same calculation gives $42–57; at 100% it gives $169–229. These alternatives
matter if the other work was much larger or smaller than remembered.

This method allocates the full purchased subscription periods, including future
availability. For an expense strictly accrued through September 22, a different
convention could allocate only days used. For example, two Plus days and one
to two Pro days, using 30-day months, would allocate only $4.67–8.00 in base
subscription time before adding project-attributable credit consumption.
That is an illustrative accounting convention; exact billing dates and credit
consumption are missing. I would not present $150 as an accrued usage invoice.

**Replacement cost of model usage** asks what comparable token traffic would
cost at public metered rates. It is useful for comparing subscription access
with buying everything separately, but it is neither a bill nor OpenAI's
internal computing cost.

## Estimating the missing resource use

For tokens I use **1.5–3.5 times the recorded sample**, centered at 2.5 times.
This allows for unrecorded early work and later discussions without multiplying
the sample by the number of requests. The sample already contains long,
multiple-task conversations, so requests are a poor extrapolation unit.
There is no way to establish the actual coverage fraction from these records.

| Whole-project estimate | Low | Working midpoint | High |
|---|---:|---:|---:|
| Input + output tokens | 6.5 million | 10.8 million | 15.1 million |
| Additional cached input tokens | 143.8 million | 239.6 million | 335.4 million |
| Agent-assisted work intervals | 12 hours | 18 hours | 25 hours |

The time estimate is separate judgment: the 5.75 recorded hours omit many tasks,
especially before R073, renderer/build work without paired timestamps, and the
long conceptual/documentation discussion after R197. It includes tool waiting
and does not mean 18 hours of continuous inference. The total could lie outside
these ranges. There is no defensible reconstruction of human attention hours,
provider GPU-hours, energy use or per-model inference time.

For a transparent replacement-cost calculation, take standard short-context
rates per million input/cached/output tokens: **$10/$1/$50 for GPT-6 Astra** and
**$0.20/$0.02/$1.20 for GPT-5.6 Luna**. Request length, speed, cache writes and
tools can alter the result. These are current reference rates, not reconstructed
historical billing.
[Official Astra rates](https://developers.openai.com/api/docs/models/gpt-6-astra),
[official Luna rates](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

Pricing the five Luna-banner records R085/R094/R096/R136/R165 as Luna and the
remaining records as Astra produces **$94.48 for the sample**. Treating all
sample traffic as Astra produces **$165.22**. The first is a model-label scenario:
a displayed model does not prove every turn in its conversation used that model.
The second is an Astra comparison, not an absolute upper bound. R094, for
example, follows a conversation with Astra usage before its Luna banner.

Applying the 1.5–3.5 coverage multiplier across these scenarios gives about
**$140–580**, or **roughly $150–600 as a working metered-token equivalent for
the project**. Speed premiums, long requests, cache-write charges and tool fees
are excluded and could raise it. This number is not added to subscription and
package purchases, and it cannot be used to infer how many purchased credits
were actually debited.

## Local computers and the work the resources bought

The records show work on an existing PC/WSL machine and an existing M4 Mac.
They do not supply a project-specific computer purchase or rented GPU invoice.
Local Python checks, rendering and builds are different resources from the
remote model usage paid through the subscription.

There are measured small numerical workloads: the
[B2 history](realizability/B2_NEXT_STEPS.md) records an R020 numerical attempt at
59.97 seconds and 757 MiB, and R033 observer checks totaling 56.25 seconds across
four attempts with 571.42 MiB maximum sampled child-tree RSS. “Physical attempt”
in that numerical workflow does not mean a water-tank experiment. These examples
are neither total CPU time nor a guarantee that a future simulation fits the
same memory. The existing 180-second/1536-MiB execution limits are budget caps,
not consumption to add to a bill.

For scale only, 12–25 computer-on hours at an assumed 50–300 W and assumed
$0.15–0.30/kWh would cost about **$0.09–2.25 in electricity**. Actual powered-on
time, both machines' loads, electricity rates and model-server energy are not
measured. Hardware depreciation and the user's time remain unpriced. No tank,
actuator, sensor or laboratory purchase is evidenced in this review.

The project has bought a visualization pipeline, renderer diagnosis and repair,
mathematical/control analysis, verification source and tests, and a documented
feasibility/cost assessment. It has not yet demonstrated the proposed
boundary-controlled contracting water flow. A material amount of activity also
went into process safeguards, repeated reviews and documentation. R092 explicitly
raised a concern about reading overhead and commissioned a reduction. The
[overhead plan](WORKFLOW_OVERHEAD_PLAN.md) records that hypothesis. Document
length decreased, but a performance benefit was not established by a controlled
comparison; the token records cannot quantify avoidable work or causal savings.

For future accounting, the smallest useful improvement is one end-of-conversation
record with the prior session identifier, token summary and models used, plus
occasional credit balances and the amount of each purchase. Keep account-wide
balances separate from project sessions. The two most valuable missing facts
for this estimate are the **count of $40 credit packages** and the **net upgrade
charge**; neither is required to use the scenario estimates above.

The separate [process and model-routing review](PROCESS_REVIEW_AND_MODEL_ROUTING.md)
examines how model choice and step size could make future work more efficient.

## Token-summary audit table

R-numbers identify where the prior conversation's summary was recorded, not a
claim that all its tokens belong to that one request. The linked request log
preserves the underlying excerpts. Only one copy of each summary is counted.

| Recorded at | Reported total | Input | Cached input | Output |
|---|---:|---:|---:|---:|
| R085 | 435,883 | 340,492 | 21,707,008 | 95,391 |
| R088 | 167,449 | 143,953 | 3,693,184 | 23,496 |
| R089 | 179,963 | 147,187 | 2,904,448 | 32,776 |
| R094 | 190,862 | 175,508 | 2,276,096 | 15,354 |
| R096 | 143,430 | 115,649 | 4,070,912 | 27,781 |
| R097 | 153,060 | 133,197 | 2,054,272 | 19,863 |
| R098 | 114,655 | 95,893 | 1,301,888 | 18,762 |
| R099 | 123,391 | 110,427 | 1,441,408 | 12,964 |
| R101 | 187,363 | 172,592 | 1,322,368 | 14,771 |
| R136 | 504,983 | 408,942 | 21,107,584 | 96,041 |
| R165 | 37,498 | 32,912 | 376,576 | 4,586 |
| R168 | 114,349 | 99,692 | 2,282,496 | 14,657 |
| R170 | 133,107 | 113,025 | 2,560,640 | 20,082 |
| R177 | 248,578 | 222,675 | 6,421,504 | 25,903 |
| R180 | 188,491 | 162,399 | 4,441,344 | 26,092 |
| R181 | 128,018 | 114,921 | 1,565,824 | 13,097 |
| R182 | 126,022 | 111,221 | 1,241,344 | 14,801 |
| R185 | 136,166 | 117,290 | 2,043,008 | 18,876 |
| R191 | 157,498 | 133,799 | 3,700,736 | 23,699 |
| R192 | 131,137 | 112,985 | 1,591,296 | 18,152 |
| R193 | 125,652 | 105,601 | 1,331,712 | 20,051 |
| R194 | 123,391 | 106,693 | 1,379,456 | 16,698 |
| R195 | 133,104 | 111,708 | 1,568,640 | 21,396 |
| R196 | 120,404 | 93,818 | 1,323,136 | 26,586 |
| R197 | 222,143 | 191,120 | 2,134,016 | 31,023 |
| **Total** | **4,326,597** | **3,673,699** | **95,840,896** | **652,898** |
