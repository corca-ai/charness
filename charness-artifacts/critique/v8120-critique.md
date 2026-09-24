# Release Critique — charness v8.12.0

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.12.0-release
- **Scope**: `v8.9.8..a47618544` — stale-exec reaping via task_run entrypoint, keep_worktree retention expiry (10-newest), DAG carrier contract, train land/verify flow, steer audit threading, basetemp pruning, worktree prune branch reclamation.
- **Reviewers**: two fresh-eye parallel reviewers (A: operational/safety angle, B: contract/readability angle) + synthesis; read-only, no repo mutation
- **Lane evidence**: release gate 89 passed, 0 failed

Fresh-eye satisfaction: parent-delegated two angle reviewers plus synthesis

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: read-only shared checkout; structured concerns schema
- **Reviewer A**: operational/data-loss angle (`/tmp/critique-A.md`) — 5 findings (2 major, 3 minor), 5 non-findings cleared, verdict SHIP-WITH-NOTES
- **Reviewer B**: contract/readability angle (`/tmp/critique-B.md`) — 5 findings (4 major, 1 minor), 5 non-findings cleared, verdict SHIP-WITH-NOTES
- **Host exposure state**: `host-defaulted`
- **Application state**: `two angle reports plus synthesis delivered with concerns and four-bin triage`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`
- **Lane evidence**: release lane green, 89 passed, 0 failed

## Merged Findings

Deduped across both reports (no overlaps: A covered deletion/safety paths, B covered naming/contract shapes). Severities as assigned by the originating reviewer.

### Ship-Blockers

None — both verdicts were SHIP-WITH-NOTES. This bin is intentionally empty.

### Pre-Release Notes

Items worth addressing before consumers pin the new shapes (B findings 1–4); none blocks ship:

1. **Steer audit text lands in `reason_detail` while the envelope also carries a machine `reason`** — consumers reading `reason` get the nack cause, not the issuer's text; docs name no key. **Severity: major.**
   Evidence: `scripts/task_run/task_run_lane_runner.py:79,84`; `charness:3451,3456`; `docs/cli-reference.md:299`.
2. **DAG plan names the executor slot `carrier`; everything else calls it `executor`.** **Severity: major.**
   Evidence: `scripts/task_run/task_run_dag.py:91,93,99,386`.
3. **`keep_worktree: true` no longer means "kept" — retention expires all but the 10 newest per key, and user docs still promise the old semantics.** Removal is salvage-gated (not data loss) but the contract change is invisible at the CLI/docs layer. **Severity: major.**
   Evidence: `scripts/gates_support/runtime_root_retention.py:22,93,280,340,348`; `docs/agent-task-runs.md:97`.
4. **`charness train` exit code conflates "verify said requeue" with failure (both exit 1), and documents no exit codes.** **Severity: major.**
   Evidence: `charness:5572`; `scripts/task_run/task_run_train_core.py:45`; `docs/cli-reference.md:398` (vs `task run` exit codes at line 327).

### Post-Release Follow-Ups

1. **TOCTOU in empty-lane force removal — clean check then `remove --force`.** Edits landing between the status check and removal are destroyed with no re-verification. Guards are otherwise strong; lane worktrees are machine-owned so the window is narrow. Fix: re-verify before `--force` (or non-force remove with retry). **Severity: major (A1).**
   Evidence: `scripts/task_run/task_run_retention.py:98,107`.
2. **Stale-exec entrypoint failures fall through to receipt-less deletion (fail-open).** `main` always exits 0 with no `log_entry` on `record-missing`/crash paths, and the sweep stop-set only bails on `runner-not-confirmed-dead` / `record-fresh` / `already-terminal` — other outcomes proceed down the legacy idle-delete path, skipping the `interrupted` terminal receipt. Fix: treat entrypoint-failure as a sweep stop. **Severity: major (A2).**
   Evidence: `scripts/task_run/task_run_stale_exec.py:100`; `scripts/gates_support/runtime_root_retention.py:216-335`.
3. **`runner_liveness` catches only two of `os.kill`'s error modes** (`ProcessLookupError`/`PermissionError`); any other `OSError` propagates as a traceback instead of YAML, feeding finding 2's fall-through. **Severity: minor (A3).**
   Evidence: `scripts/task_run/task_run_runtime.py:302`.
4. **`run_prune` irreversibly deletes branches via `git branch -D` on a heuristic** (ancestry or `git cherry` patch-equivalence + clean tree). Ref-loss not content-loss (recoverable via reflog); unknown compare errors fail closed. Risk is a `cherry` false-equivalence on degenerate diffs. **Severity: minor (A4).**
   Evidence: `scripts/worktree/worktree_audit_lib.py:308,361`.
5. **Per-entry basetemp pruning swallows errors silently and has no containment assert** (`except OSError: continue`, unlogged; no `_inside(keys_root)` check); keys with no repo marker but fresh entries are now partially pruned instead of skipped. **Severity: minor (A5).**
   Evidence: `scripts/standing_pytest_basetemp.py:225,274`.
6. **`validated-partial-result` (status) vs `validated-partial` (result_kind) doubles the vocabulary for one outcome.** Tested and documented at the exit-code layer; still a downstream-filter trap. **Severity: minor (B5).**
   Evidence: `scripts/task_run/task_run_state.py:227`; `docs/cli-reference.md:327`.

### Non-Findings Cleared

- **Salvage-before-delete gate intact and fail-closed** — `runtime_lane_salvage.py` verifies the patch with `git apply --check -R` and re-reads the untracked tar member list; `unverified` keeps the worktree. (A)
- **`keep_worktree` expiry requires verified salvage** — expired kept worktrees removed only after the salvage gate; `unverified` returns early. (A)
- **Symlink/file handling in `_remove_tree` is safe** — symlinks unlinked never followed, `_inside(keys_root)` refusal, `OSError` records `failed`. (A)
- **Dry-run honesty holds in the Sweep** — `would-remove`/`would-salvage` paths perform no writes and skip log persistence. (A)
- **Train landing is CAS-guarded and cleanup is scoped** — `_land_main` uses `update-ref <new> <old>` or `--ff-only` into a cleanliness-checked checkout; `finally` cleanup touches only uuid-scoped paths. (A)
- **YAML-on-stdout contract consistent** across `task run`/`steer`/`executors`/`train`/stale-exec via shared `emit_yaml`; sweep records `failed` on unparseable output. (B)
- **`task run` exit codes 0–5 in docs match code** (`RESULT_EXIT_CODES` vs Exit-codes block vs parametrized tests). (B)
- **Stale-exec safety gate** requires record-idle-past-window plus runner confirmed dead; live/unconfirmed runners leave the lane untouched. (B)
- **`--executor` widening** (ordered comma-separated fallback list) reflected in parser help and docs. (B)
- **Steer audit threading**: `--reason`/`--actor` reach both the message envelope and the persisted `scope_amendments` record, covered by tests. (B)

## Verdicts (Quoted)

- **Reviewer A**: "**SHIP-WITH-NOTES** — no blocker found; the two major items are narrow TOCTOU/fall-through windows on machine-owned paths, but finding 1 should get a re-verify-before-`--force` (or non-force remove with retry) and finding 2 should treat entrypoint-failure as a sweep stop, not a fall-through, in a follow-up."
- **Reviewer B**: "**SHIP-WITH-NOTES** — no data-loss or silent-corruption blocker found (removals are salvage-gated, nack paths are safe, exit codes are tested); findings 1–4 should be addressed as docs/rename follow-ups, ideally before consumers pin the `reason`/`carrier`/train-status shapes."

## Boundary Ownership

- **Producer**: release critique reviewers (angle findings plus synthesis)
- **Consumer**: release publisher and operators reading the release notes
- **Owning surface**: `charness-artifacts/critique/v8120-critique.md` (this
  record); reviewed code owned by its modules
- **Verdict**: `owned-correctly`

## Publish Recommendation

Ship v8.12.0. No ship-blockers from either reviewer; the release gate is green (89 passed, 0 failed). Before consumers pin the new shapes, address the four pre-release notes (audit `reason`/`reason_detail` key naming, DAG `carrier` vs `executor`, `keep_worktree` expiry docs, `train` requeue exit code + Exit-codes docs). Carry the six post-release follow-ups (TOCTOU re-verify, entrypoint-failure stop, liveness `OSError` catch, prune `-D` heuristic, basetemp prune logging/containment, `validated-partial` vocabulary) to the next release. Unresolved blockers: none.
