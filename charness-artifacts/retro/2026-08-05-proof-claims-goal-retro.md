# Goal Closeout Retro — proof claims explicit, scoped, and actionable
Date: 2026-08-05
Goal: charness-artifacts/goals/2026-08-05-make-proof-claims-explicit-scoped-actionable.md

## Context

This retro reviews the five-track local proof goal after #502 implementation,
#496 re-verification, #491/#504/#506 independent dispositions, and the final
quality/mutation bundle. Strong claims come from the committed focused tests,
the final `run-quality.sh --read-only` receipt, the full changed-line coverage
consumer, the issue carriers, and the fresh-eye claims review. Judgment claims
are labeled as such; remote issue state remains a separate boundary.

## Window

The closeout window runs from the activated goal and Slice B commit
`c5519bfb` through the quality-record commit `2c40cfc9`. The final local proof
was run against `HEAD` `2c40cfc98f77bc965e5fd7c3f96fb4331950d2ed` before the
final goal/carrier edits in this closeout.

## Evidence Summary

- The final read-only quality gate passed 85 checks, 0 failures, in 124.6s;
  its changed-line consumer passed in 121.4s.
- The independent full coverage consumer passed 7,108 tests with 79
  deselected, no blocking files, and `ok: true` against `origin/main`.
- The exact five-file #502-focused command passed 101 tests in 31.90s after
  the final receipt-branch tests were added.
- #496 passed 85 focused tests; #504 passed 29; #506 passed 24. The #506
  carrier is `charness-artifacts/issue/2026-08-05-issue-506-local-disposition.md`.
- The quality record, pinned inventory probes, source/plugin parity, artifact
  validators, and the final independent claims review are the durable proof
  surfaces. No metrics command is configured, so no goal-scoped token or host
  efficiency total is claimed.
- Packet Consumed: `charness-artifacts/retro/2026-08-04-235906-packet.md`.

## Waste

- Workflow waste (strong): the first final claims review caught stale
  `Final Verification`/`Auto-Retro` text, a missing #506 carrier, and the old
  #502 test count. The stale text survived because closeout editing followed
  the first green bundle instead of a describe-first final-record pass. The
  repair is to complete the goal record and rerun the claims observer after
  every final carrier or test-count change.
- Gate-baseline runtime (measured, necessary for this proof but still debt):
  the full direct coverage producer took 837.60s for 7,108 tests, followed by
  context-JSON serialization. The configured quality gate itself passed in
  124.6s, but recurring local telemetry independently records over-budget
  pytest/closeout families. This cost is routed to existing issue #505, not
  absorbed as a reason to weaken proof.
- Polling waste (proxy): repeated short waits were required while the coverage
  producer serialized a multi-gigabyte context report. No host metric source
  records a per-goal tool-call total, so this is a workflow-shape observation,
  not a measured token claim.

## Critical Decisions

- Kept five independent owners/readers and rejected a universal receipt or
  closure transaction. This preserved the user's umbrella outcome while
  preventing one terminal green from standing in for five behaviors.
- Added focused tests for every changed-line blocker reported by the mutation
  consumer. The production receipt behavior did not change; the proof gap was
  real and had to be covered before the green result was trusted.
- Recorded #506 as a local open disposition with a durable blocker rather than
  implying issue closure. The helper behavior is locally established, while
  remote readback and a #506-specific closeout critique remain future work.

## Trends vs Last Retro

The recent-lessons digest warns against stale goal binding and says to freeze
quality artifacts before broad verification. This run reproduced the same
class at a smaller scale: a final goal section and focused count lagged behind
the actual committed proof. The correction was applied in-session by adding
the carrier, refreshing the count, and requiring another independent claims
read; the lesson is reinforced rather than treated as a new universal gate.

## North Star Alignment

P1 held for the reversible record repairs: the stale wording, probe refresh, and
carrier additions were corrected by judgment and focused validators. P4/P5 held
at the proof boundary: the mutation consumer refused uncovered receipt
branches, and an independent claims reviewer read the goal rather than treating
the green gate as completion. The misapplication was temporary but material:
the first closeout record treated a green bundle as sufficient while its own
final sections and one track carrier were stale or absent. The named failure
signature was terminal trust in one evidence channel; the repair was a
different observer plus different record/test channels.

## Expert Counterfactuals

- Ousterhout lens: a strong designer would have split the final proof record
  into one owner-facing carrier per issue before writing the umbrella's final
  summary. That would have exposed #506's missing carrier and prevented the
  matrix from being mistaken for evidence.
- Kahneman lens: treat the first green bundle and remembered test count as
  anchoring signals, not facts. The required counterfactual is to recount and
  re-read the final artifact after the last test or carrier edit.

## Sibling Search

- same layer: goal final sections, quality record, and issue carriers | decision: same waste, fix now | proof: fresh-eye claims review plus `check_goal_artifact.py`, quality-artifact validation, and exact focused reruns
- abstraction up: generated probes, rolling pointers, and closeout ledgers | decision: same waste, fix now | proof: probe tests and pointer freshness rerun after the quality corpus changed
- specialization down: #491/#496/#504/#506 owner/readers | decision: intentional boundary | proof: matrix rows, separate carriers, and independent focused commands preserve distinct semantics
- mental-model siblings: recurring gate-baseline runtime and reviewer-window lineage | decision: valid follow-up outside the slice | proof: `mine_closeout_telemetry.py --detail` and the prior structural disposition review | follow-up: https://github.com/corca-ai/charness/issues/505

## Portable Candidate

not portable — the useful pattern depends on Charness's goal/issue/quality
artifact contracts, reviewer-boundary helper, and local closeout telemetry.

## Next Improvements

- workflow: `applied: run the exact focused count after the last test edit and
  require a claims reread after final carrier edits`.
- capability: `applied: add receipt-contract branch tests so changed-line
  mutation coverage cannot stop at an uncovered proof branch`.
- memory: `applied: keep the #506 local carrier and quality proof record bound
  to the active goal; leave remote closure as an explicit durable blocker`.
- gate-baseline: `issue #505 (recurs: gate-baseline-runtime and over-slice
  closeout cost); retain current proof floors while that separate track owns
  runtime design`.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-05-proof-claims-goal-retro.md
`skills/public/retro/scripts/persist_retro_artifact.py` with the canonical goal
binding and the recent-lessons digest refresh.
