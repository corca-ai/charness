# Critique Review
Date: 2026-06-26

## Decision Under Review

Use in-process `load_adapter()` calls in public skill dogfood matrix generation
instead of spawning each public skill `resolve_adapter.py`.

## Failure Angles

- Import safety: a resolver that works as a command could fail when imported.
- Behavior drift: command output and direct `load_adapter()` payloads could
  diverge.
- Generated surface drift: root script changes must sync the plugin mirror.

## Counterweight Pass

- Most resolver scripts already expose `load_adapter()` and command `main()`
  delegates to that function.
- Resolvers without `load_adapter()` still use the previous subprocess fallback.
- Focused public-skill dogfood tests passed, cProfile showed the intended speed
  reduction, boundary ratchet passed, and plugin mirror drift check passed.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/public_skill_dogfood_lib.py | action: fix | note: dogfood validation dropped from roughly 0.80s to 0.11s by avoiding 17 resolver subprocesses
- F2 | bin: valid-but-defer | evidence: moderate | ref: scripts/public_skill_dogfood_lib.py | action: defer | note: only add import-failure fallback if a concrete resolver import-safety issue appears

## Reviewer Tier Evidence

- Requested tier: n/a
- Requested spawn fields: n/a
- Host exposure state: unsupported
- Application state: same-agent low-risk critique only

## Fresh-Eye Satisfaction

not spawned: deterministic speed optimization with focused proof, cProfile
evidence, unchanged ratchet, and synced generated surface.
