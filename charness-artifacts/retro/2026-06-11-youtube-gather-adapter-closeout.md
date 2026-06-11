# YouTube gather and adapter renderer closeout retro

Mode: session

## Context

This reviews the goal
`2026-06-11-youtube-gather-and-adapter-renderer-hygiene`: #352 YouTube gather
support and #353 adapter-lib YAML renderer hygiene. The work touched support
skills, public gather rendering, adapter parsing/rendering, plugin exports,
debug/gather/critique/issue/goal artifacts, and broad repo validation.

## Evidence Summary

- Goal artifact:
  `charness-artifacts/goals/2026-06-11-youtube-gather-and-adapter-renderer-hygiene.md`
- Gather proof:
  `charness-artifacts/gather/2026-06-11-youtube-hak1koqwm18-unavailable-details.md`
- Debug RCA: `charness-artifacts/debug/latest.md`
- Closeout critique:
  `charness-artifacts/critique/2026-06-11-youtube-gather-and-adapter-renderer-closeout-critique.md`
- Issue closeout draft:
  `charness-artifacts/issue/2026-06-11-issues-352-353-closeout-commit-message.md`
- Final validation: changed-surface validators and broad pytest
  (`2771 passed, 4 skipped, 26 deselected`).
- Host-log probe:
  `charness-artifacts/retro/2026-06-11-youtube-gather-adapter-host-log.md`

## Waste

- The adapter parser fix initially over-refused real workflow-style block
  scalars; broad tests caught that, but the round trip cost came from treating
  unsupported YAML refusal and current workflow compatibility as one decision.
- The issue closeout draft initially failed the bug sibling predicate because a
  continuation line named `proof:` was parsed as a separate field. The live
  closeout-shape helper and validator caught it before commit, but the first
  draft still encoded the shape by habit instead of by exact parser behavior.
- Validation was repeated after critique folds and artifact updates. That was
  appropriate for the phase, but it reinforces that final artifact edits should
  be batched before the last broad gate when possible.

## Critical Decisions

- Kept #352 and #353 as independent implementation slices inside one goal,
  preventing the YouTube path from inheriting adapter-renderer assumptions.
- Recorded unauthenticated YouTube proof as blocked/missing-tool rather than
  treating the live URL as transcript evidence.
- Added limited block-scalar support instead of declaring every block scalar
  unsupported; this preserved existing workflow adapter use without becoming a
  general YAML implementation.
- Validated the same direct-commit issue carrier separately for #352 as
  feature-class and #353 as bug-class, preserving the issue-specific
  acceptance boundary.

## Expert Counterfactuals

- Gary Klein would have premortemed the closeout draft parser earlier: the
  likely failure was not "missing prose" but one field-looking continuation
  stealing evidence from the required field. The changed action is to consult
  the live shape helper before writing mixed-class closeout carriers.
- Gerald Weinberg would have separated "unsupported YAML" from "unsupported by
  this adapter seam." The changed action is the one taken after test failure:
  preserve the common workflow block-scalar subset and refuse only the subset
  that the renderer cannot honestly round-trip.

## Next Improvements

- workflow: before locking a direct-commit closeout carrier that covers
  multiple issues or classifications, run
  `describe_closeout_draft_shape.py` and validate the exact commit-message
  file for each issue-specific classification before final artifact edits.
- workflow: when a support/export surface is touched, keep the final sequence
  as sync plugin/debug exports, then changed-surface validators, then broad
  pytest, then only artifact-only edits plus the narrow artifact validators.
- memory: record that `proof:`-style continuation lines inside issue closeout
  draft fields can be parsed as new fields; use semicolon or same-field prose
  when a field requires both decision and proof.

## Sibling Search

Structural pattern: field-shaped continuation text in markdown artifacts can
accidentally escape the intended verifier field.

Triggering instance(s): the `Siblings:` field in the #353 direct-commit
closeout draft lost its proof token when the continuation line began with
`proof:`.

Siblings scanned: issue closeout drafts, goal closeout evidence lines, debug
RCA fields, critique structured findings, and retro improvement/disposition
lines. The live validators already cover issue closeout and critique fields;
goal and debug validators cover required evidence headings; retro disposition
review is the judgment layer for improvement classification.

Destination: applied: the closeout draft now keeps `decision` and `proof` in
the same `Siblings:` field value and both `validate-closeout-draft` runs pass.
No new issue is needed.

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-11-youtube-gather-adapter-closeout.md`
