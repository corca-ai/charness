# Debug essence/deletion redesign — critique

Date: 2026-06-21

## Decision Under Review

Apply the `impl`-exemplar essence/deletion recipe to `skills/public/debug/SKILL.md`
(the "safe" first target of the operator-agreed essence rollout — no pin deletion,
unpinned duplication only). Two deletions:

1. The "bug-class `issue resolve` invokes the same substrate through
   `../issue/references/causal-review.md` Lens N" cross-reference appeared 4×
   (intro + five-whys step + detection-gap step + sibling-search step). Now
   stated ONCE in the intro, reworded so causal-review.md's lenses map onto the
   debug steps (each step states its substrate once, not per lens). The 3
   in-workflow repetitions deleted.
2. The Bootstrap "Treat the scaffold helper as the canonical artifact contract
   shortcut:" + 5 bullets (restating what `scaffold_debug_artifact.py`'s JSON
   already emits) folded into one sentence pointing at the helper's JSON,
   preserving the one unique fact (consumer repos do not copy validator scripts).

193 → 185 lines. `debug` carries NO `check_skill_contracts.py` CORE/PACKAGE rows;
only `tests/quality_gates/test_debug_rca_reference_cite_chain.py` +
`tests/test_debug_scaffold.py` pin it — and every pinned phrase stays at a
canonical home, so zero gate/test edits.

## Failure Angles

- **Orphaned rule:** a deleted per-step "Lens N" annotation or helper bullet
  carries a load-bearing fact with no surviving home (intro, surviving steps,
  `causal-review.md` lens ownership, or the helper's JSON output).
- **Lost navigation:** a reader in the detection-gap step genuinely needed the
  inline "= Lens 2" pointer to cross into `issue resolve` correctly.
- **Pin wrap-split:** a preserved pinned phrase (e.g. `proof level separately
  from the decision`) wraps across a markdown line break and silently fails its
  `in`-substring test.
- **Less but worse:** the bullet→sentence fold reads denser, not clearer.

## Counterweight Pass

One bounded fresh-eye reviewer (read-only, shared parent worktree, `git show
HEAD:<path>` for prior versions) was tasked to REFUTE lossless distillation. It
mapped each of the 5 deleted helper bullets to a live
`scaffold_debug_artifact.py --json` field (it ran the helper) and/or the folded
sentence, and traced the lens↔substrate correspondence to its canonical owner:
`causal-review.md` Lens 1/2/3 cite `five-whys-causal-chain.md` /
`detection-gap.md` / `sibling-search.md` — the exact references each surviving
debug step still cites, so a reader crossing into `issue resolve` lands on the
same substrate without the inline lens number. Verdict: `ESSENCE-PRESERVED`. It
confirmed all 13 test-pinned phrases present on unbroken lines (21 passed) and
judged the fold "less dense to read, not more."

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: over-worry | evidence: strong | ref: skills/public/debug/SKILL.md:13 | action: document | note: the per-step "Lens N" *numbers* are the only fact the single intro line does not enumerate. The reviewer attempted this as the orphan and it fails: the lens→step mapping is bidirectionally recoverable from `causal-review.md` (its lenses cite the same `five-whys`/`detection-gap`/`sibling-search` references each debug step cites). The relationship is owned canonically by the issue side, not the debug workflow — restating it per step was the duplication. Left deleted.
- F2 | bin: valid-but-defer | evidence: strong | ref: skills/public/quality/SKILL.md | action: defer | note: next target is `quality` as the operator-agreed PIN-OPENING pilot (191-line body, 49 refs — the anchor-split only relocated). Unlike `debug` (no contract rows), `quality` deletion crosses into pinned contracts + their tests, so it needs the disciplined pin-deletion test and is the consequential checkpoint, deferred to a deliberate step. Recorded in Deliberately Not Doing.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: standard (one bounded reviewer; unpinned-duplication-only deletion, reversible, no pin/contract removal).
- Requested spawn fields: model=default (Claude Code host resolution; no override for a single bounded reviewer on a no-pin-deletion essence pass).
- Host exposure state: requested_fields_sent
- Application state: 1 bounded reviewer spawned via the Agent tool in the shared parent worktree, read-only (`git show HEAD:<path>` for prior versions, no index/worktree-mutating git ops); the host does not echo resolved spawn fields, so application is unverified-by-carrier (not claimed host-confirmed).

## Fresh-Eye Satisfaction

parent-delegated. The bounded reviewer returned `ESSENCE-PRESERVED` with a
per-deletion ledger: a 5-bullet→JSON-field table proving each helper bullet is
homed, and a lens↔substrate correspondence trace proving the cross-reference is
owned by `causal-review.md`. It verified all 13 pins on unbroken lines and
flagged one accuracy nit (HEAD is 193 not 194 lines — corrected in the dogfood
entry). Deterministic backstop: debug pin tests 21 passed; verification-lock
closeout exit 0 (packaging, doc-links, markdown, secrets, cautilus-proof,
validate_skills, ergonomics, public-skill validation + dogfood, mirror-drift all
PASS; broad pytest proof reused — markdown/json-only change, production-Python
fingerprint unchanged); cautilus planner `next_action: none` (Cautilus correctly
NOT run; scenario review recorded in the dogfood ledger).

## Deliberately Not Doing

- **Keep the per-step "Lens N" annotations (F1).** The lens↔step mapping is owned
  by `causal-review.md` and recoverable through the shared reference citations
  that survive in each step; restating it per debug step was the duplication this
  pass removes. Left deleted; flagged for maintainer eyeball.
- **Roll into `quality` this pass (F2).** `quality` is the pin-opening pilot —
  deletion crosses pinned contracts + tests and needs the disciplined
  pin-deletion test, making it the consequential operator checkpoint, not a
  bundled follow-on. Deferred to a deliberate step.
- **Mutate `evals/cautilus/scenarios.json`.** The deleted prose was duplicate
  cross-references and a helper-output restatement, not workflow behavior;
  maintained scenario coverage is unaffected. Ask-before-mutate honored.
