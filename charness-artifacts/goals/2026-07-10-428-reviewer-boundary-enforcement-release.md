# Achieve Goal: Enforce fresh-eye reviewer read-only boundaries (#428) and release

Status: complete
Created: 2026-07-10
Activation: `/goal @charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: closeout — all five slices executed; v0.65.0 released and
  #428 closed with verified carrier.
- Current slice intent: goal closeout (retro, dispositions, disposition
  review, handoff refresh, complete flip).
- Next action: none — goal complete; next-session pickups live in
  `docs/handoff.md` (#431 wiring, #430 fresh-session envelope probe, #421
  scheduled-run watch).
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
| 1 | Fix credentials-less failure in `capture-skill-run.sh` + regression test | Main's mutation gate is red; smallest unblocker | Test fails-before/passes-after in empty-HOME env; suite green | done (`3c25073c`) |
| 2 | #428 causal review + enforcement design via `issue` workflow | Handoff item 1; design before code | Recorded causal review + design in issue/goal artifacts | done (brief, no pause) |
| 3 | Implement #428 enforcement: reviewer envelope + pre/post worktree+index integrity verification + nested-spawn denial posture | The designed fix | New guard surface + regression tests covering the violation class | done (`5d894aa1`) |
| 4 | Quality gates, critique, issue closeout staging | Closeout discipline | Gate outputs, critique artifact, validate-closeout-draft proof | done (`7531144a`) |
| 5 | Release bump + push + publish + verify | Operator-requested final step | Release proof artifact, `gh release view`, remote CI observation | done (v0.65.0 published) |

## Operator Decision Queue

- Decision: prove the rail-2 reviewer envelope actually binds (spawn
  `bounded-reviewer` in a NEW session and confirm Bash/Edit/Write/Agent are
  denied with a concrete signal) — the mid-session probe in this run showed
  the tool restriction did NOT bind.
- Owner: operator (requires a fresh Claude Code session; the installed
  plugin was refreshed to 0.65.0 and active sessions must restart anyway)
- Why deferred: the host loads typed agent definitions at session start, so
  no in-session action can produce the proof; rail 1 covers the
  commit-corruption class meanwhile
- Unblock action: in a new session run the probe per issue #430 and record
  the denial (or non-denial) signal there
- Revisit trigger: first new session in this repo, or #430 resolution

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
- Gather: n/a — all context sources are repo-local artifacts, GitHub issues read through the adapter-resolved `gh` backend, and CI logs read via `gh run view`; no external source needed a durable gather asset.
- Release: charness-artifacts/release/latest.md — v0.65.0 published at https://github.com/corca-ai/charness/releases/tag/v0.65.0 (distinct-channel HTTPS readback 200), install refreshed 0.64.0 -> 0.65.0 on the maintainer machine.
- Issue closeout: #428 via direct-commit carrier `0528718e` (release bundle); `issue_tool.py validate-closeout-draft` ok:true pre-commit and `verify-closeout --expect-state CLOSED` returned status verified with resolution-critique evidence bound; #429/#430/#431/#432/#433 filed as tracked follow-ups, not closed.

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

### Slice 5: Slice 5: v0.65.0 release, #428 closeout, goal closeout

- Objective: Cut and publish v0.65.0 (minor: new additive maintained capability), carry the #428 close, verify externally, and close the goal.
- Why this approach: Operator-requested endpoint; minor bump justified by the new fingerprint capability shipped to consumers.
- Commits: 8bfa3147, 0528718e (carrier), b8930138 (tagged), 4b7ba6ca
- What changed: packaging + generated manifests via bump/sync, release/retro artifacts, release critique artifact, goal artifact closeout sections
- Alternatives rejected: Rejected: patch bump (new capability, not only fixes); helper --close-issue path (its generated commit fails the repo commit-msg closeout gate, #433 filed); rewriting placeholder-identity local commits (breaks artifact SHA references; config fixed forward instead, #432).
- Targeted verification: Release critique (fresh-eye): RELEASE-OK with one operator-confirm on close wording (applied verbatim in the carrier); fresh-checkout probes passed; release URL HTTP 200 distinct-channel; verify-closeout verified CLOSED; install refreshed 0.64.0->0.65.0; Quality Core success on pushed HEAD; Mutation Tests dispatched on 4b7ba6ca (watch recorded).
- Test duplication pressure: No new tests this slice.
- Critique: charness-artifacts/critique/2026-07-10-v0-65-0-release-critique.md (RELEASE-OK); reviewer conduct proven by rail-1 verify + transcript audit.
- Off-goal findings: #432 (identity leak), #433 (helper/gate mismatch) filed during this slice
- Lessons carried forward: Rehearse the helper-generated commit message against the commit-msg gate before --execute; amend-then-resume without close flags is the working seam until #433 lands.
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

- Issue #429 — shared skill scripts (`skills/shared/scripts/`) escape the
  ruff/length gate scope; found while manually linting the new fingerprint
  script.
- Issue #432 — a prior hotl proof session left the repo-local git identity as
  `hotl proof <hotl-proof@example.invalid>`; 62 commits carry the
  placeholder. Config unset this run; the structural restore/guard is the
  issue.
- Issue #433 — `publish_release.py --close-issue` composes a release commit
  the repo's own commit-msg closeout gate rejects; two failed publish
  attempts before the manual-carrier workaround shipped v0.65.0.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-07-10-428-reviewer-boundary-enforcement-release.md
Host log probe: charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release-host-log-probe.json
Disposition review: charness-artifacts/critique/2026-07-10-428-reviewer-boundary-disposition-review.md

Self-verification executed this run:

- Slice gates: `run_slice_closeout.py --skip-broad-pytest` all PASS at each
  slice boundary; release-time `./scripts/run-quality.sh --release` passed
  inside the publish helper.
- Broad proof: the exact CI baseline command
  (`python3 -m pytest -q -m 'not release_only' tests`) run in a
  credentials-less env: 4431 passed, 0 failed.
- Enforcement proof: 12/12 fingerprint regression tests; rail-1
  snapshot/verify clean around every bounded reviewer this run.
- External proof: at release-verification time origin/main and local HEAD
  both read `4b7ba6ca` (historical; the goal-closeout commit lands after);
  tag `v0.65.0` -> `b8930138`; release URL readback HTTP 200 (distinct
  channel);
  `verify-closeout` for #428 returned `verified` with state CLOSED;
  maintainer install refreshed 0.64.0 -> 0.65.0; post-push Quality Core
  workflow concluded success on `4b7ba6ca`.
- Pending external watch: the dispatched Mutation Tests run on `4b7ba6ca`
  (the #421 machine gate) — recorded in handoff; not claimed green here.

Residual risks and non-claims:

- Rail-2 envelope live binding unproven this session (mid-session spawn did
  not bind the tool restriction); spawn-denial has no automated regression —
  tracked #430, queued as the operator decision above.
- Rail-1 invocation not yet wired into consuming skills' spawn steps (#431);
  portable installs rely on the shared reference's Enforcement section.
- 62 pushed commits keep the placeholder author identity permanently (#432).
- No product-success/feedback signal is claimed; feedback events remain zero.

Timebox closeout (activation 02:17Z, closed ~04:50Z of a 6h box):

Early close rationale: the operator-requested endpoint (autonomous improvement, then push + release) is fully reached and externally verified; post-release continuation would either strand unpushed work or re-enter the external publish lane whose approval was scoped to this bundle, and the highest-value remaining items require a fresh session (#430 envelope probe) or their own dedicated run (#431 four-surface skill wiring, argparse debt pinned LAST/alone by handoff).
Early close report: charness-artifacts/goals/2026-07-10-428-reviewer-boundary-enforcement-release-early-close-report.md
Next slice candidate: #431 rail-1 spawn-step wiring in quality/release/issue/critique SKILL.md | decision: defer | reason: touches four gated public skill surfaces and deserves its own critique + release train, not a post-publish tail.
Next slice candidate: #430 fresh-session bounded-reviewer envelope binding probe + spawn-denial regression | decision: blocked | reason: the host loads typed agent definitions at session start, so no probe in this session can produce the binding proof.
Outcome sufficiency check: sufficient: all four User Acceptance lines are met and externally verified — release commits on origin/main with the tag and release page live, the CI baseline command green in a credentials-less environment, #428 closed with a per-acceptance-line verdict carrier, and the maintainer install refreshed to 0.65.0.

## User Verification Instructions

1. `git fetch && git log --oneline origin/main -4` — see `4b7ba6ca` /
   `b8930138` (tagged v0.65.0) / `0528718e` (the #428 closeout carrier).
2. Open <https://github.com/corca-ai/charness/releases/tag/v0.65.0> and
   <https://github.com/corca-ai/charness/issues/428> (CLOSED, with the
   behavior verdict in the carrier commit `0528718e`).
3. `CLAUDE_CONFIG_DIR=$(mktemp -d) python3 -m pytest -q tests/test_skill_efficiency_ab.py` — passes without credentials.
4. In a NEW session, run the #430 probe: spawn a `bounded-reviewer` subagent
   and ask it to run a shell command — expect a concrete tool-denial; record
   the result on #430 either way.
5. Watch the next Mutation Tests conclusion on #421 (machine-owned; do not
   close manually).

## Auto-Retro

Retro dispositions: applied: credentials-less capture-script guard + CI-parity test pin (commit `3c25073c`).
Retro dispositions: applied: #428 two-rail enforcement — fingerprint script, 12-test class matrix, read-only reviewer envelope, Enforcement contract section (commits `5d894aa1`, `8145629a`).
Retro dispositions: applied: reviewer-self-report-is-not-evidence lesson encoded in the shared reference's Enforcement section (closeout cites verify output, not self-report) and exercised live this run.
Retro dispositions: issue #429 (novel: shared-script lint/length gate scope gap found while hand-linting the new fingerprint script).
Retro dispositions: issue #430 (novel: rail-2 envelope live-binding proof and spawn-denial regression are absent; mid-session probe showed the tool restriction did not bind).
Retro dispositions: issue #431 (novel: rail-1 invocation is not wired at consuming skills' reviewer-spawn steps, so portable installs rely on the shared reference alone).
Retro dispositions: issue #432 (recurs: hotl proof git-identity leak — 62 placeholder-authored commits; `.invalid`-identity guard named in the issue direction).
Retro dispositions: issue #433 (novel: publish helper close-path composes a commit the repo commit-msg gate rejects; two wasted release-quality runs this release).
Retro dispositions: accepted-risk: background-agent completion produced no notification and TaskOutput could not resolve named agents, so multi-reviewer waits fell back to polling (~20 idle minutes this run) — the completion signal is host-runtime-owned, no repo surface owns it; recorded so the fan-out wait cost is expected, not rediscovered.

Structural follow-up: issue #432 (recurs: ambient machine state consumed instead of pinned — the same class produced both the CI credentials failure and the 62-commit identity leak; sibling sweep in the bound retro found no further unfiled instances in this run's changed surfaces)
