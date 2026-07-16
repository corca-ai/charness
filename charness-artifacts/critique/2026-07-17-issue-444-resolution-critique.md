# Critique Review
Date: 2026-07-17

## Decision Under Review

Issue #444 resolution: the commit-msg closeout hook
(`scripts/check_issue_closeout_commit_msg.py`) gains a pause carve-out — a
staged pausing resolution brief (an `Autonomous vs pause:` field in a pause
state) whose issue numbers are not close-keyworded by the commit message is
verified against a single unconditional `AI-provenance:` presence floor
instead of the full closeout ledger — plus a bold-tolerant
`_CLASSIFICATION_RE` so the brief template's `**Classification**:` form
classifies as written. `skills/public/issue/references/resolution-brief.md`
Persistence prose updated to match the actual gate predicate; plugins/
mirror synced; six regression pins added. Prior causal review:
`charness-artifacts/issue/2026-07-17-issue-444-causal-review.md`.

## Failure Angles

- Problem framing (Jackson): solving an easier adjacent problem than the
  named contract conflict; hidden scope creep in the shared regex.
- Diagnostic layer (Weinberg): carve-out patching a symptom above the
  "is this a closeout carrier?" predicate; boundary ownership between the
  brief template (producer) and hook regex (consumer).
- Operational (Gawande): silent loud→pass transitions; misleading failure
  text; template-vs-prose checklist drift.

## Counterweight Pass

- C1 | act-before-ship (fixed): a template-faithful brief carries no
  close-keyword text, so the gate never sees it and the provenance floor
  cannot fire; the first prose draft over-promised the floor for every
  pausing brief. Prose rewritten to state the recognition predicate
  honestly; a `not_applicable` pin added. Widening detection to
  `*-brief.md`/bare-`#N` was rejected: no auto-close means no escaping
  wrong answer, so a new floor there fails the north-star teeth test.
- C2 | bundle-anyway (fixed): the shared regex widening also honors a bare
  commit message's bold `**Classification**:` line — consistent with
  `_bare_classification`'s deliberate-assertion contract; pinned as
  intentional rather than silently un-deferring the causal review's parked
  sibling.
- C3 | bundle-anyway (fixed): prose said full teeth return on "the brief's
  issue number" (singular) while the hook restores the floor on any-number
  overlap; prose now says "any of the brief's issue numbers".
- C5 | bundle-anyway (fixed): `evaluate_ai_provenance` self-exempts
  question/decision-needed, letting a loosely-inferred pause brief pass with
  zero provenance; the pause path now maps floor-exempt classifications to a
  floor-applying one so the single kept requirement is unconditional.
- C4 | valid-but-defer: `_format_failure`'s generic header/footer misdirect a
  pause-only failure toward adding close keywords; the per-item line already
  names the one-line remedy. Error-string polish, separable.
- C7 | valid-but-defer: pause-marker vocabulary is duplicated between the
  template and the hardcoded regex with no drift test; a reword fails closed
  (the old refusal returns, nothing escapes).
- C6 | over-worry: a resumed brief (`paused; resumed ...`) staged with
  forgotten close keywords now passes where it failed loudly — but without
  keywords GitHub closes nothing, and a real resolution commit hits the
  overlap restoration.
- C8 | over-worry: template-copying authors do not hit a first-use reject
  because a template-faithful brief stays outside the gate entirely (C1);
  the Persistence prose documents the line for the briefs the gate does see.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/references/resolution-brief.md:76 | action: fix | note: Persistence prose over-promised the provenance floor for every pausing brief; rewritten to name the close-keyword recognition predicate, with a template-faithful `not_applicable` pin
- F2 | bin: bundle-anyway | evidence: strong | ref: tests/test_check_issue_closeout_commit_msg_inprocess.py | action: fix | note: bold bare-message classification pinned as deliberate assertion
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/issue/references/resolution-brief.md:85 | action: fix | note: singular→plural overlap wording aligned with the any-number hook behavior
- F4 | bin: bundle-anyway | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py | action: fix | note: pause provenance floor made unconditional on classification via FLOOR_EXEMPT_CLASSIFICATIONS remap
- F5 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_issue_closeout_commit_msg.py | action: defer | note: pause-case header/footer polish in `_format_failure`
- F6 | bin: valid-but-defer | evidence: moderate | ref: skills/public/issue/references/resolution-brief.md | action: defer | note: template↔regex pause-vocabulary drift test (fails closed today)
- F7 | bin: over-worry | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py | action: document | note: resumed-brief silent pass and first-use-reject fears both blocked by the no-keyword/no-auto-close boundary

## Deliberately Not Doing

- No `*-brief.md` filename or bare-`#N` detection widening: it would add a
  blocking floor to commits that cannot auto-close anything (floor-addition
  restraint; north-star teeth-only-where-escape).
- No bold-tolerance widening for `_FIELD_RE`/`_BEHAVIOR_LINE_RE`: they read
  plain commit-message text; the causal review binned them as intentional
  plain-text boundaries.

## Reviewer Tier Evidence

- Requested tier: high-leverage (issue-closeout review class).
- Requested spawn fields: adapter `reviewer_tiers.high-leverage` —
  `gpt-5.6-terra`, `medium` reasoning effort, `fork_turns: none`, priority
  tier — not exposed by this host's Agent tool (model enum is
  sonnet/opus/haiku/fable); three typed `bounded-reviewer` angle agents
  (Jackson/Weinberg/Gawande) plus one counterweight spawned with no model
  override.
- Host exposure state: host-defaulted
- Application state: read-only envelope asserted by agent type
  (Read/Grep/Glob); parent-side boundary fingerprint verify returned
  `drift: []` after the angle pass and after the counterweight pass.

## Packet Consumed

charness-artifacts/critique/2026-07-16-220649-packet.md

## Fresh-Eye Satisfaction

parent-delegated

## Boundary Ownership

- Producer: `issue` skill resolution-brief contract (template + Persistence
  prose) owns the brief shape and the pause vocabulary.
- Consumer: the repo commit-msg hook owns recognition and the residual
  provenance floor; enforcement stays in the consumer, contract prose in the
  producer.
- Verdict: owned-correctly (Weinberg angle; the duplicated pause
  vocabulary is the deferred F6 drift test, and it fails closed).
