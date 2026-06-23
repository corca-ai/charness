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
python3 "$SKILL_DIR/scripts/plan_release_run.py" --repo-root . --json
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
7. Treat helper output as evidence, not terminal success. Judge public release
   surface verified status and open risks through `references/publication-boundary.md`.
8. End with operator update steps, maintainer install-refresh status, real-host
   proof status when required, and explicit non-claims.

## Invariants

- Do not hand-edit generated plugin manifests when the repo has a sync helper.
- Do not bump a version without stating why that bump level is justified.
- Do not push, tag, or announce a release without explicit user confirmation.
- Do not report a release-linked issue as resolved until GitHub verifies it
  closed and the per-issue behavioral verdict in
  `../issue/references/closeout-discipline.md` is rendered.
- Do not treat tag push, workflow completion, or helper green as public release
  verification by itself.
- Do not run sync, export, bump, install/update, or git-mutation commands in
  parallel with validators; mutate, sync, verify, then publish.
- Do not substitute same-agent review for the release critique gate.
- Apply `../../shared/references/fresh-eye-subagent-review.md` for reviewer
  tier policy when release critique or closeout review needs a fresh observer.
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
- real-host proof when required
- open risks and non-claims

## References

- `references/index.md`
