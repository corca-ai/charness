# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- No loop is pre-queued. Decide the push/release of the committed D30 fix first
  (see Next Session), then start the next quality loop with `quality` for gate
  posture before `impl`. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **D30 (dup-ratchet id-rotation) is RESOLVED and committed, NOT yet pushed.**
  `origin/main` is `b460dc3a`; HEAD is `47767b8d` (impl) on top of `21e2b755`
  (spec checkpoint) — **ahead 2, unpushed**. The dup-ratchet code gate + clone
  advisory now key newness on a gate-computed, offset/path-independent **content
  fingerprint** (new `nose_fingerprint_lib`) instead of nose's offset/path-folding
  `family_id`, so a member-file line-shift no longer false-blocks. Baselines
  migrated in lockstep (`dup_ratchet_baseline.v2` / `nose_baseline.v3`,
  `code_family_fingerprints`, 541 ids) with the dup-review overlay re-keyed and the
  nose tool-manifest floor reconciled to `>=0.15.0`.
- Verified: full pytest (3797) + `run-quality.sh --read-only` (79/0, live
  dup-ratchet phase PASS) green; bounded fresh-eye spec critique (3 angles +
  counterweight) and impl critique (code-correctness CORRECT + migration-integrity
  SOUND + counterweight SHIP) folded in. **v0.56.7 remains the published version.**

## Next Session

- **First — decide push + release of the D30 fix.** It is consumer-visible (the
  dup-ratchet gate keys differently; baselines are schema-migrated and need no
  consumer action beyond `charness update` after a release). Push `main`, then run
  `release` for the lightest honest bump (patch) — or batch it with the next
  release. The fix is a behavior repair, so **patch** is the honest level.
- **Then pick the next quality loop:** start with `quality` for gate posture, then
  `impl` one narrow slice.

## Discuss

- Whether the changed-line mutation-coverage closeout
  (`run_slice_closeout.py --produce-mutation-coverage`) surfaced any surviving
  mutants on the migrated quality scripts; fold fixes before release if so.

## References

- [spec Slice 4 (canonical)](../charness-artifacts/spec/boy-scout-dup-ratchet.md)
- [deferred-decisions D30 (resolved)](./deferred-decisions.md)
- [impl critique packet](../charness-artifacts/critique/2026-06-27-103255-packet.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
