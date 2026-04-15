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
- Which invariants might a fresh 5-minute reader misclassify as absent because
  they are spread across implementation sites instead of declared with one
  gate, type, or durable source-of-truth pointer?

If the session explicitly allows subagents, a fresh-eye subagent is ideal.
Otherwise perform the challenge pass locally without rereading the draft first.
