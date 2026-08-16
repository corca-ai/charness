# S8: the handoff five, and the aggregate coverage debt
Date: 2026-08-16

## Context

The handoff named five items blocking the deferred 6.0.0 publish, and the owner asked
for all outstanding debt to be paid before pushing 51 commits. Four of the five are
consumer-facing defects reported from real consuming repos; the fifth is a measurement
gap. Behind them sat the item the previous session called "the largest open question
against publishing": 244 uncovered changed lines across 69 files, accumulated over the
whole unpushed range, which no slice had ever proved because each proved only its own
base.

## Evidence Summary

- Changed-line aggregate against `merge-base origin/main HEAD`: 69 blocked files /
  244 uncovered lines before, `every mapped changed pool file's changed lines are
  covered` after. Re-prove with
  [prepush_focused_changed_line_coverage.py](../../scripts/prepush_focused_changed_line_coverage.py)
  `--base-sha $(git merge-base origin/main HEAD)`.
- Standing suite 9943 -> 9945 passing; `./scripts/run-quality.sh --release` went from
  6 failed to 0 across three runs.
- Four bounded reviewers over two rounds produced 27 findings; 10 were acted on before
  shipping, 1 deferred, 1 dismissed as over-worry.
- Three lines turned out to be UNREACHABLE and were deleted rather than covered:
  a duplicated emptiness guard in
  [check_closeout_classification_parity.py](../../scripts/check_closeout_classification_parity.py),
  a `relative_to` guard in [what_reads_this.py](../../scripts/what_reads_this.py) whose
  candidates are all built from the root it compares against, and a
  [record_usage_feedback.py](../../scripts/record_usage_feedback.py) handler that
  declared four exceptions its loader absorbs while omitting the one that escapes.

## Waste

The largest single waste was self-inflicted and caught by review, not by me. I
retargeted eleven cwd-relative instruction sites to `<repo-root>/` and `<plugin-dir>/`
placeholders and shipped a new blocking gate arm to keep them that way. Four of those
sites are `command:` values that are EXECUTED — one through `shell=True`, where `<` and
`>` are redirections, and two through `shlex.split`, which expands nothing. The gate
arm additionally refused correct prose telling a consumer to run their own script. Both
were net regressions, and the whole arm had to be reverted. The cost was roughly a
quarter of the session, and the cause is one question I did not ask: *is this field
read, or run?*

Second: I iterated the Python length cap one refactor at a time — 481, then 530, then
378 after an extraction that made it worse, then a move to a different module. That is
the counted-limit-as-retry-loop trap this repo already records, walked into while the
lesson naming it was in view at session open.

Second-and-a-half, and the largest single irreversible cost: pushing the range closed
#626. A commit message from an earlier session contained the sentence "because S7
closes\n#626/#627/#631 on the strength of that gate" — narrative describing a future
release — and GitHub read `closes #626` as a directive. Only #626 bound, because the `/`
separator stops the link, and a scan of all sixty messages found no other. The repo's
guard inspects a staged `charness-artifacts/issue/*.md` for `Closes #N`; it cannot see a
keyword inside a sentence. The issue was in the intended close set, so the STATE is what
was wanted; what is missing is the closeout body that should have carried it, and the
owner has ruled against reopening.

Third, and cheap but repeated: two tests written for this slice asserted a GLOBAL
interpreter property (`find_spec("scripts") is None`, `pytest.raises(ImportError)`
around a package import) to prove a LOCAL layout fact. Both passed in isolation and
failed in the full suite, because whether some other test has left a package reachable
is not a fact about the layout under test. Each cost a full 2-minute suite cycle to
discover.

## Critical Decisions

- **Reverting the instruction-site arm rather than patching it.** A smaller true claim
  beats a larger false one, and the arm's remedy hint was itself misdirecting. #634's
  residual stays open, stated, rather than shipping a fix that broke four commands.
- **Running a second review round over the repairs.** The contract requires it for
  verdict-logic changes, and it earned its cost immediately: six defects in round 1's
  repairs, two of them strictly worse than what they replaced. `fnmatch` disagreed with
  `Path.glob` in BOTH directions on one pattern, so a root-level gate silently dropped
  out of DISCOVERY — a worse failure than the prefix/suffix decomposition it replaced.
