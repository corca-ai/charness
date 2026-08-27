# Codex Host Notes

This file owns Charness-repository Codex choices only. Portable skills and the
`charness task` CLI must not hardcode this model or reasoning tier.

## Parallel routing

Use the live host subagent API for bounded read-only investigation or short
judgment work. Use `charness task run` for independently writable work that
needs a named branch, isolated worktree, external runtime, exact scope, and a
durable result. The parent owns design, integration, final verification, and
provider mutations. Task prompts forbid descendant agents unless the operator
explicitly asks for nested delegation.

## Isolated implementation lane

The parent must be clean. Charness implementation lanes use
`gpt-5.6-luna` with `xhigh` reasoning:

```sh
charness task run \
  --repo-root <repo> \
  --path <lane-root>/<lane-name> \
  --branch luna/<lane-name> \
  --base <base-ref> \
  --scope <path-1> \
  --scope <path-2> \
  --prompt-file <brief-file> \
  --codex-arg=-m \
  --codex-arg=gpt-5.6-luna \
  --codex-arg=-c \
  --codex-arg=model_reasoning_effort=xhigh \
  --codex-arg=--approve-for-me \
  --prepare \
  --require-change
```

The task result is the only lane result carrier. Review the retained worktree
and receipt, then integrate serially. A successful process or commit is not by
itself integration proof.
