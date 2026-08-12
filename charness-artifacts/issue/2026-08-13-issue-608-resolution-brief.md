# Issue #608 Resolution Brief: claims-reviewed release preparation

Issue: [#608](https://github.com/corca-ai/charness/issues/608)
Classification: bug
Status: pre-implementation contract

## Reporter JTBD

Prepare a versioned, final local release record, let a distinct claims reviewer
inspect that exact record before publication, then resume the supported helper
without relying on a failed release attempt as workflow state.

## Observed Cause

The normal release executor commits the prepared record and immediately invokes
the tag/push/release tail. The release contract requires the claims review in
the missing interval. The existing `--resume` path models recovery from a
failed partial release, not a deliberate review stage.

## Fixed Decisions

- A normal `publish_release.py ... --execute` run ends after it creates the
  local release record; it does not tag, push, or create a GitHub release.
- The durable record renders an honest prepared state: local release mutation is
  complete, while tag/push, GitHub release, public verification, and installed
  refresh are pending.
- Publication resumes only through the supported `--resume --publish-current`
  path with a dedicated claims-review artifact. Before every publish side effect,
  resume validates that the artifact is tracked, committed, reachable at HEAD,
  and binds the prepared record's commit SHA, canonical path, blob SHA-256,
  target version/tag, and a distinct reviewer/pass verdict. The evidence commit
  contains no unrelated source or configuration change.
- The release tag continues to identify the prepared release record; the pushed
  branch additionally carries the claims-review evidence.
- Existing failure-recovery resume behavior remains available for records not
  deliberately marked as awaiting claims review. It must not be relabeled as
  review evidence.
- The supported pre-publication topology is explicit:

  ```text
  prepared release record commit (P; optional tag target)
  └── claims-review evidence commit (R; branch HEAD)
  ```

  Resume recognizes `P -> R` as `prepared-claims-review`, tags P if needed,
  pushes R plus that tag, and refuses mixed/advanced/remote-inconsistent states.
  Legacy unmarked `HEAD == P` recovery keeps its existing semantics.
- P carries a machine-readable `prepared-awaiting-claims-review` marker inside
  its canonical release record. The claims lane accepts only R whose direct
  parent is that marked P. R preserves P's release-record blob and changes only
  the declared claims-review artifact; validation reads both blobs from their
  committed trees, never from the working tree.
- The claims artifact is a repo-relative `charness-artifacts/release-review/*.json`
  `charness.release.claims-review.v1`
  JSON record. It declares P's commit/path/blob/tag/version, a `pass` verdict,
  and `preparer_context` plus `reviewer_context`. The helper mechanically
  requires nonempty unequal context identifiers and a pass verdict; the
  bounded-review process, not the helper, remains the honest evidence that the
  contexts are genuinely distinct. The artifact path is the sole allowed R
  delta, and its committed blob is the only review evidence the helper reads.
- Claims-lane resume validates marker, topology, R isolation, and the artifact
  before authentication, quality, tag, push, or release creation. It re-runs
  quality and fresh-checkout checks without rewriting P or creating another
  pre-push artifact commit; post-publication records retain their established
  separate artifact commits.
- Remote response loss is recoverable when readback proves the exact expected
  identity; only a missing leg is retried and a mismatched/advanced ref refuses:

  | State after interruption | Retry action |
  | --- | --- |
  | branch/tag absent; release absent | push R + tag P, then create release |
  | branch R present; tag P absent; release absent | push only tag P, then create release |
  | branch R/tag P present; release absent | create release only |
  | branch R/tag P/release present | continue verification tail without recreate |
  | any remote ref/tag/release identity differs | refuse; do not force or retag |

## Acceptance Checks

1. A source and shipped-plugin execution fixture proves normal execute produces
   a local prepared record and performs no tag, push, or release-create call.
2. A prepared record refuses resume before a claims artifact is supplied, and
   rejects an artifact with a missing/mismatched release-record binding before
   any publication call.
3. A valid distinct-review artifact permits resume; the resulting tag names the
   reviewed release record, while the pushed branch contains the evidence.
4. A retry after the claims artifact is committed reuses the evidence without
   duplicating it and still re-runs the established pre-push quality/fresh
   checkout checks. Recovery fixtures cover interruption before evidence commit,
   after evidence commit, after local tag, and after each ambiguous branch/tag
   push or release-create response.
5. The release record's state rendering and helper help/docs describe the
   two-stage workflow without claiming publication before it occurs.
6. Source and plugin mirrors stay synchronized; existing failure-recovery and
   post-publication issue-closeout semantics remain covered.
7. Resume rejects an uncommitted, unreachable, malformed, non-distinct, or
   non-passing claims artifact; a correct commit but wrong record path/blob hash
   also refuses before auth, quality, tag, push, or release creation.
8. Source and plugin execution fixtures prove both the paused prepare command
   and the binding-enforced resume command, rather than relying on mirror
   byte parity or a help-only exported-plugin probe.
9. The generated artifact has a machine-readable prepared marker, accurately
   renders every pre-publication field as pending, and CLI help names the single
   explicit `--claims-review-artifact <repo-relative path>` resume input and its
   safe prepare → review → resume handoff.
10. Claims-lane validation happens before authentication and every later helper
    call; failed binding/topology checks leave no tag, push, release-create, or
    rewritten prepared artifact.

## Deliberately Out of Scope

- Publishing v5.1.0, tagging, pushing, closing tracker issues, or claiming
  hosted/public/installed behavior.
- Replacing the existing pre-mutation release critique or weakening the distinct
  claims-review requirement.
- Redesigning issue-closeout, post-publication observer, or rollback semantics.
