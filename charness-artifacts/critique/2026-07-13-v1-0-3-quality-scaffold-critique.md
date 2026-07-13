# v1.0.3 Quality Scaffold Durability Critique
Date: 2026-07-13

## Decision Under Review

Add the canonical same-line reproduction-source marker to the quality
artifact scaffold's gitignored runtime-signal citation, sync the plugin mirror,
and freeze the generated output with one focused regression.

Packet Consumed:
`charness-artifacts/critique/2026-07-13-v1-0-3-quality-scaffold-packet.md`.

## Failure Angles

- Producer/final consumer: the scaffold produces the persisted citation and
  the durability validator consumes it. Fixing the literal prevents every
  scaffold user from inheriting the invalid evidence claim.
- Coverage: the scaffold test proves path and marker share one physical line;
  existing durability tests own marker grammar and reject unrelated-line
  markers. A duplicate integrated test would add overlap without new semantics.
- Portability: the marker is a Markdown HTML comment; it changes no adapter,
  command, path resolution, or runtime behavior.
- Siblings: all scaffold scripts were searched for `.charness` citations; only
  quality source and plugin mirror matched.

## Counterweight Pass

- Act Before Ship: run focused scaffold tests, final consumer durability,
  source/plugin parity, packaging, debug/seam-index, and public quality
  skill/dogfood validators on exact bytes.
- Bundle Anyway: include the debug record and generated seam-risk index because
  the failure escaped from producer to final consumer during the v1.0.2 lock.
- Over-Worry: do not alter durability grammar, add a reusable citation API,
  duplicate the final-consumer gate, run Cautilus, or raise semver above patch.
- Valid but Defer: unrelated hand-authored ignored-path citations and broader
  ignored-evidence authoring ergonomics.
- Verdict: APPROVE the bounded fix and patch release after exact-byte proof.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/quality/scripts/scaffold_quality_artifact.py | action: fix | note: prove generated same-line marker through focused scaffold and final durability consumer
- F2 | bin: over-worry | evidence: strong | ref: scripts/check_spec_evidence_durability.py | action: defer | note: existing grammar is correct and needs no expansion
- F3 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/debug/2026-07-13-quality-scaffold-reproduction-source-omission.md | action: defer | note: unrelated hand-authored ignored citations are outside this producer defect

## Public Skill Evaluation Review

- `quality` dogfood is `hitl-recommended`; the maintained case was inspected.
  Routing, planner reads, gate sequencing, structural judgment, and artifact
  path contracts are unchanged.
- No dogfood or scenario mutation is warranted. Generated-template output and
  the deterministic durability consumer directly observe this repair.
- Cautilus planner reports `required: false`, `next_action: none`, and
  ask-before-run. No Cautilus execution is claimed.

## Reviewer Tier Evidence

- Requested tier: high-leverage for a public-skill artifact producer.
- Requested spawn fields: model=gpt-5.5, reasoning_effort=medium, service_tier=priority.
- Host exposure state: requested_fields_sent
- Application state: provider application not exposed; no application claim.

## Fresh-Eye Satisfaction

parent-delegated — two read-only angles and one separate counterweight approved;
parent fingerprints verified zero worktree/index drift for every accepted pass.

## Boundary Ownership

- Producer: quality scaffold emits the Runtime Signals citation.
- Consumer: evidence-durability validator judges persisted artifact citations.
- Owning surface: public quality scaffold source plus installed plugin mirror.
- Verdict: owned-correctly

## Non-Claims

No validator-policy change, broader ignored-path grammar, arbitrary evidence
reproducibility proof, Cautilus run, issue closure, or minor-version behavior.
