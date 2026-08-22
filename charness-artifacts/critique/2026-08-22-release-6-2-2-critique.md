# Release 6.2.2 critique
Date: 2026-08-22

## Decision Under Review

Cutting patch release `6.2.2` from `6.2.1` to ship the `#681` cadence-owner
payload repair, its disclosure of a known over-fire, and the corrected
attention-state registry entry. The consumer-facing diff over the frozen range
`46169b7ad..5bd80a7b6` is one skill module, one registry JSON, and its tests.

## Failure Angles

- **Shipping churn for behavior nobody can use.** The whole consumer-visible
  delta is the wording of one non-blocking payload plus a paragraph on an
  already-blocking one. No verdict flips.
- **Shipping a known bug with a disclosure instead of a fix.** `#694`'s over-fire
  is not repaired; the refusal now explains itself. A disclosure can make a
  broken refusal look considered.
- **The disclosure being reachable from the true-positive side.** If a correct
  refusal can be read as the disclosed over-fire, the disclosure converts a
  working floor into a dismissed one.
- **A patch promising no behavior change while a payload string is parsed.**
- **Evidence frozen at a range the release commit will leave.**

## Counterweight Pass

- **Ship, and the reason is the tracker.** `#681` was reproduced on the
  installed `6.2.1` plugin, not only in source, and it is now CLOSED. Without a
  release the tracker asserts a fix no consumer can obtain while the published
  copy still tells its reader the frame "states no `Gate cadence:` line" and
  hands them the line number it just parsed. That is a proof surface lying to an
  operator mid-debug. A release is the only channel.
- **Real blocker, acted on before the cut.** The release reviewer found the
  disclosure's escape clause describes a shape that overlaps the scaffold's OWN
  seeded cadence line — which genuinely defers in its first clause, so refusing
  it beside a per-slice acceptance demand is a TRUE POSITIVE. A consumer
  scaffolding from the template, refused correctly, could read "known over-fire"
  and dismiss it, then run the broad suite every slice: the measured waste this
  floor exists to prevent. Verified against
  `goal_artifact_scaffold.DEFAULT_DRAFT_ACTIVE_FRAME_LINES` before repairing.
  The payload now leads with the disambiguating check and states plainly that a
  deferring line makes the refusal correct.
- **Real blocker, acted on:** the same reviewer found a comment in this module
  claiming the seeded frame as a live over-fire instance. It is not. Left
  standing, the next maintainer taking the upstream issue could widen the matcher
  to stop refusing the template and disarm the floor on its own scaffold. The
  comment now records the correction by name.
- **Real gap, acted on:** the refusal gave a hard-blocked consumer nothing to do.
  It now names two workable remedies. It does NOT name the tracker id, because
  this repo's `post_edit_skill_anchor_guard` refuses issue anchors in a portable
  skill package — a real conflict between the reviewer's ask and a repo gate,
  resolved on the side of the gate since concrete remedies serve the consumer
  better than an id they cannot search from an installed copy.
- **Over-worry, not acted on:** payload strings being parsed. Independently
  confirmed that only `check_goal` and `pursue_readiness` read the payload, both
  gating on `cadence["ok"]` and prefixing the reason; nothing branches on text.
- **Over-worry, not acted on:** the registry edit changing gate behavior. The
  validator checks `states`, non-empty `visibility`/`rationale`, and that every
  `evidence_terms` entry occurs in the source; all five occur, and rationale
  prose is not machine-read.
