# Gather Notion Provenance

This support runtime was informed by the published-page gather implementation
in `corca-ai/claude-plugins`, but `claude-plugins` is not the runtime owner for
`charness`.

The copied vendor helper lives in this package so consumer repos do not need to
recreate a Notion export script after installing `charness`.

Local adjustments from the reference implementation:

- the wrapper lives in `scripts/export_page.py`
- `charness` treats this as a published-page capability only
- Google Workspace access is intentionally separate and should flow through a
  real external runtime such as `gws-cli`
