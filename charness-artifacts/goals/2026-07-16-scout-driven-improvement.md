# Achieve Goal: Scout-driven north-star autonomous improvement

Status: active
Created: 2026-07-16
Activation: `/goal @charness-artifacts/goals/2026-07-16-scout-driven-improvement.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: S2 — provenance-gated update contract for glow/tokei/vulture.
- Current slice intent: flip the three `lifecycle.update` blocks to manual
  (gitleaks precedent; glow/tokei keep go/cargo provenance routing, vulture is
  manual-always), generalize the contract test to every script-mode manifest,
  update the charness_cli fixtures the flip invalidates, mirror the plugin
  copies; one commit expected. S1 done at e1653d73 (SHIP review, gates green).
- Next action: implement S2, run contract + charness_cli update tests
  (incl. release_only update-all e2e), slice closeout, commit; then S3 → S4 →
  S5 (disposition sweep + issues).
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

Close the escape-shaped findings from the five-lens improvement scout: stale session-opening handoff plus its recurrence cause, the provenance-gated update contract gap, compact doctor projection correctness, and P2-misaligned gate messaging — with explicit dispositions for every remaining surfaced finding.

## Non-Goals

- No push to origin and no release publish this run; both are queued as
  operator decisions (see Operator Decision Queue). All work lands as local
  commits on `main`.
- No skill-body split (the impl/SKILL.md P2 re-growth finding) this run; it is
  a medium-cost, review-heavy surface change that gets a tracked issue instead.
- No Cautilus evaluation runs (ask-before-run contract) and no landing of the
  D18 workspace-write carrier; D18 disposition stays operator-owned.
- No proactive splitting of warn-band Python files (repo convention per D33 is
  split at the next module-growing change); only split if a slice's own edit
  trips the 480 hard limit.
- No live Codex provider-applied model/effort experiment (handoff Discuss
  item); queued for the operator.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- This run's external side-effect scope: **GitHub issue creation only** (repo
  contract routes off-goal findings and retro dispositions through `issue`).
  No publish / push / remote-CI / apply lane is approved.
- Behavior-changing scope: flipping glow/tokei/vulture update manifests to
  provenance-gated manual aligns runtime behavior to the already-shipped
  `docs/control-plane.md` contract; it is repo-local until the operator pushes.
- GitHub issue *closing* is out of scope (no tracked issue is being resolved;
  open-issue count is 0).

## User Acceptance

- `docs/handoff.md` reads current v1.0.11 state and its References point at
  v1.0.11-era artifacts; the release closeout carries a presence-checked
  "handoff reconciled" evidence line so a publish forces the reconcile
  question instead of silently leaving the baton on a prior release.
- `charness tool update glow` (or tokei) on a machine where the tool is
  PATH-installed reports a manual next step or routes through the recognized
  go/cargo provenance instead of running another package manager's installer;
  `charness tool update vulture` reports manual-always (uv/pipx/pip are not
  recognized provenance keys); the contract test covers every script-mode
  manifest.
- `charness tool doctor <id>` compact output includes the detected version.
- `python3 scripts/validate_skills.py` over-cap error text states the
  north-star P2 split-or-delete rule instead of "move detail into references".
- Every scout finding not implemented here has a visible disposition: a filed
  GitHub issue, an Operator Decision Queue entry, or a recorded no-change
  reason in this artifact.

## Agent Verification Plan

### Low-Cost Checks

- Per-slice: focused pytest for touched surfaces; `run_slice_closeout.py
  --skip-broad-pytest` at pre-lock commit boundaries (sync-before-verify owned
  by implementation-discipline).
- Manifest mirror integrity: `diff -r integrations/tools
  plugins/charness/integrations/tools` stays clean after S2.

### High-Confidence Checks

- Final bundle: `run_slice_closeout.py --base --verification-lock` (broad
  pytest + deterministic gate battery) over the committed range.
- Fresh-eye bounded-reviewer critique per substantial slice and at closeout,
  with `reviewer_boundary_fingerprint.py` snapshot/verify around each review.

### External Or Live Proof

- None approved this run. Live `update all` execution against network
  installers is deliberately not run (mutates machine state; the manifest
  contract tests plus doctor dry-paths are the proof level). Recorded as a
  non-claim at closeout.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | Refresh `docs/handoff.md` to v1.0.11 and add a post-publish handoff-reconcile step to the release flow shaped as a presence-checked evidence line (P5: force the question, never auto-pass a content grep; any content check is fenced to `## Current State`/`## Next Session` with failure mode "ask") | Session-opening baton is 3 releases stale; round-5 retro improvement unapplied through 3 publishes (recurrence proven) | Refreshed handoff; release closeout carries a required `handoff reconciled` evidence line (or explicit n/a) + test | planned |
