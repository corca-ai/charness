# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

An evidence-surface bug hunt reproduced **30 defects** across the repo's proof
surfaces; eight families have landed. Every item carries status, file:line and a
confirmed repro in the
[bug hunt record](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
— read it before planning any of them. **11 OPEN + 6 PARTIAL remain.**

## Current State

- **The structural question is decided and half-executed.** Chosen: fix the
  critique floor as one subsystem (LANDED), reclassify proof-surface authoring as
  irreversible in the [north star](./design-north-star.md) (LANDED), then wire the
  hunt into something repeatable (NOT STARTED — the highest-value move left), and
  adopt the scope affordance opportunistically, never as a sweep.
- **The fix keeps reproducing the defect: 7 of 7 slices.** The C-cluster's three
  reviewers found eleven defects inside the fix; the sharpest was the scope
  record — added to stop verdicts over unestablished scope — asserting one on the
  common `run-quality.sh` path. Budget for review AND for the repair round after it.
- **CI is the only judge of the changed-line mutation gate.** Its local run
  outruns a usable timeout and returns `untrusted` when HEAD moves mid-run.
- Two of three bounded reviewers reported `envelope-unbound` (write tools visible
  despite the read-only agent type). None wrote; boundary verify was
  `parent-attributed`, zero unattributed drift. The typed restriction is not
  reliably applied on this host.

## Next Session

1. **A5/A6** (inside A3's commit-boundary floor), then **B4/B5**, then
   **A8/A9/A10**. **E last** — per-changed-file mutation discrimination is a
   contract change, not a patch.
2. **C3/C4/C6 are narrowed on purpose**, residuals named in the bug hunt record:
   C3 misses the `## Packet Consumed` heading form; C6 still reads the COMMITTED
   range, so the slice under critique is invisible at validation time.
3. **Two siblings the C slice implicated but did not touch:**
   `validate_retro_artifact.py:136` keeps the body-first `or` date fallback C2
   replaced; and two `LEGACY_UNDATABLE` allowlist rows name packets excluded by
   content kind, so they are dead rows reading as live decisions.
4. **A3 is PARTIAL: scheduled is not judged.** Only `check_staged_mirror_drift`
   reads the index; the rest walk the worktree, and `git revert` runs no
   pre-commit hook (probed). [A3 critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9.
5. **D4 is PARTIAL and cannot be closed by this channel.** A pushed tag with no
   release returns 200 with the tag present, before the release exists. Needs a
   release-specific channel independent of unauthenticated API quota.
6. **Two deferrals from the containment slice**
   ([critique](../charness-artifacts/critique/2026-07-27-provenance-containment.md)
   F9/F10): `capability_catalog_resolver` ranks `repo-plugin-export` above
   `repo-public-skill`; and the export-layout fact lives in three places.
7. **D28 remainder** and **sibling-scan Tier 2 finding D** are unchanged.

## Discuss

- **Fenced text is shown, not asserted.** Three gates have now read it as the
  author's claim; the C slice added a fourth before review caught it.
- **A widened content trigger buys a false refusal.** C3's widening turned
  `- Packet Consumed: n/a` into a demand for SHA256s for a packet declared absent.
  Read the declared VALUE, not just the line.
- **A scaffold that pre-loads an undisclosed failure costs a round-trip per
  artifact, forever.** If a floor refuses a scaffold default, say so in the stub.
- **A length floor is not a proof floor.** Make the skip LOUD instead.
- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed
  or `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [C-cluster critique](../charness-artifacts/critique/2026-07-28-critique-evidence-floor-as-one-subsystem.md) · [publish-gate critique](../charness-artifacts/critique/2026-07-27-publish-gate-d1-d2-d3-d5.md) · [distinct-channel critique](../charness-artifacts/critique/2026-07-28-distinct-channel-d4-d6-d8.md)
