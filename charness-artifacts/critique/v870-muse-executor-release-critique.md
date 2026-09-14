# Release Critique Artifact — charness 8.7.0 (muse executor)

- **Kind**: release critique record for publish boundary
- **Generated**: 2026-09-14
- **Release**: 8.7.0 (`--executor muse` lane support, minor bump)
- **Reviewed input**: staged feature tree (task_run lane runner + `--executor` CLI + docs + tests)
- **Substrate**: three fresh-eye workflow reviewers (gawande/operational, minto/communication, raskin/interface) in separate contexts + parent synthesis + parent counterweight pass
- **Reviewer verdict**: complete=true, unresolved=[]
- **Note**: reviewer evidence below describes the tree as reviewed; the parent counterweight pass then applied the four Act Before Ship fixes plus the effort-error context fix and the Last-verified bump. Post-fix tree: effort errors read `--effort must be one of: ... (codex|muse executor)`, `--executor` help states `Default: codex`, `docs/agent-task-runs.md` lists full muse presets and the per-executor receipt migration note.

## Counterweight Disposition (parent)

- Act 1 (effort range understated): APPLIED — paragraph now lists medium, high, xhigh, max for muse.
- Act 2 (default unstated): APPLIED — `Default: codex.` in `--executor` help, docs paragraph, regenerated cli-reference.
- Act 3 (`model: "default"` opaque): APPLIED as documented-unpinned — receipt keeps `"default"`; doc states verbatim it means whatever `muse exec` ships (the CLI exposes no model version to pin).
- Act 4 (no migration note): APPLIED — per-executor receipt/log migration note in `docs/agent-task-runs.md`.
- Valid-but-Defer (effort errors lack executor context): APPLIED anyway (one-line, keeps existing test regexes green).
- Valid-but-Defer (prompt.md perms, Last-verified): date bumped with the doc edit; perms left as-is (retained runtime/ is the existing debug convention).
- Over-Worry items: accepted as-is, no change.

Fresh-eye satisfaction: parent-delegated — three workflow child reviewers in separate contexts (gawande/operational, minto/communication, raskin/interface) plus parent synthesis; complete=true, unresolved empty.

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `workflow child agents with per-angle briefs; host-defaulted model and effort (no explicit model/effort fields sent)`
- **Host exposure state**: `host-defaulted`
- **Application state**: `three reviewer children plus one synthesis child admitted and completed; reviewer evidence and synthesis record preserved in the session journal`
- **Execution mode**: `typed-subagent`
- **Delivery state**: `findings-received`

## Boundary Ownership

- **Producer:** `scripts/task_run/` lane-runner owners (command construction, effort validation, receipt block)
- **Consumer:** parent orchestrators reading `task run` receipts (`payload["executor"]`, logs, action ids) and operators reading `--help` / `docs/agent-task-runs.md`
- **Owning surface:** task-run lane surface (implementation, CLI parser, receipt schema, docs, tests move together in this change)
- **Verdict:** `owned-correctly` — the change touches CLI parser, receipt schema, docs, and tests, but each fact is produced and consumed by its correct owner: the lane runner owns command/receipt construction, the parser owns the `--executor` surface, docs render the same surface, and no producer-owned state is encoded in a foreign layer.

## Reviewer Record (as reviewed, pre-counterweight fixes)

# Release Critique — 8.7.0

## Release Scope (8.7.0)

8.7.0 adds a `muse` lane executor alongside the existing `codex` default for `charness task run`, with per-executor effort presets, executor-namespaced receipts/logs, and regenerated CLI reference — consumer line: operators can pass `--executor {codex,muse}` with executor-dependent `--effort` to run lanes under either backend.

## Surface-Lock Inventory

- Staged scope: 10 files, +330/-33 — `charness` parser, 2 docs (`docs/cli-reference.md`, `docs/agent-task-runs.md`), 6 `scripts/task_run/` modules, `test_task_run.py`.
- New module `scripts/task_run/task_run_lane_runner.py` (78 lines) byte-identical to on-disk `plugins/charness` mirror; `task_run.py` and `task_run_runtime.py` likewise in-sync. `/plugins/` is gitignored (`.gitignore:36`) as GENERATED; `export_plugin_tree` whole-tree-copies `scripts_root` with no per-module allowlist — no staged plugin file needed, packaging regenerates it.
- CLI surface: `--executor {codex,muse}` (argparse `default="codex"`, unstated in help), `--effort` required for both; codex set `medium, xhigh, max`, muse set `medium, high, xhigh, max` (`TASK_MUSE_EFFORTS`). Plan-time `TaskRunError` via `resolve_task_inputs` plus build-time checks; dry-run-safe. Live `--help` matches staged `docs/cli-reference.md`; `test_render_cli_reference_matches_checked_in_doc` green.
- Receipt shape: codex lanes keep legacy `codex` key (same-object alias of `executor`); muse receipts carry `executor` with `kind/model/effort/timeout_seconds/timeout_scope/command`, drop `payload[codex]` (asserted absent), move command to `executor.command`, action id `{executor}-exec` (`muse-exec`), logs `{executor}.stdout/stderr.log`. Muse `model` is the opaque string `"default"` (`TASK_MUSE_MODEL`).
- Execution paths: `execution_runtime_path = <record>/runtime`; `prompt.md` written there only in non-dry-run `lane_command` muse branch. `_execute_codex` stdin delivery path reused (muse ignores stdin per fake-muse test); `--disable-approval` + `--workspace` reuses identical `writable_dirs`, mirroring codex containment.
- Retention: `release_finished_lane` rmtrees `runtime/` then keeps `[result.json, *.log]` (executor-agnostic glob); `sweep_lane` removes only `worktree/` and `runtime/` subtrees so record-level `muse.stdout/stderr.log` survive.
- Failure mode: missing `muse` on PATH yields clean preflight-fail YAML (`muse executable is not on PATH: muse`, exit 1, no traceback, no worktree). No CLI executable override (no `--codex` flag; `cmd_task_run` leaves codex default so muse resolves via PATH).
- Verification: 82 passed across `test_command_docs_gate.py`, `test_task_run.py`, `test_task_run_result.py` (incl. 3 new muse tests). No in-repo unconditional `payload[codex]` readers; `timeout_scope`/`codex-exec` referenced only in tests.

