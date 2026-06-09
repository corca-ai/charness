# Achieve Goal: Next queue — coverage-producer ergonomics + #N-anchor edit-time guard + push/tag CI + source-guard timing audit

Status: active
Created: 2026-06-10
Activation: `/goal @charness-artifacts/goals/2026-06-10-producer-base-nanchor-edittime-pushtag-ci.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: 2 — #N-anchor edit-time guard (portable adapter-declared
  auto-firing for the existing `skill_issue_anchor_scan.py` scan).
- Next action: verify-first — map where the scan runs today (manual /
  commit sweep), then classify the portable firing mechanism (adapter/preset)
  before wiring; slice 1 is done (see `## Slice Log` Slice 1).
- Timebox: ~one focused session per slice (4 slices); Activation time:
  2026-06-10 (session start); Closeout reserve: ~15% for the After-phase proof + retro;
  Done-early policy: continue_next_improvement (if a slice closes early, continue
  to the next surfaced improvement rather than stopping).
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Clear the operator-selected next queue in four independent per-slice-closed-out slices, synthesized from this session's retro, the handoff Discuss items, recent-lessons, the open-issue context, and this session's validator-timing discussion: (1) COVERAGE-PRODUCER RANGE ERGONOMICS — `run_slice_closeout.py --produce-mutation-coverage` defaults to the working-tree diff and no-ops post-commit, forcing a manual `--paths` for the committed range at the bundle boundary (this session's deferred capability); add a `--base <ref>` / origin-default auto-detect so the committed range is covered without manual paths, behavior-preserving for the existing working-tree default. (2) #N-ANCHOR EDIT-TIME GUARD AUTO-FIRING — the skill-package `#NNN` anchor trap recurred 3x+ this cycle, caught only by the commit-time `validate_skill_ergonomics` sweep; the `skill_issue_anchor_scan.py` scan already exists but is manual, so make it fire automatically at edit/preflight time via a PORTABLE adapter-declared mechanism (host-specific firing stays in adapters/presets, the scan stays repo-owned). (3) LIGHT PUSH/TAG CI + CI-PR CHANGED-LINE MIRROR — the handoff Discuss item; the local `--release`/pre-push gate is currently the only bundle proof, so add a light push/tag CI workflow and/or mirror the changed-line gate into a CI-PR check, keeping consumer-inherited behavior unchanged. (4) SOURCE-GUARD TIMING AUDIT — generalize slice 2's move: enumerate the source-guard validators that today run ONLY in the broad gate (not at edit/commit time), classify each by timing-eligibility (cheap + changed-scoped + deterministic + NOT validate-all → favorable to pull earlier; validate-all / expensive → stay at the boundary), and pull EARLIER-timing invocation through the existing dispatcher for ONLY the favorable subset — the validator stays the single portable source of truth (the earlier timing is an extra invocation, never a forked copy), behavior-preserving (earlier feedback, no new enforcement). Produce the classification table as a `docs/conventions` "validator timing-layer" doctrine line. Each slice closes out independently; skill-script changes mirror byte-synced; deterministic gates own closeout; no `#N` anchors in skill-package files (dogfood).

## Non-Goals

- Do NOT take on **#184** (product success metrics — product-level, needs
  `ideation`/`spec`; the operator left it out this round).
- Do NOT cut a release or push as part of this goal — a release/push is an
  operator-authorized lane only; this goal authors CI config + repo-local
  ergonomics, it does not execute remote CI or publish.
- Do NOT introduce NEW blocking behavior for installed-plugin **consumer** repos —
  the push/tag CI is repo-local config and the #N-anchor edit-time firing is a
  PORTABLE adapter-declared mechanism; a consumer without the adapter/CI inherits
  nothing new.
- Do NOT weaken or duplicate the commit-time `validate_skill_ergonomics` sweep —
  slice 2 is ADDITIVE edit-time surfacing; the commit sweep stays the backstop.
