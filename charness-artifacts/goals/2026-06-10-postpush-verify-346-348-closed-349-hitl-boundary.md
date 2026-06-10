# Achieve Goal: Next queue — post-push/release verification (#346/#348 CLOSED) + #349 hitl/hotl reciprocal boundary

Status: active
Created: 2026-06-10
Activation: `/goal @charness-artifacts/goals/2026-06-10-postpush-verify-346-348-closed-349-hitl-boundary.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 1 — post-push/release lane verification (read-only).
- Next action: `gh run list` for the post-push quality-core run; verify-closeout
  for #346/#348; release live installed-surface probe; mutation-run check.
- Timebox: 2.5h
- Activation time: 2026-06-10T21:26:55+09:00
- Closeout reserve: 30m
- Done-early policy: continue_next_improvement (if a slice closes early,
  continue to the next surfaced improvement rather than stopping).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Clear the next queue in two independent per-slice-closed-out slices,
synthesized from the completed next-queue goal's retro and non-claims, the
refreshed handoff, the open-issue state, and recent-lessons: (1)
**POST-PUSH/RELEASE-LANE VERIFICATION (read/verify-first).** The third
2026-06-10 push + release lane (operator-ordered right after this goal was
shaped) produced deferred proofs this goal consumes read-only: the
`quality-core.yml` push run on the new HEAD is green (triage any failure
per the CI-only failure-recovery protocol, repair repo-locally); **#346
and #348 are CLOSED** by their direct-commit carriers (verify via
`issue_tool.py verify-closeout` — never a manual close); the release
publish verified its installed-surface refresh via a LIVE local probe
(installed plugin version == released tag; checkout SHA == pushed HEAD —
the release artifact carries no `install_refresh` line, the carried
lesson); and the next green scheduled `mutation-tests.yml` run covers the
pushed state. (2) **#349 — HITL/HOTL RECIPROCAL BOUNDARY (deliberate
frozen-contract slice).** Make the routing boundary bidirectional: trim
exactly enough reviewed prose from `skills/public/hitl/SKILL.md` (or
relocate detail into its references) to open headroom under the 200-line
total ceiling, add the one-line reciprocal statement (post-apply
verification of applied live behavior routes to `hotl`), and run the
contract-freeze discipline the deferral was filed for — this is a
`preserve` claim on hitl's reviewed dogfood contract, not a behavior
change. Carrier `Closes #349` staged on the slice commit (closes land on
the NEXT operator push). Apply this session's ordering lesson: fresh-eye
slice critique BEFORE the locked coverage producer.

## Non-Goals

- Do NOT take on **#184** (product success metrics) — SIXTH consecutive
  deliberate exclusion; it is product-level and needs an operator
  `ideation` session shaped into its own goal.
- Do NOT push or cut a release inside this goal — the third 2026-06-10
  push + release lane precedes activation (operator-ordered in the shaping
  session); slice 1 verifies it read-only. The carrier staged by slice 2
  lands on the NEXT operator push.
- Do NOT manually close #346/#348/#349 — #346/#348 close via the carriers
  riding the pre-activation push (slice 1 verifies CLOSED state); #349's
  staged carrier owns its close and the next-queue goal verifies it.
- Do NOT expand slice 2 into broader hitl rework — the scope is the
  minimal headroom trim plus ONE reciprocal boundary line; everything else
  in hitl's reviewed core stays byte-stable.
- Do NOT take on ceal-side `hotl` consumption (adapter wiring, retiring
  its repo-local close-loop) — that repo's follow-up, named in #348.

## Boundaries

- **Slice 1 — lane verification.** READ/VERIFY-FIRST: `gh run list/view`
  for the post-push quality-core run and the next scheduled mutation run;
  `issue_tool.py verify-closeout` for #346 and #348 (post-publication
  verification per the achieve adapter); release verification via the
  release helper's recorded artifacts PLUS the live installed-surface
  probe (installed plugin version == released tag; checkout SHA == pushed
  HEAD). Repairs for CI friction are local-only and staged for the next
  operator push. If the scheduled mutation run has not fired/completed
  within the timebox, record the latest available green run and keep the
  next-run check a named deferred proof (the pre-resolved fallback three
  prior goals used — GitHub cron slots can be skipped; the last goal's
  slot fired in-window).
