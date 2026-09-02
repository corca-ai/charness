<!-- GENERATED: do not edit. Regenerate via `python3 scripts/gates_support/render_cli_reference.py --repo-root .` -->

# CLI Reference

> Status: generated
> Source of truth: `charness` parser and command-doc contract
> Last verified: 2026-09-02

This file is generated from `./charness --help` and subcommand help output in the current checkout.
Operational command payloads, including structured command failures, are emitted as a single YAML document on stdout; progress and unstructured fatal errors use stderr. Default operational responses are compact summaries: aggregate tool operations report counts and attention tool ids, not every tool record. This replaces the former aggregate `results` payload: automation that consumes individual tool records must request `--detail`. Commands with aggregated host or tool diagnostics expose the full evidence only through `--detail`, which still emits one YAML document.
Task runs persist one atomic typed result in the external runtime; task status reads exactly that store. Human-readable summaries print the affordance line with the `NEXT:` prefix.
Regenerate it with `python3 scripts/gates_support/render_cli_reference.py --repo-root . --output docs/cli-reference.md`.

## `charness`

```text
usage: charness [-h]
                {init,update,doctor,version,uninstall,reset,task,catalog,capability,goal,tool,worktree}
                ...

Thin charness CLI for managed local install, capability resolution, and
external tool install/update/doctor flows.

positional arguments:
  {init,update,doctor,version,uninstall,reset,task,catalog,capability,goal,tool,worktree}
    init                Bootstrap or refresh the managed local install
                        surface, cloning the managed checkout first when it is
                        missing.
    update              Refresh the installed surface, pulling the managed
                        checkout first by default.
    doctor              Inspect the managed install surface and host-facing
                        wrappers.
    version             Report the current charness version and recorded
                        install provenance.
    uninstall           Remove the managed local install surface.
    reset               Remove host plugin state for Codex and Claude while
                        preserving the managed checkout and CLI.
    task                Run or inspect a bounded task lane.
    catalog             Inspect capability inventory, packaged consumer-
                        validator adoption, or stale skill paths.
    capability          Resolve repo-local logical capabilities through
                        `<repo-root>/.charness/local/capability.json` and
                        inspect provider readiness.
    goal                Inspect and resume issue-native Goal Runs without
                        local goal-file state.
    tool                Inspect, install, update, or sync external tool
                        integrations that charness-managed skills depend on.
    worktree            Create, inspect, prepare, and clean up git worktrees
                        so mutate-phase work runs against installed
                        dependencies and live hooks.

options:
  -h, --help            show this help message and exit
```

## `charness init`

```text
usage: charness init [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                     [--target-repo-root TARGET_REPO_ROOT]
                     [--repo-url REPO_URL] [--plugin-root PLUGIN_ROOT]
                     [--codex-marketplace-path CODEX_MARKETPLACE_PATH]
                     [--claude-wrapper-path CLAUDE_WRAPPER_PATH]
                     [--cli-path CLI_PATH] [--skip-cli-install]
                     [--skip-claude-wrapper] [--detail]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit existing source checkout instead of
                        the managed default checkout.
  --target-repo-root TARGET_REPO_ROOT
                        Optional repo to inspect for post-install charness
                        onboarding. Defaults to the current working directory
                        for init/doctor; update inspects only when this is
                        explicit.
  --repo-url REPO_URL
  --plugin-root PLUGIN_ROOT
  --codex-marketplace-path CODEX_MARKETPLACE_PATH
  --claude-wrapper-path CLAUDE_WRAPPER_PATH
  --cli-path CLI_PATH
  --skip-cli-install
  --skip-claude-wrapper
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
```

## `charness update`

