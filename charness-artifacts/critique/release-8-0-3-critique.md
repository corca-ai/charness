# Release 8.0.3 Critique

Date: 2026-09-03

## Execution

Fresh-Eye Satisfaction: `parent-delegated`.
Target: `release-critique.md`.

Two bounded file-backed reviewers ran in parallel through
`skills/public/critique/scripts/run_review.py` (backend `codex_exec`, boundary
`read-only-worker`), with materially different lenses: an operational
checklist (Gawande) asking what release-time step is missing or wrong before
the tag, and an operator-surface lens (Minto and Raskin) asking whether the
surface a reader upgrades onto is legible and honest. Both delivered typed
results (`delivery_state: findings-received`); the counterweight pass below is
parent-owned. No in-process host subagent was used, so the delivery gap the
Claude host adapter records for that path does not apply here.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/release-8-0-3-final-identity-1-packet.json
- Packet path: charness-artifacts/critique/release-8-0-3-final-identity-1-packet.json
- Packet SHA256: f0e78c25a7d0d8b4828a367350eb6a7cc6975eba96802655f6416c02337cfc59
- Identity SHA256: dcda037e7b317e70e0b57cf7e84e85e7c15727de5604b709570759d480346c59
- Reviewed-path manifest: `charness-artifacts/critique/2026-09-03-release-8-0-3-reviewed-paths.txt`
  (54 release-locking paths changed since `v8.0.2`; every packet below is a
  `prepared-for` packet over that manifest, not a changed-ref sweep of the
  1,731 paths in `v8.0.2..HEAD`).
- The packet above is the identity of the FINAL bytes, derived with
  `--dry-run` after the last one-line wording repair (RV4) and reviewed by no
  one; the three reviewer passes below judged the tree one wording change
  earlier. Stated rather than hidden, per the claims-review convergence rule.
- Reviewer 1 packet: `charness-artifacts/critique/release-8-0-3-gawande-1-packet.json`,
  SHA256 `a53035cbc3a4607867243910d7ef236895ece4340d7db8140e061b0c9894501d`,
  identity `8d225218ebcc395c607cd788845641f907ec21674b88347aa60d378db6b01d68`,
  attempt `release-8-0-3-gawande-1`, verdict `block`, five findings.
- Reviewer 2 packet: `charness-artifacts/critique/release-8-0-3-minto-raskin-1-packet.json`,
  SHA256 `e0a4be936f0b9930ca1f8d117600d9a4b164baf217c7c840e910d9634ddf29e7`,
  same identity, attempt `release-8-0-3-minto-raskin-1`, verdict `defer`, two
  findings.
- Reviewer 3 packet (repair verification, on the repaired tree):
  `charness-artifacts/critique/release-8-0-3-repair-verify-1-packet.json`,
  SHA256 `6b534daa2a258cf59353893ab207cc8d395217b57ebab35b7d3d70fa0d097c60`,
  identity `97791ed64da4582894d15ed346e16188ec19178d6eca129e6299ebd8b1749219`,
  attempt `release-8-0-3-repair-verify-1`, verdict `block`, eight findings
  (five confirmations, one minor, two majors on evidence binding).
- Worker receipts, ledgers, prompts, and results under
  `.charness/reviewer-round-release-8-0-3-*/` (run state, not tracked).

## Reviewer Tier Evidence

- requested tier: `high-leverage` (adapter `reviewer_tiers.high-leverage`:
  `gpt-5.6-terra`, `reasoning_effort: medium`, `service_tier: priority`).
- requested spawn fields: file-backed Codex worker through `run_review.py`
  with the adapter's `reviewer_runner` (`mode: file-backed-worker`,
  `backend: codex_exec`, `timeout_seconds: 900`); no host subagent spawn.
- host exposure state: `host-defaulted`
- host exposure note: the Codex CLI applied its own defaults; the packet
  records the request, not the model the host chose.
- application state: unverified-by-packet.
- execution mode: `file-backed-worker`
- backend: `codex_exec`, capability status `ready`, capability envelope
  `28cb0f1d3d601800661d75b180c688ec47fe1f164ccfd593c22bae8fd3d2715f`.