- **Deferred with its residual stated:** the reviewer's fourth finding — the
  absent-branch reason asserts the frame was read even when `## Active Operating
  Frame` is missing entirely, and unlike its twin there is no mitigating refusal
  because that heading is in no required-section list. Real, non-blocking
  (`applies: false, ok: true`), and the first thing to fold into the `#694`
  slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:236 | action: fix | note: the over-fire escape clause was reachable from the true-positive side, so a correct refusal against the scaffold's own seeded frame could be dismissed; the payload now leads with the disambiguating check
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:71 | action: fix | note: a comment claimed the seeded frame as an over-fire instance; verified false against the scaffold constant and corrected, with the risk to the next maintainer named
- F3 | bin: act-before-ship | evidence: moderate | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:236 | action: fix | note: a hard-blocked consumer had no remedy; two workable ones added, tracker id deliberately omitted because the anchor guard refuses issue anchors in a portable package
- F4 | bin: valid-but-defer | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_cadence_owner.py:189 | action: file-issue | note: the absent branch asserts the frame was read when the frame heading is absent entirely, with no required-section check behind it; fold into the over-fire slice | follow-up: https://github.com/corca-ai/charness/issues/694
- F5 | bin: bundle-anyway | evidence: strong | ref: release-scope | action: document | note: post-publish, the #681 reproduction must be replayed against the INSTALLED 6.2.2 copy; a version or doctor readback is not that branch, and the requalification packet names this gap in its own non-claims
- F6 | bin: over-worry | evidence: strong | ref: skills/public/quality/references/attention-state-visibility.json | action: defer | note: registry rationale is not machine-read and the validator's checked fields are unchanged

## Reviewer Tier Evidence

- Requested tier: bounded-reviewer (host typed subagent, Read/Grep/Glob only).
- Requested spawn fields: subagent_type, prompt, description.
- Host exposure state: metadata-hidden
- Application state: reviewer-reported: the release reviewer returned typed findings inline and reported its envelope bound by construction — Bash, Edit, Write and Agent absent from the spawn. That is the reviewer's own testimony, not a host confirmation: nothing in this session reads back which tools a spawn was given. The boundary fingerprint below proves the tree did not drift, which is a different fact. The claims review flagged an earlier `host-confirmed:` wording here as an overclaim, in a session that also recorded a subagent violating its read-only instruction, and it was right to.
- Delivery state: findings-received
- Execution mode: typed-subagent
- Worker report: n/a — typed host-subagent branch, not the file-backed worker path.
- Worker report identity: n/a
- Worker report approval: n/a
- Worker report delivery: n/a
- Worker report packet identity: n/a
- Worker report input identity: n/a
- Worker report parent receipt identity: n/a
- Worker report findings identity: n/a

Boundary proof via `reviewer_boundary_fingerprint.py`, window
`release-622-critique`: `ok: true`, `verdict: parent-attributed`, `drift: []`,
`unmatched_parent_paths: []`. The tool's caveat stands: git proves the tree
changed, never who changed it.

The reviewer named one read it could not perform — diffing against
`v6.2.1:skills/public/achieve/scripts/goal_artifact_cadence_owner.py` to prove no
`ok` value changed for any input — and declined to assert past it. The claims
review then found the release record asserting that conclusion anyway and called
it a blocker. The read was then performed BY THE PARENT, not by any reviewer: 400
constructed inputs across 5 statuses, 8 cadence shapes, 5 acceptance shapes and
frame present/absent, with **0 divergences** in the `(applies, ok)` pair.
Evidence: `charness-artifacts/probe/2026-08-22-v6.2.2-cadence-verdict-differential.json`,
which records in its own non-claims that it is parent-authored and not an
independent observer's. It sits in this section because it closes a gap this
section opened, not because a reviewer produced it.

## Fresh-Eye Satisfaction

parent-delegated

The reviewer's ship recommendation was `ship-with-changes` with verdict
`approve-with-notes`. All three ship conditions were applied before the cut. The
repairs themselves are recorded as accepted-unreviewed: they are prose changes
inside the sentence the code-half's round 2 already repaired, and that critique's
two-round cap is consumed.

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer read the working tree at the paths named in its prompt, over the frozen range 46169b7ad..5bd80a7b6. -->

## Boundary Ownership

- Producer: `goal_artifact_cadence_owner.check` renders the cadence-owner verdict and the sentence an operator reads at a blocked activation.
- Consumer: `goal_artifact_lib.pursue_readiness` and `check_goal` gate on `cadence["ok"]`; the human operator consumes the reason text.
- Owning surface: the achieve goal-artifact proof surface, shipped in the plugin package.
- Verdict: owned-correctly
