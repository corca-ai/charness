# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

Two records drive this work. The
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
reproduced 30 defects over 22 surfaces; **9 OPEN + 4 PARTIAL remain**. The
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
first-looked the other 146 surfaces: **101 leads still open**, 30 high severity, plus
its own `## Leads found while closing S27/S29/S33/S34` table. `CLOSED
(parent-reproduced <date>)` is the ONLY status that means a row is done.

## Current State

- **8 sweep rows are closed; this session took S27/S29/S33/S34** — the quality
  dup/nose readers that reported `clean`/`planned`/`intentional` over a scan that
  never happened. Each was reproduced in the parent first, and the new tests were
  proven to fail against pristine HEAD source by running them there.
- **The fix carried its own class TWICE MORE: 6 instances in round 1, 4 in round 2**
  (round 2 reviewed the repairs). All 14 reviewer-derived leads are in the sweep's own
  table; 12 were repaired in-slice. Budget the repair round, then a review OF the
  repair round — the second round is where the negative survivor count and the
  `degraded`-shaped hole were found.
- **The subsystem now has one rule:** `[]` means the producer DECLARED zero families;
  anything else is a reason. Shape reading lives in
  [nose_report_shape_lib](../skills/public/quality/scripts/nose_report_shape_lib.py);
  the unestablished-input gate behavior is pinned in
  [test_dup_ratchet_unestablished_inputs.py](../tests/quality_gates/test_dup_ratchet_unestablished_inputs.py).
- **Two leads were deliberately left OPEN** (R8, R9 in that table) because each needs
  its own design, not a one-line flip. R8 is a BLOCKING gate.
- **The fix itself tripped `dup-ratchet` and the length cap**; both were resolved by
  extraction/split, not by classifying self-inflicted duplication as intentional.

## Next Session

1. **R8 first: `changed_line_coverage_gate_lib.py:27`** — a failed `git diff` returns
   `[]`, which a blocking gate renders as "no eligible changed files", and the
   freshness fingerprint is vacuous in the same breath. Canonical trigger is a shallow
   CI fetch where `base_sha` is absent locally. Reproduce that before changing it.
2. **R9: the dup-ratchet zero-family backstop** (`check_dup_ratchet.py:138`) is gated on
   `and baseline_ids`, so an empty baseline disarms it, and the doc arm has no
   equivalent though its payload carries the counts. A naive fix false-refuses a
   clone-free consumer repo — design first.
3. **The sweep's remaining high-severity rows, reproducing each first.** Class (a) is
   still dominant. Prefer batches that share one subsystem, as S27/S29/S33/S34 did:
   the siblings are where the class hides.
4. **The original hunt's A5/A6, A8/A9/A10, B4/B5** (**E last** — per-changed-file
   mutation discrimination is a contract change).
5. **A3 is PARTIAL** (scheduled is not judged; needs a live staged/revert probe, not
   fixtures — [critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9);
   **D4 is PARTIAL and unclosable by this channel** (needs a release-specific channel
   independent of unauthenticated API quota — design before code); **containment-slice
   deferrals** F9/F10, **D28 remainder** and **sibling-scan Tier 2 finding D** are still
   un-dispositioned.

## Discuss

- **Probe the contract instead of arguing it.** The one contingent risk here (is blank
  nose stdout a clean scan?) was settled in two commands: an empty-but-valid scope root
  prints `{"families":[],...}` and exits 0; a nonexistent root exits 1 with non-JSON.
- **A guard that trusts a derived value is not a guard**: `or set()`, `or {}`,
  `ranking.total_families` are all downstream of the read whose failure it must detect.
- **A count that can go negative is the tell**, and a dead allowlist row is worse than
  none — one dead guard added by the first fix was hiding the real hole one line away.
- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed
  or `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [this slice's critique](../charness-artifacts/critique/2026-07-28-four-unestablished-scope-readers-in-the-quality-dup-nose-subsystem.md) · [C-cluster critique](../charness-artifacts/critique/2026-07-28-critique-evidence-floor-as-one-subsystem.md) · [distinct-channel critique](../charness-artifacts/critique/2026-07-28-distinct-channel-d4-d6-d8.md)
