# R097 completion certificate (fixture schema 5)

This repair applies R096 J01–J04 to a new copy of R088's composed interface.
All domain/provider/outer events are injected. No native/live/physical entry
is enabled. Physical limits, old attempts and q64/q96 allowance are unchanged.

## Admission before effects

A frozen Admission holds the validated frozen Policy, canonical owner digest,
absolute reservation start, active deadline (in Policy), cleanup/recorder outer
deadline and final enclosing deadline, clock-domain token, recorder identity,
observer identity and enclosing backstop identity. All three identities differ.
The cleanup deadline has at least five seconds reserved after active work;
final evidence has positive reserved time after the recorder deadline. These
are subdivisions of the admitted total, never additional allowance. For the
fake sentinel use start=0, active=10, recorder=15, enclosing=17 seconds.
Admission is authoritative input supplied by the trusted admission layer, not
reconstructed from a child report. The owner stores it before any effects.
Both candidate and inner receipt bind its canonical digest. Supervision refuses
policy/deadline mismatch before release and still attempts both owned cleanups.
Active decisions require time < active deadline; cleanup/inner persistence may
equal min(cleanup start+5, recorder deadline). Acceptance independently checks
those absolute bounds and requires cleanup start before the active deadline
for a successful sentinel (a deadline stop remains a partial result).

## Monitor and durable binding

Schema 5 requires a nonempty ordered sample list, exact positive integer
sequences, finite nonnegative acquisition/decision times, nonoverlapping
brackets, decision before active expiry, RSS within admitted cap, complete
membership, exact Boolean root state, and terminal root integer-zero exit with
zero members. No sample may follow termination. Counts have exactly six keys;
each is either null (explicitly unknown after release) or an exact nonnegative
integer agreeing with the child's exact zero. Unknown monitor counts stay null;
only the separately bound validated child supplies final sentinel zeros.
Every candidate, including the independently loaded durable candidate, must
pass the same schema/ownership/cleanup/lifecycle validation. Canonical bytes
and receipt digest must agree; Python equality alone is insufficient.

## Independent receipt and trust boundary

OuterReceipt is a strict JSON object binding admission, owner, source manifest,
monitor, child, durable candidate and inner receipt digests. It identifies the
admitted recorder and observer, records observer startup, recorder startup,
last recorder durable output, recorder exit and observer receipt write-start.
Ordering is checked and recorder exit is at or before the recorder deadline.
Exact integer zero return code, completed state and false resource/timeout
flags are mandatory. Missing/open/mismatched/unpersisted evidence refuses.

A separate frozen TerminalWitness is supplied by the enclosing observer/backstop
adapter. It binds this receipt's canonical digest, admitted backstop/observer
identities and clock domain; observes backstop arming before observer startup,
receipt durability after its write-start, and observer exit afterward within
the enclosing deadline. Success also requires exact-zero exit, no timeout or
resource stop, confirmed terminal observation and an armed lifetime deadline
equal to the admitted enclosing deadline. Thus the receipt never certifies its
own final persistence/exit. Witness facts are trusted injected inputs here,
not authenticated OS attestations; callers cannot promote an arbitrary JSON
claim into live authority. No implementation of that trusted adapter is provided.
The enclosing backstop's own lifetime/output lies outside this defined observed
boundary. Missing enclosing observation keeps whole-recorder/live certification
false, including for this task's actual fixture recorder. There is no recursive
claim to measure the final observer by its own record.

## Actual fixture execution

One exclusive new attempt, Python 3.12.13, 120 s cumulative reservation, validator
256 MiB address space / 10 s CPU / 1 MiB per output. Reserve 20 seconds for
setup/final evidence before releasing a child bounded to at most 60 seconds.
Snapshot source and contract before launch; bind progress before each test and
all partial/final outputs. No retry switch; preserve failed/open/resource stops
for review. Actual guard startup before ENTRY and its final persistence/exit
remain unmeasured; charge five seconds explicitly as an unenforced reserve.
Passing fake TerminalWitness checks does not remove those exclusions.

Completion: positive composition, J01–J03 rebound negatives, complete sample
and count refusals, exact/late deadlines, missing/late/mismatched/unpersisted
outer evidence, both cleanup domains on failures, retained unknown counts,
unique complete registration, source/attempt bindings and partial progress.
Then Astra/high acceptance review; no OS implementation admission in this task.
