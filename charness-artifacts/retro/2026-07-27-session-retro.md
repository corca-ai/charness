# Session Retro
Date: 2026-07-27

## Context

One session under a handoff pickup: push the prior run (closing #459), close the
handoff's `Next Session` item 1 (deferred critique finding F9 — the chunked-routing
auto-draft dropped staleness facts at its last operator-facing surface), and publish
a release. Shipped `v2.11.2`, verified.

The retro exists because the release auto-retro asked whether a session retro was
owed, and because I hit three process traps in one session that turned out to share
one shape. The next slice is chosen off this retro's sibling scan.

## Window

`d8c4204b` (pre-push baseline) through `f1b55359` (post-release baton), 2026-07-27.
Seven commits, one published release, two critique rounds, seven bounded reviewers.

## Evidence Summary

- `git log d8c4204b..f1b55359` — seven commits including `eb90fa08` (release) and
  `4f19111d` (release verification).
- `scripts/run-quality.sh --release`: 83 passed / 0 failed at HEAD; 82/1 during the
  first two publish attempts (`validate-retro-lesson-index` failing).
- `grep -rn require_repo_local_helper` — five write-site callers, all in-repo
  artifact writes (`recent_lessons_lib.py:468`, `retro_persistence_lib.py:69`,
  `build_debug_seam_risk_index.py:133`, `persist_retro_artifact.py:53`,
  `refresh_recent_lessons.py:45`).
- Guard-coverage scan over every entrypoint containing `"push"` / `release create` /
  `issue close`: 18 files, **0 with a provenance guard** — including
  `publish_release_execute.py`, `publish_release_post_create.py`,
  `release_issue_closeout.py`, `issue_close.py`.
- Two critique artifacts from this session, ten findings each; four bounded
  reviewers in round one, three in round two.
- `mine_closeout_telemetry.py`: 4 recurring waste items, `over_slice` at 37
  occurrences with disposition `file-issue` — pre-existing, not this session's.

## Waste

- **Two failed publish attempts (~4 min of gate runtime each) from invoking the
  INSTALLED `publish_release.py` against the source tree.** The installed copy's
  `recent_lessons_lib` wrote an older lesson-index schema; the source repo's own
  `validate-retro-lesson-index` then rejected it and the helper rolled back. The
  first attempt I misdiagnosed entirely — I re-ran the standalone quality suite
  (83/0, clean), concluded the failure was release-state-specific, and only found
  the real cause by reading the guard's own docstring, which names this exact
  lineage ("four release publishes died to one shape").
  recurrence-class: guard-adjacent-to-action
- **A third publish attempt died on a dirty worktree** because my own diagnostic
  quality run had regenerated `sloc-inventory/latest.json`. Self-inflicted by
  debugging inside the same tree the helper requires clean.
- **The reviewer-boundary fingerprint `verify` was run after applying fixes**, so it
  reported drift it could not attribute. I had to reconcile it by hand in the
  critique artifact rather than cite it as evidence.
  recurrence-class: guard-adjacent-to-action
- **The critique packet binding staled twice**, once legitimately (fixes changed
  reviewed surfaces) and once spuriously (writing and staging the artifact that
  records the review). Cost: two regenerate-and-rebind cycles before finding
  `--reviewed-path`.
  recurrence-class: guard-adjacent-to-action

## Critical Decisions

- **Ran a counterweight pass in both critique rounds rather than folding it into an
  angle.** It paid twice by overturning premises I had already accepted: that the
  path staleness check never runs by default (it runs whenever a repo root resolves,
  `parse_handoff_entries.py:148-152`), and that the docs uniformly over-disclaim
  (`_repo_root_for_live_filters` can return `None`, so "clean OR not-checked" is
  literally true). Both would have shipped as wrong changes. I verified both
  corrections against source rather than accepting the reviewer's word.
- **Rejected six of ten code findings and four of ten release findings as
  over-worry.** Notably declined an unconditional "citation freshness" caveat bullet
  — it would have disclaimed a check that actually ran — and declined a
  `--bump-rationale` CLI flag, since the policy says "say why", not "add a surface".
- **Published with an explicit `--notes-file`.** The default `--generate-notes` with
  a one-commit delta collapses to the commit subject: a bare positive-capability
  claim for a feature whose whole premise is that an unmarked citation is *not* a
  freshness guarantee. This was the highest-value release finding.
- **Chose patch over minor and argued it in writing**, because the helper has no
  rationale field and `--part patch` would otherwise be a silent default.

## Trends vs Last Retro

