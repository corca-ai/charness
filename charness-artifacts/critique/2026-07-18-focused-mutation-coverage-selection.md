# Focused Mutation Coverage Selection Critique
Date: 2026-07-18

## Decision Under Review

Teach the focused coverage suggester to find split `Path` references and the
nearest same-directory local-loader ancestors, while leaving broad pytest and
the changed-line consumer authoritative.

Diff Scope: selector source, generated plugin mirror, and focused regression
tests. Packet Consumed: `2026-07-18-125952-packet.md`.

## Failure Angles

- Diagnostic correctness: breadth-first ancestry must terminate, prefer direct
  tests, and recognize the loader forms actually present in this repo.
- Test economics: a smaller producer is useful only if it cannot become a
  terminal proof claim or silently replace broad pytest.
- Operator contract: candidate filtering must emit runnable standing test
  targets, and the explanation must describe evidence rather than trust.

## Counterweight Pass

- The first follow-up review found a real whitespace regression in the widened
  `_load_sibling` regex. It was fixed and pinned by a multiline fixture; the
  second follow-up accepted the repair.
- The repo-backed two-argument loader form and non-terminal wording were cheap
  fixes in the touched boundary and were bundled.
- AST parsing, a dependency registry, arbitrary pytest naming support, and a
  YAML migration are unsupported expansion here. This helper's documented
  automation interface remains JSON; the root Charness CLI's YAML-first policy
  is a different boundary.
- Mapping provenance would improve diagnostics, but the current payload plus
  explicit broad fallback is sufficient for this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: scripts/suggest_mutation_coverage_command.py:70 | action: fix | note: restore whitespace-tolerant one-argument loader matching
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/lifecycle_usage_capture.py:28 | action: fix | note: recognize the repo's two-argument local sibling loader
- F3 | bin: bundle-anyway | evidence: moderate | ref: scripts/suggest_mutation_coverage_command.py:178 | action: fix | note: describe the subset as coverage evidence while retaining broad proof
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/suggest_mutation_coverage_command.py:188 | action: defer | note: add mapping provenance only when operator evidence shows diagnosis cost
- F5 | bin: over-worry | evidence: weak | ref: scripts/suggest_mutation_coverage_command.py:66 | action: document | note: AST inference and a dependency registry add maintenance without an observed miss

## Reviewer Tier Evidence

- Requested tier: high-leverage
- Requested spawn fields: fork_turns=none, model=gpt-5.6-terra, reasoning_effort=medium, service_tier=priority
- Host exposure state: requested_fields_sent
- Application state: spawn calls accepted the requested fields; provider-applied model metadata was not independently exposed.

## Fresh-Eye Satisfaction

parent-delegated: two contrasting angle reviewers and one separate counterweight
reviewer ran read-only. A correctness reviewer then accepted the repaired
follow-up diff. Parent fingerprint verification reported no worktree, index, or
HEAD drift around either review boundary.

## Boundary Ownership

- Producer: the repo-owned selector produces a conservative candidate mapping from changed files to standing tests.
- Consumer: the changed-line coverage gate judges measured lines; broad pytest separately judges the bundle.
- Owning surface: repo-python with checked-in-plugin-export synchronization.
- Verdict: owned-correctly
