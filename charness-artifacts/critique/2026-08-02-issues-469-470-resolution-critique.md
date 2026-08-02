# Resolution Critique — issues #469 and #470
Date: 2026-08-02
Issues: corca-ai/charness#469, corca-ai/charness#470
Classification: bug

## Decision Under Review

Whether #469 and #470 may be closed against commits `cf88b750` and `31303275`,
given that **neither issue's full requested outcome was delivered** and both
bodies had to be corrected first. Also under review: whether the closes are
themselves honest at an irreversible public boundary.

This critique runs BEFORE the close call. That ordering is the thing #470's
follow-up (b) exists about, so getting it backwards here would be the defect
closing its own issue.

## Failure Angles

- **Closing on a shrunken denominator.** The exact failure #470 catalogues: pick
  a scope in which the metric reads clean, then close. For #469 the tempting
  version is "the payload improved, therefore the issue is fixed" — when the
  issue's TITLE describes a behaviour that still exists.
- **Ratifying a false description.** #470's second follow-up asserted the
  precondition does not fire before the close. It does. Closing it as written
  would put a repo-endorsed wrong fact into a closed record.
- **Closing a body-edited issue and calling it resolution.** Editing an issue so
  it matches what was built is one keystroke away from moving the goalposts.
- **The close comment being the only observer of itself.**

## Counterweight Pass

- **The #469 close is defensible, but only in the narrow form.** The disclosure
  defect is genuinely and completely gone, with a machine-readable pair on every
  payload-emitting site and a control test proving the verdict did not move. The
  refusal question is not being quietly dropped — it is **D40**, it is an operator
  toll decision by the repo's own contract, and the corrected body plus the
  handoff both name it. (The first draft of this paragraph said D45, and the
  pre-close review stopped the close over it — see F0.) What would NOT be defensible is closing it as "the gate
  no longer passes over a partial denominator", and the closing comment must not
  say that.
- **The body edits are corrections, not goalpost moves, and the distinction is
  checkable.** Neither edit changes an observation. #469's edit adds a resolution
  section that states plainly what was not fixed. #470's edit corrects a factual
  claim about the tree that a plan critique disproved by reading
  `issue_close.py:87-92`, and it marks the correction inline rather than
  silently rewriting. A reader of either body can still see what was originally
  observed.
- **The strongest argument for leaving both open** is that #469's title stays
  true after the close. The counter is that an issue is a unit of work, not a
  permanent assertion, and the residual has a better home (D40) than a
  half-closed issue that reads as unfinished work rather than as a decision
  awaiting an operator. That argument is why the closing comment must carry the
  residual explicitly rather than by link alone.

## Structured Findings

- F0 | bin: act-before-ship | evidence: strong | ref: docs/deferred-decisions.md:498 | action: fix | note: THE CLOSE-STOPPING FINDING. This critique's first draft transferred #469's residual to **D45**, which is the CI/local parity gate and has nothing to do with the changed-line lane. The residual would have been filed nowhere — losing it at the close, which is the exact failure #470 catalogues, committed while closing #470. The correct owner is **D40** ("No pre-landing lane BLOCKS an unproven changed line"), whose own text was also stale ("the lane that runs before a landing exits 0 by construction", falsified since this lane began exiting 1). Origin: D45's text calls its call "the same class of call as D40", and an analogy was upgraded to an ownership claim, then copied into five surfaces including shipped code. D40 now records the residual; every surface is repointed.
- F1 | bin: act-before-ship | evidence: strong | ref: scripts/prepush_focused_changed_line_coverage.py:392-402 (`_verdict_from_consumer`; there is no `_derive_status` in the tree) | action: document | note: #469's titled behaviour STILL EXISTS — with unanalyzed pool files the payload carries no `reason`, so status derives to `clean` and `--refuse-unestablished` never fires. Verified by reading the status derivation, not assumed from the lane's improved payload. The close comment must state this, and the body now does.
- F2 | bin: act-before-ship | evidence: strong | ref: https://github.com/corca-ai/charness/issues/470 | action: fix | note: #470's follow-up (b) asserted the resolution-critique precondition does not fire before the close; `issue_close.py:87-92` raises before `_run_backend`. Corrected inline with a marked CORRECTION block rather than a silent rewrite, so the mis-statement and its repair are both legible.
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/goals/2026-08-02-make-a-verdict-state-its-denominator-and-move-the-fresh-eye-round-before-the-boundary.md | action: document | note: #470 follow-up (a) was CUT because no `goal_artifact_*` FLOOR performs a corpus measurement — every one is a per-artifact `check(text)`. The CATEGORICAL version ("the helper would have had no caller") is FALSE and was caught here: `skills/public/achieve/scripts/audit_disposition_corpus.py:83` globs the goal corpus, drives the same Created-gated family, and its summary emits `pre_rule_grandfathered` / `in_scope` while never stating the DATED denominator — #470(a)'s defect, live, in the one corpus-measurement surface the achieve skill ships. The cut stands (a floor helper had no floor caller); the body must name that surface rather than imply a clean sweep.
- F4 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/critique/2026-08-02-issues-469-470-resolution-critique.md | action: fix | note: this close is the first real exercise of the floor built for #470, so the critique it cites must itself satisfy that floor — a `parent-delegated` record, not a self-authored one. If the fresh-eye round below had not returned, the honest move would have been `blocked <host-signal>`, not a close.
- F5 | bin: over-worry | evidence: weak | ref: https://github.com/corca-ai/charness/issues/469 | action: defer | note: the concern that editing a body before closing is goalpost-moving. Checked and rejected on the specific edits: both preserve the original observation verbatim and add clearly-marked resolution/correction sections. Recorded because the concern is right in general.

