# Achieve Goal: Decide where a recurring judgment-bound lesson lives, and stop verdict surfaces losing their own evidence

Status: active
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md`

This file is the living goal scratchpad for the active run.

## Active Operating Frame

- Current slice: Slice B — build the reviewer-packet control selected for #499 and #491.
- Current slice intent: implement the reviewer question that names the invariant/claim, its
  owning boundary, a recorded instance, and an axis-varying counterexample; Slice A's selector
  and six-issue ledger are complete. Once active, this names the reviewable-intent unit in
  progress and the commits it spans; critique and broad proof do not re-fire within one
  unchanged intent — update it when the intent changes, not per commit (meaningful-slice-cadence).
- Next action: inspect the reviewer-packet producer and its consumers, then implement the
  smallest portable question and prove it bites against a #499 or #491 record.
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

Six issue findings, two questions, one axis.

**Question A — where does a recurring judgment-bound lesson live?** A gate, a reviewer question, or a recorded exemption. This repo has measured that a gate which cries wolf gets walked past, and Floor-Addition Restraint already says an advisory is the default until a recurrence is RECORDED.

- [#499](https://github.com/corca-ai/charness/issues/499) — a guard written against the OBSERVED FAILURE's shape instead of the invariant. Five instances in one session across three surfaces; it was the round-2 blocker on every slice, twice the wrong predicate was the repair of a previous wrong predicate, and the last one was caught by a RELEASE critique after two code rounds passed it. GitHub currently records this issue as CLOSED; it remains the recorded recurrence that tests the policy.
- [#491](https://github.com/corca-ai/charness/issues/491) — a shipped reference disagreeing with the code. Same axis, deliberately deferred so it would get its own shaping.
- [#500](https://github.com/corca-ai/charness/issues/500) — the second goal-artifact CREATOR gets none of the first one's value guards. The concrete case that TESTS whichever answer wins.

**Question B — why does a verdict surface keep losing the one fact its reader needs?** The operator named this after watching it twice in one session, and it is the same reasoning failure one layer out: a surface optimised for the observable (output length, a count) rather than for what the reader must act on.

- [#502](https://github.com/corca-ai/charness/issues/502) — `run-quality.sh`'s summary format has 17 hand-written consumers and no owner, so changing it is indistinguishable from sanding tests to match code.
- [#501](https://github.com/corca-ai/charness/issues/501) — `check_export_safe_imports` scans import STATEMENTS, so a module path passed as a string is invisible. That is how #497 shipped past the gate whose whole purpose is to catch it.
- [#497](https://github.com/corca-ai/charness/issues/497) — the instance: a module that cannot be imported at all in the exported plugin.

**Why these are one goal and not two.** Question B is Question A's evidence. The truncation waste was fixed by making the SURFACE carry what the reader needs — not by a gate, not by a reviewer question, and not by a lesson. That is a third answer to Question A that no one had proposed, and it worked, measurably, on the first run after it landed. Slice A gets to weigh three candidate answers with a live worked example instead of two abstractions.

The outcome is a RECORDED DECISION with its reasoning, each of the six issues dispositioned under it, and whatever that decision implies actually built and proven to bite.

## Non-Goals

- **Not re-litigating the five #499 instances.** They are repaired and committed. The
  open question is what catches the sixth.
- **Not a new blocking gate by default.** Floor-Addition Restraint says an advisory is
  the default until a recurrence is RECORDED, and a gate that guesses at a
  judgment-bound property cries wolf. #499 has a recorded recurrence; #491 may not.
  Decide per issue, not once for both.
- **Not #496.** The hollow-refill predicate is its own question and turns on nothing
  here.
- **Not a rewrite of the 17 existing summary-format assertions** as an end in itself.
  #502 asks who OWNS the format; mass-editing its consumers without settling that is
  the motion the issue was filed about.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- **One recorded decision covers #499 and #491**, with its reasoning, and each of the
  six issues is dispositioned under it. Two separate answers to one axis is the failure
  this goal exists to prevent.
- **The decision weighs THREE candidate answers, not two** — gate, reviewer question,
  and *fix the surface so the lesson is unnecessary* — because the third one already
  has a measured worked example in this repo (see `## Context Sources`).

