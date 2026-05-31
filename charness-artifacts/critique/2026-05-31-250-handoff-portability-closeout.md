# Critique — #250 handoff author-repo-internal cite portability (resolution)

Date: 2026-05-31
Target reference: code-critique (doc/portability change)
Execution: subagent (bounded fresh-eye, serial single reviewer + orchestrator counterweight)
Fresh-Eye Satisfaction: parent-delegated
Packet Consumed: n/a (no adapter sections)

## Change

Issue #250: the vendored `handoff` skill cited author-repo-internal files via
bare `<repo-root>/`/`docs/`-relative notation that dangles in a downstream repo
that vendors the skills (observed in corca-ai/ceal). Doc/portability class.

Narrow Stage A fix (handoff package only), 14 files = 7 source + 7 plugin mirror:
- `skills/public/handoff/references/chunked-routing.md`: 3 author-only cites
  (`docs/handoff-chunked-routing.md`, `tests/test_handoff_chunker_trigger.py`,
  `docs/conventions/operating-contract.md`) qualified inline with an
  authoring-repo marker; stray `<repo-root>/` prefixes dropped on
  operator-surface/output paths; achieve cite made skill-relative.
- 6 chunker script docstrings: cite in-package `references/chunked-routing.md`
  as the contract and qualify the author-only `docs/handoff-chunked-routing.md`;
  `chunked_routing_lib.py` also qualifies a fixture cite in a NotImplementedError.

## Success / Out of scope

Success: handoff-package cites no longer dangle downstream; deferral tracked;
mirror in sync; no operator surface falsely rewritten.
Out of scope (deferred to follow-up): the portability guard in
`scripts/skill_portability_lib.py`; the same-class cross-skill cites outside
handoff. A first over-broad fix (flag-everything guard → 122 files,
marker-spam on legit operator surfaces) was reverted before this narrow slice.

## Counterweight Triage

- [Act Before Ship] `chunked-routing.md` operating-contract line had the marker
  spliced mid-sentence (doubled "in the charness source repo", stacked
  parentheticals). FIXED before commit — now a single clean trailing marker.
- [Over-Worry] Markdown links / Python docstring syntax / over-marking of
  operator surfaces: all verified clean. No bare unmarked author cite remains
  in the handoff package (scan: REMAINING_UNMARKED=0).
- [Valid but Defer] Recurrence: with the guard deferred, nothing mechanically
  prevents the next edit from reintroducing a bare cite. Mitigation goes to the
  follow-up: (a) build the precise guard, (b) add the marker-convention pointer
  to `create-skill/references/portable-authoring.md` (already states the rule),
  (c) sweep the cross-skill sibling cites.

## Next Move

Commit the narrow fix (Close #250). File the follow-up issue carrying the
guard + cross-skill sweep + portable-authoring marker-convention note.

## Verification

- `validate_skills` = 0; `check_doc_links` = 0; `check_markdown_inline_code` = 0;
  `check_references_link_inventory` = 0
- `pytest -k handoff_chunker` = 117 passed
- plugin mirror byte-for-byte in sync via
  `export_plugin.py --host claude --output-root . --with-marketplace`
