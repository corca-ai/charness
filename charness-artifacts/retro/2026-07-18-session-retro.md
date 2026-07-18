# Session Retro
Date: 2026-07-18

## Mode

session

## Context

The first autonomous-improvement slice fixed an invalid `catalog list --json`
instruction and added a compact YAML summary, but the broad gate then exposed a
second problem: evidence-marker validity depended on the marker occupying the
same physical line as its citation. The operator correctly identified this as a
coupling smell and asked for sibling coupling risks to be examined as well.

## Evidence Summary

- `charness-artifacts/debug/2026-07-18-debug-review.md` records the minimal
  reproduction, falsified alternatives, root cause, and detection gap.
- `charness-artifacts/critique/2026-07-18-coupling-critique.md` records the
  bounded fresh-eye and counterweight review of the expanded fixes.
- The sibling scan found a second concrete coupling seam in
  `scripts/render_cli_reference.py`: command topology was duplicated in Python
  instead of being joined from the argparse parser and `.agents/command-docs.yaml`.
- Packet Consumed: `charness-artifacts/retro/2026-07-18-052559-packet.md`.

## Waste

The first pass treated the failing durability gate as an artifact-format fix.
That restored green locally but left the hidden physical-line assumption in the
validator. The rework came from scoping the symptom before naming the seam and
searching for sibling sources of truth.

## Critical Decisions

- Treat Markdown continuation text as part of the citation bullet while still
  rejecting nested lists, blockquotes, headings, and fences.
- Keep repo-wide durability scanning centralized; duplicating the parser or the
  scan into every artifact validator would create a larger coupling problem.
- Derive CLI reference topology and order from the real parser, and help argv
  from the YAML contract, with an explicit set-equality join guard.

## Expert Counterfactuals

- Engelbart's system-improving lens would have treated validator semantics,
  authoring language, and the gate schedule as one system at the first failure;
  the next move would have been a seam inventory before editing the artifact.
- Ousterhout's complexity lens would have asked which module owns each fact.
  That question directly reveals both physical-line leakage and the duplicated
  command registry.

## Sibling Search

- same layer: quality/debug artifact validators | decision: intentional boundary | proof: both consume the centralized repo-wide durability scan; duplicating its parser would split ownership
- abstraction up: evidence-durability contract and operating contract | decision: same waste, fix now | proof: both now define semantic citation-bullet continuation behavior
- specialization down: nested list and blockquote Markdown shapes | decision: same waste, fix now | proof: focused negative tests reject both shapes
- mental-model siblings: CLI reference command registry | decision: same waste, fix now | proof: renderer now joins argparse topology with `.agents/command-docs.yaml` and tests set mismatch plus duplicates

## Next Improvements

- workflow: after a broad-gate-only failure, name the violated seam and run the
  four-axis sibling scan before applying the smallest artifact edit.
- capability: retain explicit set-equality and ambiguity tests wherever two
  independently owned contracts are joined.
- memory: keep the detection gap, sibling findings, and concrete tests in the
  debug and critique artifacts committed with this slice.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-18-session-retro.md
