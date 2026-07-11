# Critique Review
Date: 2026-07-11

## Decision Under Review

Keep every generated quality artifact on the validator-owned `# Quality Review`
H1 while preserving a caller's custom title as additive `Title:` metadata and in
the scaffold payload.

## Failure Angles

- A custom H1 would remain invalid even if nearby string assertions passed; the
  direct, CLI, and exported-plugin tests each execute the real validator.
- Treating `Title:` as a new machine schema would add policy beyond the observed
  defect. It remains human metadata until a real consumer requires a parser.
- The plugin copy is derived from the public skill source and was regenerated,
  byte-compared, and exercised through the exported-plugin test.

## Counterweight Pass

- No new title validator, sanitizer, CLI option, or mirror-only test is needed.
- The regenerated working-tree packet names all three changed Slice A paths;
  the reviewer's only initial evidence finding is cleared.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/critique/2026-07-11-quality-scaffold-h1-worktree-packet.md | action: fix | note: regenerate the packet against the working-tree diff; cleared on reviewer follow-up
- F2 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/scaffold_quality_artifact.py | action: document | note: do not add a title schema or sanitizer without a machine consumer
- F3 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_quality_artifact.py | action: defer | note: formalize Title metadata only if a machine consumer appears

## Reviewer Tier Evidence

- Requested tier: high-leverage, for public-skill validator and export compatibility.
- Requested spawn fields: model and reasoning override were sent through the host spawn surface.
- Host exposure state: metadata-hidden
- Application state: unverified; the host accepted the requested fields but did not confirm provider application.

## Fresh-Eye Satisfaction

parent-delegated; the bounded reviewer consumed the regenerated working-tree
packet, reported no remaining act-before-ship finding, and rail-1 verification
returned `ok: true` with zero drift.

## Boundary Ownership

- Producer: the quality scaffold and its caller-provided title.
- Consumer: the artifact author/human reader and the quality artifact validator.
- Owning surface: `skills/public/quality/scripts/scaffold_quality_artifact.py`; the plugin path is derived.
- Verdict: owned-correctly
