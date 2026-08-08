# Achieve Goal: Close the gap between a repair and its caller, with the tool that proves it

Status: draft
Created: 2026-08-10
Activation: `/goal @charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-10-close-the-gap-between-a-repair-and-its-caller.md` after confirming the draft is
  still intended.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

**NARROWED after a 7-day value audit — read this before shaping.** This draft was
designed at its predecessor's closeout and is no longer the default pickup
(`docs/handoff.md` points elsewhere). Two of its three planned items did not
survive:

- The SWEEP is CUT. Its scope was unbounded and its only product was more internal
  test coverage.
- `#564` (add a step to the goal template's verification plan) is rulebook growth
  and was reconsidered on P3 grounds — prefer letting `#565`'s tool ask the
  question over writing another rule.
- `#565` SURVIVES and was re-confirmed live during the audit: the same zsh
  word-split defect recurred in a command that was verifying an audit charge, an
  hour after being filed. It is small.

The audit also refuted the premise that this repo has been over-investing in its
own machinery — see `docs/handoff.md` `## Workflow Trigger` for which four charges
broke and how to re-measure them. So do NOT shape this as a bloat-reduction goal.
If `#565` is worth doing, it is a cleanup item, not a goal. The audit's durable
instruction was to choose consumer-facing work next.

## Goal (as originally drafted)

Predecessor: `charness-artifacts/goals/2026-08-09-close-the-copies-this-run-measured.md`. It reached all three planned slices, closed and verified `#562`, put `#561` to its owner with both costs measured, and built `#560`'s ready-by-construction fixture. This goal is designed from what it MEASURED, not from what it left over.

**The one finding that repeated in every slice, and is the reason this goal exists.**

Three times — once per slice — a repair was pinned by a test that called the repaired function DIRECTLY, and deleting the repair's CALL SITE left the whole suite green. `stamp_inspection`'s existence check, the residual drift message's exit-code assertion (the only assertion a stub artifact actually reaches, because the script exits 1 first), and the bundle fixture's re-stamp call. None was visible to careful reading of the diff; each was found by one mechanical mutation. That is a different defect from the predecessor's measured "a repair inherits HALVES": those were partial rules, these were WHOLE rules with no live caller-side proof, and a second review round does not reliably catch them because the code reads correctly.

Filed as `#564`. This goal's first slice is to make the affordance rather than remember the rule.

**The second finding, and it is about the tooling that finds the first.**

The predecessor hand-authored three inline mutation harnesses. One reported NINE FALSE KILLS: `python3 -m pytest -q $T` with two space-separated paths in `T`, which zsh does not word-split, so pytest received one nonexistent path, exited non-zero, and every mutant read as `killed`. Re-run correctly, three of nine had SURVIVED. A green mutant sweep is a verdict about other code, so a sweep that cannot fail is the same shape as a gate that cannot fail — and this one was silent in the direction that matters.

Filed as `#565`. The fix is small and its two load-bearing properties are known: refuse to report a kill unless the unmutated baseline first reported a PASSING TEST COUNT, and restore even when the test command raises.

**What this goal deliberately does NOT re-derive.** The two-round rule for verdict-logic slices is now measured on two independent goals — eighteen blockers across ten rounds, then thirty-two findings across four — with the same property both times: every blocker was in a REPAIR, never in a first diagnosis. It is settled and lives in `recent-lessons.md`. Plan the second round as a cost; do not re-measure it.

**The remaining work, in the order the measurement suggests.**

- `#565` first, because it is the TOOL: a repo-owned mutate-and-restore helper with a baseline assertion. Every later slice's proof depends on it, and building it second would mean proving the other slices with the harness this goal exists to replace.
- `#564` second, using that helper: make "at least one mutant per repair deletes the CALL SITE rather than the body" a step in the goal template's `## Agent Verification Plan`. This is a prompt-surface change, so it owes the retro-lessons read and two delegated rounds.
- A SWEEP with the new helper over repairs already shipped, to find the instances nobody mutated. Three were found in one goal purely because that goal happened to mutate them; the population is unmeasured and that is the honest reason to look.

**Two operator decisions inherited, and neither is this goal's to take.** `#561`'s equality-versus-invariant pin choice belongs to D47's owner, with both costs already measured and recorded. `#547`'s literal subject was deleted by the predecessor's slice 1 while its generalized form was WIDENED by it — `refreeze` now silently re-stamps the locator set and the artifact's prose, and `stamp_inspection` still reports no diff of what moved. Both sit in the predecessor's `## Operator Decision Queue`; carry them forward unresolved rather than adopting them.

**One finding filed rather than fixed, and it is a real candidate for this goal.** The owner inspection's per-locator `issue` attribution is still outside `inspection_identity` — the artifact asserts "the surface was inspected while scoping that issue" and nothing binds it, so an attribution flip passes with every identity unchanged. It is the round-2 blocker's own shape half-repaired: the prose was pulled inside the identity and the structured claim beside it was left out. Small, and it closes the class rather than another instance.

## Non-Goals

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

What the user can do to verify completion directly — the OUTCOMES, not the
verification cadence. Whichever line of `## Active Operating Frame` states when
broad or expensive proof runs (`Gate cadence:` in the charness default frame; a
consumer adapter may seed its own) is the one owner of that answer. Restating it
here creates a second owner, and an agent reading its own acceptance criteria
obeys the acceptance criteria: one measured session paid roughly two and a half
hours re-running a 12-minute suite that way. Name what is true when the goal is
done, and point at `## Active Operating Frame` for when it is proven.

## Agent Verification Plan

### Low-Cost Checks

### High-Confidence Checks

### External Or Live Proof

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |

## Backlog Recount

Recount the tracker before scope; see `references/lifecycle-before.md`.

- Counted: To be filled by the achieve Before-phase
- Claims: To be filled by the achieve Before-phase
- Not claimed: To be filled by the achieve Before-phase

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

Queue item form:

- Decision: operator-only decision or confirmation needed
- Owner: operator or named human owner
- Why deferred: why the run did not stop immediately
- Unblock action: exact action or answer needed
- Revisit trigger: event, date, or proof boundary that reopens this

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.
- **Successor goal step** — required at EVERY completion, not conditionally. Add
  a `Successor goal:` line naming the next goal artifact this run's lessons
  designed, or write `Successor goal: n/a — <reason>` to say out loud that none
  is wanted. The closing goal is the only place that still holds what the session
  measured about this repo's real shape; a completion that does not spend it
  throws that away, and the next session re-derives it.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: fill — replace with resolved, confirmed, or approved, then the consequential activation decision and how it was settled

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. TODO the repo's governing design standard, and what it says about THIS goal —
   which facets bear on its boundaries, where its teeth belong, and which
   irreversible boundaries it crosses. Read it while SHAPING, not at closeout:
   the standard is what tells you where a wrong answer escapes, and that is a
   Before-phase question. (The retro's `## North Star Alignment` asks the
   backward-looking half; this is the forward-looking one.)

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Closeout Binding Plan

Shape these minimum fields before activation and keep them current. The field
check proves shape only; closeout workflows prove the values and identities:

- Reviewed inputs: name semantic goal/issue/quality inputs; retro, packet, reviewer, and lock records are terminal evidence.
- Frozen target: commit the semantic baseline, then bind the packet to that exact commit SHA.
- Fresh-eye: name a distinct reviewer and a different observer/evidence channel.
- Verification lock: name the lock command and evidence location; semantic input edits require rebinding.
- Complete flip: record packet/reviewer/lock evidence, then write terminal status/evidence bookkeeping outside the reviewed identity.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
