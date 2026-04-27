# Operating Contract

This document owns Charness repo conventions that do not need to be repeated in
the root instruction file. [AGENTS.md](../../AGENTS.md) stays as the session
entry and link index.

## Guiding Principles

These expand in [README.md Core Concepts](../../README.md#core-concepts):

1. Less Is More: strong defaults over menus; progressive disclosure.
2. Agents Are First-Class Users: CLIs, scripts, artifacts, docs are agent-facing.
3. Reveal Intent, Hide Detail: public surface names intent; tool detail sits underneath.
4. Human-Code-AI Symbiosis: humans judge, code verifies, AI drafts.
5. Long-Running Agents Need Quality Software: quality as trust surface.
6. Tacit Knowledge Becomes Workflow: expert moves become reusable skills.
7. The System Should Get Smarter With Use: retros and adapters learn.
8. Context Must Keep Flowing: handoff, review, release, and narrative are core work.

## Commit Discipline

- After each meaningful unit of work, create a git commit before moving on.
- Do not leave task-completing repo work in a dirty tree unless the user
  explicitly asked to pause before commit or an unresolved blocker is named.
- Prefer commit subjects that state user-facing purpose, not only mechanism.
- After any `git push`, confirm the branch is clean and the remote update succeeded.
- When a Charness workflow creates or updates durable artifacts under
  [charness-artifacts/](../../charness-artifacts/), include meaningful artifact
  changes in the same commit as the work they support.

## Premortem Discipline

- Every task-completing repo change runs premortem before closeout. Scale the
  pass, not the obligation.
- Small local-risk slices may use a short scoped premortem artifact that names
  the decision, the likely misread, counterweight triage, and the next move.
- Non-trivial design, deletion, rename, release, workflow, compatibility,
  install/update, host-proof, prompt-surface, public-skill, validator, or export
  decisions use the standalone `premortem` skill.
- `Premortem: not-applicable <reason>` is reserved for inspect-only, status-only,
  or routing-only requests that do not complete repo work.
- If the required bounded-review path is blocked by the host, stop and record
  `Premortem: blocked <host-signal>` instead of substituting same-agent review.

## Skill And Metadata Discipline

- Treat `skills/public/<skill-id>/SKILL.md` as the trigger contract and
  decision skeleton; keep long rationale, examples, schemas, and edge cases in
  `references/`.
- Sparse real-person anchors in `SKILL.md` core are intentional retrieval aids
  when they improve reasoning; keep them factual, behavior-linked, and
  supported by `references/`.
- Keep frontmatter YAML-safe. Quote descriptions when punctuation would make
  plain scalars fragile.

## Dogfood Discipline

- Loaded skills may come from a host-managed checkout or plugin cache rather
  than this working tree. For Claude managed-checkout dogfood, that path is
  usually `~/.agents/src/charness/`.
- Editing `skills/public/<id>/SKILL.md` does not reach the next Claude/Codex
  session in this repo until the relevant install or update path picks it up.
- Keep detailed dogfood procedures in [docs/development.md](../development.md),
  not in AGENTS.md.
- After a release or dogfood cycle, `charness update` with no flags restores
  the managed-checkout flow.

## Session Discipline

- Update [docs/handoff.md](../handoff.md) when the next session's first move changed.
- If the user correctly points out a missed issue, broken assumption, or
  missing gate that should likely have been caught, run a brief retro before
  continuing and say whether that retro was persisted.
