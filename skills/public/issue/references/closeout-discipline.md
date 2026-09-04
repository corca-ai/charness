# Issue Closeout Discipline

This reference owns the durable contracts that keep `issue new` and
`issue resolve` honest at the end of the operation. The Verified Ledger,
Target Durability, and External-Source Identity sections below are the
issue-specific instantiation of the shared
`../../../shared/references/closeout-discipline.md` patterns.

Ledger fields, critique/behavior/HOTL/consolidated carrier grammar, and
source-preservation forms are rendered live by
`$SKILL_DIR/scripts/describe_closeout_draft_shape.py` (use `--stub`
for a starter carrier). Do not rediscover them by failing the validator.

## Created-Issue Ledger

`issue new` closeout must render only from a verified ledger.

After every successful create, capture `{repo, number, url}` from the create
helper's payload. Those are the exact key names it emits.

`state` is deliberately NOT in that set. No create path emits it — it belongs to
the read/verify shape, and a just-created issue is `OPEN` by construction, so
reporting it from create is noise dressed as verification. When you genuinely
need state (resolve and closeout do), read it with
`gh issue view --repo <full_name> <number> --json number,url,state` or the
host-mediated equivalent — for example, the appropriate
`acme github issue view ...` invocation that returns `number`, `url`, and
`state`. That is a separate call, not a fallback for an uncertain response shape.

The closeout report includes:

- a per-issue line for each `{repo, number, url}` in the ledger
- the created issue title and a short problem/body summary rendered from the
  helper's `body_preview`, so the requester can see what was filed without
  opening GitHub
- an explicit warning when `body_verified` is not `true`
- nothing else: never report a number, repo, or status not present in the
  ledger
- if any verification call failed, surface the failure inline next to the
  affected ledger entry rather than silently smoothing it
- **a null `number` does NOT mean the create failed — do not retry it.** The
  helper returns `ok: true` with `number: null` only when the issue was created
  and its number could not be parsed from the backend's output. The issue exists.
  Re-read it (`gh issue list --repo <full_name> --limit 5` or the host-mediated
  equivalent), report it, and say the number was recovered rather than returned.
  Retrying the create here files a duplicate, and that is the harmful reaction
  that looks safe.

Suggested single-issue shape:

```text
Created <repo>#<number>: <title> (<url>)
Body summary: <one to three sentences from body_preview>
Verification: <body verified | warning: body was not verified; re-check before relying on the filed body>
```

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

Resolution critique evidence is consumed at the close boundary, not only at
commit time. For the default file-backed reviewer path, the consumer must read
the durable worker report and require approval-eligible delivery with matching
packet/input/result/parent identities and the artifact's own Reviewed Input
Identity. A worker-delivered line without that carrier is a refusal; process
success or a non-empty output is not approval. The optional typed-subagent
values remain a distinct execution branch and must not be silently
reinterpreted as file-backed delivery.

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
`--expect-state CLOSED`. The helper and verifier must re-read GitHub state after comment plus close; they fail unless the final state is `CLOSED`; command success alone is not closeout, and carrier text alone is not closeout.

Render the required shape BEFORE drafting the carrier, not after the validator
rejects it:

```bash
python3 "$SKILL_DIR/scripts/describe_closeout_draft_shape.py" --stub
python3 "$SKILL_DIR/scripts/describe_closeout_draft_shape.py"
```

Without `--stub` the script prints the full enforced shape from the live
verifier constants so it cannot drift from the gate.

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
(`achieve` goal updates and retro notes) may be valuable, but
they are separate publication surfaces and do not require a second issue
closeout push once the carrier and GitHub state are verified.

Final closeout records should render the verifier's confirmation line when the
payload is ok, and the refusal with its reasons when it is not — never a bare
status token that sounds stronger than the observation. Existing artifacts that
recorded bare status tokens are grandfathered as-written; do not reinterpret or
rewrite them.

## Per-Issue Behavioral Verdict At Close (the irreversible-boundary mandate)

