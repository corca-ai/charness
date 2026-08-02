# Achieve Goal: Close the unreachable-file class and widen the claims round

Status: draft
Created: 2026-08-04
Activation: `/goal @charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-04-close-the-unreachable-file-class-and-widen-the-claims-round.md` after confirming the draft is
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

Two items the operator named after the previous run, both structural rather than
repairs.

**A. Close the class #477 and #478 were sub-forms of.** Both issues enumerated
and fixed instances of one thing — *shipped prose asserts a file the reader can
reach, and the reader cannot* — and both sets grew during triage because every
enumeration used a denominator narrower than the class. A bounded causal review
before #478's close found **at least eleven further live instances in one pass**,
filed as [#479](https://github.com/corca-ai/charness/issues/479). Two are the
#477 depth class in the shipped mirror, and `check_doc_links.py` does not scan
`plugins/**` at all, which is why they are green today.

The narrower half of the same item: **ten `parents[3]`/`parents[2]` occurrences
in packaged Python are correct only because the exporter's kind-flattening
cancels the `plugins/<pkg>` prefix** — an arithmetic coincidence invisible at
each call site — and an eleventh (`scripts/skill_runtime_bootstrap.py:103`,
`parents[4]`) is already wrong but unreachable behind a correct ancestor walk.
One change to `export_plugin.py`'s skill-tier layout turns all of them into #477
at once.

**B. Widen the closeout-claims round beyond goal closeout.** It is a standing
contract step for `achieve` goals, and on its first outing it found five record
blockers four code-reading rounds had missed. The same question — does the
artifact's summary survive contact with the work? — is unasked at PR and release
closeout, where the record is what an outside reader gets.

The outcome is that a future enumeration of this class starts from a real zero
rather than a measured-with-the-wrong-ruler zero, and that the claims question
fires wherever a closeout record is produced.

## Non-Goals

- **Not repairing all eleven #479 instances by hand.** The point is the checker
  that makes the class decidable; hand-fixing the current members and leaving
  the denominator alone is what produced three rounds of "0 remaining" already.
- **Not re-litigating `<authoring-repo>/` or `<plugin-dir>/`.** The split shipped
  and works; whether `<plugin-dir>/` ever gets its first user is a separate call.
- **Not rewriting `export_plugin.py`'s layout.** The `parents[N]` item is about
  making the invariant STATED, not about changing what the exporter does.
- **Not adding a claims round to every commit.** The unit is a closeout record,
  not a diff.
- Not the E-cluster, not D41–D49.
## Boundaries

- **External side-effect scope.** Issue CREATION is standing per `AGENTS.md`
  `## External Side Effects` — do not ask. `git push` is standing CONDITIONAL ON
  THE GATES: push when pre-push passes, and never weaken or bypass a gate to get
  there; a refusing gate withdraws the approval. **Closing #479 is NOT covered**
  and needs its own grant, as does any release, tag, version bump, or
  `cautilus evaluate` run.
- In scope: `check_doc_links.py`'s scan surface, the new link/contradiction
  checks, the `parents[N]` family, #479's disposition table, one non-`achieve`
  closeout surface, and the `plugins/` mirror of anything touched.
- Stop conditions: (1) if a new check would refuse a LEGITIMATE reference,
  narrow the rule rather than accepting the false positive — the previous run
  shipped two of those into a blocking gate and had to retract the justification;
  (2) if widening the claims round would fire it per-commit rather than per
  closeout record, cut back to the record; (3) if resolving `parents[N]` starts
  changing what the exporter DOES, stop and treat it as a design change.
- **Cut order if short: E, then D, then C.** B is the one that closes the most
  of the class for the least judgment.
- Legacy note on the seeded rule below: external side-effect scope: name which
  phase or bundle any approved publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- **A checker refuses a relative link that escapes the plugin root**, proven by
  a fixture built from the real defect (`plugins/charness/support/README.md:26`
  resolves to `plugins/scripts/`, which exists in no tree). Running it over the
  current tree names the confirmed instances rather than reporting zero.
- **The `<repo-root>` / `authoring-repo-internal` contradiction is caught
  mechanically** — a line asserting a file is authoring-repo-internal while
  using the consumer prefix is a zero-false-positive rule, and five live sites
  prove it fires.
- **#479 carries a per-instance disposition**: fixed, or recorded with a reason.
  A reader can tell a decision from an omission.
- **The `parents[N]` invariant is either stated in code or documented with its
  revisit trigger**, and the already-wrong eleventh site is resolved either way.
- **The claims round fires at one closeout surface beyond `achieve` goals**, with
  the trigger written where that surface's contract lives — not in prose someone
  has to remember.
- **Every figure carries `<value> — <source>`**, with its denominator and when
  it was taken.
- **Non-claim in writing**: a static checker proves a path does not RESOLVE for
  a consumer. It does not prove the target would fail at runtime, and it does
  not prove the class is exhausted — only that the ruler got wider.

## Agent Verification Plan

### Low-Cost Checks

- **Re-run the sweep BEFORE building anything**, and record the count with its
  date. #479's list was taken 2026-08-02 and the tree has moved since.
- **Widen the denominator before claiming a zero.** Every prior pass reported
  "0 remaining" honestly and was wrong because its ruler was narrower than the
  class: `.py`-only, `scripts/`-only, command-only, `skills/`-only. State the
  ruler next to the count, every time.
- Sync `plugins/` mirrors before validators (`mutate -> sync -> verify`).
- Obey the dup-ratchet edit advisory when it fires, and re-run it after any
  REFACTOR of an already-classified file — fingerprints rotate.
- A new checker owes a fixture built from a REAL confirmed instance, not an
  invented one; the real ones are listed in #479.
### High-Confidence Checks

- **TWO bounded rounds for any slice that changes verdict logic**, round 2
  reading the repairs. Measured five times now, and the last was the sharpest:
  the fix for "a documented command that cannot run" shipped three new ones.
- **A closeout-claims review by a distinct observer** before the completion flip.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify` the
  MOMENT the reviewer returns, before any parent write.
- **A new checker must be proven to BITE**, by reintroducing a real defect and
  watching it refuse — not by passing on a clean tree.
- Build test inputs from source constants, never by retyping.
### External Or Live Proof

- `git push` to `main` and its CI — standing per `AGENTS.md` **conditional on the
  gates**; a refusing gate withdraws the approval, and never weaken one to reach
  a green push.
- Remote CI confirmed by a different observer AND a different channel than the
  push exit code. The combined-status API returns `pending`/`total_count: 0` for
  every commit here because this repo publishes check-runs; that is not a
  pending check.
- Closing #479 is NOT covered: issue close is per-goal and needs its own grant.
- Explicitly not in this plan: any release publish, tag, version bump, or
  `cautilus evaluate` run.
## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Re-run the sweep with the widened ruler and restate #479's count with its denominator and date | Every prior pass reported an honest zero with a narrow ruler; starting from a stale list would repeat that exactly | A dated count per axis, and the ruler stated beside it | pending |
| B | A checker that refuses a relative link escaping the plugin root, fixture-built from the real `support/README.md` defect | One check, no judgment calls, covers the majority of #479's confirmed instances — and `check_doc_links` does not scan `plugins/**` at all today | The checker refusing the real defect, a test proving it bites, and the confirmed instances named | pending |
| C | Catch the `authoring-repo-internal` + `<repo-root>/` contradiction, and disposition the remaining #479 instances | A line that says a file is authoring-repo-internal while using the consumer prefix is zero-false-positive; five live sites prove it | The rule firing on all five, plus a per-instance disposition table for what it does not cover | pending |
| D | Resolve the `parents[N]` invariant: state it in code or document it with its revisit trigger, and fix the already-wrong eleventh site | Ten sites correct by coincidence is one exporter change from eleven instances of #477 at once | The helper or the documented invariant, and `skill_runtime_bootstrap.py:103` resolved | pending |
| E | Widen the claims round to one closeout surface beyond `achieve` goals | It found five record blockers four code rounds missed, on its first outing; PR and release closeouts ask nobody that question | The trigger recorded in that surface's own contract, not in prose | pending |
| F | Closeout: bundle gate, final verification, claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green | pending |

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

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: RESOLVED 2026-08-02 — the operator named both items
  after the previous run and asked for them to be shaped as a goal for the next
  session. External side effects are already settled by the standing approvals
  in `AGENTS.md` (issue creation unconditional, push conditional on the gates),
  so the only per-goal grant this run might need is closing #479, which is
  explicitly out of scope until asked. Nothing else here is consequential: no
  release surface, no live proof, no issue close, and the one proof-level
  non-claim (a static checker proves non-resolution, not runtime failure) is
  recorded in `## User Acceptance`.
- **This goal is ready to run.**

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [design-north-star.md](../../docs/design-north-star.md) — P5 governs the new
   checks: teeth only where a wrong answer escapes, and the previous run's
   retracted "false positives are impossible" claim is the cautionary case.
2. [issue #479](https://github.com/corca-ai/charness/issues/479) — the eleven
   confirmed instances, the denominator story, and the cheapest-first direction.
3. [the #478 resolution critique](../critique/2026-08-02-issue-478-resolution.md)
   — where the class-vs-sites distinction and the prevention-scope trace come
   from. Read before assuming the existing gate covers this.
4. [the completed goal](./2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md)
   and its [retro](../retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md)
   — the `parents[N]` revisit trigger, and the claims round's first outing.
5. [operating-contract.md](../../docs/conventions/operating-contract.md)
   *Critique Discipline* — owns the claims round that slice E widens.
6. [authoring-preflight.md](../../docs/conventions/authoring-preflight.md)
   — the placeholder vocabulary the new checks decide against.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

1. **Fix the eleven, or fix the ruler?** Family considered: {hand-repair the
   confirmed instances; build the checks and let them name the set; both; defer}.
   **Chosen: the ruler first, repairs as its output.** Three passes have now
   reported an honest "0 remaining" with a ruler narrower than the class, so
   hand-repairing the current members reproduces exactly that. Rejected:
   hand-repair-first, which feels faster and rebuilds the same false zero.
   Anti-anchoring: `axis: a clean count is evidence about the ruler, not the
   tree`.
2. **How much should the claims round widen?** Family considered: {every commit;
   every closeout record; PR only; leave it at `achieve` goals}. **Chosen: one
   closeout surface beyond goals, chosen during the run.** Per-commit would make
   it ceremony, which is how a floor becomes token theatre. Rejected: leaving it
   alone — it found five blockers on one outing, and PR/release closeouts are
   read by people outside the session. Anti-anchoring: `axis: a step that pays
   once is not a step that pays everywhere`.
3. **`parents[N]`: helper, or documentation?** Family considered: {a shared
   `plugin_or_repo_root()`; document the invariant with a revisit trigger; fix
   only the already-wrong site; nothing}. **Chosen: decide in-goal, with the
   already-wrong site fixed either way.** Ten correct-by-coincidence sites are
   not urgent, and a helper touching ten call sites is its own slice; but
   `skill_runtime_bootstrap.py:103` is wrong today and is cheap. Anti-anchoring:
   `axis: fragile-but-correct and quietly-wrong deserve different urgency`.

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
