# v2.9.0 release critique
Date: 2026-07-26

## Decision Under Review

Publishing `charness` 2.9.0 over 2.8.0, covering `04dc1793` and `b60b12d2`: the
seed-budget gate stops passing a `du` scan that measured nothing, the
plugin-exported copy of that gate stops being dead on arrival, and the changed
lines that blocked the pre-push mutation gate are covered.

The bump was proposed as **patch** and the review changed it to **minor**.

## Failure Angles

One bounded read-only reviewer on the release decision itself, deliberately not
re-reviewing the code (two reviewers had already done that — see the
[fail-open critique](./2026-07-26-seed-fixture-budget-fail-open.md)):

- Bump level against `version-policy.md`, given a newly-blocking gate.
- Downstream blast radius: which consumer surfaces change behavior on upgrade,
  and whether any upgrade path leaves an operator with no exit.
- Residual honesty: which of the three recorded residuals are release-blocking
  rather than release-noted.
- Surface consistency: does any checked-in doc still describe the old fail-open.
- Version surface drift: any version-bearing file a bump would miss.

Parent-side worktree+index integrity was fingerprinted around the review
(`reviewer_boundary_fingerprint.py` snapshot/verify): `{"ok": true, "drift": []}`.

## What The Review Changed

- **The bump level was wrong.** `patch` covers "runtime corrections that preserve
  the same public shape". The shape did not stay the same: a new public flag
  (`--advisory-on-scan-failure`) on an exported gate script, and a new module
  shipped into the public plugin surface
  (`skills/public/quality/scripts/pytest_temp_scan_lib.py`, re-exported through
  `standing_test_economics_lib`). Both are `minor` under "new operator-facing
  commands ... that do not break existing callers". The reviewer also found the
  precedent: v2.8.0 shipped the same class — blocking gates getting stricter —
  as minor, with an explicit stricter-gates disclosure. Shipping the same class
  as patch one release later, with less disclosure, is the inconsistency.
- **The escape hatch was unreachable from where the gate fires.** This is the
  finding that mattered most. `run-quality.sh` fixed the gate's argv, and
  `CHARNESS_QUALITY_LABELS` is an **allowlist** — an operator cannot subtract one
  gate without enumerating the other ~80. So the gate's own remediation text
  named a flag that could not be passed on the pre-push path where it prints,
  leaving `git push --no-verify` as the only real exit: all 82 gates off to get
  past one. Verified independently (`label_is_selected` returns 1 for any
  unlisted label) before fixing. `CHARNESS_SEED_FIXTURE_ADVISORY=1` now threads
  the flag through the runner, the remediation text names both reachable paths,
  and a parametrized runner test pins the argv with and without the env var.
  This also repairs the previously-recorded BusyBox residual, whose stated
  mitigation was the same unreachable flag.
- **The handoff still described the fail-open as live** and the work as unpushed.
  Reconciled.

## Counterweight Pass

The reviewer graded down as often as up, and two of its own framings were
corrected by its own evidence:

- **The blast-radius premise was weaker than the brief assumed.** The reviewer
  checked and found CI does not run the broad bundle, the docs-only pre-push
  subset excludes this gate, and `quality_bootstrap_render.py` does not give
  downstream repos this gate at all. The felt path is the maintainer pre-push,
  not every consumer. That narrows the risk without excusing the unreachable
  hatch.
- **Residual F13 was misfiled and is not blocking.** It points at the
  `record_quality_runtime.py` half of the bundle, not the seed gate; the seed
  gate is CLI-exercised for all five classifications including `--json` and the
  new flag.
- **Residual F11 (partial-scan under-count) stays noted, not blocking.** It fails
  only toward a missed breach, never a false block, against four orders of
  magnitude of margin.
- **Version surfaces are clean.** All four generated files derive from
  `packaging/charness.json`, and all three packaging version keys are written
  together, so a half-bump is not reachable. `.agents/plugins/marketplace.json`
  carries no version key and correctly is not a version surface.

