# Spill Targets

When a handoff starts acting like a diary, move durable detail to the artifact
that already owns that truth instead of keeping it in the handoff artifact.

- Use `git log` or commit history for per-slice chronology.
- Use spec files, design docs, or repo-owned contracts for decision evolution.
- Use release notes or changelog surfaces for audience-visible milestones.
- Use `<repo-root>/charness-artifacts/release/latest.md` and
  `current_release.py` output for checked-in release/version state.
- Use `<repo-root>/charness-artifacts/quality/latest.md` for gate status, coverage deltas,
  runtime signals, and quality recommendations.
- Use `<repo-root>/charness-artifacts/retro/` for workflow lessons and repeat traps.
- Use `<repo-root>/charness-artifacts/debug/` for root-cause detail and resolved failures.
- Use `<repo-root>/docs/implementation/`, `charness-artifacts/`, or other durable work logs for
  long investigations, experiments, or design discussion that still matters.
- Keep the handoff artifact focused on next pickup, current state, and open decisions.

## Replacement Pattern

When spilling detail, leave a single action-oriented pointer such as:

- "Quality posture and recent gate numbers live in
  `<repo-root>/charness-artifacts/quality/latest.md`; next cleanup target is `<path>`."
