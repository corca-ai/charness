# Achieve Goal: North-Star Autonomous Two-Hour Release Round 4

Status: active
Created: 2026-07-13
Activation: `/goal @charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-4.md`
Timebox: 2h
Activation time: 2026-07-13T15:04:06+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad for the user-authorized implementation-
continuation run.

## Active Operating Frame

- Current slice: Slice D — full-bundle quality and release lock.
- Current slice intent: turn the admitted slices and lens non-changes into one
  honest release-readiness record, adversarial critique, and clean verification
  lock before any publication mutation.
- Next action: close and commit the Codex cache speed slice, then run the final
  distinct quality lenses and bundle proof.
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

Spend two hours improving Charness from distinct bug, maintainability,
test-economics, portability, security, and operator perspectives. Admit changes
only from reproduced failure or measured cost, then push and publish one
independently verified release.

## Non-Goals

- Do not close #433, #436, or any other tracked issue; their lifecycle requires
  separate explicit authority and behavioral closeout.
- Do not manufacture a change for every lens, optimize line or gate counts, or
  weaken proof merely to make the suite faster. A measured no-change decision
  is a valid perspective result.
- Do not add a blocking floor for a first-sighting reversible failure when an
  advisory, cleanup, ownership split, or existing gate can answer it.
- Do not alter compatibility or remove public surfaces without a separately
  reviewed migration case.

## Boundaries

- Reversible mutation is authorized until the closeout reserve begins at
  2026-07-13T16:44:06+09:00. Optional incomplete work stops there; only clean,
  reviewed, committed slices enter final verification.
- Publication may begin only after source/generated sync, bundle critique,
  clean verification lock, release dry-run, fresh-checkout proof, and
  close-keyword scan pass.
- The release target starts as patch candidate `1.0.2`; semver review over the
  complete delta may raise but never silently lower the bump.
- GitHub is the adapter-owned publication provider (`axis: release-provider`),
  while public success must be confirmed by a different observer through an
  unauthenticated content-bearing channel.
- Any mutation after the final verification lock invalidates the lock. Tags are
  never deleted or repointed as automatic rollback.
- If #433 or #436 informs a candidate, first read its live body and comments and
  record that source plus a current reproduction. OPEN tracker state alone is
  not admission evidence.
- Remote CI, if used, belongs to the final bundled release lane unless a
  runtime-affecting slice explicitly needs earlier remote proof.

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- At least three distinct lenses produce recorded evidence and an explicit
  admit/defer/no-change decision; code changes trace to a reproduced failure or
  measured operator/runtime cost.
- Focused tests prove each implementation slice; the full bundled quality gate,
  security/supply-chain checks, generated-surface parity, and clean-tree
  verification lock pass without weakening existing contracts.
- Test-speed work reports before/after measurements from the same command and
  preserves coverage; if no safe speedup is found, the goal records that
  non-claim instead of fabricating one.
- GitHub exposes the final release and tag; a separate observer confirms
  substantive public content over unauthenticated HTTPS, followed by installed
  version and doctor/readiness proof.

## Agent Verification Plan

### Low-Cost Checks

- Quality planner evidence packets, focused pytest, ruff/pycompile, surface and
  packaging parity, artifact preflights, and pre-lock slice closeout.
- Security proof uses `./scripts/check-secrets.sh` and
  `python3 scripts/check_supply_chain.py --repo-root .`.

### High-Confidence Checks

- Fresh bounded code/quality critique with reviewer-boundary fingerprints;
  final `run_slice_closeout.py --verification-lock` with mutation coverage when
  eligible Python production code changes.
- Full delta semver/release critique, release-helper dry-run, fresh-checkout
  probes, and clean-tree proof.

### External Or Live Proof

- Publish only through the repo-owned release helper under the user's explicit
  final push/release authority.
- Confirm tag, release title/body/assets, remote branch, and installed version
  through a different observer and a content-bearing unauthenticated HTTPS
  read; do not treat helper green as terminal success.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Measure the current quality and runtime-test posture | Start from repo-owned evidence rather than backlog intuition | planner packets, runtime summary, focused inventories, candidate ledger | complete |
