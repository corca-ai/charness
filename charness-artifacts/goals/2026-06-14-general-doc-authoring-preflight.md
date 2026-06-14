# Achieve Goal: Aggregate author-time preflight for general doc/markdown surfaces (resolve #362)

Status: complete
Created: 2026-06-14
Activation: `/goal @charness-artifacts/goals/2026-06-14-general-doc-authoring-preflight.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: COMPLETE. S1 (ec69f594) + S2 (1d69bb4b) committed; this
  goal-closeout commit lands the proof artifacts and flips status.
- Current slice intent: proved and completed — fresh-eye resolution critique
  (SHIP), rung-2 disposition review (FAIL on a first-occurrence dodge →
  remediated to #364), 81 affected-surface tests green, retro + host-log +
  critique closeout evidence, #362 closeout staged (`draft_verified`).
- Next action: none — goal complete. Operator-approved follow-up: push the
  fix commits to origin/main (see `## User Verification Instructions`).
- Routing: find-skills recommended the achieve goal lifecycle (it owns this
  slot); impl built the slices, issue staged the #362 closeout, retro ran the
  after-action. Per Coordination Cues.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve [#362](https://github.com/corca-ai/charness/issues/362): give general
doc/markdown surfaces (`docs/handoff.md`, `docs/*.md`) an **aggregate author-time
preflight** that surfaces, in one pass before the commit gate, the constraints an
author currently discovers by failing one gate at a time — markdownlint rules
(wrapped inline-code-span, `MD004` list-marker style, etc.), `check_doc_links`
pathy-ref/link form, and the length/cap floors (`validate_handoff_artifact`'s
70-line cap, doc length). This is the **describe-first absorption** pattern A2
just brought to goal-closeout and `check_skill_surface_preflight.py` (#284)
brought to SKILL.md, extended to general docs — closing the Problem-1
authoring-churn residual on the one surface class that still lacks it.

## Non-Goals

- **Not a new blocking floor/gate.** Per the Floor-Addition Restraint checklist,
  this is a describe-first affordance that *absorbs* the existing gates' shape up
  front, not a new serial gate. The existing gates stay the enforcement.
- **Not re-implementing the gates.** The preflight forecasts/aggregates the SAME
  constraints the existing validators enforce (shell out to / reuse markdownlint,
  `check_doc_links`, `check-markdown`, the handoff cap) — it must not fork their
  logic and drift, mirroring how A2 reused `check_complete_evidence`.
- **Not skill surfaces.** `check_skill_surface_preflight.py` already owns
  `SKILL.md` / `references/**`; this is the *general docs* gap it does not cover.
- No cross-repo work; no prompt-behavior change requiring live Cautilus.

## Boundaries

- charness-internal only. A new repo-root authoring tool (likely
  `scripts/*.py`) — run the portability classification at closeout
  (host-local authoring helper vs a generalizable capability that a consuming
  repo's docs would also want), since adding a repo-root `scripts/*.py` is a
  `follow-up:portability-classification-tripwire` trigger.
- Stay a non-blocking affordance — a goal/doc must still commit without running
  it (guards against a future hand converting the affordance into a precondition).
- This goal **resolves tracked issue #362**; the issue-closeout floor applies
  (stage the close through `issue`).
- External side-effect scope: none beyond a normal local closeout; any push is
  operator-approved at the bundle boundary, not per slice.
- Discuss before activation: resolved: the two consequential signals are settled by
  the goal's design and need no operator decision before activation — (1) issue
  closeout (#362) is the goal's explicit purpose (the close is staged through `issue`
  at the goal's own closeout, not a surprise side effect); (2) the proof non-claim
  (no live Cautilus / no release coupling in the goal) is the correct default for
  additive charness-internal tooling. No cross-repo work, no floor removal, no
  irreversible side effect.

## User Acceptance

- Running the new preflight on a doc that violates several constraints (a
  deliberately-broken `docs/*.md` fixture: a wrapped inline-code-span + an
  `MD004` `+`-bullet + a backticked pathy ref + over the length cap) emits **all
  of them in one call**, not one per failed commit — hand-runnable.
- A real `docs/handoff.md` edit drafted from the preflight output passes the
  commit gate on the **first** attempt (zero serial-rejection rounds on the
  constraints the preflight surfaces).

## Agent Verification Plan

### Low-Cost Checks

- Unit tests: a fixture doc carrying each violation class → the preflight surfaces
  each; a clean doc → silent. Forecast matches the real gate verdict (no drift).
- `validate_skills` / length / `check_doc_links` / `check-markdown` pass for the
  new tool and any doc edits.

### High-Confidence Checks

- A handoff/doc edit built from the preflight output passes `check-markdown.sh`,
  `check_doc_links.py`, and `validate_handoff_artifact.py` first try.
- `run_slice_closeout.py` bundle boundary green; `plugins/` mirror synced if a
  packaged surface is touched.

### External Or Live Proof

- None required; explicit non-claim — no live Cautilus / no release coupling in
  the goal itself (release is a separate operator-approved step).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Build the aggregate doc-surface preflight: given a target `docs/*.md`/handoff path, forecast the markdownlint + doc-link + length/cap constraints in one report (reusing the real validators, not forking them) | the Problem-1 residual the session's handoff churn exposed (5+ serial rejections) | broken-fixture unit test (all violation classes surfaced) + clean-fixture silence; no-drift vs the real gates | done |
| S2 | Wire it into the authoring flow (implementation-discipline "before authoring into a gated surface" guidance; optionally a slice-closeout advisory) and stage the #362 closeout | makes the affordance discoverable at the point of edit; closes the tracked issue | grep wiring; first-try clean handoff edit; `issue_tool.py validate-closeout-draft`/`verify-closeout` for #362 | done |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
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

Recorded evidence:

- Routing: find-skills → impl — find-skills recommended achieve (owns the goal slot); impl built the two slices under achieve.
- Routing: find-skills → quality — quality ran the gates and pytest (run_slice_closeout, check_doc_links, check-markdown).
- Routing: find-skills → issue — issue staged the #362 closeout and filed the #363/#364 off-goal findings.
- (find-skills' trigger-phrase ranking surfaced handoff/issue, but per its own
  interpretation caveat the activated goal was the real driver of the route.)
- Gather: n/a — the only external source (the #362 GitHub URL) was read live
  through the issue backend (`gh`) as tracked-issue state, not turned into a
  durable gathered knowledge asset; nothing here needs `gather`.
- Release: n/a — this goal touches no release surface (no version bump, no
  install-manifest edit); the plugin mirror sync is a generated-surface step,
  not a release.
- Issue closeout: #362 (feature) — carrier `direct-commit` (the goal-closeout
  commit body carries `Resolves #362` + the feature ledger + the resolution
  `Critique:`). Proof: `issue_tool.py validate-closeout-draft ... --carrier
  direct-commit --commit-message-file <msg>` → `ok: true, status:
  draft_verified` (resolution_critique bound + satisfied); `verify-closeout
  --expect-state CLOSED` → `state_mismatches: []` (already CLOSED, COMPLETED).
  Anomaly: #362 was auto-closed early on 2026-06-13 by commit cff2ad07's
  "resolve #362" phrasing (premature — predated the fix); the operator-approved
  push puts the implementing commits on the default branch. Off-goal gap filed
  as #363 (see `## Off-Goal Findings`).

## Slice Log

### Slice 1: S1: aggregate doc-authoring preflight

- Objective: Build scripts/check_doc_authoring_preflight.py: forecast markdownlint + wrapped-inline-code + doc-link + surface-length-cap constraints for one target doc in a single pass, reusing the real validators.
- Why this approach: Mirror the #284 SKILL.md one-shot preflight and the A2 describe-first closeout preflight (reuse the live check, never fork) extended to the general-docs surface class neither covers.
- Commits: ec69f594
- What changed: scripts/check_doc_authoring_preflight.py (new); tests/test_doc_authoring_preflight.py (new, 8 tests).
- Alternatives rejected: Re-implementing the lint/link/length checks (rejected: drift risk, the A2 lesson is reuse the live check). A new blocking gate (rejected: Floor-Addition Restraint; this absorbs existing gates up front).
- Targeted verification: 8/8 unit tests pass: broken-fixture all-4-classes, clean-fixture silence, no-drift vs real gates (check_doc_links/check_markdown_inline_code/markdownlint-cli2 verdicts), live-constant length cap, non-blocking-affordance guard. py_compile/ruff/check_python_lengths/validate_attention_state_visibility green.
- Test duplication pressure: Low: the no-drift tests subprocess the real gates to assert forecast==gate verdict (a distinct property no existing test covers); they do not re-test the gates' internal logic. Mild boundary-bypass-candidate overlap with each gate's own test, accepted as the no-drift contract.
- Critique: deferred to slice-boundary fresh-eye review (S1->S2 boundary).
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: S2: wire affordance + stage #362 closeout

- Objective: Make the preflight discoverable (authoring-preflight.md section + implementation-discipline.md bullet + non-blocking slice-closeout ADVISORY for docs/*.md edits) and stage the #362 closeout.
- Why this approach: Discoverability at the point of edit is what turns the tool from a remembered ritual into the path of least resistance (the #284/#328 precedent); the issue-closeout floor requires staging the tracked-issue close through issue.
- Commits: 1d69bb4b
- What changed: scripts/slice_closeout_advisories.py (+advise_doc_surface_preflight); scripts/run_slice_closeout.py (wire it); docs/conventions/authoring-preflight.md (+General doc surfaces section); docs/conventions/implementation-discipline.md (+bullet); tests/test_authoring_preflight_reference.py (+drift guard); tests/test_doc_authoring_preflight.py (+advisory trigger test).
- Alternatives rejected:
- Targeted verification: 14 new/changed-file tests pass; 81 passed across affected surfaces (gate-plan, slice-closeout reporting/advisories). Dogfood: ran the new preflight on both edited docs -> clean (acceptance criterion 2). check_doc_links/check-markdown/attention-state/lengths green. Plugin mirror synced.
- Test duplication pressure: Low: the advisory trigger test uses capsys (no subprocess boundary); the drift-guard test extends the existing #308/#319/#328 drift-guard family in test_authoring_preflight_reference.py rather than forking a new pattern.
- Critique: Fresh-eye resolution critique (bounded subagent) running at the closeout boundary; also serves the mandatory issue-closeout review.
- Off-goal findings: #362 was ALREADY closed (COMPLETED, 2026-06-13) by commit cff2ad07 — its body 'Pursue-ready draft goal to resolve #362' auto-closed the issue PREMATURELY (the draft predated the fix). The real fix (ec69f594+1d69bb4b) is unpushed; push (operator-approved) lands the implementing commits so the closed state is honest.
- Lessons carried forward:
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- [#362](https://github.com/corca-ai/charness/issues/362) — the tracked issue this
  goal resolves (observed churn + the precedent shape of a fix).
- `charness-artifacts/retro/2026-06-14-achieve-efficiency-internal-followups.md` —
  the `## Waste` evidence (the concrete handoff rejection sequence) the issue cites.
- `skills/public/achieve/scripts/describe_goal_closeout_shape.py` — the A2
  goal-closeout describe-first precedent to mirror (reuse the real check, no drift).
- `scripts/check_skill_surface_preflight.py` — the #284 skill-surface preflight
  precedent (the SKILL.md-only coverage this goal extends to general docs).

## Interview Decisions

- **Shape of the fix:** chose an *aggregate describe-first preflight that reuses
  the real validators*, over (a) a new blocking gate (rejected — the Floor-Addition
  Restraint reflex) and (b) re-implementing the lint/link/length checks (rejected —
  drift risk; A2's lesson is reuse the live check). The fix absorbs existing gates
  up front; it does not add or fork enforcement.
- **Surface scope:** general docs (`docs/*.md`, `docs/handoff.md`) only — SKILL.md
  surfaces are already covered by `check_skill_surface_preflight.py` (#284), so
  this is the residual gap, not a re-do.

## Plan Critique Findings

Pre-activation premortem light (additive, charness-internal). Worth stressing when
it runs: (a) **no-drift** — the preflight must forecast by invoking/reusing the
real validators (markdownlint, `check_doc_links`, the handoff cap), never a hand
copy that drifts from what the gate enforces; (b) **stays an affordance** — a doc
must still commit without it, asserted by a test (the C5-style non-blocking guard);
(c) **portability** — classify the new repo-root script host-local vs
skill-capability before closeout (the portability-classification tripwire).

Portability classification (closeout): **host-local authoring helper.**
`scripts/check_doc_authoring_preflight.py` is tightly coupled to *this* repo's
gates and modules (`check_doc_links`, `check_markdown_inline_code`,
`validate_handoff_artifact.MAX_ARTIFACT_LINES`, the repo `.markdownlint-cli2.jsonc`)
and doc surfaces — a consuming repo has different gates. It is a repo-root
`scripts/*.py` exactly like its siblings `check_skill_surface_preflight.py` (#284)
and `check_artifact_surface_preflight.py`, neither of which is a portable skill
capability. No skill-package extraction warranted; it ships via the plugin
`scripts/` mirror like the rest.

## Off-Goal Findings

- **#363 — premature close of #362.** #362 was already `CLOSED`/`COMPLETED` on
  GitHub before this run: commit `cff2ad07` (2026-06-13, a draft-goal-shaping
  commit) carried "Pursue-ready draft goal to **resolve #362**" in its body, and
  GitHub auto-closed the issue on push — ~24h before the fix existed. Filed the
  systemic gap (no charness guard against close-keyword leakage in non-fix
  commits) as [#363](https://github.com/corca-ai/charness/issues/363). The fix
  commits (ec69f594 + 1d69bb4b) are unpushed; the operator-approved push lands
  them on the default branch so the closed state is honest.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight.md
Host log probe: charness-artifacts/retro/2026-06-14-general-doc-authoring-preflight-host-log.md
Disposition review: charness-artifacts/critique/2026-06-14-general-doc-authoring-preflight-disposition-review.md

## User Verification Instructions

- **Acceptance 1 (hand-run, all-classes in one call):** run
  `python3 scripts/check_doc_authoring_preflight.py --path <a-broken-docs/*.md> --as-surface handoff`
  on a doc carrying a wrapped inline-code span + mixed `-`/`+` bullets (MD004) +
  a backticked real path + over 70 lines — all four findings print in one call.
  Reproduced in `tests/test_doc_authoring_preflight.py::test_broken_fixture_surfaces_all_classes_in_one_pass`.
- **Acceptance 2 (first-try clean edit):** the two docs edited this run
  (`docs/conventions/authoring-preflight.md`, `implementation-discipline.md`)
  passed the preflight clean, then passed `check-markdown.sh` + `check_doc_links.py`
  on the first commit attempt (zero serial doc-gate rejections).
- **Operator-approved step (push):** the fix commits `ec69f594` + `1d69bb4b`
  (+ this goal-closeout commit) are local, ahead of `origin/main`. Push them to
  `origin/main` to land the implementing commits and make #362's already-closed
  state honest. This goal does not push.

## Auto-Retro

Retro dispositions: issue #363 (novel: no prior retro occurrence of close-keyword leakage in non-fix commits) — close-keyword-leakage guard (premature close of #362); advisory-first per Floor-Addition Restraint.
Retro dispositions: issue #364 (recurs: same-day prior retro 2026-06-14-achieve-efficiency-internal-followups.md + recent-lessons.md line 18, re-violated this run) — proactive plugin-mirror sync before the commit gate. NOT first occurrence (the rung-2 disposition review caught this dodge): a recorded, decaying lesson. The `staged-mirror-drift` gate catches it; escalated to an advisory follow-up, not a blocking floor.
Retro dispositions: issue #364 (recurs: prior "Applied" in-process-test lesson in 2026-06-04 / 2026-06-07 retros, decayed out of recent-lessons.md) — default to in-process test APIs over subprocess for import-safe `scripts/*.py`. Same structural pattern as the mirror-sync habit; the in-process conversion is committed in ec69f594.
Structural follow-up: issue #363 (novel: close-keyword leakage in non-fix commits has no commit-message guard)
Structural follow-up: issue #364 (recurs: persisted pre-commit-gate-habit lessons — proactive mirror sync, in-process test default — keep decaying and getting re-violated; promote to a cheap proactive advisory, not a blocking floor)
