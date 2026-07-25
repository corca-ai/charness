# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. An explicit user task keeps its own authority. The next operator picks
  the smallest coherent backlog slice and closes it end-to-end: mutate canonical
  source, sync generated/plugin mirrors before validators, then prove with the
  mandated bounded fresh-eye critique before commit.

## Continuation Capability

The only open issue is #453; every move below names an owning artifact that holds
its evidence, so none needs re-deriving.

## Current State

- Published `2.8.0` ([release state](../charness-artifacts/release/latest.md)).
  Standing operator direction: bug fixes, friction/rework, test/code speed.
- **`check-documented-command-flags` is new and blocking** (broad-gate only,
  ~1.4s): a documented flag must be one its script's argparse accepts. Two live
  broken commands found on its first run; five reviewer-fixed defects and two
  residuals: [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md).
- **The handoff may not transcribe a fact a command regenerates** (versions, shas,
  as-of counts); a commit-time gate enforces it. A quoted value is an address,
  not a claim — that carve-out is load-bearing and must not be closed.
- **A gate's measured time is now co-scheduled**, so per-gate wall budgets partly
  measure contention; nine `(contended)` bars must be re-derived on any
  parallelism or core-count change — prefer per-gate CPU time over a hand
  relevel. Both refuted levers: [runner critique](../charness-artifacts/critique/2026-07-26-quality-runner-barrier-removal.md).
- **#453 stays deliberately OPEN** for a human close; its fixes are pushed.

## Next Session

1. **Close #453** once the next **scheduled** mutation run is verified with
   `check_mutation_run_proof.py --claim changed-line --run-id <id>`. A dispatch
   re-run cannot prove it (no `base_sha`).
2. **Re-measure `local-linux-aarch64-4cpu`.** Four bars are `(contended,
   derived)` — raised by this box's contention factor, not measured.
3. **The unpushed range cannot pass the pre-push mutation gate.** `--base-sha
   origin/main` blocks on 15 uncovered changed lines from `b12af528` in
   `check_seed_fixture_budget.py` and `record_quality_runtime.py` — and the first
   set IS the fail-open path (a permanently broken `du` reads as passing), so
   covering it and deciding bounded-retry-then-fail is one move, not two.
4. **Add a `--restamp-tool-version` path to `check_dup_ratchet.py`.** `run()`
   reaches the restamping `_scoped_rebaseline` only when an id is named, so the
   nose skew warning has no fix that does not absorb the parked #448 items.
5. **The flag gate cannot see argument ORDER** — F7/F8 of its critique. Both
   latent; both need per-token positions threaded through `split_arguments`.
6. **Pinned, not fixed:** `REPO_ROOT.resolve() / "skills" / "public"` escapes the
   export-safety predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
7. Unowned (sweep signed off): critique packet tier mismatch, specdown preset
   duplication, `recommended_commands` in `plan_cautilus_proof.py`. Still
   deferred: inline `.rglob`/`ls-files` pathspec discovery, D18, D38,
   `CODE_LANGUAGE_FAMILIES` expansion, zero/near-zero test-surface advisory,
   stale `charness-run-*` basetemps, #451's two unacted siblings.

## Discuss

- Write the violation before writing the guard; reproduce a reviewer's finding
  before fixing it; measure your own hypothesis before keeping it. All three
  fired again and all three changed code.
- A gate blocking mid-slice is a design signal, not an obstacle to route around.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet
  hard arm or the boundary-bypass ratchet). #448 items wait for the next slice.

## References

- [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md) · [runner critique](../charness-artifacts/critique/2026-07-26-quality-runner-barrier-removal.md) · [release critique](../charness-artifacts/critique/2026-07-26-v2-8-0-release-critique.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [session retro](../charness-artifacts/retro/2026-07-25-session-retro.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
