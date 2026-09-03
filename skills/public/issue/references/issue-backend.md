# Issue Backend

The `issue` skill calls one of two backend shapes:

- the default `gh` backend (`github-gh` integration, authenticated CLI)
- a host-mediated backend that exposes GitHub through a runtime capability
  (e.g. `acme github issue create -R <repo> ...`)

Backend selection is adapter-driven. The skill body never assumes a specific
binary is on PATH.

## Adapter Field

Set `issue_backend` in `<repo-root>/.agents/issue-adapter.yaml` to route through a
host-mediated backend (e.g. `acme`) instead of the default `gh` CLI.
`adapter.example.yaml` (ships with this skill) has a full worked
`issue_backend` example wired to every required operation below. Seed a
starting adapter file with:

```bash
python3 "$SKILL_DIR/scripts/init_adapter.py" --repo-root .
```

## Defaults

When `issue_backend` is omitted:

- `id: gh`
- `binary: gh`
- `commands: null` (skill uses canonical `gh` invocations)

## Harness Upstream

`harness_upstream` names the charness upstream repository as an `org/repo` slug.
It is optional and only used by the retro-derived destination split (see
`../../../shared/references/retro-issue-destination-split.md`): when a retro finding
is classified `upstream-harness`, the portable fix is filed there rather than
into the current repo.

```yaml
version: 1
harness_upstream: corca-ai/charness
```

Resolve the concrete targets with:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root . \
  resolve-destination --current <org/repo>
```

Behavior:

- **consumer repo** (current ≠ `harness_upstream`): `upstream_target` is
  `harness_upstream`, `local_target` is the current repo.
- **collapse** (current == `harness_upstream`, i.e. you are charness):
  `collapsed: true`; both targets are this repo, distinguished by label/section
  rather than destination repo.
- **unset / unresolved**: `ambiguous: true`; keep findings repo-local and state
  the ambiguity. The skill never files a harness issue into a guessed repo.

## Issue Identity: `{repo}` And `{number}`

An issue is named by `(repo, number)`. Both halves are **required** by every
command template that reads back or verifies one issue's state — the Goal Run
pickup reader's `view_state`, the closeout verifier's `view`, and the
post-close readback inside `close-with-comment`. The requirement is *rendered*
by the backend owner but *chosen* per call site (`required=`), so a surface that
does not ask for it does not get it; the three named above ask.

This is not cosmetic. `resolve_op` validates that every placeholder a template
*uses* is allowed and that every *required* one is used — but a substitution the
caller SUPPLIES and the template never consumes is dropped without comment. A
`view_state` template spelled `["view", "{number}"]` therefore silently discards
the repository, and a host binary whose default repository differs from the one
being asked about answers about **its own** issue with that number. The
downstream number check cannot catch it, because the wrong repository's issue N
also has number N. The observed result is a live backlog citation reported
`CLOSED`.

### Declaring a repo-scoped binary

A host binary genuinely bound to one repository has no `{repo}` to spell. Say so
explicitly instead of omitting the placeholder:

```yaml
issue_backend:
  id: acme
  binary: acme
  repo_scoped: corca-ai/charness   # the ONE repository this binary is bound to
  commands:
    view_state: ["view", "{number}"]
