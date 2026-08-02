# Achieve Goal: Prove the skills fire where they are installed, not only where they are authored

Status: draft
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-prove-the-skills-fire-where-they-are-installed.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-03-prove-the-skills-fire-where-they-are-installed.md` after confirming the draft is
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

Charness is a **plugin**. Every skill is meant to run in a consuming repo. Yet
every proof this harness produces is taken in the AUTHORING repo, and that gap
is where its worst defects have lived.

- **#475**: bounded review MANDATED by several skills, inert in any repo that
  never ran `setup`. Fired here, dead there.
- **#476**: the block `setup` WRITES did not match the markers that read it, so
  a repo that adopted the contract read as never having adopted it. Fired here,
  dead there.
- **The 2026-08-02 sweep**: of 14 `cannot-fire` claims, 11 were refuted — and
  most of those were "inert in a consuming repo" claims that verifiers refuted
  by exhibiting a firing input HERE. Both readings were defensible; the sweep
  recorded the consuming-repo axis as explicitly **under-measured** and could
  not settle it. 25 units were left `unread`.

This is the north star's own shape, applied to the harness: a wrong answer
escapes, and there are no teeth at the place it escapes from. A skill that
resolves cleanly here and cannot resolve where it is installed emits no failure,
no log line, no ticket — and every later session trusts it.

**Build the missing evidence channel, then re-judge what the sweep could not.**

## Non-Goals

- **Not proving AGENT BEHAVIOUR in a synthetic repo.** The prior goal withdrew a
  scratch repo for exactly this and was right: an agent told to treat a temp
  directory as its repo root yields testimony about instructions the parent
  wrote, not behaviour. **The distinction that makes this goal viable**: path
  resolution, script existence, and command executability in an installed layout
  are MECHANICAL, observable facts — not agent testimony. Only those are in scope.
- **Not a validator that audits validators.** First round is a MEASUREMENT. A
  standing gate is a separate call, made only with a recorded recurrence, per the
  Floor-Addition Restraint checklist.
- **Not re-running the whole 2026-08-02 sweep.** Only the part its own artifact
  names as unsettled: the consuming-repo axis and the 25 `unread`.
- **Not widening the delegation markers** (the #476 direction deliberately not
  taken). Revisit only if a consuming repo reports an inert floor.
- Not the E-cluster, not D41–D49.

## Boundaries

- **External side-effect scope, enumerated.** (1) `git push` to `main` plus the
  `quality-core` runs it triggers. (2) Filing issues for what the measurement
  surfaces. (3) Closing an issue only if a lane fully resolves it, through the
  close path's floor with a DELEGATED resolution critique BEFORE the close call.
  **Nothing here is pre-approved — the 2026-08-02 approval was scoped to that
  goal and does NOT carry.** Ask before the first push.
  NOT in scope at all: a release publish, a tag, a version bump, or any
  `cautilus evaluate` run.
- A temp/fixture consumer repo under a temp path IS created (and deleted). It
  holds an installed plugin layout, never an agent pretending it is at home.
- In scope: the installed `plugins/charness/` layout, every `$SKILL_DIR`-relative
  and `<repo-root>`-relative command or path a shipped SKILL.md or reference
  instructs an agent to run, and the shipped scripts' behaviour when the
  authoring repo's `scripts/` is absent.
- In scope (repairs): only findings whose repair is unambiguous AND refuses
  nothing new. Everything else is filed.
- Stop conditions: (1) if the broken-path count is large enough that repairing
  in-goal would become a rewrite, STOP at the measurement and file. (2) If a
  repair would newly refuse a checked-in artifact or newly APPLY a floor to
  repos previously outside it, it becomes an operator decision (D49). (3) If the
  channel starts growing into a permanent meta-gate, cut it back.

## User Acceptance

- **Lane A** produces a reproducible command that stands up an installed-layout
  consumer repo and reports, per shipped skill, which instructed commands and
  cited paths RESOLVE there and which do not — with a denominator and a list, not
  a pass/fail.
- **Lane B** re-judges the 2026-08-02 sweep's unsettled part using that channel:
  each previously-refuted consuming-repo claim becomes `fires-there` /
  `inert-there` / `still-undecided: <why>`, and the 25 `unread` become read or
  stay counted as unread.
- **A reader can tell "checked in the installed layout" from "checked only
  here."** That distinction not existing is what this goal is about.
- **Every figure carries `<value> — <source>` or `<value> — unbacked: <why>`**,
  every corpus measurement states its denominator AND when it was taken.
- **Non-claim carried in writing**: this proves MECHANISM in an installed layout.
  It does not prove an agent behaves correctly there. That remains operator-only.

## Agent Verification Plan

### Low-Cost Checks

- **Verify the premise before shaping each slice.** A remedy a durable record
  names is a hypothesis — including this goal's own framing.
- **Write the resolve-or-not predicate down BEFORE enumerating commands**, the
  way the 2026-08-02 sweep wrote its predicate first. That is why its count meant
  something.
- Run each measurement before the fold and again after; record WHEN.
- `check_python_lengths.py --headroom` before a large addition; SPLIT rather than
  shave. The dup-ratchet edit advisory now fires at the first big edit — obey it
  rather than deferring to the closeout aggregate.
- Targeted `pytest` AND `ruff check` in the same breath.
- File the issue first, then write its number into prose.
- **Build test inputs from source constants, never by retyping** — two escapes in
  the 2026-08-02 run came from a fixture spelled the way the matcher wanted.

### High-Confidence Checks

- One bounded fresh-eye round per slice; **TWO for anything that changes what a
  proof surface decides**, round 2 reading the REPAIRED surface. Measured twice
  in the last run: round 2 found the fix reproducing the class it fixed, and
  round 1 structurally could not see it.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify --before`
  the MOMENT the reviewer returns, before any parent write.
