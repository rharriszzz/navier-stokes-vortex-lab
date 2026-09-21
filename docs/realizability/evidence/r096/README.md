# R096 source and saved-evidence acceptance audit

The [review](../../B2_MONITOR_R088_REVIEW.md) refuses OS implementation admission
and maps H01–H04 plus residual J01–J04. R088 and older archives are preserved.

One [audit](audit.py) ran through the exclusive [runner](run_audit.py):
`/tmp/navier-fenicsx/bin/python -B docs/realizability/evidence/r096/run_audit.py`.
Do not rerun it or rename its attempt directory. It imports pure acceptance
and accounting functions; it never imports the archived validator or runs an
archived main. The fake sentinel's two constant input files and canonical
manifest are reconstructed from R088 source and match its saved manifest hash.

The [start record](attempt_01/started.json) binds all R088 files and both new
executed audit sources before release. [Progress](attempt_01/progress.json) and
[review.json](attempt_01/review.json) retain all nine observations: historical
binding/arithmetic checks, all 14 registered saved functions, positive accepted
result, two rebound semantic refusals and four accepted mutations covering
J01–J03. A passed audit means these observations were confirmed, not that R088
meets all acceptance requirements. J04 is source/saved-evidence analysis.

[Receipt](attempt_01/receipt.json): Python 3.12.13; child 0.066115114 s,
23,982,080 B lifetime peak RSS under 256 MiB address space, five CPU seconds,
one MiB per-file limit and ten-second child timeout. Separate review reservation
was 20 s including ten seconds for setup/final evidence. Observed guard time
0.091153679 s; charge 5.091154090 s includes five seconds of unmeasured final
reserve. Guard startup before ENTRY and its receipt fsync/exit are excluded;
this review audit also makes **no whole-recorder certificate**. No timeout,
nonzero exit, retry or source mutation occurred. stdout/stderr are preserved.
The audit child was reaped and its temporary fake inputs cleaned up.

Historical R088/R084/live/physical allowances are unchanged. No archived-main
replay, native source/build/startup, live OS/cgroup/signal/helper/workload,
FEM/MPI/JIT/mesh/solve, render, encode or physical run occurred. The independent
Mac build is unverified. PC retains ownership; no ignored input needs transfer.
Documentation/integrity evidence is [documentation_validation.json](documentation_validation.json).
Follow the [single next task](../../../../SESSION_HANDOFF.md#next-task).