- delivery state: `findings-received` for both; `receipt_ok`, `ledger_ok`,
  `result_schema_ok`, `provenance_ok` all true in both worker reports.

## Boundary Ownership

- Producer: `scripts/core/helper_provenance_lib.py` owns the question "which
  charness tree is this script, judged against the target repo" for every
  skill entrypoint.
- Consumers: `goal_run_pickup.py` (reports and refuses), `plan_release_run.py`
  (reports), and the publish helper's entrypoint guard (refuses), each calling
  the producer rather than restating the comparison.
- Owning surface: `scripts/core/helper_provenance_lib.py`; the receipt field
  `script_origin` is a projection of its verdict.
- Verdict: owned-correctly

The other mechanisms in this release each have one owner: the lane
changed-line verdict is produced by `release_changed_line_coverage.py` and
carried verbatim by `task_run_changed_line.py`; retention is
`runtime_root_retention.py` with `task_run_completion.py` as its one
completion-time caller; the timeout-bound predicate lives only in
`check_timeout_bound_form.py`.

## Release Scope

Version: `8.0.3`. Tag: `v8.0.3`. Previous: `8.0.2`.

Change: patch, and the operator pre-approved this version by name on
2026-09-03. 182 commits since `v8.0.2`. What changes for a consumer: a
`charness task run` lane cannot report done past a changed line the release
gate would refuse, and its receipt carries the verdict; a finished commit-only
lane releases its worktree and names the branch that carries the candidate;
the runtime tree under `charness/runtime/` reclaims itself and keys are
siblings; a test whose verdict rides on a short timeout is refused by a new
standing form check; skill scripts run inside the authoring repo say which
copy answered. No public skill, CLI subcommand, or install surface gained or
lost a member; the lightest honest bump is patch.

## Surface-Lock Inventory

- Packaging and manifests: `packaging/charness.json`,
  `plugins/charness/.claude-plugin/plugin.json`, the Codex plugin manifest,
  and the root marketplace files (unchanged since `v8.0.2` until the bump the
  publish helper writes).
- Root CLI `charness` (unchanged in this range) and the install/update path
  it owns (`init`, `update`, `version`, `doctor`).
- README and the docs owner pages this range touched: `docs/development.md`,
  `docs/agent-task-runs.md`, `docs/parallel-execution.md`,
  `docs/goal-lifecycle.md`, `docs/validator-timing-layers.md`.
- Exported shared guidance: `skills/shared/references/bootstrap-resolution.md`;
  public `SKILL.md` files touched in the range.
- Host adapters: `.agents/claude-host.md`, `.agents/codex-host.md`,
  `.agents/release-adapter.yaml`, `.agents/quality-gates.yaml`.
- New mechanisms: `scripts/task_run/task_run_changed_line.py`,
  `scripts/task_run/task_run_completion.py`,
  `scripts/gates/check_timeout_bound_form.py`,
  `scripts/gates_support/runtime_root_retention.py`,
  `scripts/runtime_bootstrap.py`,
  `skills/public/achieve/scripts/goal_run_pickup.py`,
  `skills/public/release/scripts/plan_release_run.py`.

## Findings

### Act Before Ship — fixed in `e487d14b1` before the bump

- Reviewer 1, F2 (critical). The runtime-root sweep's salvage parsed
  human-quoted `git status --porcelain` paths, so an untracked file with a
  space, quote, backslash, or non-ASCII byte was skipped silently while the
  salvage still reported complete and the worktree was removed. Now
  `--porcelain -z`, a refusal when git names a path that is not on disk, and
  an archive readback proving every untracked path is a member before the
  worktree goes; a rename's old-name record is dropped. Seeded in
  `tests/test_runtime_root_retention.py` with the five awkward names, a ghost
  path, and a lossy archive.

### Bundle Anyway — done in `e487d14b1`

