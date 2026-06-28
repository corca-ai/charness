# Critique Review
Date: 2026-06-28

## Decision Under Review

Issue #406 "Reduce achieve closeout authoring churn" resolved via 4 levers, all
in the working tree (uncommitted): B1 (a new `join_soft_wraps()` in
`goal_artifact_markdown.py`, wired into the phase-routing and coordination floors
so a soft-wrapped `Routing:`/`Gather:`/`Release:`/`Issue closeout:` step value is
no longer false-rejected); A (template seeds a backticked one-line `Routing:`
stub and an un-backticked `Discuss before activation: fill — ...` line, with the
pinned producer test updated in lockstep); B2 (`describe_goal_closeout_shape.py`
surfaces the Operator Decision Queue scaffold-clear requirement); D (describe-first
rejection text in `goal_artifact_operator_queue.py` and
`validate_critique_artifacts.py`); C (one unifying paragraph in
`docs/conventions/implementation-discipline.md`).

## Scope

Read-only fresh-eye resolution critique in the shared parent worktree. Inspected
the working-tree diff and the floor/describe/template/test source directly; ran
ad-hoc read-only Python to probe the floors against adversarial inputs; ran the
targeted and full quality-gate suites, markdownlint, and the doc-link checker. No
index- or worktree-mutating git ops. Out of scope: the eventual `Close #406`
push (a publication surface, not a behavior this critique can roundtrip).

## Failure Angles

- F-angle 1 (the load-bearing one): does `join_soft_wraps` over-join so an
  adjacent field's value or unrelated prose merges into a `Routing:`/`Gather:`
  value and FALSELY satisfies a floor? Verified by construction with concrete
  adversarial inputs (see Structured Findings F1). Result: field labels, list
  items, headings, and table rows are correctly NOT joined; a blank line is not
  bridged across into the step line; BUT a non-blank PROSE continuation line IS
  joined into the preceding step value. That widens acceptance in exactly two
  content-checks layered on the otherwise presence-only floors: the routing
  `_skill_named` skill-name match, and the opt-out `>=30` char reason length.
- F-angle 2: do the template seeds defeat their floors? Verified false — the
  `Routing: find-skills -> <skill>` stub returns `(None, None)` for every real
  skill (impl/debug/quality/issue); the `Discuss before activation: fill — ...`
  seed is present-but-UNRESOLVED when a trigger fires (does not match
  `resolved/confirmed/approved`); neither seed is flagged by the section-placeholder
  floor; markdownlint is clean.
- F-angle 3: A lockstep — producer template and pinned test changed together and
  the test asserts the new seeds and their placement. Verified true.
- F-angle 4: B2 drift — does describe re-implement floor logic? Verified false;
  the new row reads `ev["operator_decision_queue"]` (applies/ok/reason) live,
  identical to the sibling `closeout_delegation`/`section_placeholders` rows.
- F-angle 5: D semantics — do the operator-queue / critique-validator edits change
  what passes/fails, or only message text? Verified message-only; branch
  conditions and `ok`/`applies` unchanged; old exact-equality test assertions
  were RELAXED to substring + a NEW scaffold-branch test added, not deleted to
  hide a regression.
- F-angle 6: C doc — links resolve and no false claim? Verified; all three
  `../../scripts/...` targets exist, `check_doc_links.py` passes, and the
  "~20+ chars" claim matches the `_EMPTY` regex (`none — ` + 21+ chars).

## Counterweight Pass

