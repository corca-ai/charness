# Achieve Goal: Repair the commands the skills tell agents to run

Status: draft
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md` after confirming the draft is
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

A shipped skill tells an agent to run a command. **13 of those commands cannot
run**, in this repo or any other: the reference says
`<repo-root>/scripts/<name>.py` while the file lives in
`skills/public/<skill>/scripts/<name>.py`. An agent that follows the instruction
literally gets "No such file or directory".

Measured 2026-08-02, statically, over every `.md` under `skills/public`,
`skills/shared`, `skills/support`:

| form | count | state |
| --- | --- | --- |
| `$SKILL_DIR/...` (inside the skill package) | 91 | **0 resolution failures** |
| `<repo-root>/scripts/X.py`, file actually in the skill package | **13** | **broken here AND everywhere** |
| `<repo-root>/scripts/X.py`, file is a charness repo script | 9 | resolves here, unresolved in a consuming repo |
| referenced file that exists nowhere | **0** | — |

Concentration: `announcement` 4, `quality` 3, `setup` 2, `narrative` 2,
`gather` 1, `retro`/others 1.

This is the same class as #471/#475/#476 — a rule that cannot fire where it was
written — but for the first time it is **statically decidable and already
counted**. No agent testimony, no host, no temp repo: the file is there or it is
not.

The 2026-08-02 sweep had this in its hands and let it go. Verifiers refuted the
"inert" claims by showing that `inventory-dispatch.md` dispatches the SAME
script via `$SKILL_DIR`, which proves a DIFFERENT path works — not the one the
document told the agent to run. Taking that refutation at face value is the
error this goal repairs.

## Non-Goals

- **Not building an installed-layout / temp-repo proof channel.** It was the
  previous draft's Lane A and the measurement made it unnecessary for THIS
  defect class: a static grep found all 13 in seconds, and a consumer repo would
  cost far more while telling us the same thing.
- **Not answering whether the 91 `$SKILL_DIR` scripts EXECUTE** in a repo with
  no adapter and no charness `scripts/`. Existence and executability are
  different claims. There is no evidence either way today; it is recorded as the
  named follow-up, not smuggled in.
- **Not rewriting how skills reference scripts.** `$SKILL_DIR` already works for
  91 references; the 13 are typos against that working convention, not a design
  problem.
- **Not arming a blocking gate on first sight.** Floor-Addition Restraint: this
  check is cheap and static, which makes a gate tempting — the call gets made
  explicitly in Lane C with the recurrence evidence, not assumed.
- Not the E-cluster, not D41–D49.

## Boundaries

- **External side-effect scope — APPROVED BY THE OPERATOR 2026-08-02, all three
  items, for this goal.** (1) `git push` to `main` plus the `quality-core` runs
  it triggers. (2) Filing issues for what Lane B cannot resolve. (3) Closing an
  issue a lane fully resolves — still through the close path's floor, with a
  DELEGATED resolution critique running BEFORE the close call; the approval
  covers the decision to close, never the evidence floor.
  The agent had recommended a narrower grant (push blanket, issues case-by-case,
  no closing this goal) on the grounds that issue creation is the one action
  GitHub cannot undo. The operator chose the wider grant; recorded so a later
  session reads this as a deliberate call rather than an unexamined default.
  **This approval is scoped to THIS goal and does not carry to the next one.**
  NOT in scope at all: a release publish, a tag, a version bump, or any
  `cautilus evaluate` run.
- In scope: the 13 broken command references, the 9 charness-script references,
  the shipped `plugins/charness/` mirror of every touched file, and regression
  tests.
- In scope (repairs): the 13 are unambiguous — the file exists, the path is
  wrong, and correcting it refuses nothing new. The 9 are NOT unambiguous and
  are a judgement call (Lane B).
- Stop conditions: (1) if correcting a reference changes what a skill DOES
  rather than where it points, stop and treat it as a design change. (2) If any
  repair would newly refuse a checked-in artifact or newly APPLY a floor to
  repos previously outside it, it becomes an operator decision (D49). (3) If
  Lane C starts growing past a single static check, cut it back to the
  measurement.
- **Cut order if short: C, then B, never A.** A is the counted defect.

## User Acceptance

- **Lane A**: all 13 references point at a path that resolves, verified by
  re-running the same static measurement that found them, with the count going
  13 → 0 and the denominator restated. A regression test asserts every
  `<repo-root>/scripts/X.py` and `$SKILL_DIR/...` reference in shipped skill
  surfaces resolves — so this cannot silently come back.
- **Lane B**: each of the 9 charness-script references carries a recorded
  disposition — `repointed` / `documented as authoring-repo-only` /
  `issue #N` — and the artifact says which, with the reason. A reader can tell
  a deliberate authoring-repo reference from an unnoticed one.
