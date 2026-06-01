# Post-Commit Subagent Critique: Reviewer Tier, #275, #276

Date: 2026-06-01
Target: local commit `98892bd Resolve reviewer tier issue closeout`
Goal: `charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md`
Packet: `charness-artifacts/critique/2026-06-01-131726-packet.md`

## Execution

The operator asked for one more subagent critique after the local closeout
commit. The parent spawned three bounded read-only angle reviewers and one
separate counterweight reviewer. Reviewers were instructed not to edit files,
not to run worktree- or index-mutating git commands, and not to spawn nested
subagents.

Fresh-Eye Satisfaction: parent-delegated.

## Target

Code critique of the unpushed #275/#276 closeout carrier before push or remote
issue closure is claimed.

## Angles

- Michael Jackson problem framing: check whether the change solves the named
  #275/#276 problems rather than an adjacent subset.
- Gerald Weinberg diagnostic/root-cause: check whether installed-layout lookup,
  fallback diagnostics, and discussion-readiness semantics fix the cause.
- Atul Gawande operational/checklist: check whether operator-visible diagnostics
  and closeout gates are actually surfaced in the normal flow.
- Counterweight: separate skeptical triage of all angle concerns.

## Findings

Act Before Ship:

- #276 heading-form `Discuss before activation` could be empty but followed by a
  same-level heading and still count as non-empty. Disposition: fixed by ending
  heading summaries at the next same-or-higher heading and requiring
  non-heading content.
- #276 did not scan `## Non-Goals`, even though close/push restrictions often
  live there. Disposition: fixed by scanning `Non-Goals` and documenting the
  contract.
- #275 diagnostics were emitted by `parse_handoff_entries.py` but dropped by
  `propose_merges.py`, so parse-to-propose operator flows could still hide
  issue-source failures. Disposition: fixed by preserving
  `issue_source_diagnostic` in proposer output.
- #275 installed issue lookup could walk out of the current package root into an
  ancestor source tree. Disposition: fixed by resolving only the current source
  or installed package root.

Bundle Anyway:

- `draft_goal_from_chunk.py` preferred source-layout achieve before
  installed-layout achieve when both existed. Disposition: fixed while touching
  the same package-root resolver shape.
- The initial post-commit packet was generated from the clean worktree and said
  no changed paths. Disposition: regenerated with `--commit 98892bd`.
- #276 summary detection accepted labels anywhere in the artifact. Disposition:
  tightened to ignore stale summaries after `## Slice Log`.

Valid but Defer:

- Broader issue-source config diagnostics remain a separate diagnostics contract.
- Shared cross-skill resolver unification remains a separate runtime-resolver
  design slice.

Over-Worry:

- Requiring live GitHub closure before local push contradicts the explicit
  non-claim boundary; remote closure remains pending explicit push request.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_discussion.py | action: fix | note: heading-form discussion summary could be structurally present but empty
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_discussion.py | action: fix | note: Non-Goals close and push restrictions were not scanned for consequential decisions
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/propose_merges.py | action: fix | note: parse-to-propose flow dropped issue_source_diagnostic
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_issue_backend.py | action: fix | note: installed issue lookup could walk into an ancestor source tree
- F5 | bin: bundle-anyway | evidence: moderate | ref: skills/public/handoff/scripts/draft_goal_from_chunk.py | action: fix | note: installed achieve lookup should prefer installed layout when handoff is installed
- F6 | bin: bundle-anyway | evidence: moderate | ref: charness-artifacts/critique/2026-06-01-131726-packet.md | action: document | note: packet regenerated with the target commit ref
- F7 | bin: bundle-anyway | evidence: moderate | ref: skills/public/achieve/scripts/goal_artifact_discussion.py | action: fix | note: stale Slice Log discussion text should not satisfy current activation readiness
- F8 | bin: valid-but-defer | evidence: moderate | ref: skills/public/handoff/scripts/chunked_routing_issue_source.py | action: defer | note: broader issue-source config diagnostics belong to a later diagnostics slice
- F9 | bin: valid-but-defer | evidence: moderate | ref: skills/public/handoff/scripts/chunked_routing_issue_backend.py | action: defer | note: shared cross-skill resolver unification is larger than the #275/#276 carrier
- F10 | bin: over-worry | evidence: strong | ref: charness-artifacts/goals/2026-06-01-reviewer-tier-closeout-and-issue-275.md | action: document | note: live GitHub closure is intentionally not required before explicit push

## Next Move

Run changed-surface validators again, update the closeout carrier evidence, and
commit the critique fixes locally without pushing.
