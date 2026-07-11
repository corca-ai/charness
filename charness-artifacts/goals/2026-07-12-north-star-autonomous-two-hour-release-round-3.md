# Achieve Goal: North-Star Autonomous Two-Hour Release Round 3

Status: complete
Created: 2026-07-12
Activation: `/goal @charness-artifacts/goals/2026-07-12-north-star-autonomous-two-hour-release-round-3.md`
Timebox: 2h
Activation time: 2026-07-12T06:29:46+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement
Host metric window: started_at=2026-07-11T21:29:46Z completed_at=2026-07-11T23:09:46Z codex_session_file=/home/hwidong/.codex/sessions/2026/07/11/rollout-2026-07-11T12-42-43-019f4f45-3606-7892-a931-3a4bfdf739d6.jsonl

This file is the living goal scratchpad for the active round-3 autonomous run.

## Active Operating Frame

- Current slice: public-release lifecycle and goal closeout after eight
  evidence-admitted implementation/probe/review slices.
- Current slice intent: bind public, installed, issue-state, retro, host-window,
  and disposition evidence without reopening the released runtime bundle.
- Next action: finish retro/handoff/disposition evidence at the T+100 closeout
  boundary, flip the goal only after its validator passes, and push lifecycle
  artifacts.
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

Spend two hours improving Charness from distinct operator, behavior,
maintainability, and portability perspectives. Begin with the reproduced #436
residuals, admit later slices only from measured escape or operator cost, and
publish one independently verified patch release.

## Non-Goals

- Do not close #433, #436, or any other issue. This run authorizes code,
  commits, push, and a patch release, not issue lifecycle mutation.
- Do not weaken, skip, or reuse the final broad verification lock across HEADs.
- Do not add a public sync-only CLI or a new blocking floor when moving an
  existing writer/diagnostic to its owning phase is sufficient.
- Do not manufacture five nominal slices or optimize line counts. A no-change
  probe is a successful diverse-perspective result.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- Reversible mutation is authorized until T+100m
  (2026-07-12T08:09:46+09:00); incomplete optional work stops there.
- At T+100, stop any incomplete required slice too: preserve only completed,
  reviewed, committed work; no dirty tree crosses into verification and no
  publication starts when A/B/D proof is incomplete.
- Publication may begin after T+110m only when sync, critique, commits, the
  clean verification lock, quality artifact, semver/version decision, release
  notes, fresh-checkout probes, release dry-run, and issue-close keyword scan
  pass.
- At T+120m, perform only readback/evidence for already-started publication.
- Final push/tag/release is phase-scoped to the reviewed bundle. Release target
  is candidate patch `0.66.4`, subject to full-delta semver review.
- `axis: release-provider` is GitHub single-point because the repo release
  adapter owns GitHub publication; distinct public proof still uses an
  unauthenticated HTTPS channel and a different observer.
- Any mutation after the final verification lock invalidates it and returns the
  run to sync, commit, and verification. Public tags are never deleted or
  repointed as automatic rollback.

## User Acceptance

- A dirty-sync reproduction shows the SLOC inventory writer in the sync phase;
  verification-lock stops before every verify command and broad pytest when it
  creates tracked drift, with an assertion that no verify/broad command was
  invoked. The clean path remains unchanged.
- This slice proves the observed SLOC writer's phase assignment, not an
  exhaustive classification of every present or future write-shaped verifier;
  #436 remains open for evidence-backed siblings.
- A successful mutation-coverage producer payload names its resolved base SHA,
  coverage JSON, and a copyable post-commit consumer command containing
  `--reuse-coverage --require-fresh-coverage`; a roundtrip assertion proves the
  command uses the exact producer `base_sha`, `coverage_json`, and current
  post-commit `HEAD`, and produces a clean changed-line verdict without
  collecting coverage again.
- Each additional slice cites an observed escape/cost and an admission or
  no-change decision from a distinct lens.
- The full v0.66.3..HEAD bundle passes focused proof, fresh-eye critique, final
  clean verification lock, release dry-run, and fresh-checkout probes.
- GitHub exposes v0.66.4; another observer confirms substantive public content
  over unauthenticated HTTPS, installation refresh reports 0.66.4, and #433 and
  #436 remain OPEN after the final lifecycle push.

