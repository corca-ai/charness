# Google Workspace Via `gws-cli`

Google Workspace is a real external runtime boundary in `charness`.

That means:

- do not reintroduce copied Google export helpers under `skills/support/`
- prefer a host grant when one exists
- otherwise reuse authenticated `gws` CLI state
- fall back to documented `GOOGLE_WORKSPACE_CLI_*` env vars only when the host
  lacks a stronger path

## Operator Guidance

When a Google Workspace gather request targets private Docs, Drive, Sheets, or
Slides content:

1. run `python3 "$SKILL_DIR/scripts/advise_google_workspace_path.py" --repo-root .`
2. trust the returned `doctor_status` before choosing a gather path
3. if status is `missing` or `not-ready`, tell the operator the missing step
   instead of improvising a weaker private-access claim

Common next steps come from the integration manifest:

- install `gws`
- run `gws auth setup --login` when no client is configured yet
- run `gws auth login --readonly -s drive,docs,sheets,slides` for read-only
  gather access

## Output Rule

Gathered artifacts may include source identity and freshness notes, but must
not include tokens, exported credentials, or copied auth material.
