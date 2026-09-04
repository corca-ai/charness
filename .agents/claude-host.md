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
- Skill scripts in this repo run from the checkout: when Claude Code reports
  an installed plugin path as the skill's base directory, run
  `python3 skills/public/<skill>/scripts/<name>.py --repo-root .` from the
  working tree instead. `goal_run_pickup.py` and `plan_release_run.py` print
  `script_origin` so the copy that answered is in the output. The pickup
  refuses a drifted installed copy (`stale-installed-copy`) before any
  provider read; the release planner only reports, because it is read-only,
  and the publish helper's own entrypoint guard is the refusal before a
  release mutation. The rule and its reason live in
  [bootstrap-resolution.md](../skills/shared/references/bootstrap-resolution.md).
- The repo `bounded-reviewer` agent definition declares no model, so an
  omitted override silently inherits the parent model. Always pass the
  model field when spawning it.
- **A spawned review that returned no report is an UNRUN review.** In-process
  `bounded-reviewer` subagents have gone idle without delivering five times
  across two sessions (2026-08-29 ×2; 2026-08-30 ×3, one of them WITH the
  explicit `opus` override this section requires, so the override is not the
  cause). The host reports the agent as `idle`/`available`, which reads like
  completion; nothing distinguishes it from a review that ran and found
  nothing. Treat an absent report exactly as `test_empty_scope_refusals.py`
  treats an unestablished scope — it is not a pass, and integration must not
  proceed as if the angle was covered.
- Because of that, do not budget a bounded-reviewer spawn as the proof for a
  design or deletion boundary. Either verify the angle in the parent with a
  disconfirming probe against the real repository, or say plainly in the
  session output that the review did not happen. This repo's own lesson holds
  here: the defects that escaped lane tests were caught by running the
  candidate against the real tree, not by a second opinion.
- Implementation, deep review, and any independently writable work go
  through `charness task run` Codex lanes per
  [codex-host.md](./codex-host.md). The parent session owns design,
  adversarial verification, integration, generated-surface sync, and
  final proof.

## Lane orchestration

Parallel channels, disjoint writers, proof floor, and integration order live in
[docs/parallel-execution.md](../docs/parallel-execution.md). Do not restate them
here. Host-specific notes that remain: `.agents/*-adapter.yaml` checklist
entries must be single-line quoted strings (line-based readers refuse
multi-line continuations).
