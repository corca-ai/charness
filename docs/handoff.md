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

- Published `2.8.0` — scope and verification live in the
  [release state](../charness-artifacts/release/latest.md). Standing operator
  direction: bug fixes, friction/rework reduction, test/code speed.
- **The handoff may not transcribe a fact a command regenerates** (versions,
  shas, as-of counts); a commit-time gate enforces it. A quoted value is an
  address, not a claim — that carve-out is load-bearing (it lets a post-publish
  baton reconcile name a version) and must not be closed.
- Speed posture is measured, not assumed: the broad gate is 81/0 and every mode
  got faster. Numbers, both refuted levers (worker cap, concurrency cap), and the
  cost: [runner critique](../charness-artifacts/critique/2026-07-26-quality-runner-barrier-removal.md).
- **A gate's measured time is now co-scheduled.** Cheap gates run alongside
  `pytest`, so per-gate wall budgets partly measure contention; nine bars are
  marked `(contended)` in the adapter. Re-derive them on any parallelism or
  core-count change — prefer per-gate CPU time over another hand relevel.
- **#453 stays deliberately OPEN** for a human close; its fixes are pushed.

## Next Session

1. **Close #453** once the next **scheduled** mutation run is verified with
   `check_mutation_run_proof.py --claim changed-line --run-id <id>`. A dispatch
   re-run cannot prove it (no `base_sha`).
2. **Re-measure the `local-linux-aarch64-4cpu` profile.** Four bars are now
   `(contended, derived)` — raised by this box's contention factor to avoid a
   false red there, not measured. Deliberately loose; not evidence.
3. **`check-seed-fixture-budget` fails open on ANY scan error.** Ordering fixed
   the live instance (no longer races pytest's teardown), but a permanently
   broken `du` still reads as passing; bounded-retry-then-fail is a design call.
4. **Add a `--restamp-tool-version` path to `check_dup_ratchet.py`.** `run()`
   reaches the restamping `_scoped_rebaseline` only when an id is named, so the
   nose skew warning has no fix that does not absorb the parked #448 items.
5. **Documented flags are still substring-only** — dropping `--run-checks` from
   its owning script leaves the drift guards green while the command exits 2.
6. **Pinned, not fixed:** `REPO_ROOT.resolve() / "skills" / "public"` escapes the
   export-safety predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
7. Unowned: critique packet tier mismatch, specdown preset duplication, and
   `recommended_commands` in `plan_cautilus_proof.py` (sweep signed off).
8. Still deferred: inline `.rglob`/`ls-files` pathspec discovery,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory, D18,
   D38, stale `charness-run-*` basetemps, #451's two unacted siblings.

## Discuss

- Write the violation before writing the guard.
- **Reproduce a reviewer's finding before fixing it, and measure your own
  hypothesis before keeping it.** Both happened this session; both changed code.
- A gate blocking mid-slice is a design signal, not an obstacle to route around.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet
  hard arm or the boundary-bypass ratchet). #448 items wait for the next slice.

## References

- [runner critique](../charness-artifacts/critique/2026-07-26-quality-runner-barrier-removal.md) · [release critique](../charness-artifacts/critique/2026-07-26-v2-8-0-release-critique.md) · [documented-command critique](../charness-artifacts/critique/2026-07-25-documented-command-resolution-gate.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [session retro](../charness-artifacts/retro/2026-07-25-session-retro.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
