# Achieve Goal: 291 292 284 activation readiness, index isolation, and skill preflight

Status: active
Created: 2026-06-04
Activation: `/goal @charness-artifacts/goals/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Discuss before activation: RESOLVED in-thread on 2026-06-04. The user selected
the handoff first chunk `(292 284)`, identified the activation-discussion
mismatch as #291, asked to include it in this goal, and agreed to the surfaced
activation decisions. This goal is a bundled implementation-continuation run:
resolve #291 first so activation readiness blocks unresolved consequential
discussion, then #292, then #284; close tracked issues only after the pushed
carrier verifies; do not claim release, real-host update, scheduled CI, or live
proof unless a later slice explicitly runs and records it.

## Active Operating Frame

- Current slice: Slice 3, #292 root cause and containment design.
- Next action: read #292 current tracker state, run the required bug-class
  issue/debug causal path, and design the index-isolation fix before mutation.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve #291 plus the first handoff chunk from
[docs/handoff.md](../../docs/handoff.md): first make `achieve` activation
readiness block unresolved consequential activation discussion, then remove the
real-repo git-index flake from parallel pre-push quality tests, then add a cheap
skill-surface pre-edit preflight that reports headroom and known coupling
hazards before broad quality closeout.

The useful outcome is three-part:

- #291 is fixed so `check_goal_artifact.py --pursue-ready` no longer returns a
  plain activation-ready signal when `Discuss before activation` is merely
  surfaced but not resolved.
- #292 is fixed so parallel pre-push quality tests no longer call
  `git write-tree` against the shared parent worktree/index while `git push`
  and its hook are active.
- #284 is implemented as an authoring preflight for skill-surface edits that
  catches known waste triggers before the broad quality gate: length/headroom,
  skill ergonomics ceilings, markdown inline-code wrapping, reference link
  depth, plugin/export mirror sync, and real-index access hazards.

## Non-Goals

- Do not redesign the full pre-push hook, local enforcement policy, or release
  helper beyond the index-isolation fix needed for #292.
- Do not remove the staged mirror drift gate; preserve its ability to catch
  missing generated/plugin mirror sync.
- Do not turn the skill preflight into a broad replacement for
  `./scripts/run-quality.sh --read-only`; it should be a cheap pre-edit or
  early-slice signal.
- Do not claim real-host `charness update`, release checklist, scheduled CI, or
  live release proof unless those commands are actually run in this goal.
- Do not close #184, #285, #286, #287, #288, or #289; they may remain
  context or follow-up work.

## Boundaries

- #291 is bug-class issue resolution because current checker behavior diverges
  from the documented `achieve` contract. Before mutation, run the issue/debug
  causal path or record a host-blocked reviewer signal if the required bounded
  fresh-eye path is unavailable.
- #292 is bug-class issue resolution. Before mutation, run the issue/debug
  causal path or record a host-blocked reviewer signal if the required bounded
  fresh-eye path is unavailable.
- #284 is feature/deferred-work issue resolution. Before mutation, emit the
  issue-resolution brief and pause only if it exposes non-empty product, scope,
  policy, or external-side-effect decisions.
- Prefer isolating real-index tests with a temp repo, temp clone, copied index,
  or serial containment over weakening the gate's behavior assertion.
- The preflight should reuse existing validators and helpers where practical:
  `check_python_lengths.py --headroom`, `validate-skills`, `check-markdown`,
  `check-doc-links`, mirror-drift/sync checks, and changed-surface routing.
- Public skill, support, generated, plugin, and exported surfaces must follow
  `mutate -> sync -> verify -> publish`; sync generated/plugin mirrors before
  validators.
- Any new helper must preserve host portability: provider- or host-specific
  behavior belongs in adapters, manifests, presets, or repo-local scripts, not
  hidden inside public skill prose.
- This goal must not activate future work by treating `pursue_ready: true` plus
  a warning as sufficient. Once #291 is fixed, activation readiness should have
  a machine-readable state that prevents that misread.

## User Acceptance

What the user can do to verify completion directly:

- Run a goal-artifact fixture with unresolved consequential
  `Discuss before activation` content and see that the checker blocks or
  clearly separates activation readiness from shaped/discussion readiness.
- Run the previously flaky quality/pre-push test path and see that no parallel
  pytest worker reads the live parent worktree index with `git write-tree`.
- Inspect the #292 fix and confirm the staged mirror drift behavior is still
  tested against an isolated or otherwise safe index.
- Run the new skill-surface preflight on a target `SKILL.md` and see actionable
  output for remaining core/total headroom and known coupling hazards before
  editing or before a broad quality gate.
- Inspect the #284 implementation and confirm it is a cheap authoring aid, not
  a broad quality replacement or a prose-only reminder.
- Verify #291, #292, and #284 are closed only after the pushed carrier contains the
  fix and `issue_tool.py verify-closeout` confirms GitHub state.

## Agent Verification Plan

### Low-Cost Checks

- `find-skills` routing probes at phase boundaries, especially validation
  routing before closeout.
- `issue_tool.py preflight` and issue resolution reads for #291, #292, and
  #284.
- Targeted pytest for activation discussion readiness, the index-isolation
  regression, and the new preflight helper behavior.
- `ruff check` and `python3 scripts/check_python_lengths.py --headroom --paths`
  for changed Python helpers before large additions.
- Targeted markdown/docs/skill validators for any changed skill-surface files.
- Goal artifact validation:
  `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.14.0/skills/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`.

### High-Confidence Checks

- `python3 scripts/run_slice_closeout.py --repo-root . --skip-broad-pytest`
  before slice commits that span generated, plugin, validator, or public-skill
  surfaces.
- `./scripts/run-quality.sh --read-only` before final completion unless a
  concrete environment blocker is recorded.
- Bounded fresh-eye critique for the #291 activation-readiness fix plus the
  #292 isolation and #284 preflight bundle, with a packet covering intent,
  changed files, generated/plugin surfaces, invariants, proof, non-claims, and
  reviewer questions.
- `issue_tool.py validate-closeout-draft` before publishing a close-intended
  carrier and `issue_tool.py verify-closeout --expect-state CLOSED` after
  push/merge/manual fallback.
- Duplicate/pressure sample when tests are added or expanded; classify any
  final broad pressure failure as new-slice-local versus accumulated-suite
  debt.

### External Or Live Proof

- External/live proof is not planned by default. No release, real-host update,
  scheduled CI, or install-machine proof is claimed unless explicitly run and
  recorded during the goal.
- GitHub issue-state verification is required if the final carrier closes #291,
  #292, or #284.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Shape and validate the achieve goal | Prevent the handoff chunk from turning into an ad hoc issue bundle | This artifact passes normal and pursue-ready validation | done |
| 1 | Resolve #291 activation-readiness contract | The current checker can greenlight pursuit while warning discussion is unresolved | Issue/debug causal review, contract decision, failing/regression fixture | done |
| 2 | Implement #291 checker and guidance fix | The rest of this goal should operate under the stricter activation-readiness model | Updated checker fields/behavior, achieve guidance, targeted tests | done |
| 3 | Resolve #292 root cause and containment design | The pre-push flake blocks reliable closeout and informs #284's hazard list | Issue/debug causal review, selected design brief, targeted failing/regression test | pending |
| 4 | Implement #292 index isolation | Remove live parent-index access from parallel quality tests without weakening mirror drift coverage | Changed tests/helpers, targeted pytest, no live-worktree `git write-tree` in parallel path | pending |
| 5 | Design #284 pre-edit preflight contract | Convert repeated skill-surface edit waste into a cheap command surface before implementation | Resolution brief, CLI/API shape, coupling inventory, test plan | pending |
| 6 | Implement #284 preflight | Add the authoring signal while reusing existing validators and preserving portability | Helper/CLI behavior, tests for headroom and coupling output, generated/plugin sync | pending |
| 7 | Bundle critique, broad verification, issue closeout, handoff refresh | Close the tracked issues only after the proof and next-session state are durable | Fresh-eye critique, run-quality, issue closeout validation/verification, updated handoff if needed | pending |

Test-duplication pressure expectation:

- Slices 1-2 should add or adjust focused activation-readiness tests so
  unresolved consequential discussion cannot be mistaken for activation-ready.
- Slices 3-4 should add or adjust focused regression tests for index isolation,
  preferably by changing existing tests instead of adding parallel broad
  coverage.
- Slices 5-6 may add focused preflight tests because #284 introduces new
  behavior; each slice log should record duplicate-pressure evidence if tests
  expand.
- Slice 7 must classify any broad duplicate/length/pressure finding before
  final completion.

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — Gather: n/a - context sources are in-repo artifacts plus
  GitHub tracker issues read through the issue backend; no external URL, Slack,
  Notion, Docs, or Drive source needs to become a gathered repo asset.
- **Release step** — Release: n/a - no version bump, install manifest edit, or
  release surface is planned.
- **Issue closeout step** — Issue closeout: planned for #291, #292, and #284 if the
  activated run completes their acceptance criteria. Preferred carrier:
  direct-to-main commit or PR body with `Close #291. Close #292. Close #284.`
  plus the required closeout ledger; run `issue_tool.py validate-closeout-draft`
  before publishing and `issue_tool.py verify-closeout --expect-state CLOSED`
  after push/merge/manual fallback.