## Agent Verification Plan

### Low-Cost Checks

- Surface-manifest validation and obligation tests; closeout executor/parser
  tests; mutation producer/consumer tests; ruff, pycompile, mirror parity, and
  artifact preflights.
- Pre-lock closeout with `--skip-broad-pytest` at stable slice boundaries.

### High-Confidence Checks

- Fresh bounded code critique with worktree/index fingerprints before locking
  each substantial slice.
- Final v0.66.3-anchored verification lock, focused mutation-coverage producer,
  emitted exact-base consumer, duplicate ratchet, and clean-tree proof.

### External Or Live Proof

- Publish only through the repo release helper after dry-run and scan exact
  arguments/message/notes for close keywords targeting #433/#436.
- Verify tag/title/value notes/status/assets through a fresh unauthenticated
  HTTPS observer, then refresh installed Charness and run doctor/readiness.
- Read origin/main, tag, release, #433, and #436 separately after publication.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Reclassify the observed SLOC writer in the surface manifest | Repeated post-sync proof drift remains from #436 | surface plan shows sync-before-verify; dirty and clean executor proof | complete |
| B | Expose producer facts and format their exact consumer handoff | A wrong manual base caused an eight-minute duplicate run and 2.8 GB JSON | structured payload fields, wrong/stale negative proof, and roundtrip without recollection | complete |
| C | Probe operator/security/portability siblings | Counter implementation anchoring with genuinely different lenses | bounded evidence plus admit/defer/no-change decision | complete — no mutation admitted |
| D | Full-delta quality and release critique | Freeze one reviewed bundle before the irreversible boundary | quality artifact, release notes, critique, clean verification lock, dry-run | complete |
| E | Push and publish the patch release | User-authorized final external lane | tag/release URL, distinct HTTPS proof, install/doctor and issue-state reads | complete |

## Operator Decision Queue