- Do NOT change the producer's existing working-tree-diff default — slice 1 adds a
  range option; the default behavior is preserved.
- Do NOT, in slice 4, re-do the #N-anchor guard (that IS slice 2 — its concrete
  proof-of-pattern); pull only the OTHER favorable source-guards. Do NOT pull a
  validate-all guard (debug/quality/handoff-class) or an expensive one
  (mutation/coverage/full-suite) to pre-commit, and do NOT grow the pre-commit
  budget enough to push people to `--no-verify`. Earlier timing is a faster
  feedback LAYER, not a replacement for the broad gate / CI enforcement floor.

## Boundaries

- **Slice 1 — producer range ergonomics.** Add a `--base <ref>` and/or
  origin-default range auto-detect to `run_slice_closeout.py
  --produce-mutation-coverage` so the COMMITTED range is covered without a manual
  `--paths`; the working-tree-diff default is unchanged (no behavior change when
  `--paths`/working-tree is used). A test covers the new range path; the
  fingerprint stamped over the auto-detected range must match the changed-line
  gate's range. Repo-local Python (mirror-sync only if a skill script changes).
- **Slice 2 — #N-anchor edit-time guard.** The scan
  (`skill_issue_anchor_scan.py` / `check_skill_surface_preflight
  --scan-issue-anchors`) stays repo-owned; the AUTO-FIRING mechanism is
  host-specific and MUST be portable — declared via an adapter/preset, never
  hardcoded into a skill core (the portability rule). Behavior-preserving: the
  commit-time sweep stays the backstop; the edit-time guard is additive. No `#N`
  anchors in skill-package files (dogfood).
- **Slice 3 — push/tag CI + CI-PR changed-line mirror.** Author a LIGHT push/tag
  CI workflow (and/or a CI-PR changed-line check) as repo-local CI config; cutting
  a real CI run is post-push (operator lane), not in-slice. Mirror the changed-line
  gate semantics, not a new hard local gate. Behavior-preserving for consumers.
- **Slice 4 — source-guard timing audit.** VERIFY-FIRST: enumerate the
  source-guard validators and where each runs TODAY (author-time preflight /
  edit-time scan / commit-time sweep / broad-gate-only), so the audit does not
  re-pull what is already pulled. Classify each broad-gate-only guard:
  cheap + changed-scoped + deterministic + NOT validate-all => favorable to pull
  earlier; validate-all (debug/quality/handoff-class) or expensive
  (mutation/coverage/full-suite) => stays at the boundary, recorded with the
  reason. Wire the favorable subset's earlier-timing invocation through the
  EXISTING dispatcher (`staged_commit_gate_plan.py` / `check_skill_surface_preflight`),
  never a forked rule copy and never hardcoded into a host hook (portable,
  consumer-inert). Single-source preserved + a test per pulled guard; the broad
  gate stays the enforcement floor. Deliverable: the classification table as a
  `docs/conventions` "validator timing-layer" doctrine (the decision frame —
  one portable validator, invoked at as many cheap timings as fit). Bound the
  pre-commit budget so the pulled checks do not erode the hook.
- **Public-skill + generated-surface scope.** Any skill-script change
  mirror-synced (`plugins/charness/...`); deterministic gates own closeout; no
  `#N` anchors in skill-package files.
