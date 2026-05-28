# Retro: handoff-chunked-routing achieve-goal closeout

Mode: session
Date: 2026-05-28
Goal artifact: [2026-05-28-handoff-chunked-routing](../goals/2026-05-28-handoff-chunked-routing.md)
Host log probe: [2026-05-28-handoff-chunked-routing-host-log.json](../probe/2026-05-28-handoff-chunked-routing-host-log.json)

## Context

Closeout of a 7-slice achieve-goal run that absorbed the recurring
manual cost of chunking residual handoff entries into a generative-
sequence routing recommendation for `/achieve`. The pipeline now lives
behind a deterministic trigger gate on the existing `handoff` skill;
slices 1–6 shipped the spec, the four scripts (parse / propose /
ranker packet / auto-draft), and the SKILL.md wiring; slice 7 added
the trigger detector + e2e test and ran the closeout gates.

The goal entered with the Before-phase interview already complete and
plan critique folded (provenance: agentId `a33dfbee0a68a7774`,
pre-activation). It exited with 69 passing handoff-suite tests, two
slice-level critique runs (slice 3 ranker, slice 5 auto-draft),
standalone-usefulness invariant intact (no file under
`skills/public/achieve/` mutated by any of the 6 slice commits),
and the new chunker visible behind a guarded SKILL.md addition (151 →
157 lines, 43 lines of headroom under the 200-line cap).

## Evidence Summary

- Goal artifact's six appended slice logs (objectives, alternatives
  rejected, test-pressure samples, critique findings per slice).
- Slice commits ee3d696, 3b4ddcd, 0a3b9c0, 11f7e87, 1d2add0, 1d3e237.
- Two bounded fresh-eye subagent critique runs:
  - slice 1 spec critique (agentId `a3b7d3116ace3415c`, standard tier,
    pre-impl): 2 Act-Before-Ship + 2 Bundle-Anyway folded.
  - slice 3 ranker critique (agentId `af4926ec0074f654f`, standard
    tier, mid-slice): 1 Act-Before-Ship + 2 Bundle-Anyway folded.
  - slice 5 auto-draft critique (agentId `ab369da824c910faf`, standard
    tier, mid-slice): 1 Act-Before-Ship + 2 Bundle-Anyway folded.
- Host-log probe at
  [charness-artifacts/probe/2026-05-28-handoff-chunked-routing-host-log.json](../probe/2026-05-28-handoff-chunked-routing-host-log.json):
  Claude Code host detected; token/tool-call/duration metrics
  `available` or `derivable` from the active session JSONL at
  `/home/hwidong/.claude/projects/.../c4cd5e6e-…jsonl`.
- pytest tests/test_handoff_*.py: 69 passed across 7 test files.
- ruff: green across all new Python.
- check_doc_links + validate_skills + check_duplicates: green.

## Waste

- **Three doc-link follow-ups across slices 2, 3, 4.** Each slice
  created a new script file (parse, ranker packet, propose merges).
  After committing the file, check_doc_links rejected the spec doc
  because its backticked-without-link references to the to-be-created
  file became "unique-basename" hits the moment the file appeared on
  disk. Three separate amend commits followed. Phase intent was right
  (slice 1 had to forward-reference files that did not yet exist via
  `<repo-root>/` placeholders) but the doc-link gate's transition
  from "missing artifact" to "unique-basename" was repeatable waste.
- **chunked_routing_lib.py grew to 816 lines.** Not a hook gate
  (check_python_lengths.py is informational), but past the soft 360
  cap. The slice-1 plan held it at 292 (parser only); slices 3, 4, 5
  added ranker + merger + auto-draft helpers in one file. Splitting
  would have been a slice in itself; deferred.
- **Slice 7 trigger implementation surfaced late.** The spec named the
  trigger rule as "deterministic regex (Python)" in slice 1, but the
  implementation landed only in slice 7. Slices 2–6 carried the rule
  in prose alone; the test that pins it deterministically did not
  exist until closeout. A slice-3 or slice-4 ship of the trigger
  detector would have surfaced the regex-design edges (Korean
  variants, polite interrogatives) earlier.

## Critical Decisions

- **Auto-draft writer's standalone-usefulness via file-mutation gate,
  not import gate.** The slice-5 critique probed whether importing
  `goal_artifact_lib` constitutes coupling. The decision: import is
  the honest contract surface (the auto-draft must satisfy the
  achieve gate exactly), and the slice-5 invariant explicitly gates
  on file mutation in `skills/public/achieve/`, not on import-time
  coupling. Keeping the gate at file-mutation preserved both halves
  of standalone usefulness without forcing the writer to re-implement
  the goal-artifact contract.
