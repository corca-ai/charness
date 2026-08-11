# Handoff Bullet Ownership Gate Critique
Date: 2026-08-12

Fresh-eye satisfaction: parent-delegated (three bounded reviewers, spawned unnamed as `bounded-reviewer`; boundary fingerprint verify clean)

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

## Disposition

F1-F10 repaired in this slice, each with a regression test naming the input that
passed the first implementation. F11 repaired by removing the wrong pointer and
routing the item to a spec that does not exist yet. F12, F13, F14 recorded and
not resolved.

The repaired surface has NOT been read by a fresh context: this is round 1, and
a slice changing verdict logic on a proof surface owes a second round reading
the repairs. That round is owed and unproven.
