# charness

Portable Corca harness layer for skills, profiles, integrations, and
self-validation.

## Operating Stance

- USE THE ACTUAL AVAILABLE SKILLS FOR THIS TURN.
  If a matching skill exists in the current session, load it before
  improvising.
- KEEP THE HARNESS PORTABLE.
  Host-specific behavior belongs in adapters, presets, and integration
  manifests, not in public skill bodies.
- PREFER VALIDATORS AND SCRIPTS OVER PROSE RITUALS.
  If a repeated check matters, turn it into a repo-owned script.
- LEAVE AGENT-READABLE STATE AFTER PARTIAL AUTOMATION.
  If a tool cannot finish the job end-to-end, persist structured breadcrumbs so
  the next agent can continue without rediscovering machine state.
- LEAVE AGENT-READABLE STATE.
  Install, update, and support-sync flows should emit structured output and
  persist machine-readable state when they mutate the operator surface.
- KEEP MANUALLY MAINTAINED REPO DOCS IN ENGLISH.
  `docs/handoff.md` may stay Korean when that makes the next session pickup
  sharper.
- SPEAK TO THIS USER IN KOREAN UNLESS THEY ASK OTHERWISE.
  Conversation language and repo document language are separate policies.
- LESS IS MORE.
  Strong defaults and inference beat user-facing modes unless the distinction is
  genuinely meaningful and unsafe to infer.

## Repo Memory

- `docs/handoff.md`: next-session pickup and volatile repo state
- `skill-outputs/retro/recent-lessons.md`: compact recap of recent retrospective lessons and repeat traps
- `docs/roadmap.md`: optional roadmap when a repo explicitly chooses to keep one
- `docs/operator-acceptance.md`: operator-facing takeover checklist for the
  remaining roadmap items
- `docs/skill-migration-map.md`: migration intent and remaining destinations
- `docs/control-plane.md`: external integration contract
- `skill-outputs/quality/quality.md`: current dogfood quality findings and next
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

- Prefer `./scripts/run-quality.sh` as the canonical local quality entrypoint
  once the change touches multiple repo-owned quality surfaces.
- Repo-owned diff obligations live in `.agents/surfaces.json`; use
  `python3 scripts/check-changed-surfaces.py --repo-root .` to inspect them and
  `python3 scripts/run-slice-closeout.py --repo-root .` before commit when the
  slice spans generated surfaces or multiple validator families.
- Use `python3 scripts/run-evals.py` when changing validator contracts,
  adapter bootstrap behavior, or portable markdown-link assumptions.
- When editing skill packages, run `python3 scripts/validate-skills.py`.
- When editing profiles, run `python3 scripts/validate-profiles.py`.
- When editing adapter bootstrap or resolver behavior, run
  `python3 scripts/validate-adapters.py`.
- When editing integration manifests or control-plane scripts, run
  `python3 scripts/validate-integrations.py`.
- When editing committed markdown links or handoff references, run
  `python3 scripts/check-doc-links.py`.
- When markdown or secret-bearing text changes materially, run
  `./scripts/check-markdown.sh` and `./scripts/check-secrets.sh`.
- Use `./scripts/check-shell.sh` and `./scripts/check-links-external.sh` when
  `shellcheck` or `lychee` are available; these are honest optional escalations,
  not fake guarantees.
- Use `python3 scripts/check-duplicates.py` to surface helper-script duplicate
  hotspots before copying a pattern again.
- Keep `python3 -m py_compile skills/public/*/scripts/*.py` as the cheap smoke
  test for helper scripts.
- Keep `python3 scripts/sync_support.py --json` and
  `python3 scripts/update_tools.py --json` as dry-run sanity checks for the
  control plane. Use `python3 scripts/doctor.py --json` when you intentionally
  want real machine-state diagnostics.

### Change Discipline

- Prefer deleting drift over documenting drift.
- If the same helper shape appears twice, factor it before spreading it to a
  third place.
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
- To dogfood unpushed skill changes locally, run
  `charness update --repo-root . --no-pull --skip-cli-install` from this repo.
  The working tree (incl. uncommitted edits) becomes the plugin source, but the
  installed CLI still stays anchored to the managed checkout. Use this
  proof-only path when dogfooding local skill/plugin changes; restart the
  session to pick up the new SKILL.
- If you need to refresh the installed CLI itself, use the managed checkout
  path instead: `~/.agents/src/charness/charness update`.
- After a release/dogfood cycle, `charness update` (no flags) restores the
  managed-checkout flow.

### Session Discipline

- Update `docs/handoff.md` when the next session's first move changed.
- Keep durable review findings in `skill-outputs/` when a skill is designed to
  accumulate them.
- If the user correctly points out a missed issue, broken assumption, or
  missing gate that should likely have been caught, run a brief retro before
  continuing and say whether that retro was persisted.
