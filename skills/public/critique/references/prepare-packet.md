# Critique Prepare Packet

The **critique prepare packet** is a deterministic, adapter-driven payload
that fresh-eye reviewers consume *before* broad repo sampling. It exists
to keep critique focused on judgment instead of repeatedly rediscovering
enumerable inventory (changed surfaces, adapter subscriptions, doc-link
graphs, role classifications, deferred concerns).

The packet shape is portable. Charness owns the envelope and the runner;
each consumer repo's `.agents/critique-adapter.yaml` decides which
sections apply and how each section's content is produced.

## When This Fires

The prepare runner fires when:

- the user (or a parent skill) asks `critique` to prepare a packet for
  the next critique pass
- the adapter declares ≥1 `packet_sections` entry (this is the opt-in
  signal — repos with no critique adapter or no declared sections see
  no behavior change)
- the runner is invoked explicitly via
  `python3 skills/public/critique/scripts/prepare_packet.py --repo-root .`

The runner does not fire automatically inside the `critique` workflow
today. Critique consumes a packet that the parent (or a previous turn)
already produced; see the *Consumer Contract* below.

## Envelope

The packet is emitted as two artifacts:

- a JSON payload at
  `<output_dir>/<slug>-packet.json` — machine-readable contract
- a markdown render at
  `<output_dir>/<slug>-packet.md` — human-readable view that subagent
  reviewers actually read

Where `<output_dir>` defaults to `charness-artifacts/critique` (override
via adapter `output_dir`) and `<slug>` defaults to a date+sequence
identifier (override via runner `--slug` flag).

JSON envelope shape (`charness.critique_prepare_packet.v1`):

```json
{
  "kind": "charness.critique_prepare_packet",
  "version": 1,
  "repo": "<repo-name>",
  "generated_at": "<ISO8601 UTC>",
  "prepared_for": "<short label: commit range, branch, or free text>",
  "adapter_path": "<repo-relative path or null>",
  "sections": [
    {
      "id": "<slug>",
      "title": "<display title>",
      "content_kind": "static" | "script",
      "producer": "<command string or static-config marker>",
      "content": "<rendered string body of the section>",
      "ok": true,
      "errors": []
    }
  ],
  "section_count": 1,
  "ok": true
}
```

Rules:

- `kind` is the literal string `charness.critique_prepare_packet`
- `version` starts at `1`; bump on incompatible envelope changes
- `sections` is a list in declaration order (adapter-declared order
  preserved)
- Each section's `content` is a rendered string the reviewer reads
  directly. JSON-shaped section payloads are pretty-printed inside
  `content` (envelope stays one shape; section payload variety stays
  inside content).
- A failing section sets its own `ok: false` and `errors: [...]`. The
  envelope-level `ok` is `true` only when every section is `ok: true`.
- Envelope-level `ok: false` does not block packet emission; reviewers
  still read what was produced and judge whether the missing section
  changes their next move.

## Section Types

A `packet_sections` entry has:

- `id`: short slug, lowercase-with-hyphens, unique within the packet
- `title`: one-line display title for the markdown render
- `content_kind`: `static` or `script`
- `content` (when `static`, inline string or list of strings) — OR
- `content_path` (when `static`, repo-relative path to a file whose
  contents are inlined verbatim) — OR
- `command` (when `script`, repo-relative shell command the runner
  executes; stdout becomes the section content)

Exactly one of `content`, `content_path`, or `command` must be present
per section, matching the declared `content_kind`.

`static` sections capture stable enumerable data (deferred-decisions
list, non-goals list, doc-link inventory). They are cheap and ideal for
"the things this critique should not relitigate."

`script` sections capture dynamic data (changed-files-and-owning-
surfaces, scanner findings, adapter subscriptions for the changed
paths). They are the place where consumer-specific scanners live; the
runner is content-agnostic.

## Default Sections

Charness ships one default section that runs on the charness repo and
serves as the contract reference example:

- `changed-files-and-owning-surfaces` — for the current
  `git status`/`git diff` working set, list each changed path and the
  surfaces (from `.agents/surfaces.json`) that own or derive from it.
  Producer:
  `python3 scripts/render_critique_section_changed_surfaces.py --json`.

Consumers add more sections in their own `.agents/critique-adapter.yaml`.

## Consumer Contract (Critique Skill)

When `critique` runs and the repo's adapter declares ≥1 packet section:

1. The fresh-eye reviewer subagents receive the packet content
   (markdown render) before broad repo sampling. The parent passes the
   packet path or the packet body in the angle/counterweight prompts.
2. The critique closeout records `Packet Consumed: <path>`. The
   conditional hard-block is workflow-prescriptive: the rule applies
   only when the adapter declares packet sections, and enforcement
   lives in the *caller skill's* closeout validator (e.g., a future
   `validate_quality_closeout_contract.py` extension), not in a
   global `validate_critique_packet_consumed.py`. Critique itself
   writes results into the caller's artifact, so there is no canonical
   critique-output file for a global validator to scan.
3. The critique skill does not re-run the prepare runner inside its
   own workflow. The packet is produced upstream (by the caller or a
   previous turn) so the prepare cost is not paid twice.

When the adapter declares no `packet_sections`, this contract is dormant
and critique behavior is unchanged.

## Producer Script Contract

A `script` section's producer command must:

- run from the repo root
- exit 0 when the section produced honest content (even if the content
  is empty — for example, "no changed paths detected")
- exit non-zero only when the producer itself failed (missing
  dependency, parse error). Non-zero exit makes the runner record the
  section with `ok: false` and the captured stderr.
- write the rendered section body to stdout
- support `--json` if the producer also wants to emit a structured
  payload, but the runner reads only stdout text and stores it as
  `content`. JSON-shape contract is producer-side, not envelope-side.

The runner is intentionally thin: read adapter, run command, capture
stdout/stderr, fold into envelope. No retry, no caching, no merging
across runs. If a section needs caching, that lives in the producer.

## Schema Validation

The runner validates each declared section before invoking it:

- exactly one of `content`/`content_path`/`command` per section
- `content_kind` matches the populated field
- `content_path` resolves to a file under the repo root
- `command` is a non-empty string

Adapter validation is wired into the shared `validate_adapters.py`:
`.agents/critique-adapter.yaml` is parsed by
`scripts/critique_adapter_lib.load_adapter` so a malformed adapter
(missing required fields, dual-content fields, kind/field mismatch,
duplicate section ids) fails the standing adapter gate before the
runner ever spawns a producer process. A separate `validate_critique_packet.py`
validates an emitted packet's envelope shape.

## Out Of Scope For This Contract

- Charness does not classify section roles (`source` / `derived` /
  `audit-only` / `rewrite`). Roles are consumer-specific and live in
  the producer's section content.
- Charness does not enforce content correctness. The contract verifies
  packet *shape* and *presence*, not whether a scanner found the right
  things.
- The retro skill does not consume this packet today. A retro-side
  counterpart (`retro_packet_sections`) may follow as a separate slice
  once one or more repos have proven the critique-side contract.
