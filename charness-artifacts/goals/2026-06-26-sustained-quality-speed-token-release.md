# Achieve Goal: Sustained quality speed token release

Status: active
Created: 2026-06-26
Activation: `/goal @charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release.md`
Timebox: 3h
Activation time: 2026-06-26T09:34:18+09:00
Closeout reserve: 25m
Done-early policy: continue_next_improvement

This file is the active living goal scratchpad for the current run.

## Active Operating Frame

- Current slice: local-only quality continuation after premature release timing
  repair.
- Current slice intent: continue safe reversible quality/runtime/token-efficiency
  improvements without further push/release actions until the timebox closeout
  phase.
- Next action: inspect local quality/runtime candidates, choose one bounded
  non-release slice, run focused verification, critique, and commit it.
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

Run a timeboxed implementation-continuation goal for roughly three hours: keep improving Charness quality across bug fixes, test speed, script execution speed, and token efficiency, then push and prepare or publish the release surface when the release contract allows it.

## Non-Goals

- Do not weaken or remove the standing read-only quality gate.
- Do not publish a release until the release skill's proof contract is read and
  satisfied.
- Do not remove the final real CLI proof for a shipped entrypoint merely to
  lower a boundary-bypass count.
- Do not expand into unrelated product design or issue-closeout work unless a
  local quality finding must be tracked instead of fixed now.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Push/release is approved by the user's request for the final phase only; the
  run still performs local proof, release critique, and a second evidence
  channel before claiming publication.
- Cautilus remains eval-only and disabled unless the repo planner explicitly
  allows the wrapper path with a named failing-log source.
- Generated/plugin/export surfaces must be synced before validators when touched.

## User Acceptance

- Inspect the commits made during this goal and see concrete quality/runtime
  improvements rather than only prose.
- Run `./scripts/run-quality.sh --read-only` successfully after the final bundle.
- Confirm `main` is pushed and the release surface is prepared or published
  according to the repo release contract.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest for changed test modules.
- Boundary-bypass inventory summary before and after conversion slices.
- `git status --short` and generated-surface sync checks when relevant.

### High-Confidence Checks

- `./scripts/run-quality.sh --read-only` at final closeout and before push.
- Fresh-eye critique on the changed risk boundary before final broad proof.
- Release skill validation before any release publish step.

### External Or Live Proof

- `git push` result plus clean branch status after push.
- Release publish or release-preparation evidence from the release workflow; if
  publication is blocked by contract or credentials, record the concrete blocker.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Reduce more nested subprocess fanout while preserving real CLI smokes | Boundary inventory still shows 84 candidates / 144 keys / 47 convertible after prior improvements | Focused pytest, boundary inventory delta, critique artifact, commit | in-progress |
| 2 | Address the next highest signal quality/runtime/token issue found by inventories | Timebox mode continues improvement if slice 1 completes safely | Focused proof, quality artifact update, commit | queued |
| 3 | Final release and push bundle | User explicitly requested final push/release | Read-only quality gate, release proof, push output, clean status | queued |

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

Current queue: none — the user already authorized the final push/release lane;
credentials or release-tool refusal will be recorded here if encountered.

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

Routing: `find-skills` recommendation for the task returned `quality` for the
quality/runtime work and `release` for final publication.
Gather: n/a — no external URL/source context was provided for this goal.
Release: v0.56.1 was published prematurely before the intended final phase;
further push/release actions are paused until closeout. Evidence lives in
`charness-artifacts/release/latest.md` and
`charness-artifacts/retro/2026-06-26-premature-release-timing.md`.
Issue closeout: n/a — this goal is not resolving a tracked GitHub issue.

## Slice Log

### Slice 1: Retro and handoff boundary fanout

- Objective: Reduce nested subprocess fanout in retro and handoff behavior tests while preserving real CLI proof.
- Why this approach: The boundary-bypass inventory still had 84 candidates / 144 keys / 47 convertible files; these tests asserted ordinary JSON and artifact behavior through subprocesses even though import-safe main() seams existed.
- Commits:
- What changed: Converted recent-lessons refresh, retro persistence, and handoff merge-proposal behavior assertions to in-process main() calls; added quality and critique artifacts for the slice.
- Alternatives rejected: Deferred render_report.py and record_metric_window.py because they include unique CLI/argparse proof that should be split before conversion.
- Targeted verification: Focused pytest: 34 passed in 3.18s; ruff passed; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; existing tests changed from subprocess to in-process. Raw boundary inventory improved to 81 candidates / 141 keys / 44 convertible files.
- Critique: charness-artifacts/critique/2026-06-26-retro-handoff-boundary.md; fresh-eye reviewer 019f015c-bba6-79b2-9fa2-43135fc21015 found no issues.
- Off-goal findings: none
- Lessons carried forward: Before converting boundary tests, prove retained CLI smoke exists for each entrypoint; direct main() calls should use pytest-scoped monkeypatch/capsys only.
- Metrics: Runtime profile local-linux-x86_64-36cpu; run-quality latest 38.1s / median 65.7s before this slice.

### Slice 2: HITL report subprocess fanout

- Objective: Reduce repeated render_report.py subprocess calls while retaining real CLI proof.
- Why this approach: The report-mode test file launched render_report.py for ordinary report behavior 14 times; most assertions can use the import-safe main() seam.
- Commits:
- What changed: Converted report behavior tests to run_render_report(monkeypatch, capsys, ...); kept stdout indent and argparse required-argument tests as real subprocess smokes.
- Alternatives rejected: Did not remove the last four run_script calls because they prove delivery-boundary stdout formatting, argparse behavior, and handled-error process exit behavior.
- Targeted verification: ruff passed; focused pytest: 12 passed in 2.64s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 14 to 4.
- Test duplication pressure: No tests added; existing tests switched execution layer. File-level boundary count unchanged by design because retained CLI smokes remain in the same file.
- Critique: charness-artifacts/critique/2026-06-26-hitl-report-runtime.md; fresh-eye reviewer 019f0163-21e9-7c40-9fff-21702c8405cf found one Medium handled-error CLI proof issue, fixed before commit.
- Off-goal findings: Potential future inventory improvement: count within-file subprocess call reductions separately from file-level candidates.
- Lessons carried forward: File-level ratchets can hide meaningful runtime wins inside a retained-boundary test file; record direct call-count evidence.
- Metrics: render_report.py run_script calls in test_hitl_report_mode.py: base 14, current 4.

### Slice 3: Premature release timing repair

- Objective: Record and correct the workflow miss where release ran before the three-hour timebox was complete.
- Why this approach: The user correctly pointed out that the goal's push/release phase belonged at the end, not immediately after the first broad gate.
- Commits:
- What changed: Persisted charness-artifacts/retro/2026-06-26-premature-release-timing.md and refreshed recent retro lessons; stopped further release/push actions and returned to local-only quality work.
- Alternatives rejected: Did not revert the already-pushed v0.56.1 release because release/tag publication had already crossed the external boundary; instead recorded the state and continued local slices.
- Targeted verification: validate_retro_artifact passed for the new retro; git state inspected: v0.56.1 tag/release commit pushed, local verification commit remains ahead of origin.
- Test duplication pressure: No tests changed.
- Critique: Retro-triggered correction per operating contract; no separate code critique needed for this artifact-only workflow repair.
- Off-goal findings: none
- Lessons carried forward: Before push/release in a timeboxed goal, inspect Timebox, Activation time, Closeout reserve, and Done-early policy; if reserve has not started, continue safe local work.
- Metrics: Release was interrupted after publication; no further external actions allowed until final closeout.

