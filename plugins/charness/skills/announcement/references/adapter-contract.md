# Announcement Adapter Contract

`announcement` stays portable by loading repo-specific message shape and
delivery seams from a repo adapter.

## Canonical Path

Use `<repo-root>/.agents/announcement-adapter.yaml` for new repos.

Search order:

1. `<repo-root>/.agents/announcement-adapter.yaml`
2. `.codex/announcement-adapter.yaml`
3. `.claude/announcement-adapter.yaml`
4. `<repo-root>/docs/announcement-adapter.yaml`
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
- `in_progress_sources`
- `delivery_kind`
- `delivery_target`
- `release_notes_path`
- `post_command_template`
- `delivery_capability`
- `format_rules_path`
- `message_size_limit`
- `outputs`

## Defaults

- `language`: `en`
- `output_dir`: `<repo-root>/charness-artifacts/announcement`
- `sections`: `["Highlights", "Changes", "Fixes"]`
- `audience_tags`: empty list in data, but resolver should expose whether the
  field was unset or explicitly empty
- `omission_lenses`: empty list
- `in_progress_sources`: empty list. Each item is a mapping with
  `kind` (`handoff`, `issues`, or `path`), an optional `path` (required when
  `kind` is `path`), and an optional `query` (issue-tracker filter)
- `delivery_kind`: `none`
- `delivery_capability`: empty string
- `format_rules_path`: empty string (skill applies built-in baseline rules
  when the delivery seam targets a chat backend)
- `message_size_limit`: `0` (disables splitting; positive integer enables
  per-message size-aware split)
- `outputs`: empty list. When non-empty each item is
  `{id, audience_tags, delivery_role: single|parent|thread_reply}` and the
  delivery seam routes outputs accordingly

## Artifact Rule

The current draft pointer filename is fixed:

- `latest.md`

Dated draft records should use:

- `YYYY-MM-DD-<slug>.md`

The default delivery record is hidden state under the repo root:

- `.charness/announcement/announcements.jsonl`

## Delivery Kinds

- `none`
- `release-notes`
- `human-backend`

`announcement` should not hardcode one SaaS target in the public body. If a
host wants Slack, GitHub release publishing, email, or another backend,
express that through a repo-owned backend seam or a downstream adapter/preset.
One common implementation path is a repo-owned command template, but that
implementation detail is not the public delivery kind.

If one backend needs a reusable private provider, record the logical capability
id in `delivery_capability`, for example `slack.default`, rather than putting a
token path in the adapter.
