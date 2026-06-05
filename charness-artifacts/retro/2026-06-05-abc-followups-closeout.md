# Retro: A~C parallel follow-ups closeout (#307/#308/#309/#310/#312)
Date: 2026-06-05
Mode: session

## Context

Closeout review of the A~C parallel follow-up goal: gather/web-fetch acquisition
signal fidelity (#310/#309), release publish-flow resilience (#312 B1+B2), and
quality-gate economics (#307/#308). Six sub-slices landed one-commit-each on main
with `Close #N` carriers; bundle `--release` gate passed 72/0; all five issues
verified CLOSED.

## Evidence Summary

- Goal: `charness-artifacts/goals/2026-06-05-abc-followups-acquire-release-quality.md`.
- Goal artifact slice log (reproduce-then-fixed per bug) and the three bounded
  fresh-eye reviews recorded in
  `charness-artifacts/critique/2026-06-05-abc-followups-resolution-critique.md`.
- `./scripts/run-quality.sh --release` 72/0 on clean-tree SHA 9f08bdc3; pre-push
  gate 71/0.
- `issue_tool.py verify-closeout` status: verified for both classification groups.
- Host-log probe: token/tool-call/turn counts are available/derivable for the
  Claude session, but no goal-scoped metric window was recorded at activation, so
  no exact per-goal token figure is claimed (measured availability, not a number).

## Waste

- The bundle `--release` gate surfaced two real blockers the per-slice cheap
  checks missed: bare `#NNN` issue anchors in portable skill packages
  (`portable_package_issue_anchor`) and a duplicate boundary-bypass candidate
  from a redundant headroom subprocess test. Both cost one extra gate run plus a
  fix commit (9f08bdc3).
- Sharpest irony: the issue-anchor trap is a *sibling* of the attention-state
  banned-vocabulary trap that #308's authoring-preflight reference — authored in
  this same run — documents. I embedded `(#310)`/`(#312)` provenance comments in
  portable skill-package scripts without applying the very discipline I was
  writing. The constraint was discoverable in principle; I did not route my own
  authoring through it.
- Minor: an MD040 fence-language miss and two pathy-backtick doc-link misses on
  the new docs required quick re-runs (caught fast by the doc gates, not the
  bundle gate).

## Critical Decisions

- Executed mutations sequentially in the shared parent worktree rather than via
  parallel file-mutating workflow agents — the goal Boundaries mandate the shared
  worktree and the B2/C1 shared-surface guard forbids racing
  `run_slice_closeout`/usage-episode. The approved "fan out" was honored where it
  is safe: independent per-chunk reproduce-then-fixed and three parallel
  read-only fresh-eye reviews. This avoided merge/race hazards while keeping
  per-chunk independence.
- B2 cut = read-only-safe closeout (gate emission on `CHARNESS_QUALITY_MODE`)
  over test-robustness, fixing the #194 read-only-mutation invariant at the
  source rather than papering over one flaky test.
- Landed B2 before C1 on the shared usage-episode / `run_slice_closeout` surface
  per the serialize guard; C never raced B.

## Expert Counterfactuals

- Gary Klein (pre-mortem): a 30-second "what will the bundle gate flag that my
  per-slice checks will not?" before the gate would have named
  `validate_skill_ergonomics` and `check_boundary_bypass_ratchet` (both
  bundle-only relative to my per-slice set), catching both blockers before the
  ~85s gate run instead of after.
- Jef Raskin (discoverability): the fix is to make the constraint reachable at
  the moment of authoring, not just to know it exists. Changed action: extend the
  authoring-preflight reference to cover the portable-package gates and to say
  "run `validate_skill_ergonomics` after touching a skill package", so the next
  author routes through it.

## Next Improvements

- memory + capability (applied): extended `docs/conventions/authoring-preflight.md`
  with a "Portable skill packages" section covering `portable_package_issue_anchor`,
  dated-incident, and host-surface gates plus a fast `validate_skill_ergonomics`
  command — closing the exact trap hit this run and making the pre-mortem habit
  discoverable at authoring time.

## Sibling Search

Transferable pattern: "authoring a fix into a *constrained portable surface*
without first checking that surface's deterministic gate." Four-axis scan:

- Other skills/** files edited this run: only `acquire_public_url.py` (web-fetch)
  and `publish_release_resume.py` (release) gained anchors; both fixed and
  re-validated. No remaining skill-package siblings in this run's diff.
- Other constraint families on the same surfaces: dated-incident and host-surface
  gates are siblings of the issue-anchor gate — now all three are named in the
  preflight reference (the applied fix), so the sibling family is covered, not
  just the instance.
- Repo scripts (`scripts/agent_browser_runtime_guard.py`,
  `scripts/slice_closeout_usage_episode.py`): NOT portable packages, so their
  `#309`/`#194` comments are allowed; no action.
- Docs/tests: not gated for issue anchors; no action.

Decision: covered by the applied preflight extension; no new follow-up issue
filed (the goal's approved external-write scope was issue *close* only, and the
discoverability fix addresses the class). `n/a` short-circuit not used — a real
transferable pattern existed and was scanned.

## Persisted

Persisted: yes (path emitted by persist_retro_artifact.py below).
