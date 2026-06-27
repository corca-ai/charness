# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**; bare `/handoff`
  runs chunked routing over handoff + open issues.
- No loop is pre-queued. For the next quality loop, start with `quality` for gate
  posture, then `impl` one narrow slice. Before mutating, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **v0.56.8 is published and verified — it resolves D30 (dup-ratchet id-rotation).**
  `origin/main` is synced; tag `v0.56.8` points at `2f4e76e1`. Public release
  confirmed by four independent channels: the helper's https-fetch (HTTP 200),
  `gh release view` (isDraft false), `git ls-remote` (tag on origin), and the
  installed packaging version. `charness update` moved the install `0.56.7 -> 0.56.8`;
  `doctor` is green and `nose 0.15.0` matches the release's new `>=0.15.0` floor.
- v0.56.8 re-keyed the dup-ratchet code gate + clone advisory off nose's
  offset/path-folding `family_id` onto a gate-computed content fingerprint (new
  `nose_fingerprint_lib`), so a member-file line-shift no longer false-blocks.
  Baselines + the dup-review overlay were schema-migrated in lockstep. Spec, impl,
  and release each carried a bounded fresh-eye critique.

## Next Session

- **Pick the next quality loop:** start with `quality` for gate posture, then `impl`
  one narrow slice. The D30 follow-on residuals are deferred and not urgent
  (S4-Defer-1 token-aware fingerprint normalization; S4-Defer-3 subset-aware
  reduction diff) — reopen only on observed re-baseline friction.

## Discuss

- A `nose v0.16.0` upgrade is advisory-available; bumping the installed nose would
  regroup families and trigger the scanner-version skew WARNING -> a one-time
  lockstep re-baseline (by design, not a defect).

## References

- [spec Slice 4 (D30, DONE)](../charness-artifacts/spec/boy-scout-dup-ratchet.md)
- [deferred-decisions D30 (resolved)](./deferred-decisions.md)
- [release notes v0.56.8](../charness-artifacts/release/notes-v0.56.8.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md)