```text
usage: charness update [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                       [--target-repo-root TARGET_REPO_ROOT]
                       [--repo-url REPO_URL] [--plugin-root PLUGIN_ROOT]
                       [--codex-marketplace-path CODEX_MARKETPLACE_PATH]
                       [--claude-wrapper-path CLAUDE_WRAPPER_PATH]
                       [--cli-path CLI_PATH] [--skip-cli-install]
                       [--skip-claude-wrapper] [--detail] [--no-pull]
                       [--skip-codex-cache-refresh]
                       [{all}]

positional arguments:
  {all}                 Also run `charness tool update` for all tracked
                        external integrations after refreshing the charness
                        install surface itself.

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit existing source checkout instead of
                        the managed default checkout.
  --target-repo-root TARGET_REPO_ROOT
                        Optional repo to inspect for post-install charness
                        onboarding. Defaults to the current working directory
                        for init/doctor; update inspects only when this is
                        explicit.
  --repo-url REPO_URL
  --plugin-root PLUGIN_ROOT
  --codex-marketplace-path CODEX_MARKETPLACE_PATH
  --claude-wrapper-path CLAUDE_WRAPPER_PATH
  --cli-path CLI_PATH
  --skip-cli-install
  --skip-claude-wrapper
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
  --no-pull             Skip the default `git pull --ff-only` when the managed
                        checkout already contains the exact source you want.
  --skip-codex-cache-refresh
                        Do not call Codex app-server `plugin/install` to
                        refresh the enabled local plugin cache after updating
                        the source plugin root.
```

## `charness doctor`

```text
usage: charness doctor [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                       [--target-repo-root TARGET_REPO_ROOT]
                       [--plugin-root PLUGIN_ROOT]
                       [--codex-marketplace-path CODEX_MARKETPLACE_PATH]
                       [--claude-wrapper-path CLAUDE_WRAPPER_PATH]
                       [--cli-path CLI_PATH] [--next-action] [--write-state]
                       [--detail]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Inspect an explicit source checkout instead of the
                        managed default checkout.
  --target-repo-root TARGET_REPO_ROOT
                        Optional repo to inspect for charness onboarding.
                        Defaults to the current working directory.
  --plugin-root PLUGIN_ROOT
  --codex-marketplace-path CODEX_MARKETPLACE_PATH
  --claude-wrapper-path CLAUDE_WRAPPER_PATH
  --cli-path CLI_PATH
  --next-action         Print only the current primary next action message.
  --write-state         Persist the current doctor snapshot to the machine-
                        local charness state directory for later proof
                        comparison.
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
```

## `charness version`

```text
usage: charness version [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                        [--cli-path CLI_PATH] [--verbose] [--check]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Inspect an explicit source checkout instead of the
                        managed default checkout.
  --cli-path CLI_PATH
  --verbose
  --check               Refresh the cached latest-release check now instead of
                        only showing recorded state.
```

## `charness uninstall`

```text
usage: charness uninstall [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                          [--plugin-root PLUGIN_ROOT]
                          [--codex-marketplace-path CODEX_MARKETPLACE_PATH]
                          [--claude-wrapper-path CLAUDE_WRAPPER_PATH]
                          [--cli-path CLI_PATH] [--delete-checkout]
                          [--delete-cli]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit checkout path when `--delete-checkout`
                        is set.
  --plugin-root PLUGIN_ROOT
  --codex-marketplace-path CODEX_MARKETPLACE_PATH
  --claude-wrapper-path CLAUDE_WRAPPER_PATH
  --cli-path CLI_PATH
  --delete-checkout
  --delete-cli
```

## `charness reset`

```text
usage: charness reset [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                      [--plugin-root PLUGIN_ROOT]
                      [--codex-marketplace-path CODEX_MARKETPLACE_PATH]
                      [--claude-wrapper-path CLAUDE_WRAPPER_PATH]
                      [--cli-path CLI_PATH]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit checkout path when removing host
                        plugin state.
  --plugin-root PLUGIN_ROOT
  --codex-marketplace-path CODEX_MARKETPLACE_PATH
  --claude-wrapper-path CLAUDE_WRAPPER_PATH
  --cli-path CLI_PATH
```

## `charness task`

```text
usage: charness task [-h] {status,run} ...

positional arguments:
  {status,run}
    status      Show one external task-run result, or list all task-run
                results.
    run         Run one independently delegable Codex lane in a clean named
                worktree and emit a compact receipt.

options:
  -h, --help    show this help message and exit
```

## `charness task status`

```text
usage: charness task status [-h] [--repo-root REPO_ROOT] [task_id]

positional arguments:
  task_id

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Parent repo whose external task-run runtime is read.
```

## `charness task run`

