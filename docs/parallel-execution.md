# Parallel Execution

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-02

This document owns the detail behind the parallel-work rule in
[AGENTS.md](../AGENTS.md). The root file states the default; this one states
what the default covers, where it stops, and what it never buys.

The rule in one line: **parallel authoring, serialized integration, undiminished
proof.**

## Channels, Not Product Names

The standing request covers every concurrency channel the host actually exposes:

- work fanned out to additional agent contexts
- scripted multi-agent orchestration
- execution detached from the current turn
- isolated checkouts for concurrent writers

Host products label these differently. "Agent team", "dynamic workflow",
"background task", and "worktree isolation" are **examples of the channels, not
the contract** — a host may expose only some of them, name them otherwise, or
expose an equivalent this list does not anticipate. Resolve the concrete spelling
through that host's adapter or preset. Hardcoding one host's vocabulary into a
portable skill contract goes stale silently.

Inspect the current runtime's exposed tools and any host-provided deferred-tool
inventory before selecting a channel. Use a host spawn/subagent for short,
interactive, or judgment-bound work, and use the repository's isolated
`charness task run` lane for bounded implementation, long-running Codex work,
explicit branch/worktree/path scope, or a durable result carrier. Only explicit
inventory absence, invocation rejection, or a host error proves a lane
unavailable. When inventory cannot be inspected, call the lane unverified and
use what is visible; repository catalogs and prior-session memory are not host
capability evidence.

## Cost-Aware Model Selection

Needing a separate context does not by itself require the parent session's most
expensive model. For bounded, independent, reversible investigation or routine
implementation, use the host's fast model tier and pass that choice explicitly
when the spawn or task surface exposes a model field. Reserve the inherited or
stronger tier for critical-path integration, architecture, ambiguous repair, or
the high-leverage review classes named by their owning skill.

A repository or user may name the concrete host mapping. This repository keeps
that mapping in [repo-local host notes](../.agents/codex-host.md); portable
public skills keep the tier name and let the consuming host resolve it. An
explicit choice remains active across compaction, reload, and routine goal
pickup until the user or repository changes it. Omitting a model field means
"inherit"; it does not satisfy an explicit fast-tier choice.

## Speculate While Blocked

While a spawned reviewer, a detached command, or a network call is outstanding,
do the work that does not depend on its answer, and prefer starting the next
independent part over waiting.

Idling on a pending result is waste. Reporting a result that has not arrived is
fabrication. Only the second is unrecoverable, so **speculate on the work, never
on the finding**. A spawned agent is not a received result; an idle notification
reads like success and is not one.

Order-of-operations that a pending result does constrain still binds. This repo
requires a bug's causal review before its fix is designed, so speculative work on
that fix waits — while every part the review does not gate proceeds.

## Command Fan-Out Preflight

`charness task run` already owns its lane's base, branch, path, scope, and
worktree preflight. Do not create a second plan for that path. Use
[`command_plan_preflight.py`](../scripts/gates_support/command_plan_preflight.py) only for a manually assembled fan-out whose target,
ref, or flag resolution is otherwise ambiguous, or when an irreversible/review
boundary explicitly needs that receipt. It proves resolution and parser
ownership only, not runtime, installed state, hosted state, or external truth.

Each command must declare `owner_target` and use exactly
`{target:<owner_target>}` in `argv`; an explicit `help_argv` must use the same
standalone token, or the checker refuses the command. Embedded forms such as
`--input={target:<id>}` are target-token refusals rather than path substitutions.
This binds the planned invocation and
its help owner to one resolved path instead of allowing a copied literal or
wrong-owner probe to produce a false green. Keep the plan under the repo root;
relative plan paths are resolved from `--repo-root`, and preserve the report with
the slice evidence when the fan-out crosses a release or review boundary.

## Disjoint Writers

Concurrent writers must not share a file or a single-writer surface. Partition
the fan-out into disjoint path sets when the work allows it, and take isolated
checkouts when it does not.

These are single-writer surfaces regardless of how wide the authoring fan-out
was, because they are last-writer-wins:

- the generated plugin export under `plugins/` and the root marketplace manifests
- `.charness/` run state, including closeout proof caches and quality failure logs
- checked-in baselines and ratchet files
- the git index

So `mutate -> sync -> verify -> publish`
([implementation discipline](./implementation-discipline.md)) stays serial in the
parent: writers author, and the parent alone syncs generated surfaces, runs
gates, and commits.

## Reviewers Stay Read-Only

Typed read-only reviewers may share the parent worktree. An untyped or
write-capable reviewer uses an isolated worktree; if sharing is unavoidable,
the parent uses
[reviewer_boundary_fingerprint.py](../skills/shared/scripts/reviewer_boundary_fingerprint.py)
snapshot/verify before applying findings. The fingerprint is a git-state fallback,
not proof of fresh-eye delivery. A reviewer that mutates a shared tree still
corrupts the operator's pending commit with every gate green.

## The Proof Floor Does Not Move

N agents reporting success is not N verified outcomes. Each part closes on
executed proof in the integrated tree, never on a subagent's summary.

A wider fan-out earns a **wider** verification, not a thinner one. Two specific
temptations to refuse:

- treating a lane's own self-check as the closeout proof for that lane, when the
  lanes were only ever verified apart and never together
- letting the number of parts justify a narrower gate selection because the full
  battery got slow

If a fan-out bounded its own coverage — sampled, capped, or dropped a part —
report what was dropped. Silent truncation reads as "covered everything" when it
did not.