| B | Implement the highest-leverage reproduced bug or structural seam | Reversible work should serve an observed escape/cost | focused regression proof, before/after signal, code critique, commit | complete |
| C | Probe independent test-speed, portability, security, and operator lenses | Counter implementation anchoring and admit only supported work | distinct-lens admit/defer/no-change decisions; optional second clean slice | complete |
| C2 | Move duplicated Codex cache payload proof below the CLI boundary | Serial timing found 4.4-5.7s update scenarios around existing pure helpers | same-command focused before/after, retained real-boundary smoke, critique | complete |
| D | Freeze and verify the full bundle | Prevent local greens from becoming release confidence | quality artifact, bundle critique, verification lock, release dry-run | pending |
| E | Push and publish | User-authorized irreversible boundary | remote/tag/release reads, HTTPS second-observer proof, install/doctor evidence | pending |

### Candidate Ledger Schema

Each Slice A/C lens writes one Slice Log entry before Slice B consumes it:
`lens`; `pain/evidence`; `repro-or-measurement-command`; `owner`; conditional
`producer / consumer / owning surface / verdict` when shared or generic code is
crossed; `decision: admit|defer|no-change`; `proof-artifact`; `non-claim`.

### Acceptance Check Map

| Acceptance | Executed proof | Durable slot |
| --- | --- | --- |
| Three distinct evidence decisions and traceable admitted work | candidate ledger entries plus each slice's exact focused command | `## Slice Log` and quality artifact |
| Bundle quality, security, supply chain, parity, and clean lock | `run_slice_closeout.py --verification-lock`, secrets and supply-chain commands, packaging/surface checks | quality artifact and `## Final Verification` |
| Same-command speed comparison without coverage loss | identical before/after command, result and coverage-preservation field; or explicit no-speedup non-claim | candidate ledger and slice report |
| Public release, second observer, install and doctor | release-helper dry-run/publish payload, unauthenticated HTTPS content read, installed version and doctor/readiness | release artifact, disposition review, and `## Final Verification` |
| Pursue readiness and lifecycle completion | `check_goal_artifact.py --pursue-ready` before activation; closeout-shape and complete validator before host completion | this goal artifact |

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

none — the user explicitly authorized autonomous local work, push, and release;
new issue closure, compatibility removal, or external provider writes outside
the release helper remain out of scope.

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

Routing: quality -> impl -> critique -> release — quality selects evidence-admitted moves, impl owns reversible slices, critique supplies fresh observers, and release owns publication.
Gather: n/a — no external URL needs conversion into working context; existing repo artifacts are the source set.
Issue closeout: n/a — #433/#436 are context-only and remain open.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: approved — the user's request explicitly authorizes
  the two-hour implementation-continuation run plus final push and release;
  issue closure and compatibility removal are excluded, patch `1.0.2` remains
  provisional until bundle semver review, and publication success requires a
  distinct observer plus a different evidence channel.

## Slice Log

### Slice 1: Slice A — measured candidate admission

- Objective: Measure bug, maintainability, test-economics, portability, security, and operator evidence before selecting implementation.
- Why this approach: The north star requires judgment on reversible work and rejects nominal churn; repo-owned planners and same-command timings identify real cost before edits.
- Commits: pending — this plan/evidence artifact unit will commit before implementation
- What changed: Candidate ledger: test-economics | five runtime-aggregate tests each 3.74-3.85s because their spy launches 83 Python recorders | exact focused command | owner tests/quality_gates/test_quality_runner_runtime_aggregate.py | decision admit | proof focused before/after | non-claim production runner is not slow here. Bug/operator | issue resolve with forbidden --target calls gh auth before deterministic rejection | host/fake-gh timings | owner issue_plan.command_plan | decision admit | proof in-process no-backend-call plus CLI rc/payload. Bug/operability | transient root uv.lock | direct falsifiers and strace | decision no-change | proof debug artifact | non-claim writer unknown. Security | secrets and supply-chain passed | decision no-change. Portability/structure | host-reference heuristics and 1.03 test-production ratio are advisory without an ownership defect | decision defer/no-change.
- Alternatives rejected: Rejected removing standing proof, moving markdown off local proof without exact CI equivalence, broad managed-install test deletion, a new uv.lock guard from disconfirmed attribution, and line-count-only cleanup.
- Targeted verification: ./scripts/run-quality.sh --read-only passed 81 phases in 60.6s; canonical standing pytest passed 4567 tests in 39.84s; runtime summary median pytest 48.1s/read-only quality 61.9s; debug artifact validator passed; three read-only scouts returned concrete evidence.
- Test duplication pressure: No tests added in Slice A; advisory test/production ratio is 1.03 and structural-waste inventory returned no candidates.
- Critique: Goal-plan spec critique used two angles plus separate counterweight; all parent-delegated reviews verified zero worktree/index drift.
- Off-goal findings: Managed-install and Codex cache boundary-test refactors are evidence-backed but deferred until the smaller admitted slices are complete; #433/#436 remain context-only.
- Lessons carried forward: Temporal adjacency is not writer attribution; optimize test spies and invalid-input ordering only where focused observations preserve the actual contract.
- Metrics: quality 60.6s; standing pytest 39.84s; 4567 tests; focused runtime-aggregate baseline 19.5s/6 tests; issue invalid-target host 1.48s wall vs fake gh 0.74s.

