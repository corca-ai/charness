---
name: issue
description: "Use when filing a GitHub issue from current context or resolving GitHub issues end-to-end through `gh`. Issue creation reports the observed problem before suggesting solutions; issue resolution treats GitHub as the source of truth."
---

# Issue

Use this when the user wants the agent to file or resolve GitHub issues with
`gh`.

`issue` has two command-shaped intents:

- `issue new [repo]`: create an issue from the current context
- `issue resolve [repo] [number|start-end]`: resolve one or more issues

GitHub is the source of truth. Do not prefer session memory, a just-created
issue, a local note, or a stale artifact over the target repository's current
GitHub state.

This skill consumes the `github-gh` integration. When `gh` is missing or not
authenticated enough for the requested operation, follow
`../../shared/references/binary-preflight.md` and stop with the exact missing
capability.

## Bootstrap

Resolve `SKILL_DIR` to the directory that contains this `SKILL.md`.

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/issue_tool.py" preflight --json
python3 "$SKILL_DIR/scripts/issue_tool.py" resolve-invocation --repo-root . -- <issue-resolve-args>
```

Before `issue resolve`, select issue numbers through GitHub when the user did
not provide them:

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" select --repo <org/repo> --selector "<optional-number-or-range>"
```

With no selector, `select` queries the newest open GitHub issue for the target
repo by created date. It must not use the current session's last created issue.

## Target Rules

- `org/repo`: use that exact repository
- `repo`: use the adapter `default_org`, which defaults to `corca-ai`
- omitted repo: infer the current repository from Git remote; if the remote
  lacks an owner, use `default_org` and the current directory name
- for `issue resolve`, one numeric token or `start-end` token is the issue
  selector, not a repository name
- adapter defaults live in `.agents/issue-adapter.yaml`

## New Issue

1. Resolve the target repo.
2. Gather enough local context to make the observed problem transparent.
   Prefer current conversation, relevant local files, failing commands, logs,
   existing issue duplicates, and repository state over broad research.
3. Write the issue as problem context first:
   - what situation occurred
   - what the user, operator, or agent experienced
   - what evidence or commands show it
   - why the current behavior is confusing, costly, or blocked
4. Add solution direction only as an optional weak candidate:
   - "This may be solved by..."
   - "A useful outcome might be..."
   - avoid prescribing the receiving agent's design or implementation
5. Create the issue immediately with `gh issue create --repo <org/repo>`.
   Do not ask for approval unless the user explicitly asks to review first.
6. Report the created issue URL and a one-line summary.

## Resolve Issue

1. Resolve the target repo and issue selector.
   - one number means one issue
   - `start-end` means the inclusive numeric range
   - no number means newest open issue from GitHub SoT
   - one non-numeric token means repo target; two tokens mean repo target plus
     selector
2. Read each selected issue from GitHub with body, comments, labels, state,
   linked PRs when available, and current branch/repo context.
3. Choose the order that makes resolution easiest. If one issue unlocks another,
   do it first.
4. Before designing or while designing, discuss with the user when the issue
   exposes a product, policy, scope, permission, or external-side-effect
   decision the agent should not own.
5. Otherwise, design and implement the smallest complete fix, keeping the issue
   problem statement as the acceptance boundary.
6. Verify with the strongest honest local gate.
7. Run the required premortem closeout for task-completing repo work.
8. Commit, push, and close the GitHub issue only after the fix is on the remote.
   Use explicit close keywords per issue, for example `Close #1. Close #2.`
   when relying on GitHub auto-close behavior.

## Guardrails

- Do not turn `issue new` into an implementation request. Preserve problem
  context and keep solution ideas tentative.
- Do not resolve an omitted issue selector from session memory. Query GitHub.
- Do not close an issue before the pushed branch contains the fix.
- Do not hide missing `gh` auth behind a public fetch fallback when the task
  requires creating, pushing, commenting, or closing.
- Do not treat multiple issues as independent when one issue changes the design
  boundary for another.

## References

- `references/issue-shaping.md`
- `references/resolve-flow.md`
- `scripts/issue_tool.py`
- `scripts/issue_runtime.py`
- `scripts/resolve_adapter.py`
- `scripts/init_adapter.py`
