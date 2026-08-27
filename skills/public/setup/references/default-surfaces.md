# Default operating surfaces

`setup` starts with a Craken-like flat wiki: a small root README, a small
`AGENTS.md`, and one consumer-owned `docs/index.md` <!-- not vendored: consumer-repo path -->. The profile is a shape,
not a request to copy another repository's product or tool choices.

## Core

- `README.md` says what the repository is, who uses it, and where to start.
- `AGENTS.md` routes to the docs and contains only repository-specific rules
  that cannot live in an owner page. `CLAUDE.md` may symlink to it.
- `docs/index.md` <!-- not vendored: consumer-repo path --> is the sole current-docs router. Each page is listed once,
  owns one question, and links to its neighbors.

Keep the three entry surfaces short. Put procedures, rationale, dated evidence,
and historical proposals in the page or artifact under `charness-artifacts/`
that owns them. A stale or
duplicate page is classified before it is moved or deleted; do not create a
second page to avoid deciding ownership.

## Conditional surfaces

- Add `<repo-root>/docs/roadmap.md` only when ordered work is active or the user asks for a
  roadmap.
- Add `<repo-root>/docs/operator-acceptance.md` only when a real install, deployment, or
  takeover path exists.
- Add bootstrap, uninstall, hook, or retro-memory docs only when the repository
  actually uses that seam.

## Ownership boundaries

`setup` checks the shape and proposes the smallest surface change. `quality` owns exact gates, hook scope, ratchets, and quality-adapter writes. `release`
owns export and publication. `retro` owns its optional lesson ledger. No setup
inspection should turn one of those workflows into a root-file requirement.

When an existing `AGENTS.md` is too large, `normalize_host_docs.py` preserves it
by default. An explicit `--compact` plan shows the replacement digest; only
`--compact --execute` applies that replacement.

## Approval and verification

The inspector is read-only and emits a plan identity. Apply only the approved
surface changes, then run the narrowest relevant docs or probe checks. A green
quality adapter or available binary is not itself a quality verdict.
