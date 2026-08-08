# Achieve Goal: Carry the unbuilt slices: guard-shaped surfaces and the six filed issues

Status: draft
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-carry-the-unbuilt-slices-guards-and-the-six-filed-issues.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-08-carry-the-unbuilt-slices-guards-and-the-six-filed-issues.md` after confirming the draft is
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

Predecessor: `charness-artifacts/goals/2026-08-08-one-cadence-one-owner-stop-contradicting-the-agent.md`. It built and closed slices 1-3 of a nine-slice plan and closed EARLY rather than push six more slices through an exhausted session. This goal carries the remaining six, reshaped by what those three measured.

**What the predecessor established, and why it changes how these are built.**

1. **Every one of its three slices shipped a fix carrying the class it fixed, and round 2 caught all of them.** Slice 1 refused a goal while leaving `activation_ready: true` beside it (one fact, two owners — inside the slice about one fact having one owner). Slice 2's blocker fix silently dropped 25 in-repo `skills/support/` files (D9 again, in the file whose comment records D9). Slice 3's fix for `file.py:12` swallowed every SENTENCE-FINAL count, and widened trigger verbs while leaving removal labels behind. Round 2 is not optional on a verdict surface; budget it.

2. **The premise check was refuted or corrected on ALL THREE slices, at design time.** Slice 1's count was wrong in both directions (three artifacts, not five; one it named was not a contradiction, one it missed was). Slice 2's goal named the WRONG OWNER — the script it called "the precedent" was itself a hand-rolled copy. Slice 3's plan asked for a check where the answer was a shape. Verify the remedy's premise, and verify the OWNER the remedy names, before shaping.

3. **A duplicate-hash chase must not design a proof surface.** The dup ratchet was right the first time and caught a real defect. Chasing a later ROTATED hash is what routed two `complete`-state floors onto a level-aware section walk — a latent false green. Classify with a reason instead; the predecessor's `dup-review.json` entries carry the worked reasoning.

4. **Mutants are necessary and not sufficient.** 37 mutants were killed across three slices, and seven survived first. But none of round 2's blockers were mutation-findable — a reviewer found them by reading what the code would MEET, not what it was tested against.

**The remaining work**, renumbered from the predecessor's plan:

- The two lessons a gate cannot hold, written where the next session reads them (a substring pin cannot see an INVERSION; a test whose subject IS live repo state cannot be mutation-tested by editing the worktree). `recent-lessons.md` is GENERATED from retro artifacts via a selection index — this needs a retro artifact plus a refresh, not a hand edit.
- `#557` and `#559`: the fourth and fifth copies of the backend rule. `#559` had ALREADY drifted from the owner when it was filed.
- `#558`: `{repo}` is the unclosed half of an issue's identity; a wrong-repo CLOSED verdict is still reachable by reading.
- `#560` and `#561`: ready-path coverage and equality-versus-invariant pins, both deliberately deferred with reasons.
- `#556`: a check reachable only for a directory named `charness` — the same permanent-green class.
- Bundle proof and closeout.

**Two inherited obligations that are not slices.**

- **An OPERATOR DECISION blocks the bundle proof.** Three of twenty locators frozen by the `#514/#515/#518` source-freeze receipt are stale, changed by the predecessor's slices 2 and 3. Three tests are red. It was deliberately not re-stamped: `refreeze` would assert an inspection of files for issues neither goal owns. Both unblock paths are in the predecessor's `## Operator Decision Queue`. Resolve it BEFORE claiming any broad-suite green.
- **The section-locating walk is consolidated in seven call sites and NOT in seven others** inside the `achieve` package, including `slice_plan_data_row_count` in the very file that now hosts the owner. Recorded honestly in `dup-review.json` after a first draft overclaimed completeness and round 2 refuted it.

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
