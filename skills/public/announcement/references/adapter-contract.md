# Announcement Adapter Contract

`announcement` stays portable by loading repo-specific message shape and
delivery seams from a repo adapter.

## Canonical Path

Use `.agents/announcement-adapter.yaml` for new repos.

Search order:

1. `.agents/announcement-adapter.yaml`
2. `.codex/announcement-adapter.yaml`
3. `.claude/announcement-adapter.yaml`
4. `docs/announcement-adapter.yaml`
5. `announcement-adapter.yaml`

## Shared Core

- `version`
- `repo`
- `language`
- `output_dir`
- `preset_id`
- `preset_version`
- `customized_from`

## Announcement Fields

- `product_name`
- `sections`
- `audience_tags`
- `omission_lenses`
- `delivery_kind`
- `delivery_target`
- `release_notes_path`
- `post_command_template`

## Defaults

- `language`: `en`
- `output_dir`: `skill-outputs/announcement`
- `sections`: `["Highlights", "Changes", "Fixes"]`
- `audience_tags`: empty list in data, but resolver should expose whether the
  field was unset or explicitly empty
- `omission_lenses`: empty list
- `delivery_kind`: `none`

## Artifact Rule

The durable draft artifact filename is fixed:

- `announcement.md`

The default delivery record lives beside it:

- `announcements.jsonl`

## Delivery Kinds

- `none`
- `release-notes`
- `human-backend`

`announcement` should not hardcode one SaaS target in the public body. If a
host wants Slack, GitHub release publishing, email, or another backend,
express that through a repo-owned backend seam or a downstream adapter/preset.
One common implementation path is a repo-owned command template, but that
implementation detail is not the public delivery kind.