none — this goal's authorized patch release is complete; #433/#436 lifecycle
remains deliberately outside scope and becomes a future explicit task, not a
decision blocking this closeout.

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

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the find-skills-recommended skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: find-skills -> <skill> — <why this phase needs it>`

Routing: find-skills -> issue — #436 supplies fresh source-of-truth context; impl owns reversible code, quality owns proof, critique owns risk review, and release owns publication.
Gather: n/a — no public source needs conversion into a local knowledge asset; GitHub issue state is read through the issue workflow.
Issue closeout: n/a — #433 and #436 are context only and must remain OPEN.
Release: charness-artifacts/release/latest.md — v0.66.4 public HTTPS, fresh-checkout, install refresh, and non-close evidence.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: approved — the user's request authorizes one final
  push and patch release after the two-hour run; no issue close is authorized,
  v0.66.4 is provisional until semver review, and publication success requires
  a distinct observer plus content-bearing unauthenticated HTTPS evidence.

## Slice Log

### Slice 1: Slices A/B — sync writer and exact-base consumer

- Objective: Eliminate two measured proof-waste seams without weakening the final verification lock.
- Why this approach: #436 residual showed SLOC inventory drift after sync; round-2 retro showed exact-base coverage consumer mistakes caused expensive duplicate runs.
- Commits: `3f8528eb`
- What changed: Moved the SLOC inventory refresh from verify_commands to sync_commands; added producer payload fields mutation_coverage_base_sha, mutation_coverage_json, and mutation_coverage_consumer_command; synced plugin mirror.
- Alternatives rejected: Rejected generic write-shaped verifier detector, public sync-only CLI, and #436 closure.
- Targeted verification: independently rerun 69 focused tests passed;
  validate_surfaces, packaging validators, ruff, source/plugin cmp, security,
  supply-chain, and pre-lock run_slice_closeout --skip-broad-pytest passed.
- Test duplication pressure: Added two focused tests; changed files remain below Python length warn bands.
- Critique: [round3 slices A/B code critique](../critique/2026-07-12-round3-slices-a-b-code-critique.md); final valid post-commit fresh-eye review approved with zero drift. Unauthorized nested reviews and the worker's unrequested commit were quarantined as approvals, not silently counted.
- Off-goal findings: #436 remains open for exhaustive all-writer audit; #433 untouched.
- Lessons carried forward: When emitting copyable commands, separate executable install root from target repo root; prove reuse by asserting source bytes and mtime stay unchanged.
- Metrics:

### Slice 2: Slice C — operator security portability probe

- Objective: Counter A/B implementation anchoring with operator, security, runtime, and release-trigger lenses.
- Why this approach: The goal requires diverse perspectives and accepts no-change probes when no observed escape or cost earns mutation.
- Commits: none — no code change admitted
- What changed: No repo mutation; recorded probe evidence only.
- Alternatives rejected: Rejected optional security/runtime rewrites because executed checks surfaced no blocker; stale runtime samples remain advisory.
- Targeted verification: render_runtime_summary showed pytest 35.7s latest /
  36.8s median within its 140s budget and stale run-quality/read-only samples;
  check-secrets and check_supply_chain passed. Release real-host proof remains
  a final release boundary, not a Slice C claim.
- Test duplication pressure: none — no tests added
- Critique: not-applicable no-change probe; no task-completing repo mutation in this slice
- Off-goal findings: No issue closure; #433/#436 remain context only.
- Lessons carried forward: Diverse perspective does not require nominal mutation when evidence says the current slice should proceed to bundle proof.
- Metrics:

### Slice 3: Issue 433 existing-fix probe

- Objective: Check whether the release closeout-carrier mismatch still needs code
- Why this approach: A live OPEN issue was the next release-operability candidate after A/B
- Commits: none — existing fix is 041aa380
- What changed: No code; verified carrier-file/classification/pre-mutation validation already ships
- Alternatives rejected: Rejected duplicate implementation and issue closure
- Targeted verification: issue body/comments read; 041aa380 inspected; 10 focused release close-issue tests passed
- Test duplication pressure: none — no tests added
- Critique: not-applicable no-change status probe
- Off-goal findings: #433 stays OPEN by goal boundary despite existing behavior fix
- Lessons carried forward: Tracker OPEN and behavior unresolved are different claims; inspect the carrier before adding code
- Metrics:

### Slice 4: Run-quality aggregate runtime observability

- Objective: Refresh mode-level runtime trend evidence on every unfiltered quality run
- Why this approach: latest quality review found the aggregate sample 25 days stale despite successful runs
- Commits: `088840a2`
- What changed: run-quality records full/read-only/release aggregate timing best-effort; six tests moved to a seam-specific module
- Alternatives rejected: Rejected telemetry hard-fail, durable retry queue, and filtered-run samples masquerading as full runs
- Targeted verification: six focused contract/failure tests plus original summary regression; bash -n, shellcheck, ruff, length headroom, fresh-eye approval
- Test duplication pressure: six focused tests in new 132/800-line module; original module restored to 742/800
- Critique: charness-artifacts/critique/2026-07-12-run-quality-aggregate-runtime-code-critique.md; HOLD fixed and final zero-drift approval
- Off-goal findings: none
- Lessons carried forward: Observability must not replace the primary quality verdict; check test-module headroom before adding fixtures
- Metrics:

### Slice 5: Quality runner coverage-selection test split

- Objective: Restore structural headroom without changing quality-gate behavior
- Why this approach: The general runner test module remained in a warning band; the five coverage-selection cases form one stable behavioral seam
- Commits: `039ee871`
- What changed: Moved the existing helper and five coverage-selection tests into test_quality_runner_coverage_selection.py; no production code changed
- Alternatives rejected: Rejected deleting scenarios, weakening assertions, or mixing aggregate-runtime and coverage-selection fixtures
- Targeted verification: five focused scenarios passed; ruff and diff check passed; original module 644/800 and new module 101/800
- Test duplication pressure: none — existing tests moved with assertions preserved; test count unchanged
- Critique: bounded fresh-eye reviewer approved exact move, import cleanup, and cohesive boundary with zero fingerprint drift
- Off-goal findings: none
- Lessons carried forward: Treat structural headroom as ownership design: split a complete behavior seam, not arbitrary line ranges
- Metrics:

### Slice 6: Diverse operator portability proof-economics probe

- Objective: Challenge the current bundle from independent operator, host-boundary, and repeated-cost lenses
- Why this approach: A diverse run should admit only observed escape or waste, not manufacture mutation to satisfy a quota
- Commits: none — read-only probe
- What changed: No code; identified stale handoff semantics for closeout and no additional portability or proof-economics defect
- Alternatives rejected: Rejected speculative host abstraction and removal of the necessary final broad proof
- Targeted verification: source/plugin cmp and packaging/surface/skill/shim/upstream validators passed; current runtime packets stayed within budgets; handoff semantic drift reproduced
- Test duplication pressure: none
- Critique: three independent read-only probes; portability and proof economics returned NO-CHANGE, operator probe bound the handoff refresh
- Off-goal findings: none; #433/#436 remain open
- Lessons carried forward: A structurally valid handoff can still misroute work when semantic state is stale; refresh it after public lifecycle proof
- Metrics:

### Slice 7: v0.66.4 release readiness and critique

- Objective: Turn the complete bundle into a reviewable patch-release contract before irreversible mutation
- Why this approach: Publication must remain provisional until exact-bundle and distinct-channel evidence, while reversible preparation stays lightweight
- Commits: `08fa386c`, `149feb87`
- What changed: Added release-readiness quality record, three-angle release critique with counterweight, and operator-facing v0.66.4 notes
- Alternatives rejected: Rejected issue closure, new CLI/floor, speculative host abstraction, and treating helper green as terminal success
- Targeted verification: quality artifact validator and fresh-eye quality review approved; release angles/counterweight completed with zero reviewer drift
- Test duplication pressure: none — artifacts only
- Critique: charness-artifacts/critique/2026-07-12-v0664-release-critique.md; one nested-spawn review quarantined
- Off-goal findings: Conservative real-host nose checklist remains explicit but does not claim changed nose behavior
- Lessons carried forward: Release notes must teach recovery at the handoff seam, not only enumerate internal commits
- Metrics:

### Slice 8: Narrow release real-host trigger ownership

- Objective: Stop unrelated plugin scripts from triggering a seven-step external-tool host checklist without losing real host-sensitive coverage
- Why this approach: The release planner reproduced the false positive on this bundle; the broad derived plugin wildcard made reversible release preparation pay unrelated operator work
- Commits: `275788b8`
- What changed: Added external-tool-control-plane with exact source/plugin paths; release adapter subscribes to it; added unrelated-derived negative fixture
- Alternatives rejected: Rejected removing host proof, raw-glob duplication, or a generic dependency graph
- Targeted verification: six focused tests, surface/integration validators, dry-run support/update, current delta required=false; initial ownership HOLD fixed and stable reviews approved
- Test duplication pressure: one regression fixture; existing positive/empty/unresolved cases retained
- Critique: charness-artifacts/critique/2026-07-12-real-host-trigger-split-code-critique.md
- Off-goal findings: future host-sensitive files must be added explicitly; actual clean-host proof remains a publication claim
- Lessons carried forward: Trigger surfaces should name the risk seam, not reuse a broader validation surface merely because paths overlap
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- [docs/handoff.md](../../docs/handoff.md) — first move, residual boundaries,
  and non-close authority.
- `https://github.com/corca-ai/charness/issues/436` — live body and comments
  read through `issue_tool.py`; reporter JTBD and non-goals.
