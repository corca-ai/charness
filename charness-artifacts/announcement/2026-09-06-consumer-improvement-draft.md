# Consumer improvement release announcement draft

Date: 2026-09-06
Delivery: draft-only; no announcement adapter is configured. Public release notes
are published separately by the authorized release owner.

## Draft

Charness now gives ordinary implementation work clearer guidance on reusing
applicable evidence while preserving independent proof at release boundaries.
Review previews can continue into live execution without consuming the live
attempt, and release advisory findings retain their meaning instead of being
described wholesale as known inaccuracies.

Installed-package consumer journeys preserve the requested alias and existing
script behavior. Repeated-work results are mixed: the CLI journey improves,
while spec-to-impl repeats increase. The release makes no general speed claim.

Update with `charness update`, then check `charness version`.

## Sources and omission

- `../probe/2026-09-06-consumer-journeys/consumer-comparison.md`
- `../debug/2026-09-06-release-advisory-meaning.md`
- `../debug/2026-09-06-critique-preview-live-collision.md`
- Internal fixture mechanics, raw token totals and tracker bookkeeping are
  omitted from the short draft; the linked evidence retains the limitations.