- The F1 widening is REAL but is the inseparable shadow of the intended fix, not
  an oversight: the join cannot distinguish a legitimately-wrapped step value
  (which #406 WANTS to accept) from a step value followed by unrelated prose that
  happens to contain the skill word or extend the reason length. The author's own
  new tests (`test_phase_routing_satisfied_when_routed_skill_wraps_to_continuation`,
  `test_gather_optout_satisfied_when_reason_wraps_to_continuation`) encode this
  acceptance deliberately. So invariant #1 as literally worded ("must NOT widen
  what the floors accept") is technically violated, but the widening is intended
  and bounded.
- Stakes are low per the north star: these are reversible, self-authored goal-
  artifact closeout floors, where the floor author and the author being gated are
  the same agent. The floors are explicitly presence-only ("a real reference's
  content is never judged"); the two content-checks the join can perturb are the
  only non-presence edges, and exploiting them requires an author to write a
  wrong/short step line immediately followed by prose that happens to complete it
  — an unusual self-inflicted shape, not an escape vector for a wrong answer that
  reaches an irreversible boundary.
- recent-lessons corroborates the JTBD fit: the #405 retro recorded the exact
  `Discuss before activation:` placement/wording friction (summary must precede
  `## Slice Log` and begin `resolved/confirmed/approved`) and named a describe-first
  seed as the remedy — which is precisely what lever A ships.

## Per-Issue Behavioral Verdict

- classification: local-only-by-contract. #406 is a local achieve skill-tooling
  change — no runtime, provider, connector, or live-boundary behavior is in its
  acceptance surface. The reporter JTBD ("closeout authoring churn reduced") is
  verified ACHIEVED through channels DISTINCT from any future CLOSED state:
  - Floors stop false-rejecting wrapped lines: confirmed by the two new
    regression tests passing AND by my own ad-hoc replay of the legit-wrap shape
    through `apply_phase_routing_floor` / `apply_coordination_floors`.
  - Template seeds the correct shape: confirmed by running the live template
    through the phase-routing, discussion, and section-placeholder floors plus
    the pinned producer test and markdownlint.
  - ODQ requirement surfaced up front: confirmed by reading the live
    `describe_goal_closeout_shape.required_shape()` / `_floor_rows` output, which
    now carries the scaffold-clear row sourced from the live floor verdict.
  - Rejections show the target shape: confirmed by the updated operator-queue and
    critique-validator message text and the substring assertions in their tests.
  The JTBD is met; the F1 widening is a documented bounded side effect, not a JTBD
  failure.

## Operator Action Required

- None blocking. Recommended (non-blocking): when committing, capture the F1
  widening as a known, intended tradeoff (the join cannot separate a legit wrap
  from prose-completion) so a future reader does not mistake it for invariant #1
  being fully upheld. The change is otherwise ready to commit with its
  `charness-artifacts/` updates and the byte-matched `plugins/` mirror.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_markdown.py:53 | action: document | note: join_soft_wraps joins a prose continuation into a step value, so a wrong/short Routing or opt-out line completed by the next prose line false-accepts — verified by ad-hoc replay (impl-only required, satisfied flipped True); inherent to the fix and intended by the author's own tests, low-stakes self-authored presence-only floor, so document the bounded tradeoff rather than block.
- F2 | bin: over-worry | evidence: moderate | ref: skills/public/achieve/scripts/goal_artifact_markdown.py:36 | action: defer | note: the docstring/comment says "a blank line breaks joining" but a blank line is appended and the next prose line joins onto the empty line (the step line is preserved intact, so the net effect is safe) — wording is slightly imprecise, not a behavior bug.
- F3 | bin: valid-but-defer | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_template.md:96 | action: defer | note: template seeds verified non-satisfying (Routing stub -> (None,None) for every skill; Discuss seed stays unresolved on trigger; neither tripped section-placeholder; markdownlint clean) — no action needed, recorded as a positive verification.
- F4 | bin: valid-but-defer | evidence: strong | ref: skills/public/achieve/scripts/describe_goal_closeout_shape.py:206 | action: defer | note: B2 reads ev["operator_decision_queue"] live with no re-implemented floor logic; D edits are message-only with branch conditions unchanged and tests relaxed-not-deleted plus one new scaffold test — both invariants hold, no action.

## Reviewer Tier Evidence

- Requested tier: standard
- Requested spawn fields: model=opus (Claude Code host)
- Host exposure state: requested_fields_sent
- Application state: host signal: the Claude Code Agent tool spawned this bounded fresh-eye resolution critic to review #406

## Fresh-Eye Satisfaction

parent-delegated: bounded fresh-eye resolution critic reviewed the #406 diff directly via the host Agent surface.