## Agent Verification Plan

### Low-Cost Checks

- **Read the five #499 instances and the truncation fix before designing.** The issue
  tabulates the first; commit `aea9cd99` is the second. A remedy designed without
  reading what it must catch is the class it is trying to fix.
- **Never pipe a gate through `tail`/`head`** — redirect and grep. Both gates now name
  their failures in the last line, but that rule is why.
- Sync `plugins/` mirrors before validators; obey the dup-ratchet edit advisory.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.
- **Run the broad suite per slice.** On 2026-08-07 it caught three defects that the
  slice gate AND both bounded rounds passed.

### High-Confidence Checks

- **TWO bounded rounds for anything rendering a verdict**; ONE for a reviewer question
  or a prose contract.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify` the moment
  the reviewer returns, before any parent write.
- **A closeout claims review by a distinct observer before the completion flip.** The
  last one found eight false figures; budget a real round.
- **A release critique if this goal touches a release surface.** On 2026-08-07 the
  release critique caught a breaking change two code rounds had passed.

### External Or Live Proof

- `git push` to `main` and its CI — standing, conditional on the gates. Confirmed by a
  different observer AND channel than the push exit code, via the check-runs API.
- `--produce-mutation-coverage` requires `--verification-lock` and the FULL broad run;
  with `--skip-broad-pytest` it silently produces nothing and reports `blocked` without
  saying why.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Decide the axis for #499 + #491, weighing all three candidate answers, and record it with its reasoning | Both ask one question, and a third answer now has a measured worked example rather than being hypothetical | One durable selector, six-row disposition/proof matrix, and measured basis for each candidate | completed |
| B | Build what slice A chose, proven to bite against a recorded instance | A remedy that would not have caught any of the five is theatre | The chosen control surfaces or refuses a real recorded instance; if a gate, also passes the tree with false-fire cost measured | pending |
| C | Give #502's summary format an owner, or record why it should not have one | It is the cheapest live instance of "a verdict surface with many consumers and no definition", and it is where slice A's answer gets stress-tested | Changing the format is one edit plus one test, or a recorded decision that the 17 consumers are correct as they are | pending |
| D | Disposition #500, #501, #497 under slice A's answer | They are the concrete cases that show whether the answer is usable on real code | Each either fixed under the chosen shape, or carrying a recorded exemption with its reasoning | pending |
| E | Closeout: bundle gate, claims review, retro, issue closeouts, commit | Repo contract treats critique, closeout and commit as task-completing work | `--verification-lock` green with an explicit pytest number; each close through its floor | pending |

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

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`
- Routing: critique — decision premortem for Slice A; three named lenses plus a separate counterweight reviewed the selector before it was locked.
- Gather: charness-artifacts/gather/2026-08-04-goal-issue-sources.md — authenticated `gh` capture of the six named GitHub issue records; the public URL route was attempted first and blocked by captcha.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED at shaping time. The one consequential decision
  is whether this goal may ADD A BLOCKING GATE, and it is deliberately deferred to
  slice A rather than pre-decided — that IS the goal. `## Boundaries` records that a
  gate is not the default and needs a recorded recurrence. No release surface, no
  live/prod proof, no irreversible side effect beyond the three standing approvals in
  `AGENTS.md`.
- The proof-level non-claim, folded into `## User Acceptance`: **a control that cannot
  be shown to catch a RECORDED instance is not proven**, whichever of the three shapes
  it takes. Passing on a clean tree establishes nothing — this repo's P4.
- **This goal is ready to run.**

## Slice Log

### Slice 1: Select the evidence-carrying control

