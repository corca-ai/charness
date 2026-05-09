# Issue Closeout Discipline

This reference owns the durable contracts that keep `issue new` and
`issue resolve` honest at the end of the operation. The Verified Ledger,
Target Durability, and External-Source Identity sections below are the
issue-specific instantiation of the shared
`../../../shared/references/closeout-discipline.md` patterns.

## Created-Issue Ledger

`issue new` closeout must render only from a verified ledger.

After every successful create, capture `{repo, number, url, state}` from the
backend response (or, when the response shape is uncertain, re-read with
`gh issue view --repo <full_name> <number> --json number,url,state` or the
host-mediated equivalent — for example, the appropriate
`ceal github issue view ...` invocation that returns `number`, `url`, and
`state`).

The closeout report includes:

- a per-issue line for each `{repo, number, url}` in the ledger
- nothing else: never report a number, repo, or status not present in the
  ledger
- if any verification call failed, surface the failure inline next to the
  affected ledger entry rather than silently smoothing it

A closeout that mentions a number outside the ledger is a contract violation,
not a stylistic miss. It forces the operator to manually re-open every URL
to figure out which part of the report is real.

## Target Durability

The intended target repo is durable workflow state from the moment it is
named or first resolved.

- on retry within the same session (e.g. user says "다시 해보세요" or "try
  again"), reuse the prior target; do not re-walk the fallback ladder
- if the prior target is unreachable (binary missing, auth failure, no
  installation, repo moved/renamed), surface `target_unavailable: <full_name>`
  with the concrete cause and stop
- never silently fall through to another accessible repo. Switching targets
  requires the user to name the new target explicitly, or an explicit
  one-line confirmation prompt naming both the old and new target
- this rule applies to `new`, `resolve`, `select`, `comment`, and `close`
  surfaces equally

The fallback ladder in `issue_runtime.resolve_target` (argument → git remote
→ adapter `default_repo` → `default_org` + cwd) is for the *first* call only.
A second call without `target` is "reuse intent", not "rediscover from cwd".

## External-Source Identity

When the issue is filed from an external originating context — Slack thread,
Notion page, Google Doc, Drive file, gathered artifact, web URL, or other
non-repo evidence — the body must include a canonical source identity block.

Required fields when an external source exists:

- canonical URL of the source (or stable identifier)
- local gathered-artifact path when the source was captured by `gather`
  (typically under `charness-artifacts/gather/<date>-<topic>.md`)
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

Internal-only issues (filed from current repo state, failing commands, or
local files) are not required to carry an external Source block. The
discriminator is *did the originating context live outside this repo*; when
yes, source identity is required, when no, the existing evidence/JTBD is
enough.

This consumes `gather` output by reference: do not paste the full source
content into the body.
