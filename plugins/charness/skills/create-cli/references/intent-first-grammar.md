# Intent-First Command Grammar

A repo-owned CLI's public command surface should read like the user's job and
journey, not like the implementation modules underneath. This reference is the
checklist a `create-cli` review uses before any command name is locked in.

## Checklist (run this before naming commands)

Ask in this order:

1. **What workflow journey does the user repeat?** Name the verbs they would
   say out loud — `discover`, `evaluate`, `improve`, `publish`, `verify`,
   `submit`, `claim`, `gather`. Those become the candidate top-level verbs.
2. **Which nouns are objects of those verbs?** Things like `claim`,
   `scenario`, `release`, `packet`, `comparison`. They become the subcommand
   slot under the journey verb, not their own top-level command.
3. **Which commands are lifecycle/readiness, not part of the journey?** The
   stable set is small: `init`, `doctor`, `update`, `reset`, `uninstall`,
   `version`. Treat that set as a separate axis from the workflow verbs.
4. **Does every proposed top-level command read like a user job?** If a name
   sounds like an internal module (`adapter`, `eval`, `claim`, `packet`,
   `workspace`, `commands`, `healthcheck`), ask whether it belongs under a
   journey verb or a lifecycle verb instead.
5. **Where does each command live in progressive disclosure?** Decide whether
   the binary or the agent skill owns it (see *Progressive disclosure* below)
   before shipping it as a public command.
6. **What is the doc framing for this command?** A page that just maps verbs
   to internal handlers fails the JTBD check (see *Docs are JTBD, not maps*).

If a candidate command does not survive questions 1–4, rename or absorb it
before the surface ships.

## Verb-Object Readability

Top-level commands should read as `<tool> <verb> <object>`, where the verb is
a user job and the object is what the verb acts on:

```text
<tool> discover <object>
<tool> evaluate <object>
<tool> improve <object>
<tool> publish <object>
<tool> doctor <scope>
<tool> init <scope>
```

The subcommand slot is almost always an object, not another action. When the
subcommand is also a verb (`evaluate observation`, `discover scenarios`), the
second verb is acting on an implied object inside the first verb's domain,
not introducing a parallel workflow.

## Rename Examples

These are real renames from the Cautilus 0.15.4 cleanup that moved the public
grammar from implementation-shaped to intent-first. Use them as templates when
auditing an existing CLI:

| Implementation-shaped (before) | Intent-first (after) |
| --- | --- |
| `claim discover` | `discover claims` |
| `claim show` | `discover claims status` |
| `eval test` | `evaluate fixture` |
| `eval evaluate` | `evaluate observation` |
| `scenario list` / `scenario show` | `discover scenarios` / `discover scenarios show` |
| `workspace prepare-compare` | `evaluate comparison prepare` |
| `adapter init` | `init adapter` |
| `healthcheck` | `doctor binary` |
| `commands` | `doctor commands` |
| `packet inspect` | `doctor packet inspect` |

The reusable shape is not the exact Cautilus names. The shape is: a journey
verb at the top, the implementation noun pushed down as the object, and
lifecycle scopes routed under `init`/`doctor` instead of as their own
top-level commands.

## Workflow Verbs vs Lifecycle Verbs

Keep these two axes visibly separate:

- **Workflow verbs** describe the user journey the product is for. They are
  the reason an operator installed the tool. Examples: `discover`,
  `evaluate`, `improve`, `publish`, `verify`. The set is small but
  product-specific.
- **Lifecycle/readiness verbs** describe operating the tool itself. They are
  the same across most repo-owned CLIs: `init`, `doctor`, `update`, `reset`,
  `uninstall`, `version`. See `command-conventions.md` for the portable
  baseline.

Help text, docs, and `--help` summaries should make this split visible so an
operator can tell at a glance which command runs the product and which
command operates the product.

## Progressive Disclosure: Binary vs Agent Skill

Both surfaces have a place, but they own different things:

| Surface | Owns |
| --- | --- |
| CLI binary | command discovery, `--help`, status and readiness detail, scenario or packet catalogs, install/update smoke, machine-readable command registry |
| Agent skill | routing into the right command, sequencing across commands, guardrails, decision boundaries, when to call which surface |

The agent skill should not become a second command registry. If the skill is
silently maintaining its own list of available subcommands, the binary's
command-discovery surface is missing — fix the binary, not the skill.

The binary should remain the source of truth for "what commands exist and
what they do." The skill should remain the source of truth for "given this
task, which of those commands to call, in what order, with what guard."

## Do Not Hide Commands to Avoid Hard Choices

Hiding a command from `--help` or command discovery is not a substitute for
deciding whether it belongs in the public grammar.

- If a surface is genuinely necessary for operators or debugging, it should
  stay inspectable through one of `doctor`, `--help`, or
  `commands --json`, and it should be documented.
- If a surface is not part of the product promise, it should be absorbed
  under the right public verb or removed from the discovery surface — not
  smuggled in as a hidden top-level command.

A "hidden but reachable" command is the worst of both worlds: operators learn
it from tribal knowledge, agents miss it in discovery, and the next refactor
breaks it without warning.

## Docs Are JTBD, Not Maps

A command reference or contract doc is a job, not a glossary. Before writing
or accepting one, answer:

- What problem does this page help an operator or agent solve?
- When should they read it — first install, daily operation, debugging,
  release?
- What decision can they make immediately after reading it?
- Is the page explaining user-visible behavior, a maintainer contract, or a
  generated artifact?

A page that only maps command names to handler functions fails this check.
Either reframe it around the operator's job, or move it under
`docs/internals/` (or its equivalent) where its audience is explicit.

## Design Takeaway

Intent-first grammar is what lets the same CLI scale from one operator to
many agents without the public surface becoming an audit log of internal
refactors. Verbs come from the user's journey. Objects come from the
product's nouns. Lifecycle stays on its own axis. The binary owns discovery;
the skill owns routing. Docs answer a job.

If a command can survive all of that, it is ready for the public grammar.