- **Adversarial verification, defaulting to refuted, on every finding.** It killed
  11 of 14 last run. Findings taken at face value would have shipped a confident
  wrong measurement.
- A closeout-claims review by a DISTINCT observer before the complete flip.
- The measurement artifact is itself a verdict surface: its counts get
  re-derived by the reviewer, not read back.

### External Or Live Proof

- `git push` to `main` and the remote CI it triggers, confirmed per P4 by a
  different observer AND a different channel than the push exit code.
- **The pre-push changed-line mutation lane refused four times last run**, always
  correctly. Expect it; cover new failure branches as they are written, not at
  the push.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Stand up an installed-layout consumer repo and mechanically resolve every command and path the shipped skills instruct an agent to use | Two of the last three confirmed defects were "fires here, dead there", and the harness has no channel that could have caught either | The reproducible command, a per-skill resolve/not-resolve table with its denominator, and the predicate written before enumeration | pending |
| B | Re-judge the 2026-08-02 sweep's unsettled part with that channel — the consuming-repo claims and the 25 unread | That sweep's own artifact names this as under-measured; leaving it is a measurement that reads more settled than it is | Each claim moved to `fires-there` / `inert-there` / `still-undecided`, unread count reduced or restated, sweep artifact amended in place | pending |
| C | Repair the unambiguous, file the rest | Only repairs that refuse nothing new belong in-goal | Repairs with tests; issues for the rest, each with its measurement | pending |
| D | Closeout: bundle gate, final verification, closeout-claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green; retro dispositions each `applied:` or `issue #N` | pending |

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

- Discuss before activation: **THREE items, none pre-approved.** (1) **EXTERNAL
  SIDE EFFECTS ARE NOT CARRIED OVER.** The 2026-08-02 approval covered that goal
  only. This goal needs a fresh decision on `git push` to `main` plus the CI it
  triggers, on filing new issues, and on closing any issue a lane resolves.
  Confirm before the first push. (2) **IS THIS THE RIGHT BOTTLENECK?** Lane A is
  speculative until its first measurement: if almost nothing breaks in an
  installed layout, the honest move is to stop after the measurement and hand the
  session back rather than build tooling for a non-problem. Confirm that stopping
  early is an acceptable outcome, because it is the likeliest good one. (3)
  **SIZE.** Three working lanes plus closeout is the same shape as the last run,
  which consumed a full session with six reviewers and four push refusals. Cut
  order if short: C, then B, never A's measurement.
## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct the
originating context by following them in order.

1. [docs/design-north-star.md](../../docs/design-north-star.md) — "The boundary
   (load-bearing)". A skill that resolves here and not where installed is a
   fail-open proof surface, and the north star also names the anti-pattern Lane A
   must not become.
2. [the 2026-08-02 sweep](../audit/2026-08-02-can-this-rule-fire-sweep.md) — its
   `## Non-Claims` names the consuming-repo axis as under-measured and the 25
   unread. That paragraph is this goal's brief; read it before enumerating.
3. [the completed goal](./2026-08-03-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md)
   and its [retro](../retro/2026-08-02-fix-the-rule-that-cannot-fire-where-it-was-written-to-then-count-the-rest.md)
   — `## Boundaries` records WHY a scratch repo was withdrawn for agent
   behaviour; this goal's viability rests on not repeating that mistake.
4. [issue #475](https://github.com/corca-ai/charness/issues/475) and
   [issue #476](https://github.com/corca-ai/charness/issues/476) — the two worked
   examples of "fires here, dead there", both closed, both found by a person.
5. [fresh-eye-subagent-review.md](../../skills/shared/references/fresh-eye-subagent-review.md)
   — the ladder those two produced, and the reference whose own instructed
   commands Lane A must resolve in an installed layout.

## Interview Decisions

1. **Why this and not the E-cluster or D41–D49?** Family considered: {E-cluster;
   D-backlog; a consuming-repo proof channel; nothing, hand back to the operator}.
   **Chosen: the proof channel.** The last run produced two confirmed defects of
   the "fires here, dead there" shape and a measurement that explicitly could not
   settle a third bucket of them. The backlog items are known and bounded; this
   one is an unmeasured hole that the harness's own structure keeps producing.
   Rejected: E-cluster, as the most expensive lane with no new evidence pushing
   it up. Anti-anchoring: `axis: is this the real bottleneck` — the honest
   alternative is that consuming-repo breakage is rare and this is speculative
   tooling. Lane A's measurement settles that in its first pass; if the broken
   count is ~0, the goal should stop and say so rather than build for a
   non-problem.
2. **Scratch repo — didn't the last goal withdraw one?** Family considered:
   {no temp repo at all; a temp repo for agent behaviour; a temp repo for
   mechanical resolution only}. **Chosen: mechanical only.** The withdrawal was
   correct and specific: an agent told a temp directory is its repo root reports
   on instructions the parent wrote. Path resolution and script existence are not
   testimony — they are observable without asking any agent anything.
   Anti-anchoring: `axis: what kind of fact` — the prior decision is about
   TESTIMONY, and reusing it to forbid mechanical checks would over-apply it.
3. **Measurement or gate?** Family considered: {one-off measurement; standing CI
   gate; advisory}. **Chosen: measurement first, gate only on recorded
   recurrence**, per Floor-Addition Restraint. A gate here is defensible — broken
   installed paths are exactly where a wrong answer escapes — but this repo's
   recorded reflex is to add a floor on first sight, and the checklist says
   otherwise. Anti-anchoring: `axis: teeth timing`.

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
