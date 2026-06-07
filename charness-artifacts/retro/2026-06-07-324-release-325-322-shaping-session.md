# Session Retro — #324(release)+handoff-4 inline; #325+#322 child-goal shaping

Mode: session (waste-focused, requested by the operator)

## Context

One pursue session of the `2026-06-07-324-325-322-handoff-orchestrator` goal:
B1 (#324 source-preservation contract + v0.26.0 release — pushed/tagged/published,
#324 CLOSED), B2 (handoff-4 false-green warning), and B3/B4 shaped as child
`/achieve` goals. The release was published at the operator's explicit direction
(overriding the stage-and-stop default).

## Evidence Summary

Real signals from the claude session JSONL (`probe_host_logs.py` confirmed the
source; counts derived directly): 597 assistant messages, ~837K cumulative
output tokens, 262 tool calls (142 Bash / 49 Edit / 36 Read / 12 Write). Cached
input ~155.8M (NOT waste — phase-aware). Proxy signals: 3 full ~6-min
changed-line coverage producer runs, 14 `run_slice_closeout` invocations, 23
pytest invocations (mostly cheap targeted), 14 sleep/poll calls, 8 commits.

## Waste

1. **B1b authoring-preflight skip → ~4 gate round-trips (the biggest waste).**
   I added prose to `skills/public/issue/SKILL.md` and its references without
   first skimming `authoring-preflight.md` / running
   `check_skill_surface_preflight.py`, so three separate gates rejected the edit
   in sequence: (a) `check-markdown` — inline code spans wrapped across source
   lines; (b) `validate_skills` — SKILL.md over 200 lines (two trim passes); (c)
   `validate_skill_ergonomics` — `#324` issue anchors baked into the skill
   package (scrub across 7 locations). `implementation-discipline.md` explicitly
   says to skim authoring-preflight BEFORE authoring into a gated surface, and
   #308 names this exact rework-cycle. **Repeat of a named trap.**

2. **`--skip-broad-pytest` at commit boundaries hid two real defects until the
   expensive bundle boundary → ~2 wasted ~6-min producer runs (~12 min).**
   Producer run 1 failed on a stale SKILL.md prose-pin test
   (`test_issue_closeout_discipline` asserted the old "external source identity
   when filed from a Slack thread" wording I had rewritten); run 2 blocked on an
   uncovered new error branch (`issue_tool.py:209-210`, body-file-not-found).
   Both were real and worth fixing, but both were cheap to detect upstream and
   only surfaced after paying for the full coverage producer.

3. **`run_slice_closeout --produce-mutation-coverage` silently produced nothing
   → one confused detour.** With only non-Python files uncommitted, it ran no
   broad pytest and refreshed no coverage; I assumed fresh coverage existed,
   then had to switch to the consumer-direct probe. A "tool did less than
   assumed" detour, not a hard failure.

4. **Polling overhead — 14 `sleep`/`pgrep` calls** monitoring background
   producers, several interrupted (`exit 143`) and re-polled. Minor; acceptable
   for multi-minute background runs but loosely managed.

Not waste (named to avoid a false positive): the ~155.8M cached input; the 3rd
producer run (legitimately needed after the real fixes); committing B1b
separately (a deliberate correctness move, below).

## Critical Decisions

- **Committed B1b before the release stage** — made the release-commit
  changed-line mutation analysis trustworthy (the #324 Python was committed
  history, not an uncommitted `--head-sha HEAD` false-green). This actively
  avoided the trap the goal warned about and that B2 then made permanent.
- **Asked the operator** on B3/B4 structure + handoff-3 scope + sub-issue split —
  avoided building the wrong thing (inline vs child goals materially changes the
  session).
- **Published manually instead of `publish_release.py`** — the helper assumes
  the version-bump commit is at HEAD and does `git commit --amend`; mine was 3
  commits deep, so the helper would have amended the wrong commit. Manual
  publish with the same safety checks avoided that corruption.

## Expert Counterfactuals

- **Shigeo Shingo (poka-yoke / source inspection):** make the defect cheap to
  catch at the source. Run the authoring-preflight checklist + a changed-prose
  pin scan BEFORE the gated edit and BEFORE the expensive producer, so the four
  gate round-trips and two producer failures surface at near-zero cost instead
  of at the 6-min boundary. Changed action: front-load the cheap source-checks.
- **Eliyahu Goldratt (theory of constraints):** the ~6-min mutation producer is
  the bottleneck resource; never feed it un-pre-checked work. Changed action:
  subordinate the pipeline to the bottleneck — gate the producer behind cheap
  upstream filters (prose-pin scan, new-branch coverage glance) so it runs ~once,
  not three times.

## Next Improvements

- **workflow (applied as habit):** before editing a gated `SKILL.md`/reference,
  run `python3 scripts/check_skill_surface_preflight.py --repo-root . --path
  <file> --preview-delta <n>` and skim `authoring-preflight.md` (length
  headroom, inline-code-span, issue-anchor, banned vocab). The repo already ships
  these — the miss was not running them first.
  Disposition: `memory` (this artifact + recent-lessons) — the gates exist; the
  fix is sequencing, not a new gate.
- **workflow (applied as habit):** before paying for the mutation-coverage
  producer, run two cheap pre-checks — (1) `grep -rn "<changed literal phrase>"
  tests/` for prose-pin assertions on any doc/SKILL.md changed; (2) eyeball
  coverage of any NEW source branch. Disposition: `memory`.
- **capability (candidate):** a tiny `quality`/`authoring-preflight` helper that,
  given changed doc/SKILL paths, greps `tests/` for literal-string assertions
  referencing them (catches prose-pin breakage before broad pytest). This is
  adjacent to the #325 child goal's standing-doc check work.
  Disposition: candidate `issue #N` (operator's call) OR fold into the
  `2026-06-07-325-provenance-policy-handoff3-gate-capability` child goal —
  recorded here, not auto-filed.
- **memory:** persist this retro + refresh recent-lessons.

## Sibling Search

axis scan for the two transferable patterns:

- **Prose-pin breakage when changing documented text** — transferable beyond
  SKILL.md. `test_issue_closeout_discipline` is one of several tests that pin
  literal doc/skill prose; any edit to a doc whose literal text a test asserts
  can break the suite only at broad pytest. Decision: **generalize** — the
  "grep tests/ for literal pins of changed doc paths" pre-check applies to every
  doc/skill prose edit, not just this one. Candidate folds into the #325 child
  goal (standing-doc tooling) or a small `quality` helper.
- **Paying for an expensive gate before cheap upstream filters** — transferable
  to any expensive verification (broad pytest, coverage producer, real-host
  proof). Decision: **monitor** — the goal's skip-broad cadence is correct; the
  fix is adding the cheap filters, already captured above.

## Persisted

Persisted: yes — `charness-artifacts/retro/2026-06-07-324-release-325-322-shaping-session.md`
(recent-lessons.md + lesson-selection-index.json refreshed by
persist_retro_artifact.py).