```text
usage: charness task run [-h] [--repo-root REPO_ROOT] [--lane LANE]
                         [--path PATH] [--branch BRANCH] [--base BASE] --scope
                         SCOPE (--prompt PROMPT | --prompt-file PROMPT_FILE)
                         --effort EFFORT [--task-id TASK_ID] [--prepare]
                         [--require-change] [--skip-prepare]
                         [--allow-no-change]
                         [--timeout-seconds TIMEOUT_SECONDS] [--dry-run]

Run one independently delegable lane: shorthand derives a named branch,
external worktree, task id, and HEAD base; the explicit form remains available
for diagnostics. The parent worktree must be clean; the parent orchestrator
owns parallel fan-out and integration.

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Clean parent repo from which the linked worktree is
                        created. Defaults to the current working directory.
  --lane LANE           Safe lane id; derives the task id, task/<id> branch,
                        external worktree, and HEAD base.
  --path PATH           New linked worktree path outside the parent repo
                        (explicit form).
  --branch BRANCH       Named local branch for the new worktree (explicit
                        form).
  --base BASE           Commit/ref from which the named worktree is created
                        (explicit form).
  --scope SCOPE         Repository-relative candidate path or quoted glob;
                        globs must match before launch and retain the pattern
                        for new matching paths.
  --prompt PROMPT       Implementation instructions passed to `codex exec`.
  --prompt-file PROMPT_FILE
                        Read implementation instructions from this file.
  --effort EFFORT       Orchestrator-selected Codex reasoning effort: medium,
                        xhigh, or max.
  --task-id TASK_ID     Optional receipt/log identifier for explicit runs;
                        shorthand derives it from --lane.
  --prepare             Run the worktree adapter prepare step before Codex.
  --require-change      Fail unless the candidate changes at least one path.
  --skip-prepare        Shorthand diagnostic opt-out: skip the default
                        preparation step.
  --allow-no-change     Shorthand diagnostic opt-out: allow an unchanged
                        candidate.
  --timeout-seconds TIMEOUT_SECONDS
  --dry-run             Validate inputs and show the planned lane without
                        creating or running it.
```

## `charness catalog`

```text
usage: charness catalog [-h] {list,refresh,resolve-skill-path} ...

positional arguments:
  {list,refresh,resolve-skill-path}
    list                Read capability and packaged consumer-validator
                        inventory without writing artifacts.
    refresh             Write the canonical capability catalog current-pointer
                        artifacts.
    resolve-skill-path  Resolve a stale host-reported skill path after plugin
                        cache rotation.

options:
  -h, --help            show this help message and exit
```

## `charness catalog list`

```text
usage: charness catalog list [-h] --repo-root REPO_ROOT [--summary]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
  --summary             Project support/integration inventory while retaining
                        the validator catalog contract.
```

## `charness catalog refresh`

```text
usage: charness catalog refresh [-h] --repo-root REPO_ROOT

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
```

## `charness catalog resolve-skill-path`

```text
usage: charness catalog resolve-skill-path [-h] --repo-root REPO_ROOT
                                           --skill-id SKILL_ID --reported-path
                                           REPORTED_PATH [--home HOME]
                                           [--codex-home CODEX_HOME]
                                           [--marketplace MARKETPLACE]
                                           [--plugin PLUGIN]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
  --skill-id SKILL_ID
  --reported-path REPORTED_PATH
  --home HOME
  --codex-home CODEX_HOME
  --marketplace MARKETPLACE
  --plugin PLUGIN
```

## `charness capability`

```text
usage: charness capability [-h] {init,resolve,doctor,env,explain} ...

positional arguments:
  {init,resolve,doctor,env,explain}
    init                Scaffold repo-local capability config
                        (`.charness/local/capability.json` +
                        `.charness/capability.example.json`) and update
                        `.gitignore`.
    resolve             Resolve one logical capability for the current repo
                        into a profile and provider.
    doctor              Resolve one logical capability and inspect the
                        underlying provider state.
    env                 Emit shell exports that alias runtime env names from
                        non-secret source env names declared in the repo-local
                        capability config.
    explain             Explain which logical capabilities a public skill may
                        need and what the current repo adapter adds.

options:
  -h, --help            show this help message and exit
```

## `charness capability init`

```text
usage: charness capability init [-h] [--target-repo-root TARGET_REPO_ROOT]
                                [--force]

options:
  -h, --help            show this help message and exit
  --target-repo-root TARGET_REPO_ROOT
                        Scaffold capability config under this target repo.
                        Defaults to the current working directory.
  --force
```