- Objective: Lock one recorded selector policy for #499 and #491 across gate, reviewer question, and surface fix, then disposition all six issue records under that policy.
- Why this approach: The two issues share the proxy-for-invariant failure axis but do not necessarily share a mechanism; the truncation repair supplies a measured third candidate without proving it universal.
- Commits: none — Slice A changed the active goal artifact and gathered evidence only; implementation remains in Slices B–D.
- What changed: Selector: name the semantic fact and reader/control; choose a surface fix when the surface can carry and prove that fact, a reviewer question when the fact is judgment-bound, and a gate only for an observable predicate with recorded escape and measured false-fire cost. #499 CLOSED → reviewer question; #491 OPEN → reviewer question; #500 OPEN → shared creator/value surface; #502 OPEN → owned or structured verdict surface, architecture deferred to C; #501 OPEN → helper-aware import-path surface; #497 OPEN → exported-layout importability surface.
- Alternatives rejected: Rejected a semantic blocking/meta-gate because it would encode another proxy and violate P1/P5; rejected one universal mechanism because the six records have different owners; rejected a blanket surface-fix mandate because the truncation commits are a worked example, not a theorem. Deferred #502 renderer versus structured sibling to Slice C.
- Targeted verification: Read current GitHub issue JSON through the gathered record; confirmed #499 CLOSED and #491/#500/#501/#502/#497 OPEN. Read aea9cd99, a26bac92, the five #499 instances in the prior goal/retro, design-north-star.md, implementation-discipline.md, and recent-lessons.md. check_goal_artifact.py will verify the repaired artifact after this append.
- Test duplication pressure: n/a — no tests were added or expanded in this decision/artifact slice.
- Critique: Three named decision lenses plus one separate counterweight returned findings; all four shared the packet and were verified with clean reviewer-boundary fingerprints before parent writes. The full triage and packet hashes are in Plan Critique Findings.
- Off-goal findings: none — #496 remains explicitly out of scope; no new issue was filed.
- Lessons carried forward: A common policy may select different mechanisms per issue. A surface fix is preferred only when it can carry the semantic fact; a reviewer question must require an invariant, owner, recorded instance, and an axis-varying counterexample rather than a ritual reminder.
- Metrics: Host token/time/tool metrics unavailable; measured review count is 3 angle reviewers plus 1 counterweight, with 4 clean boundary verifications.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [design-north-star.md](../../docs/design-north-star.md) — the governing standard for where
   teeth belong, where judgment should remain, and which proof-surface changes are irreversible.
2. **Commits `aea9cd99` and `a26bac92`** — the worked example where a verdict surface was made
   to carry failing names and only backed log paths, paying for itself on the first rerun.
3. [gathered GitHub issue record](../gather/2026-08-04-goal-issue-sources.md) — captured primary
   bodies, current states, timestamps, and candidate directions for #499, #491, #500, #502,
   #501, and #497; the record preserves the six canonical issue URLs.
4. [the 2026-08-07 goal](2026-08-07-finish-the-sweeps-this-run-left.md) and [its retro](../retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md) — the five recorded #499 instances and the failure signature that led to this goal.
5. [the 3.1.1 release critique](../critique/2026-08-07-release-3.1.1-critique.md) — the review that caught the truncation repair reintroducing its own evidence-loss class.
6. [implementation-discipline.md](../../docs/conventions/implementation-discipline.md) — especially `## Floor-Addition Restraint` and change-discipline premise checks.
7. [recent lessons](../retro/recent-lessons.md) — recurring traps that the selector must not repeat.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