- **Lane C**: the advisory fires on a broken reference and is pinned by a test
  proving it can never change an exit code, plus a counted answer to "how did 13
  accumulate" — that count is the evidence a future blocking promotion needs,
  and its absence is why the gate was not taken now.
- **Every figure carries `<value> — <source>`**, and every count states its
  denominator AND when it was taken.
- **Non-claim carried in writing**: this proves the referenced paths RESOLVE. It
  does not prove the scripts run correctly in a consuming repo — that is the
  named follow-up.

## Agent Verification Plan

### Low-Cost Checks

- **Re-run the measurement before and after, and record WHEN.** The before-count
  is 13/91/9/0 taken 2026-08-02 after the previous goal's fold.
- **Distinguish `<repo-root>/` from `$SKILL_DIR/` in every query.** Conflating
  them produced a wrong 33/55 first count in the session that shaped this goal;
  the corrected split is 13/91/9/0. A measurement that cannot tell the two apart
  will report noise as signal.
- **A refutation that proves a DIFFERENT path works is not a refutation.** That
  is exactly how the 2026-08-02 sweep lost these 13.
- Targeted `pytest` AND `ruff check` in the same breath.
- Sync `plugins/` mirrors before validators (`mutate -> sync -> verify`).
- Obey the dup-ratchet edit advisory when it fires rather than deferring to the
  closeout aggregate.
- File the issue first, then write its number into prose.

### High-Confidence Checks

- One bounded fresh-eye round per slice; **TWO for Lane C if it wires a check
  that renders a verdict**, round 2 reading the REPAIRED surface.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify`
  the MOMENT the reviewer returns, before any parent write.
- **Adversarial verification defaulting to refuted on every Lane B disposition**
  — and this time, reject a refutation that merely names another working path.
- A closeout-claims review by a DISTINCT observer before the complete flip.
- **Build test inputs from source constants, never by retyping.**

### External Or Live Proof

- `git push` to `main` and the remote CI it triggers — **only after the approval
  in `## Boundaries` is granted** — confirmed per P4 by a different observer AND
  a different channel than the push exit code.
- Expect the pre-push changed-line mutation lane to refuse if new branches are
  added; cover them as they are written.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Repoint the 13 broken command references and pin them with a regression test over ALL shipped skill surfaces | 13 counted commands an agent is told to run and cannot; unambiguous, refuses nothing new, and the file already exists at the right place | Before/after count 13 → 0 from the same query, the test, synced mirrors | pending |
| B | Disposition the 9 charness-script references: repoint, document as authoring-repo-only, or file | They resolve here and not in a consuming repo, which is the #475 shape — but unlike the 13 they may be deliberate, so each needs a judgement recorded | A per-reference disposition table with reasons; issues for what is not resolved | pending |
| C | Wire the static path-resolution check as a NON-BLOCKING advisory (operator-decided 2026-08-02), count how the 13 accumulated, and record the recurrence evidence a later gate decision would need | An advisory is the restraint checklist's default on a first finding; the recurrence count is what a blocking promotion requires and nobody has taken it | The advisory firing on a broken reference, a test pinning it cannot change an exit code, the accumulation count with its method, and the deferred gate call written down | pending |
| D | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green | pending |

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

