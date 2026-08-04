# Achieve Goal: Decide where a recurring judgment-bound lesson lives, and stop verdict surfaces losing their own evidence

Status: complete
Created: 2026-08-08
Activation: `/goal @charness-artifacts/goals/2026-08-08-decide-where-a-recurring-lesson-lives.md`

This file is the living goal scratchpad for the active run.

## Active Operating Frame

- Current slice: Slice E — bundle proof, claims review, retro disposition, and staged issue closeouts.
- Current slice intent: close the goal only after the final evidence record is populated and a distinct
  observer has checked the goal's claims. Slice D resolved #500/#501/#497 at their producer/export
  boundaries; Slice E stages their carrier in the default-branch commit without pushing or closing
  remote state out of band. Once active, this names the reviewable-intent unit in progress and the
  commits it spans; critique and broad proof do not re-fire within one unchanged intent — update it
  when the intent changes, not per commit (meaningful-slice-cadence).
- Next action: run the locked bundle proof, bind the claims/disposition review and host probe, then
  commit the carrier and final goal record with the remote issue close still awaiting publication.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- Semantic packet question: state the semantic fact/invariant, owning boundary,
  recorded instance, and axis-varying counterexample before judging the control.
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
| B | Build what slice A chose, proven to bite against a recorded instance | A remedy that would not have caught any of the five is theatre | The chosen control surfaces or refuses a real recorded instance; if a gate, also passes the tree with false-fire cost measured | completed |
| C | Give #502's summary format an owner, or record why it should not have one | It is the cheapest live instance of "a verdict surface with many consumers and no definition", and it is where slice A's answer gets stress-tested | Changing the format is one edit plus one test, or a recorded decision that the 17 consumers are correct as they are | completed |
| D | Disposition #500, #501, #497 under slice A's answer | They are the concrete cases that show whether the answer is usable on real code | Each either fixed under the chosen shape, or carrying a recorded exemption with its reasoning | completed |
| E | Closeout: bundle gate, claims review, retro, issue closeouts, commit | Repo contract treats critique, closeout and commit as task-completing work | `--verification-lock` green with an explicit pytest number; each close through its floor | in_progress |

## Operator Decision Queue

none — no operator-only decision remains; issue publication, push, and remote
state readback are explicitly staged outside this local goal closeout.

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
- Routing: impl — built the smallest reviewer-packet control and loaded `prove` for the Slice B stop gate.
- Routing: debug — recorded the root cause and seam-risk index for the proxy-for-invariant class before shaping the control.
- Routing: quality — planned and ran public-skill quality/dogfood validation, refreshed measurement baselines, and recorded the broad-suite result.
- Routing: retro — persisted the auto-triggered session retro and refreshed the lesson-selection index.
- Routing: issue — filed off-goal recurring telemetry follow-up #503 under the standing issue-creation approval.
- Issue closeout: #497 #500 #501 staged via direct-commit carrier commit `4a2170da0a02d8dad066af9eed20beb8c9a40ceb`; `validate-closeout-draft --carrier direct-commit` was `draft_verified`, and `verify-closeout --carrier direct-commit --commit-ref HEAD` was `carrier_verified` without remote state readback because this goal does not push.
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

### Slice 2: Build the semantic reviewer-packet control

