# Google Workspace Access

Google Workspace remains a real external boundary in `charness`, but the repo
does not ship a direct Google Workspace CLI provider.

That means:

- prefer a host-mediated Google Workspace capability when one exists
- use an operator-provided export when the operator can produce one safely
- use the browser-mediated private-source ladder only when an official export or
  host capability is unavailable or insufficient
- do not reintroduce copied Google export helpers under `skills/support/`

## Operator Guidance

When a Google Workspace gather request targets private Docs, Drive, Sheets, or
Slides content:

1. run `python3 "$SKILL_DIR/scripts/advise_google_workspace_path.py" --repo-root .`
2. follow the returned `provider_mode` and `operator_prompt`
3. if no host-mediated provider is configured, ask for an exported artifact or
   use the browser-mediated private-source ladder when the request can be
   honestly completed that way

## Output Rule

Gathered artifacts may include source identity and freshness notes, but must
not include tokens, exported credentials, copied auth material, or local browser
profile secrets.
