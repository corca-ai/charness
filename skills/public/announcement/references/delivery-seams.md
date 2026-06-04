# Delivery Seams

Drafting and delivery are separate responsibilities.

`announcement` should always produce draft value first.

Delivery happens only after the user explicitly confirms.

## Supported Portable Delivery Shapes

### `none`

Draft only. No posting or file update.

### `release-notes`

Append or update a checked-in markdown file such as
`<repo-root>/docs/release-notes.md`.

### `human-backend`

Deliver through an adapter-defined human-facing backend.

One common implementation seam is a repo-owned command template, but the
portable concept is still "human-facing delivery", not "run a command".

Supported placeholders:

- `{message_file}`
- `{message_file_q}`
- `{delivery_target}`
- `{delivery_target_q}`
- `{parent_delivery_handle}` (only expanded for `outputs` entries whose
  `delivery_role` is `thread_reply`; see Chaining Outputs below)
- `{parent_delivery_handle_q}`

If a host wants a chat or SaaS backend, keep the public skill generic and route
through a repo-owned backend seam.

If that backend depends on reusable private access, keep the adapter-level
binding portable by setting `delivery_capability` to one logical capability id
such as `slack.default`.

## Format Rules

Different chat backends have different markdown dialects. Slack rejects
CommonMark-style `# Headers`, `**bold**`, and `[label](https://example.com)` links and instead
expects mrkdwn (`*bold*`, `<url|text>`, `_italic_`, no `#` headers).

When the delivery seam targets a chat backend, the skill must not let raw
CommonMark go to the wire. Two ways to express that contract:

1. Adapter-declared rules path. The adapter may set `format_rules_path` to a
   repo-owned conversion contract (for example, the runtime prompt that
   describes the chat dialect). The skill loads that contract before
   delivery and converts the draft accordingly.
2. Skill-built-in rules. When `format_rules_path` is unset and the delivery
   target is Slack-shaped, apply the built-in mrkdwn conversion below.

### Slack mrkdwn (built-in baseline)

Slack's chat surface accepts a constrained dialect:

- bold: `*bold*` (single asterisk), not `**bold**`
- italic: `_italic_`, not `*italic*`
- inline code: backtick-fenced is supported
- code block: triple-backtick block is supported
- links: `<https://example.com|label>`, not `[label](https://example.com)`
- bullets: dash-prefixed list items render reliably; asterisk-prefixed lists may render but are less predictable
- headers: there are no `#` headers; use a bold first line instead
- horizontal rules: not rendered

Convert before posting:

- replace `**x**` with `*x*`
- replace `*x*` (italic) with `_x_` if the source intended italic
- replace `[label](https://example.com)` with `<url|text>`
- strip leading `#`/`##`/`###` and bold the resulting line
- strip horizontal rules (`---`)

If the adapter declares a different chat backend (for example Discord,
Microsoft Teams), point the skill at the repo's own conversion contract via
`format_rules_path` instead of pretending Slack's rules apply.

## Per-Backend Size Limits

Most chat backends reject messages above a per-message size limit (Slack's
effective `chat.update` ceiling is around 4000 characters; other backends
have their own limits). The skill must not assume the draft fits.

The adapter declares the limit through `message_size_limit` (characters; `0`
disables splitting). When the limit is positive and the draft exceeds it, the
skill splits the draft on paragraph boundaries (blank lines) into numbered
parts before posting:

- prefix each part with `(part N/total)` so the recipient can tell what they
  have
- never split inside a fenced code block
- never split inside a numbered list step that was meant to stay contiguous;
  split on blank lines first, fall back to bullet boundaries only if a single
  paragraph alone exceeds the limit

The split policy belongs to the skill; the size limit belongs to the adapter
because every backend has its own ceiling.

## Dual Outputs

When the adapter declares an `outputs` list (see `draft-shape.md`), the
delivery seam reads each output's `delivery_role`:

- `single` — one draft body, one delivery (default when `outputs` is empty)
- `parent` — top-level message; for chat backends this is the thread starter
- `thread_reply` — posted as a reply to the most recent `parent` output

For non-chat backends (`release-notes`), `parent` and `thread_reply` may be
expressed as primary file plus an adjacent comment, primary file plus a PR
description, or whatever the repo's seam declares. The portable concept is
"primary surface vs. follow-up surface", not "Slack thread."

`message_size_limit` splitting applies to every output role, including
`thread_reply`. A long follow-up output is split on paragraph boundaries the
same way `parent`/`single` outputs are, before posting.

## Chaining Outputs

Chaining is opt-in: an adapter that declares only `single` or
`outputs: []` never needs to emit a handle, and existing
`post_command_template` shapes that ignore stdout remain valid.

When `outputs` declares a `parent` followed by one or more `thread_reply`
roles, the delivery seam must feed the parent's identifier into each
follow-up post. The portable contract is opaque-handle forwarding:

1. The seam runs `post_command_template` once per output in `outputs` order.
2. Each `post_command_template` invocation that emits content the seam may
   later need to chain into must print a single JSON object as its **last
   non-empty stdout line**, containing at least `delivery_handle`:

   ```json
   {"delivery_handle": "<backend-defined string>"}
   ```

   Additional fields are allowed; the seam reads only `delivery_handle`.
   Earlier stdout lines (logs, progress, warnings) are ignored. Anything on
   stderr is ignored.
3. The seam stores the most recent `parent` output's `delivery_handle` and
   expands `{parent_delivery_handle}` / `{parent_delivery_handle_q}` for any
   subsequent `thread_reply` output's command template.

The handle's *format* is backend-defined and opaque to the public contract.
Examples (each host owns its own shape; the public surface never names them):

- Slack: a `chat.postMessage` `ts` value such as `1700000000.123456`
- GitHub: an issue or PR comment id, e.g. `2148903456`
- Discord/Teams: a message id or thread id
- `release-notes`: a section anchor or the URL of the appended PR review
  comment

If a `thread_reply` output is declared without a parent output or without a
`{parent_delivery_handle}` / `{parent_delivery_handle_q}` placeholder in the
template, resolver output reports `delivery_contract.status: draft-only`.
Delivery code must treat that as non-executable and stop before posting a
top-level message by accident.

If a `thread_reply` output's template references `{parent_delivery_handle}` but
no prior `parent` output produced a handle at runtime, the seam should fail fast
rather than post the literal placeholder.

When a `parent` output is split into `(part N/total)` chunks by
`message_size_limit`, the seam captures the **first part's**
`delivery_handle` and uses that for downstream `thread_reply` outputs, so
follow-up replies land under the same parent anchor.

### Worked example

The host owns the JSON emission shape. A representative pattern feeds the
backend response through `jq` so the last non-empty stdout line is the
required JSON object:

```yaml
post_command_template: >-
  slack-cli chat postMessage --channel {delivery_target_q} --file {message_file_q}
  | jq -c '{delivery_handle: .ts}'
```

For a `thread_reply` output the template adds the handle placeholder:

```yaml
post_command_template: >-
  slack-cli chat postMessage --channel {delivery_target_q}
  --thread-ts {parent_delivery_handle_q} --file {message_file_q}
  | jq -c '{delivery_handle: .ts}'
```

The first invocation reads the parent post's response, projects only
`ts` to `delivery_handle`, and prints it as the final stdout line. The
seam stores that handle and substitutes it into the follow-up template.
Operators can switch to a different backend without touching the public
contract: `gh issue comment ...` piped through
`jq -c '{delivery_handle: .url}'` works the same way for GitHub
PR-comment delivery, and a release-notes seam can echo a section anchor
literal.

The resolver still emits warnings for miswired chaining, but the load-bearing
machine signal is `delivery_contract.status`: `thread_reply` configurations are
either executable or explicitly draft-only before any backend post is attempted.
