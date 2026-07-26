# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

No open issues; every move below names an owning artifact.

## Current State

- Standing operator direction: bug fixes, friction/rework, test/code speed. Last
  release tagged `"v2.11.0"`; [release state](../charness-artifacts/release/latest.md)
  is current truth, not that string.
- **A bar sized from another profile's samples cannot be honest.** A 2x-loose aarch64
  aggregate failed the very rule its cited precedent set (2.07x median) and no
  advisory would have caught it. Same slice: "sizing lives in one place" was false
  when written. [affinity-holes critique](../charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md)
- **`os.cpu_count()` was the wrong question in three places** — profile id, xdist
  worker width, eval jobs — and a gate's discriminator is its output, not its exit
  status (`du`).
- **A line-cap split is a seam decision, not a line count.** A new public MODULE plus a
  new CLI FLAG on an exported gate script sets MINOR — but that precedent does not
  reach an env var on a repo-root dev runner, which is PATCH. [bump-precedent critique](../charness-artifacts/critique/2026-07-26-v2-11-1-release-critique.md)

## Next Session

1. **`local-linux-aarch64-4cpu` has never been run.** Bars are x86_64-derived FLOORS
   with no aggregate (a 2x-loose one was reverted). On the first run there,
   `check_runtime_budget.py --runtime-profile local-linux-aarch64-4cpu
   --suggest-budgets` replaces the block; resolve `check-coverage: 60000` too. Two
   thin windows also owe a re-derive: 4-core x86_64 is n=3 with a red run in it, and
   `check-duplicates`/`dead-code-advisory` predate the 36-core barrier removal.
2. **Speed: the scheduler was the bottleneck, and the suite still is.** Profiling
   found xdist pre-assigning contiguous blocks; `--maxschedchunk 1` took the standing
   gate 45.5s -> 26.9s. What remains is the suite: `pytest` is ~35s of a ~38s
   `run-quality` run, and the longest single chains (`tests/charness_cli/` lifecycle
   tests) now set the floor. Next: seed-cache-back `seeded_quality_runner_repo`.
3. **The generated-retro signature keys on the emitted title.** Reword it and lesson
   scoring silently counts every emission as an independent recurrence again; an
   invariant test over `*-release-auto-retro.md` would catch that.
4. **The BSD/macOS `du` `illegal option` wording is unprobed**; and **the flag gate
   cannot see argument ORDER** (F7/F8, pinned not fixed:
   `REPO_ROOT.resolve() / "skills" / "public"` escapes the export-safety
   [predicate](../tests/quality_gates/test_export_safe_asset_paths.py)).
5. Unowned (signed off): critique packet tier mismatch, specdown preset duplication,
   `recommended_commands` in `plan_cautilus_proof.py`. Deferred: inline
   `.rglob`/`ls-files` pathspec discovery, D18, D38, `CODE_LANGUAGE_FAMILIES`
   expansion, zero/near-zero test-surface advisory, stale basetemps, #451's two
   unacted siblings. #453's sweep is closed; its mutation strength awaits a run.

## Discuss

- Write the violation before the guard. Run an artifact's owning `scaffold_*.py`
  first, and treat a counted limit as a planning input, not a retry loop.
- When a comment cites a precedent's rule, recompute it against the new number in the
  same edit: the citation is the claim, the arithmetic is the evidence. Likewise a
  test restating production's own expression pins the plumbing and none of the
  numbers — pin literals where an operator acts.
- Do not re-litigate the two refuted audit findings (dup-ratchet hard arm,
  boundary-bypass ratchet). #448 items wait for the next slice.

## References

- [affinity-holes critique](../charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md) · [fail-open critique](../charness-artifacts/critique/2026-07-26-seed-fixture-budget-fail-open.md) · [five-item critique](../charness-artifacts/critique/2026-07-26-handoff-backlog-five-items.md) · [#453 critique](../charness-artifacts/critique/2026-07-26-issue-453-resolution.md) · [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md) · [sweep critique](../charness-artifacts/critique/2026-07-26-453-sibling-sweep.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
