# hotl claim-fidelity — reconciliation MOVE capture (2026-07-01)

## Verdict

**MOVE EXECUTED + PROVEN: `proof-rules.md` retired from `requiredCommandFragments`.**
The reference-compaction Slice-7 census reconciliation rated hotl/proof-rules.md = MOVE
(census DUP — the 6 proof rules are inlined verbatim in SKILL.md `## Proof Rules`
L104-113, and the proof-LEVEL ladder is only a POINTER to the shared
`external-capability-proof-ladder.md` that SKILL.md L146 already lists directly). This
fresh capture proves the reduced floor.

## Spec change

`requiredCommandFragments`: `[proof-rules.md, ledger-and-dispositions.md]` → `[ledger-and-dispositions.md]`.
classTag: proof-rules.md = DUP (retired, stays declared for coverage), ledger-and-dispositions.md = DEPTH
(the completion-audit anti-proxy / P4 re-examination rule is genuine on-demand depth absent from SKILL.md).
No SKILL.md change — proof-rules.md was already fully inlined (that is WHY it is DUP).

## What ran

`/charness:hotl` (the spec's representative repo-guard proof prompt) at `HEAD`=0ee34676,
isolated worktree, exit 0, **451526ms** (< threshold 510000), 4.85M tokens, tool profile
Bash=33 Read=21 Write=3 Skill=1 Agent=1 Edit=1. Graded against the edited spec:

- **outcome=passed** — "All declared claims met." The RCF floor `[ledger-and-dispositions.md]`
  is satisfied by a **genuine Read** of `references/ledger-and-dispositions.md` (verified: a
  Read tool call on the file path, NOT a subagent-prompt name-mention — the #415 matcher
  nuance does not apply here).
- **`proof-rules.md` was NOT opened at all** (grep=0 across the stream) — stronger than the
  prior capture (which opened it incidentally). Its content is fully inlined, so a
  representative run does not need it: retiring it from the floor is unambiguously correct.
- Coverage 1/2 DEPTH (adapter-contract.md unopened — it is script-resolved via
  resolve_adapter.py, expected; not a floor). proof-rules.md (DUP) is excluded from the ratio.

## Follow-up (not required for this MOVE)

hotl/ledger-and-dispositions.md is MIXED: its INLINE tokens (the dotted
`verified_against.source_commit/.proof_artifact/.proving_surface_refs` forms + the
Operator-Decision-Queue 5-field template) could be inlined into SKILL.md as a compaction
nicety. The doc-open floor STAYS regardless (the anti-proxy DEPTH justifies it), so this is
deferred — no floor depends on it.
