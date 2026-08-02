# Critique Boundary

Task-completing release work needs critique before mutation. The publish helper
enforces this at the boundary instead of relying on prose.

## Rule

`publish_release.py --execute` refuses unless exactly one of these is present:

- `--critique-artifact <path>`: a tracked Markdown artifact under
  `charness-artifacts/critique/` proving a standalone `critique` run was
  performed for this release.
- `--critique-blocked <host-signal>`: a concrete host/tool signal used only when
  the bounded fresh-eye critique path genuinely could not run.

Supplying both is rejected. Supplying neither is rejected for publish execution.

## Claims Review

A release publishes a RECORD as much as it publishes code — release notes, an
announcement, a version claim — and that record is what readers outside the
session get. So a release closeout runs the claims round from
`../../prove/references/review-gate.md` *Claims Review*: a distinct observer
auditing what the release record ASSERTS, not whether the code is correct.

This is a different question from the critique above, and running more critique
does not answer it. The critique asks "is this release a good idea and is it
safe?"; the claims round asks "does the record of it survive contact with what
shipped?" — the version claimed against the version bumped, the notes' figures
against their sources, the "verified" lines against evidence that a verification
ran.

Why it belongs here specifically: on its first outing at goal closeout the
claims round found five record blockers that four code-reading rounds had
missed, including a verification sentence written before its verification ran
and an evidence line bound to its own record. A release record is read by more
people, later, with less context, and is the hardest to correct after the fact.

When the host cannot provide a distinct observer, record the concrete signal and
publish with the review unproven rather than substituting a same-agent reread.

## Timing

The critique gate runs before version bump, manifest sync, generated export, tag,
push, GitHub release, or install refresh. A refusal leaves the release mutation unstarted.
The claims round runs against the release RECORD, so it comes after the notes and
version claim exist and before publication makes them public.

## Update Instructions Prep

When the target version is known, run the read-only prep affordance before the
critique if update instructions may be stale or release-pinned:

```bash
python3 "$SKILL_DIR/scripts/publish_release.py" --repo-root . --part patch --prep-update-instructions
```

It emits version-agnostic adapter guidance and a staleness report without
requiring a clean worktree or critique proof. Keep per-release notes in the
release notes or release artifact, not in adapter `update_instructions`.
