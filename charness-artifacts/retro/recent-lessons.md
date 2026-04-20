# Recent Retro Lessons

## Current Focus

- The reviewed unit is the portability cleanup around `10fa560` followed by the startup-artifact bug fix in `a7d382a`.
- I removed machine-specific `cautilus` and path assumptions, saw green validations, and still failed to identify that `charness-artifacts/find-skills/latest.*` dirt was a startup discovery bug until the user challenged the framing.
- The key question is not why the bug existed, but why I did not classify it earlier.

## Repeat Traps

- When a skill already has a repo-owned artifact validator, do not reconstruct
  the durable artifact shape from memory. Check the validator contract or a
  scaffold helper first.
- I substituted an easier question for the real one. Instead of asking whether the mandatory startup artifact still represented the same canonical inventory, I asked whether there were any obvious machine-specific path strings left.
- I over-trusted broad green validation. The suite proved that repo-local code paths and docs were healthy, but it did not cover the installed-plugin invocation path that the startup workflow actually exercises.
- Once I had a convenient explanation, `find-skills latest.*` became “ambient dirt” in my head. That framing lowered urgency and stopped me from diffing the artifact immediately.

## Next-Time Checklist

- workflow: if `validate-<artifact>` exists, run it or use the paired scaffold
  helper before drafting a new checked-in artifact.
- workflow: whenever a mandatory startup step rewrites a checked-in artifact, diff it before describing it. Do not classify it in prose first.
- workflow: phrase closeout checks in terms of semantic invariants, not only string-pattern absence. For this seam the invariant is inventory parity, not path cleanliness.
- capability: keep the installed-plugin/source-repo parity test in `tests/test_find_skills.py` and add similar path-specific tests when a repo is both the source tree and a consumer of its exported plugin surface.
- memory: keep the AGENTS/handoff rule that startup `find-skills` diffs are either canonical inventory changes to commit or bugs to investigate immediately, never “unrelated dirt” by default.

## Sources

- `charness-artifacts/retro/2026-04-19-find-skills-late-detection.md`