## Slice Log

### Slice 0: Shape the handoff first-chunk goal

- Objective: Create a pursue-ready goal artifact for the selected #291/#292/#284
  handoff chunk without starting implementation.
- Why this approach: The user invoked `achieve` for the handoff first chunk, and
  `/goal` is the explicit activation boundary for execution.
- Commits: none yet.
- What changed: This goal artifact records the bundle scope, issue boundaries,
  non-claims, verification plan, slice plan, coordination floors, and resolved
  activation-discussion summary.
- Alternatives rejected: starting implementation during `/achieve`; treating
  #291, #292, and #284 as unrelated sessions; closing issues without GitHub
  verification.
- Targeted verification: initial `check_goal_artifact.py` normal passed;
  `--pursue-ready` passed with the expected activation-discussion warning for
  issue closeout, bundled scope, and proof non-claims. After the user identified
  #291 and approved the activation decisions, the artifact was reshaped to
  include #291 and mark the discussion resolved.
- Test duplication pressure: no tests added.
- Critique: Before-phase same-agent critique folded below; fresh-eye critique
  is scheduled for the activated implementation bundle.
- Off-goal findings: none.
- Lessons carried forward: Make real-index access, skill headroom, markdown
  spans, link depth, and mirror sync explicit preflight hazards instead of
  relying on broad-gate discovery.

