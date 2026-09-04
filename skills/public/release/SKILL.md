---
name: release
description: "Use when a maintainer needs to cut, bump, or verify a repo release surface such as plugin versions, generated install manifests, and operator update instructions."
---

# Release

Use this when the task is to advance or verify a repo-owned release surface,
not just to describe recent changes.

`release` is the maintainer-facing workflow for versioned plugin or package
surfaces that ship checked-in install metadata. It keeps release contracts
honest instead of improvising bumps, update advice, generated-file edits, or
publish completion claims. Every task-completing release slice records critique before closeout.

## Bootstrap

Resolve `$SKILL_DIR` per `../../shared/references/bootstrap-resolution.md`, then
run the planner before mutation, broad verification, tag push, or publish:

```bash
python3 "$SKILL_DIR/scripts/plan_release_run.py" --repo-root . --detail
```

Read every planner `required_reads` entry and follow `next_action`. The planner
surfaces current release state, configured evidence packets, target-version
staleness, critique posture, and publish commands without mutating the repo.

If the planner reports `scaffold_adapter` or `repair_adapter`, run or repair the
adapter path first:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

## Workflow

1. Restate the release goal: inspect only, publish current, patch/minor/major
   bump, or explicit target version.
2. Run `plan_release_run.py`; read required refs before acting.
3. Resolve planner blockers before mutation.
4. Run or record the required critique proof. Use
   `references/critique-boundary.md` for the exact artifact/blocked-host rule.
5. Choose the lightest honest bump.
   - patch for bug fixes, copy fixes, and behavior repairs
   - minor for new maintained capability or additive operator surface
   - major only when compatibility or invocation expectations break
6. Use the repo-owned publish helper for bump, sync, verify, tag, publish,
   distinct-channel confirmation, issue closeout, install refresh, and final
   artifact persistence.
   When it stops at `prepared-awaiting-claims-review`, write the review narrative,
   then use the planner-emitted `scaffold_claims_review.py` command. The scaffold
   derives the prepared record hash and complete release-delta partition; do not
   hand-copy those fields into JSON.
7. Treat helper output as evidence, not terminal success. Judge public release
   surface verified status and open risks through `references/publication-boundary.md`.
   Before a retry or resume, use the shared `scope-too-broad`,
   `verifier-defect`, or `subject-defect` classification and the critique retry
   helper; rerun only the smallest proof whose canonical subject, verifier,
   input, or stable failure identity changed. A new receipt label is evidence
   to record, not permission to retry. A release helper's existence does not
   justify repeating every release check.
8. End with operator update steps, maintainer install-refresh status, and
   explicit non-claims.

### Release notes are derived, not authored

Generate them from the tree being shipped, over the FINAL tree and not earlier.
Quantities belong in derived claim markers, never in typed prose.

```bash
python3 "$SKILL_DIR/scripts/generate_release_notes.py" --repo-root . --notes-file <notes.md> --sync
python3 "$SKILL_DIR/scripts/generate_release_notes.py" --repo-root . --notes-file <notes.md> --check --version <vX.Y.Z>
python3 "$SKILL_DIR/scripts/lint_release_narrative.py" --notes-file <notes.md> --version <vX.Y.Z>
```

## Invariants

- Do not hand-edit generated plugin manifests when the repo has a sync helper.
- Do not bump a version without stating why that bump level is justified.
- Do not push, tag, or announce a release without explicit user confirmation.
- Do not report a release-linked issue as resolved until GitHub verifies it
  closed and the per-issue behavioral verdict in
  `../issue/references/closeout-discipline.md` is rendered.
- Do not treat tag push, workflow completion, or helper green as public release
  verification by itself.
- Do not repeat a release gate with the same target, verifier, input, and stable
  failure identity without new evidence; narrow the proof or record the
  non-claim first. Required distinct-channel public readback after tag/push is
  an irreversible-boundary proof, not an optional retry of an unchanged local
  check; if it is unavailable, the release claim remains unproven.
- Do not run sync, export, bump, install/update, or git-mutation commands in
  parallel with validators; mutate, sync, verify, then publish.
- Do not substitute same-agent review for the release critique gate.
- Apply `../../shared/references/fresh-eye-subagent-review.md` for reviewer
  tier policy when release critique or closeout review needs a fresh observer.
- For an untyped reviewer that shares the parent tree, use the rail-1
  snapshot/verify commands from that reference's Enforcement section. Typed
  read-only and isolated reviewers do not need the extra fingerprint.
- Keep a verified release ledger; if a release target cannot be re-read, record
  the `target_unavailable` disposition from
  `../../shared/references/closeout-discipline.md`.
- If the repo lacks declared release files or sync scripts, stop cleanly and name
  the missing seam instead of inventing one.

## Output

Use the publish helper payload and release artifact as the output template. The
final answer should summarize:

- current and target version
- release scope and bump rationale
- critique proof
- verification and public release state
- operator update steps and maintainer install refresh
- open risks and non-claims

## References

- `references/index.md`