- **Slice 2 — #349.** Surfaces: `skills/public/hitl/SKILL.md` (+ its
  `plugins/charness/` mirror); possibly one hitl `references/*.md` if the
  trim relocates detail. Contract-freeze discipline: hitl is
  review-required with a reviewed dogfood case — BEFORE trimming, check
  which dogfood `observed_evidence` rows and which tests pin the exact
  prose (`python3 scripts/check_prose_pin.py --repo-root .` plus a grep of
  docs/public-skill-dogfood.json), and claim `preserve` (boundary
  clarification only; trigger, workflow, guardrails, and all behavior
  rules stay intact). The trim target is redundancy or relocatable detail,
  never a load-bearing rule. Gates: core/total headroom preflight before
  prose, all skill-package gates green, mirrors byte-synced, fresh-eye
  slice critique BEFORE the locked producer run (this session's contract
  line), carrier `Closes #349` staged via `issue_tool.py
  validate-closeout-draft`; no `#N` anchors in skill-package files.
- **External side-effect scope:** this goal performs NO push, NO release,
  NO PR; remote access is read-only `gh` plus the post-publication
  `verify-closeout` reads. The push + release lane it verifies in slice 1
  is operator-executed BEFORE activation. The slice 2 carrier takes effect
  on the next operator push (the next goal's verification input).
- Discuss before activation: RESOLVED — (a) `production_or_live_proof`:
  slice 1 is read-only consumption of the operator-ordered third
  2026-06-10 push/release lane; no remote mutation is authorized or needed
  by this goal. (b) `issue_close_or_split`: #346/#348 CLOSED-state
  verification is read-only; #349 is close-INTENDED via a staged
  `Closes #349` carrier validated with validate-closeout-draft — never a
  manual close. (c) `frozen_contract_scope`: slice 2 edits a reviewed
  at-cap skill core; the scope is bounded to the minimal trim + one
  reciprocal line with a `preserve` claim, and any discovered need for a
  larger hitl rework is a stop-and-report, not an in-goal expansion.
  Re-open this item instead of activating if any of these calls is wrong.

## User Acceptance

What the user can do to verify completion directly.

- **Slice 1:** the goal artifact's slice log names the post-push
  quality-core run id + verdict, `gh issue view 346` / `gh issue view 348`
  both show CLOSED with the carrier commit as the closer, the release
  live-probe evidence (installed == released tag, checkout SHA == pushed
  HEAD), and either a green scheduled mutation run id over the pushed
  state or the named deferred-proof line.
- **Slice 2:** `skills/public/hitl/SKILL.md` names the reciprocal `hotl`
  boundary, stays at or under 196/200 total lines
  (`check_skill_surface_preflight` green with headroom), its dogfood
  contract is unchanged (`validate_public_skill_dogfood` green, claim
  `preserve`); `git log` shows the staged `Closes #349` carrier.

## Agent Verification Plan

### Low-Cost Checks

- `check_skill_surface_preflight.py --path skills/public/hitl/SKILL.md`
  (headroom) BEFORE prose; `check_prose_pin.py` before trimming; mirror
  byte-sync; `validate_skill_ergonomics` + dogfood/validation registries;
  the touched test modules if any pin moves.
- `issue_tool.py validate-closeout-draft` for the staged #349 carrier
  before its commit; `issue_tool.py verify-closeout` for #346/#348 in
  slice 1 (read-only).

### High-Confidence Checks

- Fresh-eye slice critique for slice 2 BEFORE the locked producer run
  (ordering contract line from the prior goal's retro); broad gate
  (`run-quality.sh --read-only`) + changed-line producer/consumer at the
  bundle boundary when any mutation-pool file changes (a SKILL.md-only
  slice may not need the producer — confirm via the consumer's
  eligibility verdict rather than assuming).
- Fresh-eye goal-closeout disposition review at the end.

### External Or Live Proof

- Slice 1 consumes the already-executed push/release lane read-only via
  `gh` + the live installed-surface probe + `verify-closeout`.
- No other remote lane is authorized; the staged #349 carrier's CLOSED
  state is the NEXT goal's verification input after the next operator
  push.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Verify the third 2026-06-10 push/release lane: post-push quality-core green, #346/#348 CLOSED via verify-closeout, release installed-surface verified live, scheduled mutation green over pushed state | the lane executes immediately after this goal is shaped; consuming its deferred proofs read-only is the proven loop-closing pattern (fourth iteration) | run ids + verdicts in slice log; verify-closeout payloads; live probe output; mutation run id or the named deferred line | planned |
| 2 | #349: minimal hitl headroom trim + one reciprocal hotl boundary line under contract-freeze discipline (preserve claim) | operator-surfaced by the completed goal's critique; small, bounded, and the at-cap deferral was filed precisely so this happens deliberately rather than under closeout pressure | hitl SKILL.md ≤196/200 with the reciprocal line; all package gates green; dogfood contract unchanged; staged Closes carrier | planned |

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

## Slice Log

### Slice 1: Slice 1 — third 2026-06-10 push/release lane verification (read-only)

- Objective: Consume the operator-executed push + release-0.39.0 lane's deferred proofs read-only: post-push quality-core verdict, #346/#348 CLOSED state via verify-closeout, release installed-surface live probe, scheduled mutation coverage of the pushed state.
- Why this approach: Fourth iteration of the proven deferred-proof verification pattern; all arms are read-only gh/issue_tool/local-filesystem probes, no remote mutation.
- Commits: none (read/verify-only slice)
- What changed: Goal artifact only (activation frame + this log).
- Alternatives rejected:
- Targeted verification: quality-core push run 27275145498 on pushed HEAD 768ded84: SUCCESS (companion run 27275131498 on release commit 0d001be0 also green; 27275130967 cancelled as superseded-by-768ded84 concurrency, not a failure). issue_tool.py verify-closeout: #346 status=verified state=CLOSED carrier=direct-commit 84dc1db3; #348 status=verified state=CLOSED carrier=direct-commit a65a232c. Release live probe: released tag v0.39.0 == installed plugin version 0.39.0 (~/.agents/src/charness/plugins/charness/.claude-plugin/plugin.json); installed checkout SHA 768ded84165e2417fbdbbe3ff485b5f56a15d684 == pushed HEAD (git rev-parse both sides). Scheduled mutation: latest green run 27270609532 covers pre-push fd3c2c6c; next ~3h cron slot (~13:40Z) is in-window — re-check at closeout, with the pre-resolved record-latest + named-deferred fallback if the slot is skipped.
- Test duplication pressure:
- Critique: No repair items surfaced; the lane verified clean on every arm checked so far. Mutation-arm disposition deferred to closeout by design (Boundaries fallback).
- Off-goal findings: none
- Lessons carried forward: zsh expands a bare === separator via =cmd expansion and aborts the compound command — use a quoted echo or separate calls when chaining verify commands.
- Metrics:

### Slice 2: Slice 2 — #349 hitl/hotl reciprocal boundary (frozen-contract preserve edit)

- Objective: Make the hitl/hotl routing boundary bidirectional under hitl's 200-line ceiling: one reciprocal line in hitl's intro, compensated by a semantics-preserving trim, with the contract-freeze discipline the deferral was filed for.
- Why this approach: Preserve claim: the issue's own suggested direction (trim redundancy + one line) — the defaults-block compression is pure formatting with both paths verbatim, confirmed unpinned by prose-pin scan, dogfood observed_evidence cross-check, and an exact-phrase grep; raising the ceiling was pre-rejected at shaping.
- Commits: staged this slice: hitl SKILL.md + plugin mirror + resolution-critique artifact + this goal artifact, carrier 'Closes #349' (validate-closeout-draft: draft_verified, ready_to_commit_push; close lands on the next operator push)
- What changed: skills/public/hitl/SKILL.md (intro +1 reciprocal line; Bootstrap defaults 7->2 lines), plugins/charness/skills/hitl/SKILL.md (byte-synced mirror), charness-artifacts/critique/2026-06-10-issue-349-resolution-critique.md (new).
- Alternatives rejected: Guardrail-bullet placement (less routing-visible than the intro, and hotl's own statement lives in its intro — symmetry kept); trimming the Gawande style line (reviewed voice, not redundant); raising the 200-line ceiling (pre-rejected: weakens the headroom discipline that caught this).
- Targeted verification: check_skill_surface_preflight: 196/200 total (4 left), 155/160 core. Mirror cmp: byte-identical. Gates green: validate_skills (24 packages), markdownlint (0 errors), check_doc_links, validate_skill_ergonomics, check_skill_ownership_overlap, validate_attention_state_visibility, validate_public_skill_dogfood (20 cases). check_prose_pin: no pins. plan_cautilus_proof: required=false, goal=preserve, run_mode=ask — no eval owed, deterministic gates own closeout. Changed-line consumer eligibility confirmed post-commit (markdown-only diff).
- Test duplication pressure:
- Critique: Fresh-eye slice critique BEFORE the locked producer (ordering contract honored): SHIP-WITH-NITS, no blockers — vocabulary symmetry with hotl verified, trim confirmed semantics-preserving, commit scoping nit folded (goal artifact committed deliberately with the slice). Resolution critique (recurrence focus): ACCEPT-WITH-PROPOSALS, persisted at charness-artifacts/critique/2026-06-10-issue-349-resolution-critique.md.
- Off-goal findings: Recurrence-prevention proposals (create-skill at-cap checklist line; near-cap >=195/200 preflight warning) — five public skills sit at exactly 200/200, so the class is systemic; routed to one follow-up issue at goal closeout per the resolution critique (F2+F5).
- Lessons carried forward: For at-cap reviewed skills, run the unpinned-prose triangulation (prose-pin scan + dogfood evidence dump + exact-phrase grep) BEFORE choosing the trim target; the defaults-style formatting blocks are the cheapest safe headroom.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **The completed prior goal + its retro:**
   `charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md`
   (`## Final Verification` non-claims: #346/#348 closes land on the next
   operator push and CLOSED verification belongs to this goal; the
   hitl->hotl boundary is one-directional until #349) and
   `charness-artifacts/retro/2026-06-10-next-queue-goal-retro.md` (the
   critique-before-locked-producer ordering lesson, now a contract line;
   the at-cap fold-then-revert that became #349).
2. **Open issues:** corca-ai/charness#349 (hitl/hotl boundary
   one-directional; hitl core at its 200-line ceiling; lineage
   cross-linked to the detection class), #346/#348 (close via the
   pre-activation push carriers — slice 1 verifies CLOSED), #184
   (excluded, sixth time).
3. **Handoff:** `docs/handoff.md` (Next Session: push lane + CLOSED
   verification, #349 candidate, ceal-side consumption is the consuming
   repo's follow-up, #184 exclusion).
4. **Recent lessons:** `charness-artifacts/retro/recent-lessons.md`
   (critique-before-producer ordering; probe-to-render integration-pin
   lesson; the release live-probe pattern slice 1 leans on).
5. **Surfaces to touch:** `skills/public/hitl/SKILL.md` + mirror (slice
   2); `gh run list/view`, `issue_tool.py verify-closeout` (slice 1).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (operator-directed: "이번 세션 교훈, handoff, 열린 이슈,
  최근 레슨 포함해서 다음 할 일", followed by an operator-ordered push +
  release lane).** Family: {lane verification; #349; #184; ceal-side hotl
  consumption; idle until push}. Chosen: **verification + #349** — the
  first consumes the lane the operator just ordered (fourth iteration of
  the proven deferred-proof pattern) and verifies the #346/#348 CLOSED
  states the prior goal explicitly deferred here, the second is the prior
  goal's own surfaced improvement, filed precisely so it gets a deliberate
  frozen-contract slice instead of a closeout-pressure fold. Rejected:
  #184 (sixth exclusion — product-level, needs operator ideation as its
  own goal); ceal-side consumption (the consuming repo's work, named in
  #348).
- **#349 mechanics (probe, not fixed).** Family: {trim hitl core
  redundancy; relocate detail to references; raise the 200-line ceiling}.
  Chosen direction: **minimal trim or relocation + one reciprocal line**,
  decided at slice time after reading which prose is pinned (dogfood
  observed_evidence + prose-pin scan). Pre-rejected: raising the ceiling
  (a repo-wide gate change to serve one line is the wrong trade and would
  weaken the headroom discipline that caught this in the first place).
- **Slice 2 freeze claim.** Family: {preserve; improve}. Chosen:
  **preserve** — the reciprocal line clarifies routing, changes no
  trigger/workflow/guardrail behavior; if the slice discovers the trim
  cannot avoid load-bearing prose, stop and report rather than silently
  flipping to improve.
- **Activation timing.** Activate AFTER the operator's push + release lane
  completes (the lane runs in the same session this goal is shaped);
  slice 1's mutation-run check inherits the cron-skip fallback three
  prior goals pre-resolved.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. A fresh-eye plan critique runs at
activation per the verification cadence.

- **Provenance:** self-critique by the shaping session.
- **Slice 2 could erode the frozen hitl contract.** Folded: preserve claim
  fixed in Boundaries; prose-pin + dogfood-evidence scan BEFORE trimming;
  stop-and-report on any load-bearing-prose discovery; byte-stability of
  everything except the trim+line named in User Acceptance.
- **Slice 2 could repeat the prior goal's producer-rerun waste.** Folded:
  the critique-before-locked-producer ordering is named in
  High-Confidence Checks, and the producer may be skippable entirely for
  a SKILL.md-only slice (consumer-eligibility check named instead of
  assumption).
- **Slice 1's #346/#348 verification could mask a carrier failure (e.g. a
  reworded commit subject breaking the close keyword).** Folded:
  verify-closeout is the named instrument (it reads the carrier back from
  the commit); a NOT-CLOSED finding is a slice-1 repair item (repo-local,
  staged for the next push), not a manual close.
- **Slice 1's mutation-run check may idle on a skipped cron slot.**
  Folded into Boundaries: the pre-resolved record-latest +
  named-deferred fallback, no idle wait required.
- **Over-worry (raised, not folded):** that the release-lane verification
  duplicates the release helper's own recorded verification — the live
  installed-surface probe is the one arm the helper does not persist (the
  carried lesson), so slice 1 keeps exactly that arm plus read-only run
  checks.

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
