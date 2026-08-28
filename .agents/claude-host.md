# Claude Host Notes

This file owns Charness-repository choices specific to a Claude Code
orchestrating session. The common operating contract stays in
[AGENTS.md](../AGENTS.md); Codex lane choices stay in
[codex-host.md](./codex-host.md). Do not duplicate either here.

## Delegation and model policy (operator-set, 2026-08-28)

- Claude-side delegation uses the dynamic workflow channel with `sonnet`
  workers, or a host subagent with an EXPLICIT `sonnet` or `opus` model
  override. Never spawn a Claude subagent that inherits the parent
  session's model by omission.
- The repo `bounded-reviewer` agent definition declares no model, so an
  omitted override silently inherits the parent model. Always pass the
  model field when spawning it.
- Implementation, deep review, and any independently writable work go
  through `charness task run` Codex lanes per
  [codex-host.md](./codex-host.md). The parent session owns design,
  adversarial verification, integration, generated-surface sync, and
  final proof.

## Lane-orchestration lessons this repo has already paid for

- A lane's `--scope` list must contain every path its brief instructs it
  to touch, including repo-root shims; a missed path invalidates an
  otherwise correct candidate.
- Lane self-reports are not proof: re-run the battery in the integrated
  tree, and run the FULL standing gates before treating a
  production-surface change as done — focused per-lane checks miss
  standing regressions.
- `.agents/*-adapter.yaml` checklist entries must be single-line quoted
  strings; the adapter readers are line-based and refuse multi-line
  continuations.
