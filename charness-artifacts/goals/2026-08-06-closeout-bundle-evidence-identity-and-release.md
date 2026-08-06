# Achieve Goal: Build a closeout bundle, bind evidence identity, and publish the final release

Status: draft
Created: 2026-08-06
Activation: `/goal @charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Make the Charness closeout boundary structurally reliable: provide one opt-in closeout bundle for surfaces 1-4, freeze evidence against an immutable identity, run authoring preflight before fresh-eye review, wire retro improvements into handoff/contract state, and finish with a separately gated push and release publication/readback. The draft is inert until the operator activates it; no external side effect is executed while shaping.

## Non-Goals

- Do not turn the closeout bundle into a universal gate for ordinary reversible
  documentation or code edits; it is an opt-in `achieve` boundary workflow.
- Do not run Cautilus, provider roundtrips, cross-host runtime experiments, or
  live-agent proof in this goal unless a separate activation decision adds that
  boundary; Cautilus remains ask-before-run.
- Do not create a PR, close or reopen issues, or publish unrelated versions.
  Release version and carrier must come from the release preflight, not a draft
  assumption.
- Do not push or publish per slice. The final push/release lane is last and is
  conditional on every local gate, the release preflight, and distinct-channel
  remote verification.

## Boundaries

- Local implementation slices may edit code, scripts, tests, docs, skills, and
  artifacts, but must sync generated/exported surfaces before verification.
- The final external bundle alone may run the pre-push gate, push `main`, and
  publish the release. The push authorization is conditional on the gates and
  must never use `--no-verify` or weakened thresholds.
- Remote CI and release readback must use an observer and channel distinct from
  the push or publish exit code. A green terminal command is provisional.
- If the release target, version, carrier, or remote observer is unresolved at
  the final preflight, stop before the side effect and record the boundary.

## User Acceptance

- A single opt-in closeout bundle command can dry-run and then execute the
  surface inventory, pointer refresh, evidence identity freeze, pre-review
  authoring preflight, reviewer packet generation, and verification lock.
- Tests demonstrate refusal for stale current pointers, mutable or missing
  evidence identity, pre-review authoring failures, and retro/handoff drift.
- The final release phase records the immutable implementation target, passes
  the full pre-push gate, pushes `main`, verifies remote CI through a different
  observer/channel, publishes the release through the release workflow, and
  reads the release back through a distinct channel.
- The checked-in goal, quality, retro, handoff, critique, release, and host
  receipts agree; the worktree is clean and all non-claims are explicit.

## Agent Verification Plan

### Low-Cost Checks

- Focused unit tests for bundle orchestration, pointer reconciliation, and
  working-tree/immutable evidence identity.
- `check_doc_authoring_preflight.py`, artifact validators,
  `validate_current_pointer_freshness.py`, and staged mirror checks.
- Existing quality and changed-surface gates after every implementation slice.

### High-Confidence Checks

- A bounded fresh-eye review of the implementation contract and final claims;
  if verdict logic changes, run the required repaired-surface review round.
- Verification-locked closeout against the final immutable commit, with a
  packet SHA and reviewed-input identity that remain valid after commit.
- Release preflight and final pre-push quality gate over the complete bundle.

### External Or Live Proof

- Last phase only: push `main` under the standing gate-conditioned approval,
  verify remote CI with a different observer/channel, publish the release via
  the release skill, and verify the published release through a distinct
  readback channel.
- No provider, cross-host runtime, live-agent, or Cautilus proof is claimed.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Shape the closeout bundle contract | Existing closeout waste spans four surfaces and must have one opt-in owner without becoming universal ceremony. | Implementation contract, owner map, dry-run shape, and failure matrix. | planned |
| 2 | Implement bundle orchestration | Pointer refresh, authoring preflight, identity freeze, and reviewer packet generation currently require manual sequencing. | Helper/CLI behavior, focused tests, generated artifacts, and sync proof. | planned |
| 3 | Harden evidence identity and retro wiring | Mutable `HEAD`, late authoring checks, and retro-only memory caused avoidable rework. | Immutable/worktree identity tests, pre-review ordering, retro-to-handoff validator, and contract docs. | planned |
| 4 | Run local verification and delegated review | The repaired bundle needs independent claim review before any irreversible boundary. | Full local gates, bounded reviewer result, clean fingerprint, and verification lock. | planned |
| 5 | Push and publish the final release | External effects are safest after the complete local bundle is frozen. | Pre-push receipt, push result, remote CI distinct-channel readback, release publish receipt, and release readback. | planned |

## Operator Decision Queue

none — the user explicitly requested that push and release be the final phase;
the release preflight will derive the version and carrier before any side effect.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`

