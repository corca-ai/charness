# Achieve Goal: Current autonomous hardening tranche

Status: draft
Created: 2026-05-31
Activation: `/goal @charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation — after explicit `/goal` activation, the
agent should continue autonomously through this closed issue tranche, stopping
only on the named stop conditions.

## Goal

Turn the current autonomous hardening tranche from the handoff chunker into an
auditable maintenance run: harden closeout proof first, then complete the scoped
portability, process, and mutation follow-ups that do not require new product
direction.

This goal deliberately narrows "all autonomous work" to this closed tranche:

| Issue | Included Work | Stop Boundary |
| --- | --- | --- |
| #268 | Achieve closeout artifact evidence floor and issue closeout draft pre-validation | Stop before direct live GitHub mutation or host-level completion bypass that lacks a checked validator path |
| #269 | Guard achieve artifacts against stale mutable-HEAD SHA wording | Stop if the fix requires changing the meaning of commit/remote proof rather than wording and validation |
| #264 | Portability guard plus cross-skill author-repo-internal cite sweep | Stop if a cited surface needs a new portability policy beyond the issue's discriminator/allowlist |
| #270 | Bind targeted mutant proof to exact gate-reported lines before mutation | Stop if the gate cannot report a precise line/source target |
| #265/#261 | Mechanical survivor enumeration and clearly real survivor kills | Stop before equivalent-mutant or mutation-standard policy decisions |

The intended autonomous sequence is:

1. #268 — close the achieve/issue closeout integrity gap before this run creates
   more closeout state.
2. #269 — remove stale mutable-HEAD wording risk before this goal's own final
   proof writes achieve artifact evidence.
3. #264 — implement the portability guard and cross-skill author-repo-internal
   citation sweep from the #250 follow-up.
4. #270 — apply exact-line proof discipline immediately before targeted
   mutation work.
5. #265 / #261 — triage the residual coordination-cues mutation survivors only
   while the work remains evidence-driven and does not require a product or gate
   policy decision from the user.

## Non-Goals

- Do not push to GitHub, merge, publish a release, or mutate live issue state
  unless a slice's owning workflow explicitly stages a closeout comment/body for
  the maintainer to apply.
- Do not decide product-success criteria, AI/ML engineering research direction,
  or product metrics (#184/#185); those require user/product judgment.
- Do not include #258, #259, #252, #243, #241, #237, or #236 in this run unless
  a slice files a separate follow-up and the next session re-ranks them.
- Do not absorb the broad "other open" backlog as a single grab bag. File or
  defer off-goal findings instead of expanding this run until it loses shape.
- Do not run an expensive full cosmic-ray campaign unless the mutation slice
  proves the targeted survivor triage cannot be resolved with cheaper
  deterministic and targeted-kill proof.
- Do not change release surfaces unless a slice discovers a direct release
  correctness blocker; if that happens, stop and re-plan the release boundary.

## Boundaries

- In scope: repo-local code, tests, docs, skills, scripts, validation helpers,
  and charness artifacts needed to close #268, #264, #269, #270, and the
  autonomous portion of #265/#261.
- In scope for #268: achieve closeout validation, issue closeout draft
  pre-validation, goal-artifact evidence floors, closeout-surface sweep
  guidance, and tests/validators that make bypasses fail before external
  mutation. This is a hard phase gate: do not stage issue-closing work for later
  slices until this slice has targeted proof.
- In scope for #264: the skill-portability library/checker, author-only
  doc/test cite discriminator, operator-surface allowlist, marker escape hatch,
  cross-skill cite sweep, portable-authoring reference sentence, and tests.
- In scope for #269/#270: achieve artifact wording that could stale against a
  mutable HEAD, and mutation proof workflow that binds targeted mutants to exact
  gate-reported lines before mutation.
- In scope for #265/#261 only after the earlier guard slices: inspect the
  residual survivors, prove the precise survivor behavior, add or adjust tests
  where the intended behavior is already clear, and stop on a real gate-design
  or semantics choice. Equivalent-mutant classification and mutation-standard
  changes are not autonomous unless the existing repo policy already decides
  them mechanically.
- Stop and ask the user if a slice requires choosing a new product metric,
  changing release/version policy, pushing or closing live GitHub issues,
  accepting lower mutation standards, or deciding behavior where the current
  repo contract is ambiguous.
- Tracked bug-class issue rule: run a `debug`/root-cause step before the fix
  slice when the issue is bug-class, and stage issue closeout through the issue
  workflow or commit close keywords; do not directly close live issues.
- Portability invariant: host-specific behavior stays in adapters, presets,
  hooks, and integration manifests; public skills and shared references must not
  bake in one host's path or provider assumptions.
- Shared-tree review invariant: any bounded reviewer inspects prior versions via
  read-only git plumbing only; no checkout/restore/reset/stash/add for
  inspection.

## User Acceptance

- The final report names which of #268, #264, #269, #270, #265, and #261 were
  completed, partially completed, or intentionally left open, with issue-ready
  closeout text or explicit non-claims for each.
- `git log --oneline origin/main..HEAD` shows small, reviewable commits whose
  subjects map to the slices; `git status --short --branch` is clean unless the
  user explicitly pauses before commit.
- `python3 scripts/check_goal_artifact.py --repo-root . --goal-path
  charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md` passes at
  closeout.
- Slice-local tests and validators pass after each meaningful slice, and the
  final broad gate or documented local substitute passes before completion.
- Any live/external proof not run is named as a non-claim, not implied.
- The goal proceeds slice-to-slice only after the expected evidence for the
  completed slice is recorded in `## Slice Log`.

