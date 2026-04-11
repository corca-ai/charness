# Default Surfaces

`init-repo` uses these as the default operating surfaces.

## README

The repo root [README.md](../../../../README.md) should answer:

- what the repo is
- who it is for
- what the current scope is
- where the next planning and operator docs live

## AGENTS

The repo root [AGENTS.md](../../../../AGENTS.md) should answer:

- how an agent should operate in this repo
- language or collaboration expectations
- core repo memory surfaces
- validation and commit discipline when the repo has them

## Roadmap

The repo roadmap document, usually `docs/roadmap.md`, should answer:

- current priorities
- ordering of the next work items
- near-term exit criteria
- what is intentionally deferred

Prefer short-horizon execution direction over a grand long-range thesis.

## Operator Acceptance

The operator takeover document, usually
[docs/operator-acceptance.md](../../../../docs/operator-acceptance.md), should answer:

- what a human operator should read first
- what commands to run first
- what takeover or acceptance tasks remain
- what counts as done for each item

## Optional Install Docs

Only scaffold `INSTALL.md` and `UNINSTALL.md` when the repo really exposes an
installable surface such as a plugin, package, or operator-facing setup path.