Not acted on: the reviewer suggested confirming the v2.8.0 notes file it cited as
precedent, which is not present under `charness-artifacts/release/`. The
precedent argument stands on the v2.8.0 release critique itself, which is
present, so this is recorded rather than chased.

## Residuals

- **`du_timeout` blocks and is not classified a capability gap.** With
  `PYTEST_DEBUG_TEMPROOT` unset the scan falls back to the shared
  `/tmp/pytest-of-<user>`, where an unrelated large tree could plausibly exceed
  the 30s cap. This repo's runner keys the temp root per repo, so only direct
  invocation is exposed. Surfaced by this review, unrecorded before it, and
  carried to the handoff rather than fixed inside a release slice.
- **BusyBox/BSD `du` behavior remains inferred, not probed.** No real Alpine or
  macOS run backs the usage-error token list. The escape hatch is now reachable
  on both paths, which is what made this recordable rather than blocking.
- **The partial-scan under-count is reported but not gated** (`partial` in the
  payload, no threshold on it).

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/release/references/version-policy.md:14 | action: fix | note: patch claimed on "preserves the same public shape", but a new public flag and a new public module are additive operator surface; bumped to minor
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/run-quality.sh:620 | action: fix | note: the gate's remediation named a flag the runner could not pass and CHARNESS_QUALITY_LABELS is an allowlist, so the real exit was --no-verify; env pass-through added and pinned by a runner test
- F3 | bin: act-before-ship | evidence: strong | ref: docs/handoff.md:40 | action: fix | note: the handoff still described the fail-open as live and the range as unpushed
- F4 | bin: bundle-anyway | evidence: moderate | ref: scripts/check_seed_fixture_budget.py:179 | action: fix | note: the remediation text now names both reachable paths rather than only the direct-invocation flag
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/pytest_temp_scan_lib.py:40 | action: document | note: du_timeout blocks without being a capability gap; only direct invocation with PYTEST_DEBUG_TEMPROOT unset is exposed, carried to the handoff
- F6 | bin: over-worry | evidence: moderate | ref: charness-artifacts/critique/2026-07-26-seed-fixture-budget-fail-open.md:115 | action: defer | note: residual F13 points at the runtime recorder, not this gate, which is CLI-exercised for every classification
- F7 | bin: over-worry | evidence: strong | ref: packaging/charness.json:5 | action: defer | note: all version surfaces derive from one packaging manifest and all three keys are written together, so a half-bump is not reachable
- F8 | bin: valid-but-defer | evidence: weak | ref: charness-artifacts/critique/2026-07-26-v2-8-0-release-critique.md:45 | action: defer | note: the v2.8.0 notes file cited as precedent is absent from charness-artifacts/release/; the precedent stands on the release critique itself

## Reviewer Tier Evidence

- Requested tier: typed `bounded-reviewer` subagent (read-only: Read/Grep/Glob), session-model inheritance per the Claude Code host branch of the repo subagent contract.
- Requested spawn fields: `subagent_type: bounded-reviewer`, release-decision scope prompt, no model or effort override.
- Host exposure state: applied
- Application state: host-confirmed: the reviewer reported the envelope bound with Read/Grep/Glob only and no Bash/Edit/Write/Agent.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated

The reviewer had no Bash, so it could not read the commit stats, the published
v2.8.0 release body, or run the gate live; it named all three gaps. The two
findings that changed the release were re-derived here against the running code
before being acted on.

## Reviewed Input Identity

<!-- No prepared packet was consumed; the reviewer read the pushed worktree at b60b12d2 directly. -->

## Boundary Ownership

- Producer: the seed-budget gate, which decides whether a scan failure blocks a push.
- Consumer: the operator at the pre-push boundary, who needs a way past a block that is not "turn off every gate".
- Owning surface: `run-quality.sh` owns the invocation, so it owns whether the gate's documented escape hatch is reachable.
- Verdict: moved-to-owner
