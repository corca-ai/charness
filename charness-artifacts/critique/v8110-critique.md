# Release Critique — charness v8.11.0 (minor)

- **Kind**: `charness.release-critique` (v1)
- **Prepared for**: v8.11.0-release
- **Scope**: `v8.10.0..HEAD` — #833 task-run worktree reclamation
  (patch-equivalence in cleanup containment and audit prune reclaim,
  empty-lane release at task end); managed-checkout divergence error now
  names unique local commits and their upstream equivalence; four
  migrated managed-checkout commits (claim-boundary lessons, task-run
  fixes, retro) with their gate fallout repaired.
- **Reviewers**: two fresh-eye parallel reviewers (deletion-safety,
  contract-wording) + parent synthesis; read-only, no repo mutation
- **Lane evidence**: `./scripts/run-quality.sh --full --read-only --release`
  on the final staged tree — finalized below before publish.

Fresh-eye satisfaction: parent-delegated two angle reviewers plus synthesis

## Reviewer Tier Evidence

- **Requested tier**: `high-leverage`
- **Requested spawn fields**: `read-only shared checkout; structured concerns`
- **Host exposure state**: `host-defaulted`
- **Application state**: `two angle reports delivered with concerns triage`
- **Delivery state**: `findings-received`
- **Execution mode**: `typed-subagent`

## Release Scope

v8.11.0 reclaims worktrees whose lanes already integrated. Cleanup's
`--delete-merged-branch` and audit's `--prune` accept patch-equivalence
(`git cherry`: no `+` lines) as integrated, so cherry-picked lanes stop
lingering; prune removes integrated-and-clean `task/*` worktrees plus
their branch and reports dirty/unintegrated ones with age; task end
releases worktrees with no commits beyond the base and an independently
verified clean tree. The `charness update` divergence refusal now lists
unique local commits, their patch-equivalence, and the exact recovery
(reset-safe vs migrate-first). Four operator-authored managed-checkout
commits were migrated onto main with authorship intact.

## Surface-Lock Inventory

- `scripts/worktree/{cleanup_lib,audit_lib}.py`
- `scripts/task_run/task_run_retention.py`
- root `charness` launcher (`ensure_checkout` divergence detail)
- `docs/worktree-prepare.md` (reclaim paragraphs, page under budget)
- `skills/public/impl/SKILL.md` (reference trigger word)
- `scripts/artifact-referent-local-context.json` (superseded retro refs)
- `tests/charness_cli/test_worktree_reclaim_833.py`,
  `tests/charness_cli/test_managed_install.py`,
  `tests/charness_cli/test_task_run.py` (empty-lane contract)

## Concerns

### Act Before Ship

1. **Empty-lane release trusted candidate metadata over the tree**
   (safety + wording, fixed before publish). The first cut gated only on
   `HEAD == base` plus candidate changed/disallowed paths, with no
   independent clean-tree check, and skipped the guard entirely when the
   candidate was absent — a dirty tree with empty metadata would have
   been force-removed. Fixed: `git status --porcelain` must be empty
   (and observable) regardless of metadata; pinned by
   `test_dirty_tree_without_candidate_metadata_is_kept` and
   `test_unobservable_status_keeps_the_lane`.

### Watch (accepted residuals)

1. **Patch-equivalence is content-equality, not semantic merge.** A
   cherry-picked lane whose upstream squash rewrote the change reads as
   unintegrated and keeps lingering (report-only). Safe direction.
2. **Audit prune base defaults to HEAD.** In repos whose integration
   branch is not checked out, an integrated lane may read as
   unintegrated until HEAD moves. Report-only; the reason names the base.
3. **Migrated commits predate their review.** The four managed-checkout
   commits landed verbatim (authorship/dates preserved); their gate
   fallout was repaired in-tree and the full lane is green.
4. **`task close` remains unbuilt.** Issue #833 names it as optional;
   deferred as agreed.

### Noise

- Same-second cherry-picks can share SHAs under pinned test identity;
  the tests force a distinct committer so the patch path is really taken.
- `git branch -D` after proven patch-equivalence plus a clean tree
  loses no content; the commits exist upstream by construction.

## Boundary Ownership

- **Producer**: release critique reviewers (angle findings plus synthesis)
- **Consumer**: release publisher (`publish_release.py --execute`) and
  operators reading the release notes
- **Owning surface**: `charness-artifacts/critique/v8110-critique.md`
  (this record); integrated-verdict logic owned by
  `scripts/worktree/worktree_cleanup_lib.py`, reclaim owned by
  `scripts/worktree/worktree_audit_lib.py`, lane release owned by
  `scripts/task_run/task_run_retention.py`, wording owned by
  `docs/worktree-prepare.md`
- **Verdict**: `owned-correctly`

## Bump Rationale

minor, not patch: alongside the divergence-refusal repair, the release
adds operator-facing reclamation behavior (prune reclaim with age
reports, empty-lane release, patch-equivalence) that existing users
adopt without migration.

Read-only review; no files modified by reviewers.
