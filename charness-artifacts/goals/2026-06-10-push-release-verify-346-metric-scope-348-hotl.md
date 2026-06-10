# Achieve Goal: Next queue — push/release-lane verification + #346 Claude-host metric scoping + #348 portable hotl skill

Status: draft
Created: 2026-06-10
Activation: `/goal @charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-10-push-release-verify-346-metric-scope-348-hotl.md`.
- Timebox: 4h
- Activation time: set at `/goal` activation (REPLACE with an ISO timestamp at
  activation — the complete gate parses `Activation time:` as ISO; three prior
  goals carried this exact reminder for a reason).
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

Clear the next queue in three independent per-slice-closed-out slices,
synthesized from the completed post-push goal's retro and non-claims, the
refreshed handoff, the open-issue state, and recent-lessons: (1)
**PUSH/RELEASE-LANE VERIFICATION (read/verify-first).** The 2026-06-10
second push + release lane (operator-ordered right after this goal was
shaped) produced deferred proofs this goal consumes read-only: the
`quality-core.yml` push run on the new HEAD is green (triage any failure
per the CI-only failure-recovery protocol, repair repo-locally), the
release publish verified its installed-surface refresh (installed version
== released tag via a LIVE local probe — the release artifact carries no
`install_refresh` line, a lesson from the prior goal's activation
critique), and the next green scheduled `mutation-tests.yml` run over the
pushed state stays green (this also retires the prior goal's carried
deferred proof: no scheduled run has covered 39ff5432 or later yet). (2)
**#346 — CLAUDE-HOST PER-GOAL METRIC SCOPING.** Close the recurs-class gap
the last two goal closeouts hand-caveated: `probe_host_logs.py` gains
single-session scoping on Claude hosts (current/named session file instead
of the project-dir aggregate, mirroring the Codex `--session-id/--session-file`
affordance), and `record_metric_window.py` gains a Claude session source so
`Host metric window:` + `--goal-path` scoping works on both hosts. Carrier
`Closes #346` staged on the slice commit (closes land on the NEXT operator
push). (3) **#348 — PORTABLE `hotl` SKILL (smallest honest v1).** A new
public skill for human-on-the-loop closure of applied live behavior, using
ceal's `close-loop` as the scope/workflow reference: portable parts in the
skill (loop inventory, proof packet before execution, execute-or-record
discipline, ledger statuses + staleness semantics, the proof rules), repo
specifics adapter-owned (proof commands, surfaces, ledger schema/paths).
Routed through the `create-skill` authoring contract; implementation
reference read from the LOCAL `../ceal` checkout (operator-directed: faster
than the GitHub permalink, which stays the durable citation). Carrier
`Closes #348` staged on the slice commit. Each slice closes out
independently; skill-package changes mirror byte-synced; deterministic
gates own closeout; no `#N` anchors in skill-package files (carriers live
in commit messages only).

## Non-Goals

- Do NOT take on **#184** (product success metrics) — FIFTH consecutive
  deliberate exclusion; it is product-level and needs an operator
  `ideation` session shaped into its own goal.
- Do NOT push or cut a release inside this goal — the second 2026-06-10
  push + release lane precedes activation (operator-ordered in the shaping
  session); slice 1 verifies it read-only. The carriers staged by slices
  2-3 land on the NEXT operator push.
- Do NOT manually close #346/#348 — their staged carriers own the close;
  this goal validates the closeout drafts and the next-queue goal verifies
  CLOSED state after the push that carries them.
- Do NOT copy ceal host facts (`ceal-ops` commands, Slack/Sheets surfaces,
  ledger schema paths, channel names) into the charness skill text — they
  are adapter-owned per the portable-skill authoring contract; the skill
  ships the concepts, statuses, and proof rules.
- Do NOT take on ceal-side consumption (wiring the adapter in ceal,
  retiring its repo-local `close-loop`) — that is ceal's follow-up, named
  in #348 as planned consumption.
- Do NOT mutate anything under `../ceal` — it is a read-only reference
  checkout for this goal.

## Boundaries

