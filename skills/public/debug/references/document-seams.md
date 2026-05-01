# Document Seams

`debug` should not hardcode one universal incident path.

Use the repo's current durable troubleshooting surface:

- an incident note
- a debug note directory
- a troubleshooting doc
- an issue-linked artifact

If nothing exists, default to `<repo-root>/charness-artifacts/debug/latest.md` for the
current pointer and `<repo-root>/charness-artifacts/debug/YYYY-MM-DD-<slug>.md` for dated
records.

If the repo has a better checked-in home, move the directory choice into the
debug adapter rather than the skill body.

Do not reconstruct the artifact skeleton from memory when the repo already
ships the contract helper:

```bash
python3 skills/public/debug/scripts/scaffold_debug_artifact.py --repo-root . --json
# then run the emitted validator_command
```

The current pointer, usually `latest.md`, must use the scaffolded schema.
Dated records can remain legacy-compatible so old incident memory is still
readable and does not hide which new artifact failed validation.