- [round2 retro](../retro/2026-07-12-v0663-round2-autonomous-release.md) —
  measured SLOC and changed-line consumer waste.
- [design north star](../../docs/design-north-star.md) — judgment on reversible
  work and distinct-channel proof at publication.
- [release latest](../release/latest.md) — v0.66.3 publication/install state.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only vs implementation-continuation; chose continuation
  because the user explicitly requested two hours of execution plus release.
- #436 classification: deferred-work, not correctness bug; current behavior
  protects proof but repeats operator work. The issue stays open this run.
- Writer mechanism: move the existing command to sync ownership before adding
  a new CLI or generic write detector; the manifest already owns phase order.
- Consumer handoff: structured payload field plus copyable command, not prose
  memory or an automatic second consumer run.
- Additional slices: evidence-admitted probes across distinct lenses, not a
  quota. Security/provider/host values remain axis-specific when encountered.
- Release family: patch `0.66.4` candidate; GitHub publication is single-point
  adapter ownership, while verification must vary observer and channel.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Packet Consumed: [round3 goal plan packet](../critique/2026-07-12-round3-goal-plan-packet.md).
- Fresh-Eye Satisfaction: parent-delegated. Two valid bounded angle reruns and
  one separate counterweight completed with exact command allowlists and zero
  reviewer-boundary drift. Earlier approvals and one unauthorized child-worker
  attempt were quarantined; their code was removed before the valid reruns.
