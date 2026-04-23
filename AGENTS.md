# charness

Portable Corca harness layer for skills, profiles, integrations, and
self-validation.

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
- TREAT REPO-MANDATED BOUNDED SUBAGENT REVIEWS AS ALREADY DELEGATED.
  When this repo or a required skill makes a bounded fresh-eye subagent review
  a stop gate, do not wait for a second user message asking for delegation.
- IF THE HOST BLOCKS SUBAGENT SPAWNING, STOP AND REPORT THE HOST RESTRICTION.
  Do not substitute a same-agent pass for the canonical bounded review.
- PREFER VALIDATORS AND SCRIPTS OVER PROSE RITUALS.
  If a repeated check matters, turn it into a repo-owned script.
- LEAVE AGENT-READABLE STATE.
  If a tool cannot finish the job end-to-end, persist structured breadcrumbs so
  the next agent can continue without rediscovering machine state. Install,
  update, and support-sync flows should emit structured output and persist
  machine-readable state when they mutate the operator surface.
- KEEP MANUALLY MAINTAINED REPO DOCS IN ENGLISH.
  [`docs/handoff.md`](./docs/handoff.md) may stay Korean when that makes the next session pickup
  sharper.
- SPEAK TO THIS USER IN KOREAN UNLESS THEY ASK OTHERWISE.
  Conversation language and repo document language are separate policies.
- LESS IS MORE.
  Strong defaults and inference beat user-facing modes unless the distinction is
  genuinely meaningful and unsafe to infer.

## Skill Routing

For task-oriented sessions in this repo, call the shared/public charness skill
`find-skills` once at startup before broader exploration.

Use its capability inventory as the session's default map of public skills,
support skills, synced support surfaces, and integrations.

After that bootstrap pass, choose the durable work skill that best matches the
request from the installed charness surface.

Evaluator-backed validation, non-deterministic issue closeout, and operator
reading test wording route through `quality` before `hitl` or same-agent manual
review.

Keep this block short. Detailed routing belongs in installed skill metadata and
`find-skills` output, not in a long checked-in catalog.

## Repo Memory

- [`docs/handoff.md`](./docs/handoff.md): next-session pickup and volatile repo state
- [`charness-artifacts/retro/recent-lessons.md`](./charness-artifacts/retro/recent-lessons.md): compact recap of recent retrospective lessons and repeat traps
- `docs/roadmap.md`: optional roadmap when a repo explicitly chooses to keep one
- [`docs/operator-acceptance.md`](./docs/operator-acceptance.md): operator-facing takeover checklist for the
  remaining roadmap items
- `docs/skill-migration-map.md`: migration intent and remaining destinations
- [`docs/control-plane.md`](./docs/control-plane.md): external integration contract
- [`charness-artifacts/quality/latest.md`](./charness-artifacts/quality/latest.md): current dogfood quality findings and next
  gates

Read the smallest memory surface that answers the current question.

## Non-Derivable Conventions

### Commit Discipline

- After each meaningful unit of work, create a git commit before moving on.
- Prefer commit subjects that state user-facing purpose, not only mechanism.
- After any `git push`, confirm the branch is clean and the remote update
  succeeded.

### Skill and Metadata Discipline

- Treat `skills/public/<skill-id>/SKILL.md` as the trigger contract and decision
  skeleton only.
- Sparse real-person anchors in `SKILL.md` core are an intentional retrieval
  technique when they improve reasoning; keep them factual, behavior-linked,
  and supported by `references/`.
- Keep long rationale, examples, schemas, and edge cases in `references/`.
- Keep frontmatter YAML-safe. Quote descriptions when punctuation would make
  plain scalars fragile.
- Do not leave a profile, preset, or integration reference pointing at a
  missing artifact.

### Validation Discipline

- Prefer [`./scripts/run-quality.sh`](./scripts/run-quality.sh) as the canonical local quality entrypoint
  once the change touches multiple repo-owned quality surfaces.
- Treat `mutate -> sync -> verify -> publish` as hard phase barriers. After a
  command rewrites generated surfaces, plugin exports, versioned manifests, or
  git state, finish that phase before starting validators or publish steps.
