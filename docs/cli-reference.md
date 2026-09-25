<!-- GENERATED: do not edit. Regenerate via `python3 scripts/gates_support/render_cli_reference.py --repo-root .` -->

# CLI Reference

> Status: generated
> Source of truth: `charness` parser and command-doc contract
> Last verified: 2026-09-02

This file is generated from `./charness --help` and subcommand help output in the current checkout.
Operational command payloads, including structured command failures, are emitted as a single YAML document on stdout; progress and unstructured fatal errors use stderr. Default responses are compact; `--detail` returns the full per-item records as one YAML document ([control plane](./control-plane.md#agent-readable-state)).
Human-readable summaries print the affordance line with the `NEXT:` prefix.

## `charness`

```text
usage: charness [-h]
                {init,update,doctor,version,uninstall,reset,task,hooks,train,catalog,capability,goal,tool,worktree}
                ...

Thin charness CLI for managed local install, capability resolution, and
external tool install/update/doctor flows.

positional arguments:
  {init,update,doctor,version,uninstall,reset,task,hooks,train,catalog,capability,goal,tool,worktree}
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
    hooks               Inspect host hook intents.
    train               Stack, verify, and fast-forward an explicit queue of
                        local lane branches.
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
usage: charness task [-h] {status,report,executors,steer,run,wait} ...

positional arguments:
  {status,report,executors,steer,run,wait}
    status              Show one external task-run result, or list all task-
                        run results.
    report              Render the fixed-shape periodic status report from
                        lane metrics, the friction log, and the decision
                        ledger.
    executors           Check executor executable availability without
                        starting a lane.
    steer               Queue a message for a running lane or amend its
                        retained candidate scope.
    run                 Run one independently delegable lane in a clean named
                        worktree and emit a compact receipt.
    wait                Block until named lanes reach a terminal status.

options:
  -h, --help            show this help message and exit
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

## `charness task report`

```text
usage: charness task report [-h] [--repo-root REPO_ROOT] [--window WINDOW]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Parent repo whose external task-run runtime is read.
  --window WINDOW       Trailing window for the period (30m, 3h, 1d, or bare
                        hours).
```

## `charness task executors`

```text
usage: charness task executors [-h] [--repo-root REPO_ROOT]

Resolve the configured executor executables without launching them. Provider
quota remains unknown until an executor reports a usage limit.

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo whose task-run environment is selected. Defaults
                        to the current directory.
```

## `charness task steer`

```text
usage: charness task steer [-h] [--repo-root REPO_ROOT]
                           (--message MESSAGE | --amend-scope AMEND_SCOPE)
                           [--reason REASON] [--actor ACTOR]
                           task_id

positional arguments:
  task_id

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Parent repo whose external task-run runtime is read.
  --message MESSAGE     Message to deliver at the next executor turn boundary.
  --amend-scope AMEND_SCOPE
                        Approve an additional scope and revalidate the same
                        retained candidate; repeatable.
  --reason REASON       Why this steer/amendment is issued; recorded as the
                        envelope `reason` audit field.
  --actor ACTOR         Who issues this steer/amendment; recorded as the
                        envelope `actor` audit field.
```

## `charness task run`

```text
usage: charness task run [-h] [--repo-root REPO_ROOT] [--lane LANE]
                         [--path PATH] [--branch BRANCH] [--base BASE] --scope
                         SCOPE (--prompt PROMPT | --prompt-file PROMPT_FILE)
                         [--executor EXECUTOR] --effort EFFORT
                         [--task-id TASK_ID] [--prepare] [--require-change]
                         [--skip-prepare] [--allow-no-change] [--report-only]
                         [--self-review] [--critical-lane]
                         [--acceptance-skeleton ACCEPTANCE_SKELETON]
                         [--premise-check ID PREMISE DECISION]
                         [--timeout-seconds TIMEOUT_SECONDS]
                         [--no-progress-seconds NO_PROGRESS_SECONDS]
                         [--dry-run] [--rules-file RULES_FILE]
                         [--grant-writable GRANT_WRITABLE] [--detach]

Run one independently delegable lane: shorthand derives a named branch, external worktree, task id, and HEAD base; the explicit form remains available for diagnostics. The parent worktree must be clean; the parent orchestrator owns parallel fan-out and integration.

Exit codes:
  0 success
  1 failed
  2 premise-blocked
  3 validated-partial
  4 executor-unavailable
  5 completed-needs-review

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
                        repeatable, and a `{a,b}` group expands to one scope
                        per alternative. Existing directories include
                        descendants; a path absent from the base is an exact
                        file, so enumerate planned files in a new directory. A
                        glob that matches nothing warns and admits lane-
                        created matching paths on refresh.
  --prompt PROMPT       Implementation instructions passed to the lane
                        executor.
  --prompt-file PROMPT_FILE
                        Read implementation instructions from this file.
  --executor EXECUTOR   Ordered lane executors, comma-separated (for example
                        codex,muse); usage-limit failures fall through in
                        order. Default: codex. Effort must fit every listed
                        executor.
  --effort EFFORT       Orchestrator-selected reasoning effort: medium, xhigh,
                        or max for codex; medium, high, xhigh, or max for
                        muse.
  --task-id TASK_ID     Optional receipt/log identifier for explicit runs;
                        shorthand derives it from --lane.
  --prepare             Run the worktree adapter prepare step before the lane
                        executor.
  --require-change      Fail unless the candidate changes at least one path.
  --skip-prepare        Shorthand diagnostic opt-out: skip the default
                        preparation step.
  --allow-no-change     Shorthand diagnostic opt-out: allow an unchanged
                        candidate.
  --report-only         Report-only lane: force require-change off, treat the
                        delivered stdout report as the terminal artifact, and
                        never classify parent progress as a writer conflict.
                        Cannot be combined with --require-change.
  --self-review         Run self-review for every lane; irreversible-boundary
                        lanes are reviewed automatically.
  --critical-lane       Require a committed failing acceptance skeleton before
                        launch and green at completion.
  --acceptance-skeleton ACCEPTANCE_SKELETON
                        Repository-relative pytest file that must fail before
                        launch and pass before completion.
  --premise-check ID PREMISE DECISION
                        Premise to check before launch and the decision a
                        BLOCKED result needs; repeatable.
  --timeout-seconds TIMEOUT_SECONDS
                        Per-attempt executor timeout in seconds; a retried
                        stall reruns the full budget (see
                        CHARNESS_TASK_RUN_MAX_ATTEMPTS).
  --no-progress-seconds NO_PROGRESS_SECONDS
                        No-progress guard budget in seconds from CONTRACT-READ
                        to first EDITING/scoped diff; 0 turns the stop off.
                        Overrides CHARNESS_TASK_RUN_NO_PROGRESS_SECONDS and is
                        recorded in progress_guard.
  --dry-run             Validate inputs and show the planned lane without
                        creating or running it.
  --rules-file RULES_FILE
                        Standing-rule file the lane executor must read by
                        reference; repeatable. Listed by absolute path in the
                        lane prompt, never inlined, and never read by scope
                        evidence.
  --grant-writable GRANT_WRITABLE
                        Absolute host-state directory a codex lane may write
                        (mapped to codex --add-dir); repeatable. Refused for
                        muse lanes and for grants covering the repo root,
                        $HOME, or /.
  --detach              Launch the lane detached and return once its carrier
                        has started (exit 0, printing the task id and result
                        path), or with the task-run exit code of a preflight
                        or launch failure. Never returns 0 for a lane that did
                        not start. Cannot be combined with --dry-run.
```

## `charness task wait`

```text
usage: charness task wait [-h] [--repo-root REPO_ROOT] [--any]
                          [--timeout-seconds TIMEOUT_SECONDS]
                          task_ids [task_ids ...]

Block until all (or with --any, the first) of the named lanes reach a terminal status; print task_id and status for each finished lane. Exit with the finished lane's task-run exit code (0 success, 1 failed, 2 premise-blocked, 3 validated-partial, 4 executor-unavailable, 5 completed-needs-review); with several lanes, the first non-success in CLI order decides. An already-terminal lane returns immediately.

positional arguments:
  task_ids              Lane task ids to wait for.

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Parent repo whose external task-run runtime is read.
  --any                 Return when the first named lane ends; the others keep
                        running.
  --timeout-seconds TIMEOUT_SECONDS
                        Bound the wait in seconds; 0 waits indefinitely.
```

## `charness hooks`

```text
usage: charness hooks [-h] {status} ...

positional arguments:
  {status}
    status    Report every host-hook intent per host.

options:
  -h, --help  show this help message and exit
```

## `charness hooks status`

```text
usage: charness hooks status [-h] [--repo-root REPO_ROOT]
                             [--adapter-file ADAPTER_FILE]

Report every host-hook intent (the skill-anchor edit guard and the three command-time orchestration guards) per host: declared intent, installed actual, and whether they agree. Exit 0 when every intent is in sync, 1 otherwise.

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repo whose hook state is read. Defaults to the current
                        directory.
  --adapter-file ADAPTER_FILE
                        Adapter YAML declaring host-hook intents; absent means
                        every intent disabled.
```

## `charness train`

```text
usage: charness train [-h] [--repo-root REPO_ROOT] [--main MAIN]
                      [--profile PROFILE] [--stats] [--window WINDOW]
                      [branches ...]

positional arguments:
  branches              Local lane branches in queue order (empty with
                        --stats).

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Repository whose local main branch and lane branches
                        are integrated.
  --main MAIN           Local branch to guard and fast-forward (default:
                        main).
  --profile PROFILE     Optional verify profile; defaults to .agents/train-
                        verify.yaml or built-in standing pytest.
  --stats               Report train throughput (landings, queue wait, waste)
                        instead of landing.
  --window WINDOW       Trailing window for --stats (like 30m, 3h, 1d;
                        default: 3h).
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
                                [--ephemeral | --owned]
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
  --ephemeral           Mark the worktree disposable: create reclaims expired
                        leftovers and caps residue.
  --owned               Keep the worktree until `charness worktree cleanup`;
                        never auto-removed.
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
                             [--ephemeral | --owned] [--home-root HOME_ROOT]
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
  --ephemeral           Mark the worktree disposable: create reclaims expired
                        leftovers and caps residue.
  --owned               Keep the worktree until `charness worktree cleanup`;
                        never auto-removed.
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
                                 [--no-dependency-reuse]
                                 [--home-root HOME_ROOT]
                                 [--charness-checkout CHARNESS_CHECKOUT]

options:
  -h, --help            show this help message and exit
  --repo-root REPO_ROOT
                        Worktree to prepare. Defaults to the current working
                        directory.
  --force               Run prepare even if doctor already reports pass.
  --no-dependency-reuse
                        Do not link an installed dependency tree; the declared
                        install command runs unless doctor coverage skips
                        prepare (add --force to override that).
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
  --prune               After audit, reclaim expired ephemeral worktrees and
                        prune metadata for missing ones.
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
