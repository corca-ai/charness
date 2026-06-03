# Retro — 291 292 284 activation/index/preflight goal

Mode: session

## Context

This retro reviews the goal that resolved #291, #292, and #284 in one bundle:
activation readiness, staged-index test isolation, and skill-surface preflight.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`.
- Closeout critique:
  `charness-artifacts/critique/2026-06-04-291-292-284-final-bundle.md`.
- Issue closeout carrier:
  `charness-artifacts/issue/2026-06-04-291-292-284-closeout.md`.
- Final local broad quality passed 70/70 before push and again in the successful
  pre-push gate.

## Waste

- The first final broad gate failed on two test-structure issues that focused
  tests did not reveal: the isolated repo-copy e2e test needed
  `pytest.mark.release_only`, and #284 tests introduced a boundary-bypass
  candidate by spawning an import-safe script.
- The first push attempt hit a live usage-episode snapshot flake in one host hook
  test. A focused rerun passed, and the second pre-push broad gate passed.
- The goal artifact needed one more closeout repair pass because the After-phase
  evidence floors require explicit bound `Retro:`, `Host log probe:`,
  `Disposition review:`, `Gather:`, and `Issue closeout:` lines.

## Critical Decisions

- Fixing #291 first avoided running the rest of the goal under a warning-only
  activation-readiness model.
- Keeping #292's production staged mirror gate intact preserved the real
  pre-commit protection while moving standing pytest to a private repo root.
- Keeping #284 as a repo-local authoring preflight avoided turning it into
  another broad quality wrapper.

## Expert Counterfactuals

- Gary Klein: a pre-mortem before final broad quality would have asked which
  policy gates focused tests cannot see and would have caught release-only and
  boundary-bypass constraints earlier.
- Daniel Kahneman: a checklist would have separated "read-only test" from
  "safe for shared state" and "functional helper test" from "testability
  boundary smell."

## Next Improvements

- applied: `3b7ed973` marked the copy-heavy isolated repo test release-only and
  converted #284 tests to the in-process preflight API.
- applied: the new preflight helper and implementation-discipline guidance make
  skill-surface headroom/coupling checks executable before broad quality.
- no new issue: broader index-sensitive test inventory and installed-host proof
  are valid future work, but they are outside this bounded issue bundle and are
  recorded as non-claims.

## Sibling Search

n/a — the transferable skill-surface waste pattern was the target of #284 and
was implemented in this goal; the remaining closeout misses were fixed directly
in this bundle.

## Persisted

yes — `charness-artifacts/retro/2026-06-04-291-292-284-activation-index-and-skill-preflight.md`.