## `charness capability resolve`

```text
usage: charness capability resolve [-h] [--repo-root REPO_ROOT]
                                   [--repo-url REPO_URL]
                                   [--target-repo-root TARGET_REPO_ROOT]
                                   logical_id

positional arguments:
  logical_id

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Use an explicit charness source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --target-repo-root TARGET_REPO_ROOT
                        Resolve repo-local capability config for this target
                        repo. Defaults to the current working directory.
```

## `charness capability doctor`

```text
usage: charness capability doctor [-h] [--repo-root REPO_ROOT]
                                  [--repo-url REPO_URL]
                                  [--target-repo-root TARGET_REPO_ROOT]
                                  logical_id

positional arguments:
  logical_id

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Use an explicit charness source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --target-repo-root TARGET_REPO_ROOT
                        Resolve repo-local capability config for this target
                        repo. Defaults to the current working directory.
```

## `charness capability env`

```text
usage: charness capability env [-h] [--repo-root REPO_ROOT]
                               [--repo-url REPO_URL]
                               [--target-repo-root TARGET_REPO_ROOT]
                               logical_id

positional arguments:
  logical_id

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Use an explicit charness source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --target-repo-root TARGET_REPO_ROOT
                        Resolve repo-local capability config for this target
                        repo. Defaults to the current working directory.
```

## `charness capability explain`

```text
usage: charness capability explain [-h] [--repo-root REPO_ROOT]
                                   [--repo-url REPO_URL]
                                   [--target-repo-root TARGET_REPO_ROOT]
                                   skill_id

positional arguments:
  skill_id

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Use an explicit charness source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --target-repo-root TARGET_REPO_ROOT
                        Inspect repo-local adapter context for this target
                        repo. Defaults to the current working directory.
```

## `charness goal`

```text
usage: charness goal [-h] {run} ...

positional arguments:
  {run}
    run       Read a provider-backed Goal Run and select its next executable
              child; no local artifact path is accepted.

options:
  -h, --help  show this help message and exit
```

## `charness goal run`

```text
usage: charness goal run [-h] [--repo-root REPO_ROOT] --objective OBJECTIVE
                         [--home-root HOME_ROOT] [--repo-url REPO_URL]
                         [--charness-checkout CHARNESS_CHECKOUT]

Resume a provider-backed Goal Run; no local artifact path is accepted.

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Target repository containing the Goal Run. Defaults to
                        the current working directory.
  --objective OBJECTIVE
                        Exact issue-native objective, for example `/goal #N`.
  --home-root HOME_ROOT
  --repo-url REPO_URL
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit Charness source checkout containing the
                        current Goal Run pickup helper. Defaults to this CLI
                        checkout or the managed checkout.
```

## `charness tool`

```text
usage: charness tool [-h] {doctor,repair,sync-support,install,update} ...

positional arguments:
  {doctor,repair,sync-support,install,update}
    doctor              Write machine-readable doctor state for one or more
                        external tools.
    repair              Run post-hoc repair actions for external tool runtime
                        drift, then refresh doctor state.
    sync-support        Refresh cache-backed support skill materialization for
                        one or more external tools.
    install             Attempt tool installation where the manifest allows
                        it, otherwise persist install guidance and doctor
                        state.
    update              Attempt manifest-declared external tool updates, then
                        refresh support skill materialization and doctor
                        state.

options:
  -h, --help            show this help message and exit
```

## `charness tool doctor`

```text
usage: charness tool doctor [-h] [--home-root HOME_ROOT]
                            [--repo-root REPO_ROOT] [--repo-url REPO_URL]
                            [--plugin-root PLUGIN_ROOT] [--detail]
                            [--no-write-locks]
                            [tool_ids ...]

