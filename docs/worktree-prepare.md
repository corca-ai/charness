# Worktree Prepare, Doctor, and Audit

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

`charness worktree` is the structural answer to "agent created a git worktree, hooks went silent, node_modules was never installed" and to "eval tools created dozens of throwaway worktrees and never cleaned up."

Subcommands, flags, and exits live in [cli-reference](./cli-reference.md) and the argparse of each command. Lifetime identity lives in [worktree_lifetime.py](../scripts/worktree/worktree_lifetime.py). Canonical doctor checks live in [worktree_doctor_checks.py](../scripts/worktree/worktree_doctor_checks.py). Do not recopy those catalogs here.

## Why this exists

Two silent-hook-skip failure modes: lefthook's `.git/hooks/` shim hardcodes the install-time worktree path, and husky's `.husky/_/` is generated per worktree. The `lefthook_shim` and `husky_dir` canonical checks hold both; charness never symlinks `node_modules` (Vite/Vitest resolution breaks). Superseded analysis: [worktree-prepare-doctor.md](../charness-artifacts/spec/worktree-prepare-doctor.md) (shipped commands emit one YAML document, not `--json`).

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

charness worktree audit                          # classify primary/active/prunable/stale
charness worktree audit --doctor                 # also surface readiness failures
charness worktree audit --prune                  # reclaim expired ephemerals; prune missing dirs

# After a local merge (dry-run without --yes):
charness worktree cleanup --path ../feature-worktree --delete-merged-branch --yes
```

## When to run `create`

Use `charness worktree create --path <path> --branch <branch> --base <ref>` instead of raw `git worktree add` for an isolated feature, spec, eval, or review slice: it creates the worktree, runs `worktree doctor` on it, and returns the exact next action when readiness is missing. `--prepare` runs the repo-declared setup immediately; without it a readiness failure is a warning with a next action, keeping installation under operator control.

## When to run `audit`

Run `charness worktree audit` to read the registry. `--doctor` adds readiness. `--prune` reclaims expired ephemerals, idle unlabeled throwaways, and missing metadata. Unlabeled feature paths still need `cleanup --yes`.

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

Manifest field identity, skip coverage, and dependency-reuse linking live in the [schema](../integrations/worktree/manifest.schema.json), [worktree_prepare_lib.py](../scripts/worktree/worktree_prepare_lib.py) (`_prepare_coverage`), and [worktree_dependency_reuse.py](../scripts/worktree/worktree_dependency_reuse.py). `argv` lists use block-style YAML. `prepare.commands` are worktree setup, not lefthook hook commands; consumer lefthook entries follow the [hook failure visibility contract](../skills/public/setup/references/hook-failure-visibility.md).

## Recommended consumer setups

- **pnpm monorepo:** pnpm's bare repo + `enableGlobalVirtualStore: true`; worktrees share the global store, `node_modules` is symlinks only, and `pnpm install` is near-instant ([pnpm guidance](https://pnpm.io/11.x/git-worktrees)).
- **npm or yarn:** prepare commands typically `npm ci && npx husky install` or `yarn install --immutable && yarn lefthook install`; declare [dependency reuse](../scripts/worktree/worktree_dependency_reuse.py) so later worktrees link the parent's install.
- **CoW filesystems (APFS, Btrfs, ZFS):** reuse takes the reflink path.

## Wiring with mutate-phase skills

`spec` and `hitl` bootstrap probe `charness worktree doctor` non-fatally before mutating repo content and surface the next action on non-pass. Public skills never auto-run prepare; `task run` does, as its documented default.

## Limitations

- The lefthook shim probe is a substring match on `lefthook`; a codegen rewrite upstream may need an update.
- Monorepo `node_modules` plurality is a manifest concern: charness schedules the commands you declare, and dependency reuse links one directory keyed by one lockfile.