- Fixed/Probe/Defer coherence: Fixed = manifest-owned SLOC phase assignment,
  producer-fact/consumer-command handoff, full-delta proof, and release. Probe =
  optional operator/security/portability sibling, where no-change succeeds.
  Defer = generic write-shaped-verifier detection, public sync CLI, exhaustive
  all-writer claims, issue lifecycle, and any optional slice incomplete at T+100.
- Act Before Ship, folded: state manifest policy ownership separately from the
  writer; expose exact producer `base_sha` and coverage path; require stale or
  wrong-base rejection and no-recollection proof; define required-slice T+100
  recovery; expand the T+110 go/no-go observables.
- Bundle Anyway, folded: A and B share one release but remain independently
  testable/rollbackable; dirty-sync proof asserts verify/broad was not invoked;
  the final review record carries executable invariants and non-claims because
  packet `ok` proves shape only.
- Over-Worry, rejected: no generic detector, public CLI, new blocking floor,
  automatic second coverage run, or issue close. Splitting A/B into separate
  releases is unnecessary.
- Valid but Defer: exhaustive tracked-writer inventory and HEAD-movement cases
  beyond existing changed-pool freshness remain non-claims unless this run
  produces concrete evidence.
- Boundary ownership: manifest owns phase assignment; mutation producer owns
  resolved facts and one copyable handoff string; the existing consumer owns
  verdict semantics. A and B are bundled, not logically coupled.
- Reviewer tier evidence: requested `high-leverage` via adapter fields
  `model=gpt-5.5`, `reasoning_effort=medium`, `service_tier=priority`; host
  accepted fields but provider-side application metadata was not exposed.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- The release planner's broad integration subscription produced an unrelated
  seven-step real-host checklist; Slice 8 moved it to exact host-tool ownership.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-07-12-north-star-autonomous-two-hour-release-round-3-retro.md
Host log probe: charness-artifacts/probe/2026-07-12-north-star-autonomous-two-hour-release-round-3-host-log.json
Disposition review: charness-artifacts/critique/2026-07-12-north-star-autonomous-two-hour-release-round-3-disposition-review.md

- Final locked proof: 4,592 broad tests passed; focused mutation production
  completed in 12.9s and its exact emitted strict-reuse command returned
  `blocking=[]` for base `917239ba` without recollection.
- Release proof: `run-quality --release` passed in 82.9s; fresh-checkout passed;
  v0.66.4 tag/release is public; helper HTTPS and a separate reviewer confirmed
  substantive content; install refresh reports 0.66.4 and 13/13 doctor checks ok.
- Issue-state proof: #433 and #436 were read OPEN before and after publication;
  no issue-close flags or close keywords were present.
- Residual nonclaims: no exhaustive future-writer audit, dynamic dependency
  discovery for host-tool surfaces, Cautilus evaluation, issue lifecycle
  mutation, or non-GitHub publication proof.
- Goal-window efficiency: 1,954 timestamped events, 196 function calls, 233
  custom tool calls, 28 patch applications, two compactions, and 26 reviewer/
  worker spawns were measured from 06:29:46–08:09:46 KST. Necessary safety cost
  included fresh-eye/public proof and repeated fail-closed locks; reducible
  waste was replacement review after envelope violations and one broad run
  before quality evidence fields were machine-readable.

## User Verification Instructions

- Run `charness --version` and expect `0.66.4`; restart active Codex/Claude
  sessions so their cached plugin paths reload.
- Inspect `https://github.com/corca-ai/charness/releases/tag/v0.66.4` and use
  `charness doctor` if host readiness needs a fresh local read.
- Treat #433/#436 as OPEN tracker decisions; this release does not authorize or
  imply their closure.

## Auto-Retro

Retro dispositions: applied: exact inventory evidence fields and reproduction marker landed; applied: external-tool-control-plane plus negative trigger regression landed; applied: handoff now removes completed work and preserves only live issue/nonclaim state.
Structural follow-up: applied: .agents/surfaces.json ownership split plus tests/quality_gates/test_release_real_host.py regression guard