### Slice 1: Resolve #291 activation readiness

- Objective: Make unresolved consequential activation discussion fail the pursue-ready gate instead of returning warning-only success.
- Why this approach: #291 blocks the rest of this goal from relying on the same misleading activation signal.
- Commits: pending
- What changed: Updated achieve discussion/readiness helpers, achieve prose, plugin mirrors, CLI/helper tests, debug RCA artifact, debug seam-risk index, and this goal artifact.
- Alternatives rejected: Keeping pursue_ready true with a warning; adding activation_ready while leaving CLI exit 0; treating any summary text as resolved.
- Targeted verification: Focused pytest: 55 passed; active goal local check reports shape_ready=true, activation_ready=true, pursue_ready=true; packaging, skills, ruff, debug artifact/index, markdown/docs/secrets, public skill policy/dogfood, attention visibility, and length checks passed.
- Test duplication pressure: Expanded existing focused test files only; no broad duplicate sample run yet. Added cases distinguish hidden, surfaced-unresolved, issue-number-leading, and explicitly resolved discussions.
- Critique: Bounded fresh-eye causal review executed by subagent Mencius; root cause and sibling scan recorded in debug artifact.
- Off-goal findings: None.
- Lessons carried forward: Readiness fields must name the consumer boundary they prove: shape-ready for Before-phase continuation, activation-ready for /goal.
- Metrics: Headroom before edit: goal_artifact_lib.py 43 lines left; discussion helper 283 lines left. Kept most new logic in discussion helper.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order:

