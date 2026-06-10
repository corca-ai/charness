# charness Handoff

## Workflow Trigger

- Pickup = `charness:find-skills` -> **invoke `charness:handoff`**. Bare
  `/handoff` runs chunked routing over handoff entries plus live open issues;
  `## Next Session` is sequencing judgment, not the full queue.
- Refresh: `git status --short --branch`,
  `git log --oneline origin/main..HEAD`, `gh issue list --state open --limit 50`.
- Before mutating code/exports/validation, read
  [implementation discipline](./conventions/implementation-discipline.md) and
  [operating contract](./conventions/operating-contract.md).

## Current State

- **[Overnight quality goal](../charness-artifacts/goals/2026-06-10-overnight-quality-mainjob-350-then-push-release.md) COMPLETE; v0.40.0 SHIPPED.**
  Five quality slices + the pre-authorized push/release lane all verified:
  posture refreshed (quality/latest.md @ 2026-06-11); **#350 CLOSED**
  (at-cap checklist line + near-cap >=195/200 preflight warning, carrier
  31dbe3ad) and **#349 CLOSED** (carrier 763653c7) — both `verify-closeout`
  verified; bootstrap adapter unknown-field round-trip FIXED (aa8670c8 —
  it had silently dropped two live config blocks); `validate-handoff-artifact`
  now runs at COMMIT time when this file is staged (8288d54a); scheduled
  mutation lane reclassified — capacity drops of covered changed files are
  advisory, only uncovered changed lines block (da6b9a8e; the 47-auto-issue
  noise engine). Push 768ded84..a7185616; quality-core 27312178167 green;
  release v0.40.0 published + public-verified, install refresh auto-ran,
  live probe matched (installed SHA == a7d50604 == origin/main).
- Open issues (`gh`): **#184** (product metrics — operator ideation needed,
  SEVENTH exclusion; see Discuss); **#353** (NEW, off-goal: adapter_lib
  renderer hygiene — newline escaping, lossy rewrite normalization,
  falsy-explicit drops; latent, not user-visible).

## Next Session

- **Push the goal-closeout commit** (local-only by design; the single
  authorized push was spent on the lane). It carries the completed goal
  artifact, retro + recent-lessons refresh, disposition review, early-close
  report, and this handoff.
- **Deferred proof to consume:** the first scheduled `mutation-tests.yml`
  run with headSha >= a7185616 — it is ALSO the live proof of the
  scheduled-lane reclassification (expect: green on capacity drops; still
  red on score break / uncovered changed lines / partial runs).
- **#353** — bounded candidate when ranked: adapter_lib renderer hygiene.
- **#184** — operator decision first (Discuss), not a slice.

## Discuss

- **#184 product success metrics** — seventh consecutive deliberate
  exclusion; needs a dedicated operator `ideation` session shaped into its
  own goal. Decide: schedule it or explicitly close as not-now.
- **Announce the scheduled-mutation-lane change?** Optional operator call
  (release-critique nit): consumer operators tracking scheduled-run red
  rates will see them drop after v0.40.0; a short `announcement` would
  explain capacity-advisory vs still-blocking coverage.

## References

- [premerge-gate spec](../charness-artifacts/spec/mutation-changed-line-premerge-gate.md)
  (canonical; deferred follow-up now RESOLVED), [preflight coverage spec](../charness-artifacts/spec/artifact-shape-preflight-coverage.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md),
  [quality latest](../charness-artifacts/quality/latest.md),
  [v0.40.0 release record](../charness-artifacts/release/latest.md)
