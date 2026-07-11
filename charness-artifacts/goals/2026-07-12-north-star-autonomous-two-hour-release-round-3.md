# Achieve Goal: North-Star Autonomous Two-Hour Release Round 3

Status: active
Created: 2026-07-12
Activation: `/goal @charness-artifacts/goals/2026-07-12-north-star-autonomous-two-hour-release-round-3.md`
Timebox: 2h
Activation time: 2026-07-12T06:29:46+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad for the active round-3 autonomous run.

## Active Operating Frame

- Current slice: Slice A/B implementation for #436 residual proof-waste seams.
- Current slice intent: eliminate repeated proof work at the existing sync to
  verify boundary without weakening the final immutable-HEAD lock.
- Next action: implement the fixed SLOC sync ownership and exact-base coverage
  consumer handoff, then run focused proof and fresh-eye code critique.
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
| A | Reclassify the observed SLOC writer in the surface manifest | Repeated post-sync proof drift remains from #436 | surface plan shows sync-before-verify; dirty and clean executor proof | planned |
| B | Expose producer facts and format their exact consumer handoff | A wrong manual base caused an eight-minute duplicate run and 2.8 GB JSON | structured payload fields, wrong/stale negative proof, and roundtrip without recollection | planned |
| C | Probe operator/security/portability siblings | Counter implementation anchoring with genuinely different lenses | bounded evidence plus admit/defer/no-change decision | planned |
| D | Full-delta quality and release critique | Freeze one reviewed bundle before the irreversible boundary | quality artifact, release notes, critique, clean verification lock, dry-run | planned |
| E | Push and publish the patch release | User-authorized final external lane | tag/release URL, distinct HTTPS proof, install/doctor and issue-state reads | planned |

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
- Commits: pending
- What changed: Moved the SLOC inventory refresh from verify_commands to sync_commands; added producer payload fields mutation_coverage_base_sha, mutation_coverage_json, and mutation_coverage_consumer_command; synced plugin mirror.
- Alternatives rejected: Rejected generic write-shaped verifier detector, public sync-only CLI, and #436 closure.
- Targeted verification: 82 focused tests passed; validate_surfaces, packaging validators, ruff, py_compile, source/plugin cmp, and pre-lock run_slice_closeout --skip-broad-pytest passed.
- Test duplication pressure: Added two focused tests; changed files remain below Python length warn bands.
- Critique: [round3 slices A/B code critique](../critique/2026-07-12-round3-slices-a-b-code-critique.md); fresh-eye Act Before Ship resolved by cwd-proof executable model and coverage JSON no-recollection assertions.
- Off-goal findings: #436 remains open for exhaustive all-writer audit; #433 untouched.
- Lessons carried forward: When emitting copyable commands, separate executable install root from target repo root; prove reuse by asserting source bytes and mtime stay unchanged.
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

- none before activation.

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
