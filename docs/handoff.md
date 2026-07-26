# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

No open issues; the previous five-item list is closed. Every claim below names its source.

## Current State

- Standing operator direction: bug fixes, friction/rework, test/code speed.
  [release state](../charness-artifacts/release/latest.md) is current truth; get the
  tag from `git describe --tags --abbrev=0`, never from a transcribed string.
- **The stale-lib publish trap is enforced now, not documented.**
  [helper_provenance_lib](../scripts/helper_provenance_lib.py) refuses a helper from one
  charness tree pointed at a different charness SOURCE tree whose copy has drifted, naming
  the repo-local command rather than a remediation that loops. Guards sit at WRITE
  boundaries: the release helper reaches those directly, and a guard on a CLI that
  hand-writes the same bytes proves nothing — watched a drifted copy write the index.
- **Two handoff items were premises, not debt.** `check-duplicates` was renamed
  (`git log --oneline -S check-duplicates -- scripts/run-quality.sh`), so no run could
  re-derive its window; the named speed fix was worth 2.7ms. Check that a label still has
  a producer, and measure, before treating a handoff line as work.

## Next Session

1. **Lessons recur because the memory loop has no BIND path — fix this first**
   (operator-directed, anchor `handoff-next-session-lesson-identity`). Measured: 1594 of
   1596 lesson candidates sit at `independent_source_count == 1`, so the recurrence
   multiplier is 1.0 and selection is pure recency; one concept holds 7+ rows across 6
   dates and never won a slot, and two lessons that DID surface were violated within 2
   hours. Both halves are in the [recurrence retro](../charness-artifacts/retro/2026-07-26-lesson-recurrence-mechanism.md).
2. **The standing pytest gate is subprocess-startup-bound; that is where speed is.**
   Measured: ~25s wall at 16 workers, ~263s in-test CPU, 6959 spawns/run (4880 `git`,
   ~1840 `python`), ~31ms interpreter floor each. Next measured levers: ~390 per-test git
   seedings at ~24.5ms and in-process `run_script` conversion via
   [script_main](../tests/script_main.py) — not fixture caching, and not the deferrals
   already pinned by [test_hot_path_import_weight.py](../tests/quality_gates/test_hot_path_import_weight.py).
3. **`local-linux-aarch64-4cpu` has still never run on aarch64 hardware.** Its
   `check-coverage` is measured now, not invented (39500 at 1.4x, n=2). Owed: the real
   box, where `check_runtime_budget.py --runtime-profile local-linux-aarch64-4cpu
   --suggest-budgets` replaces the block, which still has NO aggregate bar behind its
   eight looser per-gate bars. The 4-core x86_64 read-only window still holds its one
   red; three more `--read-only` runs retire it.
4. **The nose baseline is one scanner version behind** (the dup gate names both versions
   every run). `--restamp-tool-version` refuses while the live family set differs, so
   `--write-baseline --confirm-baseline-delta` on the current scanner is the standing fix.
5. Unowned/deferred (signed off): the [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md) and #448/#451 siblings; #453's sweep is closed, its mutation strength awaits a run.

## Discuss

- **The bounded fresh-eye critique for the five-item slice did NOT run:** host
  instructions prohibited spawning subagents, which the repo contract treats as a
  higher-priority override. No same-agent pass was substituted, so the slice ships
  gate-verified (83/83) and review-unproven.
- A mechanism is a CLAIM ABOUT THE WORLD — run it in the same edit that writes it. Twice
  this turn: argparse ordering (`demo resolve --top x` exits 2, so the flag gate's union
  was unsound both ways) and BusyBox `du -k`.
- Do not re-litigate the two refuted audit findings (dup-ratchet hard arm,
  boundary-bypass ratchet).

## References

- [session retro](../charness-artifacts/retro/2026-07-26-xdist-scheduling-session-retro.md) · [affinity-holes critique](../charness-artifacts/critique/2026-07-26-runtime-profile-affinity-holes.md) · [flag-gate critique](../charness-artifacts/critique/2026-07-26-documented-command-flag-gate.md) · [five-item critique](../charness-artifacts/critique/2026-07-26-handoff-backlog-five-items.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