- **Marker-phrase scrub at the writer layer, not the gate layer.**
  Slice 5 critique surfaced that `_TRIVIAL_GOAL_MARKER` matches
  `single-slice goal` as a substring anywhere in the artifact, so a
  quoted handoff entry could poison `is_non_trivial_goal`. The fix
  belonged at the writer (scrub the substring before injection), not
  at the gate (which would require modifying
  `skills/public/achieve/scripts/goal_artifact_lib.py` and violating
  the Standalone-Usefulness Invariant).
- **Reference-file spill for SKILL.md body.** Slice 6 added 6 lines
  to SKILL.md (151 → 157, well under the 161 cap and 43 lines of
  headroom against the absolute 200 cap) and put the full trigger
  rule + pipeline body + override UX into
  `references/chunked-routing.md`. The cap retains real headroom for
  the next handoff change rather than budgeting it out.

## Expert Counterfactuals

- **Christopher Alexander (pattern integrity)**: would have insisted
  the trigger detection live in code from slice 1 — the pattern is
  "trigger rule is the same across spec, SKILL.md prose, and tests"
  and a six-slice gap between the prose and the code is a centre-of-
  pattern violation. Counterfactual: a 30-line slice-1.5 shipping
  the `should_fire_chunker` function + 7-row fixture would have
  surfaced the polite-interrogative case ("could you check the
  handoff?") before slice 6 SKILL.md prose locked in the
  imperative-only enumeration.
- **Brian Kernighan (build the smallest tool, test it, then compose)**:
  would have noticed that chunked_routing_lib.py kept growing
  monolithically across slices 3, 4, 5. By slice 5 it was 816 lines
  with parser + ranker + merger + auto-draft in one module.
  Counterfactual: split into `chunked_routing_models.py` (dataclasses),
  `chunked_routing_parser.py`, `chunked_routing_ranker.py`,
  `chunked_routing_merger.py`, `chunked_routing_writer.py` before
  slice 5. Each <200 lines, each independently importable, each
  with its own test file already mapping 1:1.

## Next Improvements

- **workflow**: When a slice plan names "deterministic regex (Python)"
  for an operator-facing rule, ship the regex + fixture in the
  earliest slice that produces a testable surface, not at closeout.
  The prose-vs-implementation drift risk multiplies across every
  intervening slice that consults the prose.
- **capability**: Add a single-file growth gate for
  `*_lib.py` modules under `skills/public/*/scripts/`. The repo
  already has `check_python_lengths.py` at the 360-line line; make
  it a pre-commit gate (currently informational) so future slice
  bundles cannot silently grow a lib past the threshold without an
  explicit splitting slice.
- **memory**: Record in
  [recent-lessons.md](recent-lessons.md): doc-link gate transition
  ("missing artifact" → "unique-basename" on file create) is
  repeatable waste; the fix-after-create pattern across three slices
  in one goal is the signal. Either pre-create empty placeholder
  files in slice 1 OR teach check_doc_links to accept
  `<repo-root>/...` placeholders for paths that do not yet exist
  (already partially supported but did not cover the bare-backtick
  case).

## Sibling Search

The "doc-link gate transition surprise" is a transferable pattern:
any validator that distinguishes "missing artifact" from "tracked
artifact" silently changes its judgment on the same source token the
moment that artifact appears. Sibling scan:

- `validate_skills.py` enforces "every references/ file is listed in
  ## References". A new reference added in one commit would fail
  validate_skills if the SKILL.md edit is in a separate commit.
  **Already enforced as a hard gate**; mitigation is to land both
  edits in the same commit. No new gap.
- `check_python_lengths.py` is the line-length informational gate.
  Same shape: a slice that adds lines under the threshold passes;
  a future slice that pushes past silently fails informationally.
  Already discussed under Next Improvements; making it a hard gate
  would surface this class of waste sooner.
- The achieve-side `check_complete_evidence` substring-only match on
  `_TRIVIAL_GOAL_MARKER` is the same shape one layer up: the gate
  changes its judgment based on whether a substring appears
  anywhere. Already addressed by the slice-5 writer-side scrub for
  the auto-draft case; the gate itself remains substring-vulnerable
  for any other surface that quotes user prose into a goal artifact.
  Track as Off-Goal for slice 7 record (the goal does not own the
  achieve-side fix; #233 may eventually do so).

Decision taxonomy:
- doc-link gate: **mitigate at producer** (write the markdown link
  upfront when forward-referencing; same-commit landing).
- python-lengths gate: **upgrade to hard gate** (capability change).
- substring-match gate: **already mitigated at writer**, defer
  generalization to achieve-side fix (Off-Goal note in goal
  artifact).

## Persisted

yes [`charness-artifacts/retro/2026-05-28-handoff-chunked-routing-closeout.md`](./2026-05-28-handoff-chunked-routing-closeout.md)