- Objective: Implement and exercise the reviewer-owned semantic question selected for #499 and #491, with a recorded instance and axis-varying counterexample.
- Why this approach: The selected branch is judgment-bound; a reviewer question can carry the invariant without adding a proxy meta-gate.
- Commits: dd699467 Carry semantic reviewer question into critique packets
- What changed: Added the shared reviewer-packet semantic question, source and plugin mirrors, adapter packet inclusion, critique consumer guidance, exact source-to-packet tests, and the worked #499/#491 application. Refreshed debug/probe/quality/retro truth surfaces and recorded the off-goal telemetry follow-up.
- Alternatives rejected: Rejected a semantic blocking/meta-gate because it would encode another proxy; rejected a reminder-only packet because it would not distinguish form from invariant; deferred surface fixes for #500/#501/#497 and #502 ownership to later slices.
- Targeted verification: Generated packet ok with three sections; exact-content and decision-boundary tests passed; three final angle reviewers plus a counterweight returned no implementation blocker with clean boundary fingerprints; cross-surface critique validation passed with owned-correctly; run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review completed; probe and inventory regression checks passed; standing suite reported 7028 passed in 42.76s; bash .githooks/pre-commit passed.
- Test duplication pressure: Focused packet and critique-skill tests cover the new producer/consumer contract; exact source equality prevents mirror drift. No semantic applicability gate was added because applicability is judgment-bound.
- Critique: charness-artifacts/critique/2026-08-04-slice-b-semantic-question.md and the generated packet/application record the delegated fresh-eye review, packet hashes, boundary ownership, findings, repairs, and non-claims.
- Off-goal findings: Filed #503 (https://github.com/corca-ai/charness/issues/503) for recurring closeout telemetry showing slow gate-runtime and over-slice costs; the retro records it as a tracked follow-up. #496 remains outside this goal.
- Lessons carried forward: A reviewer question earns its place when it names the invariant, owner, recorded instance, and varying counterexample, then compares the proposed control; packet delivery alone is not semantic proof. New quality artifacts must be measured and their probe baselines refreshed together.
- Metrics: 7028 standing tests passed in 42.76s; focused packet/critique tests 49 passed; host token/tool metrics unavailable; three final angle reviewers plus one counterweight, with clean boundary verification for each review write boundary.

### Slice 3: Assign #502 a per-run receipt owner

- Objective: Decide whether #502's 17 summary-format assertions require a new renderer or structured sibling, then implement the smallest owner-side contract that preserves the fact a truncated reader must act on.
- Why this approach: The issue's production problem is truncation-safe per-run recovery, not assertion count. The producer/consumer read showed `print_final_summary` owns the terminal receipt while `runtime-signals.json` owns historical telemetry; fresh-eye review found the final-line recovery path and aggregate-warning ordering gaps.
- Commits: 1e540417 Make quality summaries carry actionable failure receipts
- What changed: Made `scripts/run-quality.sh` the explicit per-run receipt owner: every failed label now travels with a verified `[log: path]` or `[log unavailable]` marker on the final `Quality summary` line, and aggregate runtime recording happens before that line. Regenerated `plugins/charness/scripts/run-quality.sh`, updated the focused runner tests, recorded the critique/packet evidence, refreshed the quality artifact, and persisted the Slice C retro addendum and lesson index.
- Alternatives rejected: Rejected a new JSON sibling because `runtime-signals.json` is rolling profile-scoped telemetry with no current-run failure provenance and no named machine consumer needs a second state surface. Rejected renderer extraction because there is one producer and no second format consumer. Rejected consolidating the 17 assertions because they cover distinct runner modes and failure paths.
- Targeted verification: Producer/consumer and gathered #502 evidence were inspected. Focused standing tests passed 51 in 4.91s; `bash -n` passed for source and export; critique, quality, inventory-consumption, retro, packaging, markdown, and pre-commit validators passed. The first broad run exposed an exact quality-artifact marker-shape failure and was repaired. The locked broad standing suite passed 7028 in 41.93s, and the final post-ledger rerun passed 7028 in 37.47s. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review` completed its structural/deterministic checks before the locked proof.
- Test duplication pressure: The existing 17 assertions remain distributed contract tests. Added direct final-line label/path coverage, explicit unavailable-marker coverage for failed log copies, and aggregate-recorder warning ordering coverage without widening the production test surface beyond the repaired seam.
- Critique: `charness-artifacts/critique/2026-08-04-slice-c-summary-owner.md` records the semantic fact, owner/readers, recorded instance, axis-varying counterexample, three decision angles, counterweight, repair-read blocker, final packet-bound approval, packet hashes, and clean reviewer-boundary verifications. The first repair-read reviewer caught the post-summary aggregate warning escape; the later repair-read and current-packet reviewers approved the final ordering. No Cautilus evaluation was run; deterministic proof was used under the ask-before-run contract.
- Off-goal findings: No new off-goal issue. Existing #503 remains the tracked recurring closeout-runtime follow-up; #496 remains outside the goal.
- Lessons carried forward: A verdict surface must carry the complete action fact at the actual truncation boundary: verdict, failed identity, and recovery path. Rolling telemetry is not a per-run receipt. Test the final line and place best-effort diagnostic writes before it. When a quality artifact changes inventory-consumption prose, run its consumer validator before the broad suite.
- Metrics: 7028 broad standing tests passed in 41.93s, with a final post-ledger rerun at 37.47s; 51 focused tests passed in 4.91s; 3 initial angle reviewers plus 1 counterweight, then repair-read and current-packet bounded reviewers; every reviewer boundary verification was clean; host token/tool metrics unavailable.

