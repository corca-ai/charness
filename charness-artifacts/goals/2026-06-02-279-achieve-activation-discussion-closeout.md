# Achieve Goal: #279: achieve should surface activation discussion before ready closeout

Status: active
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-279-achieve-activation-discussion-closeout.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation; shaped by `/achieve`.
- Next action: surface the activation discussion below to the user and resolve
  or confirm each item before reporting this goal ready. Only after that
  discussion is complete, offer
  `/goal @charness-artifacts/goals/2026-06-02-279-achieve-activation-discussion-closeout.md`.
- Verification cadence: cheap deterministic checks at commit boundaries; focused
  pytest and artifact validators at slice boundaries; final broad/local proof
  and issue-closeout proof at closeout.
- Slice review packet: for fresh-eye critique, provide issue #279, this goal
  artifact, changed files, expected activation-discussion invariant, tests run,
  and non-claims about host-transcript enforcement.
- History boundary: keep this frame current during the active run; move
  completed detail to `## Slice Log`, `## Final Verification`, and
  `## Auto-Retro`.

## Goal

#279: achieve should surface activation discussion before ready closeout

**Source handoff entry #2: #279: achieve should surface activation discussion before ready closeout**

> ## Problem
>
> `achieve` lets a Before-phase goal artifact pass `--pursue-ready` when it has a
> `Discuss before activation:` summary, but the workflow can still close out to
> the user without actually surfacing and resolving those discussion items first.
>
> That creates a bad operator experience: the goal file looks formally shaped,
> yet the user only discovers the remaining product decisions after the final
> answer or when reviewing the artifact. In a recent Ceal goal-shaping run, the
> artifact correctly recorded activation discussion items such as company-info
> automation scope, offboarding posture, access source of truth, instance alias
> defaults, and issue-closeout intent. The assistant then reported the goal as
> ready instead of pausing to discuss those items in the transcript first.
>
> ## User impact
>
> - The user explicitly asked to continue discussion if anything remained, but
>   the remaining questions were hidden inside the artifact.
> - `--pursue-ready` was technically true, but the human collaboration contract
>   was not satisfied.
> - The artifact's `Discuss before activation:` field became a bypass around the
>   intended interview rather than a prompt to run the interview before closeout.
>
> ## Evidence
>
> - Triggering situation: an `achieve` Before-phase created
>   `charness-artifacts/goals/2026-06-02-ceal-instance-access-events-company-info.md`
>   in the Ceal repo.
> - The checker returned `pursue_ready: true` with `discussion_required: true` and
>   `discussion_summary_present: true`.
> - The user then asked why the discussion did not happen before the goal was
>   proposed.
>
> ## Desired behavior
>
> When a Before-phase artifact has activation discussion items:
>
> - the final closeout should surface those discussion items directly;
> - if the user asked to continue discussion when questions remain, the assistant
>   should resolve or explicitly ask about them before reporting the goal as ready;
> - the checker or helper output should make it hard to treat
>   `discussion_summary_present` as equivalent to "discussion completed."
>
> ## Possible direction
>
> This may need both workflow text and helper output changes:
>
> - distinguish `discussion_recorded` from `discussion_resolved`;
> - make `check_goal_artifact.py --pursue-ready` report a stronger human-facing
>   warning when discussion is required but not resolved;
> - update `achieve` closeout guidance so activation discussion items are brought
>   into the transcript before the goal file and activation line are presented.

## Non-Goals

- Not a release: no plugin version bump expected.
- Do not absorb adjacent handoff entries beyond the selected chunk.
- Do not implement a new agent runtime or `/goal` execution engine.
- Do not claim the original Ceal host incident is replayed or fixed live unless
  an explicit cross-repo/host proof is run.
- Do not close #279 by hand outside the issue-closeout path; stage closure on
  the commit or PR that lands the fix.

## Boundaries

- In scope: `skills/public/achieve/` workflow text and helpers,
  `skills/public/achieve/scripts/check_goal_artifact.py` /
  `goal_artifact_discussion.py` behavior, tests that pin activation-discussion
  readiness, and any generated/plugin surfaces required by changed public skill
  content.
- Out of scope unless a slice proves it necessary: unrelated goal artifact
  schema changes, host-specific transcript plumbing, or retrospective changes
  outside the issue #279 failure mode.
- Portability: treat host-specific evidence from the Ceal incident as context,
  not as a global runtime assumption; repo behavior must stay portable across
  Claude/Codex plugin exports.
- Stop conditions: pause if the desired behavior requires changing host command
  semantics instead of repo skill/helper guidance, if #279 needs private Ceal
  context not present in the issue body, or if the checker cannot distinguish
  recorded versus resolved discussion without a larger schema decision.

## User Acceptance

- A user reviewing an `achieve` Before-phase result with unresolved activation
  discussion can see those discussion items in the transcript-facing closeout,
  not only inside the goal artifact.
- The pursue-readiness/helper output no longer invites an operator to treat
  `discussion_summary_present` as equivalent to discussion resolved.
- The changed guidance makes it explicit that a request to keep discussing open
  questions must be honored before reporting the goal ready for activation.
- #279 is staged for closure through the issue workflow with proof bound to this
  goal.

## Agent Verification Plan

### Low-Cost Checks

- `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-02-279-achieve-activation-discussion-closeout.md`
- Focused pytest in `tests/quality_gates/test_goal_artifact_lib.py` proving
  `discussion_required` + `discussion_summary_present` cannot be read as
  discussion resolved.
- Focused pytest in `tests/quality_gates/test_achieve_before_activation.py`
  proving closeout guidance requires surfacing/resolving activation discussion
  before presenting readiness/activation.
