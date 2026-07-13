# Achieve Goal: North-Star Autonomous Two-Hour Release Round 5

Status: active
Created: 2026-07-13
Activation: `/goal @charness-artifacts/goals/2026-07-13-north-star-autonomous-two-hour-release-round-5.md`
Timebox: 2h
Activation time: 2026-07-13T16:55:22+09:00
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice C — independently measured follow-up candidate.
- Current slice intent: use the remaining reversible-work window to reproduce
  one independent operator or maintenance defect; stop without mutation when
  current evidence supports only a no-change or defer decision.
- Next action: probe the custom-home doctor boundary identified by the scout,
  then either open a falsifiable debug record or close the candidate honestly.
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

Spend two hours improving Charness from independent bug, maintainability,
test-economics, portability, security, and operator lenses. Admit changes only
from a current reproduction or same-command measurement, then publish and
independently verify one patch release beyond v1.0.3.

## Non-Goals

- Do not close #433, #436, or any other tracked issue; tracker lifecycle is a
  separate irreversible action requiring explicit authority and issue closeout.
- Do not repeat round-four fixes, optimize gate/line counts as ends in
  themselves, or weaken boundary proof to make tests faster.
- Do not add a new blocking floor for a reversible first-sighting failure when
  an existing guard, advisory, ownership split, or focused regression suffices.
- Do not remove or incompatibly change public surfaces without a separately
  reviewed compatibility case.

## Boundaries

- Reversible implementation is authorized until the closeout reserve starts at
  2026-07-13T18:35:22+09:00; only reviewed, committed slices enter final proof.
- Start from v1.0.3 and treat v1.0.4 as a patch candidate, subject to final-delta
  semver review. Never delete or repoint an existing release tag.
- Publication is provisional until a different observer confirms substantive
  content through an unauthenticated channel distinct from the release helper.
- GitHub is `axis: release-provider`; host/reviewer choices remain
  `axis: host` and `axis: reviewer-tier`, not global defaults.
- If #433/#436 informs a candidate, first read current issue content and
  reproduce a residual against v1.0.3; OPEN state is not evidence of a bug.
- Cautilus remains ask-before-run; do not run it from this authorization.
- If Slice A finds no admissible release-worthy delta, do not manufacture or
  publish v1.0.4; record the failed release condition and continue only with a
  safe evidence-producing probe or honest no-change closeout.
- Before candidate selection, confirm current HEAD, package version, public tag,
  and installed version so round-four state cannot be mistaken for new evidence.

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.

## User Acceptance

- At least three distinct lenses record an admit/defer/no-change decision;
  every code change traces to a reproduction or measured cost.
- Focused proof passes for each slice, followed by bundled broad quality,
  security/supply-chain, generated-surface, and clean verification-lock proof.
- Test-speed work reports the same command before/after and preserves a real
  delivery-boundary test; if no safe speedup exists, record that non-claim.
- GitHub exposes the new tag/release, a distinct observer confirms substantive
  public content, and installed version plus doctor/cache readback pass.

## Agent Verification Plan

### Low-Cost Checks

- Quality planner packets, focused pytest/duration probes, ruff/pycompile,
  changed-surface and artifact preflights, packaging parity, and per-slice
  closeout with broad pytest skipped.
- `./scripts/check-secrets.sh` and
  `python3 scripts/check_supply_chain.py --repo-root .` own local security proof.

### High-Confidence Checks

- Bounded fresh-eye review with snapshot/verify fingerprints before each
  accepted slice; final `run_slice_closeout.py --verification-lock` with
  changed-line mutation coverage for eligible Python changes.
- Full-delta critique, semver review, release dry-run, fresh-checkout probes,
  current-pointer/artifact durability, and clean-tree proof.

### External Or Live Proof

- Use the repo release helper only after the final lock and under the user's
  explicit push/release authority for this final bundle.
