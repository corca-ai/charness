# Copy-Heavy Release-Only Critique
Date: 2026-05-21

## Execution

- status: blocked
- Fresh-Eye Satisfaction: blocked host signal: active delegation policy did not allow `spawn_agent` for this turn without a user subagent request.
- host signal: active developer delegation rule restricts `spawn_agent` use to turns where the user asks for subagents, delegation, or parallel agent work; this turn requested a direct test-policy correction.
- Target: test policy and standing-gate critique

## Change

Make copy-heavy repo/home/plugin tests release-only and add a deterministic
guard so future tests that use seeded repo/home copy fixtures cannot enter the
standing pre-push pytest set without `pytest.mark.release_only`.

## Findings

- Act Before Ship: do not rely on convention alone; the invariant belongs in
  `scripts/check_test_repo_copy_invariants.py` and its focused tests.
- Act Before Ship: mark all current helper/fixture users rather than only the
  largest temp-footprint files, because the maintainer intent is categorical.
- Bundle Anyway: update `docs/handoff.md` so future temp investigations first
  distinguish retained release/full-test sessions from current pre-push work.
- Valid But Defer: marker-aware nested-CLI inventory would improve reporting,
  but the standing pre-push enforcement path is already fixed by pytest marker
  exclusion plus the new invariant.

## Deliberately Not Doing

- Do not remove release/update/install lifecycle tests; they remain valuable
  pre-release proof.
- Do not add a PR CI workflow in this slice; maintainer policy keeps that
  paused.

## Next Move

Run the changed invariant, focused tests, release-only collection check, and
slice closeout; commit source, plugin export, tests, handoff, and this critique
artifact together.
