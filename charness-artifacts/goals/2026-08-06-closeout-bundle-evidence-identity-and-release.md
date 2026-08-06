# Achieve Goal: Build a closeout bundle, bind evidence identity, and publish the final release

Status: active
Created: 2026-08-06
Activation: `/goal @charness-artifacts/goals/2026-08-06-closeout-bundle-evidence-identity-and-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 6 — resolve issue #517's semantic surface-contract gap.
- Current slice intent: carry the new quality disclosure floor through a
  delegated resolution critique, verify the repaired proof surface, and close
  the bug only after the direct-commit carrier and distinct behavior proof pass.
- Next action: run the final repository gates, commit the issue ledger, push
  under the conditioned gate, verify #517 CLOSED, and reconcile the session
  baton.
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

Make the Charness closeout boundary structurally reliable: provide one opt-in closeout bundle for surfaces 1-4, freeze evidence against an immutable identity, run authoring preflight before fresh-eye review, wire retro improvements into handoff/contract state, and finish with a separately gated push and release publication/readback. The goal is active; no external side effect is executed before the final release boundary is independently verified.

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
  surface inventory, pointer-freshness validation, evidence identity freeze, pre-review
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
| 1 | Shape the closeout bundle contract | Existing closeout waste spans four surfaces and must have one opt-in owner without becoming universal ceremony. | Implementation contract, owner map, dry-run shape, and failure matrix. | completed |
| 2 | Implement bundle orchestration | Pointer-freshness validation, authoring preflight, identity freeze, and reviewer packet generation currently require manual sequencing. | Helper/CLI behavior, focused tests, generated artifacts, and sync proof. | completed |
| 3 | Harden evidence identity and retro wiring | Mutable `HEAD`, late authoring checks, and retro-only memory caused avoidable rework. | Immutable/worktree identity tests, pre-review ordering, retro-to-handoff validator, and contract docs. | completed |
| 4 | Run local verification and delegated review | The repaired bundle needs independent claim review before any irreversible boundary. | Full local gates, bounded reviewer result, clean fingerprint, and verification lock. | completed |
| 5 | Push and publish the final release | External effects are safest after the complete local bundle is frozen. | Pre-push receipt, push result, remote CI distinct-channel readback, release publish receipt, and release readback. | completed |
| 6 | Resolve issue #517's semantic surface-contract gap | The new quality issue is a direct recurrence of the closeout goal's receipt-versus-meaning boundary and was explicitly requested as follow-up work. | Gathered causal source, repaired quality artifact contract, root/plugin sync, delegated resolution critique, second proof-surface review, closeout carrier, and CLOSED readback. | in_progress |

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

Routing: achieve → gather → issue → quality → critique — selected from installed skill metadata and the active goal's issue-resolution continuation.
Gather: charness-artifacts/gather/2026-08-06-cmanki-debug-review-517.md — authenticated public-source readback persisted before implementation.
Release: charness-artifacts/probe/2026-08-06-v3.4.0-release-observer.json — release work already completed in the preceding boundary.
Issue closeout: #517 — direct-commit carrier; `issue_tool.py validate-closeout-draft` passed and `verify-closeout` is pending remote push/readback.

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

### Slice 1: Closeout bundle orchestration and evidence identity

- Objective: Deliver the first executable opt-in bundle slice that composes existing preflight, pointer, authoring, packet, identity, and verification-lock owners without silently executing behavior channels or irreversible release work.
- Why this approach: The prior final-bundle planner was dry-run only; the goal contract required one bounded execution owner with explicit safety and evidence identity seams.
- Commits: `7af2ec02` records the slice closeout; source and plugin mirrors were synchronized before commit.
- What changed: Added scripts/closeout_bundle.py and closeout_bundle_lib.py with plugin mirrors, the execution contract spec, focused tests, strict repo-owned direct-script validation, post-sync scope refresh, packet identity enforcement, and the intentional CLI boundary exemption. Refreshed the issue-510 interrupt carry-forward and the duplicate-ratchet quality record.
- Alternatives rejected: Rejected universal enforcement, shell execution of planned strings, interpreter code modes, lexical-only repository containment, stale pre-sync path reuse, and receipt creation from dry-run or failed execution.
- Targeted verification: Focused: pytest -q tests/quality_gates/test_closeout_bundle.py (13 passed); pytest -q tests/quality_gates/test_final_bundle_preflight.py tests/test_reviewed_input_identity_failures.py tests/quality_gates/test_closeout_bundle.py (32 passed before the final additions); ruff and Python length checks passed; CLI help passed with status/non-claim workflow; boundary-bypass ratchet passed; duplicate ratchet passed after two intentional portability/evidence metadata entries; plugin/source sync and copy invariants passed. A real --execute reached three surface syncs and pointer freshness, then refused before packet generation on pre-existing hand-authored critique path-authoring violations; no receipt or behavior command was produced. The full review gate ran and reported 82 passes, with ambient baseline failures in recorded probe reconciliation, docs/handoff reference inventory, and pre-existing corpus measurements; changed-surface boundary and duplicate failures were repaired and rerun green.
- Test duplication pressure: Round 1 fresh-eye review was quarantined after parent-attributed boundary drift from a fixture repair. Round 2 had a clean boundary and found symlink escape and missing post-sync behavior coverage; both were repaired. A standalone three-angle critique plus separate counterweight then found packet-binding mismatch, lazy command validation, pointer wording drift, help/status clarity, and the inert --json flag; the first two were repaired before the critique continued and the final three were repaired after counterweight triage. Repairs after the last clean reviewer windows are accepted-unreviewed under the two-round cap, not presented as a fresh approval.
- Critique: Delegated fresh-eye reviews used unnamed gpt-5.6-terra medium reviewers. Round 1 findings were independently carried forward but its approval was quarantined. Round 2 cleanly verified identity ordering, post-sync implementation, and source/plugin parity, rejected the symlink and coverage gaps, and those repairs are recorded as accepted-unreviewed. The standalone critique's Jackson/Weinberg, Gawande/Raskin, Minto/first-reader, and counterweight passes were cleanly fingerprinted; counterweight classified packet consumption as a later claims boundary, output truncation and CLI-reference placement as deferred, and required the source-of-truth/help repairs that landed.
- Off-goal findings: No pointer write, behavior-channel execution, provider or installed-consumer claim, remote CI claim, release publication, tag, or push occurred in this slice. Fresh-eye verdict consumption for the generated packet remains a later delegated claims-review boundary. Quality-gate failures tied to the pre-existing handoff reference drift and stale repository measurement probes remain non-claims.
- Lessons carried forward: Keep execution scopes rebuilt after every mutating sync; lexical path containment is not ownership when symlinks are possible; a clean reviewer boundary is evidence, while parent-attributed drift is not.
- Metrics: 13 focused tests; 32 broader focused tests before final additions; 82 quality-review phases passed; boundary candidates remained 45 with no increase; duplicate fixable-eligible families returned to 0.

### Slice 3: Goal-bound retro and disposition wiring

- Objective: Persist a retro bound to this goal and make its remaining
  improvements visible to the eventual closeout disposition review.
- Evidence: [goal-bound retro](../retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md)
  validates, the retro packet was consumed, and the recent-lessons/index
  surfaces were refreshed by the persistence owner.
- What changed: Added [the wiring validator](../../scripts/validate_retro_handoff_wiring.py)
  and its [generated plugin mirror](../../plugins/charness/scripts/validate_retro_handoff_wiring.py),
  with explicit goal/retro/handoff inputs, normalized
  repository-contained link checks, exact recurrence-marker coverage, and
  explicit non-claims. The contract and focused tests cover wrong goal identity,
  missing citation, wrapped markers, fenced content, direct/lazy blockquotes,
  path escape, ordered and alternate Markdown list markers, and source/plugin
  parity. The refreshed current handoff now cites the goal-bound retro and
  carries both recurrence markers; the validator passes against those explicit
  paths.
- Targeted verification: 14 focused wiring tests passed; the handoff validator,
  handoff artifact validator, pointer freshness, and authoring preflight passed;
  Ruff, plugin help,
  source/plugin byte parity, and the boundary-bypass ratchet passed. The
  required repaired-surface review round had a clean boundary and found the
  wrapped-marker and lazy-blockquote cases; both were repaired with regression
  tests. Per the two-round cap, those round-2 repairs are accepted-unreviewed,
  not a fresh approval. The first locked broad-pytest attempt additionally
  caught the plugin-export static import-safety guard rejecting a dev-tree path
  literal; the resolver now derives both source and plugin asset paths from the
  script directory, and the focused wiring plus empty-scope suite passes 68
  tests. This post-round-2 repair is also accepted-unreviewed. A real handoff
  integration then exposed ordered-list parsing; the validator now covers all
  standard list markers and the focused wiring suite passes 14 tests. This
  integration repair is also accepted-unreviewed under the cap.
- Retro disposition: the packet-rebinding workflow was applied by regenerating
  the Slice 3 critique packet after the final reviewed-input edits, including
  the refreshed handoff and synchronized measurement probes; the
  aggregate diagnostic proposal was filed as deferred decision D52; and the
  memory item is carried by this goal-bound retro plus the refreshed lesson
  index. The distinct final claims/disposition review and verification lock
  remain in the next slice. The material handoff refresh received a separate
  bounded critique; its two overclaims were repaired and recorded in
  [the handoff critique](../critique/2026-08-06-closeout-handoff-refresh.md).

### Slice 4: Locked local proof and final claims boundary

- Objective: prove the committed closeout surfaces with the verification lock,
  changed-line mutation consumer, and a distinct claims/disposition reader
  before any push or release effect.
- Committed proof target: `32a3f8e45c85a9ab144b3b8943b7ecb382f034f1` is the
  immutable target on which the final verification lock and mutation campaign
  ran; `80e85de0ee8e8d367db65ecec7aede50e2165e32` is the later receipt-binding
  commit, which only updates the checked-in proof receipt. The preceding meaningful
  implementation/evidence commits are `45248b4e`,
  `f4c7c5ca`, `9fea4a5d`, `e012a402`, and the generated SLOC sync commits
  `a96a90cd`, `1ac8aa7b`, `7d34c3db`, and `c98b244e`.
- Verification: `run_slice_closeout.py --base --verification-lock
  --refresh-broad-pytest-proof` passed the structural, packaging, docs,
  integration, quality, and full standing pytest gates. The final mutation
  campaign also passed with the focused closeout/wiring suite (`40 passed`)
  and `check_changed_line_mutation_coverage.py --require-fresh-coverage`.
  The exact blocked-plan target `scripts/closeout_bundle_lib.py:254` was
  manually mutated, its focused test failed, and the original line was
  restored; the durable proof is recorded in the Slice 1 critique.
- Review boundary: the handoff refresh, final claims/disposition, and 3.4.0
  release critique all have clean bounded fresh-eye reviews; the release
  observer and remote CI readbacks use distinct channels.
- Non-claims: no Cautilus evaluation, behavior-channel execution, provider or
  installed-consumer proof, remote CI readback, push, tag, release publication,
  or release readback has occurred in this slice.

### Slice 6: Issue #517 semantic surface-contract resolution

- Objective: make a green quality receipt disclose the semantic surface it
  actually observed and the axes it left unexamined, without moving product
  meaning into a host-local validator.
- Source and causal evidence: the issue planner selected #517; the public
  cmanki debug review was gathered at
  `charness-artifacts/gather/2026-08-06-cmanki-debug-review-517.md`; its
  receipt-versus-semantic-coverage recurrence shaped the change.
- What changed: added the portable surface-contract parser, required quality
  artifact section, scaffold/default, reference and skill guidance, migrated
  the current artifact, added duplicate-section and CLI enforcement tests, and
  synchronized the plugin export.
- Critique: the resolution record is
  `charness-artifacts/critique/2026-08-06-issue-517-surface-contract-resolution.md`.
  Three angle reviewers, a separate counterweight, and the mandated repaired
  proof-surface round were delegated. The first round found duplicate-section
  and integration-enforcement blockers; the repairs landed and round 2 found
  no blocker with a clean boundary. Round-2 findings are accepted-unreviewed
  under the two-round cap.
- Targeted verification: 55 focused tests passed; the current quality artifact
  validator and critique validator passed; the root/plugin mirror was synced.
- Non-claims: no product UI semantic oracle, browser/provider roundtrip,
  cross-host, live-agent, or Cautilus proof is claimed. Final gate, commit,
  push, and #517 CLOSED readback remain pending.

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

Provider freshness, cross-host runtime, live-agent proof, Cautilus, PR work,
unrelated releases, and issue #515 remain separate boundaries. Issue #517 is an
explicit user-requested continuation recorded in Slice 6.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-06-closeout-bundle-evidence-identity-and-release-retro.md
Host log probe: skipped: host-log-not-exposed: `probe_host_logs.py` found host logs but this goal has no `Host metric window:` line, so only thread-wide signals exist and no per-goal host claim is bound.
Disposition review: charness-artifacts/critique/2026-08-06-closeout-bundle-evidence-identity-and-release-disposition.md (bounded claims review accepted the corrected local target and preserved the external nonclaims; release receipts are recorded separately).
Remote CI readback: charness-artifacts/probe/2026-08-06-v3.4.0-remote-ci.json (GitHub Actions Quality Core success for `76e96fe9`, including core deterministic gates and changed-line mutation coverage; distinct from the push channel).
Release readback: charness-artifacts/probe/2026-08-06-v3.4.0-release-observer.json (unauthenticated HTTP release observation, installed refresh, `charness version`, and `charness doctor` readbacks).

## User Verification Instructions

At completion, inspect the closeout bundle manifest, immutable evidence identity,
fresh-eye disposition, pre-push receipt, remote CI readback, and release readback.
Confirm that no local green was promoted to provider, cross-host, or Cautilus proof.

## Auto-Retro

Retro dispositions: applied — the packet-rebinding workflow is recorded in the
Slice 3 critique packet, the aggregate diagnostic proposal is filed as D52, and
the memory item is persisted by the goal-bound retro and lesson-selection index.
Structural follow-up: applied for the retro-to-handoff validator,
closeout-only handoff refresh, final claims/disposition reader, and release
notes/probe discoverability repairs; external release receipts are recorded
with distinct observer/channel evidence.
