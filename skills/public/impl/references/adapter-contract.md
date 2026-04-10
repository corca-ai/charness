# Impl Adapter Contract

The impl adapter keeps repo-specific verification expectations and future
artifact policy out of the public skill body.

## Canonical Path

Use `.agents/impl-adapter.yaml` for new repos.

Search order:

1. `.agents/impl-adapter.yaml`
2. `.codex/impl-adapter.yaml`
3. `.claude/impl-adapter.yaml`
4. `docs/impl-adapter.yaml`
5. `impl-adapter.yaml` as compatibility fallback only

## Fields

Required shared core:

- `version`
- `repo`
- `language`
- `output_dir`

Optional shared provenance:

- `preset_id`
- `preset_version`
- `customized_from`

Impl-specific fields:

- `verification_tools`
- `ui_verification_tools`
- `verification_install_proposals`

## Example

```yaml
version: 1
repo: my-repo
language: en
output_dir: skill-outputs/impl
preset_id: portable-defaults
customized_from: portable-defaults
verification_tools:
  - cmd:uv
  - cmd:pytest
  - skill:agent-browser
ui_verification_tools:
  - skill:agent-browser
  - cmd:playwright
verification_install_proposals:
  - Install the repo-preferred browser verification skill or binary before closing UI work.
```

## Tool Spec Format

Each tool entry is a string.

Supported prefixes:

- `cmd:<name>` for a shell command resolved with `which`
- `skill:<name>` for a local or globally installed Codex skill

Bare names are treated as `cmd:<name>` only as a compatibility fallback. New
adapters should always use an explicit prefix.

## Field Semantics

- `verification_tools` are the general self-verification tools the repo prefers
  the agent to look for during impl bootstrap.
- `ui_verification_tools` are the stronger tools to prefer when the slice
  touches UI, rendered artifacts, browser paths, screenshots, or other
  operator-visible presentation.
- `verification_install_proposals` are plain-language install or setup prompts
  to surface when preferred verification tools are missing.

## Design Rules

- the adapter defines repo preferences, not a closed whitelist
- keep tool discovery honest: survey what is actually installed before claiming
  a capability exists
- if the repo has a stronger preferred proof path, record it here instead of
  burying it in the main skill body
- use explicit empty lists to record intentional opt-out from repo-specific
  verification preferences
