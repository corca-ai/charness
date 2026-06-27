# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- Next loop is queued below (D30). For a different quality loop, start with
  `quality` for gate posture, then `impl` one narrow slice. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.56.7 is published and verified.** `origin/main` is `0378b519`; tag
  `v0.56.7` points at `4307c2e2`. Public release confirmed by a distinct channel
  (https-fetch HTTP 200) and `gh release view`:
  `https://github.com/corca-ai/charness/releases/tag/v0.56.7`. `charness update`
  moved the install `0.56.6 -> 0.56.7`.
- 0.56.7 finished a prior agent's stopped release: the capability-first skill
  rollout (17 SKILL.md) plus proof-scope/validation tooling fixes. The dup-ratchet
  gate hard-failed on 11 rotated clone family ids; re-baselined gate + advisory in
  lockstep after proving net-zero new duplication (538 in / 538 out).

## Next Session

- **First loop — promote D30 (dup-ratchet id-rotation), start here:** see
  [deferred-decisions D30](./deferred-decisions.md). The offset-coupled family-id
  key forces a manual re-baseline on every scanned-file span shift; this release
  hit it again, so the reopen trigger fired. Fix beyond D30's sketch: have the
  gate compute its own **offset-independent content fingerprint** per family (it
  already gets member file + line ranges from nose), store it in the baseline, and
  key newness on that. This kills the false hard-block AND the false-negative D30
  feared from a path-set-only fingerprint. Cost: baseline schema migration +
  one-time re-baseline + a normalization that tracks nose clone semantics (the
  delicate part); flips the family-id rotation characterization test. Route:
  `spec` -> `critique` -> `impl`; impact files are listed in the D30 entry.
- **When reviewing broad pytest proof:** compare top-level closeout `changed_paths`
  with `recorded_broad_pytest_proofs.changed_paths`; any narrower record is
  evidence-scope drift, not JSON noise.

## Discuss

- D30 core trade: the gate's content fingerprint must match nose's grouping or the
  gate churns on its own input; that delicacy is why it earns a critique slice.

## References

- [deferred-decisions D30](./deferred-decisions.md)
- [release v0.56.7 full-delta critique](../charness-artifacts/critique/2026-06-27-release-0.56.7-full-delta.md)
- [dup-ratchet rotation debug](../charness-artifacts/debug/2026-06-21-dup-ratchet-family-id-rotation.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
