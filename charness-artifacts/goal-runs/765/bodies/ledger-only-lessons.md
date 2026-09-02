<!-- charness-work-item-key: ledger-only-lessons -->

## Situation

The operator has asked more than once that charness keep one lesson surface, the ledger (`charness-artifacts/retro/lesson-ledger.json` and its selection index), and delete the generated `recent-lessons.md` digest. On 2026-08-29 that request was implemented for consumers only: #750 added `summary_path: null` so a retro adapter can decline the Markdown projection (commit 030aa8262), and AGENTS.md was re-routed to read the ledger preview at session start (cb5d2902a). This repository's own `.agents/retro-adapter.yaml` still declares `summary_path: charness-artifacts/retro/recent-lessons.md`.

## Experience

Every retro persist rewrites the digest, `validate-retro-lesson-index` byte-compares it, and `goal_run_pickup.py` projects its lessons from the digest rather than the ledger. On 2026-09-02 the Goal Run #765 session could not leave a session-start pointer for the next session in the digest because the byte comparison would refuse it, and had to route the next session through the activation phrase instead. The operator read the surviving file as the request not having been honoured.

## Evidence

- `.agents/retro-adapter.yaml` line 7: `summary_path: charness-artifacts/retro/recent-lessons.md`.
- `scripts/recent_lessons_lib.py:447` compares the digest bytes to the expected projection; a hand edit fails `validate-retro-lesson-index`.
- `skills/public/achieve/scripts/goal_run_pickup.py` reads `charness-artifacts/retro/recent-lessons.md` for the pickup's advisory lessons.
- 35 live files under `scripts/`, `skills/`, `.agents/`, and `docs/` name `recent-lessons` (grep, 2026-09-02).
- #750 closeout: the opt-out exists and is tested for three declaration states; nothing applied it here.

## Impact

Two lesson owners where the operator decided on one: the digest costs a rebuild and a validation on every retro, blocks any hand-written pointer, and makes the ledger look optional. The recurrence is a rework instance caused by two skills' contracts.

Causing skill: retro, achieve

## Work Item (Goal Run #765, added by amendment on 2026-09-02)

### Owned scope

- Set `summary_path: null` in this repository's `.agents/retro-adapter.yaml` and delete `charness-artifacts/retro/recent-lessons.md`; the ledger and `lesson-selection-index.json` remain the only lesson surfaces here.
- Make `goal_run_pickup.py` project its advisory lessons from the ledger preview (`render_lesson_selection_preview`, the same read AGENTS.md prescribes) when the adapter declares no digest; keep the digest read only as the consumer-facing fallback when a digest is declared.
- Remove `validate-retro-lesson-index`'s digest comparison from this repository's lane when no digest is declared, and prove the lane stays green with the ledger alone.
- Disposition the 35 live references by name: consumer-facing docs and the retro skill keep describing the digest as an option; charness-only prose stops naming it as this repo's surface.

### Acceptance

- `recent-lessons.md` is absent, `/goal #765` pickup returns `verified-read` with lessons sourced from the ledger preview, and the read-only quality lane is green.
- A seeded consumer adapter that still declares a digest keeps the current behaviour (one existing test suffices).

### Dependencies

subprocess-retroactive-removal (order only; no code dependency).

### Non-claims

No change to the ledger schema, scoring, or lifecycle. No change to what consumers may declare.

AI provenance: drafted and filed by an AI agent from the operator's approval on 2026-09-02.
