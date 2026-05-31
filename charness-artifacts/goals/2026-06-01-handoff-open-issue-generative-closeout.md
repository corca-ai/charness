# Achieve Goal: Handoff and open issue generative closeout

Status: draft
Created: 2026-06-01
Activation: `/goal @charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: artifact-only draft — this Before-phase shapes the sequence and stops.
No implementation, push, PR creation, or live issue mutation runs until the
user activates this file with the `/goal` command above.

## Goal

Shape the current handoff state and every issue open at activation into one
auditable, generative closeout sequence that can discuss unresolved decisions,
execute maintenance slices in dependency order, and leave each issue either
closed through an explicit carrier or intentionally open with a documented
reason.

## Non-Goals

- Do not close, comment on, relabel, or otherwise mutate live GitHub issues
  without an explicit maintainer confirmation at the closeout carrier step.
- Do not push local commits, open a PR, or cut a release as part of shaping this
  goal. Publishing is an activation-time decision and must name its carrier.
- Do not treat product-direction issues (#184/#185) as autonomously closable
  implementation work. They require user discussion and explicit acceptance.
- Do not collapse all open issues into one grab-bag commit. Each issue gets a
  closeout matrix row: `close`, `leave open`, or `needs user decision`, with the
  reason and carrier recorded.
- Do not chase mutation survivors or policy questions past the point where the
  repo's current contract decides them mechanically.
- Do not use `docs/handoff.md` as the mid-goal scratchpad. The active goal
  artifact owns running state; the handoff is refreshed only at closeout.

## Boundaries

- In scope: the current handoff state, the live open issue backlog from `gh`,
  local branch state, issue closeout matrixing, repo-local code/docs/tests/skill
  changes needed to resolve selected issues, final verification, and a handoff
  refresh when the next session's first move changes.
- In scope issues at shaping time: #272, #265, #261, #259, #258, #252, #243,
  #241, #237, #236, #185, and #184.
- Issue tracker state is refreshed at the start of the run and before the final
  carrier. If an issue closed or changed upstream, update the matrix rather than
  proceeding from this snapshot.
- New open issues discovered at activation get a matrix row marked
  `out of activated scope` or are explicitly accepted into scope before the run
  proceeds beyond Slice 0.
- Local branch state matters: `main` is currently ahead of `origin/main` by
  `33971f2 Document achieve long-goal route`. Decide whether that commit is a
  prerequisite publish/PR carrier before closing issue work that depends on it.
  Any pre-#272 publish is only a carrier for the already-complete tranche and
  must carry an explicit #272 non-claim.
- Stop and ask the user when a slice requires product metric choices, AI/ML
  research direction, release/version policy, live issue mutation, push/PR
  publication, or accepting a lower quality/mutation standard.
- Bug-class issue slices need a causal/debug step before the fix and an issue
  closeout carrier after proof. The carrier must include close keywords or a
  deliberate leave-open reason.
- Shared-worktree fresh-eye reviewers must inspect old versions read-only
  (`git show <ref>:<path>`) and must not run checkout/restore/reset/stash or
  staging commands for inspection.
- Before any fresh-eye reviewer or live-closeout review runs, restate the #258
  shared-worktree read-only guard and confirm no index/worktree-mutating
  inspection commands are allowed. The full #258 fix can still stay in Slice 4.
- Keep host-specific behavior in adapters, hooks, presets, and integration
  manifests. Public skills and shared references stay portable.

## User Acceptance

- The final report contains an issue closeout matrix for all 12 open issues
  listed above, with every row marked `closed/carried`, `left open`, or
  `needs maintainer decision`, and with the exact close/comment/PR carrier.
- `git log --oneline origin/main..HEAD` is reviewable and maps commits to the
  issue rows or to explicit artifact/closeout-only work.
- `git status --short --branch` is clean unless the user explicitly pauses
  before commit or publish.
- Local verification proof is recorded per slice, and the final broad gate or
  its documented substitute passes before completion.
- `docs/handoff.md` is updated only at closeout and names the next first move
  after this run, not a stale full backlog duplicate.
- Live GitHub closure, remote CI, push, PR, and release proof are named as run
  or not-run non-claims; none are implied.

## Agent Verification Plan

### Low-Cost Checks

- Before activation: `python3 skills/public/achieve/scripts/check_goal_artifact.py
  --repo-root . --goal-path
  charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md
  --pursue-ready`.
- At run start and final carrier: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, and `gh issue list --state open
  --limit 100 --json number,title,labels,updatedAt,url`.
- Per slice: use `find-skills` to route the current boundary, then run targeted
  pytest/ruff/validator commands for touched surfaces.
- For any slice adding or expanding tests, record a cheap duplicate/length/test
  pressure sample or the reason it does not apply.
- Before committing code/docs/skill/export changes: run
  `python3 scripts/run_slice_closeout.py --repo-root .` or a narrower justified
  docs/artifact-only substitute.

### High-Confidence Checks

- Final `./scripts/run-quality.sh --read-only` unless the completed diff is
  strictly docs/artifacts and the docs-only local substitute is justified.
- Final `python3 scripts/check_changed_surfaces.py --repo-root .` when touched
  surfaces span multiple obligation families.
- Final `python3 skills/public/achieve/scripts/check_goal_artifact.py
  --repo-root . --goal-path
  charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`.
- Bounded critique before final closeout, plus a disposition review for retro
  improvements if the goal reaches complete.
- For GitHub issue closeout: validate the closeout draft/carrier before live
  mutation, and ensure `Close #N` rows match the commit/PR body when closure is
  intended.

