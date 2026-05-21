# Session Retro: Run Quality Changed Path Fallback
Date: 2026-05-22
Mode: session

## Context

This session continued the suppression-pattern scan by hardening
`run-quality --read-only` changed-path discovery. Failed git discovery now
queues `check-coverage` instead of allowing an unknown changed-path set to look
empty.

## Evidence Summary

- Fresh-eye design review identified the exact `|| true` and process
  substitution failure mode.
- A second sibling scan confirmed test conventions and the next shell
  file-listing targets.
- Focused `test_quality_runner.py`, slice closeout, and
  `./scripts/run-quality.sh --read-only` all passed.
- Cautilus planner returned `next_action: none`; deterministic validation owned
  the prompt-surface closeout.

## Waste

- The first implementation captured the failed command status too late and
  printed `exit_code: 0`; the new fake-git regression caught it quickly.
- The original README skip test committed the README change, so it only proved
  clean-tree skip behavior until fresh-eye review called out the gap.

## Critical Decisions

- The read-only quality selector now treats discovery failure as unknown state
  and runs the broader deterministic gate. This preserves the cost-saving skip
  when discovery succeeds and finds no relevant paths.
- Public `quality` guidance now distinguishes cost-saving selectors, which can
  run the broader gate, from publish/proof selectors, which should fail before
  publishing derived state.

## Expert Counterfactuals

- Gary Klein lens: run a premortem on shell status handling before writing the
  helper; it would have flagged that `if ! command` and compound statuses can
  easily lose the original exit code.
- Daniel Kahneman lens: do not accept a compatibility test just because its
  name matches the behavior; inspect whether the fixture actually contains the
  advertised changed state.

## Next Improvements

- workflow: when testing changed-path behavior, assert the fixture has the
  intended unstaged, staged, untracked, or clean state before relying on output.
- capability: consider a reusable shell helper for git listing diagnostics if
  the markdown/link/secret siblings are fixed in shell rather than ported.
- memory: keep shell file-listing gates as the next suppression sibling.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-05-22-run-quality-changed-path-session.md`