Routing: achieve — selected from installed skill metadata for goal shaping;
activation will resolve implementation, quality, critique, retro, and release
owners from the installed capability surface.
Gather: n/a — no new public source is needed for this repo-local goal draft.
Release: n/a — no release is executed during shaping; activation will record the
release preflight and final publish evidence.
Issue closeout: n/a — no issue closeout is in scope for this goal.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — the user explicitly requested a final
  push and release. Version, carrier, and remote observer remain preflight
  outputs; no external side effect occurs until all local and release gates pass.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [Design North Star](../../docs/design-north-star.md) — reversible work uses
   judgment, while irreversible boundaries require distinct observers and
   evidence channels.
2. [Operating contract](../../docs/conventions/operating-contract.md) — current
   pointers, critique, commit, and closeout discipline.
3. [Implementation discipline](../../docs/conventions/implementation-discipline.md)
   — sync-before-verify ordering and generated/exported surfaces.
4. [Current handoff](../../docs/handoff.md) — completed runtime boundary and the
   separation between local and external proof.
5. [Runtime closeout goal](./2026-08-07-runtime-evidence-and-final-boundary.md)
   and [goal-bound retro](../retro/2026-08-06-runtime-evidence-and-final-boundary.md)
   — recent evidence and lessons from the preceding closeout.
6. [Current quality record](../quality/latest.md) — the current validation
   posture and known non-claims.

## Interview Decisions

- Mode: implementation-continuation after explicit `/goal`; artifact-only now,
  because consuming the host goal slot during drafting would execute work before
  activation.
- Bundle scope: one opt-in `achieve` owner for surfaces 1-4, not universal
  enforcement, so ordinary reversible work does not inherit release ceremony.
- Identity: immutable commit SHA or full working-tree digest, not mutable `HEAD`,
  so the reviewed evidence cannot silently move.
- Review order: authoring preflight before fresh-eye review, then fingerprint
  verification before parent writes, so the reviewer sees the claimable surface.
- Release timing: push and release only in slice 5 after the verification lock,
  not per slice; this follows the user's explicit final-boundary request.

## Plan Critique Findings

- Blocker folded: one command owns packet, pointer, preflight, and reviewer
  sequencing while remaining opt-in.
- Blocker folded: push and release remain provisional until remote CI and release
  readback use a distinct observer and channel.
- Over-worry not folded: cross-host, provider, and Cautilus proof are outside this
  goal and would add a separate boundary rather than improve the requested 1-4.
- Provenance: Before-phase model critique; activation still requires a bounded
  fresh-eye review of implementation and final claims.

## Closeout Binding Plan

- Reviewed inputs: this goal, the preceding closeout goal and retro, operating and
  implementation contracts, current quality pointer, release adapter/manifest,
  generated/export surfaces, and the final release checklist.
- Frozen target: bind the packet to the final immutable commit SHA or full
  worktree digest, never an unqualified mutable `HEAD`.
- Fresh-eye: use a bounded implementation/claims reviewer, plus a different
  remote observer and channel for CI and release readback.
- Verification lock: record `run_slice_closeout.py --verification-lock`, the
  release preflight, and the conditioned pre-push evidence; semantic edits
  require rebinding.
- Complete flip: record packet, reviewer, lock, push, CI, release, and readback
  evidence before complete; commit terminal bookkeeping before host completion.

## Off-Goal Findings

Provider freshness, cross-host runtime, live-agent proof, Cautilus, issue
operations, PR work, and unrelated releases remain separate goals.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: not yet created — activation will persist a goal-bound retro.
Host log probe: not yet created — final push/release execution will record host receipts.
Disposition review: not yet created — activation and closeout will run the bounded claims review.

## User Verification Instructions

At completion, inspect the closeout bundle manifest, immutable evidence identity,
fresh-eye disposition, pre-push receipt, remote CI readback, and release readback.
Confirm that no local green was promoted to provider, cross-host, or Cautilus proof.

## Auto-Retro

Retro dispositions: none — this inert draft has executed no improvement; activation
must disposition each surfaced improvement.
Structural follow-up: planned — slices 1-4 will land the opt-in closeout bundle,
immutable identity, pre-review authoring order, and retro-to-handoff wiring; final
disposition must name the landed contract or guard.