### Slice 2: Slice B — runtime aggregate test call-spy

- Objective: Remove repeated Python recorder startup from aggregate-runtime tests without changing production behavior or proof depth.
- Why this approach: Measured focused duration showed five tests at 3.74-3.85s each; the test spy launched 83 recorder processes per run while direct recorder tests already owned implementation fidelity.
- Commits: pending
- What changed: Only tests/quality_gates/test_quality_runner_runtime_aggregate.py: the generated python3 wrapper now intercepts the exact recorder path, parses four known fields, writes JSONL, and preserves aggregate failure exit 73.
- Alternatives rejected: Rejected production runner changes, assertion deletion, general JSON serializer work, and moving recorder contract coverage out of its direct test module.
- Targeted verification: Focused module improved from 6 passed in 19.5s to 6 passed in 5.81-5.92s. Combined aggregate plus direct-recorder modules passed 38 tests in 14.17s; ruff passed.
- Test duplication pressure: No new test cases; existing 6 aggregate assertions and 32 direct recorder tests remain. Test helper grew 27 lines but removes roughly 415 Python process launches across the five slow cases.
- Critique: Short fresh-eye review APPROVE: exact interception, JSON shape, rc=73, fallthrough, and direct recorder ownership verified; zero reviewer-boundary drift. Caveat: generic JSON escaping is intentionally outside the constrained call-spy values.
- Off-goal findings: Managed-install and Codex cache boundary refactors remain deferred; no production quality-runner defect claimed.
- Lessons carried forward: A test double should model the call contract at the cheapest honest layer; separately owned direct tests keep implementation fidelity.
- Metrics: focused 19.5s -> 5.81s, about 70 percent faster; combined 38 tests 14.17s.

### Slice 3: Slice C — local issue misuse before remote preflight

- Objective: Return the existing resolve-target usage error before backend/auth preflight while preserving adapter precedence and valid paths.
- Why this approach: A standing test measured 5.48s because deterministic invalid input paid live GitHub auth latency; fake delay proved the remote probe was the cause.
- Commits: pending
- What changed: Moved the resolve+target guard after invalid-adapter handling and before resolve_backend; synced public issue source to plugin mirror; added exact in-process no-call regression and host-independent subprocess fixture; resolved the debug record.
- Alternatives rejected: Rejected changing valid preflight behavior, moving validation into the backend, adding broad parse audits, and duplicating exact payload assertions across both test layers.
- Targeted verification: 48 focused issue tests passed in 3.49s; the formerly slow target case no longer appears above 0.09s in the module durations; ruff, source/plugin cmp, packaging validators, and boundary escalation check passed.
- Test duplication pressure: One focused in-process regression added; existing subprocess regression stabilized. Intent remains visible at both seam and public CLI layers; no broad duplicate gate pressure observed.
- Critique: Full public-skill code critique: two angles plus separate counterweight APPROVE with no Act Before Ship findings; optional intersection test classified valid-but-defer and duplicate subprocess exactness over-worry; every reviewer fingerprint verified zero drift.
- Off-goal findings: Broader issue CLI local-error ordering audit is diagnostic-only; #433/#436 lifecycle untouched.
- Lessons carried forward: Deterministic local usage errors belong after configuration-shape validation but before provider readiness; prove absence with a no-call sentinel, not timing alone.
- Metrics: host invalid command ~0.48s, immediate fake gh ~0.07s, fake 2s auth 2.10s before repair; focused suite 48 passed in 3.49s.

