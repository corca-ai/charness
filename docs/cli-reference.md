# CLI Reference

This file is generated from `./charness --help` and subcommand help output in the current checkout.
Regenerate it with `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md`.

## `charness`

```text
usage: charness [-h]
                {init,update,doctor,version,uninstall,reset,task,capability,tool,worktree}
                ...

Thin charness CLI for managed local install, capability resolution, and
external tool install/update/doctor flows.

positional arguments:
  {init,update,doctor,version,uninstall,reset,task,capability,tool,worktree}
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
    task                Claim, submit, abort, or inspect a repo-local agent
                        task envelope.
    capability          Resolve repo-local logical capabilities through
                        `<repo-root>/.charness/local/capability.json` and
                        inspect provider readiness.
    tool                Inspect, install, update, or sync external tool
                        integrations that charness-managed skills depend on.
    worktree            Inspect and prepare git worktrees so mutate-phase work
                        runs against installed dependencies and live hooks.

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
                     [--skip-claude-wrapper] [--json]

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
  --json
```

## `charness update`

```text
usage: charness update [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                       [--target-repo-root TARGET_REPO_ROOT]
                       [--repo-url REPO_URL] [--plugin-root PLUGIN_ROOT]
                       [--codex-marketplace-path CODEX_MARKETPLACE_PATH]
                       [--claude-wrapper-path CLAUDE_WRAPPER_PATH]
                       [--cli-path CLI_PATH] [--skip-cli-install]
                       [--skip-claude-wrapper] [--json] [--no-pull]
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
  --json
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
                       [--cli-path CLI_PATH] [--json | --next-action]
                       [--write-state]

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
  --json
  --next-action         Print only the current primary next action message.
  --write-state         Persist the current doctor snapshot to the machine-
                        local charness state directory for later proof
                        comparison.
```

## `charness version`

```text
usage: charness version [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                        [--cli-path CLI_PATH] [--json] [--verbose] [--check]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
  --repo-root REPO_ROOT
                        Inspect an explicit source checkout instead of the
                        managed default checkout.
  --cli-path CLI_PATH
  --json
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
                          [--delete-cli] [--json]

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
  --json
```

## `charness reset`

```text
usage: charness reset [-h] [--home-root HOME_ROOT] [--repo-root REPO_ROOT]
                      [--plugin-root PLUGIN_ROOT]
                      [--codex-marketplace-path CODEX_MARKETPLACE_PATH]
                      [--claude-wrapper-path CLAUDE_WRAPPER_PATH]
                      [--cli-path CLI_PATH] [--json]

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
  --json
```

## `charness task`

```text
usage: charness task [-h] [--repo-root REPO_ROOT] [--json]
                     {claim,submit,abort,status} ...

positional arguments:
  {claim,submit,abort,status}
    claim               Create a claimed task envelope unless another agent
                        already owns it.
    submit              Mark a claimed task as submitted with structured
                        result metadata.
    abort               Mark a claimed task as aborted with a required reason.
    status              Show one task envelope, or list all repo-local task
                        envelopes.

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo where .charness/tasks/*.json task state is
                        stored. Defaults to the current working directory.
  --json
```

## `charness task claim`

```text
usage: charness task claim [-h] [--agent AGENT] [--summary SUMMARY] task_id

positional arguments:
  task_id

options:
  -h, --help         show this help message and exit
  --agent AGENT      Agent identity recorded in the task. Defaults to
                     CHARNESS_AGENT_ID, CODEX_SESSION_ID, USER, then `agent`.
  --summary SUMMARY
```

## `charness task submit`

```text
usage: charness task submit [-h] [--summary SUMMARY] [--artifact ARTIFACTS]
                            task_id

positional arguments:
  task_id

options:
  -h, --help            show this help message and exit
  --summary SUMMARY
  --artifact ARTIFACTS
```

## `charness task abort`

```text
usage: charness task abort [-h] --reason REASON task_id

positional arguments:
  task_id

options:
  -h, --help       show this help message and exit
  --reason REASON
```

## `charness task status`