- Reviewer 1, F1 (critical as filed). `charness update` fast-forwards the
  managed checkout's branch (`git pull --ff-only`, `charness:1205-1225`); the
  release adapter's update instruction said it installs the latest published
  release. Verified in the CLI; the instruction now says what the command
  does. Changing the command's semantics is a product decision outside this
  release (reviewer 1's own triage: "product choice, not automatic blocker").
- Reviewer 1, F5 (medium). `docs/goal-lifecycle.md` read "conditional, not
  current implementation" while the achieve skill and the CLI ship the Goal
  Run as current; marked current with the live proof named and the
  installed-consumer non-claim kept in one sentence.
- Reviewer 2, stale-planner claim (blocker as filed). The Claude host adapter
  said both the pickup and the release planner refuse a drifted copy; the
  planner only reports because it is read-only, and the publish helper's
  entrypoint guard is the refusal. The adapter now says exactly that.
- Reviewer 2, host reload gap (high). README moved from install straight to
  the first prompt; the host loads the plugin at startup, so the restart step
  the CLI already prints (`charness:1589`, `charness:2331`) is now in the
  README between install and first use, with Claude Code and Codex wording.

### Over-Worry — rejected with evidence

- Reviewer 1, F4 (high as filed). The packet did not bind the packaging and
  marketplace manifests. They were unchanged since `v8.0.2`, so the
  changed-path manifest omitted them, and the publish helper's own release
  lane (`./scripts/run-quality.sh --release --read-only`, which includes
  `validate-packaging-committed`) validates the committed packaging on the
  exact candidate before the tag. That is where the byte-bound receipt
  belongs; the critique packet is not the release lane.

### Valid but Defer

- Reviewer 1, F3 (high). No pre-tag rehearsal of the managed install/update
  surface is required by the adapter. The rehearsal exists:
  `./scripts/self-validate-install-update.sh` ran on this tree before the
  bump (37 passed in 34 s) and is recorded here. Making it a required release
  probe changes the adapter's `fresh_checkout_probes` contract and its
  budget, which belongs to the next release with its own critique.

## Repair Verification (reviewer 3)

- RV1, RV2, RV3, RV5 (info): F2, F1, F5, and the README reload step are
  confirmed implemented, file and line named in the worker result.
- RV4 (major, act before ship, fixed): `docs/development.md` still said the
  release planner refuses a drifted copy; it now says the pickup refuses, the
  planner reports, and the publish entrypoint refuses before mutation. The
  identity packet above was re-derived after this fix.
- RV6 (minor): the two generalized docstrings are
  `goal_run_pickup.py::_script_origin` and
  `plan_release_run.py::_script_origin`; named here as the attribution asked
  for.
- RV7 (major, fixed): the install/update rehearsal is now bound as a tracked
  receipt, `charness-artifacts/release/2026-09-03-v8.0.3-install-update-rehearsal.md`
  (command, tree, exit status, and the pytest tail).
- RV8 (major, evidence channel named): the exact-candidate packaging proof is
  the publish helper's release lane (`quality_command` in
  `.agents/release-adapter.yaml`, run by `publish_release.py` before the tag)
  and is recorded in the release record's Verification section; the critique
  packet does not carry it, and the F4 disposition stands on that record, not
  on this artifact.

## Operator Action Required

- None outstanding at the tag. F2, F1, F5, and both reviewer-2 findings are
  in the tree the bump is cut from; F3's rehearsal ran.

## Upgrade Path

- `charness update` fast-forwards the managed checkout; restart Claude Code
  or start a new Codex session afterwards. No migration. Rollback is
  `git checkout v8.0.2` in the managed checkout followed by `charness update
  --no-pull`.

## Deliberately Not Doing

- Making `charness update` resolve the latest published tag instead of the
  branch head. A behaviour change to the install path is not a patch-release
  repair, and the instruction now describes the real behaviour.
- Adding the install rehearsal to `fresh_checkout_probes` in this release.

## Verification

- Standing runner and full read-only quality lane on the critique-fixed tree:
  recorded in the #784 session record with counts.
- Changed-line gate on the critique-fix diff: `status: clean`.
- `./scripts/check-docs.sh`: PASS. `validate_skill_ergonomics.py`: no
  package issue-anchor findings after the two docstrings were generalized.
