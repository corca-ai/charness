# Disposition Reviewer Brief

The `achieve` After-phase's rung-2 fresh-eye disposition reviewer (see
`achieve/references/lifecycle-after.md` *Disposition Gate - Two Rungs*) has
three substantive judgment calls a deterministic floor cannot make. Read this
before running the review; it is the reviewer-facing brief, not the mega-
reference the review is spawned out of.

## Falsify `novel:` Claims

Rung 1d's floor only proves a recurrence-lineage marker is *present*. The
reviewer must judge whether it is *true*: for each `issue #N` disposition
asserting `novel:`, search the recurrence lineage (prior issues/retros of the
same class) and decide whether this is actually a re-file of a known recurring
class being laundered as a fresh narrow issue — if so, reject it (the general
fix, not the N-th point-fix, is the real disposition). A `recurs:` lineage that
names real prior instances is the honest form.

## Classify Structural-Follow-Up Destination

Rung 1e's floor only proves a `Structural follow-up:` line is *present* with a
valid form. The reviewer must judge whether the chosen *destination* is right:
for each transferable waste item the retro's `## Sibling Search` names, decide
whether the structural fix belongs in an `applied:` change landed this run, an
`issue #N`, a consuming-repo `repo-local guard: <path>`, or genuinely
`none — <reason>`. **Reject "recorded in recent-lessons" as a destination**
unless it is paired with one of those — a memory note is capture, not a
structural disposition. Rejecting that over-claim is the whole point of the
destination mandate.

## Confirm Closed-Issue Behavior Through A Distinct Channel

Confirm each closed issue's behavior at an issue-bundle closeout (the
irreversible-boundary mandate). When the goal closes a tracked GitHub issue
bundle that touches HOTL/live behavior, closing the issues is an irreversible
boundary (others read "done"), so — per *P4* of the authoring-repo-internal
[docs/design-north-star.md](../../../docs/design-north-star.md) — a passing `CLOSED` state and a deployment
readback are *claims*, not behavior proof. For **each** closed issue, the
reviewer must confirm the issue's user-facing behavior through an evidence
channel **distinct from** the bundle-level deployment readback and `CLOSED`
state — a provider/connector roundtrip, a behavior test, a fetch result, the
actual Slack/Notion/artifact observation — **or** record an explicit
non-`verified` disposition (the HOTL ledger statuses, plus
`local-only-by-contract` for a surface that is local by the resolution
contract; see `<repo-root>/skills/public/hotl/references/ledger-and-dispositions.md`).
A bundle readback (`restart_needed=false`, health `ok`) and a verified `CLOSED`
state only prove the bundle *deployed* and the tracker *closed*; they do not
prove a per-issue Slack / scheduled-workflow / public-artifact-URL /
Notion-byte / tracked-link / duplicate-workflow behavior. **Re-reading the
readback or the closeout evidence is not confirmation** — name, per issue, the
distinct channel consulted or the disposition that says the behavior was not
reached, into the bound review artifact. This is the facet a bundle closeout
silently skips: the reviewer reviews the proxy it was handed and rubber-stamps.
Deterministic teeth cannot make this honest — re-examination of the *same*
proxy is exactly what fails — so it is a rung-2 mandate, not a rung-1 floor.

## Delegated Reviewer Fast Path

If the current assignment says you are a bounded angle reviewer, counterweight
reviewer, or fresh-eye reviewer spawned by a parent, perform that assigned lens
directly and return the requested triage.
Do not run host capability checks or require nested spawn access.
Do not report blocked for missing nested subagents unless the parent asked for recursion.
Honor the repo's standing delegation grant — `<repo-root>/AGENTS.md` `Subagent Delegation`, else the structured record, else ask once (`fresh-eye-subagent-review.md`, *Where The Delegation Request Comes From*) — and consult that same reference before treating the canonical path as blocked. A repo with no `AGENTS.md` block has not refused; it has not been asked.
