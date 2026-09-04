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

### Claims Record

Do not copy a historical record as a template. After the reviewer writes a new
narrative, run the planner-emitted `scaffold_claims_review.py` command. It reads
the exact prepared commit and derives record identity, target/tag, both complete
scope lists, and `scope_basis`; reviewer identity, distinctness, findings, and
the narrative remain explicit human/agent judgment inputs. The live schema is
owned by `claims_review_schema.py` and the scaffold — not by this page.

The record's own location comes from the release adapter's `output_dir` (see
[adapter-contract.md](./adapter-contract.md)), not from a fixed path. A repo
whose adapter declares no `output_dir`, or whose release record is not readable
at the derived path, is refused rather than published through a lane that
validates no claims review.

**Non-claim, and the honest size of the residual.** Nothing runnable on the
publishing machine proves a distinct observer existed. What the validator does is
refuse the shapes that made the claim unfalsifiable. Unlike the publication
verdict — whose recorded observer is paired with a mechanical channel check —
the claims side has no mechanical arm: the distinctness signal is free text.

State the residual at its real size rather than at the cost of forging a `pass`.
The floor is keyed on a marker the same agent writes and may rewrite, and nothing
else — tag state, branch state, remote state — forces the claims lane. **Deleting
the marker line from the prepared record and amending that commit skips the floor
entirely**, which is cheaper than authoring an accepted record by an order of
magnitude. The floor raises the cost of a *careless* publication and gives a
spawn-blocked host an honest alternative; it does not defeat a deliberate bypass,
and a reviewer of a release should read the claims record itself rather than
inferring one exists from a green publish.

At a `prepared-awaiting-claims-review` stop, run
`plan_release_run.py --repo-root .` for the exact resume invocation; it reads
the marker, names a `--critique-artifact` candidate that binds to the version
being published, and emits the dry-run and execute packets.

While a stop is outstanding — including at the claims-evidence commit, where the
marker is inherited — a fresh `--execute` is refused before any mutation. This
protects the boundary the claims record binds to: a second prepare over a stop
bumps another version and leaves a HEAD with no single-parent prepared boundary,
whose only resume recovery is a reset that discards an already-committed claims
review. The exits are the resume above, or — only while nothing has been
published, and after moving any blocker fix committed on top of the stop — a
reset to the commit before the prepared record. Once the tag has reached the
remote the resume is the only safe exit; a marker can still be at HEAD there,
because a publish whose closeout tail failed leaves it.

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