- **Six disjoint-writer agents for the coverage debt, one file each.** No conflicts, and
  four of the six returned production findings I would not have looked for.
- **Stopping the publish at `unproven` rather than running a fourth claims round.**
  Three rounds each found a NEW real false claim in the body that would be posted
  verbatim as ten irreversible close comments — round 2 found that round 1's repair left
  a sibling sentence stale, and round 3 found that round 2's repair introduced a false
  attribution. A surface that keeps producing findings is telling you about the surface.
  A fourth round would have been reviewing until it passes, which is the shape round 1's
  own finding was made of.
- **Relevelling two runtime bars rather than chasing a regression.** Both were drawn at
  roughly 1.0x of observed rather than the repo's documented 1.4x, so ordinary
  contention was enough to trip them with nothing changed in either gate.

## North Star Alignment

P4's different-observer rule earned every blocker that mattered, twice: the round-1
reviewers found what my own reading had certified as a repair, and the round-2 reviewer
found what those repairs broke. Neither was reachable by more of my own reading.

The facet I mis-applied is the one about keeping teeth only where a wrong answer
escapes. I added teeth (a new blocking arm) to a surface where a wrong answer was
already visible — a documented instruction — and the teeth's own false positives were
the escape. The named signature the run walked into is "correct rule, no carrier"
inverted: a carrier built for a rule that did not need one.

## Expert Counterfactuals

- A release engineer reading the adapter contract would have asked "who executes this
  string?" before editing any `command:` value, and the whole reverted arm would never
  have been written.
- A property-based-testing lens on `matches_gate_pattern` would have found the
  `fnmatch`/`Path.glob` divergence in one line of generated input, instead of it taking
  a second review round.

## Sibling Search

- axis: export self-sufficiency | decision: valid follow-up outside the slice | proof: the unshipped-path arm in [export_self_sufficiency_lib.py](../../scripts/export_self_sufficiency_lib.py) counts AST literal nodes, so a subpath written as one literal escapes it | follow-up: deferred docs/handoff.md#next-session

## Lesson Evaluation

Five of the ten presented lessons produced an observable encounter and are scored.
Four of the five are `read-but-not-applied` or worse, which is the honest reading: the
counted-limit trap, the changed-line-proof ordering, and the claim-exceeds-the-pin
class each recurred with the lesson naming them in view at session open. The remaining
five are deliberately unscored — nothing observable happened for them in this work, and
scoring every presented lesson is not the goal.

Lesson evaluation: {"score_event_count":5,"session_id":"2026-08-16-s8-debt","status":"effect-recorded"}

## Next Improvements

- workflow: recurrence-class: executed-vs-read-field — before editing any config value,
  establish whether it is READ by a reader or RUN by an executor. A documentation
  placeholder in a read field is correct and in an executed field is a shell
  redirection, and the two are indistinguishable by looking at the value.
- capability: recurrence-class: global-probe-for-local-fact — a test proving a LOCAL
  layout fact must assert what the module under test bound, never a global interpreter
  property. Where the arm taken is not observable from the module, force it with a
  `meta_path` finder rather than by filtering `sys.path`.
- memory: recurrence-class: one-engine-per-pattern — when a pattern is used to both
  DISCOVER and MATCH, one engine must do both. `fnmatch` and `Path.glob` disagree about
  `*` crossing `/` and about `**/`, in opposite directions, so two readers of one
  pattern is a defect even when each reader is individually reasonable.
- workflow: recurrence-class: prose-claim-without-a-reader — an artifact whose PROSE
  carries verification-grade claims (counts, per-issue residual ownership, which prior
  finding recorded what) has no executable reader, so its errors are found only by
  whoever reads it next. Three independent claims-review rounds each found a NEW real
  defect in one such body; the fix is to shrink the claim surface or derive it from the
  structured findings it cites, never to add a fourth reviewer.
- capability: recurrence-class: keyword-in-prose-is-a-directive — a host parses text a
  human wrote as narrative. `S7 closes\n#626/#627/#631`, written to DESCRIBE a future
  release, closed #626 the moment the commit was pushed. Before pushing, scan the range's
  messages for the host's own keyword grammar; a guard that only inspects a staged
  carrier file cannot see a keyword in a sentence.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-16-s8-the-handoff-five-and-the-aggregate-coverage-debt.md
