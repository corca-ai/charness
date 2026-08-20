# Post-Lock Release-Blocker Path Table

Date: 2026-08-21
Source: `charness-artifacts/issues/2026-08-20-next-release-ledger.json`

This table is the R1 join barrier for the five post-lock exceptions. The
exception rows establish current release impact; this table establishes the
writer boundary. A row remains admitted only while its source read, evidence,
acceptance, and path budget all remain true.

| Track | Issue | Owner | Source paths | Test/evidence paths | Dependencies |
| --- | --- | --- | --- | --- | --- |
| A — evidence continuity | #682 | retro/prove owner | `skills/public/prove/SKILL.md`; `skills/public/retro/SKILL.md`; `skills/public/retro/scripts/check_auto_trigger.py` | `tests/test_retro_plan.py`; `charness-artifacts/issues/2026-08-21-682-reproduction.txt` | preserve fail-closed empty-input behavior; parent owns export sync |
| A — reviewer handoff | #683 | shared-boundary owner | `skills/shared/scripts/reviewer_boundary_fingerprint.py`; `skills/shared/references/fresh-eye-subagent-review.md` | `tests/quality_gates/test_reviewer_boundary_fingerprint.py`; `charness-artifacts/issues/2026-08-21-683-reproduction.txt` | serialized because `skills/shared/**` is parent-owned |
| A — delivery reliability | #687 | critique/review owner | `skills/shared/scripts/reviewer_result.py`; `skills/shared/references/fresh-eye-subagent-review.md`; `skills/public/critique/SKILL.md` | `tests/quality_gates/test_reviewer_result_delivery.py`; `tests/quality_gates/test_reviewer_delivery_state_machine.py`; `charness-artifacts/debug/2026-08-21-fresh-eye-interrupted-delivery.md` | #683 handoff vocabulary; Codex host remains external/non-claim |
| B — persistence contract | #685 | retro persistence owner | `skills/public/retro/scripts/persist_retro_artifact.py`; `scripts/retro_persistence_lib.py` | `tests/quality_gates/test_retro_persistence.py`; `charness-artifacts/issues/2026-08-21-685-reproduction.txt` | no shared writer overlap with Track A |
| B — installed path contract | #686 | retro planner owner | `skills/public/retro/scripts/plan_retro_run.py`; `scripts/portable_command_carrier.py` | `tests/quality_gates/test_retro_installed_plan_path.py`; `charness-artifacts/issues/2026-08-21-686-reproduction.txt` | installed-layout fixture; do not touch shared `tests/test_retro_plan.py`; generated export sync is parent-only |
| — requalification only | #681 | achieve quality owner | `charness-artifacts/issues/reads/681.raw.yaml`; no source writer until current consumer proof changes the premise | existing goal checker/cadence tests and current issue read | no code admission; preserve `already-satisfied` until a live regression is proven |

## Join Rules

- Track B lanes may author concurrently only after their path overlap check;
  Track A shared-boundary lanes are serialized in the parent even when their
  tests are independent.
- No writer edits `plugins/charness`, generated docs, version surfaces, the
  ledger, `.charness`, or release records. The parent integrates those surfaces
  after each lane's focused proof.
- A lane that discovers a shared helper or generated surface must stop, append
  the dependency here, and return to parent serialization; it may not widen its
  worktree budget silently.
- The #682/#686 test-path overlap is resolved by assigning the installed-path
  fixture to `tests/quality_gates/test_retro_installed_plan_path.py`; any
  change that requires `tests/test_retro_plan.py` returns to the parent join.
- R2 starts only after this table, the exception rows, and the #687 spec
  critique disposition are committed or explicitly marked host-blocked.