The prior retro (`2026-07-27-handoff-backlog-minus-aarch64-goal-run.md`) recorded
"a lesson that ships as prose only has not shipped — both rules that bit this
session were correct, checked in, and unread." **This session is that trap's next
instance, one layer deeper.** The installed-helper rule was not merely written down;
it was *enforced in code* — and it still bit, because the enforcement sits on an
inner write rather than on the entrypoint. The trend line is: prose → enforced at
the wrong seam. The remedy the last retro applied (move the rule to always-loaded
`AGENTS.md`) does not address this variant.

## Expert Counterfactuals

**Douglas Engelbart — treat (Human + Language/Artifact/Methodology + Tooling) as
one unit; design T alongside LAM.** The repo has the *methodology* (use repo-local
helpers) and the *artifact* (`helper_provenance_lib.py`, with a docstring naming
four prior casualties). What it does not have is tooling placed where the human
actually acts. I invoke `publish_release.py`; the guard lives five call-frames down
inside a lesson-index write. Engelbart's move is to co-locate the check with the
act: the entrypoint that performs the irreversible thing is the seam that must
refuse. That reframes all three of this session's traps as one design defect rather
than three lapses of discipline — which is what the sibling scan below confirms.

**Direct counterfactual: had I read `helper_provenance_lib.py`'s docstring before
the second publish attempt rather than after**, I would have saved one full gate
cycle and the misdiagnosis. The docstring names the symptom exactly. I went to the
quality suite first because a failing gate reads as a quality problem — the error
message said "run `--write`", a remediation the docstring itself flags as one that
cannot terminate.

## Sibling Search

Waste pattern: **an integrity check is bound to an inner write site or an
unconstrained moment, not to the outer action it certifies.**

- same layer: every `skills/public/**` entrypoint performing an irreversible or external action (`publish_release_execute.py`, `publish_release_post_create.py`, `release_issue_closeout.py`, `issue_close.py`) | decision: same waste, fix now | proof: scanned 18 files matching `"push"`/`release create`/`issue close` for `require_repo_local_helper` — 0 hits, while all 5 guard callers are in-repo artifact writes (reversible surfaces)
- abstraction up: `scripts/reviewed_input_identity.py:128-190` default auto-path sweep includes the critique artifact and packet files it describes, and folds in the staged/unstaged split | decision: valid follow-up outside the slice | proof: observed twice this session; binding went stale from writing and staging the record itself, with nothing under review changed | follow-up: https://github.com/corca-ai/charness/issues/460
- specialization down: `skills/shared/scripts/reviewer_boundary_fingerprint.py` verify has no binding to the review window | decision: valid follow-up outside the slice | proof: ran verify after parent edits; got `ok: false` with five drifted paths, all parent-caused and none attributable to a reviewer that had no write tool | follow-up: https://github.com/corca-ai/charness/issues/461
- mental-model siblings: `scripts/check_changed_line_mutation_coverage.py` returns `ok: true, changed_line_proof: not-provable` when no base_sha resolves | decision: intentional boundary | proof: the gate self-labels "non-blocking by construction (matches workflow_dispatch, which computes no base_sha)" and `docs/handoff.md` already names CI as the only judge locally; the check is honest about being vacuous rather than silently passing

## Next Improvements

- workflow: when a gate fails inside a helper run, read the failing validator's own module docstring before re-running the broad suite. This session's docstring named the cause; the suite run cost a full cycle and produced a wrong hypothesis.
- capability: guard the irreversible entrypoints, not the inner writes. `publish_release.py` and `issue_close.py` should refuse a foreign-copy invocation at the entrypoint, where the operator can still act, rather than failing partway through bump/sync/quality. This is the next slice, and it is `P5`-shaped: a form check at an irreversible boundary, not a new judgment gate.
- memory: the recurrence-class tag `guard-adjacent-to-action` is introduced by this retro across three Waste bullets, so `recent_lessons_lib` grouping has a seed for it.

## Portable Candidate

- Abstract pattern: an integrity/provenance check placed at an inner write site rather than at the entrypoint performing the irreversible action, so a wrong invocation gets partway through before failing — and fails closed only when the drift happens to trip an unrelated gate.
- Triggering evidence: two failed publishes this session; four earlier release publishes named in `helper_provenance_lib.py`'s own docstring.
- Intended consumer/repo shape: any repo whose tooling is also *installed* elsewhere and can be invoked against its own source tree — i.e. any repo that ships a CLI/plugin it also dogfoods.
- Destination: not portable (yet) — the pattern is real but the abstraction is currently one repo's instance with n=1 outside-repo evidence. Revisit if a consuming repo reports the same shape.
- First-prompt acceptance claim: n/a while destination is `not portable`.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-27-session-retro.md
