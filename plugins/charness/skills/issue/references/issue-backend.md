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

## Placeholders

Adapter-supplied templates substitute:

- `{repo}` — `org/name`
- `{number}` — issue number
- `{title}` — issue title
- `{body_file}` — path to a file containing the body
- `{reason}` — host-required reason text (Ceal-style audit reason)
- `{json_fields}` — comma-separated json field list for `view`

The placeholder set is the tested contract: adding a new placeholder requires
adding a substitution test (see `tests/quality_gates/test_issue_skill.py`) so
adapter command templates do not silently grow undocumented variables.

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
