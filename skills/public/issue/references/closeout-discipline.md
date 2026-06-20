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
`issue_tool.py validate-closeout-draft` against the exact draft body. For a
direct-to-default commit, rehearse the proposed commit message with
`--carrier direct-commit --commit-message-file <path>` before committing or
pushing. The draft validator uses the same ledger, critique, close-keyword, and
manual-fallback checks as `verify-closeout`, but intentionally omits final
GitHub state verification so malformed closeout markdown fails before any GitHub mutation.
After publish or manual close, still run
`issue_tool.py verify-closeout --expect-state CLOSED` for the source-of-truth
state check.

Issue-resolution carrier publication is the commit, PR body, release carrier, or
manual fallback that closes the issue. Later lifecycle/audit artifacts
(`achieve` goal updates, retro notes, handoff refreshes) may be valuable, but
they are separate publication surfaces and do not require a second issue
closeout push once the carrier and GitHub state are verified.

`verify-closeout` returns `carrier_verified` when close keywords and the
classification ledger are present but no `--expect-state` was provided. That
status is useful before push or merge, but it is not final closeout. Final
issue-resolution handoff requires `status: verified`, which means every selected
issue matched the expected GitHub state.

## Per-Issue Behavioral Verdict At Close (the irreversible-boundary mandate)

Closing a GitHub issue — and merging a PR that closes it — is an **irreversible
boundary**: others read the issue as "done", and a merge enters shared history
others build on (a reopen does not undo that it was already read as resolved). So
per *P4* of the authoring-repo-internal `<repo-root>/docs/design-north-star.md`, a
`status: verified` / `CLOSED` state and a passing carrier are *claims* — the
tracker flipped, the close keyword carried — **not** proof the reporter's
job-to-be-done behavior actually happened. `status: verified` is **necessary but
not sufficient.**

Before reporting an issue resolved, for **each** closed issue render a behavioral
verdict: confirm the issue's user-facing behavior — the reporter's JTBD acceptance
boundary — through an evidence channel **distinct from** the `CLOSED` state and
the carrier body (a behavior test that exercises the fix, a provider/connector
roundtrip, a fetch/readback of the affected surface, the actual artifact
observation). When the behavior cannot be reached, record an explicit
non-`verified` disposition naming why (the HOTL ledger statuses, or
`local-only-by-contract` for a surface that is local by the resolution contract;
see `../../hotl/references/ledger-and-dispositions.md`). **Re-reading
`verify-closeout`'s `CLOSED` result or the carrier body is not this
confirmation** — that is the same-proxy re-read *P4* names. The fresh-eye
resolution critique (next section) is the natural distinct observer; render the
per-issue verdict there. A `question`/`decision-needed` issue with no behavior
change has nothing to confirm, and the state check stands alone.

This is a per-issue **question to render, never a completion condition to
declare**: "confirm each issue, then close when all are confirmed" re-creates the
"all-green + `CLOSED` = behavior proven" equivalence this mandate exists to
remove — the obligation is to render the verdict-or-disposition per issue, not to
gate the close on an aggregate "all confirmed".

A **rung-1 presence floor** enforces exactly that obligation and no more.
`verify-closeout` / `validate-closeout-draft` refuse a `bug` / `feature` /
`deferred-work` carrier that is **silent** on a closed issue: it must carry a
`Behavior #N: <…>` line naming the distinct evidence channel the behavior was
confirmed through, **or** a typed non-`verified` disposition (a HOTL status, or
`local-only-by-contract`); a single-issue carrier may use the `Behavior:`
shorthand. The floor is **presence/form only** — it refuses *silence*, it never
declares completion: `status: verified` stays necessary-not-sufficient, a typed
non-`verified` disposition satisfies it exactly as a confirmation does, and
whether the named channel is genuinely distinct from `CLOSED`/the carrier (or the
disposition real) is the fresh-eye reviewer's judgment (**rung-2**), never the
floor's. This is the third option between judgment-only prose and a terminal-green
gate: a gate may *force the question*; it may not *declare* the behavior proven.
Alongside it, an `AI-provenance:` marker is required on the agent-authored carrier
so the irreversible external write is legible to that distinct observer.

