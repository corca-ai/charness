# Achieve Goal: Make deliberate absence representable, starting with the adapter bootstrap that destroys it

Status: draft
Created: 2026-08-05
Activation: `/goal @charness-artifacts/goals/2026-08-05-make-deliberate-absence-representable.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-05-make-deliberate-absence-representable.md` after confirming the draft is
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

**The operator hit this from outside, in a real repo, and it is data loss.**
[#481](https://github.com/corca-ai/charness/issues/481): running `quality` in a
repo whose adapter had already been customized silently reverted it toward the
preset. 14 comment lines to 0, and deleted preset keys resurrected pointing at
`lefthook.yml`, `.github/workflows/*.yml`, and a coverage-exemption file that do
not exist in that repo. `SKILL.md` calls the bootstrap as standard procedure, so
a customized repo pays this on EVERY run.

The deleted comment had predicted the failure in its own words: *"declaring gates
that do not exist sends the next session hunting for them."*

**The class, read from the code rather than from the report.**
`bootstrap_quality_adapter` does merge — `gate_commands` survived — so this is not a
blind overwrite. It fails two other ways, and they compound:

1. **Deliberate absence is not representable.** `existing.get(field) or <default>`
   cannot distinguish "absent because never set" from "absent because the operator
   deliberately removed it". Every deletion is read as the first and refilled.
2. **The only record of the intent is destroyed in the same pass.** The adapter is
   re-serialized rather than round-tripped, so the comments explaining WHY a field
   was cut die — which is also the only thing that could have told the merge, or a
   later reader, that the absence was deliberate.

Measured population, 2026-08-03: **5 helpers in this repo write a
generated/bootstrapped surface over a hand-authorable one; 0 of the 5 preserve
comments.** `bootstrap_adapter.py` already HAS an existence guard and a
`--dry-run`, and the loss happened anyway — which is the finding: the guard
protects the FILE, and what was lost was the operator's INTENT inside it.

The outcome is that a repo can say "this gate deliberately does not exist here"
in a way a generator will not undo, and that a generator which cannot honor that
says so instead of silently reverting.

## Non-Goals

- **Not redesigning the adapter schema.** Adding the ONE field that makes a
  deliberate absence representable is in scope (decided 2026-08-03); changing what
  the other fields mean is not.
- **Not adding `ruamel.yaml`.** Decided: the rationale moves into data instead, so
  comment round-tripping stops being the property the fix depends on.
- **Not converting every generated surface to round-trip YAML.** Measure which of
  the 5 writers actually face hand-authored input first; a generator whose output
  nobody edits does not need comment preservation.
- **Not the unreachable-file residue.** #482/#483/#484 are filed with their
  rulers and are a separate goal; only pick one up if this goal finishes early.
- **Not #468's deferred-remedy pattern**, though it is adjacent: the destroyed
  comment WAS a durable record of a decision. Recorded as a connection, not scope.
- Not the E-cluster, not D41—D49.

## Boundaries

- **External side-effect scope.** Issue CREATION is standing per `AGENTS.md`.
  `git push` is standing CONDITIONAL ON THE GATES — a refusing gate withdraws it,
  and never weaken one to reach a green push. Closing #481 is standing CONDITIONAL
  ON THE CLOSEOUT FLOOR; it is the operator's own report, so the behavioural
  verdict should reach THEIR repo, not only this one.
- In scope: `quality_bootstrap_lib.py`'s merge and serialization, the 4 sibling
  writers, the adapter's own vocabulary for expressing a deliberate absence, and
  the `plugins/` mirror of anything touched.
- Stop conditions: (1) if honoring deletion requires a schema migration that
  invalidates existing consumer adapters, stop and treat it as a design decision
  for the operator; (2) if the data-field approach turns out to need `ruamel.yaml` after all, STOP and
  re-ask — the operator rejected that dependency, so discovering it is
  unavoidable is a design change rather than an implementation detail; (3) if the fix
  starts changing what the adapter MEANS rather than how it is written, stop.
- **Cut order if short: D, then C.** A and B are the report; without them nothing
  is fixed for the person who filed it.

## User Acceptance

- **The reported loss cannot recur**, proven by replaying the operator's exact
  reproduction: a customized adapter with comments and deleted preset keys, run
  through the bootstrap, compared before/after. The 14-to-0 comment loss and the
  3 resurrected nonexistent-path keys are the two observables.
- **A deliberate absence is expressible as DATA**, and an adapter written before
  the field existed keeps working unchanged — back-compat is a criterion, not a
  hope, because every consumer adapter in the wild predates it.
- **The rationale survives a regeneration**, proven by running the bootstrap twice
  over an adapter carrying the field and diffing.
- **A generator that cannot honor an existing customization SAYS SO** rather than
  reverting silently. Refusing is an acceptable answer; refusing quietly is not.
- **The other 4 writers carry a decision**, each either fixed or recorded with a
  reason a reader can tell from an omission.
- **Every figure carries `<value> — <source>`**, with its denominator and date.
- **Non-claim in writing**: a fix verified in THIS repo's fixtures is not verified
  in the operator's repo. Name which channel reached which tree.

## Agent Verification Plan

### Low-Cost Checks

- **Replay the operator's reproduction FIRST**, before designing: their commands
  are in #481 and they confirmed it reproduces twice. A fix designed before the
  observation is a fix for the report, not for the behaviour.
- **Separate the two mechanisms.** Comment loss and key resurrection have
  different causes and could be fixed independently; a single test that only
  proves "the file did not change" would hide one of them.
- Re-measure the 5-writer population with the ruler stated; the first grep in this
  design said 52 and was wrong because most of those never write.
- Sync `plugins/` mirrors before validators; obey the dup-ratchet edit advisory.

### High-Confidence Checks

- **TWO bounded rounds for any slice that changes verdict or merge logic**, round 2
  reading the repairs. Measured seven times now; in the previous goal the round-2
  repairs themselves carried the class twice.
- **A new or changed rule must be proven to BITE** by reintroducing the real
  defect — here, the operator's own before/after adapter.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify` the
  moment the reviewer returns, before any parent write.
- A closeout-claims review by a distinct observer before the completion flip.

### External Or Live Proof

- `git push` to `main` and its CI — standing, conditional on the gates. Remote CI
  confirmed by a different observer AND a different channel than the push exit
  code; the combined-status API reads `pending`/`total_count: 0` here because this
  repo publishes check-runs, which is not a pending check.
- **The behavioural verdict for #481 should reach the operator's repo**, since
  that is where the loss was observed. If it cannot, record the disposition rather
  than substituting this repo's fixtures for it.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Replay #481's reproduction and separate the two mechanisms | A fix designed before the observation is a fix for the report; and the two causes could each be fixed while the other still bites | A before/after diff reproducing 14->0 comments and the 3 resurrected keys, with each attributed to its mechanism | pending |
| B | Make a deliberate absence representable, and make the merge honor it | `existing.get(f) or default` cannot see a deletion; until it can, every other fix is cosmetic | The operator's deleted keys stay deleted across a bootstrap run, proven on their fixture | pending |
| C | Move the rationale into the same data field, and keep an older adapter loading | The comment was the only record of WHY a field was cut, and it lives in the one place a re-serializer cannot keep; data survives, and no dependency is added | Rationale survives a double bootstrap run; an adapter WITHOUT the new field loads and behaves exactly as before | pending |
| D | Decide the other 4 writers | One fixed instance and three unexamined siblings is how a class comes back | Each of the 4 fixed or recorded with a reason | pending |
| E | Closeout: bundle gate, claims review by a distinct observer, retro, #481 closeout floor, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest number; `check_goal_artifact.py` green; #481 closed through its floor or explicitly deferred | pending |

## Operator Decision Queue
Both activation decisions were RESOLVED by the operator on 2026-08-03 and are
folded into `## Interview Decisions`; what remains here is the one obligation
that outlives this goal.

- Decision: re-run #481's reproduction in the operator's own repo and confirm
  the loss is gone
- Owner: operator
- Why deferred: this session cannot see that tree. The close is carried by a
  fixture RECONSTRUCTED from the before/after posted on #481, which is evidence
  about the report and not about the reporter's repo — the closeout must say so
  in those words rather than letting a reconstruction read as a live verdict.
- Unblock action: after the fix ships, run the three commands from #481 in that
  repo and compare; a clean diff closes this, a dirty one reopens #481
- Revisit trigger: the next `quality` run in that repo. Recorded in TWO places on
  purpose — here and as a comment on #481 at close time — because a deferred
  confirmation kept in one place has evaporated more than once in this repo.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  boundary, and record the route it returns. At completion, recorded
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

## Discuss Before Activation

- Discuss before activation: RESOLVED at design time. No release surface, no
  live/prod proof, no broad scope. The two consequential calls are recorded as
  Interview Decisions 2 (a possible `ruamel.yaml` dependency — default is to
  refuse rather than add it) and 3 (the behavioural verdict cannot reach the
  operator's repo from here, so it is a reconstruction and says so). Closing #481
  is standing conditional on the closeout floor. The proof-level non-claim is in
  `## User Acceptance`.
- **This goal is ready to run.**

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [issue #481](https://github.com/corca-ai/charness/issues/481) — the operator's
   own report from an external repo, with the reproduction, the before/after
   table, and the deleted comment that predicted the failure. Read this first.
2. [quality_bootstrap_lib.py](../../scripts/quality_bootstrap_lib.py) — the merge
   is real (`preserved`/`augmented` statuses); the two failures are the
   `or <default>` refill and the re-serialization. Read the code before the fix.
3. [design-north-star.md](../../docs/design-north-star.md) — P4 governs this: a
   generator's success is a claim, and "the file was written" is not "the operator's
   intent survived".
4. [the closed #479](https://github.com/corca-ai/charness/issues/479) and its
   [resolution critique](../critique/2026-08-03-issue-479-resolution-critique.md)
   — the denominator discipline, and the worked example of a critique refusing a
   close because the record misstated its own ruler.
5. [recent-lessons.md](../retro/recent-lessons.md) — repeat traps that should
   change the next move.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

1. **What is the unit of the fix — the quality adapter, or the class?** Family
   considered: {fix #481 only; fix the 5 writers; fix the concept of a generated
   surface}. **Chosen: fix #481 fully, then DECIDE the other 4 with a recorded
   reason.** One fixed instance and three unexamined siblings is exactly how a
   class returns; but a blanket refactor of 5 writers before one is understood
   inverts the order. Anti-anchoring: `axis: a class is found by fixing one
   instance carefully, not by touching five quickly`.
2. **Comment preservation, or refusal?** Family considered: {round-trip YAML via
   `ruamel.yaml`; refuse to rewrite an existing adapter; move the rationale into a
   DATA field; write a sidecar; accept the loss}. **Chosen by the operator
   2026-08-03: move the rationale into a data field (`deliberately_absent`), and
   add no dependency.**

   Two observations settled it and neither was in the original framing. First,
   **the operator does not hand-edit adapters** — so "refuse and print the diff"
   pushes the merge onto whoever called the tool, which is the tool's own job.
   Their words: *"refusing means the repo has to work it out itself, right?"*
   Second, **the lost comment reads as agent-authored** (*"the bootstrap applied
   the typescript-quality preset, but this repo uses neither..."* is written by
   whoever watched the bootstrap run), so the adapter is a record agents write and
   agents read — and a rationale agents write need not be a COMMENT at all.

   Moving it into data resolves three things at once: the merge can finally SEE a
   deletion (there is a field to look at), the rationale survives
   re-serialization, and no dependency is added. Comments still vanish, but they
   stop being load-bearing — losing one no longer produces a false signal.
   Rejected `ruamel.yaml`: a supply-chain addition in a repo that gates on supply
   chain, for a formatting property the data field makes non-essential; and
   round-trip MERGE carries its own unresolved question about where a comment
   attached to a nested node should follow. Anti-anchoring: `axis: if the only
   reader is a machine, the rationale does not belong in the one place machines
   cannot read`.
3. **Should the verdict reach the operator's repo?** Family considered: {this
   repo's fixtures only; block the close on an operator re-run; reconstruct from
   the posted before/after; reconstruct now and re-run later}. **Chosen by the
   operator 2026-08-03: reconstruct from the posted before/after and close, with
   the re-run recorded as a revisit.** The loss was observed in a tree this
   session cannot see, so the reconstruction is evidence about the REPORT and not
   about the reporter's tree, and the closeout must say exactly that. Because
   "confirm it later" has evaporated more than once here, the revisit is recorded
   in TWO durable places — a comment on #481 at close time AND this goal's
   Operator Decision Queue — rather than in prose. Anti-anchoring: `axis: a
   deferred confirmation that lives in one place is one that will be lost`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

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
