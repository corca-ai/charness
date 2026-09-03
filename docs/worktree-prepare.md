# Worktree Prepare, Doctor, and Audit

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

`charness worktree` is the structural answer to "agent created a git worktree, hooks went silent, and node_modules was never installed" — and to "eval/bench tools created dozens of throwaway worktrees and never cleaned up."

Six subcommands keep mutate-phase work honest:

- `charness worktree create` / `charness worktree add` — wraps `git worktree add`, then runs readiness doctor; optional `--prepare` runs the adapter-declared setup immediately.
- `charness worktree exec` — runs one command in an existing linked worktree with Python, pytest, coverage, and temporary output routed to an external runtime root.
- `charness worktree doctor` — fast, read-only health probe of a single worktree.
- `charness worktree prepare` — runs the consumer repo's adapter-declared prepare commands and re-validates.
- `charness worktree audit` — surveys every worktree registered to the repository and classifies primary/active/prunable/stale. Optional `--doctor` adds readiness summaries for existing worktrees; optional `--prune` drops git metadata for missing worktrees.
- `charness worktree cleanup` — dry-runs safe teardown for a registered feature worktree, then removes it with `--yes`; optional branch deletion requires local containment proof.

`create`, `audit`, and `cleanup` operate from the repository at `--repo-root`. `doctor` and `prepare` operate on the worktree at `--repo-root`.

## Why this exists

Two silent-hook-skip failure modes: lefthook's `.git/hooks/` shim hardcodes the install-time worktree path, and husky's `.husky/_/` is generated per worktree. The `lefthook_shim` and `husky_dir` canonical checks below hold both; charness never symlinks `node_modules` (Vite/Vitest resolution breaks). Analysis: [worktree-prepare-doctor.md](../charness-artifacts/spec/worktree-prepare-doctor.md).

## Quickstart

In a consumer repo that uses `git worktree add` plus a Node hook manager:

```bash
# One-time: seed a starter manifest and edit it for your package manager / hooks.
python3 "$CHARNESS_REPO/skills/public/setup/scripts/seed_worktree_adapter.py" --repo-root .

# Or copy from the example and edit:
cp "$CHARNESS_REPO/integrations/worktree/adapter.example.yaml" .agents/worktree-adapter.yaml

# Create a fresh worktree through Charness so readiness is checked immediately:
charness worktree create --path ../feature-worktree --branch feature-worktree --base main
charness worktree create --path ../feature-worktree --branch feature-worktree --base main --prepare
charness worktree add --path ../feature-worktree --branch feature-worktree --base main

# If a worktree was created raw or readiness changes later:
charness worktree doctor          # read-only probe
charness worktree prepare         # runs adapter prepare, re-validates
charness worktree prepare --force # run prepare even when doctor already passes

# Run ordinary commands with runtime output kept outside the worktree:
charness worktree exec --repo-root ../feature-worktree -- pytest -q

# Periodically (or before disk pressure builds):
charness worktree audit                          # classify primary/active/prunable/stale
charness worktree audit --doctor                 # also surface readiness failures
charness worktree audit --prune                  # also run `git worktree prune`
charness worktree audit --stale-days 30          # custom stale threshold, YAML output

# After a feature worktree has been merged locally:
charness worktree cleanup --path ../feature-worktree --delete-merged-branch
charness worktree cleanup --path ../feature-worktree --delete-merged-branch --yes
```

Management commands emit a single machine-readable YAML document on stdout.
`worktree exec` forwards the child command's output and only emits YAML for its
own preflight refusal. `doctor` and `prepare` exit 0 only when status is `pass`.
`create` exits 0 on `pass`, 1 on `warn` (created but readiness still needs
preparation), and 2 on `fail`. `audit` exits 0 on `pass`, 1 on `warn` (prunable,
stale, or readiness failures present), 2 on `fail`.

## When to run `create`

Run `charness worktree create --path <path> --branch <branch> --base <ref>` instead of raw `git worktree add` when an agent or operator is starting an isolated feature, spec, eval, or review slice. The command creates the worktree, runs `worktree doctor` against the new checkout, and returns the exact next action when the adapter reports missing dependencies or hook readiness.

Use `--prepare` when the operator wants Charness to run the repo-declared setup immediately after creation. Without `--prepare`, a readiness failure is a warning with a next action; this keeps dependency installation under operator control while still making the missing step visible at creation time.

## When to run `audit`

Run `charness worktree audit` when:

- A repo has been used for eval/bench/agent runs that call `git worktree add` to set up sandboxes. Those tools often skip cleanup; `audit` surfaces the residue.
- `git worktree list` output gets long enough that activity is hard to read.
- Disk pressure builds in `~/.cache` or `/tmp` and you want to confirm whether stale worktrees are contributing.

