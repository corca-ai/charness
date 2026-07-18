# Critique Review
Date: 2026-07-18

## Decision Under Review

Reduce two concrete hidden couplings: physical-line evidence-marker semantics
and the CLI reference generator's private duplicate command-path list.

## Failure Angles

- Semantic boundary: an indented nested list or block quote must not exempt its
  parent citation merely because it follows physically.
- Interface boundary: parser paths, command-docs help argv, and generated docs
  must disagree loudly without one contract record silently overwriting another.
- Operational boundary: avoid copying a repo-wide durability scan into every
  artifact validator or expanding the fix into a full Markdown parser.

## Counterweight Pass

- Act Before Ship: reject nested-list/block-quote marker scope and duplicate or
  missing command-doc paths with direct regressions; completed.
- Bundle Anyway: retain byte-identical generated output and focused parser-order
  coverage through the checked-in reference comparison; completed.
- Over-Worry: per-artifact copies or early scheduling of the entire repo-wide
  durability scan would create a second owner and validate-all noise.
- Valid but Defer: use a full Markdown AST only if the conservative continuation
  grammar encounters a real unsupported authoring case.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_check_spec_evidence_durability.py | action: fix | note: nested lists and block quotes cannot exempt a parent citation
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_command_docs_gate.py | action: fix | note: duplicate and missing command paths fail inside the renderer
- F3 | bin: over-worry | evidence: strong | ref: docs/conventions/validator-timing-layers.md | action: document | note: repo-wide durability remains centrally owned
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/check_spec_evidence_durability.py | action: defer | note: full Markdown parsing waits for a concrete unsupported case

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority, fork_turns=none.
- Host exposure state: requested_fields_sent
- Application state: host accepted the fields but exposed no provider-application metadata.

## Fresh-Eye Satisfaction

parent-delegated — semantic and CLI angles plus a separate counterweight consumed
`2026-07-18-051829-packet.md`; parent fingerprint verification returned `ok: true`
with no drift after both phases.

## Boundary Ownership

- Producer: durability policy for citation semantics; CLI parser for topology;
  command-docs YAML for documented help invocations.
- Consumer: repo-wide evidence gate and generated CLI reference/operator.
- Owning surface: central durability checker and CLI reference renderer joining
  parser-owned order with command-doc-owned argv.
- Verdict: owned-correctly