- Discuss before activation: RESOLVED — the triggers (`production_or_live_proof`,
  `broad_bundle_scope`) fire on keyword matches (`CI`/`push`/`remote`) in the
  slice-3 prose, not on real consequential decisions in the slices' work. Resolved:
  (a) NO live/prod proof and NO release/push is cut BY THIS GOAL — push/tag CI
  authoring produces repo-local config; the actual remote CI run + any push/tag is
  the operator-authorized lane post-bundle, named as deferred live proof, not a
  per-slice live action; (b) the broad gate + changed-line producer in the plan are
  the STANDARD bundle-boundary cadence, not a broad-scope behavior change, and the
  slice-3 CI check is repo-local + consumer-inert (not a new hard gate consumers
  inherit); (c) NO tracked issue is closed by this goal (#184 is out-of-scope).
  Safe to activate; re-open if a reviewer disagrees.
- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

What the user can do to verify completion directly.

- **Producer ergonomics:** after committing a bundle, the maintainer runs
  `run_slice_closeout.py --produce-mutation-coverage --verification-lock` with the
  new `--base`/auto-detect (NO manual `--paths`) and the committed range's changed
  lines are covered + fingerprint-stamped; the working-tree default is unchanged.
- **#N-anchor edit-time guard:** editing a `#NNN` anchor into a skill-package file
  is flagged at edit/preflight time (not only at the commit sweep), via the
  portable adapter-declared mechanism; a repo without the adapter/hook inherits no
  new blocking behavior.
- **Push/tag CI:** a push/tag triggers a light CI run (and/or a PR carries a
  changed-line check) mirroring the local gate; consumer repos inherit nothing new.
- **Source-guard timing audit:** the goal ships a classification table (each
  source-guard -> where it runs now -> favorable-to-pull-earlier / stays-at-boundary
  + reason) and a `docs/conventions` timing-layer doctrine; the favorable subset
  now fires at edit/commit time via the existing dispatcher (verifiable by editing
  a violating file and seeing it flagged earlier than the broad gate), with the
  validator unchanged as the single source and the broad gate still the floor.
- Each slice: the touched test surface passes, mirror byte-synced, and the
  per-slice fresh-eye critique attests correctness.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths --headroom` on every touched file;
  `check_skill_surface_preflight.py --scan-issue-anchors` on any edited
  skill-package file (dogfood).
- The touched test modules; mirror byte-sync + `validate_skill_ergonomics` for any
  skill-script change; for slice 3, local YAML lint/parse of the CI workflow.

### High-Confidence Checks

- The full quality / relevant test surface green; broad gate
  (`run-quality.sh --read-only`) + changed-line mutation producer at the bundle
  boundary (cover new branches in the introducing slice). Fresh-eye `critique` at
  each slice boundary.

### External Or Live Proof

- The push/tag CI's actual REMOTE execution is an operator-authorized lane
  (post-bundle), NOT run during the goal — named here as the deferred live proof.
  No prod proof otherwise; slices 1–2 are local deterministic surfaces.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Producer range ergonomics: add `--base`/origin-default auto-detect to `run_slice_closeout.py --produce-mutation-coverage` so the committed range is covered without manual `--paths`; working-tree default preserved | this session paid the `Changed paths: none` friction (producer no-ops post-commit, forced `--paths`); the recurring coverage-producer round-trip class | new range option + test; fingerprint over the auto-detected range == changed-line gate range; default unchanged; broad gate green | planned |
| 2 | #N-anchor edit-time guard: make the existing scan fire automatically at edit/preflight time via a PORTABLE adapter-declared mechanism | recent-lessons repeat trap (3x+), accepted-risk to-date; the commit sweep catches it but edit-time friction recurs | edit-time auto-firing wired portably (adapter/preset, not a skill core); commit sweep stays the backstop; consumer-inert; test | planned |
| 3 | Light push/tag CI + CI-PR changed-line mirror, repo-local + consumer-inert | handoff Discuss open item; the local `--release`/pre-push gate is currently the only bundle proof | CI workflow authored + YAML-validated locally; mirrors the changed-line gate; remote run is the operator-lane deferred proof | planned |
| 4 | Source-guard timing audit: enumerate broad-gate-only source-guards, classify timing-eligibility, pull only the favorable (cheap+changed-scoped) subset earlier via the existing dispatcher; single-source preserved | this session's validator-timing discussion — generalizes slice 2; many validators are source guards and the recent single-source templatization makes multi-timing invocation drift-free | classification table + a `docs/conventions` timing-layer doctrine; favorable subset wired earlier (not validate-all/expensive); test per pulled guard; pre-commit budget bounded; broad gate green | planned |

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
- Routing (slice 1): `find-skills --recommend-for-task` (producer --base range
  ergonomics) returned no specific tool/support/workflow route; proceeded as
  repo-local Python impl under `docs/conventions/implementation-discipline.md`,
  fresh-eye bounded subagent critique at the slice boundary per the repo
  contract.
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

### Slice 1: Slice 1 — producer --base range ergonomics

- Objective: Add --base [<ref>] to run_slice_closeout.py so a post-commit closeout covers the committed merge-base(<ref>,HEAD)..HEAD range plus the working tree without a manual --paths list; bare --base auto-detects origin/main (the changed-line gate's range anchor); working-tree default and --paths unchanged.
- Why this approach: The producer fingerprint base (default_mutation_base_sha = merge-base origin/main HEAD) already matches the gate, so only changed-path collection needed the range option — resolve_base_sha/collect_changed_paths_since_base live in surfaces_lib (single git seam), and run_slice_closeout gains a thin _resolve_changed_paths dispatch; the producer's fingerprint anchor is deliberately untouched so producer==gate holds by construction.
- Commits:
- What changed: scripts/surfaces_lib.py (+BASE_AUTO, resolve_base_sha, collect_changed_paths_since_base); scripts/run_slice_closeout.py (--base flag, _resolve_changed_paths, predict-commit guard); plugins/charness/scripts mirrors byte-synced; tests/quality_gates/test_slice_closeout_base_range.py (8 tests, new).
- Alternatives rejected: Making --base also re-anchor the produced coverage fingerprint to the explicit ref — rejected: the pre-push consumer recomputes against merge-base(origin/main,HEAD), so a non-origin anchor would always read stale; documented in the --base help text instead.
- Targeted verification: 8/8 new tests; 118 passed across related modules (slice_closeout_broad_gate, mutation_coverage_producer, staged_commit_gate_plan, surface_obligations, critique_prepare_packet); ruff+py_compile+check_python_lengths green; mirrors diff-clean; live read-only dogfood: run_slice_closeout.py --base --plan-only --json => status=planned, 6 paths (committed range + worktree).
- Test duplication pressure: New module reuses one _seed_repo tmp-git fixture; no duplication with existing closeout tests (they are subprocess CLI-shaped, the new ones are unit-shaped); no existing test copied.
- Critique: Fresh-eye bounded subagent: SHIP-WITH-NITS. Applied N1 (SurfaceError on --predict-commit --base + test), N3 (fingerprint-anchor note in --base help), N4 (raise ... from exc). N2 (empty --paths beats --base) left: consistent with pre-existing empty-paths semantics. Reviewer independently verified broad-pytest proof-cache safety under --base (HEAD sha in fingerprint).
- Off-goal findings: none
- Lessons carried forward: The fingerprint/gate range alignment was already in place; the friction was purely payload path collection — verify-first reading avoided a needless producer re-anchor.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **Producer ergonomics (this session's retro):**
   `charness-artifacts/retro/2026-06-09-closeout-preflight-and-scaffold-validator-citation.md`
   (`## Next Improvements` capability line + `## Waste`: the producer `Changed
   paths: none` / forced `--paths` friction at the bundle boundary).
2. **#N-anchor recurrence (recent-lessons):**
   `charness-artifacts/retro/recent-lessons.md` (`## Repeat Traps` / `## Next-Time
   Checklist` — the `#NNN`-in-skill-package trap recurred 3x+, accepted-risk with a
   recommended edit-time guard; the existing `skill_issue_anchor_scan.py` is manual).
