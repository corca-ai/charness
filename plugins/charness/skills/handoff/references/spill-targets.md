# Spill Targets

When a handoff starts acting like a diary, move durable detail to the artifact
that already owns that truth instead of keeping it in `handoff.md`.

- Use `git log` or commit history for per-slice chronology.
- Use spec files, design docs, or repo-owned contracts for decision evolution.
- Use release notes or changelog surfaces for audience-visible milestones.
- Use `docs/implementation/`, `charness-artifacts/`, or other durable work logs for
  long investigations, experiments, or design discussion that still matters.
- Keep `handoff.md` focused on next pickup, current state, and open decisions.
