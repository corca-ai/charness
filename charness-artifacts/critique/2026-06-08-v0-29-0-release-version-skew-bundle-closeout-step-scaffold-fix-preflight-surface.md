# v0.29.0 release — version-skew bundle (closeout step + scaffold fix + preflight surface)
Date: 2026-06-08

## Decision Under Review

Cut charness v0.28.0 → v0.29.0 (minor) via `publish_release.py --part minor
--execute` (bump + sync manifests + push `origin/main` of the 15-commit
`origin/main..HEAD` bundle + tag + GitHub release), THEN run `charness update` on
THIS dev machine and re-verify. Operator-authorized irreversible actions. The
bundle ships this goal's 5 commits plus the prior complete-but-unpushed #335
gate-recurrence goal + handoff.

## Failure Angles

- Version bump too low/high: does the Slice-2 scaffold-citation behavior change
  break a downstream consumer expectation (warrant major)?
- The install/update contract change (Slice 1) could mislead a downstream reader
  of the portable `release` SKILL.md (charness-only command leaked into core).
- Pushing 15 commits incl. prior goals: something in the range not release-ready
  (WIP, an unintended `Status: active` goal, broken link).
- `update_instructions` staleness guard: adapter described 0.28.0, not the target.
- Irreversibility: once pushed/tagged/released, what is hard to undo?

## Counterweight Pass

- Bump = minor is honest: additive preflight surface + additive closeout-contract
  step + a citation fix; the scaffold change preserves the installed-plugin
  fallback for consumer repos with no own validator (no invocation break, no
  validator verdict change). Not major; not patch.
- Portable/charness split is clean: `release` SKILL.md has zero hardcoded
  `charness update`; the concrete command lives only in the charness-specific
  reference + adapter. Will not mislead downstream.
- 15-commit bundle is release-ready: no WIP/FIXME in changed non-test files; the
  only `Status: active` goal in the range is the intentional carrier goal
  (completes post-release).
- Staleness guard: REAL blocker (F1) — found and fixed.
- Irreversibility: low-risk — target tag/release clear locally + remote; surface
  coherent (all 5 manifests at 0.28.0, no drift); guards fire pre-mutation.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: .agents/release-adapter.yaml update_instructions | action: fix | note: adapter update_instructions described 0.28.0 not the 0.29.0 target, so publish_release's update_instructions_version_blocker would SystemExit pre-mutation — FIXED by prepending a fresh 0.29.0 entry; re-review ran the real update_instructions_version_blocker(target=0.29.0) -> None, guard no longer fires
- F2 | bin: valid-but-defer | evidence: weak | ref: .agents/release-adapter.yaml | action: defer | note: stock PyYAML safe_load chokes on the unquoted backtick in update_instructions, but the publish path uses the repo's own hand-rolled load_yaml exclusively and pre-existing entries already contain backticks — a pre-existing property, not introduced by this release; awareness-only

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent reviewer (separate agent context), per the release skill's compatibility/install/visibility standalone-critique requirement and the goal's bundle-boundary verification plan.
- Requested spawn fields: read-only release-decision reviewer with the full release packet (the irreversible actions, the bundle contents, the minor-bump justification, the install/update contract change, the push of prior goals, real-host-proof plan); inspect via git diff/show/log + read-only test runs only.
- Host exposure state: applied
- Application state: host-confirmed: bounded fresh-eye subagent (general-purpose agent a371a7a57279a2dd4) returned round-1 HOLD with one real blocker (update_instructions staleness, F1); after the fix it returned round-2 SHIP, having loaded the adapter via the repo's own parser and run update_instructions_version_blocker(target=0.29.0)->None, verified all three 0.29.0-entry claims against shipped behavior, and confirmed target tag/release clear + no drift + narrative audit 7/7.

## Fresh-Eye Satisfaction

SHIP (round 2). The fresh-eye reviewer's round-1 HOLD caught a genuine pre-publish
blocker — the stale `update_instructions` that the publish staleness guard refuses
on — before any irreversible action. After the fix, round-2 SHIP confirmed the
guard no longer fires (run against the real repo parser), the minor bump is honest,
the portable/charness split is clean, the 15-commit bundle is release-ready, and
the irreversibility posture is low-risk. Remaining steps before `--execute`: commit
the adapter fix + this critique artifact (the `--critique-artifact` must be
git-tracked), then run the on-machine `charness update` + doctor + scaffold==gate
re-verify as the required real-host closeout.
