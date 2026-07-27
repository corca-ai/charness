# Session Retro: Handoff backlog minus aarch64 goal run
Date: 2026-07-27
Mode: session

## Context

One goal run over the handoff backlog (aarch64 excluded by the operator), plus
issue #458 added mid-run. Six slices shipped across 16 commits; both open issues
closed on a green CI mutation run.

## Window

From chunked routing over the live backlog through the push, the settled-tree
mutation run, and the closure of #457 and #458.

## Waste

- **Three planned items were premises, not debt, and one was work that already
  shipped.** Sibling-scan Tier 1 A/B/C were fixed by an earlier commit;
  #448/#451/#453 were closed; and slice 1 was planned as a family-wide build when
  the one-pass machinery already existed and only three validators were unwired.
  Cost: a slice plan written against a tree nobody had checked, caught by a
  reviewer rather than by planning. (recurrence-class: premise-not-checked-against-source)
- **The same class then bit a fourth time inside the resolution.** The
  sibling-scan audit still listed Tier 1 as "worth fixing first", which is what
  generated the phantom slice — and I only found that because a stranded
  reviewer's recovered transcript said so. Fixing the instance without fixing the
  artifact that produced it is what let it recur.
  (recurrence-class: premise-not-checked-against-source)
- **A named subagent spawn stranded ~8 minutes and a full review packet**, and I
  reported the findings unrecoverable without running `reviewer_result.py get` —
  the diagnostic the same contract ships for exactly that case. Running it later
  recovered a finding I never independently derived. The rule and the recovery
  path were both in a reference I had listed and not opened.
  (recurrence-class: rule-exists-but-does-not-bind)
- **Two regex passes over 42 test files corrupted multi-line `subprocess.run`
  calls** before I switched to an AST pass that re-parses each file before
  writing. Two full revert cycles, both self-inflicted by editing structured code
  with line patterns. (recurrence-class: structured-edit-by-line-pattern)
- **A `git checkout -- tests/` silently reverted a conftest fixture** I had
  already written, and the suite still passed because this machine has a global
  git identity. The reviewer caught that the fix was not in the tree at all. A
  scoped revert with an unscoped path.
- **Iterated one line at a time against a counted limit** when trimming a debug
  artifact to its 180-line ceiling — four rounds — which is the exact
  counted-limit-as-retry-loop trap the repo already records.
  (recurrence-class: counted-limit-retry-loop)

## Critical Decisions

- Reverting the critique/debug default flip when the git history showed it was an
  explicit operator narrowing (`a930cc5f`), and routing the resulting polarity
  split to the operator via D28 instead of deciding it myself.
- Making spawn count, not wall-clock, the acceptance metric for the speed slice.
  The measured wall-clock ranges overlapped, so a wall-clock claim would have been
  noise dressed as a result.
- Restating rather than discharging the background/concurrency non-claim once I
  checked that my own observation did not actually cover explicit background.
- Recording the D28 reopen instead of shipping code that silently contradicted a
  checked-in decision.

## Trends vs Last Retro

The [lesson-recurrence retro](2026-07-26-lesson-recurrence-mechanism.md) said the
loop's write path is healthy and its bind path absent. This session is a direct
instance on both halves: the spawn-shape rule was written, correct, checked in,
listed in the skill I invoked — and did not bind. That retro's own fix landed here
(concept identity plus the re-derived weighting), but it cannot demonstrate value
until retros carry tags, so the digest is unchanged apart from its policy line.

## Expert Counterfactuals

**Engelbart — design T alongside LAM.** Every recurrence above was a rule that
existed only as prose. The two that got tooling this session (one-pass validator
output; the spawn-shape rule now test-pinned on an always-loaded surface) are the
only ones with a mechanism; the rest are still wishes. The premise-checking lesson
in particular has no T at all — nothing makes "verify the finding against source
before planning it" cheaper than not doing it.

**Klein — store lessons cue-first.** The premise trap fires at a specific cue: "a
handoff or audit line names a file:line". The lesson is stored as general advice
about checking claims. A cue-shaped form — "WHEN a backlog item cites file:line,
open it before planning" — belongs in the chunker's own output, where the cue
appears.

## Sibling Search

Transferable pattern: **a durable artifact keeps asserting work that is already
done**, because nothing updates the artifact when the work lands.

- same layer: `charness-artifacts/audit/2026-07-20-abstracted-pattern-sibling-scan.md`
  listed fixed Tier-1 findings as next-session work | decision: same waste, fix now
  | proof: corrected this session with the proving tests named.
- abstraction up: `docs/handoff.md` `## Next Session` entries generally — three of
  five were stale | decision: valid follow-up outside the slice | proof: measured
  this run; the chunker reads them as candidates with no staleness check |
  follow-up: deferred handoff-entry-staleness.
- specialization down: `docs/deferred-decisions.md` D28 asserted a narrowing the
  evidence had refuted | decision: same waste, fix now | proof: reopened and
  restated in `ab56e15f`.
- mental-model siblings: the frozen debug artifact's non-claims, which would have
  aged the same way | decision: same waste, fix now | proof: restated with a
  pointer to the recurrence record rather than left implying wider coverage.

## Next Improvements

- workflow: make backlog staleness checkable at chunk time rather than at review
  time — the chunker already parses `file:line` and issue refs from every entry,
  so it can report which cited paths/issues no longer resolve before an agent
  plans against them. Disposition: issue #459 (novel: no existing entry covers
  chunker-side staleness; the closest, D28, is about validator defaults)
- capability: the recurrence-class tag shipped this session has no data until
  retros carry it. This retro is the first to carry tags, which starts the corpus.
  Disposition: applied: recurrence-class tags on the Waste bullets above, grouped
  by `scripts/recent_lessons_lib.py`
- memory: a lesson that ships as prose only has not shipped. Both rules that bit
  this session were correct, checked in, and unread. Disposition: applied: the
  spawn-shape rule moved to always-loaded `AGENTS.md`, propagated to the
  consuming-repo template, and pinned by four tests in
  `tests/quality_gates/test_reviewer_result_delivery.py`

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-27-handoff-backlog-minus-aarch64-goal-run.md
