# Critique: #269 Achieve Head Freshness

Execution: parent-delegated fresh-eye review with two code critique angles and
one separate counterweight pass.

Fresh-Eye Satisfaction: parent-delegated

Packet Consumed: `charness-artifacts/critique/2026-05-31-120238-packet.md`

Target: `code-critique`

## Change

Add a deterministic `check_goal_artifact.py` freshness check for achieve goal
artifacts that rejects current-HEAD prose naming an immutable SHA that is not
the live local `git rev-parse HEAD`, while allowing explicit historical/proof
target wording and live commands such as `--head-sha HEAD`.

## Angles

- Angle 1: correctness and false-positive/false-negative risk in the
  mutable-HEAD parser and `check_goal_artifact.py` integration.
- Angle 2: public-skill portability, mirror/sync risk, and overreach against
  historical artifacts.
- Counterweight: triaged the angle blockers after the first repair pass.

## Findings

### Act Before Ship

- The initial line-wide historical/live-command exemptions were too broad:
  `before` or `--head-sha HEAD` anywhere on a physical line could hide a stale
  current-HEAD claim. Fixed by matching SHA tokens bound to specific HEAD claims
  and testing `Before calling completion, current HEAD is ...`.
- The initial line-level token scan treated every SHA on a HEAD line as if it
  claimed to be HEAD, causing false positives for valid prose such as
  `origin/main is <base>; HEAD is <current>`. Fixed by checking direct
  `HEAD is/=/at <sha>` claims and parenthetical HEAD claims, not all line SHAs.
- `git rev-parse HEAD` setup failures could break portable validation in
  non-git or missing-git contexts. Fixed by catching `OSError` and preserving
  the skip-style report.
- The first repair pass still made `not current` ineffective for direct claims.
  Fixed by accepting same-line historical context such as `historical HEAD is
  ...` and `HEAD is ... (not current)`, with a regression test.
- Add CLI-level coverage proving `check_goal_artifact.py` emits
  `head_freshness`, sets `ok=false`, and exits nonzero. Implemented.

### Bundle Anyway

- Keep a positive test for the recommended live command shape
  `--base-sha <old> --head-sha HEAD`. Covered by the historical/live command
  regression.
- Keep the mirror sync check in closeout because the source and plugin helper
  copies must stay identical. Covered by `sync_root_plugin_manifests.py` and
  staged mirror drift checks.

### Over-Worry

- Skipping freshness when git HEAD is unavailable is acceptable for portability;
  the report names the skip and shape validation remains usable.
- Cautilus scenario routing does not need to change because this is a
  deterministic artifact-validator change, not an achieve draft/activation
  behavior change.

### Valid But Defer

- Expanding the guard to all `..HEAD` range prose would require a separate
  grammar and risks over-firing on legitimate base-range proof. This slice stays
  scoped to immutable SHA claims bound to current-HEAD wording.
- Fenced examples remain ignored. That could miss a stale proof if operators put
  first-class closeout evidence inside a fence, but checking examples would
  over-fire for normal documentation snippets.

## Next Move

Ship after targeted validators and slice closeout pass. Record the
counterweight-driven fixes in the active goal slice log and do not claim live
GitHub issue closure.
