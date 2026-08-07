# Achieve Goal: One rule, one owner; one check, its own voice

Status: draft
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-08-one-rule-one-owner-one-check-its-own-voice.md` after confirming the draft is
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

Two goals in a row have now found the same three mechanisms, and the harness
caught every instance through its EXPENSIVE channels — bounded review and the
broad gate. The mechanisms are cheap enough to check; the instances are spread
across surfaces nobody has connected. This goal connects them.

**One defect class, three faces.** A verdict surface asserts something it did not
establish. It shows up as:

1. **One rule, two owners.** The same rule is implemented twice, so a fix lands
   on one copy and the other keeps its old answer — or, worse, the two disagree
   and nothing notices. Fixed twice BY HAND in the predecessor (a sibling gate
   predicate; two goal-artifact producers), and the tracker already carries four
   more: `#548`, `#552`, `#555`, `#550`.

2. **A refusal that cannot say its own name.** A correct refusal surfaces as some
   unrelated symptom, so an operator debugs the symptom. `#537` was hit LIVE in
   the predecessor — an unmatched-surface blocker appeared as five broken bundle
   tests — and worked around without anyone noticing the issue existed. `#536`,
   `#549`, `#542` are the same shape.

3. **A label that reads as protection but establishes nothing.** The predecessor's
   subject, unfinished: `#518`, `#528`, `#546`, `#547`.

`#552` is the sharpest instance in the tracker: a checker requires a literal
token that the renderer writing the block never emits, so `charness_managed` is
permanently False and TWO AGENTS.md policy checks can never fire. A gate that
cannot fire is a permanent green.

The predecessor closed early at 2 of 7 slices so its remaining claims could be
re-homed here rather than run under a frame that did not name what they share.

## Non-Goals

- Do not build ONE generic "duplicate rule" detector before three real instances
  are repaired. A framework built ahead of its evidence is how a gate becomes a
  wolf-crier, and the predecessor measured that trade twice.
- Do not take the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`,
  `#525`, `#527`, `#531`, `#532`). It is a different question — measuring prompt
  efficacy — and the predecessor's record says mixing it in is how a goal stops
  being reviewable.
- Do not close `#530` on the gate alone. The resolver still emits the literal
  string in its title; that is an operator decision carried forward, not a
  closeout to infer.
- No release, tag, version bump, push, or Cautilus run unless separately granted.

## Boundaries

- **Premise check is a phase, not a step.** 5 for 5 across this goal family,
  INCLUDING where the premise held. Its largest save wired a skill to the wrong
  owner before a line was written.
- **A slice that changes verdict logic owes round-1 AND round-2 bounded review,
  and round 2 reads the REPAIRS.** Now 4 for 4: every measured slice shipped a
  fix carrying the class it fixed.
- **Assert a floor's REFUSAL through the composed verdict, never only through the
  module that computes it.** Three instances in the predecessor. This is the
  house failure mode.
- **When a finding says "this predicate is wrong", grep every caller before
  repairing one.** Hardening one of two sibling gates makes the other reachable.
- **No denominator in a rationale without the command that produced it.** Two
  wrong numbers shipped in one paragraph last run, both derived rather than
  measured.
- **Sync before verify, and run the gate AGGREGATE after the first rejection.**
  Two full-suite runs and four serial re-runs were burned on these two.
- **A `-k` filter is not the suite.** Run `./scripts/run-quality.sh --read-only`
  at every slice boundary; it caught what filtered runs missed three times.
- Bounded reviewers run read-only in the shared worktree, fingerprinted, and the
  window is CLOSED before the parent starts repairing.

## User Acceptance

- `#552`: a repo seeded by `charness setup` reads as charness-managed, and the
  two AGENTS.md policy checks that could never fire now can — proven by
  constructing a seeded repo and observing each check fire.
- `#548`: `write_artifact_path` means ONE thing, or the two producers name their
  meanings distinctly; no caller can write to the previous review's file believing
  it is a fresh target.
- `#555`: one tracker backend has one owner; `handoff` consumes `issue`'s rather
  than reimplementing it.
- `#550`: adapter resolver duplication is reduced or classified with a measured
  reason, not left as an unreviewed near-copy.
- `#537`: a correct bundle-preflight refusal reports ITSELF; it no longer appears
  as unrelated broken tests.
- `#536`, `#549`, `#542`: each failure names what it is and what it did not
  establish.
- `#518`, `#528`, `#546`, `#547`: no declared-but-unreached surface renders as
  clean; a repo can declare a sub-key ABSENT; a budgeted label with no sample
  stops reading as protection; a re-bind reports WHICH identities moved.
