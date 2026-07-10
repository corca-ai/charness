# Achieve Goal: Enforce fresh-eye reviewer read-only boundaries (#428) and release

Status: active
Created: 2026-07-10
Activation: `/goal @charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 1 — credentials-less CI baseline fix in
  `scripts/agent-runtime/capture-skill-run.sh`.
- Current slice intent: make the mutation-CI baseline green again by guarding
  the unconditional `.credentials.json` copy (warn, not die) and making the
  behavioral capture test deterministic in a credentials-less environment
  (CI parity via `CLAUDE_CONFIG_DIR` pointed at an empty dir). One commit.
- Next action: implement + prove fails-before/passes-after in an empty-config
  env, then move to slice 2 (#428 causal review + design).
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

Autonomously improve the repo along the handoff backlog and ship the result:

1. **Restore the mutation-CI baseline on main.** The #421 machine gate is
   currently red because `scripts/agent-runtime/capture-skill-run.sh` hard-fails
   when `~/.claude/.credentials.json` is absent (CI runner), killing
   `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`
   before mutation sampling. Fix the environment-dependent failure with
   regression coverage that runs in a credentials-less environment.
2. **Resolve #428 end-to-end through the `issue` workflow:** give bounded
   fresh-eye reviewers an enforceable read-only boundary — unauthorized
   shared-tree/index writes and undelegated child spawning are prevented or
   fail with a concrete signal, and the parent can verify pre/post worktree and
   index integrity without trusting reviewer self-report. Regression proof
   covers the violation class, not one command or one host adapter.
3. **Release the bundle:** version bump, push, tag, published GitHub release
   with verification — explicitly requested by the operator's opening message.

Timebox: 6h
Activation time: 2026-07-10T02:17:57Z
Closeout reserve: 45m
Done-early policy: continue_next_improvement

## Non-Goals

- The 80-site argparse-help debt: handoff pins it to run LAST and alone in a
  dedicated session; it is out of scope here.
- Closing #421 manually: it is machine-owned; this goal only fixes the baseline
  failure so the scheduled gate can go green on its own.
- Fabricating a usage-feedback observation: feedback events stay at zero unless
  a legitimate observer-owned event appears.
- Redoing the repo-wide quality/speed sweep closed by
  `2026-07-10-repo-wide-quality-speed-release.md`.
- Handoff closeout-vocabulary demotion: deferred pending explicit live-capture
  approval; not reopened here.
- Live `claude -p` capture reruns (skill-efficiency A/B live arms): not needed
  for either fix and not approved.

## Boundaries

- External side-effect scope: the operator's opening message ("다 끝나면 푸시
  릴리즈") approves push + tag + GitHub release publication for the FINAL
  closeout bundle only. Slices commit locally; remote proof (push, release, CI)
  batches at the end. GitHub issue-comment/close writes for #428 ride the
  normal issue-closeout carrier at that same boundary.
- Reviewer subagents follow the shared-worktree read-only contract in
  `skills/shared/references/fresh-eye-subagent-review.md`.
- Coding-task implementation runs in lower-power-model subagents per the repo
  standing request; main loop keeps design, review, and synthesis.
- No changes to the machine-owned #421 gate policy or baseline without reading
  the latest scheduled-run summary first (done: run 29061283943, read at
  shaping time).

## User Acceptance

- `git log origin/main` shows the fix + #428 resolution + release commits, and
  the new tag/release page exists on GitHub.
- Re-running the mutation workflow's baseline command
  (`python3 -m pytest -q -m 'not release_only' tests`) in a credentials-less
  environment no longer fails `test_capture_script_behavioral_no_identity_in_run_view`.
- #428 is closed with a resolution comment mapping the acceptance boundary to
  executed proof; the enforcement capability is visible in the repo.
- `claude plugin` update on the maintainer machine picks up the new version.

## Agent Verification Plan

### Low-Cost Checks

- Targeted pytest for touched modules; `bash -n` / shellcheck for touched shell.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.
- `check_goal_artifact.py` after artifact mutations.

### High-Confidence Checks

- Full `python3 -m pytest -q -m 'not release_only' tests` before the release
  bundle (the exact CI baseline command), plus repo validators via
  `run_slice_closeout.py --verification-lock` at the final boundary.
- Credentials-less reproduction: run the failing test with `HOME`/
  `CLAUDE_CONFIG_DIR` pointed at an empty dir to prove the CI failure mode is
  fixed, not environment-masked.
- Bounded fresh-eye reviews for each substantial slice and the final
  disposition, run under the #428-hardened boundary once it exists.

### External Or Live Proof

- Push to origin/main; tag + `gh release create`; `gh release view` readback.
- Post-push: trigger/observe the mutation workflow result on the new HEAD (or
  record the scheduled-run watch as the follow-up if the run window is long).
- #428 closed on GitHub via the issue-closeout carrier with verify proof.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Fix credentials-less failure in `capture-skill-run.sh` + regression test | Main's mutation gate is red; smallest unblocker | Test fails-before/passes-after in empty-HOME env; suite green | planned |
| 2 | #428 causal review + enforcement design via `issue` workflow | Handoff item 1; design before code | Recorded causal review + design in issue/goal artifacts | planned |
| 3 | Implement #428 enforcement: reviewer envelope + pre/post worktree+index integrity verification + nested-spawn denial posture | The designed fix | New guard surface + regression tests covering the violation class | planned |
| 4 | Quality gates, critique, issue closeout staging | Closeout discipline | Gate outputs, critique artifact, validate-closeout-draft proof | planned |
| 5 | Release bump + push + publish + verify | Operator-requested final step | Release proof artifact, `gh release view`, remote CI observation | planned |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns. At completion, recorded
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
form below and replace `<skill>` with the find-skills-recommended skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- Routing: find-skills -> issue — `--recommend-for-task "resolve GitHub issue #428 with causal review and closeout"` ranked `issue` first (with `github-gh` as the ready tool route); #428 resolution and closeout run through it.
- Routing: find-skills -> impl — the recommend-for-task probe for "implement enforcement code and regression tests" returned no ranked match (recorded honestly); `impl` is the route by its shipped description ("work should move into code, config, tests"), used for slices 1 and 3.
- Routing: find-skills -> quality — `--recommend-for-task "run quality gates and validation before release"` ranked `quality` first (then `release`); slice-4 gate posture runs through it.
- Routing: find-skills -> release — `--recommend-for-task "cut and publish a plugin release"` ranked `release` first; slice-5 bump/publish/verify runs through it.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — the consequential decisions are (a) external side effects (push, tag, GitHub release publication, #428 issue close) and (b) broad autonomous scope. Both were explicitly granted by the operator's opening message this session ("이 리포를 자율 개선할 계획 짜서 진행해보세요. 다 끝나면 푸시 릴리즈."), which requests autonomous improvement and names push+release as the required final step; #428 resolution is the standing handoff item 1. No live/prod capture rerun is included, so no further approval is needed. Scope of the approval is this goal's final closeout bundle only.

## Slice Log

### Slice 1: Slice 1: credentials-less capture-script fix

- Objective: Restore the mutation-CI baseline: guard the unconditional .credentials.json copy in scripts/agent-runtime/capture-skill-run.sh and pin the behavioral test to a credentials-less CLAUDE_CONFIG_DIR for CI parity.
- Why this approach: Latest #421 scheduled run (29061283943) failed the coverage baseline at test_capture_script_behavioral_no_identity_in_run_view with cp: cannot stat .credentials.json; smallest unblocker and a red-gate precondition for the release slice.
- Commits: 3c25073c
- What changed: scripts/agent-runtime/capture-skill-run.sh (+ plugins mirror), tests/test_skill_efficiency_ab.py, goal artifact
- Alternatives rejected: Rejected: skipping the test in CI (masks the class); making credentials fatal-with-message (breaks the shimmed behavioral test and any credless host); test-only env pin without script guard (leaves real CI break in place).
- Targeted verification: fails-before reproduced locally with empty CLAUDE_CONFIG_DIR (same cp error as CI); after fix: target test + full tests/test_skill_efficiency_ab.py (70 passed) in both credentials-less and normal envs; bash -n; run_slice_closeout.py --skip-broad-pytest all PASS.
- Test duplication pressure: No new test added (existing test env pinned); file headroom 657/800 code lines (143 left).
- Critique: Slice-level self-check: warning (not silence) keeps real credless captures auditable; implementation ran in a lower-power subagent per standing request, parent re-verified independently.
- Off-goal findings: none
- Lessons carried forward: Env-dependent E2E tests should pin their external-state inputs (CLAUDE_CONFIG_DIR) instead of inheriting the maintainer machine; parity with CI is the test's job, not the runner's.
- Metrics:

### Slice 2: Slice 2: #428 classification + resolution brief (design)

- Objective: Classify #428 and fix the enforcement design before mutation, through the issue workflow (planner, full read with comments, feature-class resolution brief).
- Why this approach: Issue resolution contract: GitHub is source of truth; feature-class issues need a pre-mutation resolution brief; #428 explicitly asks for enforcement of an existing contract, not more prose.
- Commits: none (design only)
- What changed: none; resolution brief emitted in transcript (inline, no pause: open decisions empty)
- Alternatives rejected: Rejected: plugin packaging export of agents/ (schema+export surface too large for this fix-unit; deferrable follow-up); OS-level sandboxing (host-owned); run_slice_closeout coupling (enforcement point is the review boundary, not commit time); Bash-included reviewer envelope (would keep the write channel open and fail acceptance line 1).
- Targeted verification: issue_tool.py plan (backend_ready true) + read (comments_read true); classification feature per labels+desired-outcome; brief pause rule evaluated: open decisions none -> continue.
- Test duplication pressure:
- Critique: Design self-check folded into brief non-goals; fresh-eye critique deferred to the implementation slice boundary per meaningful-slice-cadence.
- Off-goal findings: none
- Lessons carried forward: Design: portable class-covering detection (fingerprint) + host envelope prevention (.claude/agents read-only reviewer) satisfies acceptance without new packaging surface.
- Metrics:

### Slice 3: Slice 3: #428 enforcement implementation

- Objective: Implement the two enforcement rails: portable worktree+index fingerprint (snapshot/verify with concrete drift paths) and the Claude host read-only reviewer envelope, wired into the fresh-eye reference and AGENTS.md.
- Why this approach: The designed fix from slice 2; the smallest complete unit that satisfies the #428 acceptance boundary.
- Commits: 5d894aa1
- What changed: skills/shared/scripts/reviewer_boundary_fingerprint.py (+mirror), tests/quality_gates/test_reviewer_boundary_fingerprint.py (12 tests), .claude/agents/bounded-reviewer.md, skills/shared/references/fresh-eye-subagent-review.md Enforcement section (+mirror), AGENTS.md bullet, .gitignore, .agents/surfaces.json claude-agent-definitions surface
- Alternatives rejected: Rejected during review: leaving _git_text strict-UTF8 (crash on non-UTF8 names); markdown link to the agent def (breaks in the plugin mirror); claiming rail 1 covers non-writing spawns (it does not; rail 2 only).
- Targeted verification: 12/12 targeted tests; tests/quality_gates 2716 passed pre-fix-round; run_slice_closeout --skip-broad-pytest all PASS; manual ruff on the shared script (gate scope gap filed as #429); dogfood: rail-1 snapshot/verify wrapped this slice's own fresh-eye critique (verify ok, drift empty).
- Test duplication pressure: New test file 151/800 code lines; duplicate-pressure low (new surface, no sibling suite).
- Critique: Bounded fresh-eye critique (parent-delegated reviewer): no blockers; 5 SHOULD-FIX all applied (surrogateescape decoding, snapshot-tamper non-claim + --out guidance, rail-1 scope wording, git-show/envelope reconciliation, repo-root path form) plus rename/corrupt-JSON/non-UTF8 regression tests. Tool-use audit of the reviewer transcript confirmed its self-report.
- Off-goal findings: #429 filed: shared skill scripts escape the ruff/length gate scope.
- Lessons carried forward: Host envelope tool restriction did not bind on a mid-session spawn (probe: TOOL-EXECUTED; meta agentType echoed the spawn name); typed-envelope live proof needs a fresh session — recorded as a non-claim, rail 1 verified live instead. Never trust reviewer self-report: audit tool_use events in the transcript.
- Metrics:

### Slice 4: Slice 4: quality gates, resolution critique, closeout staging

- Objective: Run the final quality proof and stage an honest #428 closeout: resolution critique, per-line acceptance mapping, carrier rehearsal.
- Why this approach: Issue workflow step 7 and repo closeout discipline before the approved external lane (push/release).
- Commits: 8145629a (+ critique artifact in the release-prep commit)
- What changed: charness-artifacts/critique/2026-07-10-428-resolution-critique.md, fresh-eye reference quarantine line (+mirror), goal artifact
- Alternatives rejected: Rejected: closing #428 with a flat 'acceptance met' claim (resolution critique BLOCKER: lines 1-2 rest partly on the unproven rail-2 binding); holding the close until fresh-session envelope proof (the issue's impact — silent closeout corruption — is closed by rail 1 everywhere; deferral tracked as #430).
- Targeted verification: Full CI-baseline command in credentials-less env: 4431 passed, 77 deselected, 0 failed; run_slice_closeout pre-lock aggregate all PASS; validate-closeout-draft ok:true for the direct-commit carrier; rail-1 verify clean around both reviewers.
- Test duplication pressure: No new tests this slice; suite runtime 3m41s local.
- Critique: Resolution critique (bounded fresh-eye, parent-delegated): CLOSE-WITH-EDITS; BLOCKER folded into the carrier draft; SHOULD-FIXes tracked as #430/#431; NIT applied. Artifact: charness-artifacts/critique/2026-07-10-428-resolution-critique.md
- Off-goal findings: #430, #431 filed (see critique artifact)
- Lessons carried forward: Honest close = per-acceptance-line verdict mapping, not a blanket met/unmet; the verify-full-clean-after-quarantine nuance came from the reviewer's masking analysis.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. Operator opening message (this session): autonomous improvement plan +
   execute, then push and release.
2. `docs/handoff.md` `## Next Session` — item 1 (#428 via `issue`), item 2
   (#421 machine-owned watch), item 3 (feedback observation only when
   legitimate), item 4 (argparse-help debt LAST/alone).
