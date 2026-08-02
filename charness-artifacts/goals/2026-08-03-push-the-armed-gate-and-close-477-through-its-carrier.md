# Achieve Goal: Push the armed gate and close #477 through its carrier

Status: complete
Created: 2026-08-03
Activation: `/goal @charness-artifacts/goals/2026-08-03-push-the-armed-gate-and-close-477-through-its-carrier.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: all four slices complete; pushed, #477 CLOSED, claims review folded.
- Current slice intent: cross the boundary the previous goal could not — push
  the proven bundle, close #477 through its carrier with a real ledger, and
  disposition the #478 sites. One unchanged intent across all four slices, so
  critique fired at slice boundaries rather than per commit
  (meaningful-slice-cadence).
- Next action: none — goal complete. Open follow-ups live in
  `## Operator Decision Queue` (closing #478, and the `parents[3]` family).
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
| A | Push `58960639` and confirm remote CI through a different observer AND channel | The armed gate has never run outside this working tree; until CI runs it, "safe promotion" is a local claim | Pushed SHA at `origin/main`, both check-runs `success`, the `inventory-skill-script-references` step green in the CI log | complete |
| B | Close #477 through the commit-message carrier with the full closeout ledger and a delegated resolution critique | The work is done and the issue is open; the carrier is the repo's designed path and the ledger is what makes the close evidence rather than assertion | `validate-closeout-draft` + `verify-closeout` pass, GitHub state read back as CLOSED, critique artifact | complete |
| C | Get the #478 convention decided and record it for all 7 sites | The split made them visible and a visible-but-undecided set rots back into invisibility | A per-site disposition with reasons; conversions applied or an explicit deferral with a revisit trigger | complete |
| D | Closeout: bundle gate, final verification, claims review by a distinct observer, retro, commit | Repo contract treats critique, closeout, and commit as task-completing work | `run_slice_closeout.py --verification-lock`; an explicit broad-pytest run with its number; `check_goal_artifact.py` green | complete |

## Operator Decision Queue

- Decision: should #478 be closed? All 7 sites are dispositioned and applied, so it is resolvable — but closing it was outside this goal's grant, which covered #478 comments and conversions case-by-case and said nothing about the close.
- Owner: operator
- Why deferred: the work is done and the issue is accurate as an open record of what was decided; closing needs its own carrier and ledger, which is a slice rather than a footnote.
- Unblock action: grant the close, and it goes through the same commit-carrier path #477 used.
- Revisit trigger: the next goal that touches skill script references.

- Decision: should the ten `parents[3]` / `parents[2]` sites be given a named helper? They are correct today ONLY because the exporter's kind-flattening cancels the `plugins/<pkg>` prefix — an arithmetic coincidence invisible at each call site.
- Owner: operator
- Why deferred: nothing is broken, and repairing ten call sites is a slice of its own rather than a closeout footnote.
- Unblock action: decide between a shared `plugin_or_repo_root(__file__)` helper and leaving the coincidence documented.
- Revisit trigger: **any change to `export_plugin.py`'s skill-tier layout** — that single change turns all ten into #477 at once.

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

Routing: issue — selected from installed skill metadata for #477's resolve path; its planner classified the fix-unit as `bug`, which routed the causal review before the close and selected the ledger fields the carrier had to carry.

