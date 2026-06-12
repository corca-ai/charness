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

- **v0.42.0 shipped and public release is verified.** `main`/`origin/main` are
  at `9d4c5894 Record release verification for v0.42.0`; release tag
  `v0.42.0` is published and the maintainer install was auto-refreshed to
  0.42.0. See [release latest](../charness-artifacts/release/latest.md) for
  proof.
- **v0.42.0 content:** the 2026-06-12 session shipped the nose 0.7.0 quality
  pass (74/74 gates, clone advisory rebaselined,
  [quality latest](../charness-artifacts/quality/latest.md)) and
  template-first artifact-gate hardening (quality scaffold fill-time guards,
  `--report-all` on the quality/critique/debug standing gates, the
  Template-First Artifact Gates doctrine, deferred decision D28).
- **Open issues (`gh`, 2026-06-12): #184 only.** #354 is closed. #184 remains
  an operator ideation decision about product success metrics, not the next
  implementation slice.
- **Release real-host proof is not fully closed.** The `nose` tool
  doctor/install/sync-support checks are closed on this host (nose 0.7.0);
  the remaining proof is the clean temp-home/second-machine operator path,
  now against v0.42.0.

## Next Session

- **Re-scope the drafted `achieve` goal before activating it.** The
  2026-06-11 draft
  ([2026-06-11 goal draft](../charness-artifacts/goals/2026-06-11-354-nose-quality-public-doc-audit.md))
  is partially superseded: the nose install/update path, the quality scan,
  and #354 are done or closed. The unsuperseded remainder is the public-doc
  hard-coupling audit and the bounded subagent reviewer effort-policy
  cleanup; trim the goal to that scope or retire it.
- **Run the temp-home/second-machine operator path against v0.42.0 when
  practical** (the remaining real-host proof item in
  [release latest](../charness-artifacts/release/latest.md)).
- **D28 reopen triggers** ([deferred decisions](./deferred-decisions.md)): sibling-family
  fill guards, retro/handoff/ideation `--report-all`, and the scaffold
  `--write` mode wait for observed rework or an `emit_payload_main` touch.
- **Keep #184 separate.** Schedule it only if the operator wants a product
  metrics ideation session.

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
