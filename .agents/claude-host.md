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

## Lane-orchestration lessons this repo has already paid for

- A brief names every surface the change touches as the lane's deliverable,
  and `--scope` carries every one of them; the rule and its two paid instances
  live in [docs/parallel-execution.md](../docs/parallel-execution.md#disjoint-writers).
- An in-process subagent brief that touches `scripts/` or `skills/` has no
  lane receipt, so its definition of done names the gate by hand: the
  subagent runs `python3 scripts/mutation/release_changed_line_coverage.py
  --repo-root . --base-sha <base> --refuse-unestablished` on its own diff and
  reports done only with `status: clean` (or `noop`), quoting the payload.
  A `task run` lane gets the same verdict in its receipt's
  `changed_line_gate` ([docs/parallel-execution.md](../docs/parallel-execution.md#disjoint-writers)).
- Lane self-reports are not proof: re-run the battery in the integrated
  tree, and run the FULL standing gates before treating a
  production-surface change as done — focused per-lane checks miss
  standing regressions.
- `.agents/*-adapter.yaml` checklist entries must be single-line quoted
  strings; the adapter readers are line-based and refuse multi-line
  continuations.
- Integrate candidate-first: a lane's commit is inspectable in its
  worktree as soon as the lane commits, so review and integrate from
  there instead of idling on the wrapper process. When a lane times out,
  salvage its worktree commit (and any uncommitted work in it) rather
  than re-running the lane; a timeout destroys the wrapper, not the
  work. Background-waiting on a finished candidate is the antipattern
  this repo has already paid for twice.
- Run the disconfirming probe FIRST at integration — compare the
  candidate's behavior against the real repository before running its
  confirming test suite. Both defects that escaped lane tests in the
  #748 slice-1 session were caught this way, and only this way.