- `./scripts/run-quality.sh --read-only` exits 0 at EVERY slice boundary, and
  `pytest tests/ -q` reports zero failures.
- The Slice Log records the premise-check verdict BEFORE each build.

## Agent Verification Plan

### Low-Cost Checks

- `scripts/check_changed_surfaces.py` and the validators it names; root/plugin
  sync BEFORE validators; `check_python_lengths.py --headroom` before adding to a
  gated file; `check_dup_ratchet.py --summary` before writing the commit message.
- After ANY commit-gate rejection, run the aggregate (`run_slice_closeout.py`)
  rather than fixing one rejection at a time.
- Do not pipe a gate through `tail`; redirect and grep.

### High-Confidence Checks

- Mutation-check every new verdict path and report the count from a re-run.
  Include at least one mutant at the CALL SITE, not only inside the helper.
- For every repaired predicate, mutate each caller independently.
- Construct the refused input; never infer a refusal from a green suite.

### External Or Live Proof

- Remote CI is a non-claim unless separately observed, by a different observer
  AND channel than the push exit code.
- Consumer-repo product behavior remains a standing non-claim.

## Slice Plan

| Slice | Objective | Issues | Why HERE in the sequence | Status |
| --- | --- | --- | --- | --- |
| 1 | A checker requiring a token its renderer never emits — two policy checks that can never fire | #552 | Sharpest instance of the class, smallest surface, and a PERMANENT green today | planned |
| 2 | One key name meaning opposite things in two scaffolds | #548 | Same shape, and one branch can overwrite the previous review | planned |
| 3 | One tracker backend, one owner | #555 | Unblocks `#554` part 2; the duplicate was found by the predecessor's premise check | planned |
| 4 | A correct refusal that reports itself | #537 | Hit LIVE in the predecessor and worked around; also unblocks honest gate reads for later slices | planned |
| 5 | Failures that name what they did not establish | #536, #549, #542 | Cheaper once slice 4 has fixed the reporting seam | planned |
| 6 | Declared-but-unreached surfaces and absent sub-keys | #518, #528 | The predecessor's unfinished subject; largest surface, so it goes after the mechanisms are guarded | planned |
| 7 | Labels that read as protection | #546, #547 | Local, and slices 1-6 will have exercised them | planned |
| 8 | Resolver duplication | #550 | Cheapest last | planned |
| 9 | Bundle proof, goal closeout, successor | (none) | Composition can drop what each slice proved alone | planned |

## Backlog Recount

- Counted: 29 open issues on 2026-08-08 via `gh issue list --repo corca-ai/charness
  --state open`, then reconciled against this section by set-differencing the live
  numbers against the `Claims:`/`Not claimed:` lists parsed out of this very file —
  claimed + not-claimed = 29 exactly, no gaps, no already-closed entries. The
  reconciliation is a command, not an adjective: rerun it before reshaping scope.
- Claims: `#552`, `#548`, `#555`, `#550`, `#537`, `#536`, `#549`, `#542`, `#518`,
  `#528`, `#546`, `#547` — twelve issues sharing one defect class.
- Not claimed: the prompt-surface cluster (`#519`, `#520`, `#521`, `#523`, `#524`,
  `#525`, `#527`, `#531`, `#532`) — a different question, measuring prompt efficacy.
  `#514`/`#515` — consumer ownership, predating this line of work. `#539`, `#545` —
  provider/publication safety, unrelated to this class. `#530` and `#554` — carried
  forward with operator decisions recorded in THIS goal's Operator Decision Queue
  (the predecessor's queue carries only `#530`; a bounded round caught that
  mis-citation). `#535` — released for an operator decision, also queued below,
  because no goal has ever premise-checked it. `#534` — NOT claimed: a prior goal
  BUILT it green with seven passing tests, then REFUTED and REVERTED it, posted the
  refutation to the issue, and concluded it may not be worth building at all
  (`2026-08-07-close-every-open-issue-declaration-to-verdict.md`). Re-shaping a
  slice around the refuted framing is the Work Phase Map trap this goal's own
  Boundaries name; if `#534` returns it must be re-scoped from the refutation, not
  from the issue title.
- Overlap warning: `charness-artifacts/goals/2026-08-08-finish-the-declaration-to-verdict-sequence.md`
  is a LIVE draft that also claims `#518`. Two draft goals owning one issue is this
  goal's own subject at the artifact layer. Resolve the ownership before slice 6.

