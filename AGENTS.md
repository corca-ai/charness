# Charness - Corca Harness

`charness` is a Claude Code / Codex plugin developed by
[Corca](https://github.com/corca-ai), with agent skills, scripts, and a CLI packaged
as one harness.

## Guiding Principles

These expand in [README.md § Core Concepts](./README.md#core-concepts):

1. **Less Is More** — strong defaults over menus; progressive disclosure.
2. **Agents Are First-Class Users** — CLIs, scripts, artifacts, docs are agent-facing.
3. **Reveal Intent, Hide Detail** — public surface names intent; tool detail sits underneath.
4. **Human-Code-AI Symbiosis** — humans judge, code verifies, AI drafts.
5. **Long-Running Agents Need Quality Software** — quality as trust surface.
6. **Tacit Knowledge Becomes Workflow** — expert moves become reusable skills.
7. **The System Should Get Smarter With Use** — retros and adapters learn.
8. **Context Must Keep Flowing** — handoff/review/release/narrative as core work.

## Operating Stance

- ALWAYS CALL `CHARNESS:FIND-SKILLS` ONCE AT THE START OF EACH TASK-ORIENTED SESSION.
  Use its capability inventory as the session's default map of public skills,
  support skills, synced support surfaces, and integrations before broader
  repo exploration.
- USE THE ACTUAL AVAILABLE SKILLS FOR THIS TURN.
  If a matching skill exists in the current session, load it before
  improvising.
- KEEP THE HARNESS PORTABLE.
  Host-specific behavior belongs in adapters, presets, and integration
  manifests, not in public skill bodies.
- TREAT `SUBAGENT DELEGATION` AS AN EXPLICIT USER DELEGATION REQUEST.
  When a skill body requires a bounded reviewer, spawn it after initial
  inventory instead of asking for another user message.
- PREFER VALIDATORS AND SCRIPTS OVER PROSE RITUALS.
  If a repeated check matters, turn it into a repo-owned script.
- LEAVE AGENT-READABLE STATE.
  If a tool cannot finish the job end-to-end, persist structured breadcrumbs so
  the next agent can continue without rediscovering machine state.
- ROUTE EVALUATOR-BACKED VALIDATION THROUGH `quality` FIRST.
  Non-deterministic issue closeout and operator-reading test wording go
  through `quality` before `hitl` or same-agent manual review; the startup
  `find-skills` bootstrap still runs.

## References

You must read relevant references before starting.

- [`docs/handoff.md`](./docs/handoff.md): next-session pickup and volatile repo state
- [`charness-artifacts/retro/recent-lessons.md`](./charness-artifacts/retro/recent-lessons.md): compact recap of recent retrospective lessons and repeat traps
- [`docs/operator-acceptance.md`](./docs/operator-acceptance.md): operator-facing takeover checklist for the
  remaining roadmap items
- [`docs/control-plane.md`](./docs/control-plane.md): external integration contract
- [`charness-artifacts/quality/latest.md`](./charness-artifacts/quality/latest.md): current dogfood quality findings and next
  gates

## Non-Derivable Conventions

### Commit Discipline

- After each meaningful unit of work, create a git commit before moving on.
- Prefer commit subjects that state user-facing purpose, not only mechanism.
- After any `git push`, confirm the branch is clean and the remote update
  succeeded.
- When a Charness workflow creates or updates durable artifacts under
  `charness-artifacts/`, include the meaningful artifact changes in the same
  commit as the work they support.

### Skill and Metadata Discipline

- Treat `skills/public/<skill-id>/SKILL.md` as the trigger contract and decision
  skeleton; keep long rationale, examples, schemas, and edge cases in
  `references/`.
- Sparse real-person anchors in `SKILL.md` core are an intentional retrieval
  technique when they improve reasoning; keep them factual, behavior-linked,
  and supported by `references/`.
- Keep frontmatter YAML-safe. Quote descriptions when punctuation would make
  plain scalars fragile.

### Validation Discipline

- Repo-owned diff obligations live in [`.agents/surfaces.json`](./.agents/surfaces.json); use
  `python3 scripts/check_changed_surfaces.py --repo-root .` to inspect them and
  `python3 scripts/run_slice_closeout.py --repo-root .` before commit when the
  slice spans generated surfaces or multiple validator families.
- `python3 scripts/sync_support.py --json` and `python3 scripts/update_tools.py --json`
  are dry-run sanity checks. Use `python3 scripts/doctor.py --json` only when you
  intentionally want real machine-state diagnostics.

### Change Discipline

- Prefer deleting drift over documenting drift. Current-pointer helpers
  should be no-op when their canonical content has not changed; if a startup
  or inventory command rewrites an artifact without a canonical change,
  treat that as invocation drift or a helper bug to fix.
- Treat `mutate -> sync -> verify -> publish` as hard phase barriers. After
  a command rewrites generated surfaces, plugin exports, versioned manifests,
  or git state, finish that phase before starting validators or publish
  steps. Use parallel tool calls only for read-only inventory or file
  inspection; never run sync/export/bump/install/update/git-mutation commands
  in parallel with validators, closeout, or publish steps.
- When a repo-local structural fix can also improve the installed charness
  user surface, inspect whether a public skill, reference, packaging
  contract, or this document should absorb the lesson before stopping.
- If a public skill needs repeated bootstrap, adapter resolution, artifact
  naming, or recovery behavior, ship a helper script instead of leaving it
  as prose-only guidance.
- When tool install, update, or support-sync work is partly manual or
  mutates the operator surface, emit structured output and persist
  machine-readable state so a later agent can continue without rediscovering
  the machine.

### Skill Dogfood Discipline

- Loaded SKILLs come from `~/.agents/src/charness/`, a separate clone from
  this working tree. Editing `skills/public/<id>/SKILL.md` does **not** reach
  the next Claude/Codex session in this repo until the install path picks it
  up.
- Keep detailed dogfood procedures in [docs/development.md](./docs/development.md)
  (proof-only repo-local refresh and managed-checkout CLI refresh paths),
  not here.
- After a release/dogfood cycle, `charness update` (no flags) restores the
  managed-checkout flow.

### Session Discipline

- Update [`docs/handoff.md`](./docs/handoff.md) when the next session's first move changed.
- If the user correctly points out a missed issue, broken assumption, or
  missing gate that should likely have been caught, run a brief retro before
  continuing and say whether that retro was persisted.