3. GitHub issue #428 body + comments (read at shaping time via `gh issue view`).
4. GitHub issue #421 latest scheduled-run comment: mutation workflow run
   29061283943 FAIL on `2fe1e046` — baseline pytest failed at
   `tests/test_skill_efficiency_ab.py::test_capture_script_behavioral_no_identity_in_run_view`;
   CI log shows `cp: cannot stat '/home/runner/.claude/.credentials.json'`
   from `scripts/agent-runtime/capture-skill-run.sh:125`.
5. Prior goal `charness-artifacts/goals/2026-07-10-repo-wide-quality-speed-release.md`
   (the three reviewer violations that motivated #428) and
   `charness-artifacts/retro/2026-07-10-repo-wide-quality-speed-release.md`.
6. `skills/shared/references/fresh-eye-subagent-review.md` (the prose contract
   #428 asks to make enforceable).

## Interview Decisions

- **Interpretation of the prompt** — options: artifact-only shaping vs.
  full implementation continuation vs. open-ended quality sweep. Chosen:
  full implementation continuation over the handoff backlog (#421 baseline fix
  + #428) ending in a release. Rejected: artifact-only (the operator said
  "진행해보세요" — proceed — and named the release endpoint); open-ended sweep
  (the repo-wide sweep closed today and handoff explicitly says do not redo it).
  The operator is not watching live, so this strong default is recorded instead
  of asked.
- **Backlog selection** — options: #428 only; #428 + CI baseline fix; add
  feedback/argparse items. Chosen: #428 + CI baseline fix. The baseline failure
  is a live red gate on main discovered during shaping (handoff item 2's watch
  duty), and shipping a release on a red mutation baseline would be a wrong
  green. Feedback needs a legitimate external event (none exists); argparse
  debt is pinned LAST/alone by handoff.
- **Release timing** — options: release per slice vs. one final bundle. Chosen:
  one final bundle; the operator approval is scoped to the end ("다 끝나면")
  and per-slice publication buys nothing here.
- **Timebox** — 6h with 45m closeout reserve; autonomous session with no
  operator-stated deadline; done-early policy continues to the next
  improvement per repo default.

## Plan Critique Findings

- Folded: release-on-red-baseline hazard — slice 1 (CI baseline fix) ordered
  before the release slice, and the final gate reruns the exact CI baseline
  command locally in a credentials-less reproduction, because a green local
  run with maintainer credentials would mask the CI failure mode.
- Folded: #428 enforcement must not regress the legitimate maintainer flow of
  `capture-skill-run.sh` (which intentionally copies credentials for real
  runs); the fix degrades to a warning, not silence, so a real capture without
  credentials still fails loudly at auth with an auditable stderr line.
- Folded: reviewer-boundary work reviewed under its own new boundary once it
  exists (dogfood), with the #258 shared-worktree rule kept intact.
- Over-worry, not folded: multi-host adapter matrix proof for #428 (Codex-side
  enforcement) — acceptance asks for the violation class, not every host; the
  portable contract + this host's enforcement + regression tests satisfy the
  written acceptance boundary. Recorded as a residual-risk line instead.
- Reviewer provenance: self-critique at shaping time; bounded fresh-eye
  critique runs at slice boundaries per the frame.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
