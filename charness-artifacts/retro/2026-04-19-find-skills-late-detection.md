# Session Retro: Find-Skills Late Detection

## Context

- The reviewed unit is the portability cleanup around `10fa560` followed by the startup-artifact bug fix in `a7d382a`.
- I removed machine-specific `cautilus` and path assumptions, saw green validations, and still failed to identify that `charness-artifacts/find-skills/latest.*` dirt was a startup discovery bug until the user challenged the framing.
- The key question is not why the bug existed, but why I did not classify it earlier.

## Evidence Summary

- `git log --oneline -5` shows the portability cleanup commit `10fa560` landed before the actual startup-artifact fix `a7d382a`.
- `git show --stat --name-only 10fa560` shows that slice touched cautilus consumers, docs, and tests, but not `find-skills` inventory generation.
- `git show --stat --name-only a7d382a` shows the later fix touched `find-skills` source/plugin scripts, a dedicated regression test, AGENTS/handoff guidance, and retro memory.
- The earlier retro `charness-artifacts/retro/2026-04-19-find-skills-startup-artifact-classification.md` already captured the classification miss; this retro sharpens why I failed to catch it before the user intervened.

## Waste

- I substituted an easier question for the real one. Instead of asking whether the mandatory startup artifact still represented the same canonical inventory, I asked whether there were any obvious machine-specific path strings left.
- I over-trusted broad green validation. The suite proved that repo-local code paths and docs were healthy, but it did not cover the installed-plugin invocation path that the startup workflow actually exercises.
- Once I had a convenient explanation, `find-skills latest.*` became “ambient dirt” in my head. That framing lowered urgency and stopped me from diffing the artifact immediately.

## Critical Decisions

- The late detection happened because I treated repeated checked-in artifact churn as a reporting issue instead of an invariant violation.
- The relevant invariant was semantic parity of the canonical capability inventory, not absence of path literals.
- The missing test seam was the checked-in plugin export invoking `find-skills` against a source repo. Until that path had an explicit regression test, green status from other validators created false confidence.

## Expert Counterfactuals

- Daniel Kahneman: I fell into question substitution. I answered “did the portability grep come back clean?” when the real question was “did startup discovery preserve canonical inventory semantics?” The corrective move would have been to restate the invariant before trusting the search result.
- Gary Klein: the anomaly was the repeated dirty startup artifact. A recognition-primed response would have treated that anomaly as the signal, diffed it on first sight, and asked what system state could produce the same complaint across sessions.
- Michael Feathers: this was a seam problem. Before trusting the cleanup, I should have wrapped the installed-plugin invocation path in a regression test, because that was the only path capable of rewriting the checked-in inventory with packaged layout paths.

## Next Improvements

- workflow: whenever a mandatory startup step rewrites a checked-in artifact, diff it before describing it. Do not classify it in prose first.
- workflow: phrase closeout checks in terms of semantic invariants, not only string-pattern absence. For this seam the invariant is inventory parity, not path cleanliness.
- capability: keep the installed-plugin/source-repo parity test in `tests/test_find_skills.py` and add similar path-specific tests when a repo is both the source tree and a consumer of its exported plugin surface.
- memory: keep the AGENTS/handoff rule that startup `find-skills` diffs are either canonical inventory changes to commit or bugs to investigate immediately, never “unrelated dirt” by default.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-04-19-find-skills-late-detection.md
