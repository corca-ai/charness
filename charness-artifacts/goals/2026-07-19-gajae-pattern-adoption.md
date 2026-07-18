# Achieve Goal: Complete evidence-bound Gajae pattern adoption

Status: active
Created: 2026-07-19
Activation: `/goal @charness-artifacts/goals/2026-07-19-gajae-pattern-adoption.md`

This file is the living goal scratchpad. The user activated implementation
continuation in the originating session with “진행 시작” and explicitly
authorized final push plus release; the activation command remains the portable
resume form for a fresh host session.

## Active Operating Frame

- Current slice: Slice 6 — final bundle proof and publication.
- Current slice intent: lock the cumulative diff, run mutation-aware broad
  verification, then publish through the release helper with distinct-channel
  and installed-state evidence.
- Next action: commit the proven probe slice, record the final verification lock,
  complete goal/retro/handoff closeout, and enter the authorized release phase.
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

Implement and prove Slices 1-4 from the canonical Gajae-Code adoption plan, disposition governed probes without silent promotion, then push and publish a verified Charness release.

## Non-Goals

- Do not copy Gajae-Code's tmux/team runtime, Bun/TUI process machinery, npm
  release closure, mandatory consensus workflow, or LOC-based delegation rules.
- Do not narrow CI or add production session indexing without the plan's
  measured probe and promotion threshold.
- Do not treat a digest, receipt, gate, or reviewer verdict as terminal truth at
  release or another irreversible boundary.
- Do not reopen D18 unless the operator explicitly changes that disposition.
- Do not run Cautilus unless its repo planner names a warranted lane and the
  ask-before-run contract is satisfied.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Local edits, tests, generated-surface sync, critique/goal/retro/handoff
  artifacts, and per-slice commits are authorized. Push and release are
  authorized only for the final verified bundle, not intermediate slices.
- Host axis: Claude and Codex remain supported; Codex app-server details stay in
  the root CLI adapter rather than public skill contracts.
- Evidence axis: operator CLI output remains YAML-first; JSON is limited to
  protocol wire data and program-consumed durable schemas.
- Efficiency axis: cost deltas require comparable corpus/signal/model/parser
  identity and remain adjacent to correctness/outcome evidence.
- Stop condition: stop only on an unresolved product decision, unavailable
  required distinct-channel proof, or a failing gate that cannot be repaired
  within the canonical plan.

## User Acceptance

- Run focused app-server, critique binding, release observer, and efficiency A/B
  tests named in the slice log.
- Run the final locked repo closeout and see all standing gates pass.
- Inspect the release artifact and public GitHub release, then run
  `charness version` and `charness doctor` to confirm installed version and no
  source/cache drift.
- Inspect the canonical spec's `Probe Outcomes` and see every governed probe
  explicitly promoted or retained without silent scope expansion.

## Agent Verification Plan

### Low-Cost Checks

- Focused pytest files for each changed owner plus importer/registry coverage.
- Markdown, doc-link, artifact, packaging/mirror, ruff, compile, and changed
  surface checks as applicable.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.

### High-Confidence Checks

- Fresh-eye bounded critique for each meaningful code/contract slice.
- Exact tamper/negative fixtures for response deadlines, reviewed-input
  staleness, observer schema, and incomparable efficiency runs.
- Final `run_slice_closeout.py --verification-lock`, with mutation coverage when
  eligible Python pool files changed.

### External Or Live Proof

- Final push/tag/GitHub release through the repo release helper.
- Public release readback through a channel distinct from the release backend,
  then post-publish install refresh and separate `version`/`doctor` readback.
- No real-host app-server behavior claim unless the availability-gated probe is
  actually executed and recorded.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Bound Codex app-server response waiting | Only demonstrated correctness escape in the comparison | Negative fake-server matrix, compatible YAML, focused critique | completed |
| 2 | Bind critique verdicts to declared reviewed inputs | Durable review claim must identify what was judged | Identity/tamper fixtures, validator and artifact sync | completed |
| 3 | Generate one release observer from existing distinct-channel evidence | Avoid parallel success records at the irreversible boundary | Schema/renderer fixtures and release integration proof | completed |
| 4 | Add A/B comparability and retain outcome adjacency | Improve token efficiency without persuasive incomparable deltas | Comparable/incomparable report fixtures and focused tests | completed |
| 5 | Disposition governed probes | Prevent analogy from silently becoming runtime/CI scope | Recorded probe outcome and promotion/defer rationale | active |
| 6 | Final bundle proof, push, and release | User requested publication only after all work is complete | Locked closeout, distinct review/channel, public+installed readback | planned |

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

none — the operator already approved the final push/release boundary; no
credentials or product decisions are currently missing.

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

- Routing: `achieve` coordinates the long goal; `impl`/`prove` own each build
  slice, `quality` owns bundle verification, and `release` owns publication.
- Gather: `charness-artifacts/gather/2026-07-19-gajae-code-pattern-review.md`.
- Release: authorized for the final verified bundle; proof path will be added at
  closeout.
- Issue closeout: n/a — this goal does not claim a tracked GitHub issue.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — the operator approved broad Slices 1–4
  plus governed probe disposition and explicitly authorized final push/release;
  intermediate publication and unproven speed claims remain excluded.

## Slice Log

- Slice 1 completed — root cause: response timeout was recreated per received
  line instead of owned by the request. Added `wait_for_jsonrpc_response` with
  caller-supplied absolute deadlines; both initialize and plugin/install now
  have independent non-renewable budgets. Seventeen focused cache-refresh tests
  cover continuous unrelated messages, malformed JSON, EOF, initialize error,
  matching plugin error, and public failure envelopes. `ruff`, compile, debug
  artifact validation, and pre-lock slice closeout passed. Fresh-eye review
  moved from HOLD to SHIP after integration failure coverage was added; parent
  boundary fingerprints verified no reviewer mutation. Durable debug record:
  `charness-artifacts/debug/2026-07-19-codex-app-server-deadline.md`.