### Slice 4: Record metric window subprocess fanout

- Objective: Reduce one duplicate record_metric_window.py subprocess success test while preserving real CLI proof.
- Why this approach: The file still had two success-path subprocess tests; one can call main() in-process while leaving success and argparse boundary smokes.
- Commits:
- What changed: Converted the Claude-session success case to run_record_metric_window(monkeypatch, capsys, ...); added quality and critique artifacts.
- Alternatives rejected: Did not convert the remaining success/error subprocess cases because they prove real CLI success and argparse session-source behavior.
- Targeted verification: ruff passed; focused pytest: 13 passed in 2.70s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 4 to 3.
- Test duplication pressure: No tests added; one existing test switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-record-metric-window-runtime.md; fresh-eye reviewer 019f016f-56de-78c2-8250-88c7d1c006c1 found no issues.
- Off-goal findings: none
- Lessons carried forward: Prefer tiny conversions when a file mixes duplicate behavior assertions with unique CLI/argparse proof.
- Metrics: record_metric_window.py run_script calls in test_record_metric_window.py: base 4, current 3.

### Slice 5: Retro host log probe subprocess fanout

- Objective: Reduce repeated probe_host_logs.py subprocess calls while preserving representative real CLI proof.
- Why this approach: The host-log probe tests paid subprocess startup for payload/behavior assertions even though probe_host_logs.py exposes an import-safe main() seam.
- Commits:
- What changed: Added run_probe_host_logs(monkeypatch, capsys, ...) and converted six invalid/empty/payload behavior tests to in-process main() calls.
- Alternatives rejected: Did not convert the remaining subprocess tests because they prove real script bootstrap and important option families: --home, --repo-root/--goal-path, and --claude-session-file.
- Targeted verification: ruff passed; focused pytest: 17 passed in 2.65s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 9 to 3.
- Test duplication pressure: No tests added; six existing tests switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-retro-host-log-probe-runtime.md; fresh-eye reviewer 019f0173-450d-7fc0-bc2e-9cdc55de4774 found no issues.
- Off-goal findings: Startup-probe timeout tests remain a risky conversion candidate because real subprocess timeout semantics are the behavior under test.
- Lessons carried forward: Keep one real subprocess path for each important option family before converting repeated payload assertions to in-process main() calls.
- Metrics: probe_host_logs.py run_script calls in test_retro_host_log_probe.py: base 9, current 3.

### Slice 6: Goal checker subprocess fanout

- Objective: Reduce repeated check_goal_artifact.py subprocess calls in goal-head-freshness tests while preserving representative closeout-gate CLI proof.
- Why this approach: Three complete-evidence issue-string tests asserted internal JSON/message behavior through subprocesses even though check_goal_artifact.py exposes main().
- Commits:
- What changed: Added run_check_goal_artifact(monkeypatch, capsys, ...) and converted missing-evidence, invalid-skip, and unbound-evidence checks to in-process main() calls.
- Alternatives rejected: Did not convert default checker failure, pursue-ready, or missing-path usage tests because they prove distinct real CLI return-code surfaces.
- Targeted verification: ruff passed; focused pytest: 15 passed in 2.76s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 7 to 4.
- Test duplication pressure: No tests added; three existing tests switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-goal-head-freshness-runtime.md; fresh-eye reviewer 019f0176-baa4-7553-b5bb-8900cc793d74 found no blocking issue and noted complete-state subprocess coverage remains repo-level rather than file-local.
- Off-goal findings: none
- Lessons carried forward: For closeout gates, record whether retained proof is file-local or repo-level before converting any subprocess-backed complete-state behavior.
- Metrics: check_goal_artifact.py run_script calls in test_goal_head_freshness.py: base 7, current 4.

### Slice 7: Doc links validator subprocess fanout

- Objective: Reduce repeated check_doc_links.py subprocess calls while preserving representative validator CLI proof.
- Why this approach: The doc-link tests launched the validator 18 times for individual rule fixtures even though the validator exposes main().
- Commits:
- What changed: Added run_check_doc_links(monkeypatch, capsys, ...) with the same ValidationError-to-stderr wrapper as the script entrypoint, then converted fifteen rule fixtures to in-process main() calls.
- Alternatives rejected: Kept three subprocess calls for script bootstrap plus representative failure, normal success, and explicit --require-git-file-listing behavior.
- Targeted verification: ruff passed; focused pytest: 18 passed in 2.94s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 18 to 3.
- Test duplication pressure: No tests added; fifteen existing tests switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-doc-links-runtime.md; fresh-eye reviewer 019f017a-9b2e-74b0-8f58-7603a89697c2 found no blocking issue, and its --require-git-file-listing caveat was fixed before commit.
- Off-goal findings: none
- Lessons carried forward: For validators with `main()` plus a thin `__main__` wrapper, in-process tests must reproduce the wrapper's exception-to-exit-code behavior when checking failure paths.
- Metrics: check_doc_links.py run_script calls in test_check_doc_links.py: base 18, current 3.

### Slice 8: CLI skill surface validator subprocess fanout

- Objective: Reduce repeated check_cli_skill_surface.py subprocess calls while preserving real probe-execution proof.
- Why this approach: Six static adapter-rule tests asserted JSON payload behavior through subprocesses without needing external command execution.
- Commits:
- What changed: Added run_cli_skill_surface(monkeypatch, capsys, ...) and converted six static-rule tests to in-process main() calls.
- Alternatives rejected: Kept basic JSON invocation and both --run-probes tests as real subprocesses because they cover script bootstrap, external command execution, and timeout behavior.
- Targeted verification: ruff passed; focused pytest: 9 passed in 2.69s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 9 to 3.
- Test duplication pressure: No tests added; six existing tests switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-cli-skill-surface-runtime.md; fresh-eye reviewer 019f017d-a9c5-7f11-96a1-1d3e2f1ab86c found no blocking issue and confirmed retained subprocess proof for bootstrap, --run-probes success, and timeout behavior.
- Off-goal findings: none
- Lessons carried forward: Keep real subprocess tests for validator modes that execute external probes or depend on timeout semantics.
- Metrics: check_cli_skill_surface.py run_script calls in test_cli_skill_surface.py: base 9, current 3.

### Slice 9: Setup skill-routing subprocess fanout

- Objective: Reduce repeated render_skill_routing.py subprocess calls while preserving a real JSON CLI smoke.
- Why this approach: Two AGENTS-state payload tests asserted ordinary JSON behavior through subprocesses without using a distinct CLI mode.
- Commits:
- What changed: Added run_render_skill_routing(monkeypatch, capsys, ...) and converted mature-AGENTS and drifted-block payload tests to in-process main() calls.
- Alternatives rejected: Kept the default compact-mode subprocess test as the real script-bootstrap and JSON output smoke.
- Targeted verification: ruff passed; focused pytest: 3 passed in 2.43s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 3 to 1.
- Test duplication pressure: No tests added; two existing tests switched execution layer. File-level boundary count unchanged because retained CLI smoke remains.
- Critique: charness-artifacts/critique/2026-06-26-setup-routing-runtime.md; low-risk same-agent critique recorded because the slice is a two-call conversion with retained CLI proof.
- Off-goal findings: none
- Lessons carried forward: Small fanout reductions are worth doing when they follow an already-proven retained-CLI pattern and do not add new behavior.
- Metrics: render_skill_routing.py run_script calls in test_setup_render_skill_routing.py: base 3, current 1.

