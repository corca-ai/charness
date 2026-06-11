# Handoff parser and reviewer-tier setup critique

Date: 2026-06-11

## Decision Under Review

Small repair bundle: make the handoff chunker parse the bullet-shaped
`## Next Session` that `handoff` currently writes, and make `setup inspect`
surface missing or drifted critique reviewer-tier adapters so Codex
fresh-eye reviewers do not silently inherit high reasoning effort.

## Failure Angles

- The parser fix could over-read nested bullets inside an item body as new
  handoff chunks.
- The setup-inspect fix could over-constrain non-Codex repos by requiring a
  Codex-specific `reasoning_effort`.
- The new tests could add subprocess boundary-bypass debt or length pressure.
- The root miss could remain only a chat correction instead of becoming a
  transferable Charness guard.

## Counterweight Pass

- Parser risk is acceptable for this slice: the current parser already treats
  top-level list starts as item boundaries, and the regression test pins the
  current handoff writer shape. A deeper nested-list parser can wait until a
  real nested-bullet failure appears.
- Setup-inspect risk is scoped: missing critique adapter is flagged only when
  fresh-eye/critique policy is present, and `reasoning_effort: medium` drift is
  flagged only for a Codex-looking `gpt-*` high-leverage tier. Claude/non-Codex
  adapters are not forced into Codex fields.
- Test debt was folded before closeout: the new critique-adapter setup tests
  call the library in-process instead of adding a new `inspect_repo.py`
  subprocess boundary, and the large setup-inspect policy file returned below
  the warning band.
- Meta miss folded into shipped behavior: the setup inspector now gives
  consuming repos a concrete adapter recommendation instead of relying on an
  operator noticing that subagents kept inheriting high reasoning.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/handoff/scripts/chunked_routing_parser.py | action: fix | note: `handoff_entry_count: 0` against the live handoff artifact was a product defect, not only an explanation bug; fixed by parsing top-level bullets and pinned by regression tests.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/setup_agent_docs_lib.py | action: fix | note: adapter-first reviewer prose without a pinned critique adapter can still let Codex subagents inherit parent high reasoning; setup inspect now reports missing or drifted adapter state.
- F3 | bin: bundle-anyway | evidence: moderate | ref: tests/quality_gates/test_setup_inspect_critique_adapter.py | action: document | note: test split avoids growing the already-large setup inspect policy test file and avoids a new subprocess boundary-bypass candidate.

## Fresh-Eye Satisfaction

Short scoped critique for a small local-risk parser/setup-inspector repair.
No standalone subagent critique was run; deterministic parser, setup-inspect,
surface, and broad pytest gates own this closeout.
