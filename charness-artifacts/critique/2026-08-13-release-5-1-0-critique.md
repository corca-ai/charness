# Release 5.1.0 critique
Date: 2026-08-13

## Decision Under Review

Publish the frozen `origin/main..e4da7be0c3b236067767b8f866d4e2ee79ebebde`
capability and truth-surface bundle as compatible minor release `v5.1.0`. The
release contains no issue-close carrier:
the reconciled 22-issue opening cohort remains OPEN. The publish helper alone
will bump, sync, run final release quality, create the tag/release, and record
post-publication evidence.

## Release Scope

- Current version: `5.0.1`; target/tag: `5.1.0` / `v5.1.0`.
- Minor rationale: typed create verification, planner-read disclosure, and the
  maintained subprocess-settlement detail are additive operator capabilities
  without an invocation compatibility break.
- Out of scope: issue closure, a claim of remote CI before it is observed,
  provider behavior, and proof of every consumer host.

## Surface-Lock Inventory

- Checked-in plugin and marketplace version surfaces, synchronized only by the
  release helper.
- Operator-facing quality detail, issue verification/closeout refusal paths,
  public-skill policy handling, SessionStart routing, and README proof checks.
- Public GitHub release notes at
  `charness-artifacts/release/2026-08-13-v5.1.0-notes.md`, including update,
  restart, doctor, no-supported-rollback, and OPEN-cohort boundaries.
- Post-publication fresh-checkout, release observer, installed `version` and
  `doctor` readbacks; these are required evidence, not current facts.

## Failure Angles

- **Gawande / operational:** a pre-bump green cannot prove the bumped generated
  export; final quality must follow the helper's bump and sync. Fresh checkout
  and installed readback are distinct later channels.
- **Minto / communication:** a generated commit list would not tell an operator
  what changed or that the 22 OPEN rows are not closed. Curated notes must carry
  the compatible-minor scope and the non-claims.
- **Raskin / operator interface:** update instructions cannot imply a
  version-pinned rollback that `charness update` does not offer, and the cohort
  evidence link must be tag-pinned rather than mutable `main`.
- **Weinberg / release-boundary diagnosis:** the prepared claims-review record
  must bind an exact one-parent evidence handoff.  A descendant that merely
  inherits the preparation marker must not be reclassified as a new prepared
  record and unlock auth, tag, push, or release creation.

## Counterweight Pass

- The current `5.0.1` manifest values are correct before the helper performs
  the bump; hand-editing them early would create drift rather than proof.
- No candidate path hits the release adapter's real-host trigger list. Do not
  manufacture an unrelated external-tool install checklist; the normal
  post-publish update/doctor evidence still remains required.
- Keeping every cohort issue OPEN is intentional and evidence-backed. Requiring
  a public list of all 22 issue links or closing them in this release would widen
  the boundary rather than improve it.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: `git status` and `skills/public/release/references/critique-boundary.md` | action: fix | note: commit each intended critique packet, this critique, and the curated notes before invoking the clean-worktree publish helper; no generated evidence may be accidentally omitted.