### External Or Live Proof

- Live GitHub issue closure/commenting is a maintainer-confirmed final carrier,
  not an automatic side effect of this goal.
- Push/PR creation is a maintainer-confirmed publish step. If skipped, record
  remote CI and live closure as not run.
- No release is planned. If a slice touches a release surface, stop and route
  through `release` before proceeding.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Refresh handoff, branch, and open-issue state; build the closeout matrix | Prevent stale handoff or tracker state from driving a broad closeout run | Current `gh issue list`, `git status`, `origin/main..HEAD`; matrix rows for #272/#265/#261/#259/#258/#252/#243/#241/#237/#236/#185/#184 | pending |
| 1 | Settle the publish/PR carrier for the existing local commit | Handoff says local `main` is ahead; downstream issue closeout should know whether this work is already published | Maintainer decision recorded: defer publish, prepare PR for existing tranche with #272 non-claim, or fold into later carrier; no live issue closure | pending |
| 2 | Restore or reclassify the current mutation-gate blocker (#272) | A current mutation regression on `main` is quality-blocking and can invalidate later proof | Root cause/debug record; targeted fix or stale-issue reclassification; local mutation/quality proof; issue closeout row | pending |
| 3 | Finish the mutation survivor cluster (#265/#261) only to the current policy boundary | Survivor triage depends on a trustworthy mutation baseline and can otherwise absorb unlimited effort | Updated survivor inventory; real survivors killed; equivalent/policy decisions documented; close/leave-open rows for #265/#261 | pending |
| 4 | Close workflow-safety issues that affect future closeout quality (#258/#259/#237/#236) | These reduce risk while working the rest of the backlog: review index safety, symbol residue, live-apply commit classification, CI-only retry discipline | Implemented guards/docs/tests or explicit non-implementation decisions; closeout rows for each issue | pending |
| 5 | Close setup/portability extension issues (#252/#241) | These share the host-extension/compact-contract boundary and should be designed together | Compact AGENTS/setup contract and create-skill adapter extension path, or scoped split with reasons; targeted validation | pending |
| 6 | Make usage episodes useful or explicitly narrow their promise (#243) | Telemetry is collected but has no consumer; this is separate from safety gates and product metrics | Usage report/consumer and capture-gap signal, or a documented decision to narrow/remove the surface | pending |
| 7 | Discuss and decide product/AI-success work (#184/#185) | These are product judgment issues, not autonomous maintenance fixes | User-approved metric/research decision artifact; implementation follow-up if chosen; close/leave-open rows | pending |
| 8 | Final carrier: verify, critique, retro, handoff refresh, and issue closeout/publish | Only after rows are resolved should the run mutate live GitHub state or publish | Final gates; goal complete; retro dispositions; handoff refreshed; close keywords/comments/PR body match matrix | pending |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.

Initial routing:

- Routing: `find-skills` routed this request to the `handoff` public skill for
  live handoff/open-issue state and to the `achieve` public skill for this
  reviewable goal artifact. `gh` is the ready issue-provider route surfaced by
  the local GitHub integration.
- Gather: n/a — the live GitHub issue list is used as issue workflow state and
  must be refreshed through `gh`/`issue` at slice boundaries; no arbitrary
  external source is being summarized into this artifact.
- Release: n/a — no release surface is planned; stop and route through
  `release` if activation discovers a version, manifest, or publication change.

## Slice Log

_Not started. This draft is inert until `/goal` activation._

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/handoff.md` read on 2026-06-01 KST: workflow trigger, current local
  branch state, completed autonomous hardening tranche, and next-session publish
  / re-rank guidance.
- `gh issue list --state open --limit 100 --json number,title,labels,updatedAt,url`
  read on 2026-06-01 KST. Open issues at shaping time: #272, #265, #261, #259,
  #258, #252, #243, #241, #237, #236, #185, #184.
- Handoff parser with live issue union:
  `parse_handoff_entries.py --repo-root . --handoff-path docs/handoff.md
  --with-issues` reported 13 entries, 3 handoff entries, 12 issue entries, and
  2 deduped issue references (#184/#185 from handoff).
- Current branch proof at shaping: `git status --short --branch` reported
  `main...origin/main [ahead 1]`; `git log --oneline origin/main..HEAD` reported
  `33971f2 Document achieve long-goal route`.
- `charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md` for the
  completed tranche and its explicit non-claims around live GitHub closure.
- `charness-artifacts/retro/recent-lessons.md` for the closeout-keyword miss,
  issue closeout matrix rule, and mutation-survivor proof cost warning.
- `charness-artifacts/quality/latest.md` for current local gate posture.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md` for phase barriers, closeout-only
  handoff writes, artifact commit discipline, and critique obligations.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only draft vs implementation-continuation. Chosen:
  artifact-only draft now, then implementation-continuation only after explicit
  `/goal` activation. Rejected auto-execution because the user asked to set a
  goal and the achieve contract keeps shaping separate from pursuit.
- Scope family: handoff only, selected issues only, or all currently open
  issues plus handoff sequencing. Chosen: all currently open issues plus
  handoff state, because the user asked to discuss everything needed and close
  the queue in sequence. Rejected handoff-only because `## Next Session` is a
  curation memo, not the full backlog.
- Sequencing family: chronological issue order, newest-first, product-first, or
  dependency/generative order. Chosen: generative order: state/matrix,
  publish-carrier decision, current quality blocker, mutation cluster, workflow
  safety, portability/setup, telemetry, product decisions, final carrier.
  Rejected chronological/newest-first because they hide dependency and proof
  prerequisites.
- Closeout family: close everything live as soon as local proof passes vs stage
  explicit closeout carriers. Chosen: carrier-first closeout with maintainer
  confirmation for live mutation. Rejected silent live closure because handoff
  and recent retro both flag that issue closeout must be deliberate.
- Product axis: #184/#185 vary on product strategy, market/research direction,
  and maintainer judgment. Chosen: discussion-and-decision slice with stop
  conditions. Rejected autonomous implementation closure.
- Host/provider axis: Charness varies by host/runtime. Chosen: portable public
  skill behavior, with host-specific policy in adapters/hooks/manifests.
  Rejected Codex-only or GitHub-only assumptions in shared surfaces except where
  the issue-provider route is explicitly `gh`.
- Release axis: release is not part of the requested closeout goal. Chosen:
  `Release: n/a` unless activation discovers a touched release surface. Rejected
  opportunistic version bump or publication.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Same-agent preflight folded: "close all open issues" can overreach into live
  issue mutation, product strategy, release work, and policy-standard choices.
  Folded into Non-Goals, Boundaries, and stop conditions.
- Same-agent preflight folded: `#272` should precede broad backlog work because
  it is a current mutation-gate blocker on `main`; later local proof is weaker
  if the baseline is already red or stale.
- Same-agent preflight folded: `#265/#261` should follow `#272` and stop at the
  equivalent-mutant/policy boundary unless the current repo contract decides it.
- Same-agent preflight folded: workflow-safety issues (`#258/#259/#237/#236`)
  should be grouped because they all reduce future closeout waste and proof
  ambiguity, but each still needs its own closeout row.
- Same-agent preflight folded: #184/#185 belong late in the sequence because
  they require user/product judgment and may produce a decision artifact rather
  than a code slice.
- Fresh-eye plan critique: executed by bounded read-only reviewer `Copernicus`
  (`019e8053-c853-7950-bf10-fb6f4ed5b26b`). Folded blockers: activation-time
  new issue drift must become explicit `accepted into scope` or
  `out of activated scope` rows; Slice 1 publish must not imply #272 proof and
  can only carry the already-complete tranche with a #272 non-claim; #258
  shared-worktree reviewer safety must be restated before any reviewer-assisted
  activation work even though the full #258 implementation remains Slice 4.
- Fresh-eye safe-to-leave: product-vs-maintenance boundary for #184/#185 and
  maintainer-confirmed live GitHub mutation guard are sufficient for this draft.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

_None yet._

## Final Verification

_Not started._

## User Verification Instructions

1. Review this file's issue list and slice order.
2. Run `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root .
   --goal-path
   charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md
   --pursue-ready`.
3. Activate only when ready to execute: `/goal
   @charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`.
4. During activation, expect the agent to stop for maintainer decisions around
   publish/PR, live issue mutation, product metrics, release surfaces, or
   mutation policy standards.

## Auto-Retro

_Not started._
