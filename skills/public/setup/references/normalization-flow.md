# Normalization Flow

This reference covers the normalization moves for repos whose operating docs are
incomplete, duplicated, or inconsistent.

## Goal

Prefer rewriting and consolidating existing truth surfaces over dropping fresh
parallel templates.

## Checks

- is `<repo-root>/README.md` current and minimally honest
- does the consumer-owned documentation index at `<repo-root>/docs/index.md` <!-- not vendored: consumer-repo path --> provide one
  flat-wiki entry point, with each
  page listed once and no unapproved document moves
- if the repo ships an installable surface, do `<repo-root>/README.md` and the repo-local bootstrap guidance
  name probe semantics without collapsing health, readiness, and
  discoverability into one command
- if the repo wants durable retrospective pickup, is there one stable retro
  memory seam instead of scattered ad hoc notes
- do `<repo-root>/AGENTS.md` and `CLAUDE.md` express one clear host-facing contract
- when a material boundary needs an independent observer, does the owning skill
  record the decision and any unavailable-observer non-claim without requiring
  every consumer repo to carry the same root policy
- does `<repo-root>/docs/roadmap.md` exist when active ordered planning is evidenced
- can a human operator tell what to do from `<repo-root>/docs/operator-acceptance.md`
  when the repo actually has an install/deployment/takeover path
- does the quality skill's read-only bootstrap identify the same language,
  commands, hook scope, and ratchet surfaces that setup proposes
- is any hook proposal fast and staged/related-file scoped, with whole-repo work
  reserved for pre-push/CI
- are there duplicate docs that should collapse into one source of truth

## Decision Rule

- missing core profile surface: propose it, then wait for explicit user approval
- missing conditional surface: scaffold it only when its evidence trigger is present
- one missing core surface in an otherwise mature repo: do the smallest
  targeted repair and keep the rest of the operating docs intact
- stale but useful surface: rewrite it
- duplicate surface: collapse it into the more honest source of truth

Task-completing normalization should verify the changed operating surface with
the narrowest relevant checks. An independent review is selected by the owning
skill when the boundary, deletion, or uncertainty warrants it; setup does not
make that review or changed-line proof universal.

The plan is a write boundary: the inspector is read-only and emits an
`approval_plan.identity`; approval must name that digest and a pre-apply
inspection must verify it. A changed plan requires a new approval. A detected
binary or a passing quality command is not approval. Quality owns the final
adapter, gate, and ratchet verdicts.

If the repo already has a strong durable story and the main problem is alignment
across multiple docs, prefer `narrative` as the next deeper skill.