- [docs/handoff.md](../../docs/handoff.md) - first chunk recommends #292 and
  #284 together.
- [charness-artifacts/quality/latest.md](../quality/latest.md) - current quality
  posture and gate expectations.
- [charness-artifacts/retro/recent-lessons.md](../retro/recent-lessons.md) -
  repeated headroom, handoff edit, markdown, and broad-gate waste traps.
- GitHub issue #292:
  <https://github.com/corca-ai/charness/issues/292>.
- GitHub issue #284:
  <https://github.com/corca-ai/charness/issues/284>.
- GitHub issue #291:
  <https://github.com/corca-ai/charness/issues/291>.
- [docs/conventions/implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
  - sync-before-verify and headroom discipline.
- [docs/conventions/operating-contract.md](../../docs/conventions/operating-contract.md)
  - commit, critique, handoff, and local enforcement discipline.

## Interview Decisions

- Mode: implementation-continuation goal, not artifact-only. Chosen because the
  user invoked `achieve` on the handoff first chunk and named the issue pair.
  Execution still waits for `/goal`; starting slices during `/achieve` was
  rejected because activation is the pursue boundary.
- Bundle: #291 then #292 then #284 in one goal. Chosen because the user
  identified the activation-readiness concern as #291 and asked to include it;
  #291 should land first so the rest of this goal cannot repeat the warning-only
  activation-readiness mistake. Rejected alternatives: leave #291 as a separate
  follow-up, split #292 and #284 into separate goals, or start with #284 before
  fixing the current flake.
- Activation discussion: the user agreed to the surfaced decisions in-thread on
  2026-06-04. Chosen value: proceed only after this explicit agreement, and
  treat future warning-only activation-readiness as the #291 bug to fix.
- Issue closeout: close #291, #292, and #284 only when the activated run proves their
  acceptance criteria and verifies GitHub state. Rejected alternatives: leave
  issues open after complete proof, or close from local proof without
  push/state verification.
- Proof level: local deterministic plus fresh-eye proof by default; live
  release/update/scheduled-CI proof is a non-claim unless explicitly run.
  Rejected alternative: making release proof mandatory even though this chunk
  targets test isolation and authoring preflight, not release surfaces.
- Axis probe: host/environment axis applies. The index flake is local
  worktree/git-hook behavior, so the fix must avoid assuming one host runtime;
  preflight behavior should remain repo-local or adapter-backed where host
  behavior varies.

## Plan Critique Findings

- Folded blocker: the goal could start by relying on the very warning-only
  `pursue_ready` behavior that #291 says is wrong. Slice order now fixes #291
  first, and the activation discussion is explicitly marked resolved by user
  agreement before offering activation.
- Folded blocker: #292 can be "fixed" unsafely by weakening or deleting the real
  mirror-drift behavior check. Boundary added: preserve staged mirror drift
  coverage while isolating index access.
- Folded blocker: #284 could become another broad quality wrapper. Boundary
  added: keep it cheap and pre-edit/early-slice, and reuse existing validators.
- Folded blocker: tracked issue closeout requires issue workflow proof, not just
  a green local gate. Verification and coordination cues now require
  closeout-draft validation and post-publish verification.
- Folded blocker: public skill or generated/plugin changes can drift if
  validated before sync. Boundary and slice plan retain `mutate -> sync ->
  verify -> publish`.
- Over-worry not folded: requiring live release or real-host update proof for
  this goal would exceed the selected chunk unless implementation unexpectedly
  touches release surfaces.
- Reviewer provenance: same-agent Before-phase critique only; activated slices
  still require the issue/debug causal path for #292 and bounded fresh-eye
  critique before final closeout.

## Off-Goal Findings

Issues or deferred findings discovered during the run:

- None during shaping.

## Final Verification

Pending activation and execution.

## User Verification Instructions

After completion, verify by running the commands recorded in `## Final
Verification`, checking the new preflight on representative skill-surface files,
and confirming #291/#292/#284 are closed only after the pushed carrier verifies.

## Auto-Retro

Pending activation and execution.
