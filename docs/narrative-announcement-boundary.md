# Narrative And Announcement Boundary

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

## Fixed Decisions

- `narrative` owns durable truth alignment first.
- `narrative` may also derive one audience-neutral brief skeleton from that
  aligned truth.
- `narrative` adapter may declare `brief_template` as an ordered list of brief
  section labels.
- `announcement` owns audience adaptation, language adaptation, channel fit,
  and backend delivery.
- `announcement` adapter may declare one logical delivery capability when a
  human-backend delivery path needs reusable private access.

## Non-Goals

- teaching `narrative` to post to chat backends
- turning `announcement` into the source-of-truth alignment skill
- embedding audience-local formatting rules into narrative adapter defaults

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
