# Issue Backend

The `issue` skill calls one of two backend shapes:

- the default `gh` backend (`github-gh` integration, authenticated CLI)
- a host-mediated backend that exposes GitHub through a runtime capability
  (e.g. `ceal github issue create -R <repo> ...`)

Backend selection is adapter-driven. The skill body never assumes a specific
binary is on PATH.

## Adapter Field

Set `issue_backend` in `.agents/issue-adapter.yaml`:

```yaml
version: 1
issue_backend:
  id: ceal-github
  binary: ceal
  commands:
    create:
      - github
      - issue
      - create
      - "-R"
      - "{repo}"
      - "--title"
      - "{title}"
      - "--body-file"
      - "{body_file}"
      - "--reason"
      - "{reason}"
      - "--json"
    view:
      - github
      - issue
      - view
      - "-R"
      - "{repo}"
      - "{number}"
      - "--json"
      - "{json_fields}"
    close:
      - github
      - issue
      - close
      - "-R"
      - "{repo}"
      - "{number}"
      - "--reason"
      - "{reason}"
    comment:
      - github
      - issue
      - comment
      - "-R"
      - "{repo}"
      - "{number}"
      - "--body-file"
      - "{body_file}"
      - "--reason"
      - "{reason}"
    search_newest_open:
      - github
      - issue
      - list
      - "-R"
      - "{repo}"
      - "--state"
      - "open"
      - "--limit"
      - "1"
      - "--json"
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

## Required Operations

The skill consumes these operations through the adapter when available:

- `create` — file a new issue
- `view` — read body, comments, labels, state, linked PRs
- `close` — close the issue
- `comment` — append a close-comment with classification artifact
- `search_newest_open` — used only when `select` is invoked without a selector

When `id != "gh"` and `commands.search_newest_open` is missing, `select`
without an explicit selector stops with a clear error. Pass an explicit
issue number or range instead.

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
  --repo <full_name> --number <n> --body-file <path>
```

Adapter templates for `comment` accept `{repo}`, `{number}`, `{body_file}`,
and `{reason}` placeholders. Templates for `close` accept `{repo}`, `{number}`,
and `{reason}`. Templates for `view` accept `{repo}`, `{number}`, and
`{json_fields}`. The runtime enforces the allowlist per op: a template using an
unknown placeholder fails fast with the offending placeholder named, so adapter
command templates do not silently grow undocumented variables.

## Verify Closeout

`issue_tool.py verify-closeout` audits an issue-resolution carrier before final
handoff:

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
means `status: carrier_verified`, not final issue closeout. Final handoff
requires `--expect-state CLOSED`, which uses the selected backend's `view`
operation and reports `status: verified` only when every issue is closed.

## Placeholders

Adapter-supplied templates substitute:

- `{repo}` — `org/name`
- `{number}` — issue number
- `{title}` — issue title
- `{body_file}` — path to a file containing the body
- `{reason}` — host-required reason text (Ceal-style audit reason)
- `{json_fields}` — comma-separated json field list for `view`

The placeholder set is the tested contract: adding a new placeholder requires
adding a substitution test in the authoring-repo-internal
`tests/quality_gates/test_issue_skill.py` so adapter command templates do not
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

## Body Safety (#232)

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
- Never construct `gh issue create --body "<multi-line>"` (or the equivalent on
  another backend) from a raw body string — that is the #232 corruption path.
- After creating, the helper reads the issue back (`view --json body`) and
  reports `body_verified`: `true` = stored body byte-identical; `false` =
  mismatch (with a `stored_body_bytes` count); `null` = read-back not feasible
  (number unparseable or view failed) and carries a `verify_error`. Treat
  anything other than `true` as an unconfirmed write and re-check before
  reporting success. A `false` can also mean the backend normalized the body
  server-side (e.g. CRLF→LF or a trailing-newline tweak), not corruption —
  inspect the diff rather than assuming a #232 regression.
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
