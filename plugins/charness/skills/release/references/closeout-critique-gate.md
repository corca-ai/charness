# Release Closeout Critique Gate

Closes [#230](https://github.com/corca-ai/charness/issues/230) Waste 1c.
This gate makes the SKILL.md prose about "do not skip critique for
task-completing release work" a runtime refusal at the publish boundary,
not just a convention. The full contract spans achieve / issue / release
and lives at `<repo-root>/docs/prescribed-skill-closeout-contract.md`.

## Rule

`publish_release.py --execute` refuses unless exactly one of:

- `--critique-artifact <path>` — a tracked critique markdown artifact
  under `charness-artifacts/critique/` proving a standalone `critique`
  run produced findings for this release.
- `--critique-blocked <host-signal>` — a host-signal string used when
  the bounded fresh-eye `critique` subagent genuinely could not run.
  After the wrapper prefixes the signal with the
  `host-blocked-subagent` enum, the resulting reason must total at
  least 40 characters; terse signals like `host-down` are rejected by
  the shared closeout helper at
  `<repo-root>/scripts/check_prescribed_skill_executed_lib.py`.

Both flags supplied together is rejected with `pass exactly one of` so
operators cannot quietly add a fake blocked signal alongside a real
artifact.

## Why The Gate Runs Early

`enforce_release_critique_gate` runs immediately after
`validate_critique_artifact_arg`, before any version bump, manifest
sync, or generated-export mutation. A refusal here leaves the working
tree untouched. Operators get a clear failure cause before any release
work is committed.

## Operator Flow

For a normal critique-backed release:

```bash
python3 skills/public/release/scripts/publish_release.py \
  --repo-root . --part patch \
  --critique-artifact charness-artifacts/critique/2026-05-28-v0.10.1-release-critique.md \
  --execute
```

For a release where the bounded fresh-eye `critique` subagent was
genuinely blocked by the host runtime:

```bash
python3 skills/public/release/scripts/publish_release.py \
  --repo-root . --part patch \
  --critique-blocked "claude-code session reported missing Agent tool surface" \
  --execute
```

The blocked path is the honest substitute, not a convenience. If the
canonical bounded-review path is available and was simply not run, use
the artifact path instead.

## See Also

- `<repo-root>/skills/shared/references/fresh-eye-subagent-review.md` —
  owns the blocked-vs-available determination and the reviewer tier
  policy the artifact path encodes.
- `<repo-root>/docs/prescribed-skill-closeout-contract.md` — the
  closeout contract this gate enforces across achieve / issue / release.
