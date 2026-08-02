# Achieve Goal: Push the armed gate and close #477 through its carrier

Status: active
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: real draft/backlog awaiting activation.
- Current slice intent: real draft/backlog awaiting activation; reshape before
  activating if the acceptance boundary has changed. Once active, this names
  the reviewable-intent unit in progress and the commits it spans; critique
  and broad proof do not re-fire within one unchanged intent — update it when
  the intent changes, not per commit (meaningful-slice-cadence).
- Next action: activate with `/goal @charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md` after confirming the draft is
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

One commit is sitting unpushed (`58960639`) and one issue is finished but open.
Both are the same shape: **work whose local proof is complete and whose external
boundary was never crossed**, because the prior goal's side-effect approval was
scoped to that goal and expired with it.

The commit arms `inventory_skill_script_references.py --strict` as a BLOCKING
gate in `run-quality.sh`, resolves #477 (the risk-interrupt planner that had
never run in any installed plugin), splits `<authoring-repo>/` out of
`<repo-root>/`, and makes the closeout-claims review standing. Locally proven:
broad suite 6737 passed, dup ratchet clean, `--strict` exit 0, two bounded
review rounds.

Three outcomes:

1. **Push it, and prove the armed gate survives contact with remote CI.** This
   is the first push where `run-quality.sh` can refuse on a path reference, so
   the pre-push and CI runs are the first evidence the promotion is safe outside
   this working tree.
2. **Close #477 through its proper carrier — the commit message** — with the
   full closeout ledger the gate demands (`jtbd`, `root_cause`,
   `debug_artifact`, `siblings`, `prevention`, a `Behavior #477:` verdict naming
   a distinct channel, an `AI-provenance:` marker, and a delegated resolution
   critique BEFORE the close call). The mechanism was never in doubt; the
   authorization was.
3. **Get the #478 convention decided**: 7 sites / 6 scripts where skill prose
   tells a consuming repo to run a charness authoring-repo script. The
   `<authoring-repo>/` split made them visible; it did not decide them.

## Non-Goals

- **Not re-litigating the gate promotion.** It is armed, its two false-positive
  classes are repaired and pinned, and its justification is already corrected in
  four places. If CI refuses on a path reference, that is a finding to read, not
  a reason to disarm.
- **Not converting the #478 sites unilaterally.** The split gave them a spelling
  (`<authoring-repo>/` or `<plugin-dir>/`); which one — or whether to reword —
  is the operator's convention call, and taking it silently is exactly what the
  goal exists to prevent.
- **Not a release, tag, or version bump.** No `cautilus evaluate` run.
- **Not widening the delegation-contract markers for existing consumers** (D49).
- Not the E-cluster, not D41–D48.
## Boundaries

- **External side-effect scope — SETTLED BY THE OPERATOR 2026-08-02, agreeing
  with the agent's recommended split.** (1) `git push` to `main` plus the
  `quality-core` runs it triggers: **APPROVED**. (2) Closing #477 via the
  commit-message carrier: **APPROVED**, still through the close path's full
  ledger with a DELEGATED resolution critique BEFORE the close call — the grant
  covers the decision to close, never the evidence floor. (3) Comments or
  conversions on #478: **CASE-BY-CASE** — recording per-site decisions in this
  artifact needs no grant, but writing to GitHub or converting shipped prose is
  asked for individually, because #478 is a convention decision rather than a
  repair.
  **Scoped to THIS goal; does not carry to the next one.**
  NOT in scope at all: a release publish, a tag, a version bump, or any
  `cautilus evaluate` run.
- In scope: the unpushed commit `58960639`, #477's closeout ledger and critique,
  the 7 #478 sites, and the `plugins/` mirror of anything touched.
- Stop conditions: (1) if CI refuses on the newly armed path gate, read the
  refusal as a finding and fix the reference — do NOT disarm the gate to go
  green; (2) if the #478 decision would newly APPLY a floor to repos previously
  outside it, it becomes an operator decision (D49); (3) if #477's behavioural
  verdict cannot be produced through a channel distinct from the fix, record it
  unproven rather than reusing the fix's own channel.
