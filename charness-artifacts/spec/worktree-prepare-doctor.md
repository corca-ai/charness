# Spec — Worktree Prepare/Doctor Contract

Date: 2026-05-07

## Problem

Agent flows that call `git worktree add` (or any `EnterWorktree`-shaped tool) land in a checkout that is missing `node_modules`, missing per-worktree dev tool state, and pointing at a `core.hooksPath` whose shim was generated against the install-time absolute path of another worktree. Lefthook in particular generates a hook shim under `.git/hooks/` (which is shared across all worktrees of a single git common dir) with a hardcoded absolute path to the install-time `node_modules/lefthook-${osArch}-${cpuArch}/bin/lefthook`; when that path no longer resolves, the shim falls back through PATH and silently exits 0 with `Can't find lefthook in PATH` ([lefthook #1398](https://github.com/evilmartians/lefthook/issues/1398)). Husky has the equivalent failure mode for `.husky/_/` ([husky #580](https://github.com/typicode/husky/issues/580)).

Symptom: pre-commit hooks silently skip, unformatted code lands, CI catches it later. Naively symlinking `node_modules` from the source worktree breaks Vite/Vitest module resolution, so the structural fix has to live one layer up.

charness owns the agent-facing surface that creates these worktrees. The structural fix should live in charness's adapter/CLI/skill contract so consumer repos opt in once and stop hitting this trap.

## Decision

Define a portable worktree readiness contract owned by charness.

Canonical surfaces:

1. `.agents/worktree-adapter.yaml` — consumer-repo-owned manifest. Declares the `prepare` command(s) the repo wants charness to run after a fresh worktree appears, and the `doctor` health probes that decide whether a worktree is usable without running `prepare` again.
2. `charness worktree doctor` — read-only, fast, deterministic. Inspects `core.hooksPath`, lefthook/husky shim resolution, and the manifest's declared `doctor.checks`. Exit 0 = ready, non-zero = next-action surfaced.
3. `charness worktree prepare` — runs the manifest's `prepare.commands`, then re-runs `doctor` and reports. No-op when `doctor` already passes unless `--force` is passed.
4. Mutate-phase public skills (`impl`, `hitl`) call `charness worktree doctor` in their bootstrap. On failure they surface `charness worktree prepare` as the next action — they do not auto-run it.
5. `setup` seeds `.agents/worktree-adapter.yaml` from a portable preset when a consumer repo opts in, and links `docs/worktree-prepare.md` as the operator surface.

Canonical doctor checks (always run, manifest-independent):

- `git rev-parse --git-common-dir` resolves and is shared across worktrees.
- `git config core.hooksPath` resolution: if set, the resolved directory exists in this worktree.
- Lefthook shim probe: if `.git/hooks/pre-commit` (resolved against `--git-common-dir`) references `lefthook`, then either `node_modules/lefthook-*/bin/lefthook` exists in this worktree OR `lefthook` resolves on PATH.
- Husky probe: if `core.hooksPath=.husky/_` (or any `.husky/_*`), then that directory exists in this worktree.

Canonical prepare order (when manifest is present):

1. Run `prepare.commands` in declared order, each as `subprocess.run(..., shell=False)` from the worktree root.
2. After success, run all doctor checks again. Any check still failing is reported and exits non-zero.

Output contract:

- Both subcommands accept `--json` and emit a stable schema (see `Success Criteria`).
- Human output is one summary line per check: `worktree.hooks_path: pass`, `worktree.lefthook_shim: fail (next: charness worktree prepare)`.

## Non-Goals

- Symlinking `node_modules` (rejected — Vite/Vitest break, see Dave Schumaker's writeup).
- Owning a package manager wrapper. The manifest declares commands; charness only schedules them.
- Re-implementing pnpm's `enableGlobalVirtualStore` ([pnpm guidance](https://pnpm.io/11.x/git-worktrees)). The doctor surfaces the recommendation, the consumer repo configures pnpm.
- Auto-running `prepare` from inside `impl`/`hitl`. Confirmation belongs to the operator. The skill surfaces the next action.
- Patching git's hook resolution or fighting `git --git-common-dir` semantics.
- Solving the broader monorepo dependency story. Workspace `node_modules` plurality is a manifest concern, not a charness concern.

## Current Slice

1. Add `.agents/worktree-adapter.yaml` schema + `skills/public/impl/adapter.example.yaml`-style example. Schema lives at `integrations/worktree/manifest.schema.json` (separate from `integrations/tools/` because this is a repo-self-config manifest, not an external tool integration).
2. Add `scripts/worktree_doctor.py` and `scripts/worktree_prepare.py` with library split (`scripts/worktree_doctor_lib.py`) so tests can hit the library without invoking the CLI.
3. Add `charness worktree doctor` and `charness worktree prepare` subcommands wired through the existing argparse tree in `charness`.
4. Wire `impl` SKILL.md `Bootstrap` block to call `charness worktree doctor --json` non-fatally and surface the next action only when status is non-pass. Same wiring on `hitl`.
5. Add `tests/charness_cli/test_worktree_doctor.py` with deterministic fixtures for: clean worktree, missing `node_modules` + lefthook present, husky `_` directory missing, manifest-declared command failure.
6. Sync `docs/generated/cli-reference.md` (`scripts/render_cli_reference.py`) and `docs/worktree-prepare.md`. Update `docs/handoff.md` `Current State` and `Next Session`.
7. Add a portable `setup` preset slot for the worktree adapter (seeded only when the consumer repo opts in via `--seed-worktree-adapter` or equivalent post-init prompt).

## Fixed Decisions

- The manifest goes at `.agents/worktree-adapter.yaml`, sibling to existing `<skill>-adapter.yaml` files.
- `prepare.commands` is a required ordered list of strings parsed as argv (no shell expansion).
- `doctor.checks` extends but does not replace the canonical baseline checks listed above.
- `worktree doctor` exits 0 only when every canonical check and every manifest check passes. `--json` exit codes mirror text mode.
- `impl`/`hitl` bootstrap uses `--json` and never blocks; doctor failure becomes a printed next-action only.
- `node_modules` is never symlinked or copied by charness. Consumer repos that want copy-on-write share that responsibility through `prepare.commands`.
- The lefthook shim probe is heuristic and PR-shaped (matches the upstream codegen), not a hard parser of generated shim contents. If lefthook upstream changes the shim, the heuristic drifts gracefully.

## Probe Questions

- Q1: Do consumer repos need a separate `pre_prepare` hook for things like `git lfs pull` or signed-commit setup, or is the single `prepare.commands` ordered list enough for the dogfood targets?
- Q2: Should `worktree prepare` write a `charness-artifacts/worktree/last-prepare.json` so subsequent `doctor` runs can short-circuit on unchanged HEAD? Defer until first dogfood reports prepare cost.
- Q3: Should the doctor probe husky and lefthook by reading `package.json` / `lefthook.yml` directly, or only via the shim/hookspath signal? Start with shim-only; expand only if probes miss real failures.

## Deferred Decisions

- Multi-package monorepo workspace probes (yarn workspaces, pnpm workspaces, turborepo).
- Auto-detection of pnpm `enableGlobalVirtualStore` and recommendation rendering.
- A dedicated `charness worktree add` wrapper that creates the worktree and runs prepare in one step. (`EnterWorktree` tool integration stays out of scope until the doctor/prepare slice has dogfood evidence.)
- Caching prepare runs across worktrees of the same HEAD.

## Success Criteria

1. `charness worktree doctor --json` exists and emits `{"checked_at", "checks": [{"id", "status", "detail", "next_action"}], "status", "next_action"}` where `status` is one of `pass|fail|skipped` and exit code is 0 only when `status == "pass"`.
2. `charness worktree prepare --json` exists and emits `{"executed": [{"command", "exit_code", "duration_ms"}], "doctor": <doctor payload>, "status"}` and exits non-zero when any executed command fails or post-prepare doctor still fails.
3. With no `.agents/worktree-adapter.yaml`, `charness worktree doctor` runs canonical checks only and reports `manifest.found: false` without erroring.
4. With a manifest declaring `prepare.commands: ["echo hi"]`, `charness worktree prepare` executes the command and reports it in `executed[0]`.
5. In a synthetic worktree where lefthook shim references a missing `node_modules/lefthook-*/bin/lefthook` and `lefthook` is not on PATH, `charness worktree doctor` exits non-zero and the `next_action` field names `charness worktree prepare`.
6. `impl` SKILL.md and `hitl` SKILL.md both reference `charness worktree doctor` in their bootstrap surface.
7. `docs/generated/cli-reference.md` regeneration produces no drift after the new commands are wired and `tests/quality_gates/test_command_docs_gate.py` (or its equivalent) stays green.
8. `node_modules` is never written, copied, or symlinked by any charness-owned code path introduced in this slice.
9. The new code paths add no new external binary dependency to charness itself; manifests can declare their own.

## Verification Plan

- Unit/library tests in `tests/charness_cli/test_worktree_doctor.py` covering: no-manifest pass, lefthook shim missing fallback, husky `_` missing, manifest command success, manifest command failure, post-prepare doctor still failing.
- Manual proof: create a temp git worktree on this repo with `git worktree add /tmp/charness-wt-proof HEAD`, then run `python3 scripts/worktree_doctor.py --json --repo-root /tmp/charness-wt-proof` and confirm clean pass (charness has no node_modules / lefthook so canonical checks should be `skipped` not `fail`).
- Render proof: run `python3 scripts/render_cli_reference.py --repo-root . --output docs/generated/cli-reference.md` and confirm no drift after the wiring slice.
- Closeout: bounded fresh-eye subagent critique against the new manifest contract before commit.

## References

- [lefthook #1398 — install-time absolute path breaks worktrees](https://github.com/evilmartians/lefthook/issues/1398)
- [husky #580 — long-standing worktree incompat](https://github.com/typicode/husky/issues/580)
- [pnpm + Git Worktrees official guidance](https://pnpm.io/11.x/git-worktrees)
- Dave Schumaker — Vite/Vitest break with `node_modules` symlinks
- `docs/conventions/implementation-discipline.md`
- `docs/conventions/operating-contract.md`
