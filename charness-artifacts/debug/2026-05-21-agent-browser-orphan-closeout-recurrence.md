# Agent Browser Orphan Closeout Recurrence Debug
Date: 2026-05-21

## Problem

`python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`
failed after all slice validators passed because the final
`agent_browser_runtime_guard.py --assert-no-orphans` phase found one orphan
`agent-browser` daemon tree.

## Correct Behavior

Given slice closeout runs after a code change, when all deterministic validators
pass, then the final external-runtime hygiene phase should still fail if a
browser daemon tree is orphaned, print the cleanup command, and allow the
operator to clean and re-run closeout.

## Observed Facts

- All sync, packaging, docs, integration, ruff, and pytest phases passed.
- The final runtime hygiene command failed with `orphan_daemon_count=1` and
  named `python3 scripts/agent_browser_runtime_guard.py --repo-root .
  --cleanup-orphans --execute` as the next step.
- Running that cleanup command returned `orphan_daemon_count=0`,
  `remaining_pids=[]`, and no forced pids.
- A later README docs-ergonomics closeout hit the same guard again with one
  orphan `agent-browser` daemon tree. The closeout command's cleanup fallback
  removed it; a follow-up `--assert-no-orphans` returned clean.
- The directly related prior RCA is
  [2026-05-20 agent-browser runtime hygiene](./2026-05-20-agent-browser-runtime-hygiene.md).

## Reproduction

1. Leave an orphan `agent-browser` daemon tree in local runtime state.
2. Run `python3 scripts/run_slice_closeout.py --repo-root .
   --ack-cautilus-skill-review`.
3. Observe the final hygiene phase fail after validators pass.

## Candidate Causes

- A prior browser-mediated support or manual command left a PPID=1 daemon tree.
- A stale local browser command recreated a daemon after an earlier cleanup.
- The new usage-episode emitter changed closeout behavior and spawned
  `agent-browser`.

## Hypothesis

If the closeout failure is a recurrence of the known external-runtime hygiene
seam, then cleanup should remove the orphan tree without code changes and a
re-run should pass the hygiene phase. If the new emitter caused it, the orphan
would recur from the same closeout path after cleanup.

## Verification

- Cleanup command succeeded and reported no remaining orphan pids.
- The new emitter code does not import or execute `agent-browser`; it only reads
  the usage-episodes adapter and appends JSONL when enabled.
- The README docs-ergonomics slice changed markdown and plugin README export
  only; it also did not add an `agent-browser` execution path.
- Similar-pattern scan reused the prior RCA's sibling set: browser-mediated
  support scripts, adapter-configured probes, integration healthchecks,
  quality closeout, and stale lock payloads. No new `agent-browser` call was
  added in this slice.

## Root Cause

Dirty local external-runtime state from a prior `agent-browser` session
survived until this slice closeout. The final hygiene guard correctly converted
that runtime state into a blocking closeout failure instead of allowing a green
ship with orphan browser processes.

## Detection Gap

- No new detection gap. The intended guard fired at closeout and printed the
  cleanup command.

## Sibling Search

- Mental model: a passed validator set means the local runtime is clean.
- Same seam: browser-mediated gather or support commands can still leave
  long-lived runtime state; decision: already covered by prior RCA and final
  guard; proof: this closeout failure.
- Adjacent seam: new emitters should not invoke long-lived external runtimes;
  decision: scanned current usage-episode emitter code; proof: no
  `agent-browser` references added.
- Evidence seam: generated runtime payloads under `.charness/` should stay
  ignored; decision: emitter writes under `.charness/usage-episodes/` only when
  enabled; proof: adapter remains disabled in this repo.

## Seam Risk

- Interrupt ID: agent-browser-runtime-hygiene
- Risk Class: operator-visible-recovery
- Seam: external browser daemon lifecycle across closeout and support scripts.
- Disproving Observation: closeout after cleanup reports no orphan daemon tree.
- What Local Reasoning Cannot Prove: that future upstream `agent-browser`
  commands cannot leave new orphan trees.
- Generalization Pressure: monitor

## Interrupt Decision

- Critique Required: no
- Next Step: impl
- Handoff Artifact: docs/handoff.md

## Prevention

Keep the final closeout hygiene guard. Treat future failures of this shape as
runtime-state cleanup unless a same-slice code diff added a new
`agent-browser` execution path.

## Related Prior Incidents

- [2026-05-20 agent-browser runtime hygiene](./2026-05-20-agent-browser-runtime-hygiene.md):
  root RCA and sibling scan for this recurring external-runtime seam.
