# Spill Targets

When a handoff starts acting like a diary, move durable detail to the artifact
that already owns that truth instead of keeping it in [`handoff.md`](../../../../docs/handoff.md).

- Use `git log` or commit history for per-slice chronology.
- Use spec files, design docs, or repo-owned contracts for decision evolution.
- Use release notes or changelog surfaces for audience-visible milestones.
- Use [`charness-artifacts/quality/latest.md`](../../../../charness-artifacts/quality/latest.md) for gate status, coverage deltas,
  runtime signals, and quality recommendations.
- Use `charness-artifacts/retro/` for workflow lessons and repeat traps.
- Use `charness-artifacts/debug/` for root-cause detail and resolved failures.
- Use `docs/implementation/`, `charness-artifacts/`, or other durable work logs for
  long investigations, experiments, or design discussion that still matters.
- Keep [`handoff.md`](../../../../docs/handoff.md) focused on next pickup, current state, and open decisions.

## Replacement Pattern

When spilling detail, leave a single action-oriented pointer such as:

- "Quality posture and recent gate numbers live in
  [`charness-artifacts/quality/latest.md`](../../../../charness-artifacts/quality/latest.md); next cleanup target is `<path>`."
