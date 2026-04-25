# Spec: AGENTS.md craken refactor + docs reorganization

## Problem

`AGENTS.md` (currently 130 lines after the hitl review on 2026-04-25) is
an inline policy document. For external readers and agents on entry: the
policy is co-located but the document is not a craken-style map-first entry.
`docs/` (20 files, ~3,500 lines) is a contract/reference surface but is
flat — no categories. Some docs look stale (`support-tool-followup` 386L,
`retro-self-improvement-spec` 286L, `deferred-decisions` 168L,
`gather-provider-ownership` 121L). The boundary between AGENTS.md and
`docs/` for *where a policy lives* is blurry.

Goal: AGENTS.md becomes "policies that are immediately actionable in every
session + a link index". `docs/` becomes a craken-categorized contract
surface.

## Current Slice

One implementation session does all of:

1. `docs/` inventory + per-file fate decision (with user)
2. craken-style categorization
3. Move inline AGENTS.md policy sub-sections into separate `docs/conventions/`
   files
4. Clean up stale docs (merge / delete / move)
5. Rewrite AGENTS.md (link-index, ~50 lines)
6. plugin export sync + validators pass

## Fixed Decisions

- AGENTS.md shape: craken-style link-index. Inline iff:
  - (a) the rule is referenced on every session start, AND
  - (b) the rule is ≤ 3 lines, AND
  - (c) no link suffices.
  All other policies move to `docs/conventions/`.
- Policy split destination is `docs/conventions/`. File names (e.g.
  `commits.md`, `skills-metadata.md`, `validation.md`, `changes.md`,
  `session.md`) are the only open Q3 question — confirmed in round 1
  review.
- AGENTS.md length target: ~50 lines, hard ceiling ≤ 60 lines, AND the
  measurable shape constraint below in Acceptance Checks.
- Stale criterion: (a) last meaningful change ≥ 6 months ago AND (b) zero
  references from any skill / script / test AND (c) explicit user
  agreement that it is stale. **If (c) cannot be obtained in-session for
  a candidate, the default action is *keep*. Success Criterion #2's
  "≥ 3 stale removed" becomes best-effort, not blocking.**
- Host-specific entry files (CLAUDE.md, GEMINI.md, `.codex`-rooted entry,
  etc.) must either link to AGENTS.md as canonical or be linked from
  AGENTS.md's References section. The decision must be resolved before
  the AGENTS.md rewrite step.
- Canonical artifact: this file (`charness-artifacts/spec/agents-md-craken-refactor.md`).
- No conflict with the already-committed portability link sweep (commit
  38a3ae6).

## Probe Questions (resolved during implementation, with user)

1. Per-file fate of all 20 docs — keep / move / merge / delete. The four
   stale-suspect files first.
2. Category names — Manual / Design / Coding / Operations / Debugging,
   or charness-specific (e.g. Surface contracts / Skill policy / Operator
   surfaces / Architecture / Memory).
3. Exact file names under `docs/conventions/` (the destination directory
   is fixed; only naming is open).
4. References vs Further Reading split — one section or two; how to
   place volatile (handoff, recent-lessons, quality/latest) vs stable
   contract docs.

## Deferred Decisions

- `charness-artifacts/spec/` cleanup of 14 stale-suspect spec records.
- Issue #74 (migrate script + check_doc_links portable awareness).
- Issues #72 (hitl Apply Phase) and #73 (broken inline-code refs).
- README ↔ AGENTS.md persona separation (external reader vs agent) —
  partial here, full narrative pass later.

## Non-Goals

- Changing charness policy itself. This spec only relocates.
- Adding or changing skills.
- Adding new policy.

## Deliberately Not Doing

- Cutting AGENTS.md below 50 lines if policy density justifies more.
- Moving every charness-only policy into `docs/`. The compact Start Here,
  Subagent Delegation, and Phase Rules bullets stay inline (craken intent).
- Pure mechanical sed/grep migration. Every policy split goes through
  user review.

## Constraints

- All links valid for downstream charness plugin consumers.
- pre-push plugin export drift check passes.
- `check_doc_links`, `check-markdown`, `validate_skills` all green.
- No conflict with the portability sweep already on `main`.

## Success Criteria

1. `wc -l AGENTS.md` ≤ 60.
2. `docs/` net file count does not grow by more than +2 vs current 20.
3. AGENTS.md References / Further Reading uses craken categories.
4. SSOT for every relocated policy lives in `docs/conventions/*` only;
   AGENTS.md only links.
5. `./scripts/run-quality.sh` passes.
6. External reader can land on AGENTS.md and reach docs/ depth naturally.
7. One implementation session, including 1–2 user review rounds.

## Acceptance Checks

1. `wc -l AGENTS.md` ≤ 60.
2. `python3 scripts/check_doc_links.py --repo-root .` exit 0.
3. `./scripts/run-quality.sh` exit 0.
4. Every docs link in AGENTS.md resolves to an existing file (link
   checker).
5. AGENTS.md non-link, non-heading prose lines ≤ 20 — count lines that
   are not headings, not blank, and do not contain a markdown link.
6. User manual review: read AGENTS.md as an external reader, confirm
   entry friendliness.

## Premortem

Fresh-eye subagent review on the spec contract surfaced six patches
(stale-criterion default, Success #2 arithmetic, "immediately actionable"
inline rule, Probe Q3 destination as Fixed not Probe, Acceptance #5
measurability, host-specific entry sequencing). All six were applied to
this artifact before saving. The spec is ready for implementation.

## Canonical Artifact

`charness-artifacts/spec/agents-md-craken-refactor.md` (this file).

## First Implementation Slice

1. `docs/` inventory + per-file fate decision via the hitl skill, round
   1.
2. Resolve host-specific entry doc question (CLAUDE.md / GEMINI.md /
   `.codex` entries).
3. Move inline AGENTS.md policies to `docs/conventions/`.
4. Rewrite AGENTS.md (link-index, ~50 lines).
5. plugin export sync.
6. validators pass.
7. Update this spec artifact with implementation findings.
8. commit + push.

## Implementation Findings

- 2026-04-25 implementation kept every existing `docs/*.md` file. The stale
  candidates named above were all changed in April 2026, and the fixed stale
  criterion requires explicit user agreement before deletion.
- `AGENTS.md` was rewritten to 37 lines with 9 non-link, non-heading prose
  lines, so Acceptance Checks #1 and #5 are satisfied before full closeout.
- Inline AGENTS policy moved into two convention files:
  [docs/conventions/operating-contract.md](../../docs/conventions/operating-contract.md)
  and
  [docs/conventions/implementation-discipline.md](../../docs/conventions/implementation-discipline.md).
- Host-specific entry resolution used the deterministic `init-repo` case:
  [CLAUDE.md](../../CLAUDE.md) is now a symlink to [AGENTS.md](../../AGENTS.md).
- The surface manifest now treats `CLAUDE.md` as a repo markdown and
  prompt-behavior source path so future alias changes carry the same closeout
  obligations as `AGENTS.md`.
- `evals/cautilus/instruction-surface-cases.json` compact synthetic AGENTS
  surfaces now use the new Start Here / Subagent Delegation / Phase Rules shape
  instead of the retired Operating Stance / Skill Routing shape. This is the
  scenario-design change to exercise during final Cautilus proof.
- Round-1 HITL inventory and conservative fate decisions are recorded in
  [charness-artifacts/hitl/2026-04-25-agents-md-craken-refactor.md](../hitl/2026-04-25-agents-md-craken-refactor.md).
