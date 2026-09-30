# Release Critique — charness v8.14.4 (patch)

Date: 2026-09-30

## Decision Under Review

Ship charness v8.14.4 (tag v8.14.4, surfaces 8-14-4) as a patch release
carrying the #881 (cleanup chmod of shared hardlink inodes), #882 (detached
lane shorthand dropping `--base`), #883 (steer queue producer/consumer path
split), #884 (brief precheck confusing its Codex context with the selected
Muse executor), and #825 (mutation scope-gap coverage) fixes, plus
critic-driven follow-ups (detach parity gaps, setup flat imports, Windows
unlink guard, budget honesty, resolver core, chmod tripwire) and
release-critique bundle items (help honesty, executor wording, raw
provenance), with focused tests throughout.

Kind: charness release critique
Prepared for: v8.14.4 patch release
Scope: 28 shipped files over 12dfc1590..45c17392a (1 CLI entry, 2 docs, 14
task-run/setup/support scripts, 11 test files); reviewers read the pushed
range plus the working tree before the bundle commit, and the parent verified
the bundle diff directly with focused suites.
Reviewers: 2 native read-only fresh-eye subagents (operational + legibility),
parent-owned counterweight (this artifact)

## Release Scope

v8.14.4 is a patch release: five issue fixes plus structural follow-ups and
focused tests. It closes #881, #882, #883, #884, and #825. No new commands,
flags, skills, or install surfaces; no migration; additive receipt keys only
(`prelaunch.brief_critique.lane_executor/lane_executable`,
`progress_guard.budget_raw`).

## Surface-Lock Inventory

Generated artifacts: the `plugins/` mirror is generated and gitignored; the
8.14.4 bump regenerates it via `sync_root_plugin_manifests.py` (verified
no-op on the pre-bump tree). `docs/cli-reference.md` is generated from the
parser and was regenerated for the `--lane`/`--base` help fix.

Consumer-visible behavior:
- Detached launch refuses before spawn what the foreground plan refuses
  (lane mixed with `--path`/`--branch`; explicit runs missing
  `--path`/`--branch`/`--base`), byte-identical messages, exit 1.
- Detached lanes now honor `--base` with `--lane` and enforce
  `--require-change` (previously both silently dropped).
- `task steer --message` on a running lane is delivered at the next turn
  boundary (previously accepted but silently lost).
- Brief precheck names the validated lane executor instead of inferring
  unavailability from its own Codex tools; fewer false premise-blocks.
- Garbage `CHARNESS_TASK_RUN_NO_PROGRESS_SECONDS` records source `default`
  (was: falsely `env`) with the raw spelling kept in `budget_raw`.
- POSIX cleanup no longer chmods file inodes (Windows-only file bits kept,
  where unlink requires them).

Documentation surfaces: `--lane`/`--base` help corrected;
`docs/agent-task-runs.md` exceptional-setup line narrowed; release notes
carry the two behavior reversals (require-change enforcement, base honored).

## Operator Action Required

None before upgrade. After upgrade, two expected behavior reversals: detached
`--require-change` lanes that previously "passed" unchanged may now fail the
changed-gate (the fix working, not a regression); detached `--lane` + `--base`
runs now use the given base instead of silently running on HEAD. Steers
queued-but-undelivered across the upgrade instant stay undelivered (they were
never delivered under the old path split either).

## Upgrade Path

Standard patch upgrade from any 8.x install via `charness update`; no
migration, no config change. Rollback to 8.14.3 is safe (old builds ignore
the new receipt keys) but reintroduces the dropped base/require-change,
dropped steers, and mislabeled budget source.

## Verification Scope Decision

- Claim under test: v8.14.4 patch ships the 881/882/883/884/825 fixes plus
  follow-ups with tests and breaks no pinned contract (refusal vocabulary,
  receipt shapes, resolver messages, POSIX unlink semantics).
- Changed surfaces: charness, docs/agent-task-runs.md, docs/cli-reference.md,
  scripts/cli/cmd_task.py, scripts/gates_support/runtime_root_retention.py,
  scripts/runtime_scratch.py, scripts/setup/setup_adapter_inspect_lib.py,
  scripts/setup/validate_maintainer_setup.py, scripts/task_run/task_run_attempts.py,
  scripts/task_run/task_run_brief_critique.py, scripts/task_run/task_run_detach.py,
  scripts/task_run/task_run_execution.py, scripts/task_run/task_run_git.py,
  scripts/task_run/task_run_lane_runner.py, scripts/task_run/task_run_plan.py,
  scripts/task_run/task_run_prelaunch.py, scripts/task_run/task_run_progress.py,
  scripts/task_run/task_run_runtime.py,
  tests/charness_cli/test_task_run_detach_wait_866.py,
  tests/charness_cli/test_task_run_git_refusals.py,
  tests/charness_cli/test_task_run_no_progress_835.py,
  tests/charness_cli/test_task_run_premise_gates.py,
  tests/charness_cli/test_task_run_steer.py,
  tests/quality_gates/test_chmod_allowlist.py,
  tests/quality_gates/test_maintainer_hooks.py,
  tests/quality_gates/test_setup_inspect_adapters.py,
  tests/test_runtime_root_retention.py, tests/test_runtime_scratch.py
- Minimum sufficient proof: two fresh-eye reviewer passes with all findings
  triaged below; bundle fixes parent-verified with focused suites (58 CLI
  premise/detach/budget tests green); standing suite 11078 passed on the
  final tree; ruff check clean; pre-push full/read-only and release lanes
  green on the pushed range; parser round-trip and chmod-allowlist tripwires
  green with executed negative controls.