### Slice 10: Usage episodes seed subprocess fanout

- Objective: Reduce repeated seed_usage_episodes_adapter.py subprocess calls while preserving write/refusal CLI proof.
- Why this approach: Dry-run schema validation and force-overwrite behavior can call main() directly; initial write and overwrite refusal remain meaningful CLI boundaries.
- Commits:
- What changed: Added run_seed_usage_episodes(monkeypatch, capsys, ...) and converted dry-run and force-overwrite tests to in-process main() calls.
- Alternatives rejected: Kept initial write and overwrite refusal as real subprocess tests because they prove shipped adapter-writing behavior.
- Targeted verification: ruff passed; focused pytest: 6 passed in 2.56s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 5 to 3.
- Test duplication pressure: No tests added; two existing tests switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-usage-episodes-seed-runtime.md; low-risk same-agent critique recorded because the slice is a two-call conversion with retained write/refusal CLI proof.
- Off-goal findings: none
- Lessons carried forward: Seed scripts should retain subprocess proof for write/refusal behavior, but dry-run and force-path payload assertions can use main().
- Metrics: seed_usage_episodes_adapter.py run_script calls in test_setup_seed_usage_episodes.py: base 5, current 3.

### Slice 11: Dependency seed subprocess fanout

- Objective: Reduce repeated seed_dependencies.py subprocess calls while preserving write/refusal/error CLI proof.
- Why this approach: Recommendation seeding and force-overwrite payload checks can call main() directly; initial write, overwrite refusal, and mutually-exclusive input remain useful CLI boundaries.
- Commits:
- What changed: Added run_seed_dependencies(monkeypatch, capsys, ...) with SystemExit handling and converted recommendation and force-overwrite behavior to in-process main() calls.
- Alternatives rejected: Kept explicit write, refusal without --force, and explicit-plus-recommendation rejection as real subprocess tests.
- Targeted verification: ruff passed; focused pytest: 5 passed in 3.04s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 7 to 5.
- Test duplication pressure: No tests added; two behavior checks switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-dependencies-seed-runtime.md; low-risk same-agent critique recorded because write/refusal/error CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: For seed-script tests, distinguish setup subprocess calls from the behavior under assertion before claiming a large runtime win.
- Metrics: seed_dependencies.py run_script calls in test_setup_seed_dependencies.py: base 7, current 5.

### Slice 12: Skill ownership scanner subprocess fanout

- Objective: Reduce repeated check_skill_ownership_overlap.py subprocess calls while preserving current-repo CLI proof.
- Why this approach: Synthetic scanner fixtures can call main() directly; the real current-repo allowlist smoke remains a useful script-bootstrap boundary.
- Commits:
- What changed: Added run_ownership_overlap(monkeypatch, capsys, ...) and converted three synthetic scanner fixtures to in-process main() calls.
- Alternatives rejected: Kept the current-repo seeded-allowlist test as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 4 passed in 2.45s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 4 to 1.
- Test duplication pressure: No tests added; three synthetic tests switched execution layer. File-level boundary count unchanged because retained CLI smoke remains.
- Critique: charness-artifacts/critique/2026-06-26-skill-ownership-runtime.md; low-risk same-agent critique recorded because the slice is a scanner-fixture conversion with retained current-repo CLI proof.
- Off-goal findings: none
- Lessons carried forward: Keep one real current-repo subprocess smoke when converting synthetic scanner fixtures.
- Metrics: check_skill_ownership_overlap.py run_script calls in test_skill_ownership_overlap.py: base 4, current 1.

### Slice 13: Repo-copy invariant subprocess fanout

- Objective: Reduce repeated check_test_repo_copy_invariants.py subprocess calls while preserving current-repo CLI proof.
- Why this approach: Synthetic drift fixtures can call main() directly; the real current-repo invariant smoke remains a useful script-bootstrap boundary.
- Commits:
- What changed: Added run_repo_copy_invariants(monkeypatch, capsys, ...) and converted four synthetic drift fixtures to in-process main() calls.
- Alternatives rejected: Kept the current-repo invariant test as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 11 passed in 3.61s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 5 to 1.
- Test duplication pressure: No tests added; four synthetic tests switched execution layer. File-level boundary count unchanged because retained CLI smoke remains.
- Critique: charness-artifacts/critique/2026-06-26-repo-copy-invariant-runtime.md; low-risk same-agent critique recorded because the slice is a synthetic-fixture conversion with retained current-repo CLI proof.
- Off-goal findings: none
- Lessons carried forward: Repo-copy guards protect expensive tests; retain a current-repo entrypoint smoke even when synthetic fixtures move in-process.
- Metrics: check_test_repo_copy_invariants.py run_script calls in test_repo_copy_invariants.py: base 5, current 1.

### Slice 14: Public doc coupling subprocess fanout

- Objective: Reduce repeated check_public_doc_coupling.py subprocess calls while preserving human-output CLI proof.
- Why this approach: JSON advisory fixtures can call main() directly; text-output checks are the delivery surface shown in quality logs.
- Commits:
- What changed: Added run_public_doc_coupling(monkeypatch, capsys, ...) and converted three JSON fixture tests to in-process main() calls.
- Alternatives rejected: Kept clean text and advisory text tests as real subprocess smokes.
- Targeted verification: ruff passed; focused pytest: 8 passed in 2.80s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 5 to 2.
- Test duplication pressure: No tests added; three JSON tests switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-public-doc-coupling-runtime.md; low-risk same-agent critique recorded because human-output CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: Advisory gates should retain human-output subprocess smokes when JSON fixtures move in-process.
- Metrics: check_public_doc_coupling.py run_script calls in test_check_public_doc_coupling.py: base 5, current 2.

### Slice 15: Ubiquitous language subprocess fanout

- Objective: Reduce repeated inventory_ubiquitous_language.py subprocess calls while preserving first-run and current-repo CLI proof.
- Why this approach: Contract-backed synthetic fixtures can call main() directly; unconfigured and current-repo checks are useful entrypoint smokes.
- Commits:
- What changed: Added run_ubiquitous_language(monkeypatch, capsys, ...) and converted three synthetic scanner fixtures to in-process main() calls.
- Alternatives rejected: Kept unconfigured adapter and current-repo contract tests as real subprocess smokes.
- Targeted verification: ruff passed; focused pytest: 5 passed in 3.11s; boundary-bypass ratchet OK with 77 candidates / 40 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 5 to 2.
- Test duplication pressure: No tests added; three synthetic tests switched execution layer. File-level boundary count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-ubiquitous-language-runtime.md; low-risk same-agent critique recorded because first-run/current-repo CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: Terminology scanners should retain first-run and current-repo subprocess smokes while synthetic contract fixtures can run in-process.
- Metrics: inventory_ubiquitous_language.py run_script calls in test_quality_ubiquitous_language.py: base 5, current 2.

### Slice 16: Behavior recommendation subprocess fanout

