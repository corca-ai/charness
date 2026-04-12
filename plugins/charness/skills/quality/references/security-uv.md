# Supply-Chain Checklist: uv

This reference covers the `uv` lockfile and audit moves that matter to
`quality`.

## Offline Gate

- if `pyproject.toml` declares dependencies or dependency groups, check in
  `uv.lock`
- if the repo stays dependency-free, do not invent a meaningless lockfile just
  to satisfy ceremony
- keep dependency declarations and the lockfile in the same repo root unless
  the packaging contract says otherwise

`scripts/check-supply-chain.py` currently owns this offline alignment check for
`charness`.

## Manual Or Networked Follow-Up

- live vulnerability checks still depend on external advisory sources
- trust review for new package indexes, direct URLs, or publisher changes still
  needs human judgment
- if a downstream repo wants a standing online audit command, make it explicit
  which binary or service owns that check and where maintainers will read it;
  `scripts/check-supply-chain-online.py` now wraps that path explicitly with
  `uv audit --frozen`