```

`repo_scoped` names the repository, and a bare `true` is **refused**. This skill
routes to two targets (`upstream_target` and `local_target`), so a waiver that
could not say *which* repository it covers would drop the identity for whichever
target the binary is not bound to — the same defect, reintroduced through the
escape hatch. Asked about any other repository, the placeholder is required
again.

The waiver covers `{repo}` and **only** `{repo}`. `{number}` is never waivable —
no binary carries an issue number implicitly, and a template omitting it resolves
to a listing whose first row gets read as the asked-about issue's state.

It is also **opt-in per call site**, not global. The Goal Run pickup reader
accepts it, because a wrong answer there is one stale pickup decision. Closeout
verification does **not**, because a wrong answer there closes a real issue and
that boundary is not reversible — so a `repo_scoped` backend still must spell
`{repo}` in its `view` template.

Omitting `{repo}` **without** the declaration is now a loud error naming the
missing placeholder, not a silent waiver. Declared, defaulted, and absent are
three different states.

### The answer is checked too

Requiring the placeholder cannot catch a binary that is *given* the repository
and ignores it, so the reported answer is checked as well: when a payload names
the repository it describes — a `repository` object (`nameWithOwner`, or an
`owner`/`name` pair) or an issue `url` — it must be the repository that was
asked about. A payload that names **no** repository is accepted, because
refusing every backend whose payload shape omits one would turn correct answers
into permanent `UNKNOWN`.

The default `gh` invocations request `url` for this reason: `gh issue view` has
no `repository` JSON field (`--json repository` exits with `Unknown JSON field`),
so `url` is the only field that names the answer's repository, and without it the
check would be one that can never fire.

The URL parse requires the path to be exactly `<owner>/<repo>/issues/<number>`
after the host, and a `repository` string without an owner is treated as *not
saying* rather than as an answer. Returning a **wrong** repository would be worse
than returning none: silence is accepted, while a wrong value refuses a correct
verdict.

## Required Operations

The skill consumes these operations through the adapter when available:

- `create` — file a new issue
- `view` — read body, comments, labels, state, linked PRs
- `close` — close the issue
- `comment` — append a close-comment with classification artifact
- `search_newest_open` — used only when `select` is invoked without a selector

Issue-native goal trackers additionally consume:

- `discover_managed_issues` — exhaustively return all issue rows needed for an
  exact local Work Item key match; search-index-only discovery is insufficient
- `update` — replace a parent body from `{body_file}`
- `list_sub_issues` — return a JSON list (or paginated list-of-lists) of real
  child issue objects, each carrying issue/repository identity and
  `parent_issue_url`
- `resolve_issue_id` — return the child issue object with its positive database
  `id`; GitHub's relationship mutation uses this id rather than issue number
- `add_sub_issue` / `remove_sub_issue` — mutate one real relationship using
  `{sub_issue_id}` and preserve prior successful relationships on failure

Run `issue_tool.py tracker-preflight --repo <owner/repo> --number <parent>`
before the first tracker write. The bootstrap preflight combines adapter/binary/
auth health, exact existing-parent repository readback, and rendered create,
view, discover, update, list, resolve, add, and remove templates. The default
`gh` backend owns canonical CLI/REST commands. A non-`gh` backend must declare
each command with all required placeholders; missing or malformed capability
yields `tracker-capability-missing` and blocks activation rather than falling
through to another backend.

`create-or-reuse-child` requires the exact marker
`<!-- charness-work-item-key: <key> -->` once in the body. It discovers before
create and after any invoked create; duplicate, mismatched, or undiscoverable
outcomes stop without a blind second create. `update` returns without mutation
when the child identity is already current, refuses stripped/malformed or
identity-mutated Goal Run metadata, and confirms the provider's target identity
after a write. Existing Goal Run parent prose is reversible provider history. A
bound parent amendment may carry the optional repo-contained canonical
`charness.goal-run-parent-amendment/v1` authorization receipt, whose
parent/binding identity, reason, and explicit approval fields are checked before
mutation; metadata bootstrap does not bind surrounding prose. `list-sub-issues` proves exact
issue and parent identities; Markdown links never count. `add-sub-issue` is
idempotent: an existing relationship returns `already-linked` without mutation.
Before parent close, `list-sub-issues --expect-all-closed` refuses while any
linked child remains open. Once a mutation command is invoked, command failure,
readback failure, or identity mismatch is `unverified-write`; retry begins with
a new read and never calls the mutation again based only on exit status.

For a complete graph comparison, prefer
`list-sub-issues --expect-child-file <json>` over repeated command-line flags.
The file is a strict `charness.expected-sub-issue-set/v1` object containing
`repo`, `parent_number`, and unique positive `children`; the result reports the
complete input-byte SHA-256. Target mismatch, duplicate numbers, unknown fields,
and malformed JSON refuse before comparison. Repeated `--expect-child` remains
only for short ad hoc reads and is mutually exclusive with the file input.

Primitive mutating tracker commands retain their explicit `--draft-sha256` and
`--binding-sha256` arguments because they have no Goal Run parent reader. Goal
Run provider operations instead resolve those optional identity fields from the
live parent metadata; a provider-free `record-observation` must carry them
explicitly. All mutation paths require `--attempt-id` and a repo-contained
`--observation-dir`. A
`charness.goal-run-observation/v1` started receipt is atomically made immutable
before the provider call; a terminal receipt binds its hash and the structured
result. A started receipt with no terminal pair is an unresolved attempt, not a
successful or no-write claim.

### Goal Run provider surface

When one parent owns a full issue-native Goal Run, use the file-backed provider
commands instead of assembling a long sequence of primitive flags:

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" goal-run-preflight \
  --repo <owner/repo> --number <parent> --plan-file <plan.json>
python3 "$SKILL_DIR/scripts/issue_tool.py" goal-run-read \
  --repo <owner/repo> --number <parent>
python3 "$SKILL_DIR/scripts/issue_tool.py" goal-run-apply \
  --repo <owner/repo> --number <parent> --operation-file <operation.json>
```