- Objective: Reduce repeated recommend_behavior_test.py subprocess calls while preserving argparse-error CLI proof.
- Why this approach: JSON and markdown success paths only need argparse/stdout semantics; the missing-report error case is the user-facing CLI boundary.
- Commits:
- What changed: Added run_recommend_behavior_test(monkeypatch, capsys, ...) and converted two success-path tests to in-process main() calls.
- Alternatives rejected: Kept the --state executed missing-report test as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 3 passed in 2.40s; boundary-bypass ratchet OK with 76 candidates / 39 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; subprocess.run calls dropped 3 to 1.
- Test duplication pressure: No tests added; two success-format checks switched execution layer. Boundary ratchet effective candidates dropped by one.
- Critique: charness-artifacts/critique/2026-06-26-behavior-recommendation-runtime.md; low-risk same-agent critique recorded because argparse-error CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: For recommendation emitters, keep a real subprocess around argparse failure while moving pure formatting success checks in-process.
- Metrics: recommend_behavior_test.py subprocess.run calls in test_quality_behavior_recommendation.py: base 3, current 1.

### Slice 17: Markdown preview bootstrap subprocess fanout

- Objective: Reduce repeated bootstrap_markdown_preview.py subprocess-backed helper calls while preserving full execute CLI proof.
- Why this approach: Existing-config and not-applicable fixtures can call main() directly; scaffold-and-execute remains the command bootstrap plus fake-glow proof.
- Commits:
- What changed: Added run_quality_preview(monkeypatch, capsys, ...) and converted existing-config preservation plus not-applicable tests to in-process main() calls.
- Alternatives rejected: Kept the scaffold-and-execute test as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 3 passed in 3.01s; boundary-bypass ratchet OK with 75 candidates / 38 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; subprocess-backed helper calls dropped 3 to 1.
- Test duplication pressure: No tests added; two behavior checks switched execution layer. Boundary ratchet effective candidates dropped by one.
- Critique: charness-artifacts/critique/2026-06-26-markdown-preview-bootstrap-runtime.md; low-risk same-agent critique recorded because full execute CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: Bootstrap tests should retain one full command+backend subprocess and move pure classification/config variants in-process.
- Metrics: _run_quality_preview calls in test_quality_markdown_preview_bootstrap.py: base 3, current 1.

### Slice 18: Debug seam-risk index subprocess fanout

- Objective: Reduce repeated build_debug_seam_risk_index.py subprocess calls while preserving write-mode CLI proof.
- Why this approach: Stale-index rejection can call main() directly if the helper mirrors the script's ValidationError wrapper; write mode remains command/file-output proof.
- Commits:
- What changed: Added run_debug_seam_risk_index(monkeypatch, capsys, ...) and converted the stale-index check to an in-process main() call.
- Alternatives rejected: Kept write + JSON output + index file creation as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 2 passed in 2.48s; boundary-bypass ratchet OK with 74 candidates / 37 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 2 to 1.
- Test duplication pressure: No tests added; one error-path check switched execution layer. Boundary ratchet effective candidates dropped by one.
- Critique: charness-artifacts/critique/2026-06-26-debug-seam-index-runtime.md; low-risk same-agent critique recorded because write-mode CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: In-process conversions for scripts with __main__ exception wrappers must mirror the wrapper, not only call main().
- Metrics: run_script calls in test_debug_seam_risk_index.py: base 2, current 1.

### Slice 19: Issue 57 renderer subprocess fanout

- Objective: Reduce repeated render_issue_57_design_study.py subprocess calls while preserving write-mode CLI proof.
- Why this approach: Default markdown/no-write rendering can call main() directly; write + JSON + artifact creation remains the command boundary.
- Commits:
- What changed: Added run_issue_57_design_study(monkeypatch, capsys, ...) and converted the default markdown/no-write test to an in-process main() call.
- Alternatives rejected: Kept write + JSON output + markdown artifact creation as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 2 passed in 2.42s; boundary-bypass ratchet OK with 73 candidates / 36 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 2 to 1.
- Test duplication pressure: No tests added; one output-only check switched execution layer. Boundary ratchet effective candidates dropped by one.
- Critique: charness-artifacts/critique/2026-06-26-issue-57-renderer-runtime.md; low-risk same-agent critique recorded because write-mode CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: Renderer tests should retain file-writing subprocess proof and move pure stdout rendering checks in-process.
- Metrics: run_script calls in test_issue_57_design_study.py: base 2, current 1.

### Slice 20: Narrative scenario subprocess fanout

- Objective: Reduce duplicate narrative adapter subprocess calls while preserving volatile-review and init-write CLI proof.
- Why this approach: Simple resolve/missing-adapter JSON checks can call main() directly; volatile review and init adapter remain command/write boundaries.
- Commits:
- What changed: Added run_narrative_resolve_adapter(...) and run_narrative_review_adapter(...), then converted two simple JSON checks to in-process main() calls.
- Alternatives rejected: Kept volatile missing-path review and init adapter file creation as real subprocess smokes.
- Targeted verification: ruff passed; focused pytest: 6 passed in 2.51s; boundary-bypass ratchet OK with 73 candidates / 36 clean-convertible / 33 internally-spawning / 23 likely keep-boundary and candidate keys reduced 130 to 128; run_script calls dropped 4 to 2.
- Test duplication pressure: No tests added; two JSON checks switched execution layer. File-level candidate count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-narrative-scenario-runtime.md; low-risk same-agent critique recorded because volatile-review/init-write CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: Adapter scenario tests should keep command/write proof for init and one complex review while moving simple JSON paths in-process.
- Metrics: run_script calls in test_narrative_scenario_blocks.py: base 4, current 2.

### Slice 21: Bootstrap visibility subprocess fanout

- Objective: Reduce duplicate resolve-adapter subprocess calls while preserving narrative fallback CLI proof.
- Why this approach: Find-skills and announcement checks assert JSON payload content only; narrative fallback remains the command smoke for richer-doc discovery.
- Commits:
- What changed: Added run_resolve_adapter(monkeypatch, capsys, ...) and converted find-skills plus announcement resolve-adapter checks to in-process main() calls.
- Alternatives rejected: Kept narrative rich-doc fallback as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 3 passed in 2.40s; boundary-bypass ratchet OK with 73 candidates / 36 clean-convertible / 33 internally-spawning / 23 likely keep-boundary and candidate keys reduced 128 to 126; run_script calls dropped 3 to 1.
- Test duplication pressure: No tests added; two JSON checks switched execution layer. File-level candidate count unchanged because retained CLI smoke remains.
- Critique: charness-artifacts/critique/2026-06-26-bootstrap-visibility-runtime.md; low-risk same-agent critique recorded because narrative fallback CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: Hyphenated skill directories need path-based module loading when converting tests in-process.
- Metrics: run_script calls in test_bootstrap_visibility.py: base 3, current 1.

### Slice 22: Current-pointer scanner subprocess fanout

