# Gather: Evidence-Based Expert Panel Prompt

## Source

- URL: <https://github.com/itsbluetic/expert-panel-by-ebp/blob/main/%EC%A0%84%EB%AC%B8%EA%B0%80%EC%86%8C%ED%99%98.md>
- Repository: `itsbluetic/expert-panel-by-ebp`
- Source identity: Korean markdown prompt for `/전문가소환`, an evidence-based expert-panel workflow.
- Accessed: 2026-04-15 UTC

## Freshness

GitHub rendered the file as `189 lines (130 loc) · 7.5 KB` on `main` at access time.
No repository-local copy of the source was found before this gather artifact.

## Requested Facts

The source has useful structure for `charness`, but it should be treated as a
reference workflow, not a template to import wholesale.

Reusable ideas:

- Evidence map before expert judgment. The workflow identifies relevant
  disciplines, chooses primary evidence sources, and only then asks experts to
  interpret the evidence. This reinforces the current `charness` bias that
  named experts are optional retrieval anchors, not authority.
- Evidence strength tags on every claim. The `[Strong]`, `[Moderate]`,
  `[Emerging]`, `[Expert]`, and `[Contested]` taxonomy is more explicit than
  most current `charness` review outputs. A lighter version could improve
  `quality`, `premortem`, `retro`, and `hitl` findings when claims mix local
  evidence, general practice, and intuition.
- Myth warning as a first-class output. The source explicitly flags common
  beliefs that spread through authority without good evidence. This maps well to
  `quality` and `retro` when a repeated habit sounds plausible but is not
  backed by repo evidence.
- Implementation design after recommendation. Separating core practice from
  peripheral practice is a useful way to avoid cargo-culting another repo's
  workflow. This aligns with `charness` portability: preserve the invariant,
  adapt the adapter/runtime details.
- PBE loop after EBP. The source closes with a short practice-based experiment:
  minimum experiment, success/failure criteria, observation points, and
  iteration cadence. This is a good pattern for converting advice into a small
  falsifiable repo slice.

What not to copy:

- Six-expert panels are too heavy for most `charness` turns. The useful move is
  evidence discipline plus one or two divergent lenses, not a standing panel
  ritual.
- `--quick` weakens the strongest part of the workflow by skipping source
  mapping. For `charness`, quick mode should mean "use the smallest available
  evidence surface," not "skip evidence."
- Real-person voice imitation is not a portable skill requirement. The useful
  rule is to select a lens that changes the next action and keep source-faithful
  claims.

## Candidate Charness Adaptations

1. Add an optional evidence-strength field to review-style outputs where claims
   are currently mixed together, especially `quality`, `premortem`, and
   `retro`.
2. Add a "myth or authority-only belief" check to `quality` fresh-eye review
   when the repo is relying on a habit, second implementation, or conventional
   best practice without a gate.
3. Use `Core Practice` / `Peripheral Practice` framing in provenance and
   reference-implementation guidance when learning from another repo.
4. Add "minimum experiment + observation point + revisit cadence" to suggested
   next gates when the recommendation is not yet automatable.

## Open Gaps

- This gather pass reviewed one source file only. It did not audit the rest of
  `itsbluetic/expert-panel-by-ebp`.
- The source cites Kim Chang-joon and EBP as inspiration, but this pass did not
  independently verify those external references.
- Any `charness` behavior change should be made in the relevant skill/reference
  documents with validators updated as needed, not only by leaving this note.
