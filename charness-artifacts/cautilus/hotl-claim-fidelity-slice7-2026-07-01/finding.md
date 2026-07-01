# hotl claim-fidelity capture — 2026-07-01 (reference-compaction Slice 7)

## Verdict

**FLOOR PROVEN (HYPOTHESIS→PROVEN); Move C does NOT apply — keep the RCF floor.**
The first live hotl capture scores **outcome=passed, coverage 2/3** and OPENS BOTH
RCF docs (`proof-rules.md` + `ledger-and-dispositions.md`; only the script-resolved
`adapter-contract.md` is unopened). The doc-opens are load-bearing, so #410's
RCF→RSF move does NOT apply — unlike gather (which opened zero docs) and unlike
create-cli (whose dropped enum was fully inlined in core).

## What ran

`/charness:hotl` proving a real repo guard (the pre-commit block on `#NNN` issue
anchors in portable skill edits) evidence-first: write a proof packet → classify
the acceptance class → record an explicit ledger disposition. Capture at
`HEAD`=8700f526, exit **0**, 253485ms, 2.27M tokens, tool profile Bash=14 Read=6
Write=3 Skill=1. The run authored the proof packet, ran the guard against a
disposable input, classified it `local-only`, and recorded a ledger status —
opening `proof-rules.md` (for the proof-level ladder) and `ledger-and-dispositions.md`
(for the field semantics + anti-proxy rule) to do so.

## Why Move C does not apply (keep the floor)

hotl's SKILL.md previews the six proof rules (`## Proof Rules`) and the ledger
Output-Shape fields, but the capture shows a representative run STILL opens both
docs — because their unique authority is NOT in the preview: `proof-rules.md`
owns the proof-LEVEL ladder (surface/worker_queued/host_decision/provider_roundtrip/agent_choice),
and `ledger-and-dispositions.md` owns the `verified_against.*` field semantics,
the staleness model, and the completion-audit anti-proxy rule. That is judgment
authority, not an emittable enum reducible to a `## Closeout Vocabulary` token
(the impl/create-cli pattern). And hotl has **no substance judge**
(`outcome-assertions.json` absent), so moving to an emitted-token FORM floor would
let a run echo a ledger token from the preview without the anti-proxy discipline —
over-relaxation. The RCF doc-open floor is the honest instrument; it is KEPT.

## The assumed tokens were NOT emitted (S5 don't-assume lesson, again)

#410 assumed the run emits `verified_against` / `disposition` field tokens. It
emitted NEITHER literally (0×). It emitted `proving_surface` (2×, from
`verified_against.proving_surface_refs`), `source_commit` (1×), `local-only` (4×),
`acceptance class` (1×), `Ledger Status`, `Proof Packet`. Had this been a
mechanical RSF pin, the assumed token would have shipped a false floor — exactly
why capture-before-pin is load-bearing.

## Change landed

No RCF/RSF move (correctly). The spec `_comment` records the PROVEN status + the
Move-C-N/A finding, and `thresholds.max_duration_ms=510000` is set from this first
PASSING baseline (253485ms) at ~2x headroom (advisory degrade). hotl moves off the
HYPOTHESIS-floor list (correctness-sweep item #2).