## Agent Verification Plan

### Low-Cost Checks

- Before pursuing: `python3 skills/public/achieve/scripts/check_goal_artifact.py
  --repo-root . --goal-path
  charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md
  --pursue-ready`.
- Per slice: run targeted pytest/ruff/validator commands for the touched files;
  record exact commands and results in `## Slice Log`.
- When tests are added or expanded, record a cheap duplicate/length/pressure
  sample or the reason it was not applicable.
- Before any commit after code/test/doc mutation: run
  `python3 scripts/run_slice_closeout.py --repo-root .` or a narrower
  justified aggregate when the slice is docs/artifact-only.
- For mutation-work slices: bind the target to the exact gate-reported line
  before hand-mutating; record RED target-kill proof and GREEN restoration.

### High-Confidence Checks

- Final `./scripts/run-quality.sh --read-only` unless the run remains strictly
  docs/artifacts and the docs-only subset is the justified local substitute.
- `python3 scripts/check_changed_surfaces.py --repo-root .` when changed
  surfaces are unclear.
- Fresh-eye critique/review at material boundaries, with concrete host signal
  recorded if delegation is blocked.
- Final closeout evidence includes a bound retro artifact, host-log probe output
  or an explicit skip reason, a bound disposition review artifact or
  `host-blocked-subagent` skip, and gather/release coordination floor handling.
- `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root .
  --goal-path charness-artifacts/goals/2026-05-31-autonomous-backlog-hardening.md`
  before flipping complete.

### External Or Live Proof

- GitHub issue closure is not performed by this goal operator unless a later
  explicit user instruction says to mutate live issues. Stage closeout evidence
  locally instead.
- No push or release publication is part of this goal. If final proof depends on
  remote CI, record it as `not run` and give the maintainer the exact follow-up.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Confirm pursue-readiness and live issue context for the selected backlog | Prevent a broad autonomous instruction from running with stale or unshaped state | Goal artifact pursue-ready; current `gh issue list`/issue details reviewed; any stale handoff item recorded as off-goal | pending |
| 1 | #268 closeout integrity: make achieve closeout and issue closeout drafts fail before incomplete external or host-level completion | This run will create closeout state; harden the proof floor first | Tests/validators for goal evidence floor and issue closeout draft pre-validation; slice closeout green | pending |
| 2 | #269 stale mutable-HEAD wording guard | This proof-quality guard can affect this goal's own final artifact wording | Achieve artifact wording avoids stale mutable HEAD claims; validator/test or reference update pins the rule | pending |
| 3 | #264 portability guard and cross-skill cite sweep | Curated handoff chunk with well-scoped discriminator/allowlist; reduces portability drift before broader skill edits | Guard implemented; author-only doc/test cites blocked; operator surfaces (`docs/handoff.md`, `charness-artifacts/...`, adapter yaml) allowed; marker-qualified authoring-repo cites allowed; docs/reference updated; targeted tests green | pending |
| 4 | #270 exact-line targeted mutant proof guard, then #265/#261 mechanical survivor triage | Exact-line proof is the prerequisite for honest targeted survivor mutation; heavier survivor work should follow proof/portability guardrails | Gate-reported line/source target recorded before mutation; exact survivor behavior mapped; clearly real survivors killed with RED/GREEN proof; issue-ready residual policy decision recorded if needed | pending |
| 5 | Final closeout, critique, retro, handoff refresh, and commit discipline | Consolidate proof and leave the next operator a clean state | Final gate/substitute pass; goal artifact complete; retro improvements dispositioned; docs/handoff.md updated only at closeout; commits created | pending |

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

