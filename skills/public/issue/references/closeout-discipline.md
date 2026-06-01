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

## Resolve Auto-Close Linkage

`issue resolve` should prefer GitHub's built-in auto-close path over a manual
close command whenever the backend can carry close keywords into default-branch
history.

For PR-based work:

- put explicit close keywords (`Close #1. Close #2.`) in the PR body
- include the classification-specific closeout summary in that same PR body
- before merge, preserve the keywords if the repository uses squash, rebase, or
  edited merge commits

For direct-to-default work:

- put explicit close keywords in the commit body, not only the transcript
- include enough closeout context in that commit body for later issue readers
- when staging an issue closeout artifact, the repo-owned `commit-msg` hook
  blocks the commit unless the message body carries the same close keywords and
  required closeout ledger fields
- push first, then run `issue_tool.py verify-closeout` with
  `--carrier direct-commit`, `--commit-ref <ref>`, and
  `--expect-state CLOSED` so the carrier and GitHub state are both checked

Manual `issue_tool.py close-with-comment` is the fallback when auto-close is
unsupported by the backend or failed after the pushed or merged remote state was
verified. When manual close is used, say why auto-close was unavailable or
insufficient, then run `issue_tool.py verify-closeout` with
`--carrier manual-fallback`, `--manual-fallback-reason <reason>`, and
`--expect-state CLOSED`. The helper and verifier must re-read GitHub state after comment plus close; they fail unless the final state is `CLOSED`. command success alone is not closeout, and carrier text alone is not closeout.

Before a PR body, direct commit body, or manual close comment is published, run
`issue_tool.py validate-closeout-draft` against the exact draft body. It uses the
same ledger, critique, close-keyword, and manual-fallback checks as
`verify-closeout`, but intentionally omits final GitHub state verification so
malformed closeout markdown fails before any GitHub mutation. After publish or
manual close, still run `issue_tool.py verify-closeout --expect-state CLOSED`
for the source-of-truth state check.

`verify-closeout` returns `carrier_verified` when close keywords and the
classification ledger are present but no `--expect-state` was provided. That
status is useful before push or merge, but it is not final closeout. Final
issue-resolution handoff requires `status: verified`, which means every selected
issue matched the expected GitHub state.

## Resolution-Critique Carrier Header

For `bug`, `feature`, and `deferred-work` classifications, the carrier body
must carry one of the following lines so `verify-closeout` can prove the
resolution-critique sub-skill ran and is bound to the selected issue(s) (closes the
[#230](https://github.com/corca-ai/charness/issues/230) Waste 1b
self-substitution pattern):

- `Critique: <path>` — a checked-in critique artifact under
  `charness-artifacts/critique/` referencing the resolution. This shorthand is
  valid only for one selected issue; the file must exist, be non-empty, and bind
  to that issue number by basename or content.
- `Critique: blocked <host-signal>` — the single-issue shorthand when the host
  genuinely could not spawn the bounded fresh-eye subagent.
- `Critique #N: <path>` or `Critique #N #M: <path>` — issue-bound or explicit
  bundle critique evidence for multi-issue carriers. Every selected issue must
  be bound by one of these lines.
- `Critique #N: blocked <host-signal>` — when the host genuinely could not
  spawn the bounded fresh-eye subagent. The signal text must be specific
  enough that the total skip reason
  (`host-blocked-subagent: <signal>`) exceeds 40 characters; terse
  signals like `host-down` are rejected.

`question` and `decision-needed` classifications do not run the critique
substrate and skip this gate. The gate is additive — it runs before the
existing ledger checks (`missing_close_keywords`, `missing_fields`,
`state_mismatches`, `manual_comment_missing`) and the existing
`_classification_requirements` field set is **not** extended. The full
contract lives at the authoring-repo-internal
`<repo-root>/docs/prescribed-skill-closeout-contract.md`.

Release-driven direct-to-default work follows the same linkage. If the
repo-owned release helper is used, pass resolved issue numbers with
`--close-issue <number>` so the helper can place close keywords in the release
commit body, preflight `gh issue view` before release mutation, verify GitHub
issue state after the push and public release step, and manually close only when
the issue remains open after remote verification. The closeout must name the
carrier, manual-fallback status, and the verified final issue state.
This release helper path is already its own verifier surface; ordinary
`issue resolve` work uses `issue_tool.py verify-closeout` instead of reworking
the release helper.

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
