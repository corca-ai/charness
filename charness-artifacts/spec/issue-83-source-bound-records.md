# Spec: Issue #83 - Source-Bound Records

Source: https://github.com/corca-ai/charness/issues/83

## Problem

Multi-source workflows can accidentally let the model bind extracted fields to
the wrong source or principal when interpretation and commit payload assembly are
mixed. The risk matters most when the workflow also performs an external,
irreversible, expensive, or hard-to-dedupe side effect.

## Current Slice

Teach a source-bound record pattern in the public authoring surfaces. This slice
does not define a generic batch intake schema or runtime helper.

## Fixed Decisions

- Primary home: `create-skill`, because this is a skill-authoring failure mode.
- Crossrefs: `create-cli`, `spec`, and `impl` should name the external-write
  boundary without duplicating the full pattern.
- Cardinality: one `ExtractionCandidate` envelope belongs to one source item and
  may validate into zero or more `ValidatedIntent`s.
- Code owns joins, idempotency, commit payload assembly, and final reports. The
  model echoes existing source item ids only.
- Final user-visible facts come from `report.json` or commit artifacts, not from
  agent recomputation.

## Non-Goals

- Generic batch intake schema.
- Extraction provider ladder.
- Admin review UI.
- Cross-messenger universal source identity taxonomy.
- Ceal-specific receipt policy in Charness or in a Slack adapter.

## Success Criteria

- `create-skill` carries a source-bound external-write failure mode and a
  reference describing the pattern.
- `create-cli` connects the pattern to prep/execute artifacts for agent-facing
  multi-source external-write commands.
- `spec` and `impl` require the contract to name source identity, cardinality,
  validation, idempotency evidence, and report ownership when model-authored
  payloads cross an external-write boundary.
- Tests pin the public anchors and the deliberately scoped non-goals.

## Acceptance Checks

- `rg -n "source-bound|SourceRecord|ExtractionCandidate|ValidatedIntent|report.json" skills/public`
  finds the intended anchors.
- Focused quality tests pass for the new public guidance.
- Plugin manifests are synced before validation.

## Premortem

- Misread: future agents turn this into a universal schema. Counterweight: keep
  non-goals and "not a generic schema" explicit.
- Misread: duplicate source ids are rejected too broadly and block valid
  one-source-to-many-intent workflows. Counterweight: reject duplicate candidate
  envelopes for one source, while allowing multiple validated intents from that
  source.
- Misread: final response recomputes facts from chat context. Counterweight:
  make `report.json` or commit artifacts the final report owner.

## Fresh-Eye Premortem

Fresh-Eye Satisfaction: parent-delegated.

- Act Before Ship: prompt-affecting surfaces require refreshing
  `charness-artifacts/cautilus/latest.md`. The maintained instruction-surface
  proof passed after the Cautilus eval command was run with the checked-in
  fixture.
- Bundle Anyway: the initial test overfit Markdown wrapping around
  `source/principal binding drift`; fixed by normalizing whitespace and adding
  direct scope assertions.
- Over-Worry: the reference is not leaking into a generic batch schema; it
  requires multiple source items plus source/principal binding risk plus
  external side effects, and it excludes read-only synthesis.
- Valid But Defer: minimum `report.json` fields can wait for a real adopter;
  forcing them now would turn this guidance into the generic schema this issue
  deliberately avoids.

## First Implementation Slice

Add one reference and small public-core anchors, then cover them with focused
tests and the maintained Cautilus instruction-surface proof.