## Behavioral Verdict

The behavior each issue asked about, checked on a channel distinct from the
commit that changed it:

- **#469's disclosure:** every payload-emitting site in the consumer carries the
  key — stated as the checkable claim rather than as a count, because "eight
  paths" did not reproduce for a reviewer who counted seven emit sites. The live
  pre-push run on this session's own push emitted
  `"changed_pool_file_counts": {"analyzed": 7, "changed": 7}` in its payload —
  the pair present on a real verdict, from the gate as wired into the hook. Noted
  precisely: `analyzed == changed` is the case where nothing was left out, so this
  is a live proof that the KEY is present, NOT a live proof of the partial shape
  #469 filed (`49 of 51`). That shape is proven deterministically, in
  `test_a_partial_denominator_states_both_numbers_on_a_passing_run`.
- **#469's residual:** read directly out of the status derivation
  (`prepush_focused_changed_line_coverage.py:392-402`), which is why F1 is stated
  as a live defect rather than as a closed one.
- **#470's floor — stated with its real channel, because the first draft got this
  wrong.** That draft cited the pre-push gate refusing this session's first push.
  That gate is #469's subject; its refusal proves the new modules are line-covered
  and says nothing about whether `close-with-comment` refuses an undelegated
  critique. Mislabeling it was structurally the #467 defect: citing a green from a
  run whose scope never contained the question. The refusal arm's real proof is
  deterministic, not live — `test_a_self_authored_critique_is_refused_at_the_close_boundary`
  and `test_an_absent_field_is_refused_under_the_contract_and_silent_without_it`,
  with the contract's liveness pinned by
  `test_the_delegation_contract_is_live_in_this_repo`. The corpus measurement
  (0 of 133) is the NON-refusal direction. **The only live exercise available is
  this close itself, and it exercises the PASS path.**

## What stops this class from recurring

The recurrence is not "an issue gets closed early". It is **closing on the half
of the ask that was easy to satisfy, and letting the title carry the other half
away silently**. Two things stand against it now, and only one is structural:

1. Structural: the close boundary refuses a resolution whose critique records no
   distinct observer, so a closure cannot be its own only witness. That is what
   this close exercises.
2. Not structural, recorded honestly: "state the residual in the closing comment,
   not only in a linked decision record" is discipline. No gate reads a closing
   comment for whether the residual it omits exists.

## Sibling search

- The same "resolved the disclosure, left the refusal" shape is available in every
  gate that warns and passes. Not audited this run — a non-claim, not a clean
  finding. Carried to the handoff.
- #471 is the sibling found while building: a guard whose own activation condition
  was never tested. Filed, not fixed, because repairing it arms a dormant gate
  across 400+ artifacts.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (this repo's typed read-only reviewer agent).
- Requested spawn fields: `subagent_type: bounded-reviewer`, `run_in_background: false`, no host addressing/team `name` (an addressed spawn routes onto a teammate protocol whose retrieval tool is not exposed here). No model/effort override: on a Claude Code host the per-host contract uses session-model inheritance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: the spawn returned findings inline in this session, and the reviewer reported its own envelope as Read/Grep/Glob only.
- Delivery state: findings-received

Parent-side boundary integrity: `.charness/reviewer-boundary/issues-469-470.json`,
verified `clean` with empty drift on the reviewer's return, before any parent
write.

**What the round actually found, recorded because a tier block that says a
reviewer ran and not what it said is exactly half a record** — on #467 the
reviewer's FINDINGS were the whole story:

- **It stopped the #469 close.** Verdict: "#470: close. #469: do NOT close as
  prepared." Cause: F0 above.
- Two further blockers, both folded: the categorical follow-up-(a) claim (F3), and
  the Behavioral Verdict citing #469's gate as evidence for #470's floor.
- It independently confirmed F1 (tracing five hops from the wrapper's
  `--limit-to-file` construction to `main`'s return), F2, and that this artifact
  passes the very floor it is about to be cited under — including that the
  `parent-delegated` inside F4's prose does not become the record, because the
  `##` section wins.
- It flagged one mechanical trap that changed how the closes are executed: a bare
  `Critique: <path>` line binds to nothing when more than one issue number is in
  scope, so each close is issued singly.

**One honesty item it raised that the floor structurally cannot catch:** the
`Application state` and `Delivery state` lines above were written BEFORE this
round returned. They are true now, and they were a pre-write when authored. That
is precisely the gap the coordination rule concedes stays discipline — the teeth
cannot see a claim written before the review it describes — and the first
exercise of the new ordering committed it. Recorded rather than quietly
backdated.

**Ordering, stated because it is the point:** this round ran BEFORE the
`close-with-comment` call. On #467 the equivalent round ran ten minutes after the
close and forced a public correction on an already-closed issue.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; the reviewer received an inline brief naming both issues, the corrected bodies, the two commits, the specific claim that #469's titled behaviour survives, and the question of whether closing either is honest. The binding floor is therefore off by design, and this critique does not claim packet-bound identity. -->

## Boundary Ownership

- Producer: the two closing comments, and the corrected issue bodies.
- Consumer: anyone reading #469 or #470 later as a record of what this repo decided, plus the D40 decision record that inherits #469's residual.
- Owning surface: the issues own their observations; D40 owns the transferred toll decision; the goal artifact owns the delivery evidence.
- Verdict: single-surface
