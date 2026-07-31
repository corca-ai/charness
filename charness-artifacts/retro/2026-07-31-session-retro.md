# Session Retro
Date: 2026-07-31

## Context

One goal run: handoff chunked routing picked chunk 1 (the 2026-07-28 triage
sweep's remaining high rows), `achieve` shaped it, and `/goal` ran it to
completion. Four repairs shipped (S5, S7, S21, S22) and one row was refuted
rather than repaired (S8). The unit under review is the whole goal — shaping,
five slices, and the bundle closeout — because the interesting failures were in
the *review structure*, not in any single repair.

## Window

From the handoff pickup at `main` = `0e8d9760` (post-v3.0.0) through commits
`4302aeaa` and `ec72c301`. Five bounded reviewer spawns, one plan critique plus
two review rounds on each of two repair bundles.

## Evidence Summary

- Goal artifact: `charness-artifacts/goals/2026-07-31-repair-the-sweep-s-remaining-high-rows-s5-density-exemption.md`
  (slice log, proof-surface dispositions, operator decision queue).
- Sweep rows and their new statuses plus the closeout non-claims:
  `charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md`.
- Executed proof: every row reproduced on a seeded repo before any edit; targeted
  tests plus `git apply -R` revert-checks per repair; `run_slice_closeout.py
  --skip-broad-pytest` completed; full `pytest tests/` = 6361 passed, 1 xfailed;
  `prepush_focused_changed_line_coverage.py --base-sha 0e8d9760` = clean (after it
  found one uncovered branch).
- Host metrics (measured, thread-wide, not per-goal — no `Host metric window:`
  was set): 468 token snapshots, 323 function calls, 58 patch applications, 0
  context compactions, 5 subagent spawns. Proxy signals: no repeated broad gates,
  no repeated VCS commands.
- `mine_closeout_telemetry.py`: the recurring `verify:pytest -q -m 'not
  release_only' …` gate is 16 occurrences with a 475s peak — a pre-existing
  repo-wide runtime trap, not this session's.

## Waste

- **The fence question was answered three times, wrongly each time, in three
  different files.** First in the density *count* (a fix that dropped fenced
  lines entirely — a regression that re-opened the class being repaired), then in
  the density *audit*, then in the chunk-contract detector. The duplicate-ratchet
  is what finally forced one shared `split_fenced_lines`. Cost: two review-round
  findings and one extra dup-ratchet cycle that a single shared helper on the
  first pass would have avoided.
- **Four dup-ratchet cycles at the closeout boundary.** Each of my edits rotated a
  boilerplate family fingerprint (an import block, a `format_human` twin), and
  each rotation surfaced only when the aggregate ran. Two were genuine extractions
  worth doing; three were classifications of unextractable import preambles.
- **Not waste, though it looks like it:** the sequence "reproduce → repair →
  revert-check" ran five times and never once was skipped. That is the contract
  working, and it is what let S8 be refuted instead of "fixed".

## Critical Decisions

- **Demoting S8 instead of repairing it.** The plan critique showed the sweep's
  reading was wrong and the naive repair would have turned the pre-push lane red
  for every future `SKILL.md` commit. Asked the operator rather than deciding it;
  the answer changed the goal's title.
- **Bundling slices 2/4/5 into one review pair instead of three.** The three
  repairs are the same defect class in three files; one reviewer reading the class
  produced sharper findings than three reviewers reading one file each would have.
- **Making over-budget charge density instead of blocking.** Round 1 caught that
  the blocking verdict contradicted its own remediation message. Choosing the
  message over the verdict kept the gate honest and let the budgets be tightened
  toward observed usage rather than padded for safety.
- **Not porting the repair into `skill_ergonomics_lib.py`.** It must stay
  skill-local-portable, so S5 is closed at the author-time preflight only. Written
  as an explicit non-claim in two places and queued as an operator decision rather
  than left implicit.

## Trends vs Last Retro

- The recent-lessons trap "**a rationale is a claim** — verify the compensating
  control in the same breath as citing it" recurred in a new shape: the fence
  repair's own docstring said fenced lines "are still counted" while the code had
  stopped counting them. Round 2 caught it. The lesson is holding as a *detector*
  but not yet as a *habit*.
- The "planned items were premises, not debt" trap did not recur: every row was
  reproduced before planning its repair, and the one row that was a premise (S8)
  was caught in the plan critique, before any code was written.
- New this session, and the reason the two-round rule earned its cost twice: both
  round-2 blockers were defects that **did not exist when round 1 ran**. Neither
  reviewer could have caught the other's.

## Expert Counterfactuals

- **Engelbart (`system-improving-itself`) — treat (H + LAM + T) as one unit.**
  The repairs improved the tool (LAM); what actually failed three times was the
  *process for changing it* (T): three independent fence walks in one goal, each
  authored by the same model an hour apart. Engelbart's move is to notice that the
  second occurrence is the signal, not the third — the moment a concept (fence
  handling) is implemented twice in one work unit, stop and make it one surface
  with a declared failure direction. Concretely: after the density-count fence fix,
  a 30-second `grep -rn "startswith(\"\`\`\`\")" scripts/` would have shown two
  existing walks and pre-empted both round-2 findings. The dup ratchet eventually
  forced this — a gate doing the job the process should have done, which is itself
  the finding.
- **Gary Klein (pre-mortem, decision quality).** Before shaping, ask "it is
  closeout and a row is *worse* off than before — what happened?" The plausible
  answer for four of the five rows was "the repair made an ordinary run fail", and
  that is exactly what the plan critique found for S8/S21/S7. A pre-mortem at
  shaping time would have surfaced the pinning tests (`test_cautilus_proof_artifact.py:12`,
  `test_hitl_chunk_contract.py:71`, `test_cautilus_diagnostic_artifact.py:73`)
  before the plan was written rather than after — the plan's own evidence column
  contradicted its objective for a full review cycle.

## Sibling Search

- axis: **same concept, other implementations** | location: fence/code-block
  walking across `scripts/` | decision: repaired in-slice (consolidated into
  `skill_markdown_lib.split_fenced_lines`, now used by `skill_core_density.py` and
  `hitl_review_artifact_lib.py`) | proof: dup ratchet went from hard-block on
  `5068eb82`/`00a71e31`/`377b9244` to clean; `pytest` green | follow-up: none
- axis: **same defect class, other copies of the repaired surface** | location:
  `skills/public/quality/scripts/skill_ergonomics_lib.py:45-67` and
  `scripts/validate_quality_artifact.py:196` | decision: valid follow-up outside
  the slice (portability boundary; changing the portable copy changes a public
  skill's gate semantics) | proof: read both; neither budgets, audits, nor tracks
  fences; `dup-review.json` entry `76b34d112c417b21` records the divergence |
  follow-up: queued in the goal's `## Operator Decision Queue`, and stated as a
  non-claim in `docs/conventions/authoring-preflight.md` and the sweep record
- axis: **same first-block reading the row was about** | location:
  `scripts/skill_markdown_lib.py::extract_h2_section_lines` | decision: valid
  follow-up outside the slice | proof: it returns only the first matching H2, the
  exact shape S5 punished elsewhere; no current caller depends on multi-block
  behavior | follow-up: recorded in the goal's `## Off-Goal Findings`

## Next Improvements

- workflow: **when a concept is implemented a second time inside one work unit,
  stop and unify it before the third.** Cheap trigger: after any fix that walks
  markdown structure (fences, headings, frontmatter), grep for sibling walks
  before moving to the next slice. This session paid two review findings and a
  ratchet cycle for skipping it.
- workflow: **run the pre-mortem against the pinning tests at shaping time.** For
  a goal whose slices change verdict logic, list the checked-in assertions that
  pin today's behavior *before* writing the slice plan; three of five rows had one,
  and one plan slice was internally contradictory because of it.
- capability: teach the changed-line gate's `blocking_targets` payload to name
  when a blocked line's only coverage path is a subprocess test — carried forward
  from the 2026-07-30 retro, still unapplied, still owed its own two-round review.
- memory: the two-round rule's evidence is now three-for-three — every measured
  slice that changed verdict logic shipped a fix carrying the class it fixed, and
  round 2 caught it each time. Recorded here and in the goal's slice log.

## Portable Candidate

not portable — the concrete lesson (unify a structural walk on its second
occurrence) is a repo-internal discipline, and the reusable half already exists as
the duplicate ratchet, which is a shipped public-skill capability.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-31-session-retro.md