- **Cut order if short: C, then B, never A.** A is the boundary that is already
  paid for — the work is proven and only the crossing is missing.
- Legacy note on the seeded rule below: external side-effect scope: name which
  phase or bundle any approved publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- **Push**: `git ls-remote origin main` shows the pushed SHA, and remote CI is
  confirmed by a DIFFERENT observer AND a DIFFERENT channel than the push exit
  code. Explicitly: the combined-status API returns `pending`/`total_count: 0`
  for every commit in this repo because it publishes check-runs, not legacy
  statuses — reading that as a pending check is a known misread and must not be
  repeated.
- **#477 closed with evidence, not assertion**: closed via the commit-message
  carrier; `issue_tool.py validate-closeout-draft` and `verify-closeout` both
  pass; the GitHub state is read back as `CLOSED` through the adapter rather
  than inferred from the push. The `Behavior #477:` line names a channel that is
  NOT the same one that produced the fix.
- **#478 carries a recorded decision** — one of `repointed to <plugin-dir>/` /
  `reworded as charness-only` / `bullet dropped` / `deferred with a named
  revisit trigger` — with the reason, for all 7 sites. A reader can tell a
  decision from an omission.
- **The armed gate is proven outside this tree**: a CI run where
  `inventory-skill-script-references --strict` actually executed and passed.
- Every figure carries `<value> — <source>`, with its denominator and when it
  was taken.
- **Non-claim in writing**: a green CI proves the gate did not FALSELY refuse on
  this tree's current content. It does not prove it refuses correctly on content
  nobody has written yet.

## Agent Verification Plan

### Low-Cost Checks

- `git log --oneline origin/main..HEAD` BEFORE anything, to confirm the bundle
  is still exactly `58960639` and nothing drifted since it was proven.
- Re-run `inventory_skill_script_references.py --repo-root . --strict` and
  record the exit code and denominator with the date.
- `issue_tool.py preflight` / `plan` before touching GitHub, not after.
- Draft the closeout ledger and run `validate-closeout-draft` BEFORE composing
  the commit, so the gate is not discovered at commit time.
- **A close keyword in prose auto-closes even inside a negation.** This session's
  commit was refused for the sentence "this does not close #477"; GitHub does
  not read the negation. Check the whole message, not just the subject.
- Sync `plugins/` mirrors before validators (`mutate -> sync -> verify`).
- Obey the dup-ratchet edit advisory when it fires, and re-run it after any
  REFACTOR of an already-classified file — fingerprints rotate.
### High-Confidence Checks

- A DELEGATED resolution critique for #477 before the close call — the approval
  covers the decision to close, never the evidence floor.
- **A closeout-claims review by a distinct observer** before the completion flip.
  This is now a standing contract step (`operating-contract.md` Critique
  Discipline), added because three code-reading rounds missed a skipped
  verification step, a self-contradiction, and an unreconciled headline count
  that one claims round caught.
- `reviewer_boundary_fingerprint.py snapshot` around each review, `verify` the
  MOMENT the reviewer returns, before any parent write.
- A SECOND bounded round if any slice changes verdict logic on a proof surface.
  Measured twice this session: both times round 2 found blockers round 1 could
  not, because the repaired code did not exist yet.
- Build test inputs from source constants, never by retyping.
### External Or Live Proof

- `git push` to `main` and the `quality-core` CI it triggers — only after the
  approval in `## Boundaries` is granted.
- The GitHub `CLOSED` state for #477, read back through the adapter.
- Expect the pre-push changed-line mutation lane to refuse if new branches are
  added; it refused three times this session and was correct every time.
- Explicitly NOT in this plan, and therefore non-claims: any release publish,
  tag, version bump, or `cautilus evaluate` run.
## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Push `58960639` and confirm remote CI through a different observer AND channel | The armed gate has never run outside this working tree; until CI runs it, "safe promotion" is a local claim | Pushed SHA at `origin/main`, both check-runs `success`, the `inventory-skill-script-references` step green in the CI log | pending |
| B | Close #477 through the commit-message carrier with the full closeout ledger and a delegated resolution critique | The work is done and the issue is open; the carrier is the repo's designed path and the ledger is what makes the close evidence rather than assertion | `validate-closeout-draft` + `verify-closeout` pass, GitHub state read back as CLOSED, critique artifact | pending |
| C | Get the #478 convention decided and record it for all 7 sites | The split made them visible and a visible-but-undecided set rots back into invisibility | A per-site disposition with reasons; conversions applied or an explicit deferral with a revisit trigger | pending |
| D | Closeout: bundle gate, final verification, claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green | pending |

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

- Discuss before activation: RESOLVED 2026-08-02 — the operator agreed with
  the agent's recommended split rather than granting a blanket scope: push to
  `main` plus its CI is APPROVED, closing #477 through the commit-message
  carrier is APPROVED (evidence floor unchanged — full ledger plus a delegated
  resolution critique first), and #478 GitHub writes / prose conversions stay
  CASE-BY-CASE. Recorded as a deliberate narrower grant, not an inherited
  default: the prior goal's operator chose a WIDER scope than recommended, so a
  later session should read this as a different call made on purpose. Scoped to
  this goal only.
- **This goal is ready to run.**

## Slice Log

### Slice 1: A — push the armed gate