## Operator Decision Queue

- Decision: is the GATE the right surface for `#530`, or must the RESOLVER warn
  too? Owner: operator. Carried forward from the predecessor with its cost
  measurement (a 3.1s reader scan on every resolver invocation, including the 16
  subprocesses the gate itself spawns). Until resolved, `#530` stays open.
- Decision: is `#535` (identity-binding surfaces ship without a one-command
  re-bind) worth claiming at all? Owner: operator. Why deferred: it pairs with
  `#547`, which this goal DOES claim, but no goal has ever run a premise check on
  `#535` itself — it was carried between goal artifacts by inheritance. Unblock
  action: premise-check it, or say it is not wanted. Revisit trigger: slice 7
  (`#547`) discovering it cannot finish without the re-bind.
- Decision: does `#554` part 2 (an automated recount helper) ship once `#555`
  gives the tracker one owner? Owner: operator. Why deferred: the floor already
  makes the recount mandatory and visible; the helper is convenience, and its
  seam only becomes clean after slice 3.

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

CONFIRMED 2026-08-08 by explicit operator instruction in session: take the
structural class as the goal's center of gravity, go LARGER than the remaining
slices, and pull in the related open issues.

- RESOLVED — scope is the thirteen issues named in `## Backlog Recount`, chosen
  by defect class rather than by area.
- RESOLVED — the predecessor is closed EARLY at 2 of 7 by the same instruction,
  and its unfinished claims are re-homed here rather than run in parallel.
- RESOLVED — the prompt-surface cluster stays excluded; it is a measurement
  question, not a verdict question.
- RESOLVED — no push, release, tag, or Cautilus run is implied by activation.
  Each is per-request, and `#530`/`#554` closure awaits operator decisions.

## Slice Log

## Context Sources

1. `charness-artifacts/goals/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster.md`
   — the predecessor. Its Slice Log holds the measured instances of all three
   mechanisms and is this goal's evidence base.
2. `charness-artifacts/retro/2026-08-08-arm-the-verdict-and-close-the-false-green-cluster-retro.md`
   — the retro whose `## Sibling Search` named this goal's scope.
3. Live tracker recount 2026-08-08: 29 open issues, reconciled against this
   goal's claim split programmatically.
4. `#552`, `#548`, `#537` read in full during shaping to confirm the class rather
   than infer it from titles.

## Interview Decisions

- Ordered by SHARPNESS, not by issue number or size. `#552` goes first because a
  check that can never fire is a permanent green and its surface is small.
- Grouped by defect class rather than by owning skill. The predecessor's evidence
  is that these instances share a mechanism, so slices can share evidence and
  avoid repairing the same shape three times independently.
- `#535` is NOT claimed despite being in the predecessor's list: it pairs with
  `#547`, and the predecessor recorded no premise check for it. Left for a
  decision rather than inherited silently.
- A generic detector is deliberately NOT slice 1. Three real repairs come first;
  generalization is slice 9's question if the evidence supports it.

## Plan Critique Findings

- Corrected while drafting: the first shape put `#518` first because it is the
  predecessor's next numbered slice. That buries the mechanism work behind the
  largest surface in the goal, which is exactly how the predecessor stalled at
  2 of 7. Reshaped to put the sharp, small, permanent-green instance first.
- Open risk, not resolved: thirteen issues is large for one goal. Mitigation is
  the class grouping — if slices 1-3 do NOT share evidence as predicted, that
  refutes the grouping premise and the goal should be re-cut, not pushed through.
- Open risk, not resolved: `#518` has never been scoped by any goal that claimed
  it. Its premise check must run before any remedy is shaped, and the record is
  5 for 5 that the named remedy is wrong.
- Open risk, not resolved: the portable-gate generalization is parked at slice 9
  of 9, and the two preceding goals reached slices 2 and 2. On that record slice 9
  is the least likely slice to be reached. The deferral is defensible on
  wolf-crier grounds; its SCHEDULING is not, and if slices 1-4 make the mechanism
  obvious the generalization should be pulled forward rather than left last.
- Open risk, not resolved: `#528` and `#550` are the weakest members of the class.
  `#528` is a missing third state (declared/defaulted/absent), a capability gap
  rather than a false green; `#550`'s acceptance can be discharged by classifying
  duplication rather than repairing a verdict surface. The re-cut trigger above
  extends to them.
- Open risk, not resolved: repairing duplication (`#550`, `#555`) can itself
  create a shared surface that drifts. Any consolidation ships with a test that
  fails if the two consumers diverge again.

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
