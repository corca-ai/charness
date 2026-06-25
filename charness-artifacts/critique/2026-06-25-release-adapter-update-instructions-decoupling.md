# Release Adapter Update Instructions Decoupling Critique
Date: 2026-06-25

Packet Consumed: charness-artifacts/critique/2026-06-25-004012-packet.md

## Decision Under Review

Change the `release` adapter contract so `update_instructions` is an evergreen operator refresh path, not a per-release notes store. Per-release behavior, migration, and rollback narrative moves to release notes or generated release artifacts.

## Failure Angles

- Michael Jackson problem framing: the original patch still solved the immediate `0.54.2 -> 0.54.3` stale-text symptom more than the general "version-pinned adapter text" problem.
- Gerald Weinberg diagnostic: checking only previous/target versions missed older release-note residue such as `0.18.0` in a downstream adapter.
- Atul Gawande operational checklist: `--publish-current`, first-publish, and dirty-worktree planner paths could still bypass or hide the evergreen-adapter repair.

## Counterweight Pass

- Act before ship: broadened the guard to detect release-like `x.y.z` pins in adapter `update_instructions`, including older non-previous versions, target-only pins, `previous == target`, and `previous is None` paths.
- Act before ship: moved planner `prep_update_instructions` ahead of `clean_worktree` because prep is read-only and explicitly safe before a clean release mutation tree.
- Bundle anyway: retained the dotted-date false-positive guard so `2026.06.05` does not become a release-version blocker.
- Over-worry: a perfect semantic classifier for every possible version-looking token is not the goal; the field should be short evergreen operator guidance, so a narrow release-like pin detector is proportionate.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/publish_release_preflight.py | action: fix | note: version-pinned adapter text escaped when previous_version was absent or equal to target_version
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_release_publish_resilience.py | action: fix | note: older non-previous release pins lacked regression coverage
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/release/scripts/plan_release_run_packets.py | action: fix | note: dirty worktree advice hid the read-only prep_update_instructions repair path
- F4 | bin: over-worry | evidence: moderate | ref: skills/public/release/scripts/publish_release_preflight.py | action: document | note: a broader semantic version oracle is unnecessary for this short adapter field

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: adapter declared model=gpt-5.5, reasoning_effort=medium, service_tier=priority; host tool call omitted explicit fields and inherited parent defaults.
- Host exposure state: host-defaulted
- Application state: host returned agent ids 019efc38-bc84-7110-8d62-3b593f3ecdc5, 019efc38-d589-7393-8783-982fe776edc3, and 019efc38-f382-7201-aaf5-a5441929827e.

## Fresh-Eye Satisfaction

Fresh-Eye Satisfaction: parent-delegated. Three bounded fresh-eye reviewers completed read-only code critique lenses and all Act Before Ship findings were fixed before closeout.