- Routing: `find-skills` already routed bare handoff pickup to
  `charness:handoff`, and the chunker ranked the backlog before this goal was
  shaped.
- Gather: n/a — no arbitrary external URL/source is being summarized into this
  artifact; issue tracker state is used as the work queue and must be refreshed
  through the issue/handoff workflow inside the relevant slice.
- Release: n/a — no release surface is planned; stop and re-plan if one becomes
  necessary.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/handoff.md` current `Workflow Trigger`, `Current State`, and ranked
  `Next Session` entries.
- Handoff chunker output from this session: `chunk-5` (#268), `chunk-1` (#264),
  `chunk-3` (#269/#270), `chunk-2` (#265/#261), then `chunk-4` broad backlog.
- Live issue list freshness: `gh issue list --state open --limit 50` read at
  2026-05-31T20:08:56+09:00; issue ids are treated as live issue workflow state,
  not gathered external source material.
- `charness-artifacts/quality/latest.md` for current validation posture and
  gate expectations.
- `charness-artifacts/retro/recent-lessons.md` for current repeat traps:
  exact-line mutation proof, stale mutable-HEAD wording, and mutation runner
  cleanup lessons.
- `docs/conventions/implementation-discipline.md` and
  `docs/conventions/operating-contract.md` for verify-before-commit,
  closeout-only handoff writes, critique, and commit discipline.
- Open issue ids in scope: #268, #264, #269, #270, #265, #261. Broad backlog
  issue ids are intentionally not pulled into this goal unless filed as
  off-goal findings.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only draft vs implementation-continuation. Chosen:
  implementation-continuation after explicit `/goal` activation, because the
  user asked to set the goal so all autonomous work can proceed. Rejected:
  artifact-only draft would strand the requested autonomy.
- Scope family: one chunk, all handoff chunks, or all open issues. Chosen: all
  handoff-ranked chunks in the current autonomous hardening tranche, with
  product/gate-policy decisions as stop conditions. Rejected: one chunk is too
  narrow for the user's wording; all open issues would overreach into product
  metrics and broad backlog churn.
- Ordering family: #264 first per handoff memo vs #268 first per chunker rank.
  Chosen: #268 first because closeout integrity should be hardened before this
  run creates more closeout evidence; this intentionally overrides the handoff
  memo's #264-first curation because the chunker read the live backlog and
  ranked #268 first. Rejected: #264 first remains reasonable but leaves the
  known closeout bypass active during subsequent slices.
- Sequencing family: #269/#270 as one process slice vs split by use point.
  Chosen: #269 immediately after #268 because it can affect this goal's own
  final proof wording; #270 immediately before #265/#261 because it is most
  useful as the targeted-mutation checklist. Rejected: bundling them as generic
  process work hides their different proof timing.
- Host/provider/environment axis: host-specific behavior is an axis in this
  repo. Chosen: keep host-specific behavior in adapters/hooks/manifests and
  write portable public skill/docs behavior. Rejected: Codex-only or
  Claude-only assumptions in shared surfaces.
- Release axis: release is not part of this goal. Chosen: `Release: n/a` unless
  a direct release-surface blocker is discovered. Rejected: opportunistic
  version bump during a maintenance/autonomy run.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Fresh-eye satisfaction: parent-delegated. Three bounded reviewers completed
  read-only lenses: sequencing, autonomy boundary, and proof/closeout risk.
- Act Before Ship findings folded: narrow wording from "all autonomous backlog"
  to a closed hardening tranche; fill the required sections; make #268 a hard
  first phase gate; split #265/#261 so autonomous work stops before
  equivalent-mutant or gate-policy decisions; explicitly exclude product,
  release, live mutation, and broad backlog expansion.
- Bundle Anyway findings folded: keep #268 first; move #269 immediately after
  #268; keep #270 adjacent to #265/#261; inline #264 discriminator/allowlist;
  add per-slice evidence and freshness.
- Same-agent preflight folded: the phrase "all autonomous work" can overreach.
  Folded into Non-Goals, Boundaries, and stop conditions so the agent cannot
  silently absorb product decisions, live issue mutation, release work, or broad
  backlog grooming.
- Same-agent preflight folded: #268 should precede #264 despite handoff curation
  because closeout-proof bypasses should be fixed before generating more
  closeout state.
- Valid but defer: #184/#185 product success work remains outside this goal
  because it requires product judgment, not only repo maintenance execution.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

## User Verification Instructions

## Auto-Retro