- **Slice 1 — lane verification.** READ/VERIFY-FIRST: `gh run list/view`
  for the post-push quality-core run and the next scheduled mutation run;
  release verification via the release helper's recorded artifacts PLUS the
  live installed-surface probe (installed plugin version == released tag;
  checkout SHA == pushed HEAD). Repairs for CI friction are local-only and
  staged for the next operator push. If the scheduled mutation run has not
  fired/completed within the timebox, record the latest available green run
  and keep the next-run check a named deferred proof (the same pre-resolved
  fallback two prior goals used — GitHub cron slots can be skipped).
- **Slice 2 — #346.** Surfaces: `skills/public/retro/scripts/probe_host_logs.py`
  and `skills/public/achieve/scripts/record_metric_window.py` (+ their
  `plugins/charness/` mirrors and tests). Behavior-preserving for Codex
  hosts and for existing payload keys; Claude scoping must degrade
  gracefully (missing/ambiguous session file -> the current honest
  aggregate-with-caveat posture, never a crash); per-goal scoping is opt-in
  via the same `--goal-path` / window mechanics the Codex path uses. Tests
  cover both hosts' selection logic and the degrade negative. Carrier
  `Closes #346` staged via `issue_tool.py validate-closeout-draft` before
  commit; no `#N` anchors inside skill-package files.
- **Slice 3 — #348 hotl skill.** Route through `create-skill` (public
  skill + adapter classification, failure-mode simulation, portable
  authoring contract). Smallest honest v1: SKILL.md + adapter contract +
  references carrying the preserved close-loop shape (inventory, proof
  packet, execute-or-record, ledger statuses `verified` /
  `blocked-needs-operator` / `blocked-needs-capability` /
  `deferred-by-operator` / `issue` / `accepted-risk` / `out-of-scope`,
  `verified_against` staleness refs, and the proof rules: normalized match
  != rendering proof, direct post != scheduled-workflow proof, bot smoke !=
  human-ingress proof, mutation proof needs before/after readback, local
  tests don't prove live behavior unless the acceptance class is
  local-only). Helper scripts only where the create-skill contract demands
  them (bootstrap/adapter resolution); heavier ledger tooling may be named
  as a follow-up issue rather than forced into v1. Relationship to `hitl`
  (review inside the loop vs supervising applied behavior) stated in the
  skill text. Implementation reference: read `../ceal/.agents/skills/close-loop/`
  directly (read-only); cite the GitHub permalink from #348 as the durable
  source. All skill-package gates (ergonomics, anchors, attention-state,
  lengths, mirror sync, doc links) green; carrier `Closes #348` staged via
  validate-closeout-draft.