### Slice 4: Slice C2 — Codex cache proof economics

- Objective: Remove duplicated full-update cost while preserving official app-server, update-wiring, and actual rotation/staleness evidence.
- Why this approach: The focused file measured 22.30s, with four update-boundary calls around behavior already exposed by pure cache helpers.
- Commits: pending
- What changed: Retained two real update tests; folded actual rotation/staleness assertions into the official refresh smoke; moved stable/no-diff and unrelated-cache assertions to diff_cache_entries/session_staleness_payload.
- Alternatives rejected: Rejected mocking the app-server seam, removing the real rotation payload assertion, changing production, and adding the optional full-diff assertion after approval.
- Targeted verification: Same focused command: 7 passed in 22.30s before; 6 passed in 14.02s parent run after (worker repeats 9.85-13.53s); ruff and diff check passed.
- Test duplication pressure: Two redundant full update calls were removed, one pure helper scenario replaces them, and the distinct real-boundary assertions remain in one smoke.
- Critique: Fresh-eye APPROVE on the frozen diff; reviewer fingerprint verified zero drift. A prior overlapping review was quarantined after fingerprint drift and supplies no approval.
- Off-goal findings: Full-suite benchmark not claimed; managed-install serial costs remain deferred.
- Lessons carried forward: When several scenarios pay the same slow boundary, keep one content-bearing boundary proof and move only directly owned pure transformations below it.
- Metrics: focused 22.30s -> 14.02s parent confirmation (37%); fastest repeat 9.85s; test count 7 -> 6 with retained app-server and update wiring.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- [design north star](../../docs/design-north-star.md) — judgment on reversible
  work and provisional, different-channel proof at publication.
- [handoff](../../docs/handoff.md) — current v1.0.1 state and explicit #433/#436
  lifecycle boundaries.
- [recent lessons](../retro/recent-lessons.md) — avoid duplicate coverage runs,
  post-proof tracked drift, and unbound reviewer envelopes.
- [round-three goal](2026-07-12-north-star-autonomous-two-hour-release-round-3.md)
  — prior timebox/release pattern and its non-claims.
- [latest quality record](../quality/latest.md) and [latest release
  record](../release/latest.md) — current evidence baseline.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only vs implementation-continuation; chose continuation
  because the user explicitly requested two hours of autonomous iteration plus
  push and release.
- Scope family: predetermined backlog vs evidence-admitted lenses; chose the
  latter so OPEN tracker state alone cannot manufacture a duplicate fix.
- Release family: no publication vs patch candidate vs compatibility release;
  chose patch candidate `1.0.2`, subject to final-delta semver review.
- Provider value: `axis: release-provider`; GitHub publication follows the
  release adapter, but verification varies observer and channel.
- Host/model values: `axis: host` and `axis: reviewer-tier`; coding workers use
  a lower-power model under repo policy, while high-leverage reviewers remain
  adapter/host resolved rather than becoming global defaults.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Execution: two bounded spec-critique angles plus a separate counterweight;
  all three returned `Fresh-Eye Satisfaction: parent-delegated` and rail-1
  reviewer-boundary verification reported zero drift after each review.
- Packet Consumed:
  [round-4 goal plan packet](../critique/2026-07-13-round4-goal-plan-packet.md).
- Reviewer Tier Evidence: requested tier `high-leverage`; adapter fields
  `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority` were sent;
  host exposure state `requested_fields_sent`; provider application is not
  claimed.
- Act Before Ship (applied): define the candidate/lens ledger; map every user
  acceptance claim to executable proof and a durable slot; require live issue
  reads plus current reproduction before #433/#436 can inform work.
- Bundle Anyway (applied): align the security lens, name the repo security and
  supply-chain commands, add conditional boundary-ownership fields, bind
  release/retro proof slots, and keep remote CI in the final bundle lane.
- Over-Worry: do not preselect a bug, create a full planner ontology, require
  boundary ownership for local-only candidates, or run remote CI per slice.
- Valid but Defer: automate ledger completeness only after an observed
  recurrence; exhaustive #436 writer audit stays outside this run.

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
