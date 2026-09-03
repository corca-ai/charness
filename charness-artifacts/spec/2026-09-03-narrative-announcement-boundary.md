# Narrative/announcement boundary: spec-phase rationale and satisfied checklists, moved out of `docs/narrative-announcement-boundary.md` on 2026-09-03

## Problem

`narrative` and `announcement` were drifting into overlapping territory.

The intended split is:

- `narrative`: align durable truth and compress it into one audience-neutral
  brief skeleton
- `announcement`: adapt that aligned story or brief for one concrete audience,
  language, tone, length, and delivery channel

Without that split, the same repo story has to be regenerated whenever the
audience changes, and repo adapters start carrying delivery-local concerns that
do not belong in the truth-alignment layer.

## Success Criteria

- `narrative` public docs describe the brief as audience-neutral.
- `narrative` no longer frames audience/language/channel adaptation as its own
  primary responsibility.
- `narrative` adapter contract records repo-specific brief skeleton structure
  through `brief_template`.
- `announcement` is clearly described as the next step when one aligned story
  must be tailored for different audiences or delivery targets.

## Acceptance Checks

- narrative resolver accepts `brief_template`
- narrative adapter example and current repo adapter include the new field
- docs and tests describe the new boundary without contradicting announcement
