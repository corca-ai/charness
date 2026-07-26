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
  Release state: [release state](../charness-artifacts/release/latest.md).
- **A bar sized from another profile's samples cannot be honest.** A 2x-loose
  aarch64 aggregate cited a precedent whose own rule it failed (2.07x median) and no
  advisory would have caught it; the hole stays open, one command wide. Same slice:
  "sizing lives in one place" was false when written — only the constant moved, so
  the slack advisory proposed 10969 where `--suggest-budgets` said 11000.
  [affinity-holes critique](../charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md)
- **A gate's discriminator is its output, not its exit status** (`du`), and a runtime
  profile keys on affinity, not `os.cpu_count()` — measure under a CPU limit.
- **A line-cap split is a seam decision, not a line count.** And the last release
  went out minor, not the planned patch: a new exported flag plus a new exported
  module set the bump, twice running.
  [release critique](../charness-artifacts/critique/2026-07-26-v2-10-0-release-critique.md)

## Next Session

1. **`local-linux-aarch64-4cpu` has never been run.** Its bars are x86_64-derived
   FLOORS with no aggregate (a 2x-loose one was drafted and reverted for failing its
   own cited rule). On the first run there, `check_runtime_budget.py
   --runtime-profile local-linux-aarch64-4cpu --suggest-budgets` replaces the block
   from that machine's samples; do that instead of re-deriving from x86_64. Resolve
   its `check-coverage: 60000` then too — the 4-core block refuses to invent it.
2. **Two thin windows.** The 4-core x86_64 one is n=3 with a red run in it;
   `check-duplicates`/`dead-code-advisory` stay unbudgeted on 36-core because their
   samples predate the barrier removal. Re-derive both when the windows fill.
3. **The BSD/macOS `du` `illegal option` wording is unprobed** — BusyBox and GNU are
   measured against real binaries; that third wording is not.
4. **The flag gate cannot see argument ORDER** — F7/F8 of its critique. Pinned, not
   fixed: `REPO_ROOT.resolve() / "skills" / "public"` escapes the export-safety
   predicate ([decision point](../tests/quality_gates/test_export_safe_asset_paths.py)).
5. Unowned (signed off): critique packet tier mismatch, specdown preset
   duplication, `recommended_commands` in `plan_cautilus_proof.py`. Deferred: inline
   `.rglob`/`ls-files` pathspec discovery, D18, D38, `CODE_LANGUAGE_FAMILIES`
   expansion, zero/near-zero test-surface advisory, stale basetemps, #451's two
   unacted siblings. #453's sweep is closed with per-line coverage; its mutation
   strength waits on a scheduled run.

## Discuss

- Write the violation before writing the guard; reproduce a reviewer's finding
  before fixing it. A gate blocking mid-slice is a design signal, not an obstacle.
- A test restating production's own expression pins the plumbing and none of the
  numbers; pin literals where an operator acts on the value. Scope a budget block by
  observed cost on THAT profile — sibling parity skips what only this hardware finds
  expensive, and an aggregate cannot backstop it when one gate is the critical path.
- Check the payload shape before citing a green run: "not in blocking_targets" was
  an ABSENCE OF ANALYSIS. Ask what the measurement measured.
- Do not re-litigate the two refuted audit findings (removing the dup-ratchet hard
  arm or the boundary-bypass ratchet). #448 items wait for the next slice.

## References

- [affinity-holes critique](../charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md) · [fail-open critique](../charness-artifacts/critique/2026-07-26-seed-fixture-budget-fail-open.md) · [five-item critique](../charness-artifacts/critique/2026-07-26-handoff-backlog-five-items.md) · [#453 critique](../charness-artifacts/critique/2026-07-26-issue-453-resolution.md) · [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md) · [sweep critique](../charness-artifacts/critique/2026-07-26-453-sibling-sweep.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
