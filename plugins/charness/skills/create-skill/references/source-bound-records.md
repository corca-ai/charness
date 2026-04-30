# Source-Bound Records

Use this pattern when all of these are true:

- the workflow handles multiple source items
- source identity or principal binding matters
- the workflow performs external, irreversible, expensive, or hard-to-dedupe
  side effects

Do not apply it to read-only summaries or ordinary multi-document synthesis.

## Pattern

1. Deterministic code collects `SourceRecord`s with immutable `itemId`, source
   digest, source path or id, message/thread provenance, and user or principal
   provenance.
2. The model fills one `ExtractionCandidate` envelope per source item. It may
   extract zero or more domain items inside that envelope, but it must only echo
   an existing `itemId`.
3. Deterministic validation rejects unknown item ids, missing item ids, and
   duplicate candidate envelopes for the same source before commit. A source
   may still validate into zero or more `ValidatedIntent`s.
4. Deterministic commit code owns joins, idempotency, destination evidence or
   ledger lookup, partial success, and external side effects.
5. Deterministic report code emits `report.json`; the final agent response uses
   that artifact or commit artifacts instead of recomputing facts from context.

The record is source-bound, not row-bound. One source can produce no validated
intent, one validated intent, or several validated intents without losing the
source/principal binding.

## Required Contract

Name these before implementation:

- source identity: source id/path/digest plus uploader, user, message, thread,
  permalink, or equivalent host evidence
- cardinality: `SourceRecord -> ExtractionCandidate -> ValidatedIntent(s) ->
  CommitResult(s)`
- validation: how unknown, missing, and duplicate source item ids are rejected
- idempotency: destination evidence, ledger, or lookup used to avoid duplicate
  side effects
- report owner: the `report.json` or commit artifact fields that user-visible
  facts must come from
- retention: which source artifacts, OCR text, personal data, and destination
  evidence are retained, redacted, or kept transient

## Failure Modes To Simulate

- copied fields from one source onto another source id
- uploader or principal attached to the wrong extracted item
- row-oriented output that loses the source item envelope
- partial commit that cannot tell which source succeeded
- retry that creates duplicate destination records because idempotency was only
  promised in prose
- final response that summarizes chat memory instead of the checked report

## Non-Goals

- generic batch intake schema
- extraction provider ladder
- admin review UI
- cross-messenger universal source identity taxonomy