- **External side-effect scope:** this goal performs NO push, NO release,
  NO PR; remote access is read-only `gh`. The push + release lane it
  verifies in slice 1 is operator-executed BEFORE activation. Carriers
  staged by slices 2-3 take effect on the next operator push (the next
  goal's verification input, the proven deferred-proof pattern).
- Discuss before activation: RESOLVED — (a) `production_or_live_proof`:
  slice 1 is read-only consumption of the operator-ordered second
  2026-06-10 push/release lane's results; no remote mutation is authorized
  or needed by this goal. (b) `issue_close_or_split`: #346 and #348 are
  close-INTENDED via staged `Closes #N` carriers validated with
  `issue_tool.py validate-closeout-draft`; the closes land on the next
  operator push and the next-queue goal verifies CLOSED state — never a
  manual close. (c) `broad_bundle_scope`: slice 3 creates one new public
  skill package; its scope is bounded to the smallest honest v1 named in
  Boundaries, with ledger tooling explicitly deferrable to a follow-up
  issue. Re-open this item instead of activating if any of these calls is
  wrong.

## User Acceptance

What the user can do to verify completion directly.

- **Slice 1:** the goal artifact's slice log names the post-push
  quality-core run id + verdict, the release-verification evidence
  (installed == released, live probe), and either a green scheduled
  mutation run id over the pushed state or the named deferred-proof line.
- **Slice 2:** on this machine,
  `python3 skills/public/retro/scripts/probe_host_logs.py --repo-root .
  --format markdown` scoped to the current session no longer reports the
  project-dir aggregate as its measured block, and a goal artifact carrying
  a `Host metric window:` line recorded from a Claude session yields a
  scoped `goal_window_audit`; `git log` shows the staged `Closes #346`
  carrier.
- **Slice 3:** `skills/public/hotl/SKILL.md` exists, passes the
  skill-package gates, names the adapter-owned seam, carries the preserved
  proof rules and ledger statuses, and contains no ceal host facts;
  `git log` shows the staged `Closes #348` carrier; the next-queue session
  can wire a ceal adapter without editing the skill text.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched
  file; mirror byte-sync for any exported-script change;
  `check_skill_surface_preflight.py` before prose into the new skill
  package (slice 3); the touched test modules per slice.
- `issue_tool.py validate-closeout-draft` for each staged carrier before
  its commit.
- Slice 2: if a new pool module is added, the new-pool-module advisory's
  early producer+consumer self-check BEFORE the slice commit; walk degrade
  branches in the introducing slice (the closed W1 trend stays closed).

### High-Confidence Checks

- Full relevant test surface green per slice; broad gate
  (`run-quality.sh --read-only`) + changed-line producer
  (`run_slice_closeout.py --base --verification-lock
  --produce-mutation-coverage`) at the bundle boundary, consumer confirming
  0 uncovered. Fresh-eye `critique` at each mutating slice boundary; the
  goal-closeout disposition review at the end.

### External Or Live Proof

- Slice 1 consumes the already-executed push/release lane read-only via
  `gh` + the live installed-surface probe.
- No other remote lane is authorized; the staged carriers' CLOSED states
  are the NEXT goal's verification input after the next operator push.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Verify the second 2026-06-10 push/release lane: post-push quality-core green, release installed-surface verified live, scheduled mutation green over pushed state (retires the carried 39ff5432 deferred proof) | the lane executes immediately after this goal is shaped; consuming its deferred proofs read-only is the proven loop-closing pattern (third iteration) | run ids + verdicts in slice log; live probe output; mutation run id or the named deferred line | planned |
| 2 | #346: Claude-host single-session scoping for probe_host_logs + Claude session source for record_metric_window | recurs-class (two consecutive closeouts hand-caveated); small bounded helper-script change with clear tests | scoped measured block + goal_window_audit on a Claude session; degrade negative; staged Closes carrier | planned |
| 3 | #348: portable hotl public skill (smallest honest v1, adapter-owned repo specifics) from ceal's close-loop reference | operator-requested; the discipline is locked in one repo and ceal maintains portable content locally against the authoring contract; local ../ceal checkout makes reference reading cheap NOW | skill package green under all gates; preserved proof rules/statuses; no ceal host facts; staged Closes carrier | planned |

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
- **Issue closeout step** — #346 (slice 2) and #348 (slice 3) are
  close-INTENDED via `direct-commit` carriers staged on their slice commits
  and validated with `issue_tool.py validate-closeout-draft`; record both
  validations here at completion. The closes land on the next operator
  push; CLOSED-state verification belongs to the next-queue goal. #184 is
  context-only (excluded).
- **Gather note** — the #348 implementation reference is the LOCAL
  `../ceal/.agents/skills/close-loop/` checkout (operator-directed; the
  GitHub permalink in #348 is the durable citation). Reading a local
  sibling checkout is not an external URL fetch; if a durable in-repo copy
  becomes necessary, route that materialization through `gather` and record
  the asset here, else record `Gather: n/a — local checkout + permalink`.

## Slice Log

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **The completed prior goal + its retro:**
   `charness-artifacts/goals/2026-06-10-postpush-verification-deleted-checkout-scan-pr-mirror.md`
   (`## Final Verification` non-claims: the scheduled mutation run over
   39ff5432 is the carried deferred proof; the PR-mirror blocking arm
   classified an empty set) and
   `charness-artifacts/retro/2026-06-10-postpush-goal-retro.md` (W1 trend
   closed; the probe-attribution waste that became #346; the accepted-risk
   shaping habit whose compensating gate is the activation plan critique).
2. **Open issues:** corca-ai/charness#346 (per-goal metric scoping on
   Claude hosts — pattern/instances/destination split in the body),
   corca-ai/charness#348 (portable hotl skill; preserves ceal close-loop's
   shape, proof rules, ledger statuses; evidence permalink
   `corca-ai/ceal` `.agents/skills/close-loop/SKILL.md` @ `70170c5`),
   #184 (excluded, fifth time).
