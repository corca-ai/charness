# 344 new-pool-module advisory slice critique
Date: 2026-06-10

## Decision Under Review

Resolve #344 (continuation slice under the 2026-06-10 next-queue goal's
done-early policy): a deterministic, advisory-only nudge in
`run_slice_closeout` that fires when a slice ADDS a new eligible
mutation-pool module, naming the documented early changed-line self-check so
the recurring confirm-not-discover trap becomes workflow signal.

## Failure Angles

- The advisory could misfire loudly in normal flows (long-lived branches,
  stale origin/main) and train operators to ignore it.
- The detection could fork the mutation-pool definition or add cost to the
  closeout path.
- Tests could mock both seams and never exercise the real glue, or miss the
  call site entirely (a deleted call passes function-level tests).
- The repo-degradation contract (tmp repos without origin/main) could break
  consumer flows.

## Counterweight Pass

- Real and folded: the vacuous module-import test replaced with a call-site
  pin (rebinding identity + the invocation string in run_slice_closeout);
  the message assertion extended to the load-bearing
  implementation-discipline.md pointer; the origin/main-vs-merge-base anchor
  choice recorded as a code comment (deleted-upstream files can fire a
  spurious stderr-only advisory — accepted over extra plumbing); the
  function-local subprocess import moved to module top.
- Over-worry: per-path `git cat-file -e` cost (two cheap guards run first;
  ~ms per changed .py against a closeout whose floor is broad pytest in
  minutes; a batched ls-tree exists if it ever matters); long-branch
  re-fires (the file's lines are still in the changed-line gate's range, so
  the named exposure is still live — signal, not noise).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_slice_closeout_new_pool_advisory.py | action: fix | note: test_module_import_has_no_sys_side_effects was vacuous (trivially true after import) and nothing pinned the run_slice_closeout call site. Fixed: replaced with a call-site pin asserting both the rebinding identity and the invocation string.
- F2 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_slice_closeout_new_pool_advisory.py | action: fix | note: the fires-test asserted the slogan but not the implementation-discipline.md pointer, which is the issue Destination's load-bearing part. Fixed: assertion added.
- F3 | bin: bundle-anyway | evidence: weak | ref: scripts/slice_closeout_advisories.py _added_vs_base | action: document | note: anchor checks base:<path> directly, not merge-base(base, HEAD); a file deleted upstream reads as added and fires a spurious advisory-only line. Recorded as a code comment.
- F4 | bin: valid-but-defer | evidence: weak | ref: tests/quality_gates/test_slice_closeout_base_range.py seeded-repo pattern | action: defer | note: an end-to-end positive (seeded tmp repo with local origin/main) would exercise the unmocked glue; the piecewise real-git tests + the live demo on this goal's own new module cover the seams today.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: bounded fresh-eye subagent reviewer (separate agent context, read-only, prior state via git show HEAD).
- Requested spawn fields: subagent_type=general-purpose, name=slice4-critique, bounded slice packet (intent, changed files, invariants, proof, out-of-scope, reviewer questions).
- Host exposure state: applied
- Application state: host-confirmed: Agent tool returned reviewer verdict with agentId a2f5a8981f7405ab3 (28 tool uses; independently re-ran the tests, the live demo, mirror cmp, and verified the monkeypatch hits the same module object import_repo_module returns).

## Fresh-Eye Satisfaction

Verdict: SHIP-WITH-NITS, no blockers (reviewer agentId a2f5a8981f7405ab3).
The reviewer confirmed the change maps exactly to #344's Destination, the
advisory cannot block (stderr-only), the degradation guard works, the pool
definition is not forked, and the recommended command + doc pointer are
real. Nits F1-F3 folded before commit; F4 recorded as deferred with the
named seeded-repo pattern.