1. **What is the unit?** Family considered: {#499 alone; #499+#491; #499+#491 plus the
   verdict-surface cluster; the whole open backlog}. **Chosen: #499+#491 plus the
   verdict-surface cluster (#502/#501/#497), with #500 as the test case.** The operator
   asked for the truncation-waste improvement to join this goal, and it belongs: it is
   not a sixth item, it is the WORKED EXAMPLE of a third answer to the goal's central
   question. Anti-anchoring: `axis: adding an item to a goal is scope creep UNLESS it
   changes what the goal can conclude` — checked, and it does.
2. **Should the remedy be pre-decided?** Family considered: {pre-decide a gate;
   pre-decide a reviewer question; pre-decide the surface fix; leave it to slice A}.
   **Chosen: leave it to slice A.** Pre-deciding makes this an implementation ticket.
   The surface fix having worked once is evidence, not a conclusion — it worked for a
   waste with a cheap surface to fix, and #499's class may not have one. Anti-anchoring:
   `axis: one success is a data point, not a policy`.
3. **How is a non-code answer proven?** Family considered: {ship and trust; prove it
   catches a recorded instance; require a live re-run}. **Chosen: prove against a
   RECORDED instance.** A reviewer question is not pytest-testable but is falsifiable.
   Anti-anchoring: `axis: "not automatable" is not the same as "not provable"`.

## Plan Critique Findings

Blockers folded into the Slice A decision and active frame; over-worry raised but
not folded; reviewer provenance preserved so a fresh session can re-verify the
folded revisions without re-running critique.

- **Selector locked:** name the semantic fact/invariant and its reader or control;
  first ask whether a source/verdict surface can carry or derive that fact and prove
  a recorded instance; if yes, fix that surface; if the fact remains judgment-bound,
  require a reviewer-packet question; use a gate only for a mechanically observable
  predicate with a recorded escape, measured false-fire cost, and Floor-Addition
  Restraint. The selector chooses per issue; it is one policy, not one universal
  mechanism.
- **#499 and #491:** both select the reviewer-packet branch for Slice B. #499's
  "right boundary" is semantic and a detector would be another proxy; #491's
  current inventory has no `reference-claims` or claims-manifest surface, while the
  review-owned shape already caught all three recorded mismatches. The surface-fix
  branch remains selected for the concrete verdict/creator/export cases where the
  surface can carry the missing fact.
- **Six-row proof ledger:** #499 (CLOSED, five recorded instances) — reviewer question,
  prove against one instance plus an axis-varying counterexample; #491 (OPEN, three
  recorded mismatches) — reviewer question, name the claim, owner, and changed behavior;
  #500 (OPEN) — surface fix at the shared creator/value boundary, with an explicit
  exemption only if premise checks prove no shared contract; #502 (OPEN) — surface fix
  for an owned/structured verdict output, exact renderer architecture deferred to Slice C;
  #501 (OPEN) — surface fix for helper-supplied module-path semantics; #497 (OPEN) —
  surface fix for exported-layout importability. Slices B–D owe the recorded-instance
  proof for each selected branch.
- **Rejected:** a semantic blocking gate or meta-gate for "correct reasoning" would
  encode another proxy and contradict P1/P5; a blanket reviewer question would leave
  machine-observable evidence-loss and export failures unfixed; a blanket surface-fix
  mandate over-generalizes the truncation worked example. #502's renderer-versus-
  structured choice is valid but deferred to its own consumer-inventory slice.
- **Fresh-eye review:** parent-delegated high-leverage decision critique with three
  named lenses and one separate counterweight; all four findings were received and
  each boundary fingerprint verified `verdict: clean` before parent writes. Packet
  JSON: `charness-artifacts/critique/2026-08-03-211703-packet.json`, SHA-256
  `8bb22a4dea80a1540e489ad2059b130d1e6bba4de2b4bef4b1f2315d370a40a1`; reviewer
  markdown consumed: `charness-artifacts/critique/2026-08-03-211703-packet.md`,
  SHA-256 `a5ccbc7413e293b37a1cfb7ad8e220e8156a0881776355be1453f6edc7e472b0`;
  reviewed-input identity `eab5f4d09d3ff4509d30542b05cfabfb4259ebfd517c1483c96ac61117b55722`;
  requested spawn fields were `gpt-5.6-terra`, medium, priority; application was
  not independently confirmed by the host.

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