- Deliberately omitted checks: end-to-end detached Muse lane on a live
  provider (no credentialed lane run in this slice; forwarding proven through
  the real parser plus dry-run plans); Windows execution of the nt-gated
  unlink branches (no Windows host; POSIX branches proven, nt branches
  simulated by platform patch); scheduled mutation sample over these files
  (owned by the scheduled mutation lane, not this release).
- Verifier contract: native read-only subagents on the shared tree (reviewer
  verdicts in this session's subagent logs, agents 18 and 19); standing
  pytest; run-quality full read-only lane; ruff check; real-parser probes;
  this artifact validated by validate_critique_artifacts.py.
- Failure classification: none
- Negative control: command: temporarily removed ("critical_lane", "--critical-lane") from _mode_argv and ran the parser round-trip test; expected: the round-trip test fails because the child argv no longer re-parses to the parent namespace; observed: 1 failed; receipt: restored the line, 36 passed after (this-session run record).
- Subject identity: sha256:f69d6ac6982d10bb8f151eed74020bd903e65600bba523330d8e5bda749452e1
- Verifier identity: sha256:1986176e22e058ac35accf0002f1065b8230d46351096e7d34f3caf0084d9767
- Input identity: sha256:471af90fc9284721e144971bfdf90b9e543bb0c632eadfdd1747d7456f25295d
- Failure identity: stable:clean
- Evidence identity: sha256:f673ad4a672f2a205ec84122320ce04066256bff360119424e5efc0e2f61b3f8
- Retry disposition: first-attempt
- Retry key: sha256:00aeca5176955475e42bfb3d2f32952891d00548508d78761c918b22fb02bc5a

Identity preimages (reproducible): subject is sha256 of
`git diff 12dfc1590..45c17392a` bytes; verifier is sha256 of the two reviewer
verdict texts joined by NUL (agents 18/19); input is sha256 of the string
"release 8.14.4 patch over 12dfc1590..45c17392a closing #881 #882 #883 #884
#825"; evidence is sha256 of "standing:11078 passed;" plus the first 512
bytes of tests/quality_gates/test_chmod_allowlist.py.

## Failure Angles

- Operational readiness and surface lock (reviewer 18): version-surface
  consistency (all 7 fields at 8.14.3, zero drift), manifest sync state,
  exact behavior diffs with file:line, install/upgrade/rollback hazards.
  Returned one procedural blocker (bump missing before tag — the publish
  sequence itself), two majors (behavior reversals need release-note lines),
  four minors (stale tracking ref, stderr-vs-YAML envelope, docs gaps,
  in-flight steer orphans). No code defect asserted.
- Legibility and interface (reviewer 19): operator story compression,
  user-facing wording diffs, help/README/doctor impact. Returned no
  blockers, two majors (help contradicts the detach fix; reversals need
  explicit notes lines), four minors (carrier collision, raw shadowing,
  receipt-only fallback, branch-missing message). No code defect asserted.

## Counterweight Triage

- Act Before Ship: none in code. The procedural bump-before-tag item is the
  publish sequence below, not a code hold.
- Bundle Anyway (implemented in 45c17392a, parent-verified): --lane/--base
  help corrected plus cli-reference regen and agent-task-runs line; prompt
  and helper renamed from carrier to executor; budget_raw recorded even when
  the flag shadows env (plus test); branch-missing refusal unified with the
  explicit-form requirement text. Release notes carry the two behavior
  reversals and the in-flight steer note.
- Over-Worry: detach stderr-vs-YAML envelope (pre-existing pattern, same exit
  codes, unchanged by this release); in-flight steer orphans beyond a notes
  line (never delivered under either path).
- Valid but Defer: live stderr note on garbage env (repeats per attempt;
  needs once-per-lane design); task-dir spelling unification (consistent
  today; needs an enforcement gate to be real); steer post-loop TOCTOU
  (true race, honestly recorded via undelivered entries).

## Fresh-Eye Satisfaction

parent-delegated: two independent native-subagent passes with materially
different lenses (operational, legibility) returned no blocking code defect;
every finding either shipped in the bundle commit with tests or triaged above
with a named reason. The bundle diff itself (help text, prompt wording, raw
hoist, refusal message) was parent-verified with focused suites rather than a
third reviewer round; the slice stops here by the bounded follow-up rule.

## Reviewer Tier Evidence

- Requested tier: native read-only subagents on the shared tree (no file-backed worker tier requested; host exposes no reviewer-tier control)
- Requested spawn fields: role, objective, task_name per reviewer via subagent_spawn; read-only brief, no isolation (shared checkout, no writes)
- Host exposure state: host-defaulted
- Application state: two findings received in parent context; both reviewers read-only with no writes; model/effort mapping not host-visible
- Delivery state: findings-received
- Execution mode: typed-subagent

## Boundary Ownership

- Producer: the foreground plan resolver (owns target/base refusal vocabulary), the lane receipt writers (own receipt fields), the env readers (own budget values)
- Consumer: detached-lane operators and orchestrators reading refusal text, steer senders, receipt readers (orchestrator, claims review), no-progress guard debuggers
- Owning surface: task-run lane modules (detach argv builder, steer queue owner, prelaunch gates, progress guard)
- Verdict: owned-correctly
