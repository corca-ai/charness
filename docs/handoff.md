# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh live state before acting: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.41.0 shipped and public release is verified.** `main`/`origin/main` are
  at `5051119d Record release verification for v0.41.0`; release tag
  `v0.41.0` is published. See
  [release latest](../charness-artifacts/release/latest.md) for proof.
- **#352 and #353 are closed.** The YouTube gather transcript UI fallback and
  issue-read-with-comments work shipped in v0.41.0; do not treat the prior
  handoff's #352/#353 push note as current work.
- **Open issues (`gh`, 2026-06-11): #354 and #184.** #354 is the active
  regression pickup. #184 remains an operator ideation decision about product
  success metrics, not the next implementation slice.
- **Release real-host proof is not fully closed.** The release helper ran the
  maintainer update path, and the 2026-06-12 quality pass closed the `nose`
  tool doctor/install/support checks on this host (nose 0.6.0 → 0.7.0; see
  [quality latest](../charness-artifacts/quality/latest.md)). The remaining
  v0.41.0 proof is the clean temp-home/second-machine operator path.

## Next Session

- **Activate the drafted `achieve` goal for the next bundle:**
  `/goal @charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md`.
  It covers the latest available `nose` install/update path, a quality scan with
  that `nose` surface available, public-doc hard-coupling audit, bounded
  subagent reviewer effort-policy cleanup, and the #354 fix.
- **Start #354 from the latest issue comments, not only the body.** The current
  signal is a scheduled mutation regression on `main`: changed-line coverage
  now blocks on the issue-read files even though local release closeout passed.
  Read the scheduled run's base/seed/test-selection mechanics before deciding
  whether the fix belongs in test selection, changed-line coverage production,
  or issue-read tests.
- **Fold the remaining v0.41.0 real-host proof into the same quality pass when
  practical.** Run the `nose` doctor/install/dry-run/sync-support/inventory
  checks from [release latest](../charness-artifacts/release/latest.md), and
  record which parts were real host proof vs advisory scan evidence.
- **Keep #184 separate.** Schedule it only if the operator wants a product
  metrics ideation session after #354 and the quality scan are closed.

## Discuss

- For the public-doc audit, decide whether historical issue-number references
  are acceptable in release notes/retro artifacts but not in public skills,
  reusable references, operator docs, or generated guidance.
- After #354 is fixed, decide whether an operator announcement is still useful
  for the v0.40.0 scheduled-mutation-lane change and the v0.41.0 YouTube/issue
  retrieval improvements.

## References

- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
- [quality latest](../charness-artifacts/quality/latest.md)
- [v0.41.0 release record](../charness-artifacts/release/latest.md)