- F2 | bin: act-before-ship | evidence: strong | ref: `.agents/release-adapter.yaml` `quality_command` | action: fix | note: let the release helper run `./scripts/run-quality.sh --release` only after the 5.1.0 bump and plugin-manifest sync.
- F3 | bin: act-before-ship | evidence: strong | ref: `skills/public/release/references/publication-boundary.md` | action: fix | note: after publication, retain the helper's public-release observer and installed update/version/doctor readbacks as distinct recorded channels; do not claim hosted CI or machine-distinct observation when none ran.
- F4 | bin: act-before-ship | evidence: strong | ref: `.agents/release-adapter.yaml` fresh-checkout and post-publish readbacks | action: fix | note: retain fresh-checkout and installed update/version/doctor results in the 5.1.0 release record; the 5.0.1 record is historical only.
- F5 | bin: act-before-ship | evidence: strong | ref: `skills/public/release/references/critique-boundary.md` Claims Review | action: fix | note: run a separate closeout-claims review after the version and final release record exist, before publication.
- F5a | bin: act-before-ship | evidence: strong | ref: `skills/public/release/scripts/publish_release_claims_review.py` | action: fix | note: retain the repaired exact-parent and first-marker-only classifier tests; a prepared record, its direct claims child, and the released tag must stay distinguishable before publication.
- F6 | bin: bundle-anyway | evidence: strong | ref: `charness-artifacts/release/2026-08-13-v5.1.0-notes.md` | action: fix | note: notes now name the 22-issue opening cohort, pin the execution-ledger link to `v5.1.0`, and state that no issue closes.
- F7 | bin: bundle-anyway | evidence: strong | ref: `charness-artifacts/release/2026-08-13-v5.1.0-notes.md` | action: fix | note: notes now remove the unsupported rollback direction and specify update, restart, doctor, and retry behavior.
- F8 | bin: over-worry | evidence: moderate | ref: `.agents/release-adapter.yaml` real-host trigger paths | action: defer | note: no changed path triggers the external-tool real-host checklist; do not add a destructive host exercise to this release.
- F9 | bin: valid-but-defer | evidence: moderate | ref: `charness-artifacts/goals/2026-08-12-open-backlog-execution-ledger.md` | action: defer | note: individual tracker closures and post-publication behavior verdicts remain their own issue workflow, not a release shortcut.

## Operator Action Required

- Run the publish helper with this critique artifact and the curated notes only
  after its inputs are committed and the worktree is clean.
- If final quality, fresh checkout, public release observation, or
  installed readback fails, stop publication/closeout at that boundary and
  preserve the OPEN carriers.

## Upgrade Path

Run `charness update`, restart the active Codex or Claude Code host, and run
`charness doctor` if update or startup remains unhealthy. There is no supported
version-pinned rollback command in this release.

## Reviewer Tier Evidence

- Requested tier: high-leverage.
- Requested spawn fields: `fork_turns=none`, `model=gpt-5.6-terra`, `reasoning_effort=medium`, `service_tier=priority`.
- Host exposure state: requested_fields_sent
- Application state: host confirmation unavailable; requested reviewer fields were accepted but no applied-tier metadata was returned.
- Delivery state: findings-received.

## Fresh-Eye Satisfaction

parent-delegated — Gawande and Minto angle reviews plus a separate counterweight
read the candidate. Their two concrete blockers (prepared-marker merge topology
and stale routing/unsupported CI sequencing) were repaired; the counterweight
then required this refreshed packet identity. A final fresh reader verified the
exact committed-candidate JSON/Markdown packet binding and found no remaining
release blocker.

## Reviewed Input Identity

- Packet consumed: `charness-artifacts/critique/release-5-1-0-final-packet.json`
- Packet path: `charness-artifacts/critique/release-5-1-0-final-packet.json`
- Packet SHA256: `a51fdee23916cb7d6a77fb5150c6ba74c2bfc93445da444447bc59912014ad9f`
- Identity SHA256: `f5869d47887789022748549034980d7397d973bad728b66683cf65a6f24a84b1`
- Markdown render reviewed by bounded readers: `charness-artifacts/critique/release-5-1-0-final-packet.md` (SHA256 `5504c588c7f42cde4ee91ef6832d44103b10fe09be5bde3697c411573dec2177`).
- The final release claims review remains a separate, post-version boundary.

## Boundary Ownership

- Producer: the release adapter and `publish_release.py` own version mutation,
  manifest sync, final quality, tag/release creation, and evidence recording.
- Consumer: the operator reading the GitHub release and the release artifact;
  GitHub issue state remains a separate consumer owned by `issue`.
- Owning surface: release helper plus checked-in plugin export.
- Verdict: owned-correctly — versioned release facts stay in the release helper
  and artifact; the handoff/ledger preserve OPEN issue disposition without
  becoming a second publisher.

## Deliberately Not Doing

- Do not close, auto-close, or imply closure for any of the 22 OPEN issues.
- Do not call same-host HTTP, local tests, or a tag itself independent
  machine/CI proof.