```text
usage: charness task status [-h] [task_id]

positional arguments:
  task_id

options:
  -h, --help  show this help message and exit
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
                                [--force] [--json]

options:
  -h, --help            show this help message and exit
  --target-repo-root TARGET_REPO_ROOT
                        Scaffold capability config under this target repo.
                        Defaults to the current working directory.
  --force
  --json
```

## `charness capability resolve`

```text
usage: charness capability resolve [-h] [--repo-root REPO_ROOT]
                                   [--repo-url REPO_URL]
                                   [--target-repo-root TARGET_REPO_ROOT]
                                   [--json]
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
  --json
```

## `charness capability doctor`

```text
usage: charness capability doctor [-h] [--repo-root REPO_ROOT]
                                  [--repo-url REPO_URL]
                                  [--target-repo-root TARGET_REPO_ROOT]
                                  [--json]
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
  --json
```

## `charness capability env`

```text
usage: charness capability env [-h] [--repo-root REPO_ROOT]
                               [--repo-url REPO_URL]
                               [--target-repo-root TARGET_REPO_ROOT] [--json]
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
  --json
```

## `charness capability explain`

```text
usage: charness capability explain [-h] [--repo-root REPO_ROOT]
                                   [--repo-url REPO_URL]
                                   [--target-repo-root TARGET_REPO_ROOT]
                                   [--json]
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
  --json
```

## `charness tool`

```text
usage: charness tool [-h] {doctor,sync-support,install,update} ...

positional arguments:
  {doctor,sync-support,install,update}
    doctor              Write machine-readable doctor state for one or more
                        external tools.
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
                            [--json] [--no-write-locks]
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
  --json
  --no-write-locks      Skip updating integrations/locks/*.json when you only
                        want a read-only probe.
```

## `charness tool sync-support`

```text
usage: charness tool sync-support [-h] [--home-root HOME_ROOT]
                                  [--repo-root REPO_ROOT]
                                  [--repo-url REPO_URL] [--json]
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
  --json
  --upstream-checkout UPSTREAM_CHECKOUT
  --dry-run
```

## `charness tool install`

```text
usage: charness tool install [-h] [--home-root HOME_ROOT]
                             [--repo-root REPO_ROOT] [--repo-url REPO_URL]
                             [--json] [--upstream-checkout UPSTREAM_CHECKOUT]
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
  --json
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
                            [--json] [--upstream-checkout UPSTREAM_CHECKOUT]
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
  --json
  --upstream-checkout UPSTREAM_CHECKOUT
  --dry-run
  --skip-sync-support   Skip support skill rematerialization after update.
```

## `charness worktree`

```text
usage: charness worktree [-h] {doctor,prepare,audit} ...

positional arguments:
  {doctor,prepare,audit}
    doctor              Probe worktree readiness (hooksPath, lefthook shim
                        resolution, husky directory, manifest checks).
    prepare             Run the worktree adapter's prepare commands and re-
                        validate readiness.
    audit               Survey all worktrees registered to the repository and
                        classify primary/active/prunable/stale.

options:
  -h, --help            show this help message and exit
```

## `charness worktree doctor`

```text
usage: charness worktree doctor [-h] [--repo-root REPO_ROOT] [--json]
                                [--home-root HOME_ROOT]
                                [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Worktree to inspect. Defaults to the current working
                        directory.
  --json
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
                                 [--json] [--home-root HOME_ROOT]
                                 [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Worktree to prepare. Defaults to the current working
                        directory.
  --force               Run prepare even if doctor already reports pass.
  --json
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
                               [--stale-days STALE_DAYS] [--prune] [--json]
                               [--home-root HOME_ROOT]
                               [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository to inspect. Defaults to the current working
                        directory.
  --stale-days STALE_DAYS
                        Detached-HEAD worktrees older than this many days are
                        reported as stale (default: 14).
  --prune               After audit, run `git worktree prune` to drop metadata
                        for prunable worktrees.
  --json
  --home-root HOME_ROOT
                        Home root used to locate the managed charness checkout
                        when the entrypoint is a PATH shim.
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit charness source checkout to load worktree
                        helpers from. Defaults to the embedded or managed
                        checkout.
```
