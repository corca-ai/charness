# Session Retro
Date: 2026-08-03

## Context

One goal, run end to end: `make-deliberate-absence-representable` — issue #481,
where the `quality` bootstrap silently reverted an operator's customized adapter
toward the preset, destroying 14 comment lines and resurrecting 3 keys naming files
that do not exist in their repo. Shipped as `cec8c9b8` on `main`; #481 closed
through its floor; #485 and #486 filed as residue.

This retro matters because the run's own review machinery caught more than the
implementation did, and the two places it caught things are both places this repo
has been burned before.

## Evidence Summary

- Goal artifact: `charness-artifacts/goals/2026-08-05-make-deliberate-absence-representable.md`
  (4 slice-log entries).
- Debug artifact: `charness-artifacts/debug/2026-08-05-quality-adapter-silent-revert.md`.
- Resolution critique: `charness-artifacts/critique/2026-08-05-issue-481-resolution-critique.md`.
- Commits: `20f8898b` (the fix), `fa14e4ee` + `b876abe5` + `cec8c9b8` (mutation-lane
  coverage repairs).
- Host log probe (claude session `2f1ddd0f`): 243 function calls, 71 patch
  applications, 3 subagent spawns, 0 context compactions, 422 token snapshots.
  Window filter not applied, so these are thread-wide, not per-goal.
- Proxy signal from the same probe: `git push` x3, `git add` x4. The three pushes
  are the shape worth reading (see Waste).
- Closeout telemetry: the broad `pytest` gate recurs 16 times with a peak of 475s;
  this run spent ~10 minutes per full-suite invocation and ~9 minutes per push.
- Reviews: 3 delegated bounded read-only rounds, each fenced by
  `reviewer_boundary_fingerprint.py snapshot`/`verify`, all `clean`.
  Findings: round 1 = 7, round 2 = 6, resolution critique = 9.

## Waste

**1. A dup-ratchet extraction that created more duplication than it removed.**
The ratchet flagged one new family after the `--dry-run` repair made two writers
converge. I extracted BOTH the shared decision (`plan_generated_write`) and the
shared write (`write_generated_file`). The second was a two-line
`mkdir` + `write_text` body — already an idiom in 15 files — so naming it created
**4 new trivial families** where there had been 1. Reverted that half, kept the
first. Net: one wasted extract/measure/revert cycle, each measure costing a
multi-minute ratchet scan.

**2. Shell command substitution silently ate content from the goal artifact.**
`append_slice_log.py` was invoked with prose containing backticks
(`` `preserved` ``, `` `written` ``). zsh substituted them before the process
started, so three slice-log lines were written with holes in them. Caught by
reading back, then repaired by hand. The helper cannot defend against this — the
expansion happens before its argv exists — so the fix belongs in how agents invoke
it. Every later invocation used a Python heredoc instead and was clean.

**3. Under-weighting the local mutation lane's own scope warning.**
The pre-push run printed `analyzed only 6 of 7 changed mutation-pool file(s). A
clean verdict says NOTHING about the rest: scripts/markdown_preview_bootstrap_lib.py`
— and then passed. I read the pass and pushed. Remote CI analyzed the 7th file and
blocked on `markdown_preview_bootstrap_lib.py:149`. The warning was precise, correct,
and phrased as exactly the thing that then happened. Cost: one extra push cycle
(~9 min) plus a CI round trip (~12 min).

**4. Three pushes where one was possible.** Two of the three were consumed by
mutation-lane coverage that a single local run at full scope would have surfaced
together. Related to (3), and the same root: I treated the changed-line lane's
partial-analysis state as advisory.

## Critical Decisions

- **Replaying before designing, and following the negative result.** The first
  replay did NOT reproduce. Treating that as a finding rather than a fixture bug is
  what surfaced M3 — `diff_is_defaulted_only` fails open, and the unblocking change
  is created by the quality run itself. M3 is not in the operator's report and would
  not have been found by designing from the report.
- **Rejecting the obvious repair.** Tightening `diff_is_defaulted_only` was the
  natural fix and would have shipped a tool that still could not REPRESENT the
  intent. "Suppression is not representation" is the line that made the rest of the
  design fall out.
- **Escalating rather than absorbing the resolution-layer half.** Making
  `quality_adapter_lib` honor the declaration would change what fields mean at
  resolution time. That hit the goal's own recorded stop condition, so it became
  #485 with a mitigation, rather than a quiet schema change.
- **Letting the resolution critique refuse the close.** It found that
  `## User Acceptance` claimed "the operator's EXACT reproduction" and "14-to-0"
  when the fixture measured 12-to-0 on 24 lines. That is the same misstated-ruler
  class for which this repo refused the #479 close. Corrected before the close, and
  kept out of the close comment.

## Trends vs Last Retro

Against `charness-artifacts/retro/recent-lessons.md`: the round-2 obligation on
verdict-logic surfaces has now paid out again, and harder than the prior instances
— round 1's repairs contained two HIGH defects of the class they repaired, one of
which (a trailing comment swallowing a whole nested block) destroyed MORE operator
data than the original bug. The prior lesson said "the round that reads the repairs
catches blockers the first round could not see"; this run supplies the sharpest
instance yet, and adds a mechanism: both defects came from **duplicating a rule
rather than moving it** (a second comment-start implementation; a strip applied at
one of two dispatch layers).

