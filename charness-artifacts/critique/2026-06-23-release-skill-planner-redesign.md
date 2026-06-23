# Release Skill Planner Redesign Critique

## Execution

Three bounded fresh-eye subagents reviewed the pending release skill planner,
reference split, quality lens, and tests.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewer Tier Evidence

- Requested tier: high-leverage bounded fresh-eye reviewers.
- Requested spawn fields: agent_type=explorer, read-only scope, inherited parent
  model and reasoning settings.
- Host exposure state: requested_fields_sent
- Application state: spawn tool accepted and completed reviewers
  `019ef482-75ba-7e92-9ce8-70c65a3098a8`,
  `019ef482-90c2-7ee0-8050-f8bdc1214faf`, and
  `019ef482-a8a7-7b70-9219-2791d7449d8b`; provider-side application is not
  separately visible.

## Packet Consumed

n/a (no adapter sections)

## Target

code critique

## Diff Scope

Compress `release/SKILL.md`, split release references by concept, add a
read-only release run planner, strengthen the quality skill ergonomics lens, and
reduce tests that were coupled to exact prose.

## Findings

### Act Before Ship

- Public `install-refresh.md` leaked the local `charness update` command into a
  portable release reference. Fixed by making the adapter own the refresh
  command.
- `plan_release_run.py` passed an empty path list to real-host proof, hiding
  changed-path triggers. Fixed by using the same changed-path collection as the
  proof CLI.
- `plan_release_run_packets.py` replaced a concrete `--critique-blocked` signal
  with `<host-signal>`. Fixed by preserving and shell-quoting the supplied
  signal.
- Publish packets were emitted even when the planner said critique or update
  prep was still required. Fixed by emitting publish packets only for
  `next_action.kind == publish_dry_run`.
- Tests still pinned exact prose fragments for quality skill ergonomics and
  release phase barriers. Fixed by adding stable `review_topic_ids`, checking
  structured planner payloads, and narrowing release contract checks to active
  source files.

### Bundle Anyway

- The single `references/index.md` entry in `SKILL.md` is acceptable because the
  planner owns normal progressive disclosure.

### Over-Worry

- No over-worry findings affected the change.

### Valid but Defer

- A broader host-surface portability wording pass may be useful later, outside
  this release-skill redesign slice.

## Pre-Merge Action

All Act Before Ship findings were addressed in the current diff before closeout.
