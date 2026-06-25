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

## Timing

The critique gate runs before version bump, manifest sync, generated export, tag,
push, GitHub release, or install refresh. A refusal leaves the release mutation unstarted.

## Update Instructions Prep

When the target version is known, run the read-only prep affordance before the
critique if update instructions may be stale or release-pinned:

```bash
python3 "$SKILL_DIR/scripts/publish_release.py" --repo-root . --part patch --prep-update-instructions
```

It emits version-agnostic adapter guidance and a staleness report without
requiring a clean worktree or critique proof. Keep per-release notes in the
release notes or release artifact, not in adapter `update_instructions`.
