# Achieve Goal: Handoff and open issue generative closeout

Status: active
Created: 2026-06-01
Activation: `/goal @charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`

This file is the living goal scratchpad. It is active as of 2026-06-01 KST.

Mode: active goal execution. The pre-activation decisions are frozen below; this
run now implements the accepted sequence and records slice evidence here.

## Goal

Shape the current handoff state and every issue open at activation into one
auditable, generative closeout sequence that can discuss unresolved decisions,
execute maintenance slices in dependency order, and leave each issue either
closed through an explicit carrier or intentionally open with a documented
reason.

## Non-Goals

- Do not close, comment on, relabel, or otherwise mutate live GitHub issues
  before the final carrier. Maintainer authorization is granted for final
  carrier live close/comment work when the issue matrix, gates, and carrier body
  are ready.
- Do not push local commits, open a PR, or cut a release as part of shaping this
  goal. Publishing is deferred to the final carrier.
- Do not close the product-success issue (#184) in this goal. The maintainer has
  active but not-yet-organized product-success thinking; leave #184 open with a
  precise carry-forward note. Resolving #184 later requires re-reading/gathering
  its originating Slack thread plus the maintainer's newer product-success
  framing.
- Do not treat AI/ML engineering success (#185) as a sufficient product-success
  definition. This goal may close #185 only by recording necessary engineering
  success conditions and, when useful, implementing supporting usage/report
  surfaces.
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
- Local branch state matters: the run is intentionally accumulating local
  commits on `main` for a final carrier. After Slice 3, `main` is ahead of
  `origin/main` by 11 commits through `d1970c1 Record workflow safety goal
  progress`. These commits are not published early; they are folded into the
  final carrier.
- Stop and ask the user when a slice requires product metric choices for #184,
  release/version policy, live issue mutation before the final carrier, push/PR
  publication before the final carrier, or accepting a lower quality/mutation
  standard.
- Pre-activation decision rule: decide all policy/scope questions in this
  session before activation, except #184 product success, which is intentionally
  carried forward as a separate open issue. The next session should activate and
  implement the accepted plan, stopping only when implementation discovers a
  genuinely new decision not covered here.
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
- Live GitHub closure/commenting and publish/PR work happen only in the final
  carrier, after the matrix and gates are ready. Remote CI and release proof are
  named as run or not-run non-claims; none are implied.

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

- Live GitHub issue closure/commenting is authorized only as the final carrier,
  after local proof and the issue matrix are complete. Close/comment exactly the
  rows marked for live action; leave-open rows get their documented reason.
- Push/PR creation is deferred to the final carrier. If the repository policy
  calls for a PR instead of direct push, prepare/open the PR there with the
  issue closeout body.
- No release is planned. If a slice touches a release surface, stop and route
  through `release` before proceeding.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Refresh handoff, branch, open-issue state, and pre-activation decisions; build the closeout matrix | Prevent stale handoff or tracker state from driving a broad closeout run | Current `gh issue list`, `git status`, `origin/main..HEAD`; matrix rows for #272/#265/#261/#259/#258/#252/#243/#241/#237/#236/#185/#184; final-carrier authorization recorded | complete |
| 1 | Restore or reclassify the current mutation-gate blocker (#272) | A current mutation report is quality-blocking even though Python survived count is 0, because changed-line blockers excluded changed files before mutation | Root cause/debug record; decide stale vs real blocker; changed-line coverage/selection proof; local mutation/quality proof; issue closeout row | complete |
| 2 | Finish the mutation survivor cluster (#265/#261) through this session's accepted policy boundary | Survivor triage depends on a trustworthy mutation baseline and can otherwise absorb unlimited effort | Updated survivor inventory; real survivors killed; equivalent/policy decisions applied from this session; close/leave-open rows for #265/#261 | complete |
| 3 | Close workflow-safety issues that affect future closeout quality (#258/#259/#237/#236) | These reduce risk while working the rest of the backlog: review index safety, symbol residue, live-apply commit classification, CI-only retry discipline | Implemented guards/docs/tests or explicit non-implementation decisions; closeout rows for each issue | complete |
| 4 | Close setup/portability extension issues (#252/#241) | These share the host-extension/compact-contract boundary and should be designed together | Compact AGENTS/setup contract and create-skill adapter extension path, or scoped split with reasons; targeted validation | pending |
| 5 | Make usage episodes useful or explicitly narrow their promise (#243) | Telemetry is collected but has no consumer; this can observe necessary engineering-success conditions, not prove product success | Usage report/consumer and capture-gap signal tied to closeout correctness, validation cost, portability, continuity, or decision-before-automation; or a documented decision to narrow/remove the surface | pending |
| 6 | Record and apply AI/ML engineering necessary-success conditions (#185), while leaving product success (#184) open | #185 can be closed by engineering principles and supporting implementation; #184 needs separate product thinking not settled in this goal | Decision artifact for necessary engineering success conditions; optional #243 implementation linkage; #185 closeout row; #184 leave-open row: product-success frame pending maintainer synthesis and source-thread refresh | pending |
| 7 | Final carrier: verify, critique, retro, handoff refresh, publish, and live issue close/comment | Only after rows are resolved should the run mutate live GitHub state or publish | Final gates; goal complete; retro dispositions; handoff refreshed; close keywords/comments/PR body match matrix; push/PR and live issue actions completed or explicitly blocked | pending |

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

## Issue Closeout Matrix

Slice 0 refreshed the live backlog on 2026-06-01 KST. No new open issues were
discovered beyond the 12 already shaped into the goal, so no issue is marked
`out of activated scope`. All live issue close/comment work is deferred to the
final carrier after local proof and carrier-body validation.

| Issue | Cluster | Intended Disposition | Closeout Carrier / Evidence |
| --- | --- | --- | --- |
| #272 | Mutation/report reliability | Close in final carrier | `cd9cfc5 Clarify mutation report blockers` separates overall status, mutation score, and blocking signals; debug artifact `charness-artifacts/debug/2026-06-01-issue-272-mutation-report-clarity.md`; final PR/issue carrier should explain `Killed: 78`, `Survived: 0`, score pass, and changed-line blocker disposition |
| #265 | Mutation/report reliability | Close in final carrier | Existing `765f5d4 Harden coordination survivor tests` is ancestor of HEAD/origin/main; current proof re-rendered the scoped trio dump as 514/514 executed, 467 killed, 47 survived, 90.9% reachable score; focused survivor tests pass |
| #261 | Mutation/report reliability | Leave open intentionally | Final carrier note/comment should say mechanical survivor triage is done via #265, but equivalent/low-value mutation-standard policy remains open; no gate-design exclusion was implemented in this goal |
| #259 | Closeout/workflow safety | Close in final carrier | `d7fb8e4 Harden workflow safety closeout` adds advisory `check_symbol_residue.py` with deleted-symbol scanning plus explicit `--symbol`/`--concept`; implementation-discipline docs and targeted tests prove the workflow |
| #258 | Closeout/workflow safety | Close in final carrier | Existing shared reviewer hygiene plus `check_staged_reversion.py` are now wired into the actual `.githooks/pre-commit` predict path via `staged_commit_gate_plan.py`; fresh-eye re-review reported no remaining blockers |
| #252 | Portability/setup extensibility | Close after setup accepts a compact AGENTS profile while preserving irreducible host-read-time safety rules | Setup validation tests and compact profile docs |
| #243 | Usage/engineering success | Close after usage episodes have a consumer/report or the promise is explicitly narrowed; the report may observe necessary engineering-success conditions but must not claim product success | Usage report/consumer tests or narrowed-contract decision |
| #241 | Portability/setup extensibility | Close after `create-skill` adapter metadata supports a host-owned extension namespace without forking Charness-authored files | Adapter resolver tests and docs for `host_extensions` / `x-*` semantics |
| #237 | Closeout/workflow safety | Close in final carrier | `achieve` lifecycle now requires post-apply checkpoint, current `HEAD`, and `runtime-affecting`/`test-only`/`audit-doc-only` classification with uncertainty treated as runtime-affecting |
| #236 | Closeout/workflow safety | Close in final carrier | `quality` maintainer-local enforcement now carries focused CI-only failure recovery before another broad full-gate push retry |
| #185 | Usage/engineering success | Close after necessary AI/ML engineering success conditions are recorded and any chosen supporting implementation is complete | Decision artifact plus optional #243-linked usage/report implementation |
| #184 | Product success | Leave open intentionally | Final carrier note: product-success frame pending maintainer synthesis and source-thread refresh (`slack://C05J5LTFSCU/1778805288.184149`) |

## Slice Log

_Goal activated on 2026-06-01 KST. Slice reports below are the running source of
truth._

### Slice 0: Activation and live backlog refresh

- Objective: Refresh handoff, branch, open-issue state, and pre-activation decisions; build the closeout matrix.
- Why this approach: The goal spans the whole live open backlog, so execution must start from current tracker and branch state rather than the shaping snapshot.
- Commits: n/a — activation/context slice
- What changed: Goal status flipped to active; Issue Closeout Matrix added; Slice 0 marked complete; activation branch proof updated from ahead 1 to ahead 5.
- Alternatives rejected: Did not start #272 implementation before recording the matrix; issue closure and publish remain final-carrier work.
- Targeted verification: PASS: find-skills read-only route recommends achieve/handoff/issue; PASS: check_goal_artifact.py --pursue-ready; PASS: git status --short --branch reports main...origin/main [ahead 5]; PASS: gh issue list shows the same 12 open issues (#272/#265/#261/#259/#258/#252/#243/#241/#237/#236/#185/#184); PASS: handoff parser with --with-issues reports 13 entries, 12 issue entries, 2 deduped issue refs.
- Test duplication pressure: No tests added.
- Critique: Pre-activation critique already folded into the goal; #258 read-only reviewer guard remains active before any fresh-eye review.
- Off-goal findings: No new open issues discovered; no out-of-activated-scope rows needed.
- Lessons carried forward: Keep all live issue mutation and publish work for the final carrier; treat the issue matrix as the source of truth for close vs leave-open decisions.
- Metrics: Metrics: when available.

### Slice 1: Issue 272 mutation report clarity

- Objective: Resolve the confusing mutation report where overall Status: FAIL appeared alongside Killed: 78, Survived: 0, and a passing reachable score.
- Why this approach: #272 was a report-interpretation blocker: the gate could fail correctly on changed-line coverage/selection while the single status row made it look like survived mutants caused the failure.
- Commits: cd9cfc5 Clarify mutation report blockers
- What changed: Separated mutation summary rendering into Status, Mutation score, and Blocking signals rows; documented how to read score-pass/blocker-fail reports; pinned changed-line blocker and advisory-only PASS report shapes in tests; recorded a debug artifact and refreshed the seam-risk index; synced the plugin mirror and froze the quality dogfood note.
- Alternatives rejected: Did not weaken or remove the changed-line blocker; did not run live Cautilus because the planner reported no proof kind and deterministic validation owned the slice.
- Targeted verification: PASS: pytest -q tests/quality_gates/test_quality_mutation_score_validity.py tests/quality_gates/test_check_mutation_score_partial.py (30 passed); PASS: pytest -q tests/quality_gates/test_public_skill_dogfood.py tests/quality_gates/test_quality_mutation_score_validity.py tests/quality_gates/test_check_mutation_score_partial.py (32 passed); PASS: ruff check scripts/check_mutation_score.py tests/quality_gates/test_quality_mutation_score_validity.py; PASS: python3 -m py_compile scripts/check_mutation_score.py; PASS: python3 scripts/validate_debug_artifact.py --repo-root .; PASS: python3 scripts/validate_public_skill_dogfood.py --repo-root .; PASS: python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review (latest run completed, including broad pytest and agent-browser runtime guard).
- Test duplication pressure: Expanded existing mutation-score validity tests only; no new test file. check_python_lengths passes, with scripts/check_mutation_score.py at 477/480 and in advisory warn band.
- Critique: Fresh-eye read-only subagent Banach reviewed the diff and reported No findings; it confirmed mutation_metrics/main pass/fail semantics stayed unchanged and the new changed-line label maps to the existing changed_scope_gap_count blocker.
- Off-goal findings: Cautilus planner reported next_action none / proof_kinds none; routine deterministic validation owns this slice. scripts/check_mutation_score.py is near the hard length limit and should get a helper-module split before more expansion.
- Lessons carried forward: For mutation reports, keep overall gate status, score threshold result, and non-score blockers separate so a correct failure is not misread as a survived-mutant failure.
- Metrics: Usage episode emitted by slice closeout at `.charness/usage-episodes/usage_episode.jsonl` with episode id `slice-closeout-3dd74c6ba699474d80591f59159b525e`; host token/tool metrics unavailable.

### Slice 2: Issues 265 and 261 survivor disposition

- Objective: Refresh the coordination-cues survivor evidence and decide the close/leave-open boundary for #265/#261 without redoing already-merged mechanical triage.
- Why this approach: #265 is the residual exhaustive triage pickup for #261; current HEAD already contains the survivor-hardening commit, so the cheapest correct move is to verify that evidence and record which issue is closable versus policy-bound.
- Commits: 765f5d4 Harden coordination survivor tests (already ancestor of HEAD/origin/main); no new implementation commit in this slice
- What changed: No code changed. Re-read live #265/#261 issue bodies; confirmed `765f5d4` is an ancestor of HEAD and origin/main; re-rendered the existing scoped Cosmic Ray dump through the clarified #272 summary path; updated the goal matrix so #265 closes in the final carrier and #261 remains open for the equivalent/low-value mutation-standard policy decision.
- Alternatives rejected: Did not add more low-value survivor tests or implement equivalent-mutant exclusion. Did not close #261 under #265 proof because #261 still owns the mutation-standard policy boundary the user wanted kept separate.
- Targeted verification: PASS: gh issue view 265 and 261 read current OPEN issue bodies; PASS: git merge-base --is-ancestor 765f5d4 HEAD and origin/main contains 765f5d4; PASS: python3 scripts/check_mutation_score.py --repo-root . --stats reports/mutation/coordination-cues-dump.jsonl --sample-manifest reports/mutation/nonexistent-sample.json re-rendered 514/514 executed, 467 killed, 47 survived, 90.9% reachable score vs 80% threshold; PASS: pytest -q tests/quality_gates/test_goal_coordination_floors.py tests/quality_gates/test_goal_disposition_gate.py tests/quality_gates/test_goal_head_freshness.py tests/quality_gates/test_achieve_before_activation.py (84 passed).
- Test duplication pressure: No tests added. Reused existing survivor-hardening tests and existing ignored Cosmic Ray dump for evidence refresh.
- Critique: No new diff to critique. Prior fresh-eye critique for this survivor-hardening unit is recorded at charness-artifacts/critique/2026-06-01-265-261-coordination-survivor-triage-critique.md with no blockers; this slice only maps that proof to the active issue matrix.
- Off-goal findings: The re-rendered scoped summary still reports blocking signals for sampled mutants without coverage and a deliberately nonexistent sample manifest; these are not new survivor failures and are unsuitable as scheduled-gate closeout proof. They remain context for why #261's mutation-standard policy is left open.
- Lessons carried forward: Do not re-pay a full mutation campaign when the target files and tests have not changed; record whether the remaining work is mechanical survivor killing or a policy decision.
- Metrics: Scoped survivor proof remains 514/514 executed, 467 killed, 47 survived, 90.9% reachable score.

### Slice 3: Workflow safety issues 258 259 237 236

- Objective: Close workflow-safety issues that reduce future closeout risk: shared-worktree reviewer index safety, symbol/concept residue, live-checkpoint commit classification, and CI-only retry discipline.
- Why this approach: These four issues are proof-quality and closeout-safety infrastructure; closing them before portability/usage slices reduces the chance of corrupt commits, stale docs, misleading deployment closeout, or expensive CI retry loops.
- Commits: d7fb8e4 Harden workflow safety closeout
- What changed: Added `check_symbol_residue.py` advisory with deleted-symbol scanning plus explicit `--symbol`/`--concept` inputs; wired `check-staged-reversion` into the pre-commit `--predict-commit` plan; documented symbol-residue use in implementation discipline; added achieve post-apply checkpoint commit classification guidance; added quality CI-only failure recovery guidance; updated public-skill dogfood notes; synced plugin mirrors and added targeted tests.
- Alternatives rejected:
- Targeted verification: PASS: pytest -q tests/quality_gates/test_check_symbol_residue.py tests/quality_gates/test_workflow_safety_docs.py tests/quality_gates/test_check_staged_reversion.py tests/quality_gates/test_achieve_before_activation.py tests/quality_gates/test_inventory_ci_local_gate_parity.py (42 passed before blocker fixes); PASS: pytest -q tests/quality_gates/test_check_symbol_residue.py tests/quality_gates/test_staged_commit_gate_plan.py tests/quality_gates/test_check_staged_reversion.py tests/quality_gates/test_workflow_safety_docs.py (27 passed after blocker fixes); PASS: ruff check touched scripts/tests; PASS: python3 -m py_compile scripts/check_symbol_residue.py scripts/staged_commit_gate_plan.py; PASS: python3 scripts/staged_commit_gate_plan.py --repo-root . --paths scripts/check_staged_reversion.py --json shows check-staged-reversion first; PASS: python3 scripts/check_symbol_residue.py --repo-root . --concept 'Trivial Goal Exemption' --json; PASS: python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review (completed, broad pytest and agent-browser guard passed).
- Test duplication pressure: Added two focused test files and expanded staged_commit_gate_plan tests. Broad closeout passed; length gate only reported existing advisory warn-band files.
- Critique: Fresh-eye reviewer Sartre first found two blockers: #258 detector was not in the pre-commit predict path, and #259 needed explicit non-Python concept input. Both were fixed; follow-up review reported No remaining blockers.
- Off-goal findings: No new live issues filed. Cautilus planner reported next_action none/proof_kinds none for achieve and quality; dogfood notes were recorded instead of running live Cautilus.
- Lessons carried forward: Closeout affordances need to be wired into the actual commit path, not only implemented as standalone scripts; prose residue scans need explicit concept input when the deleted idea is not recoverable from a Python symbol.
- Metrics: Usage episode emitted by slice closeout: slice-closeout-0321918b7511417a9908562f9ef620a8.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `docs/handoff.md` read on 2026-06-01 KST: workflow trigger, current local
  branch state, completed autonomous hardening tranche, and next-session publish
  / re-rank guidance.
- `gh issue list --state open --limit 100 --json number,title,labels,updatedAt,url`
  read on 2026-06-01 KST. Open issues at shaping time: #272, #265, #261, #259,
  #258, #252, #243, #241, #237, #236, #185, #184.
- `gh issue view 184 --json number,title,state,labels,body,updatedAt,url` read
  on 2026-06-01 KST. #184 explicitly cites an originating Slack thread
  (`slack://C05J5LTFSCU/1778805288.184149`) and says to re-read the source
  before resolving; this goal therefore leaves #184 open rather than forcing a
  stale product-success definition.
- `gh issue view 265` and `gh issue view 261` read on 2026-06-01 KST. #265 is
  the residual exhaustive-triage pickup for #261; #261 also carries the
  equivalent-mutant gate-design policy question.
- Handoff parser with live issue union:
  `parse_handoff_entries.py --repo-root . --handoff-path docs/handoff.md
  --with-issues` reported 13 entries, 3 handoff entries, 12 issue entries, and
  2 deduped issue references (#184/#185 from handoff).
- Current branch proof at activation: `git status --short --branch` reported
  `main...origin/main [ahead 5]`; `git log --oneline origin/main..HEAD` reported
  `15b384b`, `273529d`, `279616f`, `93150d8`, and `33971f2`.
- Current branch proof after Slice 3: `git status --short --branch` reports
  `main...origin/main [ahead 11]`; `git log --oneline origin/main..HEAD` adds
  `b16ca67`, `cd9cfc5`, `c841cfa`, `45fa641`, `d7fb8e4`, and `d1970c1`.
  These local commits are final-carrier material and are not published early.
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

- Mode family: artifact-only draft vs implementation-continuation. Historical
  shaping choice: artifact-only draft, then implementation-continuation after
  explicit `/goal` activation. Current state: the goal is now active and Slices
  0-3 have executed; the remaining document job is to keep the active run
  auditable and make the next slice pickup unambiguous, not to re-present this
  as an inert draft.
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
- Product-success axis: #184 is not closed here. Chosen: leave #184 open as a
  separate product-success issue because the maintainer has recent thinking that
  is not yet organized and the issue's source thread must be refreshed before
  resolution. Rejected forcing a product-success definition from engineering or
  usage metrics.
- Engineering-success axis: #185 can close here only as necessary conditions,
  not sufficient product success. Chosen necessary-condition set: closeout
  correctness, validation confidence per unit cost, portable host behavior,
  operator continuity, and decision before automation. Rejected claiming these
  are sufficient for product success without evaluator-backed evidence.
- Evaluator evidence axis: sufficient product-success claims would need a later
  approved evaluator-backed proof path. In this repo, that means routing through
  `quality` and the supported `cautilus evaluate fixture`, `cautilus evaluate
  observation`, or `cautilus evaluate skill-experiment` surfaces when
  appropriate; do not invoke unsupported Cautilus discovery or broader agent
  orchestration.
- Host/provider axis: Charness varies by host/runtime. Chosen: portable public
  skill behavior, with host-specific policy in adapters/hooks/manifests.
  Rejected Codex-only or GitHub-only assumptions in shared surfaces except where
  the issue-provider route is explicitly `gh`.
- Release axis: release is not part of the requested closeout goal. Chosen:
  `Release: n/a` unless activation discovers a touched release surface. Rejected
  opportunistic version bump or publication.
- Publish timing family: early publish of the existing local commits vs final
  carrier. Chosen: final carrier. Rejected early publish because the user wants
  all decisions settled in this session and next-session activation to implement
  the full sequence.
- Live issue action family: draft-only closeout vs live close/comment at final
  carrier. Chosen: perform live close/comment in the final carrier when the
  matrix and proof are ready. Rejected mid-run live mutation because issue rows
  can still change while implementation proceeds.
- Product/policy timing family: decide during goal vs decide before activation
  vs carry product success separately. Chosen: this session decides #185
  necessary-condition and #265/#261 policy boundaries before activation, while
  #184 remains open for separate product-success work. Rejected activation-time
  product debate because it would interrupt the intended long run; rejected
  pretending necessary engineering conditions are sufficient product success.
- #272 interpretation: the current report is not failing because Python
  mutants survived. It reports `Killed: 78`, `Survived: 0`, and `100.0%`
  reachable score, but still marks FAIL because changed-line blockers excluded
  changed files before mutation. The implementation slice should debug whether
  that blocking signal is stale, over-strict, or real uncovered changed-line
  debt.

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
- Same-agent preflight folded: #185 belongs late in the sequence because it
  produces a decision artifact and may drive #243 implementation; #184 stays
  open because product-success thinking is not ready to collapse into this
  closeout goal.
- Fresh-eye plan critique: executed by bounded read-only reviewer `Copernicus`
  (`019e8053-c853-7950-bf10-fb6f4ed5b26b`). Folded blockers: activation-time
  new issue drift must become explicit `accepted into scope` or
  `out of activated scope` rows; publish must not imply #272 proof and is now
  deferred to the final carrier; #258
  shared-worktree reviewer safety must be restated before any reviewer-assisted
  activation work even though the full #258 implementation remains Slice 4.
- Fresh-eye safe-to-leave, amended by user discussion: product-vs-maintenance
  boundary is now #185 necessary engineering success only; #184 product success
  remains open. Maintainer-confirmed final-carrier GitHub mutation guard is
  sufficient for this draft.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

_None yet._

## Final Verification

_Not started._

## User Verification Instructions

1. Review this file's issue list and remaining slice order, especially Slices
   4-7.
2. Run `python3 skills/public/achieve/scripts/check_goal_artifact.py --repo-root .
   --goal-path
   charness-artifacts/goals/2026-06-01-handoff-open-issue-generative-closeout.md`.
3. To continue the active goal, resume at Slice 4 (#252/#241). Do not re-run
   activation or re-open settled decisions from Slices 0-3 unless live tracker
   state has changed.
4. Expect the agent to stop for maintainer decisions around product-success
   metrics for #184, release surfaces, accepting a lower mutation/quality
   standard, or publishing/live GitHub mutation before the final carrier.

## Auto-Retro

_Not started._