- Objective: Reduce repeated check_current_pointer_writes.py subprocess calls while preserving scanner output and HITL sync CLI proof.
- Why this approach: Synthetic scanner variants share the same command mode and can call SCANNER.main(); text/JSON scanner smokes and HITL bootstrap/sync remain real subprocesses.
- Commits:
- What changed: Added run_current_pointer_scanner(monkeypatch, capsys, ...) and converted seven synthetic scanner fixtures to in-process main() calls.
- Alternatives rejected: Kept HITL bootstrap/sync plus text-output and JSON-output scanner tests as real subprocess smokes.
- Targeted verification: ruff passed; focused pytest: 20 passed in 2.89s; boundary-bypass ratchet OK with 73 candidates / 36 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; run_script calls dropped 11 to 4.
- Test duplication pressure: No tests added; seven scanner checks switched execution layer. File-level candidate count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-current-pointer-scanner-runtime.md; same-agent deterministic critique recorded because text/JSON scanner and HITL subprocess proof remains.
- Off-goal findings: none
- Lessons carried forward: Scanner suites can move repeated synthetic cases in-process when at least one text and one JSON CLI smoke remain.
- Metrics: run_script calls in test_current_pointer_writes.py: base 11, current 4.

### Slice 23: Usage episode validator subprocess fanout

- Objective: Reduce repeated validate_usage_episodes.py subprocess calls while preserving slice-closeout command proof.
- Why this approach: Post-closeout validator checks can call main() directly; run_slice_closeout.py remains the behavior boundary for emission, suppression, and rotation.
- Commits:
- What changed: Added run_validate_usage_episodes(monkeypatch, capsys, ...) and converted three validator checks to in-process main() calls.
- Alternatives rejected: Kept _run_closeout(...) as a real subprocess for every closeout scenario.
- Targeted verification: ruff passed; focused pytest: 6 passed in 3.96s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary and candidate keys reduced 126 to 125; run_script calls dropped 4 to 1.
- Test duplication pressure: No tests added; three validator checks switched execution layer. Boundary ratchet clean-convertible count dropped by one.
- Critique: charness-artifacts/critique/2026-06-26-usage-episode-validator-runtime.md; low-risk same-agent critique recorded because slice-closeout subprocess proof remains.
- Off-goal findings: none
- Lessons carried forward: Closeout tests should keep the closeout command boundary and move secondary validators in-process.
- Metrics: run_script calls in test_slice_closeout_usage_episode.py: base 4, current 1.

### Slice 24: Tool recommendation subprocess fanout

- Objective: Reduce repeated quality list_tool_recommendations.py subprocess calls while preserving recommendation CLI proof.
- Why this approach: Quality recommendation fixtures share the same script and isolated PATH semantics; narrative recommendation remains a real command smoke.
- Commits:
- What changed: Added _run_quality_recommendations(monkeypatch, capsys, ...) and converted three quality recommendation fixtures to in-process main() calls.
- Alternatives rejected: Kept the narrative recommendation fixture as a real subprocess smoke.
- Targeted verification: ruff passed; focused pytest: 4 passed in 2.61s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; subprocess-backed helper calls dropped 4 to 1.
- Test duplication pressure: No tests added; three recommendation checks switched execution layer. File-level candidate count unchanged because retained CLI smoke remains.
- Critique: charness-artifacts/critique/2026-06-26-tool-recommendation-runtime.md; low-risk same-agent critique recorded because narrative recommendation CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: In-process recommendation tests must preserve isolated PATH semantics with monkeypatch.
- Metrics: _run_recommendations calls in test_quality_tool_recommendations.py: base 4, current 1.

### Slice 25: Markdown preview support subprocess fanout

- Objective: Reduce repeated render_markdown_preview.py subprocess calls while preserving full-render and backend checker CLI proof.
- Why this approach: Degraded/backend-error preview variants can call main() directly while still running fake glow through the renderer; full render and backend checker remain command boundaries.
- Commits:
- What changed: Added run_helper_in_process(monkeypatch, capsys, ...) and converted four preview variant tests to in-process main() calls.
- Alternatives rejected: Kept full render, default/disabled, unsupported backend, and check_glow_backend.py subprocess tests as real command smokes.
- Targeted verification: ruff passed; focused pytest: 11 passed in 3.87s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; subprocess-backed run_helper calls dropped 7 to 3.
- Test duplication pressure: No tests added; four preview variants switched execution layer. File-level candidate count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-markdown-preview-support-runtime.md; low-risk same-agent critique recorded because full-render/backend subprocess proof remains.
- Off-goal findings: none
- Lessons carried forward: In-process preview tests must preserve PATH and timeout environment while still letting backend subprocess proof run.
- Metrics: run_helper calls in test_markdown_preview_support.py: base 7, current 3.

### Slice 26: Quality bootstrap resolve subprocess fanout

- Objective: Reduce repeated quality resolve_adapter.py subprocess calls while preserving bootstrap/init write proof and one direct resolve CLI smoke.
- Why this approach: Follow-up resolve checks after bootstrap/init are read-only; bootstrap/init remain the write boundary and invalid-field resolve remains the command smoke.
- Commits:
- What changed: Added _run_quality_resolve_adapter(...) and converted five follow-up resolve checks to in-process main() calls.
- Alternatives rejected: Kept bootstrap_adapter.py, init_adapter.py, and the direct invalid review-fields resolve test as real subprocesses.
- Targeted verification: ruff passed; focused pytest: 17 passed in 3.47s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; resolve_adapter subprocess calls dropped 6 to 1.
- Test duplication pressure: No tests added; five read-only resolve checks switched execution layer. File-level candidate count unchanged because write-boundary subprocesses remain.
- Critique: charness-artifacts/critique/2026-06-26-quality-bootstrap-resolve-runtime.md; low-risk same-agent critique recorded because bootstrap/init and direct resolve CLI proof remain.
- Off-goal findings: none
- Lessons carried forward: Bootstrap suites should keep write commands as subprocesses and move only read-only follow-up probes in-process.
- Metrics: quality resolve_adapter subprocess calls in test_quality_bootstrap.py: base 6, current 1.

### Slice 27: Markdown preview backend-check subprocess fanout

- Objective: Reduce repeated check_glow_backend.py subprocess launches while preserving markdown-preview command proof.
- Why this approach: The backend checker main() is a thin status-to-exit-code wrapper; full markdown-preview render CLI proof remains in the same file.
- Commits:
- What changed: Converted healthy, blank-output, and timeout backend checker cases to in-process main() calls using pytest monkeypatch for PATH and timeout environment.
- Alternatives rejected: Kept broader markdown-preview command smokes and backend renderer subprocess behavior.
- Targeted verification: ruff passed; focused pytest with durations: 11 passed in 3.66s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; backend-check subprocess launches dropped 3 to 0; test call duration dropped 0.40s to 0.23s in local samples.
- Test duplication pressure: No tests added; one three-case exit-code test switched execution layer. File-level candidate count unchanged because retained CLI smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-markdown-preview-backend-check-runtime.md; low-risk same-agent critique recorded because broader markdown-preview CLI proof remains.
- Off-goal findings: none
- Lessons carried forward: Thin wrapper exit-code tests can run in-process when a neighboring full CLI smoke remains.
- Metrics: check_glow_backend.py subprocess launches in test_markdown_preview_support.py: base 3, current 0.

### Slice 28: Artifact path payload subprocess fanout

