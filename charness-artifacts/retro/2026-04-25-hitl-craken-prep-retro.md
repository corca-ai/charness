# Session Retro: hitl review and craken prep

## Context

A multi-task session that ran a paragraph-level hitl review of `AGENTS.md`,
filed three follow-up GitHub issues (#72 hitl Apply Phase, #73 lint
inline-code references, #74 migrate script + check_doc_links portable
awareness), added a `.githooks/pre-commit` hook, swept 178+ broken
portability links across portable skill bodies, and saved a craken refactor
spec. Five user-flagged misses surfaced through the session — three of them
were the kind of mistake automated checks should be catching, not the user.

## Evidence Summary

- During AGENTS.md apply, Operating Stance bullet 4 still said "When the
  section below applies, spawn the bounded reviewer..." even though C3 had
  deleted the `## Subagent Delegation` section. The self-reference was
  caught only when the user spotted it alongside an unrelated `fresh-eye`
  example.
- 110+ markdown links inside portable skill bodies under `skills/public/`
  and `skills/support/` used charness-relative paths
  (`[label](../../../../path)`). They were valid inside this repo and
  invalid for any downstream charness plugin consumer. No quality or lint
  surface had caught the breakage. A subagent audit found the pattern only
  after the user explicitly asked for one.
- `scripts/migrate_backtick_file_refs.py` had previously converted
  backticked paths to markdown links repo-wide without distinguishing
  portable surfaces from charness-only surfaces. It produced the broken
  state above. `scripts/check_doc_links.py` then warns on the symmetric
  mistake (bare backticked paths) inside portable bodies, where the only
  valid form is a placeholder. Together the two tools push portable bodies
  toward whichever form is currently broken.
- The first portability fix used `~~~text` tilde fences to avoid a
  non-existent nested-fence collision. CommonMark allows it, but the
  variant is unfamiliar and reduced readability for no real benefit.
- Hook contract drift: the first round of HITL accepted-text writes tried
  to apply edits to `AGENTS.md` mid-loop. The HITL skill body's
  `require_explicit_apply: true` adapter contract did not say "the target
  file is touched only in the apply phase," so the agent inferred a
  scratchpad-and-apply pattern only after the user pointed it out.

## Waste

- **Apply blocked twice** for the same class of mistake (broken
  cross-reference after section deletion; placeholder vs link confusion).
  Each retry burned a pre-commit cycle plus user attention.
- **Re-running the lint after each fix** when a single sweep would have
  surfaced all path-shape findings at once. This was a hook-output
  discoverability gap, not a logic gap.
- **One incorrect commit shape** (db83ee7) had to be partially reverted by
  c38e06b on the same day; the bulk sweep then re-touched the same file in
  38a3ae6. Three commits where one would have sufficed if the portability
  policy had been recognized before any apply pass.

## Critical Decisions

- Portable skill body links must not point above `skills/`. Use
  placeholders like `<repo-root>/...` for charness-only paths inside
  backticks; reserve markdown links for targets that stay inside the skill
  family (same skill, sibling public skill, support skill).
- HITL workflow needs an explicit Apply Phase step. Filed as #72.
- `migrate_backtick_file_refs.py` and `check_doc_links.py` both need
  portable-surface awareness. Filed as #74.

## Expert Counterfactuals

- Atul Gawande-style checklist discipline would have caught the deleted
  section's outgoing references with a "did you sweep self-references after
  this delete" line item before the apply step.
- Jef Raskin-style discoverability would have surfaced the portable-vs-
  charness boundary as a visible attribute on the skill body, not as
  implicit knowledge inside the maintainer's head and the migrate script.

## Lessons

- After deleting or renaming a heading or anchor, sweep every
  cross-reference (including the section's own callers) before an apply
  pass.
- Before running a repo-wide markdown migrator, separate portable surfaces
  (`skills/public/`, `skills/support/`) from charness-only surfaces and
  apply distinct rules per surface.
- Keep the markdown fence as standard backticks unless a real nested-fence
  collision forces a variant. Do not introduce `~~~` for hypothetical
  collisions.
- When a hook flags one mistake, run the underlying validator end-to-end
  (e.g. `python3 scripts/check_doc_links.py --repo-root .`) instead of
  retrying commits one fix at a time.

## Persisted To

- `charness-artifacts/retro/recent-lessons.md` (this lesson set added to
  Repeat Traps and Next-Time Checklist).
- GitHub issues #72, #73, #74 — these track the underlying tool /
  validator gaps that allowed the session to drift in the first place.
- `charness-artifacts/spec/agents-md-craken-refactor.md` consumes the
  outcome (AGENTS.md is now ready for the craken-style refactor).