| S2 | Complete the provenance-gated update contract: flip glow/tokei/vulture `lifecycle.update` (update only — install stays script) to manual; glow/tokei keep go/cargo provenance routing, vulture is manual-always (no recognized provenance key); mirror plugin manifests; generalize the contract test to all script-mode manifests; audit/update the charness_cli update-all + doctor-output tests and fixtures that seed fake cargo/uv toolchains or pin tokei/vulture script-mode expectations | `docs/control-plane.md` promise shipped in v1.0.11 but 3/6 manifests still guess installers from PATH (live brew-owned glow evidence) | Manifest diffs; extended `test_update_manifest_contract.py` iterating every script-mode manifest; updated `tests/charness_cli` fixtures; mirrors byte-identical | planned |
| S3 | Fix compact tool-doctor projection to carry `observed_version`; point mutating aggregate `next_action` at a non-mutating inspection path | Default doctor output never shows the detected version (dead key); current next_action tells operators to re-run mutating updates | Regression tests in `tests/charness_cli/test_update_output.py`; live doctor output shows version | planned |
| S4 | Align the skill length-gate failure message with north-star P2 and state the cap semantics in `create-skill`; correct the D36 orphan-fingerprint residual note | Gate message instructs the P2-forbidden move at the exact moment of cap pressure; doc points readers at pruned fingerprints | Updated `validate_skills.py` text + test; create-skill line; D36 note marked pruned | planned |
| S5 | Disposition sweep against the enumerated scout-finding inventory (below): file tracked issues / record decisions for impl SKILL.md split, round-5 retro capability+memory items, D18, handoff Discuss item; before filing, dedup against existing open/recently-closed issues; after filing, confirm each created issue URL resolves | Zero open issues + silent debt means nothing routes these; presence-only disposition floor; the inventory makes a silently dropped finding visible | Issue numbers or recorded decisions in this artifact + Operator Decision Queue entries; every inventory row dispositioned | planned |

Per-slice proof cost: S1 medium (release-lane test), S2 medium (contract test
fan-out), S3 small, S4 small, S5 small. Test-duplication pressure: S2/S3 add
tests near existing suites — carry a dup-pressure sample via
`append_slice_log.py --test-pressure` on those slices.

### Scout Finding Inventory (disposition ledger)

Raw findings from the five-lens scout (run `wf_90efafab-b8b`), each with its
disposition route so a dropped finding is visible (plan-critique F4):

| # | Lens | Finding | Value | Disposition route |
| --- | --- | --- | --- | --- |
| 1 | staleness | docs/handoff.md three releases stale (claims v1.0.8; repo at v1.0.11) | high | S1 |
| 2 | north-star-teeth | Four skill bodies within 5% of the 200-line cap; impl re-grew 184→195 in 4 commits (P2 split-or-delete) | medium | S5: tracked issue (Non-Goal this run) |
| 3 | north-star-teeth | validate_skills.py over-cap message instructs the P2-forbidden "move detail into references"; create-skill never states split-or-delete | medium | S4 |
| 4 | gate-health | check_skill_surface_preflight.py at 479/480 code lines | medium | S5: recorded no-change decision (D33 convention: split at next module-growing change) |
| 5 | gate-health | D36 residual note points at orphan fingerprints (3d4af4, d38941) that were pruned at the 1.0.10 re-baseline | low | S4 |
| 6 | retro-debt | Same staleness as #1 plus recurrence proof: round-5 retro reconcile improvement unapplied through 3 publishes | high | S1 |
| 7 | retro-debt | D18 reopen trigger FIRED 2026-07-05, disposition pending operator decision | medium | Operator Decision Queue |
| 8 | retro-debt | Round-5 retro improvement triplet carries no disposition markers (workflow / capability / memory items) | medium | workflow item → S1; capability + memory items → S5 |
| 9 | retro-debt | docs/handoff.md `## Discuss` live-Codex-probe question unowned for two release cycles | low | Operator Decision Queue |
| 10 | correctness | Provenance-gated update contract implemented for only 3/6 script-updated tools; glow/tokei/vulture guess installers from PATH | high | S2 |
| 11 | correctness | Compact tool-doctor projection selects dead `observed_version` key; detected version never shown | medium | S3 |
| 12 | correctness | Mutating aggregate `next_action` tells the operator to re-run a mutating command (`--detail` re-executes updates) | low | S3 |

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

Queue:

