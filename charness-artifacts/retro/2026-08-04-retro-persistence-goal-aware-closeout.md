# Retro: Goal-Aware Retro Persistence Closeout

Date: 2026-08-04

Goal: charness-artifacts/goals/2026-08-04-retro-persistence-goal-aware.md

## Waste

The original closeout path could persist a retro before the owning goal identity
was checked. That made the first artifact, summary, lesson index, and event writes
the wrong place to discover a mismatch. The slice also spent review cycles on
metadata parsing boundaries that were initially under-specified: later headings,
indented Markdown headings, fence lengths, Setext headings, and slug-shaped output
all needed explicit tests.

An intermediate broad standing run during probe refresh found two plugin-parity
failures after the validator comment changed. The canonical mirror sync repaired
that drift; it is retained here as a reminder that generated surfaces and durable
quality artifacts are part of the measured corpus.

## Critical Decisions

- Keep goal awareness opt-in at the shared persistence writer so ordinary session
  and release retros retain their existing contract.
- Make only one exact top-level preamble `Goal:` field identity-bearing. Accept an
  exact path or slug as input, but write the canonical repo-relative path.
- Validate before every derived write, including `.charness/t-events` and output
  directory creation; prove the whole side-effect tree remains unchanged on refusal.
- Treat issue #504 remote closure as unproven while host-level enforcement of the
  caller flag remains unavailable. Local caller-contract proof is not remote proof.

## Next Improvements

- Applied: shared write-boundary identity validation, canonicalization, full-tree
  no-write tests, caller-contract regression coverage, and synchronized plugin mirrors.
- Applied: current-tree inventory probes were refreshed after the quality corpus
  changed, with the refusal count still measured at five citations across four artifacts.
- Out-of-scope: host-installed invocation proof and remote issue closure require a
  separate observer/channel and the existing issue closeout floor.

## Sibling Search

The issue causal review and bounded repair reads found the same producer/final-consumer
seam in the shared retro writer and achieve closeout guidance. No second persistence
writer was found that could bypass the shared library while preserving the current
session/release contract. The remaining sibling risk is caller enforcement on a host,
not another local writer.

## Verification

- Focused proof: 115 persistence, goal-library, and disposition tests passed.
- Pre-lock deterministic closeout: completed with broad pytest intentionally skipped.
- Locked broad and mutation results: pending — the frozen closeout bundle has not
  run yet, so no locked result is claimed; no Cautilus evaluation was requested.
- Non-claims: host-installed behavior, provider/live behavior, and remote issue closure
  are not established by this local artifact.

## North Star Alignment

The design north star held at the reversible local boundary: identity validation
is judgment-backed evidence protection, and ordinary session retros remain
supported. The failure signature was a write sequence that could discover an
ownership mismatch only after derived artifacts existed; the repair moved that
check to the shared writer and kept remote issue closure provisional because its
different observer and channel are unavailable here.

## Auto-Retro

Retro dispositions: applied: goal-aware persistence guard, canonical output, and no-write proof.
Structural follow-up: none — host invocation enforcement is unavailable in this local contract, so no additional guard is claimed.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-04-retro-persistence-goal-aware-closeout.md