- Treat helper output as a claim: independently read remote refs, substantive
  unauthenticated HTTPS/API content, installed version, and doctor/cache state.
- The different observer is a bounded reviewer or human operator in a separate
  context; it must cite its own public ref/URL/API/install readback and may not
  use the release helper payload as its only evidence.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | Measure current bug/quality/speed/security candidates | Avoid backlog and prior-session anchoring | planner packets, timings, candidate ledger | completed |
| B | Repair the highest-leverage reproduced defect | Serve observed behavior before cleanup | RCA, focused regression, critique, commit | completed |
| C | Improve one independently measured test/maintenance seam | Use remaining time for honest economics | same-command delta, retained boundary coverage, critique | planned |
| D | Freeze and verify the bundle | Prevent local greens from becoming release confidence | exact lock, security/parity, semver and release review | planned |
| E | Push/publish the patch and complete goal closeout | Complete the user-authorized release boundary, not any issue lifecycle | public refs/body, install/doctor, retro/handoff | planned |

### Candidate/Lens Ledger Contract

Every Slice A lens writes one entry into `## Slice Log` before B/C consumes it:
`lens`; `candidate`; `current reproduction or measurement command`; `relation
to round-four evidence`; `decision: admit|defer|no-change`; `rationale`;
`proof path`; `write-back/disposition`. Probe answers write back to this ledger;
off-goal deferrals also enter `## Off-Goal Findings` with a reopen trigger.

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

Routing: quality — selected from installed metadata to own current quality, runtime, security, and structural evidence before implementation.
Routing: debug — selected to require a falsifiable invalid-root hypothesis, detection gap, and sibling search before repair.
Routing: impl — selected to own the smallest refresh-specific backend/consumer/test slice and generated plugin synchronization.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: approved — this repeated user request explicitly authorizes autonomous local work and the final locked-bundle push/release; issue closure, Cautilus, and a hollow release without an admissible delta remain excluded, and public success requires a separate observer plus separate channel.

## Slice Log

### Slice 1: Slice A — evidence inventory

- Objective: Measure current bug, maintainability, test-economics, security, and operator candidates without replaying round four.
- Why this approach: North-star evidence admission prevents activity from becoming the objective.
- Commits: ff4c40f6 starts the auditable goal; evidence closes with Slice B.
- What changed: No product code; recorded current quality/runtime/security/structure/CLI/skill-ergonomics inventories.
- Alternatives rejected: Rejected a forced speed refactor, blanket lint cleanup, and issue-state-driven work because current evidence did not justify them.
- Targeted verification: run-quality --read-only 81/81 in 59.6s; secrets and supply-chain pass; structural/CLI/brittle-guard inventories clean.
- Test duplication pressure: Managed-install standing boundary: 3 tests/0.61s; release-only boundary: 14 tests/78.78s; defer optimization because cases exercise distinct install/update boundaries. Standing nested CLI cluster: 44 tests/3.77s.
- Critique: Plan critique accepted evidence ledger and no-hollow-release rules; zero reviewer fingerprint drift.
- Off-goal findings: No test-speed claim. Future release-only managed-install economics require same-command measurement plus retained real-boundary smoke.
- Lessons carried forward: Scaffold current-pointer output must be paired with the quality record resolver; the observed round4 target was contract-compliant, not a tool bug.
- Metrics: lens ledger: bug/operator=admit catalog invalid root; test economics=defer; maintainability=no-change; security=no-change; skill ergonomics=no-change.

### Slice 2: Slice B — catalog invalid-root repair

