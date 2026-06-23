# Release Reference Index

Use this index when browsing the package manually. The run planner owns
progressive disclosure during normal operation:

```bash
python3 "$SKILL_DIR/scripts/plan_release_run.py" --repo-root . --json
```

## Core References

- `references/version-policy.md` — choose patch/minor/major honestly.
- `references/adapter-contract.md` — adapter schema, defaults, and repo-specific
  release seams.
- `references/critique-boundary.md` — critique artifact or honest blocked-host
  proof before task-completing release mutation.
- `references/publication-boundary.md` — tag, workflow, public visibility, and
  issue-close boundaries.
- `references/install-refresh.md` — operator update instructions and
  post-publish maintainer install refresh.
- `references/real-host-proof.md` — release-time host proof triggers and
  checklists.

## Compatibility Pointer

- `references/install-surface.md` — compatibility index for older references;
  new guidance lives in the concept-specific files above.
