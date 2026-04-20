# Narrative Review
Date: 2026-04-20

## Source Map

- `README.md`
- `INSTALL.md`
- `AGENTS.md`
- `docs/handoff.md`
- `docs/support-skill-policy.md`
- `docs/public-skill-validation.md`
- `docs/operator-acceptance.md`
- `docs/host-packaging.md`
- `charness-artifacts/quality/latest.md`
- `charness-artifacts/retro/2026-04-17-readme-intent-carry-forward-miss`
- `charness-artifacts/spec/readme-intent-rewrite-plan.md`

## Narrative Drift

- The previous README improved front-door product framing, but it still treated
  the public surface too much like a flat catalog.
- Quick Start still read like a human-operated install recipe instead of an
  agent-facing handoff into `INSTALL.md`.
- The public skill map still under-expressed intent distinctions the user
  considered load-bearing: `init-repo` as a distinct entrypoint, `quality` and
  `retro` as quality-raising loops for people and agents, and communication
  skills grouped by who is speaking to whom.
- `cautilus` was over-exposed in the README front door instead of being
  introduced where support skills and integrations are explained.

## Updated Truth

- README now leads with who `charness` is for, what kind of repo-owned agent
  work it helps structure, and the current capability-map-first session model.
- Quick Start now tells human readers to start with `INSTALL.md` directly, and
  still gives agents a clean install-contract handoff prompt plus a short
  command summary: `init`, `doctor`, then `update`.
- The command summary now reads as the main operator/agent path readers will
  keep seeing, while still leaving the detailed install, uninstall, and task
  contracts in their owner docs.
- The public skill map now groups skills by intent rather than flattening them
  into one list, with `init-repo` separated as a special entrypoint.
- `quality` and `retro` now read as dedicated quality-raising loops rather
  than implementation cleanup.
- `announcement`, `narrative`, `handoff`, and `hitl` now read by speaking
  direction, not only by topic.
- `cautilus` now appears in the support-skill / integration explanation where
  it belongs, but is described as an integration/evaluator boundary rather than
  as a fully productized public-facing concept.

## Brief

### One-Line Summary

`charness` now reads more like an operator-facing workflow map: start the host
surface through the install contract, choose the right public skill by intent,
and keep support binaries and deeper contracts in their owner sections.

### Current Contract

- README is the first-touch orientation surface.
- `INSTALL.md` remains the canonical install contract for humans and agents.
- `AGENTS.md` owns the current session discipline, including startup
  `find-skills`.
- deeper packaging, operator, and validation details stay in their owner docs
  and artifacts.

### What Changed

- Replaced the flat "what to use when" framing with an intent-based skill map.
- Moved Quick Start to an agent-facing prompt into `INSTALL.md`.
- Separated `init-repo` from the ordinary implementation flow.
- Reframed `quality` and `retro` as distinct quality-improvement loops.
- Reframed communication skills by speaker/recipient direction.
- Removed the low-value repository-shape section from the README.
- Kept support-skill and integration explanation, but moved `cautilus` into
  that section instead of front-door contrast framing.

## Claim Audit

- Claim: the README now preserves the user's stated intent distinctions rather
  than only improving surface polish.
  Evidence: `quality`/`retro`, `init-repo`, communication directions, and the
  Quick Start handoff model all reflect the explicit carry-forward feedback from
  the 2026-04-17 retro and follow-up discussion.
- Claim: install truth still belongs outside the README.
  Evidence: Quick Start hands off to `INSTALL.md` instead of recreating the
  install contract locally.
- Claim: support tools and upstream-owned capabilities are now placed in a more
  honest part of the README.
  Evidence: `cautilus`, `agent-browser`, `specdown`, and `gws-cli` are
  introduced under support skills and integrations rather than as top-level
  product contrast.

## Compression

- The README is shorter at the top level of ideas even though it now makes more
  distinctions explicit.
- The main compression move was to replace repeated inventory sections with one
  intent-based skill map plus two bounded example flows.

## Open Questions

- Should the README eventually mention the startup `find-skills` rule more
  explicitly in the Quick Start or keep it as session discipline owned by
  `AGENTS.md`?
- Should one future doc own a fuller scenario catalog once more public skills
  gain strong reviewed dogfood examples?

## Next Step

1. Re-read the new README from the perspective of a maintainer starting a new
   repo versus one already inside an existing repo.
2. If the user approves the direction, translate the same intent map into the
   Korean README variant instead of translating line by line.
3. Fold the carry-forward lessons into the `narrative` skill and repo-local
   adapter before running the `cautilus` evaluation loop.
