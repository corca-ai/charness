# Fresh-Eye Premortem

The prior quality artifact is historical, not the authoritative universe.

Before finalizing a report:

- re-derive the source, spec, and gate inventory from the repo as it exists now
- compare that fresh inventory against the draft
- look for absent seams rather than only reclassifying already-visible ones

Focus questions:

- Which source files are not covered by any standing floor decision?
- Which quality-gate scripts are inferred by naming convention, and do
  lefthook / CI reference the same set?
- Which specs rely on `Covered by pytest:` notes, and is there a validator for
  those references?
- Which recommendations are truly `active` now, and which are `passive`
  because they depend on future tooling, budget, or product decisions?
- Which finding rests on a plausible convention, expert memory, or inherited
  best practice instead of repo evidence, source citation, or an executable
  gate?
- Which invariants might a fresh 5-minute reader misclassify as absent because
  they are spread across implementation sites instead of declared with one
  gate, type, or durable source-of-truth pointer?

Canonical execution uses a fresh-eye subagent. Before reporting that path as
blocked, run the capability check in
`../../premortem/references/subagent-capability-check.md`: attempt the bounded
subagent setup, resolve availability uncertainty, and cite the concrete host
signal. If the canonical fresh-eye premortem path is blocked, say that
explicitly and leave the host-side contract gap visible. Do not substitute a
same-agent local pass for the canonical path.
