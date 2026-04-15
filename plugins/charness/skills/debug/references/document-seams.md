# Document Seams

`debug` should not hardcode one universal incident path.

Use the repo's current durable troubleshooting surface:

- an incident note
- a debug note directory
- a troubleshooting doc
- an issue-linked artifact

If nothing exists, default to `charness-artifacts/debug/latest.md` for the
current pointer and `charness-artifacts/debug/YYYY-MM-DD-<slug>.md` for dated
records.

If the repo has a better checked-in home, move the directory choice into the
debug adapter rather than the skill body.
