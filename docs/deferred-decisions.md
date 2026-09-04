# Deferred Decisions

> Status: current
> Source of truth: this page and the archive it names
> Last verified: 2026-09-04

This page answers one question: how do we record a product-boundary choice that is not yet held by a mechanism?

There is no open register. A choice already held by a script, schema, or owning docs page does not belong here. A declined or resolved item belongs in the [archive](../charness-artifacts/spec/2026-09-04-deferred-decisions-archive.md). Add a row here only while the operator has not chosen and no mechanism holds the answer. When a mechanism lands or the operator declines, move the row to the archive in the same change.

## Record Shape

```text
Decision ID:
Question:
Current choice:
Why now:
Alternatives considered:
Impact surfaces:
Reopen trigger:
```

## Named Remedy Premise

A remedy recorded on a deferred decision is a hypothesis, not an implementation plan. Before shaping work around it, inspect the current owner of the channel the remedy assumes, then run or read the smallest evidence that can establish whether that channel exists and behaves as described. A historical sentence is not a current capability.

```text
Named remedy premise:
- Remedy: <the proposed repair, quoted or named>
- Premise: <the current fact the repair depends on>
- Evidence channel: <file read, command, fixture, or live readback>
- Observation: <what the current channel actually establishes>
- Downstream decision delta: <the later remedy, scope, order, or stop decision changed by this result>
- Status: verified | falsified | narrowed | withdrawn | not-run
```

`not-run` is an explicit non-claim, not permission to implement the named remedy. This is a review convention, not a mechanical floor.
