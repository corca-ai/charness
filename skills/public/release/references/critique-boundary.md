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

### Claims Record Shape

The claims round's record is a `charness.release.claims-review.v4` JSON file

under `charness-artifacts/release-review/`, committed as the direct child of the
marked prepared release commit, together with the review narrative it names and
nothing else.

A `pass` must additionally declare `review_scope` (`blocking_paths` /
`advisory_paths`), `scope_basis` (the previous tag plus the exact changed-path
digest/count), and `advisory_findings`. The split exists because a claims
round that reviews the session narrative shipping inside its own bundle cannot
converge: repairing a narrative finding changes the bundle, which changes the
record and the counts, which needs new prose nothing has reviewed. Two releases
stalled on that loop. Shipped surfaces gate the tag; session narrative is
reported, published as known-inaccurate, and repaired on a later pass. The
required fields are what stop the split becoming a way to launder findings —
`advisory_findings: []` is a claim that the advisory scope was clean, not
permission to skip it.

Distinctness is a RECORDED observable, in the same shape
`publication-boundary.md` already requires of the other release verdict — each
verdict record names its observer identity explicitly rather than leaving it to
be inferred. The record carries the prepared-record bindings (`prepared_commit`,
`release_record_path`, `release_record_sha256`, `target_version`, `tag_name`), a
`verdict`, a `preparer_context` and `reviewer_context` (still required as distinct
nonempty strings — a weak leftover from the previous shape, kept because it names
the two sides in the operator's own words), and an `observer_distinctness` object:

- `kind`: one of `separate-agent-context`, `separate-host`, `separate-operator`
  for a `pass`, or `unproven`. There is deliberately no `same-agent` value — a
  same-agent reread is the observer this floor exists to exclude.
- `signal`: the concrete signal behind that kind (which reviewer ran, on what
  host, or the host refusal that blocked the spawn). One line, under 600 bytes,
  and it may not contain the prepared-stop marker: it is rendered verbatim into
  the published release record, which other gates parse, so a newline there
  injects arbitrary lines into that document. The reasoning belongs in the
  review's own narrative.
- `review_artifact`: for a `pass`, the Markdown narrative the round produced,
  naming the prepared commit and target version so an earlier release's record
  cannot be re-pointed. `null` for `unproven`.

`verdict: unproven` is a first-class state, not a failure: it is how the
paragraph above is actually written down. Publication may proceed on it, and the
claims-review record says plainly that the distinct-observer property was never
established. The published release record mirrors it: every record written after
a validated claims review carries a `## Claims Review` section naming the record
path, the verdict, the distinctness kind and its signal, and the review
narrative — and for `unproven` it states the negative property rather than the
bare token, so a reader of the record alone can tell a release whose claims round
had a distinct observer from one where none was ever established.

The record's own location comes from the release adapter's `output_dir` (see
[adapter-contract.md](./adapter-contract.md)), not from a fixed path. The floor
derives it by joining `output_dir` and `latest.md` without normalizing the
declared value, because any normalization applied on one side only is a way for
the floor and the writer to name two different files. A repo whose adapter
declares no `output_dir` at all, or whose release record is not readable at the
derived path — including one whose release output directory is untracked — is
refused rather than published through a lane that validates no claims review.

Do not copy a historical record as a template. After the reviewer writes a new
narrative, run the planner-emitted `scaffold_claims_review.py` command. It reads
the exact prepared commit and derives record identity, target/tag, both complete
scope lists, and `scope_basis`; reviewer identity, distinctness, findings, and
the narrative remain explicit human/agent judgment inputs.

An already-committed pre-`v4` record is repaired by AMENDING that commit in place; a
follow-on commit is not the direct child of the prepared record and is refused,
and an already-pushed record needs a force-push to the release branch.

Every pre-`v4` shape is refused by name. The early shapes' only distinctness test was that
`preparer_context` and `reviewer_context` were unequal strings, so one agent
writing two different strings satisfied the distinct-observer floor completely,
and a spawn-blocked session had `verdict: pass` as its only path forward.

**Non-claim, and the honest size of the residual.** Nothing runnable on the
publishing machine proves a distinct observer existed. What the validator does is
refuse the shapes that made the claim unfalsifiable: an undeclared relationship, a
same-agent reread with nowhere to say so, and a `pass` carrying no product of the
review it asserts. Unlike the publication verdict — whose recorded observer is
paired with a mechanical channel check — the claims side has no mechanical arm:
`signal` is free text.

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