3. **Push/tag CI (handoff Discuss):** `docs/handoff.md` "Discuss" ("No push/tag
   CI") + `charness-artifacts/spec/mutation-changed-line-premerge-gate.md`
   "Deferred Decisions" (mirror the changed-line gate into a CI-PR check).
4. **Surfaces to touch:** `scripts/run_slice_closeout.py` +
   `scripts/check_changed_line_mutation_coverage.py` (slice 1);
   `scripts/skill_issue_anchor_scan.py` + `scripts/check_skill_surface_preflight.py`
   + an adapter/preset (slice 2); a CI workflow surface +
   `scripts/run-quality.sh` / `.githooks` (slice 3).
5. **Validator-timing discussion (slice 4 origin):** this session's exchange —
   many validators are effectively source guards; the recent "templatization"
   (the `check_artifact_surface_preflight` describe-shape work) established the
   single-source needed to invoke one validator at multiple timings; the operator
   asked to extract the broad-gate-only source-guards and pull only the favorable
   (cheap + changed-scoped) ones earlier. The decision frame: one portable
   validator, invoked at as many cheap timings as fit (author -> edit -> commit ->
   bundle -> CI), scaled by cost; pre-commit is a fast LAYER, not the enforcement
   floor (bypassable via `--no-verify`; `check_boundary_bypass_ratchet` guards
   erosion). Existing multi-timing dispatchers: `check_artifact_surface_preflight`
   (registry + `--type`/`--changed-artifacts`/`--emit-stub`) and
   `staged_commit_gate_plan.py` (the pre-commit dispatcher).
6. **Tracked-but-out-of-scope (NOT this goal):** #184 (product metrics — needs
   `ideation`/`spec`).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Which next work (operator-selected).** Family offered: {producer range
  ergonomics; #N-anchor edit-time guard; push/tag CI; #184 product metrics}.
  Chosen: **producer ergonomics + #N-anchor guard + push/tag CI** (operator picked
  1+2+3). Rejected: #184 (product-level, needs `ideation`/`spec`). `axis: theme` —
  each tracked independently, per-slice closed out.
