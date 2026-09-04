# Worktree Prepare, Doctor, and Audit

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

`charness worktree` is the structural answer to "agent created a git worktree, hooks went silent, node_modules was never installed" and to "eval tools created dozens of throwaway worktrees and never cleaned up."

Six subcommands keep mutate-phase work honest:

- `charness worktree create` / `add` — wraps `git worktree add`, then runs readiness doctor; `--prepare` runs the adapter-declared setup immediately.
- `charness worktree exec` — runs one command in a linked worktree with Python, pytest, coverage, and temporary output routed to an external runtime root.
- `charness worktree doctor` — fast, read-only health probe of one worktree.
- `charness worktree prepare` — runs the adapter-declared prepare commands and re-validates.
- `charness worktree audit` — classifies every registered worktree as primary/active/prunable/stale; `--doctor` adds readiness, `--prune` drops git metadata for missing directories.
- `charness worktree cleanup` — dry-runs teardown of a feature worktree, removes it with `--yes`; branch deletion requires local containment proof.

`create`, `audit`, and `cleanup` take the repository as `--repo-root`; `doctor` and `prepare` take the worktree.

## Why this exists

Two silent-hook-skip failure modes: lefthook's `.git/hooks/` shim hardcodes the install-time worktree path, and husky's `.husky/_/` is generated per worktree. The `lefthook_shim` and `husky_dir` canonical checks hold both; charness never symlinks `node_modules` (Vite/Vitest resolution breaks). Analysis: [worktree-prepare-doctor.md](../charness-artifacts/spec/worktree-prepare-doctor.md).

## Quickstart

In a consumer repo that uses `git worktree add` plus a Node hook manager:

```bash
# One-time: seed a starter manifest (or copy integrations/worktree/adapter.example.yaml).
python3 "$CHARNESS_REPO/skills/public/setup/scripts/seed_worktree_adapter.py" --repo-root .

# Create a worktree with readiness checked immediately (--prepare runs the adapter setup):
charness worktree create --path ../feature-worktree --branch feature-worktree --base main --prepare
charness worktree add --path ../feature-worktree --branch feature-worktree --base main

# Raw worktree, or readiness changed later:
charness worktree doctor              # read-only probe
charness worktree prepare [--force]   # adapter prepare, re-validates

# Ordinary commands with runtime output kept outside the worktree:
charness worktree exec --repo-root ../feature-worktree -- pytest -q

# Periodically:
charness worktree audit                          # classify primary/active/prunable/stale
charness worktree audit --doctor                 # also surface readiness failures
charness worktree audit --prune --stale-days 30  # also `git worktree prune`; custom threshold

# After a local merge (dry-run without --yes):
charness worktree cleanup --path ../feature-worktree --delete-merged-branch --yes
```

Management commands emit one YAML document on stdout; `worktree exec` forwards
the child's output and emits YAML only for its own preflight refusal. `doctor`
and `prepare` exit 0 only on `pass`. `create` exits 0 on `pass`, 1 on `warn`
(created, readiness still needs preparation), 2 on `fail`; `audit` exits 1 on
`warn` (prunable, stale, or readiness failures), 2 on `fail`.

## When to run `create`

Use `charness worktree create --path <path> --branch <branch> --base <ref>` instead of raw `git worktree add` for an isolated feature, spec, eval, or review slice: it creates the worktree, runs `worktree doctor` on it, and returns the exact next action when readiness is missing. `--prepare` runs the repo-declared setup immediately; without it a readiness failure is a warning with a next action, keeping installation under operator control.

## When to run `audit`

Run `charness worktree audit` when eval/bench/agent runs have left `git worktree add` residue, when `git worktree list` is too long to read, or when disk pressure builds under `~/.cache` or `/tmp`. `audit --doctor` runs the read-only readiness probe on each registered worktree. `audit` never deletes directories; `--prune` only runs `git worktree prune` for directories already gone. Remove a still-existing stale worktree with `git worktree remove --force <path>`.

## When to run `cleanup`

Run `charness worktree cleanup --path <worktree>` after the worktree is merged into the local base you trust. It refuses the primary worktree, refuses dirty targets without `--force`, and defaults to dry-run. `--delete-merged-branch` deletes the local branch only when `--branch-base` (default `HEAD`) contains it, using `git branch -D` because Git's upstream-aware `-d` refuses a branch whose base was never pushed.

## Manifest contract

The consumer repo owns [.agents/worktree-adapter.yaml](../.agents/worktree-adapter.yaml); the [schema](../integrations/worktree/manifest.schema.json) and the [canonical example](../integrations/worktree/adapter.example.yaml) live under `integrations/worktree/`.

Minimum useful manifest:

```yaml
version: 1
repo: my-repo
language: en
prepare:
  commands:
    - id: install-deps
      argv:
        - pnpm
        - install
        - --frozen-lockfile
    - id: install-hooks
      argv:
        - pnpm
        - exec
        - lefthook
        - install
```

Notes:

- `argv` lists must use **block-style YAML**; the repo-local loader does not parse inline `[a, b]` arrays.
- `prepare.skip_if_doctor_passes` defaults to `false`; `--force` bypasses an established skip.
- `doctor.checks` extends the canonical baseline: each is an `argv` invocation with optional `expect_exit_code` (default 0), `next_action_hint` surfaced on failure, and `covers`, the prepare command ids a pass establishes.
- A skip is licensed only by that `doctor.checks[].covers` -> `prepare.commands[].id` relation, established when every prepare command has a unique id covered by a passing check (`_prepare_coverage` in [worktree_doctor_lib.py](../scripts/worktree/worktree_doctor_lib.py)); the payload reports it under `coverage`.
- `prepare.dependency_reuse` (optional) names the install command (`command_id`), the lockfile, and the installed directory that [dependency reuse](#dependency-reuse) may link in place of running that command.
- `doctor.disable_canonical_checks` opts out of a canonical check by id (`git_common_dir`, `hooks_path`, `lefthook_shim`, `husky_dir`). Use only when you genuinely do not use that hook surface.
- `prepare.commands` are worktree setup commands, not lefthook hook commands. For consumer lefthook `pre-commit`/`pre-push` entries, apply the [hook failure visibility contract](../skills/public/setup/references/hook-failure-visibility.md): declare `fail_text`, retain a stable failure log for long gates, and avoid output-filter pipelines.

## Dependency reuse

Without copy-on-write, every fresh worktree paid a full install before bounded work started ([#792](https://github.com/corca-ai/charness/issues/792)). With `prepare.dependency_reuse` declared, prepare (so `create --prepare` and every `task run` lane) links an installed tree before the install command: first the parent tree when its lockfile digest matches, then the runtime cache `worktree-deps/` keyed by that digest and seeded whenever a fresh install had to run. `cp --reflink=always` is tried, then `cp -al`; when neither holds the install command runs as before. The payload's `dependency_reuse` key records `strategy`, `origin`, `source`, `reason`, and `cache_seed`. `--no-dependency-reuse` disables linking (a doctor-licensed skip still needs `--force`); `--force` alone does not disable reuse, because reuse is prepare. Hard links share inodes between the parent, the cache entry, and every worktree linked from either: package managers replace files, so installs in a lane leave the others intact, but an in-place edit under the linked directory reaches all of them. Recovery: delete the cache entry, prepare with `--no-dependency-reuse`. Declaring the field accepts that trade; the setup seeder emits it commented out, and pnpm users should use its global virtual store instead ([module docstring](../scripts/worktree/worktree_dependency_reuse.py)).

## Canonical doctor checks

These run regardless of the manifest:

| id | What it checks | Failure means |
| --- | --- | --- |
| `git_common_dir` | `git rev-parse --git-common-dir` resolves. | Path is not a git checkout. |
| `hooks_path` | If `core.hooksPath` is set, the resolved directory exists in this worktree. | Hook manager state is missing for this worktree. |
| `lefthook_shim` | If `pre-commit` shim references lefthook, then `node_modules/lefthook-*/bin/lefthook` or PATH `lefthook` resolves. | Lefthook shim will silently exit 0 — hooks are dead. |
| `husky_dir` | If `core.hooksPath` points at a husky `_/` directory, that directory exists. | Husky prepare step has not run in this worktree. |

Checks return `pass`, `fail`, or `skipped` (precondition not met).

## Recommended consumer setups

- **pnpm monorepo:** pnpm's bare repo + `enableGlobalVirtualStore: true`; worktrees share the global store, `node_modules` is symlinks only, and `pnpm install` is near-instant ([pnpm guidance](https://pnpm.io/11.x/git-worktrees)).
- **npm or yarn:** prepare commands typically `npm ci && npx husky install` or `yarn install --immutable && yarn lefthook install`. File count is the bottleneck; declare [dependency reuse](#dependency-reuse) so later worktrees link the parent's install.
- **CoW filesystems (APFS, Btrfs, ZFS):** dependency reuse takes the reflink path automatically.

## Wiring with mutate-phase skills

`spec`, `impl`, and `hitl` bootstrap probe `charness worktree doctor` non-fatally before mutating repo content and surface the next action on non-pass; the operator decides whether to run `charness worktree prepare`. Public skills never auto-run prepare; `task run` does, as its documented default.

## Limitations

- The lefthook shim probe is a substring match on `lefthook`; a codegen rewrite upstream may need an update.
- Monorepo `node_modules` plurality is a manifest concern: charness schedules the commands you declare, and dependency reuse links one directory keyed by one lockfile.
