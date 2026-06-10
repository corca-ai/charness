# Adapter Contract

`.agents/hotl-adapter.yaml` names the repo-owned facts this skill must never
hardcode: which live surfaces the repo applies behavior to, which repo-owned
commands may execute or read back proof, and where the proof ledger lives.

## Fields

| Field | Type | Meaning |
| --- | --- | --- |
| `version` | int | adapter schema version (currently `1`) |
| `repo` | string | repo display name |
| `language` | string | artifact language |
| `output_dir` | string | durable artifact dir (default `charness-artifacts/hotl`) |
| `surfaces` | list of strings | the live surface classes this repo applies behavior to (for example `chat`, `scheduled-workflow`, `sheet`, `public-tools`, `control-action`, `local-guard`) |
| `proof_commands` | list of mappings | repo-owned commands the skill may use for proof; see below |
| `ledger_path` | string or unset | repo-relative path of the proof ledger, when the repo maintains one |
| `ledger_schema` | string or unset | repo-relative path of the ledger's machine-readable schema, when one exists |
| `completion_audit_command` | string or unset | repo-owned command that audits linked ledger entries before completion |

Each `proof_commands` entry:

| Key | Type | Meaning |
| --- | --- | --- |
| `id` | string | stable name the proof packet cites |
| `command` | string | the repo-owned invocation |
| `kind` | string | one of `readiness`, `readback`, `live`, `audit` |
| `boundary_reason_required` | bool | whether the command demands an explicit boundary reason (defaults to true for `live`) |

## Posture

- Fallback is `visible`: without an adapter the skill may inventory loops,
  write proof packets, and record dispositions while naming its inferred
  defaults, but it must not invent proof commands — a proof that needs an
  undeclared repo-owned command is recorded `blocked-needs-capability`.
- `unset` and `explicitly empty` differ: an unset `proof_commands` means the
  repo has not declared its proof surface yet; an explicitly empty list means
  the repo decided it owns no proof commands and every live proof routes
  through manual action packets.
- Provider execution goes through adapter-declared repo-owned commands
  whenever possible; raw provider CLIs and secrets handling stay out of the
  skill and out of the adapter examples.

## Consumption

A consuming repo wires this skill by declaring its own commands, surfaces, and
ledger facts in the adapter — the skill text never changes per repo. The first
proof packet written in a consuming repo is a good adapter review: every
feasibility line that says "command must be implemented" is either a new
repo-owned command or a `blocked-needs-capability` entry, never an ad hoc
ritual.