3. **Local implementation reference (read-only):**
   `../ceal/.agents/skills/close-loop/SKILL.md` (104 lines) and its
   surrounding skill dir — operator-directed faster path than the GitHub
   permalink for slice 3 reference reading.
4. **Handoff:** `docs/handoff.md` (Next Session: push lane, deferred
   mutation proof, #346 candidate, #184 exclusion).
5. **Recent lessons:** `charness-artifacts/retro/recent-lessons.md`
   (release-helper persistence note slice 1 leans on; W1
   confirm-not-discover; the prior goals' lane-verification pattern).
6. **Surfaces to touch:** `skills/public/retro/scripts/probe_host_logs.py`,
   `skills/public/achieve/scripts/record_metric_window.py` + mirrors +
   tests (slice 2); `skills/public/hotl/**` (new, slice 3, via
   `create-skill`); `gh run list/view` (slice 1).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (operator-directed: "이번 세션 교훈, handoff, 열린 이슈,
  최근 레슨 포함해서 다음 할 일", followed by an operator-ordered push +
  release lane).** Family: {lane verification; #346; #348; #184; defer #348
  to its own goal}. Chosen: **verification + #346 + #348** — the first
  consumes the lane the operator just ordered (third iteration of the
  proven deferred-proof pattern) and retires the carried mutation-run
  proof, the second closes the recurs-class gap this session's retro filed,
  the third is the operator's explicit request with a cheap local
  reference. Rejected: #184 (fifth exclusion — product-level, needs
  operator ideation as its own goal); deferring #348 (it is the largest
  slice but bounded to a v1 skill package, and the operator named it now
  with the ../ceal shortcut).
- **#348 design scope (probe, not fixed).** Family: {full skill + ledger
  tooling + helper scripts; SKILL.md + adapter contract + references v1;
  support skill instead of public}. Chosen direction: **public skill,
  smallest honest v1** via `create-skill` classification — the issue
  explicitly leaves design to charness and names the public/support/adapter
  decision as create-skill's; ledger tooling is deferrable to a follow-up
  issue if v1 cannot carry it honestly. Pre-rejected: copying ceal host
  facts into skill text (authoring-contract violation, named in the issue
  itself).
- **#348 reference path.** Family: {GitHub permalink fetch via gather;
  local ../ceal read; in-repo materialized copy}. Chosen: **local ../ceal
  read-only** (operator-directed, faster) with the permalink as durable
  citation; gather-materialization only if a durable in-repo asset becomes
  necessary at slice time.
- **#346 mechanics (probe, not fixed).** Deferred to slice-time
  verify-first — but behavior-preservation for Codex hosts and
  degrade-to-current-posture on Claude ambiguity are fixed in Boundaries.
- **Activation timing.** Activate AFTER the operator's push + release lane
  completes (the lane runs in the same session this goal is shaped); slice
  1's mutation-run check inherits the cron-skip fallback two prior goals
  pre-resolved.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. A fresh-eye plan critique runs at
activation per the verification cadence.

- **Provenance:** self-critique by the shaping session.
- **Slice 3 could blow the timebox (a whole new public skill).** Folded:
  smallest-honest-v1 boundary with ledger tooling explicitly deferrable to
  a follow-up issue; `create-skill` owns the classification so the slice
  does not improvise structure; the 4h timebox (vs 3h prior) prices the
  larger slice.
- **Slice 3 could leak ceal host facts into portable text.** Folded:
  Non-Goal + Boundaries name the adapter-owned seam and the concrete fact
  classes (commands, surfaces, schema paths, channels); User Acceptance
  checks "no ceal host facts".
- **Slice 2 could break the Codex path or existing payload consumers.**
  Folded: behavior-preservation and degrade boundaries fixed; both hosts'
  selection logic and the degrade negative are named test evidence.
- **Carrier staging could repeat the #347 duplicate-filing slip.** Folded:
  carriers are commit-message-only (no new issue filing in this goal);
  validate-closeout-draft runs before each carrier commit.
- **Slice 1's mutation-run check may idle on a skipped cron slot again.**
  Folded into Boundaries: the pre-resolved record-latest + named-deferred
  fallback, with no idle wait required by the goal text.
- **Over-worry (raised, not folded):** that reading ../ceal couples
  charness to ceal's current state — the permalink in #348 pins the exact
  reference revision, and the skill ships concepts, not ceal code.

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
