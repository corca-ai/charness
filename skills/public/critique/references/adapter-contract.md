# Critique Adapter Contract

`critique` reads its repo policy from `<repo-root>/.agents/critique-adapter.yaml`.
The adapter is optional. Without it, `critique` runs with inferred
defaults and consumes no prepare packet. Concrete host mappings and current
model versions are owned by [adapter.example.yaml](../adapter.example.yaml) and
the [scaffold template](../scripts/templates/critique_adapter.yaml). A
scaffolded `<repo-root>/.agents/critique-adapter.yaml` is the repo-specific policy; this
portable contract defines only lookup and field semantics.

## Lookup Order

The adapter loader searches:

1. `<repo-root>/.agents/critique-adapter.yaml` (default)
2. `.codex/critique-adapter.yaml`
3. `.claude/critique-adapter.yaml`
4. `<repo-root>/docs/critique-adapter.yaml`
5. `critique-adapter.yaml`

First file wins. Missing adapter is a valid state.

## Adapter Fields

```yaml
version: 1
repo: <repo-name>
language: en
output_dir: charness-artifacts/critique
reviewer_runner:       # optional; defaults to a file-backed worker
  mode: file-backed-worker
  backend: codex_exec   # or claude_p; host-defaulted in portable templates
  timeout_seconds: 900
reviewer_tiers:        # optional portable-tier to host-field mapping
  high-leverage:
    model: "<host-specific model>"
    reasoning_effort: "<host-specific effort>"
    service_tier: "<host-specific service tier>"
    fork_turns: "<host-specific context fork>"
  medium:
    reasoning_effort: "<host-specific effort>"
    fork_turns: "<host-specific context fork>"
packet_sections:
  - id: changed-files-and-owning-surfaces
    title: Changed Files And Owning Surfaces
    content_kind: script
    command: "python3 scripts/review/render_critique_section_changed_surfaces.py"
  - id: known-deferred-concerns
    title: Known Deferred Concerns
    content_kind: static
    content_path: charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md
  - id: non-goals
    title: Non-Goals
    content_kind: static
    # `content` accepts a string or a list of strings (one per line).
    # Block scalars (`|`) are not supported by the repo-local YAML loader.
    content:
      - "- This critique should not relitigate the host/worker boundary portability decision."
      - "- This critique should not redesign the adapter slot shape."
```

Field semantics:

- `version` — adapter schema version, integer, currently always `1`
- `repo` — display name; defaults to the repo directory name
- `language` — render language hint for the markdown packet
- `output_dir` — repo-relative directory where packet artifacts land;
  defaults to `charness-artifacts/critique`
- `reviewer_runner` — execution boundary for the default fresh-eye run. The
  normal operator entry point is `scripts/run_review.py`; it resolves this
  adapter and derives the low-level runner inputs. `mode` is
  `file-backed-worker` (default) or the legacy `typed-subagent`; `backend` is
  `codex_exec`, `claude_p`, or `host-defaulted`; `timeout_seconds` is a
  positive integer. File-backed mode is ultimately executed through the
  compatibility runner `../../../shared/scripts/run_reviewer_worker.py`, which
  uses the repo-owned `../../../shared/references/bounded-review-result.schema.json`
  and emits the combined worker report. The semantic wrapper owns packet,
  capability, schema, and artifact-path derivation before that runner starts.
  Typed-subagent mode is a separate host branch; the
  file-backed runner refuses it rather than silently changing proof mode. The
  adapter is authoritative: a caller may not override the selected mode,
  concrete backend, or timeout for one invocation. `host-defaulted` delegates
  only the concrete backend choice to the host. The consumer must read the
  combined worker report and delivery ledger, never infer approval from an
  output file, delivery CLI field, or process exit code.
- `packet_sections` — list of declared sections; empty list is valid
  (signals "no opt-in" same as omitting the field)
- `reviewer_tiers` — optional mapping from a portable reviewer tier
  (`high-leverage`, `medium`, or `standard`) to host-specific spawn fields. The tier is
  host-plural: it translates the portable policy in
  [fresh-eye-subagent-review.md](../../../shared/references/fresh-eye-subagent-review.md)
  into the values for whichever host this repo runs on. Use `medium` for
  routine bounded fresh-eye packets and reserve `high-leverage` for release,
  issue, quality closeout, deployment-confidence, or explicitly justified
  high-risk reviews. Each tier value may set `model`, `reasoning_effort`,
  `service_tier`, and `fork_turns` (all strings, all optional);
  `reasoning_effort` / `service_tier` / `fork_turns` apply only where the host
  exposes them. Unknown tier names
  warn; unknown sub-fields error. A host without subagent model overrides
  ignores it. Use the example or scaffolded adapter for concrete host mappings
  instead of copying provider-specific model/version values into this reference.

Reviewer-tier fields are requested spawn fields, not provider-application
evidence. A host accepting or sending them does not prove the provider applied
them; record application only when the host confirms it. On hosts whose roles
can override caller-selected fields (such as Codex `agent_type`), either omit
that role or ensure its mapping preserves the requested model and reasoning
effort. This remains host-specific: other hosts own their own role and
application semantics.

Each `packet_sections` entry:

- `id` — slug, lowercase with hyphens, unique within the packet
- `title` — display title
- `content_kind` — `static` or `script`
- `command` (when `script`) — repo-relative shell command; stdout is
  the section content
- `content` (when `static`) — inline string or list of strings (one
  per line); block scalars (`|`) are not supported by the repo-local
  YAML loader, so use `content_path` for multi-line content
- `content_path` (when `static`) — repo-relative file path; contents
  are inlined verbatim

Exactly one of `command`, `content`, `content_path` must be present.

## Opt-In Signal

Repos opt in by declaring ≥1 `packet_sections` entry. When the list is
empty or the field is omitted, the conditional hard-block in
`critique` SKILL.md stays dormant.

## What The Adapter Does Not Own

- The packet envelope shape (`charness.critique_prepare_packet.v1`) —
  see [prepare-packet.md](./prepare-packet.md)
- Scanner content correctness — adapters point at producers; producers
  decide what they find
- Cross-skill packet sharing — the retro skill, if it later grows a
  prepare-packet contract, reads `<repo-root>/.agents/retro-adapter.yaml`'s own
  section slot, not this adapter

## Migration For Existing Repos

A repo that already runs critique can adopt this contract without
touching critique-time behavior: omit `packet_sections` and nothing
changes. To opt in, declare one or more sections and confirm
`prepare_packet.py` produces a packet before invoking critique. The
critique closeout validator only fires the conditional hard-block when
the adapter declares sections.