The plan and operation files are strict `v1` contracts. Each operation names the
parent, a unique attempt id, and a repo-contained observation directory. A
provider operation may repeat binding path and draft/binding identity; when
omitted, those identities are resolved from the live parent metadata. A parent
with no metadata block yet accepts exactly one operation, the parent
`update-body` that installs the first block, and only when the operation
carries all three identities itself; the desired block is validated against the
binding before the write, and the result reports `parent_metadata_bootstrap`. Body and
expected-graph paths are required to stay inside the repository. The provider
routes every operation through the selected adapter, persists
started/terminal observations, and returns typed
`verified-read`, `verified-write`, `unverified-write`, or refusal outcomes.
Create recovery performs exact discovery before any retry, so a provider/index
race can be read back and reused without a second create.

Closing is deliberately separate:

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" goal-run-close \
  --repo <owner/repo> --number <parent> --proof-file <close-proof.json>
```

The close provider checks a repo-contained, complete-byte-hash-bound final
proof index before provider selection. The index is
`charness.goal-run-final-proof-index/v1` and carries the draft/binding hashes,
repository and parent identity, a hash-bound typed expected-child file,
hash-bound parent-obligation bytes, and generic role-labelled evidence
artifacts. The close proof separately binds its comment bytes and the index
bytes; missing, stale, malformed, foreign, or mismatched inputs refuse without
a provider call. Issue core checks artifact identity and bytes; the Goal agent
owns the meaning and sufficiency of CI/docs/whole-system roles. After that
preflight, the provider checks the
exact child graph, all linked child states, and issue-owned evidence identities
before one guarded close. Generic `close-with-comment` refuses a body carrying
the Goal Run marker, preventing a routine issue close from bypassing the Goal
Run proof.

The close terminal observation is immutable. Once it exists, the provider
updates only `terminal_observation_path` and
`terminal_observation_sha256` through the existing binding-aware tracker body
update and independently reads the parent back. The final read must still
identify the requested parent, report `CLOSED`, and bind the exact terminal
receipt. A failed metadata update or final readback is reported as
`unverified-write`; it is not folded into the close mutation's success.
Retry uses typed mutation stages: a proven prior comment resumes at close
without re-commenting, and a now-closed parent can repair terminal metadata by
binding the prior close receipt without re-closing. An already-closed read is
verified only after the referenced local receipt pair matches the Goal identity.

When `id != "gh"` and `commands.search_newest_open` is missing, `select`
without an explicit selector stops with a clear error. Pass an explicit
issue number or range instead.

## Read Before Resolution

Issue resolution must read comments with the body before designing. Use:

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" read \
  --repo <full_name> --number <n>
```

For the default `gh` backend this runs:

```bash
gh issue view --comments --json number,title,body,comments,labels,state,url,author,createdAt,updatedAt
```

For adapter backends, `commands.view` must return the same `comments` list when
passed `{json_fields}` containing `comments`; otherwise `read` fails and the
resolution is blocked.

Goal Run pickup may request the optional GitHub `subIssuesSummary` field in the
same parent `view` call. The field is a live count only (`total`, `completed`,
and the derived open count); it never replaces the parent-owned execution
cursor and it never hydrates the child graph. Custom backends keep the base
reader field set unless they provide an equivalent summary, so an unavailable
summary is reported as unavailable rather than becoming a new provider gate.

## Milestones

The skill assigns only milestones the repository already has and never creates
one. The flow is backend-routed:

1. List existing milestones through the selected backend. For the default `gh`
   backend: `gh api repos/<org/repo>/milestones --jq '.[].title'`. A
   host-mediated backend should expose its own milestone-list command; if it
   has none, report the capability gap instead of guessing.