- Objective: Reduce repeated resolve_artifact_path.py command launches in artifact path calculation tests without weakening package-level command proof.
- Why this approach: The script now has a reusable payload_for() function that main() delegates to, so pure payload assertions can call the same implementation in-process.
- Commits:
- What changed: Extracted payload construction from resolve_artifact_path.py and converted record-current, handoff-current, and symlinked-current tests to direct payload_for() calls with explicit adapter payloads.
- Alternatives rejected: Kept exported resolver, invalid artifact class, and refresh-current-pointer subprocess tests as command/package boundary proof.
- Targeted verification: ruff passed; focused artifact-naming pytest passed 18 tests in 4.19s; converted three-test sample passed with all call durations below 0.005s after previously showing 0.08s-0.10s calls; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; three duplicated command launches converted to the shared payload implementation. Ratchet counts unchanged because retained command smokes remain.
- Critique: charness-artifacts/critique/2026-06-26-artifact-path-payload-runtime.md; low-risk same-agent critique recorded because exported/package command proof remains.
- Off-goal findings: none
- Lessons carried forward: Extract script payload builders when tests need repeated pure assertions, but keep package/export command proof at the actual boundary.
- Metrics: direct resolve_artifact_path.py launches in converted artifact-naming tests: base 3, current 0.

### Slice 29: Quality closeout contract validator subprocess fanout

- Objective: Remove an unnecessary validate_quality_closeout_contract.py subprocess from docs-and-misc policy tests.
- Why this approach: The test is asserting validator behavior, and the validator is already exposed as validate_quality_closeout_contract().
- Commits:
- What changed: Imported validate_quality_closeout_contract() directly in test_docs_and_misc.py and replaced the run_script call with the direct validator call.
- Alternatives rejected: Left release, narrative, bump-version, and packaging subprocess tests unchanged because those are closer to command/package boundary proof.
- Targeted verification: ruff passed; focused docs-and-misc pytest passed 30 tests in 3.08s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary and candidate keys reduced from 125 to 124.
- Test duplication pressure: No tests added; one duplicated command launch converted to direct validator behavior.
- Critique: charness-artifacts/critique/2026-06-26-quality-closeout-contract-runtime.md; low-risk same-agent critique recorded because this is a direct validator call and command-heavy release tests remain untouched.
- Off-goal findings: none
- Lessons carried forward: In mixed documentation suites, convert only the pure validator checks and leave release/package subprocess proof at the boundary.
- Metrics: validate_quality_closeout_contract.py launches in test_docs_and_misc.py: base 1, current 0.

### Slice 30: Skill ergonomics gate subprocess fanout

- Objective: Reduce repeated validate_skill_ergonomics.py process launches while keeping command-wrapper proof.
- Why this approach: The validator already exposes evaluate(), has_failures(), and _format_human(); repeated rule-behavior assertions can call those APIs directly.
- Commits:
- What changed: Loaded the skill ergonomics validator module once in test_skill_ergonomics_gate.py and converted most JSON/plain subprocess assertions to direct evaluate/formatter calls.
- Alternatives rejected: Kept one skill-helper CLI success smoke and two root wrapper failure smokes instead of removing all command-boundary proof.
- Targeted verification: ruff passed; focused skill-ergonomics pytest passed 17 tests in 2.68s after a 4.04s pre-change sample; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; repeated validator subprocess calls dropped from 23 to 3 while retaining command smokes.
- Critique: charness-artifacts/critique/2026-06-26-skill-ergonomics-gate-runtime.md; low-risk same-agent critique recorded because command-wrapper proof remains.
- Off-goal findings: none
- Lessons carried forward: For validator suites with many rule permutations, keep a small command smoke set and run the rule matrix against the import-safe evaluator.
- Metrics: validate_skill_ergonomics subprocess launches in test_skill_ergonomics_gate.py: base 23, current 3.

### Slice 31: Goal pursue-ready subprocess fanout

- Objective: Reduce repeated check_goal_artifact.py subprocess launches in pursue-ready return-code tests while preserving CLI smokes.
- Why this approach: test_goal_head_freshness.py already has run_check_goal_artifact(), which sets argv, calls main(), captures stdout/stderr, and returns a subprocess-shaped result.
- Commits:
- What changed: Converted the ready and unshaped pursue-ready checks to run_check_goal_artifact().
- Alternatives rejected: Kept head-freshness failure and missing-path subprocess tests as command-boundary proof.
- Targeted verification: ruff passed; focused goal-head-freshness pytest passed 15 tests in 2.62s; pursue-ready test duration dropped from 0.16s to 0.01s in local samples; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; check_goal_artifact.py subprocess launches in the file dropped from 4 to 2.
- Critique: charness-artifacts/critique/2026-06-26-goal-pursue-ready-runtime.md; low-risk same-agent critique recorded because CLI smokes remain.
- Off-goal findings: none
- Lessons carried forward: Reuse existing main() harnesses for return-code branch matrices, but keep at least one real CLI error/smoke path.
- Metrics: check_goal_artifact.py subprocess launches in test_goal_head_freshness.py: base 4, current 2.

### Slice 32: Create-skill adapter resolver subprocess fanout

- Objective: Reduce repeated create-skill resolve_adapter.py process launches while preserving resolver and init command proof.
- Why this approach: The resolver exposes load_adapter(), so the adapter-shape matrix can call the real resolver directly against temp files.
- Commits:
- What changed: Loaded the create-skill resolver once in test_create_skill_adapter.py and converted nine resolver matrix tests to direct load_adapter() calls.
- Alternatives rejected: Kept one resolver CLI smoke and the init_adapter write command test.
- Targeted verification: ruff passed; focused create-skill adapter pytest passed 11 tests in 2.46s after a 3.05s pre-change sample; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; create-skill resolver subprocess calls dropped from 10 to 1 while init command proof remains.
- Critique: charness-artifacts/critique/2026-06-26-create-skill-adapter-runtime.md; low-risk same-agent critique recorded because command/write proof remains.
- Off-goal findings: none
- Lessons carried forward: Adapter resolver matrices should usually test the resolver API directly and reserve subprocesses for one wrapper smoke plus write commands.
- Metrics: create-skill resolve_adapter.py launches in test_create_skill_adapter.py: base 10, current 1.

### Slice 33: Profile and preset validator subprocess fanout

- Objective: Remove simple profile/preset validator subprocesses while leaving adapter boundary tests intact.
- Why this approach: validate_profile() and validate_preset() expose the exact validator behavior needed for the first three error cases.
- Commits:
- What changed: Converted missing-skill, organization-scope, and product-slice exposure tests to direct validator function calls and direct ValidationError message assertions.
- Alternatives rejected: Left gitignored-file and adapter validation subprocesses unchanged because they prove command/gitignored/boundary behavior and dominate runtime.
- Targeted verification: ruff passed; focused profile/preset pytest passed 18 tests in 5.29s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; three pure validator subprocess calls removed.
- Critique: charness-artifacts/critique/2026-06-26-profile-preset-validator-runtime.md; low-risk same-agent critique recorded because command-heavy checks remain.
- Off-goal findings: adapter validation remains the dominant runtime in this file.
- Lessons carried forward: In mixed validator files, trim direct validator checks first and leave git/adapter command behavior for a separate proof plan.
- Metrics: pure profile/preset validator subprocess launches in test_profile_and_preset_validation.py: base 3, current 0.

### Slice 34: Standing-doc provenance subprocess fanout