## Resolution-Critique Carrier Header

For `bug`, `feature`, and `deferred-work` classifications, the carrier body
must carry one of the following lines so `verify-closeout` can prove the
resolution-critique sub-skill ran and is bound to the selected issue(s) (closing
the self-substitution pattern):

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

## External-Source Identity And Preservation

`axis: external-source-provider`. Slack is one adapter instance, **not** the
schema. The same contract covers Notion, Google Workspace, Drive files,
browser-gathered pages, gathered artifacts, web URLs, and any external
conversation source. Charness owns this invariant; adapters (e.g. a Ceal Slack
gather) may satisfy it, but only when the issue points to the asset/source
identity clearly enough for a fresh session.

When the issue is filed from an external originating context, the body must
carry a `Source` block that (a) marks the external origin, and (b) **preserves
the original user context** so a future resolver understands the requested
intent without the current session's memory.

Required marker:

- `Source origin:` — the external provider (`slack`, `notion`,
  `google-workspace`, `browser`, `web`, …). Its presence is what makes the
  preservation requirement apply; internal-only issues omit it.

Identity fields (use a stable identity so a fresh session can re-find the
source):

- `Source identity:` — canonical URL or stable identifier of the source
- `gathered:` — local gathered-artifact path when captured by `gather`
  (typically under `charness-artifacts/gather/<date>-<topic>.md`)
- `access:` — access mode (`public`, `private-grant`, `browser-mediated`, …)
- `freshness:` — the `gather` artifact date or last-fetched timestamp

Preservation — supply **at least one** of these auditable forms:

1. `Source text:` — relevant original source text, verbatim enough that a
   future resolver understands the intent without session memory. Form 1 is
   **allowed and encouraged** for distributed-thread intent: paste the
   load-bearing excerpt (keep it scoped; do not dump the whole thread). Quote
   it with `>` prefixes so inner `key: value` lines are not misread as fields.
2. `Re-read obligation:` — a stable `Source identity:` plus an explicit duty
   that the resolving agent must re-read / verify that source before resolving
   or closing.
3. `Source degraded reason:` — when the source is **inaccessible** during
   resolution, say so explicitly here; the closeout then classifies the proof
   as degraded rather than silently closing on missing context.

Format suggestion (form 1 + identity):

```text
## Source

- Source origin: slack
- Source identity: https://corca.slack.com/archives/.../p<ts>
- gathered: charness-artifacts/gather/2026-05-09-<topic>.md
- access: private-grant (slack-bot)
- freshness: 2026-05-09T02:14Z
- Source preservation: source-text
- Source text: |
    > earlier: "managed/dynamic progress tips, not hard-coded copy"
    > now: "and the raw timestamp needs a shared time-rendering rule"
```

Form 2 swaps the last two lines for:

```text
- Source preservation: re-read-required
- Re-read obligation: resolver must re-read Source identity before resolving or closing
```

Internal-only issues (filed from current repo state, failing commands, or
local files) carry no `Source origin:` and are exempt. The discriminator is
*did the originating context live outside this repo*; when yes, the marker +
one preservation form are required, when no, the existing evidence/JTBD is
enough.

Enforcement: `issue_tool.py verify-closeout` and `validate-closeout-draft`
fail (block) when the carrier body marks an external `Source origin:` but
carries none of the three preservation forms — missing source preservation is
a workflow risk, not optional prose style.
`issue_tool.py check-source-preservation --body-file <path>` runs the same
check over a created issue body or local artifact (add `--require-external` to assert the
issue must be externally sourced). This consumes `gather` output by reference
for identity, but form 1 deliberately preserves the load-bearing excerpt
in-body.