- Decision: push this run's local commits to origin/main (and optionally cut a
  release carrying the S2 manifest behavior change)
  - Owner: operator
  - Why deferred: no external lane was granted by the opening instruction;
    all slices are safe as local commits
  - Unblock action: operator approves push (and names whether a release rides)
  - Revisit trigger: next operator session or an explicit push request
- Decision: D18 disposition — land the workspace-write carrier + routing-eval
  `--read-only` wiring now, or explicitly re-defer with a new trigger
  - Owner: operator (the D18 status line names it "pending operator decision")
  - Why deferred: fired 2026-07-05; landing needs a carrier-location choice
    the deferral reserves for the operator, and Cautilus is ask-before-run
  - Unblock action: operator picks land-now vs re-defer; if land-now, choose
    docs/public-skill-dogfood.json entry vs new evals/cautilus fixture
  - Revisit trigger: any session that re-touches the Cautilus eval surface
- Decision: run (or decline) the bounded live Codex probe for provider-applied
  reviewer model/effort evidence (handoff `## Discuss` item)
  - Owner: operator
  - Why deferred: needs a live Codex host session; this run is Claude-hosted
    and the item is explicitly a separate live-host experiment per the handoff
  - Unblock action: operator schedules the probe or records not-worth-proving
  - Revisit trigger: next Codex-hosted charness session

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

- Routing: achieve — goal lifecycle operator for this autonomous run; impl — slice execution discipline (S1–S4); issue — S5 tracked-issue filing; critique — plan/slice/final fresh-eye review via bounded-reviewer; retro — closeout after-action review; handoff — S1 baton refresh shape.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — (1) broad bundled scope (5 slices) is deliberate: the operator's opening instruction is an autonomous-improvement run with the plan delegated to the agent, so scope is settled by that standing instruction plus the Non-Goals fence; (2) no irreversible external lane is taken: push and release publish are explicitly out of scope and queued to the operator; the only external write is GitHub issue creation, which the repo contract itself mandates for dispositions; (3) the S2 behavior change (glow/tokei/vulture update mode) implements the already-shipped control-plane contract rather than introducing new policy, and stays repo-local until pushed; (4) D18's fired reopen trigger is explicitly NOT being landed or re-deferred by this run — it is surfaced verbatim in the Operator Decision Queue because the deferral text names it an operator decision.

## Slice Log

### Slice 1: S1: handoff refresh + post-publish baton reconcile observation

- Objective: Refresh docs/handoff.md from stale v1.0.8 claims to v1.0.11 ground truth and close the recurrence: the release closeout tail now records an adapter-driven baton_reconcile observation (payload + '## Baton Reconcile' artifact section) that forces the reconcile question when the session baton still claims a prior release; opt-in via post_publish_baton_path (this repo: docs/handoff.md).
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 7 unit tests (test_release_baton_reconcile.py) + 2 e2e asserts in the release_only publish test; 56 focused + 14 release_only tests pass; run_slice_closeout --skip-broad-pytest --ack-cautilus-skill-review completed; doc preflight clean; fresh-eye bounded-reviewer verdict SHIP (2 minor should-fixes applied: handoff wording softened to refresh-not-readback, post_publish_* family added to adapter-contract.md); reviewer fingerprint verify ok (zero drift). Cautilus decision: plan not-required (run_mode ask); deterministic tests are the proof level, no eval run. Floor-Addition Restraint: recorded at BATON_SECTIONS site (non-blocking observation, recurrence recorded).
- Test duplication pressure: dup-ratchet: clean after boy-scout dedup (shared tests/quality_gates/release_script_loading.py loader replacing per-file importlib boilerplate in 2 test files) + scoped accept of collateral clustering rotation 895d96962b294ed4 (members untouched pre-existing files: check_prescribed_skill_executed.py + markdown_preview_render.py); baseline 639->640
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: S2: provenance-gated update contract completed for glow/tokei/vulture

- Objective: Flip glow/tokei/vulture lifecycle.update to manual per the gitleaks precedent so no update guesses an installer from PATH: glow/tokei keep go/cargo provenance routing via package_managers metadata, vulture is manual-always (uv/pipx/pip are not recognized provenance keys). Generalized the contract test: every script-mode update command must not 'command -v'-branch across managers (remaining script updates are the canonical single-command agent-browser/defuddle/nose). Removed the now-dead fake cargo/uv update-all toolchain fixtures; retargeted the hand-built tokei rendering example to the truthful package_manager shape.
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: validate_integrations passed (11 manifests); 25 focused control-plane/charness_cli tests pass; 3 release_only update-all e2e tests pass after mirror sync; diff -r integrations/tools plugins/charness/integrations/tools identical; run_slice_closeout --skip-broad-pytest completed
- Test duplication pressure: dup-ratchet clean; net test change: +3 contract tests, -2 dead fixture files
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Five-lens read-only scout workflow, this session (run `wf_90efafab-b8b`,
  5 agents, all completed; findings embedded in the Slice Plan rationale).
  Lenses: stale operator surfaces, north-star gate/skill alignment, test+gate
  health, undisposed improvement debt, latent correctness in recent commits.
