# Resolution Critique — issues 632, 631, 630 verify-and-close
Date: 2026-08-18

## Decision Under Review

Close [#632](https://github.com/corca-ai/charness/issues/632),
[#631](https://github.com/corca-ai/charness/issues/631), and
[#630](https://github.com/corca-ai/charness/issues/630) as fixed on main, each on
executed reproductions run this session plus one bounded fresh-eye closeout round.

## Failure Angles

Raised by the bounded reviewer, not the author:

- **#632 residual emissions.** After the citation-module fix, does any error path still
  emit `scripts/build_retro_lesson_selection_index.py` or `skills/public/retro/...`
  unconditionally to a consumer? The reviewer's broad grep found only docstrings,
  tests, and repo-internal gate commands — plus one real residue: the unreachable
  fallback in `session_start_lesson_context.py` still used the banned `<charness>`
  placeholder and the `skills/public/` spelling. Repaired this session (commit
  `de9bb2fcc`); the fallback now spells the bare `CHARNESS_PLUGIN_DIR` token.
- **#631 both directions.** Retiring the false positive must not retire the true
  positive: `foreign_scores` still flags an outcome event citing a retro that does not
  claim the session, pinned by `test_a_genuinely_foreign_encounter_still_fails`; and
  the modern recorder contract (`--source-retro` = the retro RECORDING the encounter)
  prevents recurrence for new-style events.
- **#630 sibling sweep.** No bare `npm exec` survives anywhere in the tree, a gate test
  now forbids the class in any language, and the deliberate non-unification of
  `check-secrets.sh`'s `--no-install` is recorded at the decision site.

## Counterweight Pass

- #632's third defect (`seed-lesson-ledger.py --repo-root`) is NOT fixed here and needs
  no fix here: the script appears nowhere in this repo's tree, artifacts, or history
  (`git log --all -S seed-lesson-ledger` returns nothing) — it is consumer-owned. The
  close states this as a non-claim rather than a repair.
- #631's reviewer minor — no single end-to-end test drives a two-origin session with
  two NEW-style outcome events through the reconciler — is a coverage nicety; the pass
  is derivable from the shipped ownership tests, and the executed reproduction of the
  issue's exact scenario returned `ok: true` with zero violations.
- The reviewer could not run `git log` (read-only toolset); the parent executed the
  history probe for `seed-lesson-ledger` itself and it returned empty.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/session_start_lesson_context.py | action: fix | note: unreachable fallback used the banned `<charness>` placeholder and a `skills/public/` spelling no consumer tree has; repaired to the bare `CHARNESS_PLUGIN_DIR` token with the fallback test updated.
- F2 | bin: valid-but-defer | evidence: moderate | ref: tests/test_lesson_outcome_vocabulary.py | action: defer | note: a two-origin two-outcome-event end-to-end reconciler test would pin #631's modern path directly; semantics make the pass derivable from shipped tests, so deferred rather than blocking the close.
- F3 | bin: over-worry | evidence: weak | ref: skills/public/retro/scripts/plan_retro_run.py | action: defer | note: a plan packet carries a repo-local script literal but pairs it with an `available: false` flag when absent — not an unconditional instruction, and outside the lesson-session error surface #632 names.

## Reviewer Tier Evidence

- Requested tier: high-leverage (repo default for issue closeout review).
- Requested spawn fields: subagent_type=bounded-reviewer, unnamed one-shot spawn, no
  model/effort override (session-inherited).
- Host exposure state: applied
- Application state: host-confirmed: typed `bounded-reviewer` spawn accepted and ran
  with the read-only toolset (Read/Grep/Glob only, per its own envelope report).
- Delivery state: findings-received

## Reviewed Input Identity

<!-- No packet was consumed: this critique reviews verify-and-close decisions over
repo state at 5a8d2005a, not a prepared packet. -->

## Boundary Ownership

- Producer: `lesson_command_citation.py` mints runnable-path citations (#632);
  `lesson_score_outcome_lib.py` owns score-event ownership semantics (#631);
  `check-markdown.sh` owns its own resolver tiers (#630).
- Consumer: lesson-session error surfaces, the continuity reconciler, and the
  commit-time markdown gate respectively.
- Owning surface: lesson-loop error/citation surfaces and repo gate scripts.
- Verdict: owned-correctly

## Fresh-Eye Satisfaction

`parent-delegated`. One bounded reviewer, spawned unnamed as `bounded-reviewer`,
covered all three issues with per-issue verdicts CLOSE-SAFE. Boundary fingerprint
verify around the round: `ok: true`, `verdict: parent-attributed`, `drift: []`
(window w-20260817T225724Z-928775; the parent declared its one in-window write,
`scripts/validate_debug_artifact.py`, a surface none of the three issues touch).

## Non-Claims

- #632 defect 3 is consumer-owned and not repaired by this close.
- No claim that installed consumer copies carry these fixes before their next upgrade.
- The #636-residual validator work reviewed in this session's other round is not part
  of these three closes.
