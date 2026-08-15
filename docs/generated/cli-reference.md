<!-- GENERATED: do not edit. Regenerate via `python3 scripts/render_cli_reference.py --repo-root .` -->

# CLI Reference

This file is generated from `./charness --help` and subcommand help output in the current checkout.
Operational command payloads, including structured command failures, are emitted as a single YAML document on stdout; progress and unstructured fatal errors use stderr. Default operational responses are compact summaries: aggregate tool operations report counts and attention tool ids, not every tool record. This replaces the former aggregate `results` payload: automation that consumes individual tool records must request `--detail`. Commands with aggregated host or tool diagnostics expose the full evidence only through `--detail`, which still emits one YAML document.
Payloads that can name a follow-up carry it as an in-band affordance instead of relying on out-of-band knowledge: `next_step` is a single human-readable follow-up string on command payloads (task, tool, and worktree surfaces; on `charness task` it appears on success and on structured `rejected` failures alike), `next_steps` is a list of human-readable follow-up strings (tool doctor, `capability init`, gather advise), `host_next_steps` maps host ids to per-host status messages on runtime doctor/update output, and `next_action` is a structured object (`kind` plus context) on runtime doctor payloads and skill plan envelopes. Human-readable summaries print the affordance line with the `NEXT:` prefix. `charness task` also persists `next_step` into `.charness/tasks/<task-id>.json`, so the state file carries the same continuation affordance as the original response.
Regenerate it with `python3 scripts/render_cli_reference.py --repo-root . --output docs/generated/cli-reference.md`.

## `charness`

```text
usage: charness [-h]
                {init,update,doctor,version,uninstall,reset,task,catalog,capability,goal,tool,session-capture,worktree}
                ...

Thin charness CLI for managed local install, capability resolution, and
external tool install/update/doctor flows.

positional arguments:
  {init,update,doctor,version,uninstall,reset,task,catalog,capability,goal,tool,session-capture,worktree}
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
    catalog             Inspect or refresh deterministic installed capability
                        inventory and resolve stale skill paths.
    capability          Resolve repo-local logical capabilities through
                        `<repo-root>/.charness/local/capability.json` and
                        inspect provider readiness.
    goal                Run stable goal helper commands without embedding
                        versioned plugin cache paths.
    tool                Inspect, install, update, or sync external tool
                        integrations that charness-managed skills depend on.
    session-capture     Inspect and reconcile the SessionStart hook charness
                        installs into Claude/Codex for usage-episodes capture.
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
usage: charness task [-h] [--repo-root REPO_ROOT]
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

## `charness catalog`

```text
usage: charness catalog [-h] {list,refresh,resolve-skill-path} ...

positional arguments:
  {list,refresh,resolve-skill-path}
    list                Read installed public/support/synced/integration
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
  --summary             Emit compact hidden support/integration inventory.
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
usage: charness goal [-h] {check} ...

positional arguments:
  {check}
    check     Validate a Charness achieve goal artifact through the installed
              or source checkout helper.

options:
  -h, --help  show this help message and exit
```

## `charness goal check`

```text
usage: charness goal check [-h] [--repo-root REPO_ROOT]
                           [--goal-path GOAL_PATH] [--slug SLUG] [--date DATE]
                           [--pursue-ready] [--home-root HOME_ROOT]
                           [--repo-url REPO_URL]
                           [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo containing the goal artifact. Defaults to the
                        current working directory.
  --goal-path GOAL_PATH
  --slug SLUG
  --date DATE
  --pursue-ready
  --home-root HOME_ROOT
  --repo-url REPO_URL
  --charness-checkout CHARNESS_CHECKOUT
                        Explicit Charness source checkout containing the
                        achieve helper. Defaults to this CLI checkout or the
                        managed checkout.
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

## `charness session-capture`

```text
usage: charness session-capture [-h] {status,install,uninstall} ...

positional arguments:
  {status,install,uninstall}
    status              Report adapter intent vs actual host settings; exits 0
                        in sync, 1 on drift.
    install             Install the SessionStart hook entry for the requested
                        host(s) without running a full charness update.
    uninstall           Remove the charness-installed SessionStart hook entry
                        from the requested host(s).

options:
  -h, --help            show this help message and exit
```

## `charness session-capture status`

```text
usage: charness session-capture status [-h] [--home-root HOME_ROOT]
                                       [--repo-root REPO_ROOT]
                                       [--repo-url REPO_URL]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
                        Home root used to resolve host settings paths
                        (default: $HOME).
  --repo-root REPO_ROOT
                        Use an explicit charness source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
```

## `charness session-capture install`

```text
usage: charness session-capture install [-h] [--home-root HOME_ROOT]
                                        [--repo-root REPO_ROOT]
                                        [--repo-url REPO_URL]
                                        [--host {claude,codex}]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
                        Home root used to resolve host settings paths
                        (default: $HOME).
  --repo-root REPO_ROOT
                        Use an explicit charness source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --host {claude,codex}
                        Restrict the install to a single host; default
                        installs both.
```

## `charness session-capture uninstall`

```text
usage: charness session-capture uninstall [-h] [--home-root HOME_ROOT]
                                          [--repo-root REPO_ROOT]
                                          [--repo-url REPO_URL]
                                          [--host {claude,codex}]

options:
  -h, --help            show this help message and exit
  --home-root HOME_ROOT
                        Home root used to resolve host settings paths
                        (default: $HOME).
  --repo-root REPO_ROOT
                        Use an explicit charness source checkout instead of
                        the managed default checkout.
  --repo-url REPO_URL
  --host {claude,codex}
                        Restrict the uninstall to a single host; default
                        removes from both.
```

## `charness worktree`

```text
usage: charness worktree [-h] {create,add,doctor,prepare,audit,cleanup} ...

positional arguments:
  {create,add,doctor,prepare,audit,cleanup}
    create              Create a git worktree, then run readiness doctor and
                        optional prepare.
    add                 Alias for `create`: wrap `git worktree add` with
                        readiness doctor and optional prepare.
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
