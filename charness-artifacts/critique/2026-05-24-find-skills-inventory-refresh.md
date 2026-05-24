# Find-Skills Inventory Refresh Critique

Date: 2026-05-24

## Decision

Commit the `find-skills` inventory refresh produced by the mandatory startup
bootstrap. The refresh changes the durable capability map by adding three
installed plugin support skills (`agent-browser`, `cautilus`, `specdown`) and
new RCA ledger references for `debug`, `issue`, and `retro`.

## Likely Misread

The risky misread is treating host-local plugin cache paths as portable repo
source. The artifact is a capability inventory, so absolute installed-plugin
paths are evidence about this runtime's discoverable support surface, not
canonical repo source paths. The corresponding repo-owned integrations still
remain listed separately under `integrations/tools/`.

## Counterweight

This is not a product or validation-policy change. The inventory command
reported `requires_repo_closeout: true` because canonical capability content
changed, and current-pointer freshness plus read-only rerun showed the writer is
stable after the refresh. Keeping the artifact updated helps future routing
resolve support capabilities instead of rediscovering them ad hoc.

## Proof

- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `python3 scripts/check_command_docs.py --repo-root .`
- `./scripts/check-markdown.sh`
- `./scripts/check-secrets.sh`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 -m py_compile skills/public/*/scripts/*.py skills/support/*/scripts/*.py`
- `python3 scripts/check_skill_ownership_overlap.py --repo-root .`
- `python3 scripts/validate_current_pointer_freshness.py --repo-root .`
- `python3 skills/public/find-skills/scripts/list_capabilities.py --repo-root . --read-only`

## Next Move

Do not close #184 or #185 from this slice. #184 still needs the 2-4 week
baseline-first numeric target decision, and #185's remaining improvement tracks
need explicit choice before spec: LLM-as-judge evaluation, usage-episode
activation, or no new runtime surface until more RCA data accrues.