### Slice 4: Repair producer and export boundary verdicts

- Objective: Disposition #500, #501, and #497 under Slice A's surface-owner answer, with the final consumer proving the repaired behavior.
- Why this approach: The debug reproductions showed split value ownership, an AST-only export blind spot, and an authoring-layout-only exported validator. Each boundary could carry and prove its own semantic fact without adding a proxy gate.
- Commits: aa30b66d Repair producer and export boundary verdicts; 583f731a Cover export boundary branches.
- What changed: Moved newline/prose/total-loss supplied-slug invariants into `goal_artifact_lib.py` and applied them to the exact handoff-rendered values before any write; added the narrow literal `import_repo_module` call detector with positional/keyword and `Path(__file__)` coverage plus explicit dynamic-form non-claims; made adapter resolver loading and discovery source/flattened-layout aware; and added a generated exported-validator subprocess proof with `CHARNESS_REPO_ROOT` cleared. Synced the checked-in plugin mirrors.
- Alternatives rejected: Kept template consolidation, general package-loader redesign, and arbitrary dynamic-import inference out of scope. The duplicate-ratchet families for standalone pipeline CLI scaffolding and bootstrap preambles were reviewed as intentional, with their rationale recorded in `dup-review.json`.
- Targeted verification: Debug artifact and seam-risk index validate; critique and quality artifacts validate; source/export import checks validate 645 files; source adapter validation reports 16 resolvers and 18 YAML files; exported validation reports 16 resolvers; focused producer/export tests pass 127, then 89 after the changed-line branch additions. The broad quality run passed 85 checks with no failures before commit; the post-commit run established the mutation lane, found two uncovered branches, and the final direct changed-line producer reports every mapped changed line covered. No Cautilus evaluation was run.
- Test duplication pressure: The new tests prove hostile goal values leave no artifact, canonical CR handling, explicit-slug refusal, auto-draft fallback, exact import-call boundaries, source/flattened resolver branches, and environment-isolated exported execution. The new duplicate families were either removed or classified intentionally after reading their owners.
- Critique: The pre-implementation critique used three decision angles and a separate counterweight; the final repair-read bounded reviewer found no blocker or medium finding, with clean boundary fingerprint verification. The final packet is `charness-artifacts/critique/2026-08-04-slice-d-final-packet.json`.
- Off-goal findings: none — #496 remains outside this goal; tracked issue closeouts are deferred to Slice E under the standing closeout floor.
- Lessons carried forward: Validate the exact values the final consumer will read, and prove exported behavior through the generated layout rather than mirror equality. A narrow static predicate is stronger when its unsupported forms are explicit. Generated current artifacts must be recaptured after broad quality refreshes before packet binding is committed.
- Metrics: 85 broad quality checks passed with zero failures before the final coverage repair; 89 focused branch/export tests passed; the direct changed-line producer is clean; 3 critique angles plus 1 counterweight and a final repair-read reviewer; host token/tool metrics unavailable.

### Slice 5: Bundle proof, claims review, retro, and staged issue carriers

