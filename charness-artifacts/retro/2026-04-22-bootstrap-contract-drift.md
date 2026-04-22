# Session Retro

Mode: session

Context: README/install-contract cleanup landed, but follow-up review exposed that
skill defaults, helper scopes, adapter contracts, generated exports, and current
artifacts still carried the old `INSTALL.md`/`brew` bootstrap story.

Evidence Summary: user correction in-thread, repo-wide survey of `INSTALL.md`,
`UNINSTALL.md`, `brew`, and entrypoint-doc assumptions, plus the resulting
validator and cautilus-proof refresh in this slice.

Waste:
- I initially treated the problem as a README/create-cli issue when the actual
  contract lived across public skills, repo-local adapters, helper defaults,
  generated plugin exports, integration manifests, and current-pointer
  artifacts.
- The repo had no narrow reminder that when a first-touch bootstrap contract
  changes, helper defaults and generated surfaces must be reviewed in the same
  slice.

Critical Decisions:
- Move the portable default toward README-first thin bootstrap and repo-owned
  next-action surfaces instead of separate install manuals as the default
  assumption.
- Remove `brew` from the supported install-ownership story and align control
  plane provenance/update helpers, manifests, locks, and tests in one slice.
- Refresh the checked-in cautilus proof and current artifacts in the same slice
  so the installed prompt surface, not just source docs, carries the new
  contract.

Expert Counterfactuals:
- John Ousterhout: when the interface changes, delete residual alternate
  stories quickly instead of leaving helper defaults to imply two contracts.
- Dan North: keep proof close to behavior; if a prompt-affecting install story
  changes, refresh the routing proof and current-pointer artifacts immediately.

Next Improvements:
- workflow: whenever bootstrap semantics change, run a repo-wide survey for
  helper defaults, adapters, generated exports, integration manifests, and
  current artifacts before calling the slice closed.
- validation: consider a narrow gate that flags default `INSTALL.md`/`UNINSTALL.md`
  assumptions or `brew` in maintained first-touch/operator surfaces.
- memory: keep `docs/handoff.md` focused on the next dogfood move once the
  bootstrap contract changes, not on the superseded document layout.

Persisted: yes `charness-artifacts/retro/2026-04-22-bootstrap-contract-drift.md`