positional arguments:
  tool_ids

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit existing source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --plugin-root PLUGIN_ROOT
                        Installed plugin root where upstream support skills
                        are materialized.
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
  --no-write-locks      Skip updating integrations/locks/*.json when you only
                        want a read-only probe.
```

## `charness tool repair`

```text
usage: charness tool repair [-h] [--home-root HOME_ROOT]
                            [--repo-root REPO_ROOT] [--repo-url REPO_URL]
                            [--plugin-root PLUGIN_ROOT] [--detail] [--execute]
                            [tool_ids ...]

Run repo-owned post-hoc repair actions for external tool runtime drift, then
refresh doctor state. For agent-browser this is mitigation only; invocation-
bound Chrome/profile teardown remains upstream/unproven.

positional arguments:
  tool_ids

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit existing source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --plugin-root PLUGIN_ROOT
                        Installed plugin root where upstream support skills
                        are materialized.
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
  --execute             Execute the repair. Defaults to a dry-run preview.
```

## `charness tool sync-support`

```text
usage: charness tool sync-support [-h] [--home-root HOME_ROOT]
                                  [--repo-root REPO_ROOT]
                                  [--repo-url REPO_URL]
                                  [--plugin-root PLUGIN_ROOT] [--detail]
                                  [--upstream-checkout UPSTREAM_CHECKOUT]
                                  [--dry-run]
                                  [tool_ids ...]

positional arguments:
  tool_ids

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit existing source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --plugin-root PLUGIN_ROOT
                        Installed plugin root where upstream support skills
                        are materialized.
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
  --upstream-checkout UPSTREAM_CHECKOUT
  --dry-run
```

## `charness tool install`

```text
usage: charness tool install [-h] [--home-root HOME_ROOT]
                             [--repo-root REPO_ROOT] [--repo-url REPO_URL]
                             [--plugin-root PLUGIN_ROOT] [--detail]
                             [--upstream-checkout UPSTREAM_CHECKOUT]
                             [--dry-run] [--skip-sync-support]
                             [--recommend-for-skill RECOMMEND_FOR_SKILL]
                             [--recommendation-role {runtime,validation}]
                             [--next-skill-id NEXT_SKILL_ID]
                             [tool_ids ...]

positional arguments:
  tool_ids

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit existing source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --plugin-root PLUGIN_ROOT
                        Installed plugin root where upstream support skills
                        are materialized.
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
  --upstream-checkout UPSTREAM_CHECKOUT
  --dry-run
  --skip-sync-support   Skip support skill rematerialization after install
                        guidance or execution.
  --recommend-for-skill RECOMMEND_FOR_SKILL
                        Install tools declared as supporting a public skill
                        instead of passing explicit tool ids.
  --recommendation-role {runtime,validation}
                        Install tools with a recommendation role, optionally
                        scoped by --next-skill-id.
  --next-skill-id NEXT_SKILL_ID
                        Public skill id used with --recommendation-role;
                        defaults to quality.
```

Examples

```bash
charness tool install --recommendation-role validation --next-skill-id quality
```

## `charness tool update`

```text
usage: charness tool update [-h] [--home-root HOME_ROOT]
                            [--repo-root REPO_ROOT] [--repo-url REPO_URL]
                            [--plugin-root PLUGIN_ROOT] [--detail]
                            [--upstream-checkout UPSTREAM_CHECKOUT]
                            [--dry-run] [--skip-sync-support]
                            [tool_ids ...]

positional arguments:
  tool_ids

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Use an explicit existing source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --plugin-root PLUGIN_ROOT
                        Installed plugin root where upstream support skills
                        are materialized.
  --detail              Emit the full diagnostic YAML payload instead of the
                        default compact operational summary.
  --upstream-checkout UPSTREAM_CHECKOUT
  --dry-run
  --skip-sync-support   Skip support skill rematerialization after update.
```

## `charness worktree`

```text
usage: charness worktree [-h]
                         {create,add,exec,doctor,prepare,audit,cleanup} ...

positional arguments:
  {create,add,exec,doctor,prepare,audit,cleanup}
    create              Create a git worktree, then run readiness doctor and
                        optional prepare.
    add                 Alias for `create`: wrap `git worktree add` with
                        readiness doctor and optional prepare.
    exec                Run one command in an isolated worktree with external
                        runtime caches.
    doctor              Probe worktree readiness (isolation, hooksPath,
                        lefthook shim resolution, husky directory, manifest
                        checks).
    prepare             Run the worktree adapter's prepare commands and re-
                        validate readiness.
    audit               Survey all worktrees registered to the repository and
                        classify primary/active/prunable/stale.
    cleanup             Safely remove a registered git worktree and optionally
                        delete its merged local branch.

options:
  -h, --help            show this help message and exit
```

## `charness worktree create`

```text
usage: charness worktree create [-h] [--repo-root REPO_ROOT] --path PATH
                                [--branch BRANCH] [--base BASE] [--detach]
                                [--prepare] [--dry-run] [--force]
                                [--home-root HOME_ROOT]
                                [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo root that the worktree should be created under.
                        Defaults to the current working directory.
  --path PATH           Path for the new git worktree.
  --branch BRANCH       Create a new local branch for the worktree.
  --base BASE           Base ref passed to `git worktree add` after the path.
  --detach              Create a detached-HEAD worktree.
  --prepare             Run readiness prepare after creation.
  --dry-run             Print the planned git command without creating the
                        worktree.
  --force               Pass --force to `git worktree add`.
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```

## `charness worktree add`

```text
usage: charness worktree add [-h] [--repo-root REPO_ROOT] --path PATH
                             [--branch BRANCH] [--base BASE] [--detach]
                             [--prepare] [--dry-run] [--force]
                             [--home-root HOME_ROOT]
                             [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo root that the worktree should be created under.
                        Defaults to the current working directory.
  --path PATH           Path for the new git worktree.
  --branch BRANCH       Create a new local branch for the worktree.
  --base BASE           Base ref passed to `git worktree add` after the path.
  --detach              Create a detached-HEAD worktree.
  --prepare             Run readiness prepare after creation.
  --dry-run             Print the planned git command without creating the
                        worktree.
  --force               Pass --force to `git worktree add`.
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```

## `charness worktree exec`

```text
usage: charness worktree exec [-h] [--repo-root REPO_ROOT] [--allow-main]
                              [--home-root HOME_ROOT]
                              [--charness-checkout CHARNESS_CHECKOUT]
                              ...

Run one command in an isolated worktree with external runtime caches.

positional arguments:
  command               Command after `--`.

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Worktree in which to run the command. Defaults to the
                        current working directory.
  --allow-main          Allow an intentional command in the primary worktree;
                        parent writes are then possible.
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```

## `charness worktree doctor`

```text
usage: charness worktree doctor [-h] [--repo-root REPO_ROOT]
                                [--require-isolation] [--home-root HOME_ROOT]
                                [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Worktree to inspect. Defaults to the current working
                        directory.
  --require-isolation   Fail unless this checkout is a linked worktree rather
                        than the main one. Pass it before handing a WRITE-
                        CAPABLE agent a checkout: without isolation that agent
                        shares the parent's tree and index, and a stray git op
                        lands in the parent's commit. Without the flag,
                        isolation is reported as a fact and never enforced.
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```

## `charness worktree prepare`

```text
usage: charness worktree prepare [-h] [--repo-root REPO_ROOT] [--force]
                                 [--home-root HOME_ROOT]
                                 [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Worktree to prepare. Defaults to the current working
                        directory.
  --force               Run prepare even if doctor already reports pass.
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```

## `charness worktree audit`

```text
usage: charness worktree audit [-h] [--repo-root REPO_ROOT]
                               [--stale-days STALE_DAYS] [--prune] [--doctor]
                               [--home-root HOME_ROOT]
                               [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo root whose worktree registry should be audited.
                        Defaults to the current working directory.
  --stale-days STALE_DAYS
                        Detached-HEAD worktrees older than this many days are
                        reported as stale (default: 14).
  --prune               After audit, run `git worktree prune` to drop metadata
                        for prunable worktrees.
  --doctor              Run readiness doctor for existing worktrees and
                        include per-worktree readiness summaries.
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```

## `charness worktree cleanup`

```text
usage: charness worktree cleanup [-h] [--repo-root REPO_ROOT] --path PATH
                                 [--delete-merged-branch]
                                 [--branch-base BRANCH_BASE] [--yes] [--force]
                                 [--home-root HOME_ROOT]
                                 [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo root whose worktree should be operated on.
                        Defaults to the current working directory.
  --path PATH           Registered worktree path to remove.
  --delete-merged-branch
                        Delete the local branch only after it is contained in
                        --branch-base.
  --branch-base BRANCH_BASE
                        Local ref that must contain the target branch before
                        branch deletion; defaults to HEAD.
  --yes                 Execute the planned cleanup. Defaults to dry-run.
  --force               Pass --force to git worktree remove for dirty targets.
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```
