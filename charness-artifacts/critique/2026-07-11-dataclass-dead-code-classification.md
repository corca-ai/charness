# Critique Review
Date: 2026-07-11

## Decision Under Review

Classify Vulture findings for annotated fields directly inside dataclass bodies
as structured-output fields using source AST, instead of repeatedly sending
them to the generic human review queue.

## Failure Angles

- Name allowlists would encode repo accidents. The runner matches finding line
  and name to an annotated field under a syntactic dataclass decorator.
- Ordinary class and module annotations must remain review candidates; focused
  negatives pin both branches.
- Qualified/called and nested decorators are separate AST branches; the fixture
  covers direct `@dataclass` and nested `@dataclasses.dataclass(frozen=True)`.
- Re-reading every file per finding would move waste rather than remove it; the
  parser caches field locations once per finding path.

## Counterweight Pass

- No blocking floor, exact-name exemption list, import-resolution theorem, or
  ClassVar/InitVar policy was added. This remains a non-blocking triage aid.
- Context-free callers retain the prior `rss_kib` hint; real runs use AST
  context and therefore do not extend that name heuristic.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_quality_dead_code_advisory.py | action: fix | note: cover qualified/called and nested dataclass decorator branches; cleared
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/run_dead_code_advisory.py | action: document | note: retain line-name matching, per-path cache, and ordinary annotation negatives
- F3 | bin: over-worry | evidence: moderate | ref: skills/public/quality/scripts/run_dead_code_advisory.py | action: defer | note: do not resolve decorator imports or add ClassVar/InitVar policy for this syntactic advisory

## Reviewer Tier Evidence

- Requested tier: high-leverage for a public quality classifier and repeated-review signal.
- Requested spawn fields: lower-power read-only explorer fields were sent through the host spawn surface.
- Host exposure state: metadata-hidden
- Application state: unverified; host acceptance did not expose provider application.

## Fresh-Eye Satisfaction

parent-delegated; the reviewer consumed the worktree packet, identified one
missing branch-proof item, then cleared it after the focused fixture extension.
Both rail-1 verifies returned zero drift.

## Boundary Ownership

- Producer: Vulture line/name findings plus repo source AST.
- Consumer: dead-code summary and human cleanup triage.
- Owning surface: public quality advisory; plugin copy is derived.
- Verdict: owned-correctly