- Objective: Reduce repeated check_standing_doc_provenance.py process launches while preserving CLI and adapter-error proof.
- Why this approach: The checker exposes run() and _render_plain(), so behavior-matrix tests can call the same implementation in-process.
- Commits:
- What changed: Loaded the standing-doc provenance checker once in test_standing_doc_provenance.py and converted most JSON/plain checks to direct run()/formatter calls.
- Alternatives rejected: Kept one JSON CLI smoke and the invalid-adapter CLI failure case.
- Targeted verification: ruff passed; focused standing-doc provenance pytest passed 10 tests in 2.61s after a 3.23s pre-change sample; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; standing-doc provenance subprocess calls dropped from 11 to 2.
- Critique: charness-artifacts/critique/2026-06-26-standing-doc-provenance-runtime.md; low-risk same-agent critique recorded because CLI smokes remain.
- Off-goal findings: none
- Lessons carried forward: For checker behavior matrices, keep one command smoke and run the rest through the exported run() API.
- Metrics: check_standing_doc_provenance.py launches in test_standing_doc_provenance.py: base 11, current 2.

### Slice 35: Surface validation subprocess fanout

- Objective: Reduce selected validate_surfaces.py process launches without weakening surface command-routing tests.
- Why this approach: surfaces_lib.load_surfaces() is the actual manifest validator, so pure recursive-glob validation cases can call it directly.
- Commits:
- What changed: Converted three recursive-glob manifest validation tests to direct load_surfaces()/SurfaceError assertions.
- Alternatives rejected: Kept duplicate-id and bare-recursive validate_surfaces command smokes, and left check_changed_surfaces/select_verifiers routing tests at the CLI boundary.
- Targeted verification: ruff passed; focused surface-obligation pytest passed 25 tests in 4.04s after a 4.21s pre-change sample; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; three pure manifest-validation subprocess calls removed.
- Critique: charness-artifacts/critique/2026-06-26-surface-validation-runtime.md; low-risk same-agent critique recorded because command-routing tests remain.
- Off-goal findings: none
- Lessons carried forward: In surface-routing suites, only lower pure manifest-validation cases; keep command routing at the boundary.
- Metrics: selected validate_surfaces.py launches in test_surface_obligations.py: base 5, current 2.

### Slice 36: Boundary inventory repeated-probe cache

- Objective: Reduce repeated file probes inside the boundary-bypass inventory script used by the ratchet gate.
- Why this approach: The inventory scans many test files that point at the same import-safe scripts, so per-scan path-result caches avoid re-reading the same targets for import-safety, internal-boundary, and sibling-lib checks.
- Commits:
- What changed: Added local caches to find_boundary_bypass_candidates() and threaded them through analyze_test_file().
- Alternatives rejected: Did not broaden optimization further because wall-clock timing stayed in the same 0.64s-0.68s band and AST scanning needs profiling before more complexity.
- Targeted verification: ruff passed; boundary-bypass ratchet JSON output unchanged with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; five-run timing remained effectively flat; plugin mirror synced and drift check passed.
- Test duplication pressure: Not a test conversion; this improves the script path used by pre-commit and quality gates.
- Critique: charness-artifacts/critique/2026-06-26-boundary-inventory-cache.md; low-risk same-agent critique recorded because output is unchanged and generated surfaces are synced.
- Off-goal findings: timing did not materially improve; further ratchet speed work needs profiling.
- Lessons carried forward: Prefer honest structural caching only when output is unchanged, and do not claim speed wins from noise-band timing.
- Metrics: repeated import-safe/internal/lib probes now cache per target path during one inventory scan.

### Slice 37: Public skill dogfood registry subprocess fanout

- Objective: Remove subprocess startup from the current real public-skill dogfood registry validation test.
- Why this approach: tests/test_public_skill_dogfood.py already imports load_registry() and validate_registry(), so the checked-in registry can be validated directly.
- Commits:
- What changed: Replaced the validate_public_skill_dogfood.py subprocess in the current-real-registry test with validate_registry(load_registry(ROOT), ROOT).
- Alternatives rejected: Did not add a separate command smoke because the command wrapper is thin and suggestion CLI tests remain subprocess-based.
- Targeted verification: ruff passed; focused public-skill dogfood/validation pytest passed 13 tests in 3.27s; current-real-registry call duration dropped from 0.81s to 0.69s; boundary-bypass ratchet OK with 73 candidates / 35 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; one full real-registry subprocess removed.
- Critique: charness-artifacts/critique/2026-06-26-public-skill-dogfood-runtime.md; low-risk same-agent critique recorded because the same validator API now runs directly.
- Off-goal findings: most remaining duration is registry validation itself, not command startup.
- Lessons carried forward: When the real checked-in data path is expensive, separate command-wrapper proof from data-validation proof instead of paying both every time.
- Metrics: validate_public_skill_dogfood.py launches in tests/test_public_skill_dogfood.py: base 1, current 0 for the real registry validation path.

### Slice 38: Setup skill-routing subprocess fanout

- Objective: Remove the last render_skill_routing.py subprocess in setup routing tests.
- Why this approach: test_setup_render_skill_routing.py already had a run_render_skill_routing() main() helper covering argv and stdout capture.
- Commits:
- What changed: Converted the default compact-mode rendering test to the existing helper and removed the now-unused run_script import.
- Alternatives rejected: Kept seed_retro_memory.py tests as subprocesses because they write adapter, summary, and gitignore files.
- Targeted verification: ruff passed; focused setup render/retro pytest passed 6 tests in 2.44s; boundary-bypass ratchet improved to 72 candidates / 34 clean-convertible / 33 internally-spawning / 23 likely keep-boundary.
- Test duplication pressure: No tests added; render_skill_routing.py subprocess launches in test_setup_render_skill_routing.py dropped to zero.
- Critique: charness-artifacts/critique/2026-06-26-setup-skill-routing-runtime.md; low-risk same-agent critique recorded because helper still exercises main().
- Off-goal findings: none
- Lessons carried forward: Finish partial main-helper migrations when all remaining cases share the same command wrapper.
- Metrics: render_skill_routing.py launches in test_setup_render_skill_routing.py: base 1, current 0.

### Slice 39: Debug scaffold subprocess fanout

- Objective: Reduce local debug scaffold command launches while preserving exported package proof.
- Why this approach: scaffold_debug_artifact.py exposes payload_for(), so local payload assertions can call the real builder directly.
- Commits:
- What changed: Imported the debug scaffold module and converted the source-tree local scaffold payload tests to payload_for().
- Alternatives rejected: Kept exported plugin scaffold command proof and validator command execution as subprocesses.
- Targeted verification: ruff passed; focused debug scaffold pytest passed 3 tests in 2.77s after a 2.83s pre-change sample; boundary-bypass ratchet improved to 72 candidates / 34 clean-convertible / 33 internally-spawning / 23 likely keep-boundary with candidate keys reduced to 122.
- Test duplication pressure: No tests added; two local scaffold subprocess launches removed.
- Critique: charness-artifacts/critique/2026-06-26-debug-scaffold-runtime.md; low-risk same-agent critique recorded because exported command proof remains.
- Off-goal findings: exported plugin proof dominates this small file's runtime.
- Lessons carried forward: Local scaffold payload shape can use payload_for(), while exported consumer-package tests should stay command-backed.
- Metrics: local scaffold_debug_artifact.py launches in tests/test_debug_scaffold.py: base 2, current 0.

### Slice 40: Public skill dogfood resolver subprocess speed

