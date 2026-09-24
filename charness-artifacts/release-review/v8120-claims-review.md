# Claims Review — charness v8.12.0 (independent observer narrative)

Observer distinctness: separate agent context in this session; read-only
review of the prepared record. Did not prepare the release, did not rerun
the quality gate.

## Narrative

The record at 899b85f96581 ("Release charness 8.12.0") claims a prepared-only
state: bump 8.11.1 → 8.12.0 on local main, with branch/tag push, GitHub
release creation, and public-surface verification all explicitly pending
this independent claims review. The state marker
`prepared-awaiting-claims-review` matches that posture, and the push-pending
claim held: no `v8.12.0` tag exists and no remote branch contains the
commit. The version bump itself held where checked:
`packaging/charness.json` (top-level, codex and claude manifests) and
`.claude-plugin/marketplace.json` (metadata and plugin entries) all read
8.12.0 at the commit, and the parent commit read 8.11.1 throughout. The
referenced critique proof `charness-artifacts/critique/v8120-critique.md`
exists at the commit. What did not hold is evidential backing for the two
Verification lines. The quality line asserts `run-quality.sh --release
--read-only` "exited 0 in 297.4s" but cites only the command invocation,
appends the hedge "quality unestablished: pytest-release pending final
resume," and no matching durable receipt exists in the record. The drift
line (`current_release.py` no drift, 4 versioned + 1 presence-only) cites
no output or receipt. The record is honest about absences elsewhere
(adapter preflight `not_run`, bump rationale not recorded, claims review
not yet performed), but honesty about incompleteness is not verification
of the two positive claims.

## Findings

- [major] Quality-gate "exited 0" line has no citable durable receipt in
  the record; the same sentence concedes quality is unestablished pending
  final resume. Publish must wait on a receipted full run.
- [major] No `charness-artifacts/release/8.12.0-prepush-quality.json` (or
  equivalent) committed or referenced; the verification chain for this tag
  has no durable receipt.
- [minor] `current_release.py` no-drift claim cites no output or receipt.
- [minor] Bump rationale explicitly not recorded; 8.11.1 → 8.12.0 is
  unexplained per version-policy. Preparer note: minor is justified by new
  maintained capability — the stale-exec reaping entrypoint plus sweep
  integration, steer `--reason`/`--actor` audit surface, and keep_worktree
  retention expiry.
- [none] Pending-state claims verified: tag absent, commit unpushed,
  GitHub release uncreated, adapter preflight honestly `not_run`,
  claims-review honestly "not yet performed." Critique file reference
  resolves.

## Suggested verdict

unproven — the version bump and pending-state claims held, but the
quality-gate pass and drift-check claims lack backing evidence and the
record itself flags quality as unestablished.
