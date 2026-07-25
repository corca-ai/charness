# Issue 454 resolution critique
Date: 2026-07-25

## Decision Under Review

The fix for corca-ai/charness#454: promoting reviewer **result delivery** into the
shared fresh-eye contract (`## Result Delivery`), pinning it with a guard, and
adding a typed `Delivery state` floor to the critique closeout validator so a
review can no longer be recorded as obtained without stating that its findings
arrived.

## Failure Angles

- **Recurrence** — what lets this class, and the step-4 siblings, come back.
- **Portability / host-plurality** — whether a one-host, `n=1` finding was
  written into a host-plural contract as if universal.
- **Counterweight** — what the fix got wrong rather than merely incomplete, and
  which concerns are over-worry.

## Counterweight Pass

The counterweight confirmed the fix is substantially correct — rule right,
ownership placement right, mirrors synced byte-identical, `latest.md` symlink
correct, and both 2026-06-20 retro cites resolving exactly as described. It
explicitly rejected six likely-but-not-worth-acting concerns (see over-worry
findings below), which kept the response scoped to four real defects plus one
structural gap rather than a broad rewrite.

Both angle reviewers independently flagged the unconditional `## Do Not` bullet,
which is the strongest signal in the set: two lenses converging on one line.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md | action: fix | note: Do Not bullet was unconditional while the section body carved out hosts that expose the retrieval tool; fixed by matching the carve-out, so the rule no longer forbids a working call
- F2 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md | action: fix | note: distinct-named-lens guidance could be implemented as the host name parameter and re-enter the mailbox trap; fixed by naming the lens in packet prose, never the spawn field
- F3 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/fresh-eye-subagent-review.md | action: fix | note: one-host n=1 mechanism stated as universal with no per-host scope or Codex split; fixed by mirroring rail 2's live-claim wording and citing the debug artifact's non-claims
- F4 | bin: act-before-ship | evidence: moderate | ref: tests/quality_gates/test_reviewer_result_delivery.py | action: fix | note: guard pinned a line-wrap fragment and markdown emphasis; fixed by asserting the real sentence and stripping emphasis in the reader
- F5 | bin: bundle-anyway | evidence: strong | ref: scripts/validate_critique_artifacts.py | action: fix | note: typed delivery states were consumed by no validator, making them naming ceremony; added the Delivery state floor plus scaffold field and enum drift pin, so closeout cannot omit the delivery claim
- F6 | bin: act-before-ship | evidence: moderate | ref: charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md | action: fix | note: artifact used a glob filename and attributed one retro's quote to two; fixed by pinning the filename and splitting the attribution, since the 07-17 retro recorded the opposite observation
- F7 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/debug/2026-07-25-bounded-reviewer-result-delivery.md | action: document | note: the bounded-reviewer envelope edit is release-gated and was not live this session; recorded as a non-claim so it is not counted as proven
- F8 | bin: valid-but-defer | evidence: strong | ref: docs/deferred-decisions.md | action: defer | note: the lesson-decay class that caused the recurrence is unaddressed; booked as D38 with concrete lineage and a reopen trigger rather than guessing a promotion taxonomy mid-fix
- F9 | bin: over-worry | evidence: weak | ref: tests/quality_gates/test_reviewer_result_delivery.py | action: defer | note: the guard cannot test actual delivery; delivery is a per-host live claim and a test cannot spawn, which the guard docstring already scopes
- F10 | bin: over-worry | evidence: weak | ref: skills/shared/references/fresh-eye-subagent-review.md | action: defer | note: prose-only-fix objection does not hold; the recurrence cause was decay of a rolling lesson, so moving it into a test-pinned contract is the mechanism

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (causal review + three resolution-critique reviewers).
- Requested spawn fields: none sent — per the repo's per-host subagent split, Claude Code hosts use the host's own typed-agent controls (`bounded-reviewer`) with session-model inheritance rather than a requested model/effort.
- Host exposure state: host-defaulted
- Application state: reviewers ran on the session-inherited model; no host tier-application signal exposed.
<!-- allowed Delivery state: findings-received | spawn-accepted-no-delivery | pending-parent-spawn. Boundary cleanliness is a separate claim and does not imply delivery. -->
- Delivery state: findings-received — all four reviewers (causal review plus three critique lenses) returned findings text inline under the unnamed spawn shape.

## Fresh-Eye Satisfaction

`parent-delegated`. Four bounded reviewers spawned as `bounded-reviewer` under
the `AGENTS.md ## Subagent Delegation` contract; every one returned its findings
to the parent. Rail-1 boundary verified `{"ok": true, "drift": []}` after the
causal review and after the critique reviewer set (set-level attribution for the
concurrent set, per-reviewer for the causal review).

## Reviewed Input Identity

<!-- Packet-bound critiques replace this comment with three bullets copied from prepare_packet.py after the reviewed packet is final: Packet path, exact Packet SHA256, and Identity SHA256. Leave this section comment-only when no packet was consumed. -->

## Boundary Ownership

<!-- allowed Verdict (substitute only these): single-surface | owned-correctly | moved-to-owner | escalated-to-issue-spec. Run the producer/consumer brief at skills/shared/references/boundary-ownership-brief.md. -->
- Producer: the bounded reviewer's final assistant message, plus the parent's spawn call shape that selects its delivery channel.
- Consumer: the parent session's context, and downstream the closeout artifact that records whether the review was obtained.
- Owning surface: `skills/shared/references/fresh-eye-subagent-review.md` for the portable rule; `scripts/validate_critique_artifacts.py` for the closeout floor.
- Verdict: owned-correctly — delivery is a cross-skill concern for every reviewer-spawning skill, so it belongs in the shared reference that those skills already cite rather than being restated per skill, and the enforcement sits with the existing reviewer-evidence floors instead of growing a new gate surface.
