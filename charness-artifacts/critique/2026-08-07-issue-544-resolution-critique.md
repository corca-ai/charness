# Issue #544 Resolution Critique
Date: 2026-08-07

## Decision Under Review

Resolving `#544` by partitioning runtime samples into `<profile>.<regime>` when a
run's gate set differs from the standard battery, while changing no budget bar and
adding no refusal — against an issue whose stated cause (contention drift, a
one-way ratchet) two delegated reviews and direct measurement largely refuted.

## Failure Angles

- **Fixing a different problem than the reporter has.** The issue asks for relief
  from false reds; this slice repairs measurement attribution and explicitly
  declines to raise the bars the reporter expected to move. If the reporter's real
  pain is a blocked push, they get no relief today.
- **Teeth loss.** Re-keying samples away from the enforced profile could leave a
  budgeted label with an empty window. Round 1 traced this: a sampleless budgeted
  label WARNs and exits 0, so the loss would be silent.
- **A carve-out that does not fire, or fires wrongly.** `#534` in this same goal
  shipped seven passing tests over code no input could reach.
- **The fix carrying the class it fixes.** A regime derived from an ambient
  variable is itself ambient state leaking across a boundary.
- **Claims outrunning code.** Every doc and artifact sentence asserting "the
  profile key distinguishes gate sets" is broader than a fix that lumps every ad
  hoc filter into one bucket.
- **Incomplete partition.** Handling the narrowing direction only, while a widening
  opt-in still contaminates the enforced window.

## Counterweight Pass

Real, and acted on before shipping: the ambient-leak angle was not theoretical —
round 1 predicted three specific test failures from it and execution confirmed
exactly those three. The incomplete-partition angle was also real twice over: the
first fix handled narrowing only, and the first repair of that handled one opt-in
by name while a structurally identical second went untouched.

Over-worry, after checking: teeth loss cannot be caused by this change. Re-keying
requires a non-standard run, and a non-standard run means that label simply was not
measured under the enforced regime; the prior twenty samples stay. The underlying
sampleless-exits-0 hole is real but pre-existing, and is now `#546` rather than a
blocker here.

Not over-worry but correctly scoped: "fixing a different problem". The reporter's
premise was measurably wrong — `check-secrets` returned to 15,679 ms from its
17,669 ms peak inside the same window — so raising bars would have encoded noise as
a permanent loosening. Declining is the right call, but it owes the reporter an
explicit decision rather than silence, which the close comment gives.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/conftest.py:37 | action: fix | note: the exported regime leaked into the pytest gate and reddened three recorder tests; reproduced with `CHARNESS_RUNTIME_REGIME=filtered pytest`, fixed by scrubbing it and `CHARNESS_RUNTIME_PROFILE` session-wide
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:78 | action: fix | note: only the narrowing direction was handled; `CHARNESS_QUALITY_DEAD_CODE=1` widened the battery with no filter and still reached the enforced window
- F3 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:86 | action: fix | note: the widening repair named one opt-in; `CHARNESS_SUPPLY_CHAIN_ONLINE` has the identical shape, so the tokens are now enumerated and composed rather than special-cased
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/debug/2026-08-07-issue-544-runtime-budget-regime-mixture-debug.md:104 | action: fix | note: the carrier claimed "four runner tests, three mutants" against six and ten actual; counts now restated from a re-run of the full mutation set, not from memory
- F5 | bin: act-before-ship | evidence: moderate | ref: skills/public/quality/references/standing-gate-verbosity.md:118 | action: fix | note: "a run that merely narrows or widens the standard battery is regimed automatically" was false in both directions; narrowed to what the code does and states what it deliberately does not regime
- F6 | bin: act-before-ship | evidence: moderate | ref: scripts/run-quality.sh:295 | action: fix | note: the comment claimed a regime on the aggregate path was unreachable, which the widening arm made false; the aggregate is regimed through the export, and now has an assertion
- F7 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/scripts/check_runtime_budget.py:118 | action: file-issue | note: a budgeted label with no sample WARNs and exits 0, so a bar can be permanently unenforceable; pre-existing and not reachable from this change | follow-up: https://github.com/corca-ai/charness/issues/546
- F8 | bin: valid-but-defer | evidence: strong | ref: scripts/validate_issue_source_freeze.py:114 | action: file-issue | note: `refreeze` re-stamps all 19 locator digests silently, so a one-file re-bind can launder unreviewed drift; verified by git diff that only `scripts/run-quality.sh` moved on both runs here | follow-up: https://github.com/corca-ai/charness/issues/547
- F9 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/runtime_budget_lib.py:256 | action: document | note: feared teeth loss from an emptied window; a re-keyed run means the label was not measured under the enforced regime and the prior twenty samples remain, so the enforced verdict is unchanged
- F10 | bin: over-worry | evidence: moderate | ref: scripts/run-quality.sh:905 | action: document | note: the agent-browser gates looked like unhandled widening cases; they are queued and flushed in their own phase, so they compete with nothing and change no sibling's sample
- F11 | bin: valid-but-defer | evidence: moderate | ref: scripts/run-quality.sh:774 | action: defer | note: `check-coverage` is conditionally queued, so `--read-only` runs a slightly smaller standard battery unregimed; splitting the dominant sample population over a one-gate delta costs more evidence than it buys, and the docs now say so rather than claiming otherwise

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded reviewer (`bounded-reviewer` typed agent), three spawns — causal review before design, implementation round 1, implementation round 2 on the repairs.
- Requested spawn fields: subagent_type `bounded-reviewer`, no host addressing name, read-only toolset (Read/Grep/Glob).
- Host exposure state: host-defaulted
- Application state: host-confirmed: all three spawns returned findings inline; each reported `envelope-unbound`/`envelope bound as expected` with no Bash, Edit, Write, or Agent tool visible.
- Delivery state: findings-received

Per-host note: this is a Claude Code host, so the repo's Codex-only `gpt-5.6-terra`/`medium` request does not apply; typed `bounded-reviewer` agents with session-model inheritance were used instead, which is contract-conformant rather than a degradation.

## Fresh-Eye Satisfaction

`parent-delegated`. Three bounded reviewers, each in a distinct context, each
boundary-fingerprinted with `reviewer_boundary_fingerprint.py`
snapshot/verify — windows `w-20260807T060625Z-805735`,
`w-20260807T063258Z-907199`, and `w-20260807T065338Z-1004980`, all three verifying
`clean` with empty drift.

Round 2 earned its place: it caught F4 (a false proof count in the closeout
carrier) and F3 (the second opt-in the first repair missed), neither of which round
1 could have seen because both were introduced BY round 1's repairs. That is the
second-round rule paying for itself as the contract predicts.

## Reviewed Input Identity

<!-- No packet consumed: this critique binds to the issue body, the working tree at review time, and the three reviewer reports, all cited inline above. -->

## Boundary Ownership

- Producer: `scripts/run-quality.sh` and `scripts/record_quality_runtime.py`, which observe the run's gate set and write the sample.
- Consumer: `skills/public/quality/scripts/check_runtime_budget.py`, which reads a window and renders a pass/fail verdict against a committed bar.
- Owning surface: the quality runtime-signals recorder and its profile key, exported through the `quality` public skill and mirrored into `plugins/charness/`.
- Verdict: owned-correctly
