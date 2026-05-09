# Closeout Discipline (Shared)

Three closeout patterns that started in `issue` and apply equally to other
skills that mutate target repositories or external surfaces and report back
to the human afterward. Skills cite this reference and add their own concrete
verification commands.

## Verified Ledger

Closeout output renders only from a verified per-target ledger.

After every successful mutation (issue create, release publish, gather
fetch, announcement post, etc.) capture the canonical identifiers from the
backend response, or re-read with the backend's `view` equivalent when the
write response shape is uncertain. The closeout report then includes:

- one line per `{target, identifier, url}` entry in the ledger
- nothing else: never report a target, identifier, or status that is not in
  the ledger
- if any verification call failed, surface the failure inline next to the
  affected ledger entry rather than silently smoothing it

A closeout that mentions an entry outside the ledger is a contract violation,
not a stylistic miss. It forces the operator to manually re-check every
target to figure out which part of the report is real.

## Target Durability

The intended target is durable workflow state from the moment it is named or
first resolved. This applies to GitHub repos for `issue`/`release`, gather
sources for `gather`, and delivery channels for `announcement`.

- on retry within the same session ("다시 해보세요" / "try again"), reuse the
  prior target; do not re-walk the fallback ladder
- if the prior target is unreachable (binary missing, auth failure, no
  installation, target moved/renamed), surface
  `target_unavailable: <full_target>` with the concrete cause and stop
- never silently fall through to another accessible target. Switching
  targets requires the user to name the new target explicitly, or an
  explicit one-line confirmation prompt naming both the old and new target

A skill's first-call fallback ladder (argument, git remote, adapter default,
inferred current cwd, etc.) is for the *first* call only. A second call
without a target argument is "reuse intent", not "rediscover from cwd".

## External-Source Identity

When the operation is initiated from an external originating context — Slack
thread, Notion page, Google Doc, Drive file, gathered artifact, web URL, or
other non-repo evidence — the human-facing artifact (issue body, release
notes, announcement, narrative section, handoff entry) must include a
canonical source identity block.

Required fields when an external source exists:

- canonical URL of the source (or stable identifier)
- local gathered-artifact path when the source was captured by `gather`
  (typically under `<repo-root>/charness-artifacts/gather/<date>-<topic>.md`)
- access mode (`public`, `private-grant`, `browser-mediated`, etc.) when
  available from `gather` output
- freshness (the `gather` artifact date or the last-fetched timestamp)

Format suggestion:

```text
## Source

- thread: https://corca.slack.com/archives/.../p<ts>
- gathered: charness-artifacts/gather/2026-05-09-<topic>.md
- access: private-grant (slack-bot)
- freshness: 2026-05-09T02:14Z
```

Internal-only operations (initiated from current repo state, failing
commands, or local files) are not required to carry an external Source
block. The discriminator is *did the originating context live outside this
repo*; when yes, source identity is required, when no, the existing
evidence/JTBD is enough.

This consumes `gather` output by reference: do not paste the full source
content into the body.
