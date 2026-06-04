# Quality Economics Refactor Closeout

Reviewer: subagent `019e92af-f5a9-79d1-b6bf-a60d8ab5969c`.

## Scope

Bounded closeout review for the post-0.18.0 quality slice:

- extracted `git_inventory_lib.py` for shared git-visible file listing in
  quality inventories
- synced the plugin mirror
- converted release critique-gate refusal tests from full publish subprocess
  setup to in-process preflight tests

## Findings

- No commit-blocking behavior regression was found.
- Low severity: both new helper files must be committed with their consumers:
  `skills/public/quality/scripts/git_inventory_lib.py` and
  `plugins/charness/skills/quality/scripts/git_inventory_lib.py`.
- Low severity: the release critique-gate tests no longer exercise the full
  publish CLI subprocess for those refusal paths. This is acceptable because
  `publish_release_cli.py` still wires artifact validation before the critique
  gate, and broader publish tests keep CLI-level publish proof.

## Verification

- Focused quality helper validators passed.
- Focused release critique-gate pytest passed.
- `nose` advisory inventory no longer reports the `git_visible_repo_files`
  clone family in the top 30 after the helper extraction.

## Disposition

Proceed with the commit after staging both public and plugin helper files.