- Objective: close the six-row decision record with the locked bundle proof, a distinct claims/disposition review, the triggered retro disposition, and a direct-commit carrier for #497/#500/#501 without publishing remote state.
- Why this approach: P4/P5 make the evidence record and second observer the stop condition; the achieve lifecycle stages issue close keywords in the default-branch commit and leaves push/readback outside this local goal.
- Carrier: `charness-artifacts/issue/2026-08-04-issues-497-500-501-closeout.md`, validated with `issue_tool.py validate-closeout-draft --carrier direct-commit --commit-message-file` as `draft_verified` before the carrier commit.
- What changed: Reconciled the debug record after the causal review found stale candidate-owner/pending-test prose; persisted the triggered Slice D retro and lesson-selection index; bound the issue-specific resolution critique to the exact JSON packet identity; and recorded separate behavior channels for all three issues.
- Alternatives rejected: Did not push, close GitHub state out of band, or replace the carrier with a manual fallback. Did not infer remote behavior from local tests or treat `verify-closeout` carrier checks as final tracker readback.
- Targeted verification: `run_slice_closeout.py --verification-lock --refresh-broad-pytest-proof --ack-cautilus-skill-review` completed its staged structural/deterministic bundle checks; the separate standing runner reported 7048 passed in 44.52s. The debug seam index, retro, critique, goal, and carrier validators pass; the resolution critique ran three named angles plus a separate counterweight with clean boundary verification; no Cautilus evaluation was run. The claims review remains the final completion check for this slice.
- Critique: `charness-artifacts/critique/2026-08-04-issue-497-500-501-resolution-critique.md` records the causal context, three issue-bound behavior verdicts, boundary ownership, packet hashes, four fresh-eye findings, and the counterweight bins. The goal-level claims/disposition review is the remaining distinct observer before the status flip.
- Off-goal findings: #496 remains outside the goal; recurring closeout-runtime/over-slice telemetry remains filed as #503.
- Lessons carried forward: A closeout record is itself a verdict surface. Bind the exact packet bytes, keep debug ownership current, and name each final-consumer behavior channel separately from the carrier and tracker state.
- Metrics: 7048 standing tests passed; 4 issue-resolution reviewers returned findings; the first claims review returned three closeout blockers that were repaired; the final claims review is the completion evidence; host window metrics are unscoped because the goal has no `Host metric window:` line.

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

Retro: charness-artifacts/retro/2026-08-04-session-retro.md
Host log probe: charness-artifacts/probe/2026-08-04-decide-where-a-recurring-lesson-lives.json
Disposition review: charness-artifacts/critique/2026-08-04-decide-where-a-recurring-lesson-lives-disposition-review.md
- Standing proof: `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only` — 7048 passed in 44.52s.
- Bundle proof: `run_slice_closeout.py --verification-lock --refresh-broad-pytest-proof --ack-cautilus-skill-review` completed with all staged structural/deterministic checks passing; `run_standing_pytest.py --mode read-only` separately reported 7048 passed in 44.52s. No Cautilus evaluation was run under the ask-before-run contract.
- Claims boundary: local tests and `verify-closeout` carrier checks do not prove remote issue state; push, GitHub close, and post-publication state readback remain outside this local goal closeout.
- Host metrics: the probe found available thread-wide Claude/Codex logs but no goal-scoped window because this artifact has no `Host metric window:` line; goal-window elapsed/token/tool totals are therefore unclaimed.

## User Verification Instructions

- Run the final carrier commit through the normal default-branch publication path; its `Closes #497`, `Closes #500`, and `Closes #501` keywords are staged in `charness-artifacts/issue/2026-08-04-issues-497-500-501-closeout.md`.
- After publication, run `python3 skills/public/issue/scripts/issue_tool.py verify-closeout --repo corca-ai/charness --number 497 --number 500 --number 501 --classification bug --carrier direct-commit --commit-ref <published-carrier-sha> --expect-state CLOSED` and retain the distinct behavior verdicts already recorded in the carrier.

## Auto-Retro

Retro dispositions: applied: synchronized quality artifacts and probes before broad verification.
Retro dispositions: applied: carried the semantic reviewer question and worked #499/#491 application into the critique packet.
Retro dispositions: applied: made the truncation receipt carry verdict, failed identity, and recovery path.
Retro dispositions: out-of-scope: the quality-packet corpus-denominator capability needs a separate owner and was not required to resolve this goal's six issue findings.
Retro dispositions: out-of-scope: promoting rolling telemetry into a structured per-run receipt needs a named consumer, retention, and stale-state contract outside this goal.
Retro dispositions: applied: ran the changed-line producer after focused branch-coverage repair.
Retro dispositions: applied: reconciled the debug record's ownership, invariant, sibling, and final-consumer proof paragraphs.
Structural follow-up: issue #503 (recurs: recurring closeout-runtime and over-slice telemetry needs a gate-owner decision; the separate corpus-denominator packet surface remains explicitly out-of-scope here)
