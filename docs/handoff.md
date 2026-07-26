# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

No open issues; every move below names an owning artifact.

## Current State

- Standing operator direction: bug fixes, friction/rework, test/code speed.
  [release state](../charness-artifacts/release/latest.md) is current truth; get the
  tag from `git describe --tags --abbrev=0`, never from a transcribed string.
- **When the repo IS the tool, run the repo's copy.** Four publish attempts died to the
  release helper invoked from the INSTALLED plugin: its `recent_lessons_lib` predated
  this repo's `independent_source_count` change, so it wrote an old-schema lesson index
  the repo's own gate rejected. [bootstrap-resolution](../skills/shared/references/bootstrap-resolution.md)
  already says `SKILL_DIR=skills/public/<id>` inside the source tree.
- **A runtime bar is SIZED from a slice but ENFORCED on the 20-sample window median**,
  so during a regime change a correctly-derived bar can still sit ~2% from a blocking
  red. Converge the window first. [bars critique](../charness-artifacts/critique/2026-07-26-xdist-scheduler-chunking-and-the-budget-bars-it-invalidated.md)
- **A new public MODULE plus a new CLI FLAG on an exported gate script sets MINOR** —
  that precedent does not reach an env var on a repo-root dev runner, which is PATCH.
  [bump-precedent critique](../charness-artifacts/critique/2026-07-26-v2-11-1-release-critique.md)

## Next Session

1. **Make the installed helper refuse to write through stale libs.** The gate caught
   the drift above, but its message ("index is stale; run `--write`") names a fix that
   CANNOT work — `--write` emits the new schema and the next publish overwrites it.
   Warn or refuse when `--repo-root` is the charness source tree and versions differ.
   Same-shaped siblings: `persist_retro_artifact`, `write_current_artifact`,
   `build_debug_seam_risk_index`.
2. **`local-linux-aarch64-4cpu` has never been run.** Bars are x86_64-derived FLOORS
   with no aggregate. On the first run there, `check_runtime_budget.py
   --runtime-profile local-linux-aarch64-4cpu --suggest-budgets` replaces the block;
   resolve `check-coverage: 60000`. Thin windows owing a re-derive: 4-core x86_64 (n=4,
   one red), `check-duplicates`, `dead-code-advisory`.
3. **Speed: the scheduler is fixed, the suite is not.** `pytest` is now ~35s of a ~38s
   `run-quality` run and `tests/charness_cli/` lifecycle chains set the floor. Next:
   seed-cache-back `seeded_quality_runner_repo` (module-scoped, ~80 consumers, now
   rebuilt per worker instead of once or twice).
4. **The generated-retro signature keys on the emitted title.** Reword it and lesson
   scoring counts every emission as an independent recurrence again; an invariant test
   over `*-release-auto-retro.md` would catch it.
5. Unprobed/pinned-not-fixed: BSD/macOS `du` `illegal option` wording; the flag gate
   cannot see argument ORDER (F7/F8 — `REPO_ROOT.resolve() / "skills" / "public"`
   escapes the [export-safety predicate](../tests/quality_gates/test_export_safe_asset_paths.py)).
6. Unowned/deferred (signed off): see the [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
   and #448/#451 siblings; #453's sweep is closed, its mutation strength awaits a run.

## Discuss

- A version floor, an upstream mechanism, and a precedent's scope are CLAIMS ABOUT THE
  WORLD — check each against its source in the same edit that writes it. This session
  shipped one of each from inference and a reviewer caught all three.
- Run an artifact's owning `scaffold_*.py` first; treat a counted limit as a planning
  input, not a retry loop. Pin literals where an operator acts.
- Do not re-litigate the two refuted audit findings (dup-ratchet hard arm,
  boundary-bypass ratchet).

## References

- [session retro](../charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md) · [affinity-holes critique](../charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md) · [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