2. Gate the requested milestone with the worker:

   ```bash
   python3 "$SKILL_DIR/scripts/issue_tool.py" resolve-milestone \
     --requested "<title>" --existing "<title-1>" --existing "<title-2>"
   ```

   `action: assign` means the title matches an existing milestone and is safe to
   pass to the backend (`gh issue create --milestone "<title>"`, which itself
   rejects unknown titles). `action: leave-unassigned` means no existing
   milestone matched — leave it unset and tell the operator; do not create one.
3. Verify the final milestone in closeout through the backend `view` op (add
   `milestone` to `{json_fields}` for `gh`).

This keeps milestone handling backend-agnostic: the worker only decides
assignability from titles the agent fetched, so it never embeds a `gh`-specific
milestone mutation.

## File-Backed Close Comments

For multi-line close comments, route through the backend rather than
reconstructing the `gh` invocation. `gh issue close --comment-file` does
not exist; the working pattern is `gh issue comment --body-file <path>`
followed by `gh issue close --reason completed`. The helper subcommand
`close-with-comment` on `issue_tool.py` runs both ops through the
adapter (default `gh`, or a host-mediated backend when the adapter
declares `commands.comment` and `commands.close`):

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" close-with-comment \
  --repo <full_name> --number <n> --body-file <path> --classification <classification>
```

`--classification` selects the applicable rung-1 presence checks (behavioral
verdict or typed non-verified disposition, HOTL entry disposition,
AI-provenance marker, source preservation, and bug-only resolution-critique
binding) that run against `--body-file` before any GitHub mutation; a silent body is refused
before the comment or close command is invoked. This mirrors `verify-closeout`'s
existing checks so the manual-fallback carrier cannot mutate the issue on
evidence-free text.

Adapter templates for `comment` accept `{repo}`, `{number}`, `{body_file}`,
and `{reason}` placeholders. Templates for `close` accept `{repo}`, `{number}`,
and `{reason}`. Templates for `view` accept `{repo}`, `{number}`, and
`{json_fields}`. The runtime enforces the allowlist per op: a template using an
unknown placeholder fails fast with the offending placeholder named, so adapter
command templates do not silently grow undocumented variables.

## Verify Closeout

`issue_tool.py verify-closeout` audits an issue-resolution carrier before final
closeout:

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" verify-closeout \
  --repo <full_name> --number <n> --classification bug \
  --carrier direct-commit --commit-ref HEAD --expect-state CLOSED
```

Carrier modes:

- `direct-commit`: reads `git show -s --format=%B <commit-ref>` and requires
  GitHub closing keywords for every `--number`.
- `pr-body`: reads `--body-file` and requires closing keywords for every
  `--number`; use this as a pre-merge carrier audit unless paired with final
  `--expect-state CLOSED`.
- `manual-fallback`: reads `--body-file`, requires
  `--manual-fallback-reason` (`auto-close-unsupported`,
  `auto-close-failed-after-remote-verification`, or
  `operator-directed-manual-close`), and checks the manual close comment ledger.

All carriers require an explicit `--classification` so the verifier can check
the classification-specific closeout ledger. Without `--expect-state`, success
means `status: carrier_verified`, not final issue closeout. Final issue closeout
requires `--expect-state CLOSED`, which uses the selected backend's `view`
operation and reports `status: verified` only when every issue is closed.

For pre-push direct-to-default commits, use `validate-closeout-draft` instead of
`verify-closeout`:

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" validate-closeout-draft \
  --repo <full_name> --number <n> --classification bug \
  --carrier direct-commit --commit-message-file <path>
