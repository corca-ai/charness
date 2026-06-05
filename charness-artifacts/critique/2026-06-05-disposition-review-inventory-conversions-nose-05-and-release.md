# Disposition Review: inventory-conversions-nose-05-and-release

Goal: charness-artifacts/goals/2026-06-05-inventory-conversions-nose-05-and-release.md
Reviewer: fresh-eye disposition review (bounded subagent, read-only, shared parent worktree)

Slug: inventory-conversions-nose-05-and-release

## Verdict per improvement

- Pre-flight the flaky/expensive pre-push gate before an irreversible publish →
  **issue #305**: `sound`. #305 is OPEN; body item 1 covers the non-resumable
  mid-publish failure and the #194 pre-push flake leaving commit+tag local.
- `publish_release.py` installed-cache bootstrap failure → **issue #305**:
  `sound`. #305 body item 2 covers it verbatim (`ModuleNotFoundError:
  skills.public`; only the repo-root copy works).
- Adapter `update_instructions` staleness — immediate refresh → **applied**
  (`.agents/release-adapter.yaml`); systemic detection gap → **issue #305**:
  `sound`. Working-tree refresh reads "pull 0.21.0 …" (HEAD still 0.20.0,
  file `M`); #305 body item 3 covers the detection gap (preflight only triggers
  on adapter-file change).
- nose 0.5 schema-parse regression risk → **applied** (regression test): `sound`.
  `tests/quality_gates/test_quality_nose_advisory.py::test_nose_advisory_parses_v05_object_schema`
  emits a top-level 0.5 object and asserts `family_count == 1`; committed in
  `7bd7d1ee`, durable.
- Memory/lesson capture → **applied** (retro + recent-lessons): `sound`.
  `charness-artifacts/retro/2026-06-05-inventory-conversions-nose-05-and-release.md`
  exists; `recent-lessons.md` refreshed and cites this run.

## Overall

Dispositions are honest enough to close the goal. All five map to genuine
evidence — three to an open #305 whose body covers each claimed item, two
`applied` claims that landed durably. No over-claim, no relabeling needed.

One closeout condition (folded): the item-3 "applied" adapter refresh is the only
disposition still working-tree-only (`M`), so its honesty depends on the closeout
commit including `.agents/release-adapter.yaml`. That file is staged into the
closeout commit, satisfying the condition.
