# Handoff Bullet Ownership Gate Critique
Date: 2026-08-12

Fresh-eye satisfaction: parent-delegated (four rounds, nine bounded reviewers total, each spawned unnamed as `bounded-reviewer`; boundary fingerprint snapshot/verify clean around every round)

## Decision Under Review

Whether the new handoff ownership gate — every list entry in `## Current State`
and `## Next Session` must carry a markdown link, an inline command, or an issue
id — may ship as a blocking floor in a PUBLIC skill package, and whether the
claims made for it in `9930d425` survive their own sources.

## Failure Angles

- Verdict-logic correctness: false negatives that launder an unowned entry, and
  false positives that reject markdown an author would legitimately write.
- Portability and contract agreement: does the skill prose, the run planner, the
  scaffold stub, and the validator describe one rule, and is it safe as an export.
- Claim fidelity: does each commit-message claim have a channel that could have
  falsified it, and do the repaired handoff entries carry real ownership.

## Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: fix | note: a fence attached across arbitrary intervening content, so the ledger block permanently exempted the last `## Current State` bullet of the live artifact
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: fix | note: the fence toggle was the plain form `scripts/markdown_doc_scan.py` documents as wrong; a tilde line inside a backtick fence inverted state for the rest of the section
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: fix | note: section bounds ignored fences, so a fenced heading bound the section to the EXAMPLE and the real section was never scanned
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: fix | note: an unbalanced backtick turned the rest of the entry into a "command" — same laundering class as the two-span regex bug the slice was fixing
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: fix | note: the issue-id pattern had no left boundary, so `issue<id>` and `guide.md<anchor>` read as owners while the sibling count rule in the same validator already carried the guard
- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: fix | note: a double-backtick span read as two empty spans, rejecting the exact command form an author must use when the command contains a backtick
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: fix | note: a list marker indented one space was dropped entirely rather than checked, and a multi-paragraph item carrying its owner in the second paragraph was charged as unowned
- F8 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/SKILL.md | action: fix | note: the motivating incident happened in `## Workflow Trigger`, a section this rule does not read, while the docstring and commit called it the measured cost
- F9 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/references/spill-targets.md | action: fix | note: a forced refresh read modelled replacement bullets as backticked paths, the exact shape the new gate rejects
- F10 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/plan_handoff_run.py | action: fix | note: the planner computed `unowned_entries` but excluded them from `status`, so a draft the gate would refuse reported `ok`
- F11 | bin: think-more | evidence: moderate | ref: docs/handoff.md | action: fix | note: the thesis link added to the recent-lessons item points at an artifact holding unimplemented proposals, one of which is the filter the entry forbids; the design has no artifact yet
- F12 | bin: think-more | evidence: moderate | ref: scripts/validate_handoff_artifact.py | action: defer | note: the no-grandfather rationale was borrowed from a rule that fires on a defect being PRESENT, while this one fires on absence and can reject every bullet of an otherwise clean consumer handoff
- F13 | bin: think-more | evidence: moderate | ref: skills/public/handoff/scripts/handoff_bullet_ownership.py | action: accept | note: the issue-id form is GitHub-shaped, so a tracker using `PROJ-123` has two owner forms rather than three until an adapter names its id shape
- F14 | bin: over-worry | evidence: weak | ref: scripts/doc_authoring_rules.py | action: defer | note: the authoring preflight does not render this rule, against that module's "no second copy of any rule text" promise; real, but the planner status now carries the forecast

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (typed read-only agent; Read/Grep/Glob only)
- Requested spawn fields: `subagent_type=bounded-reviewer`, no host addressing `name`, three
  independent angle-scoped prompts
- Host exposure state: applied
- Application state: host-confirmed: each reviewer enumerated its own visible tool set as
  Read/Grep/Glob and named the absence of Bash/Edit/Write/Agent; two declined to run commands they
  wanted, listing the evidence they could not fetch, and the boundary fingerprint verified clean
- Delivery state: findings-received

## Boundary Ownership

- Verdict: owned-correctly

The predicate ships with the skill package for the same reason the content
budget does — the run planner and the repo gate must agree on what counts as an
owner. The enforced sections and the ceiling stay with the repo validator. F13's
tracker-shape gap is the one seam that belongs in an adapter and is recorded
rather than resolved here.

## Rounds 2-4

Round 1's findings above are the ORIGINAL gate. Three further rounds read each
successive repair, and every one of them found the repair carrying the class it
fixed — the pattern the operating contract's two-round rule predicts, measured
three times in one slice.

- Round 2 (repairs of F1-F10): two repairs COLLIDED. Closing an entry at a fence
  cleared the same variable the indent rule read as "no parent", so a child
  after its parent's own code block was charged for a pointer the parent had.
  The fence detachment also rested on a blank line nothing requires.
- Round 3 (repairs of round 2): the inheritance merge ran BACKWARDS — it pooled
  the child's text into the parent's, so a child's link laundered an unowned
  parent. The HTML rule added in round 2 fired on `<https://...>` autolinks, one
  of this rule's own owner forms, and discarded the rest of the bullet. Path
  acceptance contradicted two shipped surfaces.
- Round 4 (repairs of round 3, after the operator narrowed the contract to a
  flat link list): the parser core verified clean against every earlier input,
  but the merge still laundered an ATTACHED child, and four prose surfaces still
  stated the pre-narrowing rule.

## Disposition

F1-F10 repaired. F11 repaired by removing the wrong pointer and routing the item
to a spec that does not exist yet. F12, F13, F14 recorded and not resolved.

F7's second half was REVERSED rather than kept: round 1 made a multi-paragraph
item find its owner in the second paragraph, and the narrowing deliberately
charges it as unowned again, because supporting that shape was one of the
branches whose interaction produced rounds 2 and 3. F1's repair was superseded
rather than kept — a fence now attaches to nothing at all.

The narrowing removed fence attachment, the sub-bullet merge, multi-paragraph
entries, the HTML rule, and path acceptance. Round 4's own repairs — skipping a
child instead of merging it, a two-space child indent, and four prose surfaces
— are ACCEPTED-UNREVIEWED: the contract caps rounds at two, the operator
authorized four, and no reviewer has read what round 4 motivated.