```

Success means `publication_status: ready_to_commit_push`; it does not prove
remote issue state. After push, run `verify-closeout` with
`--carrier direct-commit`, `--commit-ref <ref>`, and `--expect-state CLOSED`.

## Placeholders

Adapter-supplied templates substitute:

- `{repo}` — `org/name`
- `{number}` — issue number
- `{title}` — issue title
- `{body_file}` — path to a file containing the body
- `{reason}` — host-required reason text (Acme-style audit reason)
- `{json_fields}` — comma-separated json field list for `view`
- `{sub_issue_number}` — child issue number used to resolve its database id
- `{sub_issue_id}` — positive child database id used by relationship mutations

The placeholder set is the tested contract: adding a new placeholder requires
adding a substitution test in the authoring-repo-internal
`<authoring-repo>/tests/quality_gates/test_issue_skill.py` so adapter command templates do not
silently grow undocumented variables.

The skill does not sanitize values past what the host CLI already enforces.
The host backend is responsible for argument quoting, escaping, and audit
logging.

## Preflight Behavior

`issue_tool.py preflight` reports `selected_backend` with:

- `id`, `binary`, `binary_path`, `found`
- `auth_status` for `gh` (`gh auth status` exit code and output)
- `version` for non-gh backends (`<binary> --version` smoke probe)
- `commands` (echo of adapter templates so the agent can substitute
  placeholders)

Preflight returns ok only when:

- adapter is valid
- backend binary is present on PATH
- for `gh`, `gh auth status` exits 0

For non-gh backends, presence of the binary is treated as ready; the host
owns deeper auth/health probing because the worker sandbox should not
introspect host credentials.

## Body Safety

Issue bodies were repeatedly corrupted because creation flows built a backend
command with an inline shell-quoted `--body` string. Multi-line Korean/English,
Markdown, fenced code, backticks, single/double quotes, dollar signs and
shell-looking snippets, and URLs survive only if the body never passes through a
shell quoting layer.

Always create through the helper, which writes the body to a file and hands the
backend `--body-file` (rendered via the `create` op template, run with no
shell):

```bash
python3 "$SKILL_DIR/scripts/issue_tool.py" create \
  --repo <org/repo> --title "<title>" --body-file <path> \
  [--label <existing-label> ...] [--milestone <existing-milestone>]
```

- The body file is read in UTF-8 and delivered verbatim; title/labels/milestone
  ride as argv values (also no shell), so none of them can be corrupted.
- The helper refuses known placeholder titles after trimming and case-folding,
  before invoking the backend. Use `--allow-placeholder-title` only when that
  title is intentional; no broad minimum-length rule is applied.
- The helper also refuses Markdown or HTML image references to private Slack
  file URLs before invoking the backend. Publish the media at a durable URL the
  target audience can read, or replace the image syntax with an explicit
  `Media evidence unavailable:` disposition. Plain private source-identity URLs
  remain allowed as provenance; the helper does not mistake them for images.
- Use `--skip-readback` only when the caller accepts an unverified result:
  creation still occurs, and this flag skips only the post-create readback.
  Run `issue_tool.py verify-create --repo <org/repo> --number <n> --body-file
  <path>` to perform the later byte-for-byte readback through the same tool
  grammar; omit `--body-file` only when identity readback is sufficient. Never
  issue a second `create` command to verify the first one.
- Never construct `gh issue create --body "<multi-line>"` (or the equivalent on
  another backend) from a raw body string — that is the body-corruption path.
- After creating, the helper reads the issue back (`view --json number,body,url`),
  confirms the returned issue number and repository identity, and reports
  `body_verified`: `true` = stored body byte-identical; `false` =
  mismatch (with a `stored_body_bytes` count); `null` = read-back not feasible
  (number unparseable or view failed) and carries a `verify_error`. Treat
  anything other than `true` as an unconfirmed write and re-check before
  reporting success. A `false` can also mean the backend normalized the body
  server-side (e.g. CRLF→LF or a trailing-newline tweak), not corruption —
  inspect the diff rather than assuming a body-safety regression.
- The create payload also carries `body_preview`, a bounded excerpt of the
  submitted body for user-facing closeout summaries. It is context for what was
  filed, not a substitute for `body_verified`.
- Provider-agnostic: a non-gh backend declares `commands.create` (and
  `commands.view`) with the `{repo}`/`{title}`/`{body_file}` and
  `{repo}`/`{number}`/`{json_fields}` placeholders; labels/milestone are
  appended as `--label`/`--milestone` flags after the rendered base command.
  Those flag names are gh-shaped — a backend whose label/milestone syntax
  differs must handle them its own way (the body-file safety still holds).

## Proof Levels

Pair every backend change with the
`shared/references/external-capability-proof-ladder.md` levels:

- adapter declared and preflight reports it: `surface` + `host_decision`
- adapter create/view/close template rendered correctly with substitutions:
  `worker_queued`
- a real `provider_roundtrip` happens only when the host actually executes
  the rendered command against GitHub; `host_decision` returning ok is not
  the same thing
- `agent_choice` (a fresh agent picks `issue new` from natural language with
  the alternate backend installed) is independent and must be proven
  separately when relevant