## Findings

### Act Before Ship

1. **Muse effort range is understated in docs.** `docs/agent-task-runs.md` says "`muse` (muse default model, `high` effort available)" but implementation allows four presets — `TASK_MUSE_EFFORTS = ("medium", "high", "xhigh", "max")` and `--effort` help says "medium, high, xhigh, or max for muse". An operator reading only the paragraph will think `high` is the sole muse option.
   - Operator Action Required: fix paragraph to "`muse` (muse default model; effort one of medium, high, xhigh, max)".
2. **Default executor unstated.** Help reads "Lane executor: codex (fixed gpt-5.6-luna model) or muse (muse default model). Effort presets depend on the executor." with no "(default: codex)" though argparse sets `default="codex"`. Combined with the codex+high trap, an operator omitting `--executor` and passing `high` gets a rejection with no pointer.
   - Operator Action Required: add "Default: codex." to `--executor` help, docs paragraph, and `cli-reference` copy (regenerate/verify via docs gate).
3. **Muse receipt `model: "default"` is opaque/unauditable.** `record_lane_runner` sets `"model": TASK_MODEL if codex else TASK_MUSE_MODEL` where `TASK_MUSE_MODEL = "default"` (test asserts `payload["executor"]["model"] == "default"`). Against docs "muse default model", a receipt grepping `model: default` pins no CLI version.
   - Operator Action Required: either resolve the real `muse` model version at launch or document verbatim in `agent-task-runs.md` that `model: "default"` means "whatever `muse exec` ships, unpinned".
4. **Per-executor receipt/log break has no doc migration note.** Muse receipts drop `payload[codex]`, move command to `executor.command`, rename action id to `muse-exec` and logs to `muse.stdout/stderr.log`. External readers keyed on `codex` break.
   - Operator Action Required: document per-executor receipt shape and log names (migration note) in `agent-task-runs.md` and/or `cli-reference`.

### Bundle Anyway

- Plugin export mirror needs no staged file: `/plugins/` is gitignored/generated, exporter copies the whole tree, mirror already byte-identical; release packaging regenerates it.
- `cli-reference` regeneration is done and verified: staged doc matches renderer output (gate green), live `--help` matches staged text, command-docs assertions pass.
- Payload schema change is safe as staged: codex keeps legacy `codex` key, muse carries `executor` block; no in-repo unconditional `payload[codex]` readers, `timeout_scope` has no consumers beyond tests, both retention paths are executor-agnostic so `muse.*.log` survive.
- Muse executable resolution failure verified by live probe: clean preflight-fail payload, actionable error, exit 1, before worktree creation. No executable override flag is acceptable for this release.
- Bad `--executor` quality is good at both surfaces — keep: CLI argparse `invalid choice: 'bogus' (choose from 'codex', 'muse')`; API `resolve_task_inputs` `--executor must be one of: codex, muse`.
- `--executor` UX (choices, default codex, plan-time error), per-executor effort validation (plan-time + build-time, tested), `--disable-approval` headless tradeoff with same-`writable_dirs` `--workspace` containment, and prompt-inside-granted-root are self-consistent — no change.

### Over-Worry

- `prompt.md` lifecycle under the retention sweep: written to `<record>/runtime/prompt.md`, removed with `runtime/` on release and by sweep, never in any kept-list, never written on dry-run. No leak, no sweep bug.
- Codex-specific → generic renames ("Implementation instructions passed to the lane executor.", adapter/lane wordings) plus executor-interpolated dry-run `next_step`/`action` ids and log filenames are legible and consistent.
- `_execute_codex` still feeding stdin prompt to muse (ignored per fake-muse test) is cosmetic-only; codex-named internals need no rename for ship. `--effort high` without `--executor` failing under the codex default is guided by error + help text.

### Valid but Defer

- Effort errors omit executor context (`--effort must be one of: ...` names neither `codex` nor `muse`), forcing a help round-trip at the confusing boundary. Cheapest fix inside `build_*_args`: append `(executor: codex|muse)`. Deferrable because `--effort` help already prints both sets side by side.
- Muse `prompt.md` is a persistent umask-mode file (retained on failed lanes for debugging, consistent with keeping `runtime/`) vs codex anonymous 600 temp stdin that is never persisted; consider restrictive perms/cleanup and one doc line. Same doc's Last verified date (2026-09-05) unbumped and effort understatement (see Act item) are cosmetic beyond the Act fixes.

## Upgrade Path

None — codex-default back-compat preserved (default `codex`, legacy `codex` payload key kept, retention globs executor-agnostic); muse is opt-in via `--executor muse`. Only external readers keyed on `payload[codex]` / `codex.stdout.log` / `codex-exec` need the Act-item migration note if they consume muse lanes.