- CLI proof for `check_goal_artifact.py --pursue-ready` showing the helper emits
  a human-facing warning for unresolved discussion.
- `python3 scripts/check_changed_surfaces.py --repo-root .` after the first
  implementation slice to confirm generated/export obligations.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  before committing implementation slices that touch public skill/helper/test
  surfaces.
- Fresh-eye critique of the implementation slice and final closeout packet,
  bounded to the #279 activation-discussion invariant.
- `python3 scripts/run-quality.sh --read-only` at final closeout or a documented
  substitute if the changed surface and recent lessons justify a narrower gate.

### External Or Live Proof

- `gh issue view 279` is enough to confirm the originating issue remains the
  tracked source.
- No live Ceal transcript replay is planned by default; if a slice needs private
  Ceal context, stop and ask for the access path before claiming host proof.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Confirm issue #279 as a bug-class workflow gap and record a minimal RCA/debug basis | The issue reports behavior diverging from the intended human collaboration contract; root cause should precede the fix | Debug artifact or inline RCA in Slice Log names symptom, correct behavior, candidate causes, hypothesis, and detection gap | pending |
| 1 | Tighten `achieve` Before-phase/closeout guidance and helper output so recorded discussion cannot be mistaken for resolved discussion | This is the direct failure mode and should be fixed before broader validation | Changed skill/helper surfaces plus focused tests for discussion-required output and closeout wording | pending |
| 2 | Sync generated/plugin surfaces and run focused closeout proof | Public skill changes must propagate before validators and commit | Surface sync output if needed; focused pytest, changed-surface check, and slice closeout proof | pending |
| 3 | Stage #279 issue closeout and final goal proof | The tracked issue should close through the issue workflow only after implementation proof exists | Draft/validate closeout carrier after proof; verify GitHub CLOSED only after push/merge; manual close only as fallback; final critique, retro, final quality proof or justified substitute, complete goal artifact | pending |

## Coordination Cues

- Routing: use `find-skills` recommendation probes at real runtime or validation
  boundaries during the active run; do not hard-code a phase-to-skill map here.
- Gather: n/a - GitHub issue #279 is the tracked originating issue, its body is
  copied into this goal, and issue closeout owns final tracker state.
- Release: n/a - no release surface is planned for this goal.
- Issue closeout: planned for #279 via `issue` at final closeout; carrier should
  include `Close #279` only when the fix and proof are ready to land.

Discuss before activation: confirm before offering activation:
implementation-continuation for #279; stage `Close #279` only on the
proof-bearing commit/PR; no live Ceal replay by default; stop for user input if
private Ceal context or host-command semantics changes are required.

## Slice Log

### Slice 1: Slice 0 RCA

- Objective: Confirm issue #279 as a bug-class workflow gap before implementation.
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Debug artifact created and validated: charness-artifacts/debug/2026-06-02-279-achieve-activation-discussion-closeout.md; python3 scripts/validate_debug_artifact.py --repo-root .
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Slice 1 implementation

- Objective: Tighten achieve activation-discussion helper output and guidance so surfaced discussion cannot be read as resolved.
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: PASS: python3 -m pytest -q tests/charness_cli/test_goal_helpers.py tests/quality_gates/test_goal_artifact_lib.py tests/quality_gates/test_achieve_before_activation.py (58 passed); PASS: python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest --ack-cautilus-skill-review; PASS: python3 scripts/check_duplicates.py --repo-root . --fail-on-match --require-git-file-listing; CLI proof emits activation_discussion_warning for this goal. Fresh-eye critique found no blocker; low CLI-wrapper coverage gap fixed.
- Test duplication pressure: No duplicates found at threshold 0.98.
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

- Source: handoff entry #2 (#279: achieve should surface activation discussion before ready closeout) — see [docs/handoff.md](../../docs/handoff.md).
- GitHub issue: https://github.com/corca-ai/charness/issues/279 (read through
  `gh issue view 279` on 2026-06-02).
- Cited path: `charness-artifacts/goals/2026-06-02-ceal-instance-access-events-company-info.md`
- Cited issue: #279

## Interview Decisions

- Mode: implementation-continuation after explicit `/goal` activation; rejected
  artifact-only because the user asked to "achieve 279" after selecting the
  issue chunk, and #279 describes a repo behavior fix.
- Scope: issue #279 only; rejected bundling #184/#261/#274 because handoff
  chunking ranked #279 as its own standalone process-risk chunk.
- Live proof: no default Ceal replay; rejected assuming private cross-repo host
  proof because the public issue body is enough to shape the repo fix, but not
  enough to claim live incident replay.
- Issue closeout: stage closure through `issue` on the landing commit/PR;
  rejected manual out-of-band closing because the repo contract wants bound
  closeout proof.
- Axis probe: host behavior is an axis (Claude/Codex/plugin exports), so the
  fix must live in portable skill/helper behavior rather than a single-host
  transcript assumption.

## Plan Critique Findings

- Initial self-check: the main risk is over-fitting to the Ceal incident without
  making the repo-level invariant testable. Folded into Boundaries and
  Verification by requiring portable helper/skill behavior and focused tests.
- Initial self-check: issue closeout could be started too early. Folded into
  Slice Plan and Coordination Cues by reserving `Close #279` for the final
  proof-bearing carrier.
- Fresh-eye critique (2026-06-02, read-only bounded reviewer): found one blocker
  that the first draft repeated #279 by pointing straight to `/goal` while still
  carrying activation discussion items. Folded by making the next action resolve
  or confirm activation discussion before offering activation, rewriting the
  discussion line as explicit confirmation items, naming focused tests for the
  core invariant, and clarifying issue closeout timing.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
