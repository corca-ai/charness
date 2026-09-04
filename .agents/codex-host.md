# Codex Host Notes

This file owns Charness-repository Codex effort *judgment*. Model identity and
allowed effort tokens are held by `scripts/task_run/task_run_contract.py`;
callers choose only the reasoning effort for a lane.

## Effort judgment

Choose effort from the work, not from the fact that a lane exists:

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
  --effort xhigh
```

The task result is the only lane result carrier. Review the retained worktree
and receipt, then integrate serially. A successful process or commit is not by
itself integration proof.

Channel choice (host subagent vs `charness task run`) lives in
[docs/parallel-execution.md](../docs/parallel-execution.md).

## Sandbox / network

On this host, Codex lanes run `--sandbox workspace-write` with
`network_access = true` set in `~/.codex/config.toml` (operator-approved
2026-08-28), so lanes may fetch dependencies directly; no parent-side
prefetch is needed.