- Objective: Cross the boundary the previous goal could not: push the proven bundle and prove the newly armed path gate survives outside this working tree.
- Why this approach: The gate had only ever run here. Until CI ran it, 'safe promotion' was a local claim.
- Commits: 58960639, f5c84f3c, cd223b3a, c31a6eca
- What changed:
- Alternatives rejected:
- Targeted verification: Pre-push refused ONCE, correctly: the changed-line mutation lane named the plugins/* non-directory guard, a branch round 1 had asked about in prose and I had answered without a test. Covered, then 83 passed / 0 failed. Pushed c31a6eca. inventory-skill-script-references PASSED in pre-push (303ms) and in CI. Confirmed per P4 on three channels: gh run watch --exit-status = 0; the commit check-runs API independently (both success); git ls-remote matching the pushed SHA.
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward: The armed gate's first external run is the evidence, not the local run. It passed both.
- Metrics:

### Slice 2: B — close #477 through the commit carrier

- Objective: Close #477 with evidence rather than assertion: the full bug ledger, a delegated causal review before the close call, and a behavioural verdict from a channel distinct from the fix.
- Why this approach: The carrier was never in question — the commit message is the repo's designed path. What the ledger demands (root_cause, siblings with decision AND proof, prevention, a distinct-channel behaviour verdict) is what turns a close into evidence.
- Commits: 98f2e749
- What changed: charness-artifacts/critique/2026-08-02-issue-477-resolution.md, charness-artifacts/probe/2026-08-02-477-installed-layout-plan-risk-interrupt.md, RCA ledger append.
- Alternatives rejected: Rejected issue_tool.py close-with-comment: it skips exactly the ledger fields that make the close auditable. Rejected asserting the behaviour from the in-repo mirror: the reviewer showed that cannot distinguish a self-sufficient package from a nearby authoring tree.
- Targeted verification: validate-closeout-draft went draft_failed FOUR times before draft_verified, each for a real gap: missing root_cause/debug_artifact parsing, a siblings value lacking the required decision-AND-proof shape, an unrecognised critique line form, and a critique artifact with no Fresh-eye satisfaction line. Then the artifact's own validator refused it for a missing Boundary Ownership verdict and reviewer tier evidence. All fixed rather than routed around. verify-closeout: state CLOSED via backend-state-readback, ok true, no state mismatches.
- Test duplication pressure:
- Critique: Delegated bounded causal review before the close (window issue-477-causal, snapshot/verify clean). It supplied the three-mechanism root cause, swept four sibling axes, and REFUTED two claims the fix made about itself — that it 'resolves the layout ambiguity' (it removes one instance of a class live at ~10 other sites) and that a two-candidate probe would have confused check_doc_links (that gate structurally cannot read the form).
- Off-goal findings: Ten packaged-Python sites use hard-coded parents[3]/parents[2] and are correct ONLY because the exporter's kind-flattening cancels the plugins/<pkg> prefix. Recorded with a revisit trigger (any export_plugin.py skill-tier layout change), not repaired.
- Lessons carried forward: The behavioural verdict is the field most likely to be asserted rather than proven. Exporting to /tmp and running the documented command there cost minutes and reproduced BOTH halves of the report — the wrong path, and the swallow that hid it.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. [design-north-star.md](../../docs/design-north-star.md) — P4 governs this
   whole goal: push and issue-close are irreversible boundaries, so success is
   provisional until a DIFFERENT observer on a DIFFERENT channel confirms it. P5
   governs the gate that is being pushed: teeth only where a wrong answer
   escapes.
2. [the completed goal](./2026-08-03-repair-the-commands-the-skills-tell-agents-to-run.md)
   and its [retro](../retro/2026-08-02-repair-the-commands-the-skills-tell-agents-to-run.md)
   — the 13 repairs, the three-silence accumulation mechanism, and the waste
   items this goal's verification plan is built from.
3. [issue #477](https://github.com/corca-ai/charness/issues/477) — the planner
   that never ran in an installed plugin; slice B closes it.
4. [issue #478](https://github.com/corca-ai/charness/issues/478) — the 7 sites,
   including the reviewer's separating principle for deciding them.
5. [operating-contract.md](../../docs/conventions/operating-contract.md)
   *Critique Discipline* — now carries the standing closeout-claims review that
   slice D must run.
6. [authoring-preflight.md](../../docs/conventions/authoring-preflight.md)
   — the `<repo-root>/` vs `<authoring-repo>/` split and its one decidable
   exception, which is the convention #478 is decided against.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

1. **Push now, or shape a goal and push there?** Family considered: {push
   immediately under the previous approval; ask for a one-line approval and push
   inline; shape a goal and push inside it; leave unpushed indefinitely}.
   **Chosen: shape a goal.** The operator asked for it, and it is also the
   honest reading of phase-scoped approval — the prior grant is spent, so the
   crossing needs its own frame with its own proof plan. Rejected: pushing under
   the old approval, which is precisely the silent carry-forward the contract
   names. Anti-anchoring: `axis: proven work feels pre-authorized` — local proof
   completeness creates the strongest possible pull to treat the boundary as a
   formality, and that is when it is least examined.
2. **Close #477 by commit carrier or by a manual close?** Family considered:
   {commit-message carrier with full ledger; `issue_tool.py close-with-comment`;
   leave open}. **Chosen: the commit carrier.** It is the repo's designed path,
   and the ledger it demands (`root_cause`, `siblings`, `prevention`, a
   behavioural verdict on a distinct channel) is what turns a close into
   evidence. Rejected: the manual close, which skips exactly those fields.
   Anti-anchoring: `axis: the gate is the contract` — the commit-msg gate
   refusing this session's message was the mechanism working, not friction to
   route around.
3. **Decide #478 in this goal, or defer again?** Family considered: {decide all
   7; decide the clear ones and defer the rest; defer wholesale}. **Chosen:
   require a recorded decision per site, allowing an explicit deferral with a
   revisit trigger.** A visible-but-undecided set is how the original 13 became
   invisible. Rejected: another wholesale defer, which would waste the
   visibility the `<authoring-repo>/` split just bought. Anti-anchoring:
   `axis: making it visible is not deciding it`.

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
