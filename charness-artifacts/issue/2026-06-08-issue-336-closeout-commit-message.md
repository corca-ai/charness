achieve: close out the workflow-ergonomics bundle (Close #336)

Close #336.

Classification: feature.
Issue closeout carrier: direct-commit.
Issue: #336 drafting an achieve goal artifact must not consume the host
active-goal slot. The fix landed in cead7949 (Slice 1 of the
workflow-ergonomics bundle goal); this commit is the closeout carrier and
lands the goal completion, retro, and disposition review.

JTBD: an operator who drafts an achieve goal artifact (Before-phase /
shaping) wants the host active-goal slot to stay EMPTY, so the next goal
creation does not fail with "a goal is still active" and the
drafted-artifact-vs-active-pursued-goal distinction stays clear; the host
slot should start tracking only when the operator runs `/goal @artifact`.

Boundary: the host active-goal slot is host-owned (Claude `/goal` Stop-hook;
the Codex thread-goal slot) and charness coordinates it without
reimplementing it. The portable change is the `achieve` contract — drafting
is artifact-only and never consumes the slot; consumption happens only at
`/goal` pursuit. A host that auto-activates the slot on artifact creation
(regardless of the agent's tool calls) is a host-runtime limitation recorded
as an explicit non-claim, not faked with a no-op adapter knob. Determination
settled early in Slice 1: slot consumption is agent/operator-driven
(`upsert_goal.py` is pure file I/O), so the portable contract IS the real
fix for the controllable path, not a partial.

Resolution brief: add the missing symmetric Before-phase rule to the
`achieve` skill — the lifecycle previously stated the host-goal-tool boundary
only at completion (completion is downstream of the artifact); the
Before-phase counterpart was absent, which is the root of the friction.
Surface the rule on three durable surfaces plus by-construction teeth.

Implementation: SKILL.md Before-phase save step now says the phase is
artifact-only and must not consume the host active-goal slot (only `/goal`
pursuit does); lifecycle.md gains a "Drafting does not consume the host goal
slot" subsection with the host-owned determination and the honest
host-runtime residual non-claim; adapter-contract.md gains a "Host Goal-Slot
Boundary" section documenting that no adapter knob exists by design; a
contract-pinning test (test_drafting_does_not_consume_host_goal_slot) and a
third achieve dogfood acceptance criterion give the rule teeth; the plugin
mirror is byte-synced. Behavior-preserving: routing, draft creation,
activation, inert-until-activation, and completion are unchanged — the new
acceptance criterion describes behavior the draft already had.

Prevention: the contract-pinning test fails if any of the three surfaces
drops the rule, and the dogfood acceptance criterion keeps the
draft-does-not-consume-the-slot guarantee in the maintained consumer
contract, so a future edit that regresses to draft-consumes-slot friction
trips a test rather than re-shipping the operator HOLD.

Tests: targeted achieve suite (tests/quality_gates/test_achieve_before_activation.py)
9 passed; the broad gate `./scripts/run-quality.sh --read-only` passed all 73
phases, 0 failed (including the full pytest suite, check-changed-line-mutation-
coverage with a fresh marker over merge-base origin/main..HEAD, validate_skills,
validate_skill_ergonomics, and check-markdown).

Critique #336: charness-artifacts/critique/2026-06-08-issue-336-host-goal-slot-resolution-critique.md
Retro: charness-artifacts/retro/2026-06-08-workflow-ergonomics-bundle-336-goal-slot.md