Routing: impl — selected for the code slices (the shared shim module, three shims, the seven #478 site edits) and their tests; `prove` owns the closeout ledger it loads at the stop gate.

Routing: quality — selected for validation posture: the dup-ratchet edit advisory obeyed at the edit, the newly armed `--strict` gate's first external runs, and the broad-suite number recorded rather than inferred from a green closeout.

Routing: debug — selected when the pre-push mutation lane refused: the uncovered line was read as a signal (one was DEAD code, deleted rather than tested) instead of retried.

Routing: critique — selected for four bounded fresh-eye contexts: a causal review before the close, two rounds on the shim slice, and the standing closeout-claims round.

Gather: n/a — the URLs in `## Context Sources` are GitHub issue links to this repo's own tracker plus in-repo relative paths, all read through `gh` or the local tree; no external page became working context.

Release: n/a — no version bump and no install-manifest edit. The `/tmp` export was a throwaway proof channel, not a release surface.

Issue closeout: #477 — carrier `direct-commit` (commit `98f2e749`), classification `bug`. `issue_tool.py validate-closeout-draft` → `draft_verified` / `ready_to_commit_push`; `verify-closeout --expect-state CLOSED` → `CLOSED` via `backend-state-readback`, `ok: true`. #478 remains OPEN by design: its 7 sites are dispositioned and applied, but closing it was not in this goal's grant.

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

## Lane C — #478 Site Analysis

All 7 sites, against the separating principle the adversarial reviewer derived:
**a reference is safe when the reader's executable instruction is satisfiable
without resolving the path; it is broken when the path IS the deliverable the
reader is sent to fetch or run.** All 7 fail that test — each sends the reader
to a file only charness has.

Verified 2026-08-02: all six scripts DO ship in the exported plugin
(`export_plugin.py` into `/tmp`; all six present under the package's `scripts/`).
So the affordance is recoverable; the question is how to spell it.

| # | site | reference | what the prose asks |
| --- | --- | --- | --- |
| 1 | `critique/references/angle-selection.md:117` | `check_title_slug_drift.py` | "Run … as deterministic evidence for the title-slug lens" |
| 2 | `critique/references/rename-critique.md:85` | `check_title_slug_drift.py` | "Run … before relying on prose judgment alone" |
| 3 | `gather/SKILL.md:153` | `refresh_current_pointer.py` | a `## References` bullet among package-relative siblings |
| 4 | `shared/references/binary-preflight.md:173` | `validate_skills.py` | "5. Run … to confirm the new gate accepts the change" |
| 5 | `setup/references/default-surfaces.md:125` | `check_doc_links.py` | "See … for the shipped reference implementation" |
| 6 | `setup/references/default-surfaces.md:126` | `check-links-internal.sh` | same sentence (the `.sh` no `.py`-only count ever saw) |
| 7 | `setup/references/default-surfaces.md:127` | `migrate_backtick_file_refs.py` | same sentence, "one-shot migrator" |

### The four options, with the cost each actually carries

- **(a) `<plugin-dir>/scripts/X.py`.** Resolvable in principle and already a
  recognised placeholder. **But it has ZERO usage precedent** — it appears only
  in the placeholder list in `authoring-preflight.md`, never in a skill — and
  unlike `$SKILL_DIR` there is no bootstrap variable behind it, so the agent
  must work out the plugin directory itself. Adopting it here makes this the
  convention's first real user.
- **(b) A `skills/shared/scripts/` shim per script**, the pattern just proven
  for `plan_risk_interrupt`. Resolves in both layouts with no new convention and
  no agent-side resolution. Cost: one shim file per script, and it moves
  repo-level tools onto the shipped skill surface.
- **(c) Reword to `<authoring-repo>/`.** Honest, and already the convention for
  the 8 sites converted this run — but the consumer loses the affordance: the
  sentence becomes "charness has a thing you cannot run".
- **(d) Drop the reference.** Right only where the affordance is not really the
  skill's, which is arguably true for site 3: `gather`'s own
  `scripts/write_record.py` is what its prose actually tells the reader to use,
  and `asset-refresh.md:40` already carries the descriptive mention under
  `<authoring-repo>/`.

### Agent recommendation, per site

- **Sites 1, 2, 4 → (b) shim.** These are imperatives inside skills a consuming
  repo genuinely runs (`critique`, and skill-authoring guidance cited by
  `create-skill` / `create-cli`). The shim pattern is proven in this repo as of
  today and needs no new convention.
- **Sites 5, 6, 7 → (c) `<authoring-repo>/`.** "See X for the shipped reference
  implementation" is a pointer to an example, not a command; the honest fix is
  to say whose example it is. Site 6 is a `.sh` and must move with its two
  neighbours or the sentence stays half-repaired.
- **Site 3 → (d) drop the bullet.** It advertises an affordance `gather` does
  not portably have, and the descriptive mention already exists elsewhere.

### Outcome — APPLIED

The analysis above was written and recorded FIRST, with the edits withheld,
because prose conversion is case-by-case under this goal's grant. The operator
then read the per-site recommendation and answered "추천대로" (as recommended),
which is the grant for these seven conversions and is recorded here because a
grant that lives only in a transcript is indistinguishable from an assumption.

All seven were then applied exactly as recommended — 3 to shims, 3 to
`<authoring-repo>/`, 1 bullet dropped — in commits `8de5d168`, `eb283497`, and
`727cbf40`. An earlier version of this section still read "NOT APPLIED —
awaiting the operator" after the edits had shipped; the closeout-claims round
caught the contradiction, in the one section that carries the per-site reasons.

**#478 itself remains OPEN.** All seven sites are resolved, so it is closable,
but the grant covered comments and conversions and never mentioned the close.
Recorded in `## Operator Decision Queue` rather than taken.


## Slice Log

### Slice 1: A — push the armed gate

- Objective: Cross the boundary the previous goal could not: push the proven bundle and prove the newly armed path gate survives outside this working tree.
- Why this approach: The gate had only ever run here. Until CI ran it, 'safe promotion' was a local claim.
- Commits: 58960639, f5c84f3c, cd223b3a, c31a6eca
- What changed: `58960639` carried the proven bundle inherited from the previous goal (the armed gate, the #477 repair, the `<authoring-repo>/` split, the standing claims-review contract). `f5c84f3c` shaped this goal and repointed the handoff at it; `cd223b3a` recorded the operator grant and flipped the goal active; `c31a6eca` covered the `plugins/*` non-directory guard the pre-push mutation lane refused on. The plan's "confirm the bundle is still exactly `58960639`" precheck was therefore NOT satisfiable as written — three commits were added before the push, all of them this goal's own work, and the honest form of that bullet is a diff review of the range rather than a fixed-SHA equality.
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

### Slice 3: C — disposition all 7 #478 sites

- Objective: Give every #478 site a recorded, applied disposition rather than leaving a visible-but-undecided set.
- Why this approach: The <authoring-repo>/ split made them visible; visible-and-undecided is how the original 13 became invisible.
- Commits: 8de5d168, eb283497, 727cbf40
- What changed: NEW skills/shared/scripts/authoring_script_shim.py + two shims; plan_risk_interrupt shim refitted onto it; 7 sites dispositioned (3 to shims, 3 to <authoring-repo>/, 1 bullet dropped); tests/test_shared_authoring_script_shims.py; two floors in tests/test_skill_script_references.py lowered with reasons.
- Alternatives rejected: Rejected <plugin-dir>/ despite being the obvious answer: zero usage precedent, no bootstrap variable behind it, so the agent would have to resolve the plugin dir itself and these sites would be the convention's first users. Rejected three copies of the resolution logic: the dup ratchet would have caught it at closeout, so the shared module came first.
- Targeted verification: Both repaired invocations run verbatim from an export outside the repo. inventory --strict clean: 402 refs (201/201), the only surviving <repo-root>/scripts/ reference is rca-ledger-append.md, which is correct as an existence predicate. Broad suite 6752.
- Test duplication pressure: check_dup_ratchet clean throughout — the shared module is why three shims produced no new family.
- Critique: TWO bounded rounds, both productive. Round 1: run() discarded the targets' __main__ error handling so a failing validation surfaced as a traceback (fixed with runpy); the unbounded ancestor walk (capped); and a test comment that cited an authoring-only fixture as the guard for a SHIPPED-layout floor, where no fixture produced a shipped BROKEN row at all. Round 2, reading those repairs: THE REPAIR NAMED A COMMAND THAT CANNOT RUN — the three call sites I authored used a bare path while the shims ship mode 100644, i.e. permission denied. Also a swallow guard asserting only half the swallow, a bounded-walk fixture that tolerated a 5-to-7 loosening, and a shipped parametrization running the authoring module.
- Off-goal findings:
- Lessons carried forward: Fourth measured instance of the round-2 class, and the sharpest: the fix for 'a documented command that cannot run' shipped three new documented commands that cannot run. Copying an invocation's SHAPE without its interpreter prefix is the same defect wearing different clothes.
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

- **`scripts/skill_runtime_bootstrap.py:103`** returns `parents[4]`, wrong for a
  shipped skill script. Latent (the ancestor walk finds `scripts/adapter_lib.py`
  first in every real tree), so recorded rather than repaired. See the
  `## Final Verification` non-claims.
- **Markdown links of the form `../../../scripts/...` in `skills/shared`
  references** resolve to `plugins/scripts/...` from the shipped mirror. Raised
  by the claims round and NOT folded: these are markdown links that
  `check_doc_links` resolves (and it passes), not commands an agent runs, and the
  critique's "none live" sibling row was explicitly scoped to `$SKILL_DIR`
  commands. Recorded so a later sweep can decide rather than rediscover.

### Verification-plan bullets NOT evidenced, stated rather than quietly dropped

The claims round checked each `## Agent Verification Plan` bullet against the
record. Three were performed without leaving evidence, and are recorded as
unproven rather than claimed:

- `git log --oneline origin/main..HEAD` before anything — not recorded, and its
  premise (a bundle of exactly `58960639`) had already changed; see Slice 1.
- `issue_tool.py preflight` / `plan` before touching GitHub — `plan` WAS run and
  its classification (`bug`) drove the causal-review routing, but no output was
  captured in the artifact.
- The close-keyword-in-prose check — performed reactively rather than
  proactively: the commit-msg gate refused two drafts, which is how the trap was
  found, not a pre-check that prevented it.
- "Build test inputs from source constants, never by retyping" — mixed and
  unrecorded. `test_skill_script_references.py` derives its tier from
  `PORTABLE_SKILL_KINDS`, while the new fixtures retype the reference literals.
  Some retyping is correct (an assertion that imports its expected value proves
  nothing), but the practice was neither claimed nor disclaimed at the time.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md
Host log probe: charness-artifacts/retro/2026-08-02-push-the-armed-gate-and-close-477-through-its-carrier.md
Disposition review: charness-artifacts/critique/2026-08-02-goal-closeout-claims-push-and-close-477.md

Executed proof, with its date (all 2026-08-02):

- **FOUR separate pushes**, not one, advancing `origin/main`
  `2a9d2aff → c31a6eca → 98f2e749 → 20dedbe8 → 727cbf40` (ten commits total;
  `git log --oneline 2a9d2aff..727cbf40`). The pre-push gate refused TWICE across
  the run, both times from the changed-line mutation lane and both times
  correctly — once in slice A (the `plugins/*` non-directory guard) and once
  before slice A's first successful push (the `__main__` entrypoint line). Final
  pre-push on `727cbf40`: **83 passed, 0 failed**.
- **Remote CI ran on EVERY pushed SHA and passed on every one**, named rather
  than implied — `gh run list` 2026-08-02: `727cbf40`, `20dedbe8`, `98f2e749`,
  `c31a6eca` all `Quality Core: success`. Confirmed per P4 by a different
  observer AND a different channel than the push exit code: `gh run watch
  --exit-status` → 0, then the commit check-runs API independently (`Core
  deterministic gates: success`, `Changed-line mutation coverage: success`), then
  `git ls-remote origin main` matching the pushed SHA. The combined-status API
  returns `pending`/`total_count: 0` for every commit here because this repo
  publishes check-runs, not legacy statuses — recorded so the misread is not
  repeated.
- **#477 CLOSED**, verified by `issue_tool.py verify-closeout` →
  `backend-state-readback`, `ok: true`, no state mismatches — read back through
  the adapter rather than inferred from the push.
- Behavioural verdict for #477 from a channel distinct from the fix and its
  tests: `export_plugin.py` into `/tmp`, then the documented command run from
  `<plugin>/skills/impl` against a consumer repo holding only `.agents/`. The
  OLD path reproduced both halves of the report; the NEW path ran.
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only` →
  **6752 passed, 0 failed**.
- `inventory_skill_script_references.py --strict` → `all 402 (201 authoring /
  201 shipped) resolve`, exit 0. The newly armed gate passed in pre-push (303ms)
  and in CI — its first runs outside this working tree.
- **FIVE** bounded fresh-eye reviewer contexts, each bracketed by
  `reviewer_boundary_fingerprint.py` snapshot/verify, every one `clean` with no
  drift: the #477 causal review, two rounds on the #478 shim slice, and the
  closeout-claims round — whose own `verify` ran the moment it returned, before
  this line was written. An earlier draft of this bullet said "four … all clean"
  while the fourth had not returned; the claims round caught its own count, which
  is the shape the verification plan warns about.

Non-claims, carried in writing:

- The #477 probe is an EXPORT, not a host install. It proves the exported
  package is self-sufficient for that command; it does not exercise a host's
  installer, marketplace resolution, or plugin discovery.
- A green CI proves the armed gate did not FALSELY refuse on this tree's current
  content. It does not prove it refuses correctly on content nobody has written.
- The ten `parents[3]`/`parents[2]` occurrences are correct today and were NOT
  repaired. They resolve in both layouts only because the exporter's flattening
  cancels the `plugins/<pkg>` prefix — recorded with a revisit trigger, not
  proven safe against a layout change.
- **An ELEVENTH site is already WRONG, not merely fragile**, and an earlier draft
  of this non-claim dropped it: `scripts/skill_runtime_bootstrap.py:103` returns
  `parents[4]` as the fallback of `repo_root_from_skill_script`, which yields
  `plugins/` from a shipped skill script. Unreachable today because every tree
  carries `scripts/adapter_lib.py` and the ancestor walk finds it first, so it is
  a latent wrong constant behind a correct walk. Not repaired, and named here
  because a "correct today" headline that quietly excludes the one item a
  reviewer flagged as incorrect is the record-stronger-than-evidence class.
- No release publish, tag, version bump, or `cautilus evaluate` run.

## User Verification Instructions

## Auto-Retro

Retro dispositions: applied: all FIVE shim call sites now assert `python3 `, both halves of the swallow (`|| true` AND `2>/dev/null`), and no `../../../` — the interpreter-prefix miss is enforced rather than remembered
Retro dispositions: applied: the bounded-walk fixture sits AT the boundary (ancestor index 5) and asserts that depth in place, after the previous one tolerated any cap up to 7 and was verified by running `locate` at caps 5/7/8
Retro dispositions: applied: a shipped-layout `BROKEN` fixture exists at last, and the comment that cited an authoring-only fixture as its guard is corrected
Retro dispositions: applied: `run()` executes targets via `runpy` as `__main__`, so a failing validation reports its own verdict instead of a traceback, and the shim inherits each target's entry contract rather than re-implementing one
Retro dispositions: applied: `authoring_script_shim.py` carries the resolution logic once, so three shims produced no new duplicate family — the previous retro's dup-ratchet lesson applied BEFORE the block rather than after it
Retro dispositions: applied: the #477 critique artifact is amended where it still recorded the unbounded walk as deferred-not-repaired, because a durable record naming a deferred remedy is read at slice-shaping time
Retro dispositions: applied: `AGENTS.md` now carries a standing issue-creation approval under a new `## External Side Effects` section, with push / issue-close / release / tag / cautilus explicitly still per-goal — three consecutive goals had re-granted the same permission and the repetition was the signal it belonged in the contract
Retro dispositions: applied: the retro carries an explicit north-star facet mapping (P1/P4/P5 plus the failure signature this run walked into), which the operator asked for twice and neither retro had recorded
Retro dispositions: accepted-risk: the ten `parents[3]` sites stay as they are, correct by an exporter-flattening coincidence, with an explicit revisit trigger in the Operator Decision Queue rather than a silent assumption
Retro dispositions: out-of-scope: a repo-wide "every documented invocation is executable as written" check, which would subsume both this run's path gate and its interpreter-prefix lesson — named in the retro's `## Portable Candidate` rather than built at closeout

Structural follow-up: applied: `tests/test_shared_authoring_script_shims.py` — the `## Sibling Search` names "prose naming an invocation that cannot execute as written" as the transferable class, and the call-site assertions turn its three failure modes (unresolvable path, missing interpreter, swallowed error) into a test rather than a rule someone has to remember.
