# Charness Handoff

## Workflow Trigger

- With no explicit task, run `charness:handoff` chunked routing over the live
  backlog; an explicit user task keeps its own authority. Pick the smallest coherent
  slice and close it end-to-end: mutate canonical source, sync generated/plugin
  mirrors before validators, then prove with the mandated bounded critique.

## Continuation Capability

Two records now drive this work. The
[2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
reproduced 30 defects over 22 surfaces; **11 OPEN + 6 PARTIAL remain**, each with
a confirmed repro. The
[triage sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md)
then first-looked the other **146** never-examined surfaces: **109 leads survived
adversarial refutation** (34 refuted), 37 high severity. Only 4 are
parent-reproduced — read its status vocabulary before citing any row.

## Current State

- **The structural plan is executed except its last step.** Critique floor as one
  subsystem (LANDED); proof-surface authoring reclassified irreversible in the
  [north star](./design-north-star.md) (LANDED); triage sweep over the 146
  (LANDED — 109 survivors to burn down); birth trigger for new proof surfaces
  (LANDED as a closeout advisory). Remaining: adopt the scope affordance
  opportunistically as each gate is touched, never as a repo-wide sweep.
- **The burn-down is now the work.** Cycle cadence is coupled to closure capacity,
  not the calendar: do not start a new deep cycle while the prior one's confirmed
  rows are unclosed. Class (a) — empty input still returns PASS — is a third of
  the survivors, the same dominant shape as the first hunt.
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

1. **Work the sweep's 37 high-severity rows by reproducing each one first**, or
   continue the original hunt's **A5/A6**, **B4/B5**, **A8/A9/A10** (**E last** —
   per-changed-file mutation discrimination is a contract change). The sweep's
   `SUBAGENT-CONFIRMED` rows are stronger than leads and weaker than proof.
2. **C3/C4/C6 are narrowed on purpose**, residuals named in the bug hunt record:
   C3 misses the `## Packet Consumed` heading form; C6 still reads the COMMITTED
   range, so the slice under critique is invisible at validation time.
3. **Two siblings the C slice implicated:** `validate_retro_artifact.py:136` keeps
   the body-first `or` date fallback C2 replaced; two `LEGACY_UNDATABLE` rows are
   dead allowlist entries reading as live grandfather decisions.
4. **A3 is PARTIAL: scheduled is not judged.** Only `check_staged_mirror_drift`
   reads the index; the rest walk the worktree, and `git revert` runs no
   pre-commit hook (probed). [A3 critique](../charness-artifacts/critique/2026-07-27-a3-staged-scope.md) F8/F9.
5. **D4 is PARTIAL and cannot be closed by this channel.** A pushed tag with no
   release returns 200 with the tag present, before the release exists. Needs a
   release-specific channel independent of unauthenticated API quota.
6. **Containment-slice deferrals** F9/F10, **D28 remainder** and **sibling-scan
   Tier 2 finding D** are unchanged; see their linked records.

## Discuss

- **Fenced text is shown, not asserted.** Three gates have now read it as the
  author's claim; the C slice added a fourth before review caught it.
- **A widened content trigger buys a false refusal**, and a length floor is not a
  proof floor. Make the skip LOUD instead; read the declared VALUE, not the line.
- Run release/skill helpers from `skills/public/.../scripts/`, NOT an installed
  or `plugins/` copy ([RCA](../charness-artifacts/debug/2026-07-27-absent-guard-not-dead-guard.md)).

## References

- [chunked-routing contract](./handoff-chunked-routing.md) · [deferred decisions](./deferred-decisions.md) · [design north star](./design-north-star.md)
- [why the class stayed invisible](../charness-artifacts/audit/2026-07-28-why-the-hunt-class-stayed-invisible.md) · [sibling scan backlog](../charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md)
- [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md) · [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [C-cluster critique](../charness-artifacts/critique/2026-07-28-critique-evidence-floor-as-one-subsystem.md) · [publish-gate critique](../charness-artifacts/critique/2026-07-27-publish-gate-d1-d2-d3-d5.md) · [distinct-channel critique](../charness-artifacts/critique/2026-07-28-distinct-channel-d4-d6-d8.md)
