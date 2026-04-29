# CLI Reference

This file is generated from `./charness --help` and subcommand help output in the current checkout.
Regenerate it with `python3 scripts/render_cli_reference.py --repo-root . --output docs/cli-reference.md`.

## `charness`

```text
usage: charness [-h]
                {init,update,doctor,version,uninstall,reset,task,capability,tool}
                ...

Thin charness CLI for managed local install, capability resolution, and
external tool install/update/doctor flows.

positional arguments:
  {init,update,doctor,version,uninstall,reset,task,capability,tool}
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
    capability          Resolve repo-local logical capabilities into machine-
                        local provider profiles and inspect provider
                        readiness.
    tool                Inspect, install, update, or sync external tool
                        integrations that charness-managed skills depend on.

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
                        Use an explicit checkout path when removing Claude
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

## `charness capability`

```text
usage: charness capability [-h] {init,resolve,doctor,env,explain} ...

positional arguments:
  {init,resolve,doctor,env,explain}
    init                Scaffold machine-local capability profile and repo
                        binding config files for first use.
    resolve             Resolve one logical capability for the current repo
                        into a profile and provider.
    doctor              Resolve one logical capability and inspect the
                        underlying provider state.
    env                 Emit shell exports that alias runtime env names from
                        machine-local source env names.
    explain             Explain which logical capabilities a public skill may
                        need and what the current repo adapter adds.

options:
  -h, --help            show this help message and exit
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
