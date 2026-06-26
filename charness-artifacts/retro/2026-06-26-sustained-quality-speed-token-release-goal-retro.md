# Retro: Sustained quality speed token release goal
Date: 2026-06-26

## Mode

session

## Context

Closeout retro for
`charness-artifacts/goals/2026-06-26-sustained-quality-speed-token-release.md`:
a roughly three-hour quality continuation run covering bug fixes, test runtime,
script runtime, token efficiency, and final publication as `v0.56.2`.

## Evidence Summary

- The run shipped forty-four local quality slices before the final release
  lane. Most slices reduced duplicated subprocess startup in tests while keeping
  representative real CLI proof.
- Late slices improved actual script paths: public-skill dogfood resolver lookup
  now uses import-safe resolver APIs with subprocess fallback; command-doc help
  probes and skill-surface preflight checks now share ordered parallel
  subprocess execution.
- The premature `v0.56.1` publication was corrected as a workflow miss: the
  release was not reverted after crossing the external boundary; local-only work
  resumed until the closeout reserve, then `v0.56.2` was published with release
  critique and distinct-channel verification.
- Final release proof is recorded in
  `charness-artifacts/release/latest.md`; GitHub release
  `https://github.com/corca-ai/charness/releases/tag/v0.56.2` is public, and
  `origin/main` points at `e7ad8668`.
- Goal-window probe:
  `charness-artifacts/probe/2026-06-26-sustained-quality-speed-token-release-host-log.json`
  records a parsed Codex window from `2026-06-26T09:34:18+09:00` to
  `2026-06-26T12:13:29+09:00`.

## Waste

- The first release lane started too early. The goal file already contained the
  timebox and closeout reserve, but the release phase was treated as available
  after broad proof instead of after the closeout window opened.
- Many small subprocess-conversion slices repeated the same proof pattern. That
  was low-risk but generated heavy artifact and commit churn; the later shared
  helper slice was the higher-leverage form of the same work.
- The first parallelization implementation duplicated a collection shape in two
  scripts and tripped `dup-ratchet`; extracting `run_processes_in_order()` was
  the right repair.
- Host metrics were initially probed without a goal window, which would have
  reported whole-session pressure as goal-scoped pressure. Recording the metric
  window before the final probe fixed the attribution.

## Critical Decisions

- Preserved real boundary smokes while moving repeated behavior assertions
  in-process. This kept the previous-session lesson intact: lower the proof
  layer only when a shipped-entrypoint check remains.
- Continued local quality work after the user's timing correction instead of
  stacking more remote side effects on top of the premature release.
- Published `v0.56.2` rather than trying to rewrite `v0.56.1`; the earlier tag
  and GitHub release had already crossed the public boundary.
- Treated the `dup-ratchet` failure as a real design issue, not a gate to waive,
  and extracted a shared helper before refreshing the reviewed baseline.

## Expert Counterfactuals

- A release-manager lens would have checked the goal's activation time and
  closeout reserve before any publish helper call; that would have avoided the
  `v0.56.1` timing miss.
- A refactoring lens would have asked earlier whether the two parallelization
  sites wanted a shared helper first; that would have avoided the duplicate
  shape and baseline churn.

## Sibling Search

- premature-release-phase axis: timeboxed goals with a final external side
  effect can recur in any `achieve` run. Decision: applied locally by keeping
  the goal artifact's timing correction and final closeout evidence explicit;
  no new global gate in this run because the existing closeout-shape checker
  cannot infer human intent around "roughly three hours" without over-firing.
- duplicated-parallel-helper axis: independent script optimizations can copy a
  concurrency pattern. Decision: applied by adding
  `scripts/subprocess_guard.py::run_processes_in_order()` and using it from both
  hot paths.
- unwindowed-host-probe axis: long goals can accidentally report thread-wide
  metrics. Decision: applied by recording `Host metric window:` before final
  probe and citing the windowed probe file.

## Next Improvements

- workflow: Before any final release/push in a timeboxed goal, explicitly check
  activation time, current time, closeout reserve, and done-early policy.
- capability: Prefer shared concurrency helpers before adding a second ordered
  parallel subprocess collector.
- workflow: For long goals, record the metric window before the first closeout
  host-log probe, not after seeing an `absent` window.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-06-26-sustained-quality-speed-token-release-goal-retro.md