- Slice 2 completed — critique packets now capture a canonical declared-path
  identity across content, staged/unstaged patches, untracked inputs, and
  changed-ref targets; durable records bind exact packet bytes separately.
  Validator fixtures prove declared changes/tamper stale the verdict while
  unrelated edits/commits do not. Traversal, symlinked-directory, final symlink,
  changed-ref/worktree, explicit-output collision, same-slug rerun, unavailable,
  and retro non-inheritance seams are covered. Seventy-five focused tests plus
  dogfood/skill/packaging/Markdown/static closeout gates passed. Public dogfood
  records the expanded critique output while retro's maintained contract stays
  unchanged. The first review approval was quarantined when the parent mutated
  during its fingerprint window; a clean final snapshot/verify and repaired
  re-review reached SHIP. Critique:
  `charness-artifacts/critique/2026-07-19-gajae-slice2-reviewed-input-binding.md`.
- Slice 3 completed — release closeout now derives one
  `charness.release_observer.v1` record from the canonical distinct-channel
  observation after install refresh plus YAML-first version/doctor readbacks,
  before issue close. Missing commands, runner faults, and persistence failures
  remain typed non-blocking dispositions after publication; both final commit
  paths stage the JSON when available. The slice also repaired a discovered
  structural coupling: historical `--all` critique validation now checks packet
  integrity without requiring old reviewed inputs to equal today's worktree,
  while changed critiques still enforce current applicability. 119 focused
  release/critique tests and the full pre-lock structural closeout passed; a
  bounded review moved HOLD to SHIP with clean parent fingerprints. Critique:
  `charness-artifacts/critique/2026-07-19-gajae-slice3-release-observer.md`.
- Slice 4 completed — the existing A/B result/report owner now requires matching
  source, command, corpus, signal, reconstruction, model, and parser identities
  before emitting a cost delta. Incomparable arms retain raw observations but
  expose no persuasive delta; comparable JSON entries and Markdown rows keep
  capture and outcome-grade pass rates adjacent. Fresh-eye review found and
  repaired aggregate-order baseline inversion and duplicate-declaration
  self-comparison. Comparability tests were split into a cohesive file before
  the original test module reached its hard length limit. 104 focused tests and
  pre-lock closeout passed. Critique:
  `charness-artifacts/critique/2026-07-19-gajae-slice4-efficiency-comparability.md`.
- Slice 5 completed — quality runtime history kept
  affected-CI unchanged because no canonical CI explainer or unknown-path full
  fallback exists and test execution dominates the retained sample windows.
  Goal receipts/leases remain deferred because the discovered stale claim was a
  release-sync failure, not a conflicting goal-state owner. A real Codex 0.144.5
  initialize probe found different result fields plus post-response warning and
  remote-control notifications; the fake-server integration now represents that
  lifecycle without adding a live release dependency. The optional session
  index probe found a 1.7 GiB/322k-row audit cost, but the source SQLite already
  owns the needed indexes: SQL-side aggregation reduced measured wall time from
  4.84 seconds to 1.90–1.96 seconds and peak RSS from 661,492 KiB to about 26,000
  KiB, so no sidecar state or invalidation contract was added. Twenty-eight
  focused tests, ruff, the pre-lock structural closeout, and a clean-fingerprint
  bounded fresh-eye SHIP review passed. Critique:
  `charness-artifacts/critique/2026-07-19-gajae-slice5-governed-probes.md`.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Canonical contract:
  `charness-artifacts/spec/2026-07-19-gajae-code-adoption-plan.md`.
- Gathered source review:
  `charness-artifacts/gather/2026-07-19-gajae-code-pattern-review.md`.
- Plan critique:
  `charness-artifacts/critique/2026-07-19-gajae-code-adoption-plan.md`.
- Governing standard: `docs/design-north-star.md`.
- Session lessons: `charness-artifacts/retro/recent-lessons.md`.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only vs implementation-continuation. Chosen:
  implementation-continuation because the operator said “진행 시작”; rejected
  artifact-only because the plan is reviewed and the user requested completion.
- Publication family: local-only vs intermediate pushes vs final bundle.
  Chosen: final bundle push/release; rejected intermediate publication because
  the user conditioned publication on all work completing.
- Output axis: public JSON vs public YAML with internal JSON. Chosen: YAML-first
  operator output and JSON only for protocol/program consumers, preserving the
  existing multi-host CLI contract.
- Efficiency family: hard blocking metric gate vs evidence-backed advisory.
  Chosen: comparable A/B evidence adjacent to outcome; rejected a universal
  hard gate because reversible work must not be blocked by noisy metrics.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Folded: narrow Slice 1 to per-request deadline/ID waiting; bind verdict
  identity at the critique artifact; derive observer records from existing
  distinct-channel evidence; constrain efficiency comparison to the existing
  A/B owner; govern probes with promotion thresholds.
- Rejected as over-worry: generic JSON-RPC framework, notification-count policy,
  mandatory pipe-buffer choreography, and unconditional SQLite indexing.
- Provenance: two bounded spec angles, separate counterweight, and final
  fresh-eye review all recorded `SHIP` in the canonical critique workflow.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

none — source review findings are either selected in the canonical plan or
explicitly rejected/deferred there.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

Pending execution; final commands and release URL will be recorded at closeout.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
