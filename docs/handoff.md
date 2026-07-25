# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Continuation Capability

The only open issue is #453; every move below names an owning artifact that
already holds its evidence, so none of them needs re-deriving.

## Current State

- Published `2.8.0` — scope, verification, and the observer record are in the
  [release state](../charness-artifacts/release/latest.md). Standing operator
  direction: bug fixes, friction/rework reduction, test/code speed.
- **The handoff may not transcribe a fact a command regenerates** (versions,
  shas, as-of counts); a commit-time gate enforces it. A quoted value is an
  address, not a claim — that carve-out is load-bearing (it lets a post-publish
  baton reconcile name a version) and must not be closed.
- Speed posture is healthy and measured, not assumed: the broad gate is 81/0 and
  109.8s of serial gate work lands in ~62s wall. Detail and the refuted
  worker-cap lever: [quality review](../charness-artifacts/quality/latest.md).
- **#453 stays deliberately OPEN** for a human close; its fixes are pushed.

## Next Session

1. **Close #453** once the next **scheduled** mutation run is verified with
   `check_mutation_run_proof.py --claim changed-line --run-id <id>`. A dispatch
   re-run cannot prove it (no `base_sha`).
2. **Move `pytest` out of the third `flush_phase` batch in `run-quality.sh`** —
   the largest remaining speed lever (~13% of wall, bigger than the worker-cap
   raise measurement refuted); keep the `doc-duplicates` → `dup-ratchet` order.
3. **Retighten the `pytest` runtime budget** once the split sample window fills.
   The slack advisory will NOT prompt you: its factor is 3.0 and the ratio is
   2.15, so this is an owed deliberate revisit.
4. **Add a `--restamp-tool-version` path to `check_dup_ratchet.py`.**
   `_scoped_rebaseline` already restamps while refusing unnamed deltas, but
   `run()` reaches it only when an id is named — so the nose skew warning has no
   fix that does not also absorb the parked #448 items.
5. **Documented flags are still substring-only** — dropping `--run-checks` from
   its owning script leaves the drift guards green while the command exits 2.
   Needs argparse introspection, not another literal.
6. **Pinned, not fixed:** `REPO_ROOT.resolve() / "skills" / "public"` escapes the
   export-safety predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
7. Unowned: critique packet tier mismatch, specdown preset duplication, and
   `recommended_commands` in `plan_cautilus_proof.py` (its sweep is signed off —
   do not re-run it). Budgets are retuned for x86_64 only; check aarch64.
8. Still deferred: inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory, D18,
   D38, stale `charness-run-*` basetemp reaping, #451's two unacted siblings.

## Discuss

- Write the violation before writing the guard. Done four times this session and
  every demonstration changed the design.
- A gate blocking mid-slice is a design signal, not an obstacle to route around:
  the dup-ratchet block produced the shared markdown walk.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet
  hard arm or the boundary-bypass ratchet). #448 items wait for the next slice.

## References

- [release critique](../charness-artifacts/critique/2026-07-26-v2-8-0-release-critique.md) · [documented-command critique](../charness-artifacts/critique/2026-07-25-documented-command-resolution-gate.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [session retro](../charness-artifacts/retro/2026-07-25-session-retro.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
