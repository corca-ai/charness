# Parallel Execution

This document owns the detail behind the `## Dynamic Workflows` block in
[AGENTS.md](../../AGENTS.md). That block states the default; this one states what
the default covers, where it stops, and what it never buys.

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
checked-in contract goes stale silently, exactly as a pinned model id would; that
is the same failure this repo already recorded for subagent model defaults.

A channel the host does not expose is a concrete block to report, never a reason
to claim the work ran some other way.

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

Bounded fresh-eye reviewers run in the shared parent worktree and treat git as
read-only, per
[fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md).
Parallelism does not relax that: a reviewer that mutates the shared tree to "see
the old behavior" corrupts the operator's pending commit with every gate still
green.

A parent that must write inside an open review window declares its own paths to
[reviewer_boundary_fingerprint.py](../../skills/shared/scripts/reviewer_boundary_fingerprint.py)
`verify`. Undeclared drift is a boundary signal only for a window in which the
parent made no writes, so declaring is what keeps the signal meaningful — not a
way around it.

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