- Repo-owned diff obligations live in [`.agents/surfaces.json`](./.agents/surfaces.json); use
  `python3 scripts/check_changed_surfaces.py --repo-root .` to inspect them and
  `python3 scripts/run_slice_closeout.py --repo-root .` before commit when the
  slice spans generated surfaces or multiple validator families.
- Use `python3 scripts/run_evals.py` when changing validator contracts,
  adapter bootstrap behavior, or portable markdown-link assumptions.
- When editing skill packages, run `python3 scripts/validate_skills.py`.
- When editing profiles, run `python3 scripts/validate_profiles.py`.
- When editing adapter bootstrap or resolver behavior, run
  `python3 scripts/validate_adapters.py`.
- When editing integration manifests or control-plane scripts, run
  `python3 scripts/validate_integrations.py`.
- When editing committed markdown links or handoff references, run
  `python3 scripts/check_doc_links.py`.
- When markdown or secret-bearing text changes materially, run
  [`./scripts/check-markdown.sh`](./scripts/check-markdown.sh) and [`./scripts/check-secrets.sh`](./scripts/check-secrets.sh).
- Use [`./scripts/check-shell.sh`](./scripts/check-shell.sh) when `shellcheck` is available; this is an
  honest optional escalation, not a fake guarantee.
- [`./scripts/check-links-internal.sh`](./scripts/check-links-internal.sh) and [`./scripts/check-links-external.sh`](./scripts/check-links-external.sh)
  require `lychee` and will fail if it is missing. Internal link existence is
  always verified; external URLs are verified online only when
  `CHARNESS_LINK_CHECK_ONLINE=1`.
- Use `python3 scripts/check_duplicates.py` to surface helper-script duplicate
  hotspots before copying a pattern again.
- Keep `python3 -m py_compile skills/public/*/scripts/*.py` as the cheap smoke
  test for helper scripts.
- Keep `python3 scripts/sync_support.py --json` and
  `python3 scripts/update_tools.py --json` as dry-run sanity checks for the
  control plane. Use `python3 scripts/doctor.py --json` when you intentionally
  want real machine-state diagnostics.

### Change Discipline

- Prefer deleting drift over documenting drift.
- Use parallel tool calls only for read-only inventory or file inspection. Do
  not run sync/export/bump/install/update/git-mutation commands in parallel
  with validators, closeout, or publish steps.
- If the same helper shape appears twice, factor it before spreading it to a
  third place.
- When a repo-local structural fix can also improve the installed charness user
  surface, inspect whether a public skill, reference, packaging contract, or
  this [`AGENTS.md`](./AGENTS.md) should absorb the lesson before stopping.
- If a public skill needs repeated bootstrap, adapter resolution, artifact
  naming, or recovery behavior, ship a helper script instead of leaving it as
  prose-only guidance.
- When tool install or update work is partly manual, keep the remaining steps
  explicit in structured output and lock state so a later agent can continue
  without rediscovering the machine.

### Skill Dogfood Discipline

- Loaded SKILLs come from `~/.agents/src/charness/`, a separate clone from
  this working tree. Editing `skills/public/<id>/SKILL.md` does **not** reach
  the next Claude/Codex session in this repo until the install path picks it
  up.
- Keep detailed dogfood procedures in [docs/development.md](./docs/development.md),
  not here. Use that doc for proof-only repo-local refresh and managed-checkout
  CLI refresh paths.
- After a release/dogfood cycle, `charness update` (no flags) restores the
  managed-checkout flow.

### Session Discipline

- Update [`docs/handoff.md`](./docs/handoff.md) when the next session's first move changed.
- Keep durable review findings in `charness-artifacts/` when a skill is designed to
  accumulate them.
- If the mandatory startup `find-skills` call rewrites
  `charness-artifacts/find-skills/latest.*`, diff it immediately. Commit it
  only when the canonical capability inventory changed; otherwise treat the
  rewrite as invocation drift or a bug to fix, not as unrelated ambient dirt.
- If the user correctly points out a missed issue, broken assumption, or
  missing gate that should likely have been caught, run a brief retro before
  continuing and say whether that retro was persisted.