- `docs/design-north-star.md` — governing standard (P1–P5).
- `docs/handoff.md` (stale v1.0.8 claims; `## Discuss` item) and
  `charness-artifacts/release/latest.md` (v1.0.11 ground truth).
- `charness-artifacts/retro/2026-07-13-north-star-autonomous-round-5-retro.md`
  — the undisposed improvement triplet.
- `docs/deferred-decisions.md` — D18 (trigger FIRED 2026-07-05, pending),
  D33 (split-at-next-change convention), D36 residual note (orphan
  fingerprints since pruned).
- `docs/control-plane.md:68-70` + commit `d1745d98` — the provenance contract
  S2 completes; `integrations/tools/{glow,tokei,vulture}.json`.
- `charness-artifacts/retro/recent-lessons.md` — read before contract/surface
  changes per repo rule.

## Interview Decisions

No live interview was possible (autonomous run; operator not watching). The
opening instruction settles the high-leverage questions; assumed
interpretations are recorded per the strong-default rule:

- Mode: implementation-continuation (not artifact-only). Family: artifact-only
  draft vs execute-once-activated. The prose "계획해서 진행" (plan it and
  proceed) plus "다이나믹 워크플로우 허용" names execution intent; activation
  is performed in-session under that instruction. Rejected: stopping at a
  draft, which would ignore the explicit "proceed".
- Candidate selection: escape-shaped findings first (stale routing surface,
  contract-vs-behavior gap, lying default output), cosmetic/count findings
  demoted. Family: breadth-first cleanup vs escape-first. Rejected:
  breadth-first, because the north star measures value as escape-closed, not
  count.
- External lanes: local commits + issue creation only. Family: full
  push+release (prior rounds' shape) vs local-only. Rejected: push/release,
  because the opening instruction does not grant an external lane and achieve
  does not push; queued to operator instead.
- Anti-anchoring probe: v1.0.11 as "current version" — single-point: read live
  from `git tag` + `packaging/charness.json` + installed `charness version`,
  not inherited from memory. The `gpt-5.6-terra` subagent request — axis: host
  (Claude Code host does not expose that model field; limitation stated in the
  transcript, session model inherited). Provenance manifests — axis: installer
  ecosystem (go/cargo/brew/pipx per-manifest `package_managers` metadata), so
  S2 must route per-manifest, not hardcode one manager.

## Plan Critique Findings

Reviewer provenance: bounded-reviewer subagent (read-only Read/Grep/Glob),
fresh context, this session; worktree+index fingerprint snapshot/verify around
the review passed with zero drift. Verdict: RESHAPE-FIRST (wording/additive
folds only; no slice restructuring). All folds applied before activation:

- F1 (folded → S2, User Acceptance): vulture has no recognized provenance
  route — `scripts/install_provenance_lib.py` `PACKAGE_MANAGER_KEYS` is
  npm/cargo/go only and vulture.json carries no `package_managers` block — so
  vulture is scoped manual-always; extending provenance keys to uv/pipx/pip is
  out of scope.
- F2 (folded → S2): the mode flip's test blast radius named explicitly —
  `tests/charness_cli/support.py` fake cargo/uv toolchains,
  `test_update_output.py` script-mode label, `test_tool_lifecycle.py`
  selected-tool pins; flip update lifecycle only (glow install stays script).
- F3 (folded → S1, User Acceptance): the recurrence guard reshaped from an
  auto-passing content grep (P5 terminal-green risk; false-fires on legitimate
  historical version mentions in References/Discuss) to a presence-checked
  "handoff reconciled" evidence line in the release record; any content check
  is fenced to `## Current State`/`## Next Session` with failure mode "ask".
- F4 (folded → Slice Plan): added the Scout Finding Inventory ledger so the
  S5 disposition sweep is auditable against an enumerated list.
- F5 (folded → S5, borderline over-worry): dedup against existing issues
  before filing; confirm created issue URLs resolve after filing.
- F6 (over-worry, not folded — recorded as counterweight): D36 prune claim
  verified safe; no existing handoff-refresh helper or release-flow reconcile
  step exists (S1 is not duplicating one); the 3/6 provenance framing and
  gitleaks/ruff/specdown precedent are real.

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
