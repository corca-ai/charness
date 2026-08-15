# Session Retro
Date: 2026-08-15

## Context

S4 of the 6.0.0 release contract: make `check_docs_graph.py` judge named metrics
against declared bars, repair this repo's own link-only-line population, and stop
the handoff scaffold teaching context-free links (#629). Committed `ad58786ff`.
What matters next is S5, the least bounded slice in the release, and whether the
authoring path — not the gate — is where the remaining defect class lives.

## Window

From the `2026-08-15-s4` lesson-session declaration through commit `ad58786ff`.
One slice, two bounded review rounds, two full-suite runs.

## Evidence Summary

- `git show --stat ad58786ff` — 32 files, the gate, the handoff validator and
  scaffold, nine docs pages, and the exported mirror.
- `awiki lint -root docs -recursive` — `link_only_lines` 255 before, 167 after;
  `python3 scripts/check_docs_graph.py --repo-root .` passes at its bar.
- Full suite, second run over the final tree: 9463 passed, 0 failed, 21m30s.
  First run: 22 failed / 21 errors, every one `needs_sync`, against a tree whose
  export was stale mid-run.
- `reviewer_boundary_fingerprint verify` on windows `s4-docs-graph-r1` and `-r2`:
  both `parent-attributed`, no approvals quarantined.
- `mine_closeout_telemetry.py` — `over_slice` recurring at 69 occurrences,
  disposition `file-issue`; unchanged by this slice and not caused by it.

## Waste

**A 21-minute suite run spent on a stale tree.** `sync_root_plugin_manifests.py`
ran after the #629 work and before the gate work, so the export was current for
one half of the slice and stale for the other when the first full suite started.
Every one of the 22 failures and 21 errors was the same `needs_sync` blocker, and
the run had to be repeated end to end. The handoff already carries the rule this
violates — "a suite run started before a repair does not prove the tree after it"
— and the rule was followed for the repairs and not for the *sync*, which is a
repair the slice performs on a generated surface rather than on source.

**Two commit-gate round trips after the work was done.** The skill core-line cap
fired on a four-line SKILL.md addition, and the boundary-bypass ratchet fired on
a moved call-site fingerprint. The S3 retro named this exact pattern one slice
ago ("caps and ratchets fired at the commit gate again, after the work was
done"). Nothing changed between S3 and S4 to surface either budget while
authoring, so the recurrence was predictable from the prior retro alone.

**One wrong measurement, caught cheaply.** The first classification of the 255
findings put 88 in the bare-list-entry bucket; reading the flagged source lines
showed 5 of those carried a descriptor that had wrapped onto the next line, so
the real split was 83 + 5 + 167. Caught within minutes because the check was a
re-read of source rather than of the earlier claim — this is the cheap case, and
it is the same discipline that failed one surface over (see North Star).

## Critical Decisions

- **Size the bar to the wrapped-prose remainder rather than sweep the tree.** A
  checked-in decision in `docs/docs-graph-checks.md` already said a reflow sweep
  is not the way; this slice honored it instead of relitigating, and repaired the
  population that is a real defect. Constrains every later slice: the lane has
  zero headroom, so the next docs edit that adds a wrapped link line reddens it.
- **Extend scope to the validator rule, and record the extension as SC13.** A
  placeholder-only #629 fix would close an issue on behavior the tree does not
  have. The alternative — shipping the rule and leaving it in the diff — is what
  a round-1 reviewer would have called scope creep with no criterion, and did.
- **Delegate descriptor authoring to parallel subagents over disjoint files.**
  Roughly ninety authored claims, spot-checked by me and sampled by one bounded
  reviewer (~55 of them). Verification of the rest is partial and stated as such
  rather than implied by the green gate.
- **Stop at the two-round cap with round-2 repairs unreviewed.** Round 2 found
  defects in round 1's repairs; a third round would likely find some in round
  2's. The cap is the stopping rule and it was honored rather than argued with.

## North Star Alignment

P4 is the whole story of this slice, in both directions. The governing contract
asserted that `check_docs_graph.py` and `awiki lint` are "two independent
channels that agree"; I copied that into the gate's own source comment and into
`docs/docs-graph-checks.md` without checking it against `_run_awiki`, which
shells out to awiki and regex-reads its stdout. One observer, read twice —
exactly the "re-reading the same proxy" P4 forbids, written into a proof
surface's own calibration note.

What caught it was P4 applied properly: a bounded reviewer with a different
evidence channel read the function rather than the sentence. The two-round
bounded review at an irreversible-ish boundary is the north star's
different-observer rule operating as designed, and it is the only reason the
claim did not ship.

## Trends vs Last Retro

Against `2026-08-15-s3-lesson-loop.md`: S3 ran three rounds and found 29
blockers with four false prose claims authored inside the release built to stop
them. S4 ran two rounds and authored one, of the same class. The direction is
better and the class is unchanged — and S3's own closing lesson said why: "the
binding step is a check at the moment of writing." No such check was built
between S3 and S4, so S4 relied on review again and review again was what worked.
The gate-fires-at-commit pattern is also flat across both slices.

## Expert Counterfactuals

**Engelbart (system-improving-itself; H + LAM + T as one unit).** This slice
improved T — the gate now judges bars, names failures, guards its own tables —
and left LAM untouched. The language for *stating how a bar was measured* stayed
free-form prose, which is precisely where the false claim landed. Engelbart's
different action: co-design the notation with the tool. Instead of a comment
above `LINK_ONLY_LINES_BAR`, emit a typed provenance record next to the value —
observer, command, date, field read — that the ratchet test parses alongside the
number. "Two independent channels" then becomes unwritable rather than
unreviewed, because the form has one observer slot per entry and a second entry
has to name a different command. The slice built a gate that refuses
context-free links while its own calibration note was a context-free sentence.

**Klein (premortem on a new constant).** Before writing `167`, ask: it is a year
from now and this number is wrong — why? Two answers arrive immediately, and both
are what round 2 actually found: it has zero headroom so the next docs edit
reddens the lane, and it travels into the exported plugin where it describes a
docs tree the consumer does not have. Both were then discovered by reviewers at
review cost rather than by the author at two minutes' cost. The different action
is a standing two-minute premortem on every constant that enters a proof
surface, before the constant is written rather than after it is reviewed.

## Sibling Search

The transferable pattern: **a bar guarding a proof surface that records its value
but not its permitted direction or the authority to change it.** The docs-graph
bar had neither until this slice; the scan asks where else that holds.

- same layer: `scripts/check_python_lengths.py:20-22` (`REPO_SCRIPT_FILE_MAX`,
  `SKILL_HELPER_FILE_MAX`, `TEST_FILE_MAX`) and their WARN bands | decision:
  valid follow-up outside the slice | proof: `grep -rn "TEST_FILE_MAX" tests/
  scripts/ docs/` returns only the definition and its own use — the values are
  required constants (so `bar-recorded-as-prose` is satisfied) but nothing
  records a direction, and raising one is a single-literal edit with the suite
  green | follow-up: deferred docs/handoff.md `## Discuss` "Bars record a value
  but not a direction"
- abstraction up: `skills/public/quality/scripts/validate_skill_ergonomics.py:300`
  `max_core_lines=160` | decision: valid follow-up outside the slice | proof: an
  inline literal at a call site, not a named constant; `grep -rn "160"` over the
  skill-ergonomics tests finds no pin. It fired on this slice's SKILL.md edit,
  and neither its value nor its direction is recorded anywhere | follow-up:
  deferred docs/handoff.md `## Discuss` "Bars record a value but not a direction"
- specialization down: `scripts/check_boundary_bypass_ratchet.py` with
  `scripts/boundary-bypass-baseline.json` | decision: intentional boundary |
  proof: it already carries the stronger form this slice reached for — a
  checked-in baseline with `writer_integrity_sha256`, a `no_increase` policy
  field, and `--confirm-baseline-delta` required to replace it. Nothing to fix;
  it is the model the docs-graph record is a weaker version of.
- mental-model siblings: the handoff content ceiling
  (`skills/public/handoff/scripts/handoff_content_budget.py`,
  `MAX_CONTENT_LINES`) | decision: intentional boundary | proof:
  `scripts/validate_handoff_artifact.py:67-84` records a dated rationale for
  raising it 58 -> 78 by operator decision, with the reasoning kept. This is a
  bar that legitimately ROSE, which refutes the naive generalization: the
  follow-up above must record each bar's direction and authority, not ratchet
  everything downward.

## Lesson Evaluation

Answering the evaluator's harmful question first: **no presented lesson pushed
this session toward a wrong action.** Six of the ten returned nothing for this
slice — there was no goal artifact (`goal-closeout-evidence-binding`), no quality
artifact (`artifact-contract-late-feedback`), no causal claim resting on one
observation (`cause-named-from-one-observation`), and no changed-line coverage
question (`changed-line-proof-before-broad-quality`). Those stay unscored;
nothing observable happened to them.

Lesson evaluation: {"score_event_count":4,"session_id":"2026-08-15-s4","status":"effect-recorded"}

## Next Improvements

- workflow: run `sync_root_plugin_manifests.py` as the first step of any long
  verification run, not once mid-slice — the generated mirror is a repair
  surface, and the "a run started before a repair does not prove the tree after
  it" rule applies to it exactly as it applies to source.
- capability: give a bar a typed provenance record the ratchet test parses —
  observer, command, date, field — so a corroboration claim has one observer slot
  per entry and "two independent channels" cannot be written as free prose.
- memory: a bar is two decisions, its value and its permitted direction plus who
  may change it. Recording only the value satisfies `bar-recorded-as-prose` and
  still leaves the ratchet as prose, which is what round 2 measured here.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-15-session-retro-s4.md
