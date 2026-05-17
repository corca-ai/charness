# Bootstrap Seams

Use this when `setup` detects optional Charness seams beyond the default repo
operating surfaces.

Rule: `setup` may seed local adapters, starter artifacts, or AGENTS.md policy
blocks. Runtime behavior stays with the owning skill, command, or integration.
Do not expand `setup` into `quality`, `retro`, `handoff`, or product runtime
work just because the seed path is convenient.

## Installable Surface Probe

When the repo ships an installable CLI, plugin, package, or agent-facing
integration, make the README or bootstrap doc name a small probe surface.

Use `probe-surface.md` for the details. The first probe should be cheap,
machine-readable when possible, and honest about whether it proves only binary
healthcheck, machine-readable command discovery, local discoverability, or a
real workflow.

## Durable Retro Memory

When the repo wants durable retrospective memory, seed:

- `<repo-root>/.agents/retro-adapter.yaml`
- `<repo-root>/charness-artifacts/retro/recent-lessons.md`

Use `$SKILL_DIR/scripts/seed_retro_memory.py` instead of hand-writing the seam.
After seeding, `retro` owns later memory updates and selection policy.

## Artifact Commit Policy

When Charness workflows write durable artifacts, make `<repo-root>/AGENTS.md`
say meaningful `charness-artifacts/` changes are repo state and commit targets.
Current-pointer helpers should no-op without canonical content changes.

## Announcement And Release Commit Bodies

When the repo uses announcement or release-note workflows, make
`<repo-root>/AGENTS.md` say meaningful behavior commits should include a short
body with issue linkage, human-visible value, verification, and operator/apply notes when relevant.

Keep GitHub close keywords and merge-commit specifics in
`agent-docs-policy.md` or `default-surfaces.md`, not in the core setup flow.

## Bounded Review Delegation

When the repo uses bounded fresh-eye or critique-style subagent review as a
stop gate, make `<repo-root>/AGENTS.md` say that review is already delegated by
the repo, agents should not wait for a second user message asking for
delegation, and host spawn restrictions should be reported explicitly instead
of replaced with a same-agent pass.

## Skill Routing

When installed Charness skills are present, add a short `Skill Routing` block
to `<repo-root>/AGENTS.md`.

Keep the block startup-bootstrap-heavy and discovery-first. Use
`$SKILL_DIR/scripts/render_skill_routing.py` so mature repos get an add-block
suggestion instead of a silent rewrite.

## Repo-Owned Skill Proof

When the repo keeps repo-owned skills under `skills/public/` or
`skills/support/`, make `<repo-root>/AGENTS.md` say semantic skill changes
should freeze current consumer intent before broad edits by deciding whether
reviewed dogfood, maintained evaluator scenarios, or checked-in scenario review
proof will carry the change.

## Worktree Adapter

When the repo uses git worktrees plus a Node hook manager such as `lefthook`,
`husky`, or `simple-git-hooks`, seed:

- `<repo-root>/.agents/worktree-adapter.yaml`

Use `$SKILL_DIR/scripts/seed_worktree_adapter.py` so `charness worktree prepare`
can install dependencies and re-register hooks per worktree. Worktree runtime
behavior stays with the worktree command surface.

## T-Events

When the repo wants to capture T-loop events such as `skill_invoked`,
`lesson_cited`, or `anchor_invoked` as Tier C evidence for the Skill-T
mechanism inventory, seed:

- `<repo-root>/.agents/t-events-adapter.yaml`

Use `$SKILL_DIR/scripts/seed_t_events_adapter.py`. Consumers that prefer not to
capture events flip `enabled: false` after seeding. Runtime capture stays with
the `t-events` integration.

## Usage Episodes

When a user-facing product repo wants privacy-bounded H-LAM/T usage episodes,
seed:

- `<repo-root>/.agents/usage-episodes-adapter.yaml`

The setup implementation uses `$SKILL_DIR/scripts/seed_usage_episodes_adapter.py`,
but that helper is not a user-facing API. After seeding, run `quality` for the validation gate; `quality` resolves and runs the Charness package-root `validate_usage_episodes.py` validator when the adapter exists.

Runtime JSONL under `.charness/usage-episodes` remains generated local state.
Runtime capture and product-specific episode vocabulary stay with the product
repo and the `usage-episodes` integration.
