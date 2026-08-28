# Codex Host Notes

This file owns Charness-repository Codex effort choices. `charness task` fixes
its model to `gpt-5.6-luna`; callers choose only the reasoning effort.

## Parallel routing

Use the live host subagent API for bounded read-only investigation or short
judgment work. Use `charness task run` for independently writable work that
needs a named branch, isolated worktree, external runtime, exact scope, and a
durable result. The parent owns design, integration, final verification, and
provider mutations. Task prompts forbid descendant agents unless the operator
explicitly asks for nested delegation.

## Model and effort presets

Use `gpt-5.6-luna` for Charness lanes and choose effort from the work, not from
the fact that a lane exists:

| Work | Effort | Default stop shape |
| --- | --- | --- |
| bounded read-only search or a short self-evident edit | `medium` | return the requested top findings or focused patch; stop instead of widening |
| careful implementation, proof/verdict logic, or a migration whose wrong shape is expensive to unwind | `xhigh` | resolve the named hard uncertainty; do not broaden into a repo audit |
| explicitly selected, consequential critique | `max` | two bounded reviewers by default, with deliberately different perspectives or scopes |

The orchestrator chooses the preset by judging the work itself. Do not encode
that choice as filename, diff-size, label, keyword, or other mechanical
heuristics. The parent may promote a lane only after naming the concrete
uncertainty the lower tier could not settle. Do not use `xhigh` or `max` as a
generic signal that work matters. A prompt still carries the outcome, exact
scope, non-claims, stop condition, and result shape; effort does not repair a
vague brief.

The two default critique prompts must seek materially different evidence—for
example contract/behavior and simplification/operability—not duplicate the same
review with different wording. The orchestrator integrates their findings and
decides whether either warrants a change.

## Isolated implementation lane

The parent must be clean. The ordinary implementation preset is:

```sh
charness task run \
  --lane <lane-name> \
  --scope <path-1> \
  --scope <path-2> \
  --prompt-file <brief-file> \
  --effort xhigh \
  --codex-arg=--approve-for-me
```

The task result is the only lane result carrier. Review the retained worktree
and receipt, then integrate serially. A successful process or commit is not by
itself integration proof.