`audit --doctor` runs the same read-only readiness probe that `doctor` runs for each existing registered worktree, so active-but-unprepared worktrees are visible before verification fails. `audit` never deletes worktree directories on its own. `--prune` only invokes `git worktree prune`, which drops git metadata for worktrees whose directory is already gone. Use `git worktree remove --force <path>` to remove a still-existing stale worktree manually.

## When to run `cleanup`

Run `charness worktree cleanup --path <worktree>` after the feature worktree has been merged into the local base you trust. Cleanup refuses the primary worktree, refuses dirty targets unless `--force` is passed, and defaults to dry-run. `--delete-merged-branch` deletes the local branch only when the branch is contained in `--branch-base` (default `HEAD`), then uses `git branch -D` to avoid Git's upstream-aware `-d` refusal when the branch is merged locally but the base has not been pushed yet.

## Manifest contract

The manifest lives at [.agents/worktree-adapter.yaml](../.agents/worktree-adapter.yaml) in the consumer repo. Schema is at [integrations/worktree/manifest.schema.json](../integrations/worktree/manifest.schema.json) and the canonical example is [integrations/worktree/adapter.example.yaml](../integrations/worktree/adapter.example.yaml).

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

- `argv` lists must use **block-style YAML**. The repo-local YAML loader does not parse inline `[a, b]` arrays.
- `prepare.skip_if_doctor_passes` defaults to `false`. Set it to `true` only when passing manifest doctor checks explicitly cover every declared prepare command; pass `--force` to bypass an established skip.
- `doctor.checks` extends the canonical baseline. Each check is an `argv` invocation with optional `expect_exit_code` (default 0), `next_action_hint` surfaced on failure, and `covers`, a list of prepare command ids whose readiness the passing check establishes.
- A skip is licensed only by the manifest's `doctor.checks[].covers` -> `prepare.commands[].id` relation, established when every prepare command has a unique id covered by a check that passed (`_prepare_coverage` in [worktree_doctor_lib.py](../scripts/worktree/worktree_doctor_lib.py)); the prepare payload reports it under `coverage`.
- `doctor.disable_canonical_checks` opts out of a canonical check by id (`git_common_dir`, `hooks_path`, `lefthook_shim`, `husky_dir`). Use only when you genuinely do not use that hook surface.
- `prepare.commands` are worktree setup commands, not lefthook hook commands. For consumer lefthook `pre-commit`/`pre-push` entries, apply the [hook failure visibility contract](../skills/public/setup/references/hook-failure-visibility.md): declare `fail_text`, retain a stable failure log for long gates, and avoid output-filter pipelines.

## Canonical doctor checks

These run regardless of the manifest:

| id | What it checks | Failure means |
| --- | --- | --- |
| `git_common_dir` | `git rev-parse --git-common-dir` resolves. | Path is not a git checkout. |
| `hooks_path` | If `core.hooksPath` is set, the resolved directory exists in this worktree. | Hook manager state is missing for this worktree. |
| `lefthook_shim` | If `pre-commit` shim references lefthook, then `node_modules/lefthook-*/bin/lefthook` or PATH `lefthook` resolves. | Lefthook shim will silently exit 0 — hooks are dead. |
| `husky_dir` | If `core.hooksPath` points at a husky `_/` directory, that directory exists. | Husky prepare step has not run in this worktree. |

Checks return `pass`, `fail`, or `skipped` (precondition not met — e.g., no `core.hooksPath` set).

## Recommended consumer setups

- **pnpm monorepo:** the cleanest worktree story available today is pnpm's bare repo + `enableGlobalVirtualStore: true`. Worktrees share the global content-addressable store, each worktree's `node_modules` is symlinks only, and `pnpm install` in a new worktree is near-instant. See [pnpm's official guidance](https://pnpm.io/11.x/git-worktrees).
- **npm or yarn:** prepare commands typically `npm ci && npx husky install` or `yarn install --immutable && yarn lefthook install`. Be aware that file count is the bottleneck, not dependency download.
- **CoW filesystems (APFS, Btrfs, ZFS):** copy-on-write `cp -c -R node_modules ../new-worktree/node_modules` is fast and safe.

## Wiring with mutate-phase skills

`spec`, `impl`, and `hitl` bootstrap probe `charness worktree doctor` non-fatally before mutating repo content. On non-pass status, the recommended next action is surfaced; the operator decides whether to run `charness worktree prepare`. charness never auto-runs prepare from inside a public skill.

## Limitations

- The lefthook shim probe is heuristic (substring match on `lefthook`). If lefthook upstream rewrites its codegen, the heuristic may need an update.
- Multi-package monorepo workspace `node_modules` plurality is a manifest concern; charness only schedules the commands you declare.
- Consumer repos that want copy-on-write share that responsibility through `prepare.commands`.
