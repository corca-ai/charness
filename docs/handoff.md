# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- For another quality-improvement loop, start with `quality` for gate posture,
  then move to `impl` for one narrow slice. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.56.7 is published and verified.** `origin/main` is `0378b519`; tag
  `v0.56.7` points at `4307c2e2`. Public release verified by a distinct channel
  (https-fetch HTTP 200) and `gh release view` (`isDraft:false`):
  `https://github.com/corca-ai/charness/releases/tag/v0.56.7`. `charness update`
  moved the install `0.56.6 -> 0.56.7`.
- 0.56.7 finished a prior agent's stopped release, shipping the full
  `v0.56.6..HEAD` delta: the capability-first skill surface rollout (17 SKILL.md
  contracts) plus proof-scope/validation-startup tooling fixes. The dup-ratchet
  gate was re-baselined in lockstep (gate + advisory) for 11 rotated family_ids
  after verifying net-zero new duplication; a full-delta release critique
  (4 angles + counterweight) corrected the notes before publish.

## Next Session

- **First high-value loop:** start with `quality` for gate posture, then `impl`
  one narrow slice. Candidate: closeout auto-discovery that offers the suggested
  focused mutation-coverage command without hiding the explicit proof path.
- **When reviewing broad pytest proof:** compare top-level closeout `changed_paths`
  with `recorded_broad_pytest_proofs.changed_paths`; any narrower proof record is
  evidence-scope drift, not harmless JSON noise.

## Discuss

- The dup-ratchet clone family ids rotate whenever a scanned file shifts span
  offsets; treat a constant-total in/out balance as a re-baseline (gate plus
  advisory in lockstep), not new duplication.

## References

- [release v0.56.7 proof](../charness-artifacts/release/latest.md)
- [release v0.56.7 full-delta critique](../charness-artifacts/critique/2026-06-27-release-0.56.7-full-delta.md)
- [v0.56.7 release notes](../charness-artifacts/release/notes-v0.56.7.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
