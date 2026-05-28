# Confirmed-Input Over-Anchoring

A `critique` angle reference for Before-phase reviews. Use when the
pending change locks a value that came from user confirmation, issue
framing, prior session memory, or any external input that closed a
design space without proving the value is the only point.

This angle implements the
[#229 lesson](https://github.com/corca-ai/charness/issues/229) — the
agent treated a single confirmed model name as a global default when the
repo is known to run on multiple hosts. The miss was not the value; the
miss was treating one confirmed input as a closed design space.

## When This Angle Fires

Pick this angle when any of the following are present:

- The pending change cites a value from a user `AskUserQuestion`
  confirmation, an issue title, a prior session note, or a quote.
- The repo varies on a known axis (host, provider, environment, profile,
  locale, runtime, tier).
- The change writes that value into a durable surface that other axes
  will read (adapter, generated export, public skill metadata, release
  artifact, schema, validator).
- The interview that produced the value framed it as
  "confirm value X vs defer", which actively constrains the design to a
  single point.

Skip this angle when the change is genuinely scalar and the system does
not vary on the relevant axis.

## What To Probe

For each anchored value, ask:

- Is the axis named? `host`, `provider`, `environment`, `profile`,
  `locale`, `runtime`, `tier`, or an explicit
  `single-point: <reason>`.
- Does this repo already vary on that axis somewhere else (adapter,
  preset, profile, integration manifest, dogfood path)? Cite the
  varying surface.
- Would a different host or environment legitimately have a different
  value here, and would the durable surface silently use the locked
  value anyway?
- Did the interview offer the family shape, or a confirm/defer binary?
  A confirm/defer binary on a host-plural value is the failure mode.

## Counterweight Considerations

Real over-worry to push back on:

- The value really is a singleton in this codebase and adding axis
  abstraction would just be ceremony.
- The axis exists but is internal to one skill; widening it adds
  coordination cost without payoff.
- A future axis is plausible but the next non-trivial change will
  naturally surface it.

Real concerns to keep:

- The value is named in a generated export, schema, or other surface
  multiple axes read.
- The repo already varies on the axis somewhere else and the locked
  value would silently override that variance.
- The interview shape was confirm/defer when the system is plural.

## Output Contribution

When this angle finds a real concern, the spec or change artifact must
record one of:

- `axis: <name>` for the locked value (e.g., `axis: host`).
- `single-point: <reason>` when the value really is a singleton.
- Removal of the confirm/defer interview pattern in favor of a family
  shape question.

The `Counterweight Triage` bin for this angle's findings is usually
`Act Before Ship` when a generated surface or shared schema reads the
value, `Bundle Anyway` when only one skill reads it, and `Over-Worry`
when the axis truly does not vary.

## See Also

- [achieve lifecycle](../../achieve/references/lifecycle.md) — owns
  the Before-phase anti-anchoring probe step.
- [angle-selection.md](./angle-selection.md) — selection rules for the
  full angle slate.
- [counterweight-triage.md](./counterweight-triage.md) — bin
  definitions for the post-angle pass.