## Expert Counterfactuals

**Engelbart (`system-improving-itself`) — treat (H + LAM + T) as one unit.**
The tooling (T) already knew things the human-agent loop (H) discarded. The local
mutation lane *told* me it had analyzed 6 of 7 files and that its verdict proved
nothing about the 7th; the dup ratchet *told* me the advisory fires per-file as I
edit. In both cases T emitted a correct, specific signal and the loop treated it as
narration because it did not change an exit code. Engelbart's move is not "read
harder" — it is to give the signal teeth in T so H cannot route around it: a lane
that cannot analyze its full changed set should not be able to return a bare green.
That is a one-line disposition change in the gate, and it converts a warning nobody
weighted into a state the pipeline has to answer for.

**John Ousterhout (deep modules / information leakage) — on the extraction misfire.**
The failed `write_generated_file` extract is textbook shallow-module: its interface
was as large as its implementation, so it added a name without hiding a decision.
Ousterhout's test — does the abstraction hide enough complexity to pay for its
interface? — would have rejected it before the measure cycle, and would have kept
`plan_generated_write` (which hides a real three-way policy decision the callers
were each re-deriving). The actionable difference: when a duplication gate flags a
family, ask which of the duplicated spans encodes a *decision* and extract only
that; a span that encodes an *idiom* should stay duplicated, and the honest move is
to classify the family `intentional` rather than to name the idiom.

## Sibling Search

- axis: helper scripts taking free prose through CLI args | location: `achieve`'s
  `append_slice_log.py` / `upsert_goal.py`, and any skill helper documented with a
  shell-quoted prose argument | decision: real, transferable, outside this slice |
  proof: three slice-log lines lost backticked content this run; the helpers cannot
  defend against pre-argv expansion, so the fix is invocation guidance or a
  file/stdin input path | follow-up: issue #487
- axis: gates that return green while reporting incomplete scope | location:
  `check_changed_line_mutation_coverage.py` (`unanalyzed_changed_pool_files`), and
  the same shape wherever a checker emits a partial-coverage advisory | decision:
  real, transferable, outside this slice | proof: local green + explicit
  "analyzed 6 of 7" warning, then remote CI blocked on the 7th file |
  follow-up: issue #488
- axis: duplication-gate remedies that add duplication | location: this run's
  `write_generated_file` revert | decision: no follow-up — the corrective knowledge
  is the Ousterhout lens above and belongs in the lesson digest, not a gate; a rule
  that guessed "idiom vs decision" mechanically would misfire more than it caught |
  proof: 1 extract created 4 families where 1 existed; reverting restored the count

## Portable Candidate

not portable — both follow-ups are repo-local gate/invocation concerns. The
underlying idea (a checker that cannot cover its full scope must not return a bare
pass) is general, but it is already expressed in this repo's design north star as
"success is provisional"; a separate public skill would restate rather than add.

## North Star Alignment

Consulted `docs/design-north-star.md`.

**Held.** P4 — "success is provisional at an irreversible boundary; confirm with a
different observer and a different evidence channel, never a terminal green" — is
the reason this run did not ship a false claim. The push exit code was green and the
remote check-runs API said the mutation mirror **failed**. Had the push exit code
been treated as the verdict, `main` would carry a lane failure nobody looked at.
Same facet, second instance: the local mutation lane's green was contradicted by its
own scope warning.

**Held.** "Keep teeth only where a wrong answer escapes" — the gates that refused
this run all refused correctly, every time: the commit-msg gate on a missing bug
ledger, the artifact validators on hand-authored critique/debug shapes, the dup
ratchet, the changed-line mutation lane (three separate times, once naming genuinely
DEAD code in `_string_round_trips_bare`), and the helper-provenance refusal that
stopped a drifted installed copy from writing this very artifact. Zero false
refusals across the run.

**Mis-applied, by me.** The north star's "a terminal green is not a verdict" was
applied faithfully at the push boundary and **not** applied one step earlier, at the
mutation lane's own partial-scope pass — even though the lane printed the
qualification in plain text. The facet was known and the instance was missed, which
is why the fix routed to #488 (make the gate's exit express what its prose already
says) rather than to a note telling the next agent to read harder.

**Failure signature walked into.** "The guard protects the FILE, and what was lost
was the INTENT inside it" — the run's own subject matter. It recurred at the meta
level twice: round 1's repairs re-created the class they fixed (a comment counter
that disagreed with the parser; a strip applied at one of two dispatch layers), and
both instances came from duplicating a rule instead of moving it. The
second-round obligation on verdict-logic surfaces is what caught both.

## Next Improvements

- workflow: when a gate prints a scope-limitation warning alongside a pass, treat
  the warning as the verdict until the scope is closed — do not push on the pass.
  Applied this run only after CI forced it.
- capability: give the changed-line mutation lane a non-green state for incomplete
  scope (issue #488), and give the `achieve` slice-log helpers a prose input path
  that cannot be shell-expanded (issue #487).
- memory: the round-2 mechanism — a repair that DUPLICATES a rule rather than
  moving it is the shape that carries the class forward — into
  `recent-lessons.md` via this artifact's digest.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-03-session-retro.md
