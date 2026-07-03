# ideation H0 — format-rule micro-lever check: ABSENT (static, no capture) (2026-07-03)

Serves [intent.md](./intent.md): north = SMARTER agent; test = "그게 정말 최선인가?"
Rank-1 pickup: does ideation's non-ceiling validator (`## Structured Questions`
enums) produce a format-rule micro-lever like retro's `Persisted` case? **Verdict:
NO — churn ABSENT.** Static check is conclusive; no capture spent (justified at the
end — spending it would be the over-build the intent warns against).

## Static check (the locked heuristic, both conditions)

Churn PRESENT ⇐ (a) hand-edits its artifact via `Edit`, no persist helper AND (b)
the run must iterate to satisfy an **invisible** validator-format rule.

- **(a) TRUE** — `scaffold_ideation_artifact.py` is scaffold-only: it emits a TODO
  skeleton through `_scaffold_lib.emit_payload_main` and never writes/stamps the
  file. Like every skill except retro (anti-churn-patterns pattern 1).
- **(b) FALSE** — ideation's ONLY validator rule (`validate_ideation_artifact.py`,
  the `urgency`/`action` enums under `## Structured Questions`) is **surfaced, not
  invisible**: the scaffold's `STRUCTURED_QUESTIONS` constant emits a valid block
  inline and, per its own comment, "Mirrors the enums ... so the block validates
  unedited." The rule is also opt-in + section-gated (prose-only output passes).
  No `MAX_*_LINES`, no `size_budget` anywhere (grep clean).

(b) fails → **churn ABSENT.** ideation is pattern 2 ("surface the gate's expectation
up front") ALREADY applied — its format rule is the surfaced case, not the invisible
one debug/quality had to fix.

## Why ideation structurally cannot have retro's `Persisted` micro-lever

retro's micro-lever = the tool COMPUTED a value (the durable path) but wrote a
PLACEHOLDER, forcing the run to re-type a known value (fix: stamp it). ideation has
**no such value**: it ships no persist helper, and the validator checks only content
the tool CANNOT compute — which enum fits a real question, and the note text, both
irreducible agent judgment. The scaffold already supplies the maximum a tool can (the
format, valid out of the box); nothing is left to stamp. The residual edits (fill the
notes, pick the enum, or delete the section for a prose-only run) are authoring or
opt-out, not churn.

## Heuristic refinement (leverage for the rest of the sweep)

A non-ceiling format rule churns ONLY when EITHER the format is **invisible** (the run
write-then-fixes: debug/quality) OR a **tool-computable value is hidden** behind a
placeholder (retro's `Persisted`). When the format is surfaced AND the residual content
is irreducible judgment the tool can't supply (ideation), there is nothing left to
surface or stamp → **no churn**. Static-check the value-hidden case specifically, not
"has a format rule" in the abstract.

## Considered and rejected (do not manufacture a fix)

- **Force-emitted opt-in section:** the scaffold always emits `## Structured
  Questions`, so a prose-only run deletes it (≤1 edit). Pedagogical-vs-ergonomic
  tradeoff (the block demos a valid form + exercises the validator out of the box),
  not a churn lever.
- **Partial enum surfacing** (fresh-eye's strongest angle, still sub-threshold): the
  demo block shows 2 of 3 `urgency` and 2 of 3 `action` enums — `defer`/`hold` live
  only in `references/structured-questions.md` (routed at SKILL.md:155-156). A run
  wanting a `defer`/`hold` item that skips the reference could guess-then-fix once.
  This is authoring judgment against a surfaced, documented schema, not a
  tool-computable value and not the retro `Persisted` shape; at most a rare single
  edit. **Optional nicety** (add the two remaining enums to the demo block), NOT a
  churn defect — recorded for the operator, deliberately not shipped as marginal
  over-build.

A "fix" for either would fail the one test.

## Fresh-eye

Bounded adversarial reviewer (tasked to REFUTE): **VERDICT SOUND** — could not refute
churn-ABSENT / no-capture on any of five angles; confirmed "validates unedited" and
"no `size_budget`/ceiling" empirically (ran the scaffold template through the
validator; `emit_payload_main` never reaches `current_pointer_payload` where
`size_budget` lives). Its one surviving angle (partial enum surfacing) is folded in
above as a sub-threshold nicety, not a defect. No wording fixes required.

## Why no capture (turning "allow cautilus" into a justified no-op)

The locked method captures only heuristic HITS; ideation is a predicted non-hit. A
capture cannot resolve a decision-relevant uncertainty here — both branches (keep or
delete the section) yield no churn — so it would spend ~20k tokens / ~6 min to
re-confirm what the structure already proves. That is the overhead disease the intent
is curing. The claim-fidelity RCF context corroborates the shape: ideation's only
engage-always floor is `concept-architecture.md` (load-bearing living-model
discipline, DEPTH), not the format rule — nothing churn-shaped is on the critical path.