Closing a GitHub issue — and merging a PR that closes it — is an **irreversible
boundary**: others read the issue as "done", and a merge enters shared history
others build on (a reopen does not undo that it was already read as resolved). So
per *P4* of the authoring-repo-internal `<authoring-repo>/docs/design-north-star.md`,
a closed tracker state and a passing carrier are *claims* — the tracker flipped,
the close keyword carried — **not** proof the reporter's job-to-be-done behavior
actually happened. Tracker/`verify-closeout` success is **necessary but not sufficient.**

Before reporting an issue resolved, for **each** closed issue render a behavioral
verdict: confirm the issue's user-facing behavior — the reporter's JTBD acceptance
boundary — through an evidence channel **distinct from** the `CLOSED` state and
the carrier body (a behavior test that exercises the fix, a provider/connector
roundtrip, a fetch/readback of the affected surface, the actual artifact
observation). When the behavior cannot be reached, record an explicit
non-verified disposition naming why (the HOTL ledger statuses, or
`local-only-by-contract` for a surface that is local by the resolution contract;
see `../../hotl/references/ledger-and-dispositions.md`). **Re-reading
`verify-closeout`'s `CLOSED` result or the carrier body is not this
confirmation** — that is the same-proxy re-read *P4* names. The fresh-eye
resolution critique is the natural distinct observer; render the per-issue
verdict there. A `question`/`decision-needed` issue with no behavior change has
nothing to confirm, so *this* floor is exempt — but the state check does NOT
stand alone: the AI-provenance marker applies to every classification, and a
presented HOTL entry is judged whatever the classification claims to be.

This is a per-issue **question to render, never a completion condition to
declare**: "confirm each issue, then close when all are confirmed" re-creates the
"all-green + `CLOSED` = behavior proven" equivalence this mandate exists to
remove — the obligation is to render the verdict-or-disposition per issue, not to
gate the close on an aggregate "all confirmed".

Presence/form of behavior, HOTL, critique, consolidated, and provenance lines is
enforced by `validate-closeout-draft` / `verify-closeout`. Discover the live
grammar with `describe_closeout_draft_shape.py` rather than copying it here. The
floor forces the question; it does not declare the behavior proven. Whether a
named channel is genuinely distinct from `CLOSED`/the carrier remains human or
reviewer judgment.

Routine `feature`, `deferred-work`, `question`, and `decision-needed`
classifications skip the bug-only critique gate. A caller may still request
critique when a feature or deferred close crosses a material boundary. The full
contract lives at the authoring-repo-internal
`<authoring-repo>/docs/prescribed-skill-closeout-contract.md`.

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

## Consolidated Closes

`consolidated` says the issue MOVED to an umbrella; it says nothing about
whether the defect was fixed. It swaps the resolution floor for a destination
floor that is machine-verifiable. Meeting a resolution floor with false
`Implementation:` / `Prevention:` sentences is worse than no floor.

Close via `issue_tool.py close-with-comment --reason "not planned"` — not via
auto-closing carriers. Live destination/body grammar is in
`describe_closeout_draft_shape.py` (rerun with `--classification consolidated`).
An umbrella's own close must state an outcome for every member it absorbed.

NOT YET EXERCISED END TO END. As shipped, no umbrella has been filed and no
member closed through this path against a live tracker. The refusals are tested;
the happy path against real GitHub is not.

## External-Source Identity And Preservation

`axis: external-source-provider`. Slack is one adapter instance, **not** the
schema. The same contract covers Notion, Google Workspace, Drive files,
browser-gathered pages, gathered artifacts, web URLs, and any external
conversation source. Charness owns this invariant; adapters (e.g. an Acme Slack
gather) may satisfy it, but only when the issue points to the asset/source
identity clearly enough for a fresh session.

When the issue is filed from an external originating context, the body must
mark that origin and preserve enough original user context that a future
resolver understands the requested intent without the current session's memory.
Internal-only issues are exempt. The discriminator is *did the originating
context live outside this repo*.

Live field forms are in `describe_closeout_draft_shape.py`. Enforcement:
`issue_tool.py verify-closeout` and `validate-closeout-draft` fail when an
external origin is marked without a preservation form.
`issue_tool.py check-source-preservation --body-file <path>` runs the same
check over a created issue body or local artifact (add `--require-external` to
assert the issue must be externally sourced).