- Objective: Speed up public-skill dogfood matrix generation by avoiding per-skill resolver subprocesses.
- Why this approach: Almost all public skill resolve_adapter.py scripts expose load_adapter(), while the command wrapper delegates to that function; dogfood only needs the adapter payload's artifact/output path.
- Commits:
- What changed: public_skill_dogfood_lib._resolve_artifact() now loads resolver modules in-process and calls load_adapter() when available, with subprocess fallback for legacy resolvers; artifact path extraction moved to _artifact_path_from_payload().
- Alternatives rejected: Did not remove subprocess fallback for resolvers without load_adapter(); did not add broad exception masking around import failures without a concrete failure case.
- Targeted verification: ruff passed; focused public-skill dogfood/validation pytest passed 13 tests in 2.65s; current real registry call duration dropped from 0.69s to 0.09s; cProfile validation runtime dropped from about 0.80s to 0.11s; boundary-bypass ratchet OK with 72 candidates / 34 clean-convertible / 33 internally-spawning / 23 likely keep-boundary; plugin mirror synced and drift check passed.
- Test duplication pressure: Not a test conversion; this reduces actual validator script subprocess fanout.
- Critique: charness-artifacts/critique/2026-06-26-public-skill-dogfood-resolver-speed.md; low-risk same-agent critique recorded because focused proof, profiler evidence, and mirror proof passed.
- Off-goal findings: none
- Lessons carried forward: When a validator fans out into many repo-owned Python entrypoints, prefer import-safe functional APIs with a legacy subprocess fallback.
- Metrics: resolver subprocess calls from dogfood matrix generation: base 17 in current registry profile, current 1 fallback in profile.

### Slice 41: Proof artifact durability repair

- Objective: Fix the broad non-release pytest failure caused by a quality
  artifact citing a gitignored runtime metrics file without a same-line
  reproduction-source marker.
- Why this approach: The failure was in the proof record, not production code;
  moving the marker onto the cited path line satisfies the existing durability
  contract without weakening the validator.
- Commits:
- What changed: Repaired
  `charness-artifacts/quality/2026-06-26-public-skill-dogfood-resolver-speed-quality-review.md`
  and added this slice's quality/critique records.
- Alternatives rejected: Did not relax `check_spec_evidence_durability.py`;
  the validator caught a real proof-recording mistake.
- Targeted verification: focused durability pytest passed; full
  `check_spec_evidence_durability.py --repo-root .` passed across 224 docs; the
  repaired quality artifact validated.
- Test duplication pressure: No tests added; this is an artifact contract fix.
- Critique: charness-artifacts/critique/2026-06-26-proof-artifact-durability.md;
  low-risk same-agent critique recorded because no runtime code changed.
- Off-goal findings: none.
- Metrics: broad non-release pytest exposed the failure after 257.54s; focused
  durability proof now passes in 4.37s.

### Slice 42: Skill-surface preflight parallel checks

- Objective: Reduce the slowest broad non-release standing test by speeding the
  actual `check_skill_surface_preflight.py --run-checks` script path.
- Why this approach: The run-checks validators are independent read-only package
  gates; executing them concurrently preserves proof coverage while reducing the
  critical path.
- Commits:
- What changed: `_run_checks()` now uses `ThreadPoolExecutor` to run the same
  commands concurrently, then returns results in the original command-list order;
  plugin mirror regenerated.
- Alternatives rejected: Did not remove any validator from the one-shot
  preflight; did not make tests bypass the integration path.
- Targeted verification: ruff passed; focused preflight pytest passed 21 tests
  in 6.88s; focused integration tests passed; boundary-bypass ratchet passed;
  staged mirror drift passed.
- Test duplication pressure: No tests added; existing integration proof now runs
  faster.
- Critique: charness-artifacts/critique/2026-06-26-skill-surface-preflight-parallel.md;
  low-risk same-agent critique recorded because the validator set and output
  order are preserved.
- Off-goal findings: none.
- Metrics: slow integration test call dropped from 7.10s to 4.26s; full focused
  file dropped from 9.71s to 6.88s in local samples.

### Slice 43: Command-docs help probe parallelism

- Objective: Reduce the command-docs current-repo validator hot spot from broad
  non-release pytest.
- Why this approach: Each command-docs entry runs an independent help command
  and reads docs; collecting futures in contract order preserves output
  determinism while reducing the critical path.
- Commits:
- What changed: `check_command_docs.py` now runs `check_command()` calls through
  a `ThreadPoolExecutor`; plugin mirror regenerated.
- Alternatives rejected: Tested but reverted `render_cli_reference.py`
  parallelism because it did not improve direct wall time and made the focused
  render test slightly slower.
- Targeted verification: ruff passed; focused command-doc pytest passed 7 tests
  in 5.98s; direct `check_command_docs.py --repo-root .` passed in 0.344s;
  plugin sync ran.
- Test duplication pressure: No tests added; existing command-doc proof now runs
  faster.
- Critique: charness-artifacts/critique/2026-06-26-command-docs-parallel.md;
  low-risk same-agent critique recorded because command set and finding order
  are preserved.
- Off-goal findings: none.
- Metrics: current-repo command-docs test dropped from 3.37s to 0.35s; focused
  file dropped from 8.98s to 5.98s.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- User request on 2026-06-26: run a three-hour sustained quality improvement
  goal and finish with push/release.
- `docs/design-north-star.md`
- `docs/conventions/implementation-discipline.md`
- `docs/conventions/operating-contract.md`
- `charness-artifacts/retro/recent-lessons.md`
- `charness-artifacts/quality/2026-06-26-five-pass-boundary-quality-review.md`
- `charness-artifacts/critique/2026-06-26-five-pass-boundary.md`

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only draft vs implementation-continuation. Chosen:
  implementation-continuation because the user explicitly requested a sustained
  goal and final push/release. Rejected: artifact-only would fail the request.
- Quality axis: broad refactor vs measured slice sequence. Chosen: measured
  slices with focused proof and final broad gate because repo contracts require
  evidence before publication. Rejected: one large speculative sweep would make
  critique and rollback harder.
- Runtime axis: remove subprocess boundaries everywhere vs preserve boundary
  smokes. Chosen: convert ordinary behavior assertions only when a real
  boundary proof remains. Rejected: eliminating unique CLI proof repeats the
  prior-session failure class.
- Release axis: publish unconditionally vs release-contract-gated publication.
  Chosen: release skill decides whether to publish, prepare, or block. Rejected:
  direct publish without release proof violates the north-star irreversible
  boundary rule.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Folded blocker: converting subprocess tests can erase the only shipped CLI
  smoke for an entrypoint; the slice explicitly checks for remaining real-boundary
  proof before conversion.
- Folded blocker: push/release is irreversible enough that final success cannot
  be claimed from terminal green alone; final phase uses the release skill and a
  second evidence channel.
- Over-worry not folded: avoiding all test conversion because subprocess smokes
  can be valuable. Counterweight: the boundary-bypass ratchet already separates
  likely keep-boundary rows; ordinary behavior assertions should move lower when
  safe.
- Reviewer provenance: same-agent plan critique at activation; bounded
  fresh-eye critique is planned before final broad proof.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

None yet.

## Final Verification

Closeout pending until the final release/push phase.

## User Verification Instructions

- Run `./scripts/run-quality.sh --read-only`.
- Inspect `git log --oneline origin/main..HEAD` before push, or the pushed tag /
  release evidence after publication.

## Auto-Retro

Retro pending final closeout.
Retro dispositions: pending final closeout.
Structural follow-up: pending final closeout.