- Discuss before activation: RESOLVED — both activation items settled by the
  operator in-transcript on 2026-08-02, and this goal is ready to run.
  (1) APPROVED — external side effects: `git push` to `main` plus the CI it
  triggers, filing new issues, and closing an issue a lane resolves are all
  approved for this goal by the operator, who chose a wider grant than the agent
  recommended. Closes still run through the close path's floor with a delegated
  resolution critique first. Scoped to this goal; does not carry forward. (2) **RESOLVED / DECIDED 2026-08-02** — Lane C ships a
  NON-BLOCKING advisory, not a gate. The operator took the restraint
  checklist's own default: what exists today is one FINDING (13 references), not
  a recorded RECURRENCE, and promotion to a blocking floor waits for the
  recurrence count Lane A produces. Recorded honestly: the usual argument for
  advisory-first — that a floor false-fires and trains token-theater — is WEAK
  here, because this check is fully deterministic and a false positive is
  structurally impossible. The gate was defensible; the restraint rule was
  followed anyway, because this repo's recorded failure is adding floors on
  first sight rather than missing them. **Size is NOT an open item** — this goal
  is materially smaller than the last one: one counted repair set, one
  disposition table, one recorded decision.
- **Both activation items are settled. This goal is ready to run.**
## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — teeth belong
   where a wrong answer escapes. A documented command that cannot run is a wrong
   answer that escapes silently, and this one is statically decidable.
2. [the 2026-08-02 sweep](../audit/2026-08-02-can-this-rule-fire-sweep.md) — it
   HAD these 13 and lost them, because verifiers refuted "inert" by exhibiting a
   different working path. Read `### Refuted cannot-fire claims` before Lane B.
3. [the completed goal](./2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md)
   and its [retro](../retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md)
   — the class, and why round 2 on a repaired surface keeps earning its cost.
4. [issue #475](https://github.com/corca-ai/charness/issues/475) and
   [issue #476](https://github.com/corca-ai/charness/issues/476) — the two closed
   worked examples of "fires here, dead there"; #476's close records why the
   non-retroactive direction was chosen, which Lane B will face again.
5. [implementation-discipline.md](../../docs/conventions/implementation-discipline.md)
   *Floor-Addition Restraint* — Lane C's checklist, and the reason Lane C is a
   decision rather than a foregone conclusion.

## Interview Decisions

1. **Static repair, or an installed-layout proof channel?** Family considered:
   {temp consumer repo that resolves everything mechanically; static reference
   audit; both; neither, hand back}. **Chosen: static.** The draft this replaces
   proposed the consumer-repo channel and called Lane A speculative. The
   measurement settled both halves at once: the defect is REAL (13 counted) and
   the channel is UNNECESSARY for it (a grep found all 13 in seconds). Rejected:
   the channel, for costing far more and telling us the same thing about this
   class. Anti-anchoring: `axis: cost of the instrument vs the finding` — the
   instinct to build a rig is strongest right after a class has embarrassed you,
   and that is when it is least justified.
2. **Are the 13 and the 9 one lane or two?** Family considered: {one sweep; two
   lanes; fix 13 only}. **Chosen: two lanes.** The 13 are unambiguous (file
   exists, path wrong, refuses nothing new); the 9 may be deliberate
   authoring-repo references. Merging them would let a judgement call ride in on
   a typo fix's certainty. Anti-anchoring: `axis: certainty is not uniform`.
3. **Gate the check now?** Family considered: {blocking gate; advisory; prose
   only; decide in-goal}. **Chosen (operator, 2026-08-02): a non-blocking
   advisory**, with a gate reconsidered only after Lane A counts the recurrence.
   A cheap deterministic check that catches a real defect is the most tempting
   possible floor, and this repo's recorded reflex is to add one on first sight.
   Rejected: the gate — defensible here, and unusually so, because the standard
   objection (a floor that false-fires trains token-theater) does not apply to a
   check whose false positives are structurally impossible; it was still declined
   because one finding is not a recurrence. Rejected: prose only, which is what
   let 13 accumulate unnoticed. Anti-anchoring: `axis: teeth timing` — the
   strongest case for teeth is right after the defect embarrasses you, which is
   also when the evidence for permanence is thinnest.

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