- Objective: Prevent catalog refresh from turning an invalid explicit repo root into writes or a traceback.
- Why this approach: The current public repro was operator-visible and crossed an artifact-writer boundary.
- Commits: pending this slice closeout commit.
- What changed: Added refresh-specific backend destination validation, typed error translation in both CLI consumers, synced plugin export, and backend/direct/handler/real-process regressions.
- Alternatives rejected: Rejected a shared _repo_root guard, Git-checkout requirement, and broader list/resolve narrowing.
- Targeted verification: 21 focused tests in 14.06s; ruff; plugin byte parity; missing/file real-process rc2 with clean channels and no missing-path creation.
- Test duplication pressure: One 0.37s public process regression retains the delivery boundary; lower-layer tests own the broader input matrix.
- Critique: Two distinct fresh-eye angles plus separate counterweight; Act Before Ship real-process test fixed; all fingerprint verifies zero drift. Artifact: charness-artifacts/critique/2026-07-13-catalog-refresh-invalid-root-code-critique.md.
- Off-goal findings: Permission and symlink edge matrices deferred until operator evidence; list/resolve missing-root behavior intentionally unchanged.
- Lessons carried forward: Validate mutation authority at the producer boundary and translate typed failure at each final consumer.
- Metrics: RCA converted to durable test: writer-accepts-invalid-destination; ledger aggregate 35/42 seed-excluded, current 28d 11/11.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- [design north star](../../docs/design-north-star.md) — reversible judgment and
  different-observer/different-channel proof at publication.
- [handoff](../../docs/handoff.md) — v1.0.3 state, host restart, managed-install
  timing candidate, and #433/#436 lifecycle boundaries.
- [round-four goal](2026-07-13-north-star-autonomous-two-hour-release-round-4.md)
  and [retro](../retro/2026-07-13-north-star-autonomous-two-hour-release-round-4-retro.md)
  — completed slices, measured costs, review waste, and explicit non-claims.
- [recent lessons](../retro/recent-lessons.md) — producer/final-consumer and
  reviewer-window recurrence signals.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- Mode family: artifact-only versus implementation-continuation; chose
  continuation because the user explicitly requested two hours of autonomous
  iteration followed by push and release.
- Candidate family: prior deferred item versus fresh evidence-admitted sweep;
  chose the sweep so managed-install timing and OPEN issues are candidates, not
  predetermined answers.
- Release family: no publish, patch, or compatibility release; chose patch
  candidate v1.0.4 because the request authorizes publication but not breaking
  change. Final semver review may raise, never silently lower, the bump.
- Proof family: local-only, helper-only, or distinct live observation; chose
  distinct observation because publication is irreversible under the north star.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- Initial self-critique folded three constraints into the plan: do not replay
  round-four work, keep issue lifecycle out of scope, and preserve one real
  delivery-boundary proof when moving slow scenarios below a boundary.
- Over-worry not folded: requiring one code change per lens, remote CI per
  slice, or a full-suite speedup would reward activity rather than evidence.
- Execution: two bounded spec angles plus a separate counterweight consumed
  `charness-artifacts/critique/2026-07-13-075725-packet.md`; all reviewers were
  parent-delegated, read-only, and fingerprint verification reported zero drift.
- Act Before Ship (applied): resolved final-bundle publication authority; added
  the no-admissible-delta stop rule, current-state precheck, and candidate/lens
  ledger with probe write-back anchors.
- Bundle Anyway (applied): named the separate observer contract and clarified
  that Slice E completes goal/release closeout, never issue lifecycle.
- Over-Worry: no new ledger validator and no remote CI per slice.
- Valid but Defer: consider a deterministic lens-ledger validator only after a
  recorded recurrence shows the lightweight contract is insufficient.
- Fixed/Probe/Defer coherence: pass after the applied edits; every probe now has
  a Slice Log/Off-Goal write-back and every fixed publication decision has a
  no-delta fallback.
- Acceptance coverage: each criterion maps to ledger fields, focused/bundle
  commands, or the distinct observer/channel release proof.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- None at shaping time; record findings only after current reproduction or
  measurement distinguishes them from round-four history.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

- Run the released `charness --version`, then `charness doctor --json` and
  compare checkout/source/cache/Claude versions plus Codex cache drift.
- Open the public release and inspect substantive notes rather than relying on
  the presence of a tag alone.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
