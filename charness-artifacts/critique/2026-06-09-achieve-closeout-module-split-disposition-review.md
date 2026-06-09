# Disposition Review — at-cap achieve closeout module split

Reviewer: fresh-eye subagent (achieve rung 2)
Goal: charness-artifacts/goals/2026-06-09-achieve-closeout-module-split.md
Verdict: PASS

## Per-improvement audit

The retro's `## Next Improvements` surfaced two items (one `workflow`, one
`memory`); both are dispositioned in the goal's `## Auto-Retro`. Audited each
disposition's `applied:` claim against the real working tree / committed source.

- **workflow** — "treat every pre-existing uncovered branch in the moved code as
  a newly-gated changed line; cover those branches IN the introducing slice"
  -> Auto-Retro `applied:` "covered the 7 moved-but-previously-uncovered branches
  + the two `_load_local_module` fail-closed branches with targeted tests"
  -> **VERIFIED** (real working-tree tests, all green). Evidence:
  - `_mask_fences` unbalanced-fence `return text`: source
    `skills/public/achieve/scripts/goal_artifact_disposition_grammar.py:77-78`
    (`if in_fence: return text`); test
    `tests/quality_gates/test_goal_disposition_gate.py:515-520`
    (`test_grammar_mask_fences_returns_text_on_unbalanced_fence`).
  - `_section_body` heading-at-EOF `return ""`: source
    `goal_artifact_disposition_grammar.py:122-123` (`if body_start == -1: return ""`);
    test `test_goal_disposition_gate.py:523-527`
    (`test_grammar_section_body_empty_when_heading_is_last_char`).
  - 5 loader `raise ImportError` arms (early_close_report / metric_window /
    phase_routing / closeout_delegation / adapter_policy): all five present in
    `skills/public/achieve/scripts/goal_artifact_closeout_loaders.py` (lines 76,
    92, 123, 141, 154); test `test_goal_disposition_gate.py:496-512`
    (`test_closeout_loaders_fail_closed_for_each_sibling`) iterates exactly those
    5 loaders + their expected missing-name strings. (The other 3 of the 8
    loaders — `_load_shared_helper`, `_load_sibling_disposition`,
    `_load_sibling_coordination_floors` — are pinned elsewhere per the test's own
    docstring; the disposition correctly claims only the remaining 5.)
  - 2 `_load_local_module` fail-closed branches: source
    `goal_artifact_disposition.py:52-53` and
    `goal_artifact_closeout_evidence.py:29-30` (both `if spec is None or
    spec.loader is None: raise ImportError(...)`); tests
    `test_goal_disposition_gate.py:470-481`
    (`test_disposition_load_local_module_fails_closed`) and `:483-493`
    (`test_closeout_evidence_load_local_module_fails_closed`), each exercising
    both the `spec is None` and `spec.loader is None` arms.
  - Command: `python3 -m pytest -q tests/quality_gates/test_goal_disposition_gate.py`
    -> `38 passed in 2.74s`. The 7 + 2 = 9 branches map to real, passing tests.
  - The "7 branches" count is accurate: 1 (`_mask_fences`) + 1 (`_section_body`)
    + 5 (loaders) = 7 moved-but-previously-uncovered; the two `_load_local_module`
    arms are the NEW glue, counted separately exactly as the disposition states.

- **memory** — "persist the refinement to recent-lessons so the next module-split
  goal starts from it" -> Auto-Retro `applied:` "extended the in-slice-coverage
  guardrail in `charness-artifacts/retro/recent-lessons.md` (auto-refreshed from
  this retro) to cover the moved-but-previously-uncovered-branch case"
  -> **VERIFIED** (real working-tree change). Evidence:
  - `charness-artifacts/retro/recent-lessons.md:11` now carries the refinement
    verbatim: "moving code into a NEW file makes every line a *changed* line, so
    pre-existing uncovered branches in the moved source become newly-gated …
    discovered rather than confirmed" — the exact moved-but-previously-uncovered
    refinement the retro's `## Next Improvements` / `## Sibling Search` named.
  - `git diff charness-artifacts/retro/recent-lessons.md` shows the entry ADDED to
    `## Repeat Traps` plus the `**memory:**` bullet ADDED to `## Next-Time
    Checklist` (line 20) and this retro ADDED to `## Sources` (line 48). This is a
    real working-tree mutation, not prose-only.

- **Structural follow-up** — Auto-Retro `applied:` "extended the existing
  in-slice-coverage guardrail wording … no new gate; the changed-line producer
  already catches it at the bundle boundary" -> **VERIFIED** and matches the
  retro's `## Sibling Search` decision exactly: "recent-lessons refinement
  (memory) — extend the existing in-slice-coverage guardrail wording rather than
  file a new issue; no new gate is needed." The claim that "no new gate is needed
  because the producer already catches it" is internally consistent with the
  retro's own Waste analysis (the producer DID flag the 7 branches at the bundle
  boundary). Decision (memory, no new gate, no issue) is the honest call: this is
  a refinement of the recurring #339 in-slice-coverage lesson (already present at
  `recent-lessons.md:19`), not a novel class warranting a gate.

## Notes

Genuinely disposed — both surfaced improvements are real, not token-theater.

- The workflow disposition is the strongest: it is not just memory but a concrete
  set of 9 passing tests over real source branches (verified line-by-line in the
  grammar leaf, the loaders leaf, and both wrappers). The "0 uncovered changed
  lines" claim is consistent with these tests covering every branch the retro's
  Waste section enumerated.

- The memory disposition is real but worth a calibration note (not a blocker):
  the mechanism is the `persist_retro_artifact.py` recency-selection digest, so
  the "guardrail wording" that landed in recent-lessons is the retro's own Waste
  bullet copied verbatim into `## Repeat Traps`, plus the `**memory:**`
  Next-Improvement bullet — not a separately-authored, prescriptive checklist
  rule. The Auto-Retro is honest about this ("auto-refreshed from this retro").
  It is a genuine durable working-tree change to memory and satisfies the
  intent (the next module-split goal will see the refinement in the digest), so
  it passes — but a reader expecting a hand-written, action-shaped checklist line
  should know it is the carried retro narrative, not new guidance prose.

- recent-lessons.md is a working-tree modification (`git status` shows ` M`), as
  is the test file. The grammar + loaders leaves are already committed
  (`a4830fec` slice 1, slice 2 commit). The disposition artifacts are not yet
  committed — expected mid-closeout; the deterministic floor and this review
  pass on the working-tree state, and the operator commits the bundle next.

- No `applied:` claim was unverifiable. Every cited artifact (test functions,
  source branches, recent-lessons entry) was located and confirmed at concrete
  file:line. No token-theater detected.

One-paragraph summary: Every `applied:` claim in the goal's `## Auto-Retro`
verified against real source and tests. The 7 moved-but-previously-uncovered
branches (`_mask_fences` `return text`, `_section_body` `return ""`, and 5 loader
`raise ImportError` arms) plus the two `_load_local_module` fail-closed branches
all map to concrete, passing tests in
`tests/quality_gates/test_goal_disposition_gate.py` (38 passed); the
in-slice-coverage refinement is genuinely persisted to
`charness-artifacts/retro/recent-lessons.md:11` as a real working-tree change; and
the Structural follow-up (recent-lessons refinement, memory, no new gate, no
issue) matches the retro's `## Sibling Search` decision exactly. The only nuance
is that the memory persistence is the auto-digest of the retro's own Waste bullet
rather than hand-authored checklist prose — disclosed honestly in the disposition
and not a blocker. VERDICT: PASS