- **Slice 4 added mid-discussion (operator-directed).** Family considered: {leave
  it a one-off opinion; durable `ideation`/`spec` decision artifact only; a WORK
  slice that audits + applies the favorable subset}. Chosen: **a work slice**
  (audit broad-gate-only source-guards, classify, pull only the favorable ones)
  with the classification table doubling as the durable timing-layer doctrine, so
  the principle lands as applied change + doctrine in one slice. Rejected: opinion-
  only (no durable change); doctrine-only (the operator asked for the apply work).
  Scoped to NOT re-do #N-anchor (slice 2) and NOT pull validate-all/expensive guards.
- **Slice 2 firing mechanism (probe, not fixed).** Family: {adapter-declared hook;
  a preset; a hardcoded host-specific hook}. Deferred to slice 2 — must stay
  PORTABLE (host-specifics in adapters/presets per the portability rule); classify
  before wiring.
- **Slice 3 shape (probe, not fixed).** Family: {push/tag CI workflow only; CI-PR
  changed-line check only; both}. Deferred to slice 3 — keep it LIGHT + consumer-
  inert; classify before wiring.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- **Provenance:** self-critique by the shaping session (a fresh-eye plan critique
  runs at activation per the verification cadence; folded blockers below).
- **Slice 2 could embed host-specific firing into a portable skill (the exact
  portability trap).** Folded: the firing mechanism is adapter/preset-declared,
  never hardcoded in a skill core; the scan stays repo-owned (Boundaries slice 2).
- **Slice 3 push/tag CI could add consumer-inherited blocking behavior or a new
  hard gate.** Folded: the CI is repo-local config + the check mirrors the existing
  changed-line gate semantics (no new hard local gate); consumer-inert (Non-Goals
  + Boundaries slice 3).
- **Slice 1 range auto-detect could change the producer's existing default and
  silently re-scope coverage.** Folded: the working-tree default is preserved; the
  range option is additive and its fingerprint must match the changed-line gate's
  range (Boundaries slice 1).
- **Over-worry (raised, not folded):** that push/tag CI duplicates the local
  pre-push gate with no new value — counter: the local gate only runs on the
  maintainer machine; a push/tag CI catches a bypass (a direct push without the
  local hook) and gives a remote authoritative verdict, which the local gate cannot.

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
