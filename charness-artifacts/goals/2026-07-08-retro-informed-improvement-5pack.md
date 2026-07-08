# Achieve Goal: Retro-informed autonomous improvement: 5 decided slices (ratio-A, required-reads validator, #371 Tier 1, dup-ratchet A+B, #408 item 4 prose)

Status: active
Created: 2026-07-08
Activation: `/goal @charness-artifacts/goals/2026-07-08-retro-informed-improvement-5pack.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: G (#408 item 4 — forbidden-string prose principle).
  Landed: R `6415175b`, V `6440b24d` (+debt fix `30e3dd11`), B `cf7e6f47`.
- Current slice intent: one prose principle + worked example as a new section
  in `skills/public/quality/references/unit-test-quality.md`, cross-linked
  (one line) from `brittle-source-guards.md`; blesses the legitimate permanent
  negative classes; names the rejected ratchet as the recurrence-triggered
  escalation path. Doc-arm dup trips resolve via dup-review classification in
  this slice, not D. One reviewable intent unit (meaningful-slice-cadence).
- Next action: skill-surface preflight, author, verify, bounded critique,
  pre-lock closeout, slice log, commit; then D (last, single re-baseline);
  then repair the pre-goal red test (preflight roundtrip) before the final
  verification lock.
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

Land the five retro-informed improvement slices decided on 2026-07-08 (design
briefs: `charness-artifacts/design-studies/2026-07-08-retro-informed-improvement-briefs.md`),
selected because prior sessions paid for each friction at least twice or a
retro/quality artifact explicitly queued it:

1. **Slice R** — remove the live-repo hard test/production-ratio bound from
   `tests/quality_gates/test_test_production_ratio.py:25-26`; posture becomes
   advisory-only (decided). Per-branch synthetic fixtures for all three main()
   ratio branches.
2. **Slice V** — new blocking validator `validate_scenario_conditional_reads`
   (blocking + seeded waiver channel, decided): flags planner forced-tier
   conditional required-reads that no scenario `engage-always` forces. v1
   handoff-only extractor; waiver+reason for the two known real findings
   (state-selection judge-branch, adapter-contract branch).
3. **Slice B** — #371 Tier 1: SIGTERM/SIGINT/atexit signal-safe teardown for the
   gather browser path (`acquire_public_url.py`), red/green fake-CLI proof;
   #371 stays open (decided) with a partial-resolution comment; correct the
   `docs/handoff.md` "self-contained" mislabel.
4. **Slice D** — dup-ratchet S4-Defer-1 (token/comment-aware normalization,
   algo v2) + S4-Defer-3 (schema-v3 member-hash reduction diff, advisory
   reduction pre-pass) as ONE combined migration with ONE re-baseline
   (decided).
5. **Slice G** — #408 residual item 4: prose-only forbidden-string
   test-authoring principle in `unit-test-quality.md` (validator rejected,
   decided), cross-linked from `brittle-source-guards.md`.

Mode: this drafting session is artifact-only (goal + fresh-eye plan critique);
implementation runs in the next session after `/goal` activation — settled by
the operator's prose ("실구현은 다음 세션").

## Non-Goals

- No soft `no_increase` test-LOC ratchet and no hard sub-target ratio (decided:
  advisory-only; a forcing function re-creates the Goodhart pressure Slice R
  removes). Test-debt reduction itself is NOT in this goal — it becomes a
  standing rotation item scoped to the post-2026-07-03-audit delta.
- No `Close #371`: the raw tool-call/ceal path is upstream
  (`vercel-labs/agent-browser#1334`); Tier 1b (profile-dir lease, needs a
  pinned-CLI capability probe) and Tier 3 (host-adapter PDEATHSIG watchdog) are
  out of scope.
- No forbidden-string ratchet validator (rejected under north-star P1: the
  harmful/legitimate split is semantic, not syntactic) — prose principle only,
  with the ratchet named as the recurrence-triggered escalation path.
- No dup-ratchet corpus-reduction pass (`fixable_ceiling` is already 0; the
  largest families are confirmed portable-by-design boilerplate).
- No new claim-fidelity scenarios for the two known validator findings in v1 —
  they get waiver+reason, not fixtures (decided).
- Not picked up from the standing backlog: #410 reference-compaction flips
  (capture-gated, ~1.7-2.4M tokens each), #413 greenfield capture, 81-site
  argparse-help debt (handoff pins it LAST) — deliberately out of this goal.

## Boundaries

- External side-effect scope: name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication.
- GitHub writes limited to: ONE partial-resolution comment on #371 (no state
  change, no close). Everything else is local commits; push is a separate
  operator-approved lane.
- Slice D rewrites the three lockstep derived baselines (dup-ratchet-baseline,
  nose-baseline, dup-review overlay) exactly once, after ALL scanned-scope
  source edits in this goal are batched (implementation-discipline batching
  rule); no other slice may touch scanned clone-member files after that
  re-baseline. The single re-baseline is NOT a blind full-scan overwrite
  (critique F1): split it into (a) the algo-migration remap of
  member-preserving survivor families and (b) an explicit review-then-accept
  of every family this goal grew or added (e.g. Slice V's new thin script
  growing a portable-boilerplate family) via the scoped-rebaseline path — a
  blind `--write-baseline` would silently absorb goal-introduced duplication.
- Slice G's doc edits hit the dup-ratchet DOC arm, outside D's code
  re-baseline scope: if G trips a doc-signature drift, resolve it via
  dup-review classification in Slice G, not by folding it into D (critique F4).
- Slice V adds a new deterministic blocking floor: the Floor-Addition Restraint
  checklist call must be recorded at the floor site or in the slice
  commit/critique (justification pre-drafted in the briefs artifact).
- Slice ordering is a hard constraint: R first (every later slice adds tests
  against a 5-line live headroom); D last among code slices (single
  re-baseline); V/B/G in any order between.

## User Acceptance

- `python3 scripts/check_test_production_ratio.py --repo-root . --json` still
  reports the live ratio, `pytest tests/quality_gates/test_test_production_ratio.py`
  passes, and a test-adding diff no longer fails the suite via the live ratio
  pin (Slice R).
- `python3 scripts/validate_scenario_conditional_reads.py --repo-root .` exits
  0 on the live repo, and deleting
  `evals/cautilus/handoff-claim-fidelity/pickup-ambiguous.spec.json` in a
  scratch copy makes it flag `continuation-sequence.md` (Slice V — the 7/2
  incident, now machine-caught).
- The red/green SIGTERM test in the web-fetch cleanup suite demonstrates the
  close-on-signal contract; #371 carries the partial-resolution comment and
  remains open (Slice B).
- An in-place comment edit inside a duplicated span no longer rotates the
  family fingerprint, and a membership-shrink surfaces as an advisory
  REDUCTION instead of a hard-block (Slice D).
- `unit-test-quality.md` carries the forbidden-string principle with the
  worked example; `run-quality.sh` and full pytest are green at closeout
  (Slice G, all).

## Agent Verification Plan

### Low-Cost Checks

- Per commit: focused pytest for the touched test family; matching aggregate
  preflight before editing any gated surface
  (`check_skill_surface_preflight.py` for Slice G's references,
  `check_artifact_surface_preflight.py` for artifacts,
  `check_doc_authoring_preflight.py` for the handoff edit in Slice B).
- Slice V: the validator's own synthetic pass/flag/waived fixtures; extractor
  unit test pinning extractor set == planner forced tier; a directed fixture
  for the "skill has no registered extractor → advisory not-yet-covered, never
  silent pass" branch (critique F3 — per-branch fixture discipline).
- Slice B: a directed fixture for the "signal fires with no open session →
  idempotent no-op" handler branch, alongside the red/green SIGTERM test
  (critique F3).
- Slice D: prototype-proven fixture set (comment-edit stable / real-edit
  rotates / fallback==v1 / reduction / genuine-new / grow / shrink-then-recur).

### High-Confidence Checks

- Per slice: `run_slice_closeout.py --skip-broad-pytest` pre-lock rehearsal;
  fresh-eye slice critique with the bounded slice packet BEFORE the locked
  producer run (critique-after-producer burned two instrumented reruns on
  2026-06-10).
- Final bundle: `run_slice_closeout.py --verification-lock
  --produce-mutation-coverage` (Slices R/V/B/D all touch mutation-pool Python),
  full `./scripts/run-quality.sh`, plugin-mirror sync staged with sources.
- Slice D migration: one-shot `distinct(v2 fingerprint) == distinct(nose id)`
  collision assertion; every live overlay intentional id present post-remap
  with class/note/reviewed_at preserved.

### External Or Live Proof

- #371 partial-resolution comment posted and visible via `gh issue view 371`
  (the only external write; confirm-before-post).
- No release in this goal; `Release: n/a` expected at closeout. Live-browser
  proof for Slice B is explicitly NOT claimed — the fake-CLI red/green test is
  the proof level (SIGKILL and raw tool-call paths are non-claims).

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| R | Remove live hard ratio bound; advisory-only posture; per-branch synthetic fixtures | Blocked two consecutive sessions; 5-line headroom blocks every later slice here | Focused pytest green; test-adding diff no longer trips suite; proof cost XS; test-pressure: net −2 live asserts +1 synthetic fixture (~15 LOC) | planned |
| V | `validate_scenario_conditional_reads` blocking + seeded waivers, handoff extractor | Promotes the 7/2 hand-caught gap to a validator (repo principle); two real findings already known | Synthetic pass/flag/waived + incident-reconstruction test; live repo green; restraint call recorded; proof cost S-M; test-pressure: ~150 test LOC (post-R safe) | planned |
| B | #371 Tier 1 SIGTERM/atexit teardown + handoff mislabel fix + partial comment | Self-contained charness-owned gap; handoff carries a wrong scope label today | Red/green fake-CLI signal test; #371 comment; no #302/#365 regression; proof cost S; test-pressure: ~2 tests | planned |
| G | Forbidden-string prose principle in `unit-test-quality.md` + cross-link | #408 disclosed residual; three live vacuous-pass examples found | Skill-surface preflight green; dup-ratchet clean cross-link; proof cost S; test-pressure: none (prose) | planned |
| D | Combined algo-v2 + schema-v3 dup-ratchet migration, single re-baseline | Dominant observed churn class (11 rotations/46 commits); combined = one re-baseline | Full fixture set; migration remap assertions; gate CLEAN post-migration; proof cost M (~2d); test-pressure: largest of the goal (post-R safe) | planned |

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

Seeded at drafting:

- Decision: exact wording/scope of the #371 partial-resolution comment (names
  what Tier 1 fixes, what stays upstream at #1334)
- Owner: operator (external write, confirm-before-post)
- Why deferred: local slices proceed without it; the comment is the last step
  of Slice B
- Unblock action: approve the drafted comment text below (drafted at Slice B,
  cf7e6f47) and post via `gh issue comment 371`
- Revisit trigger: goal closeout (Slice B landed; draft ready)
- Draft: "**Partial resolution — Tier 1 landed (cf7e6f47).** Charness now
  installs SIGTERM/SIGINT handlers plus an `atexit` hook around the
  `acquire_public_url.py` gather-browser path: a module-level live-session
  registry is populated while an `agent-browser` stage is in flight, and a
  host SIGTERM/SIGINT now triggers a best-effort close via the existing
  `_close_cleanup_error` chain before the process exits with its original
  signal disposition — verified red/green with a real-subprocess test.
  **Stays open:** (1) the raw host tool-call path where the harness invokes
  `agent-browser` directly and it self-daemonizes — upstream
  vercel-labs/agent-browser#1334; (2) SIGKILL — backstopped by the
  runtime-guard reaper, not this teardown; (3) Tier 1b profile-dir lease —
  deferred pending a pinned-CLI capability probe."

- Decision: whether the standing test-debt rotation item (post-audit delta
  sweep) gets queued into handoff after Slice R lands
- Owner: operator
- Why deferred: out of this goal's scope by decision; only the queue placement
  needs a call
- Unblock action: yes/no at goal closeout
- Revisit trigger: goal closeout handoff refresh

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

- Routing: find-skills -> achieve + impl — recommendation engine (`list_capabilities.py --recommend-for-task`, 2026-07-08, read-only) matched `achieve` for operating the active goal lifecycle and `quality` for the gate-touching slices; `impl` owns each code slice per the achieve coordination contract.

## Discuss Before Activation

A Before-phase summary of any consequential activation decision — surfaced from
the Non-Goals / Boundaries / Verification / Interview / Critique sections — that
must be resolved before `/goal`. Required only when a trigger fires (live/prod
proof, issue close/split, broad scope, irreversible side effect, or a
proof-level non-claim); replace the `fill` line below, or delete it when none
applies.

- Discuss before activation: resolved — four consequential decisions were put
  to the operator in the drafting session (2026-07-08, AskUserQuestion) and
  answered: (1) ratio posture = advisory-only, no ratchet; (2) #371 = Tier 1
  only, issue stays open, upstream split stands; (3) dup-ratchet = A+B combined
  migration, one re-baseline; (4) validator posture = blocking + seeded waiver
  channel. The remaining external write (#371 comment) is queued
  confirm-before-post in `## Operator Decision Queue`; no live/prod proof, no
  release, no issue close in scope. Proof-level non-claim (critique F2),
  acknowledged at drafting: Slice B's proof ceiling is the fake-CLI SIGTERM
  red/green test — live-browser behavior, SIGKILL, and the raw tool-call/ceal
  path are explicit non-claims (Tier 1 scope only).

## Slice Log

### Slice 1: Slice R — live hard ratio pin removed (advisory-only)

- Objective: Remove the live-repo hard test/production-ratio bound (test_test_production_ratio.py:25-26) so the posture is advisory-only; add the missing under-threshold rc-0 synthetic per-branch fixture.
- Why this approach: Decided slice (goal Interview Decisions); hard live pin at 5-line headroom blocked every later test-adding slice, so R lands first.
- Commits: 6415175b
- What changed: tests/quality_gates/test_test_production_ratio.py (live asserts -> degenerate-zero sanity checks + comment; new in-process test_cli_under_threshold_returns_zero_on_synthetic_repo); goal artifact frame/routing.
- Alternatives rejected: Soft no_increase ratchet and hard sub-target ratio (re-Goodhart, rejected at drafting); subprocess-based new fixture (would flip boundary-bypass classification).
- Targeted verification: Focused pytest 8/8; run_slice_closeout --skip-broad-pytest all PASS; live ratio now 1.0002 and suite green (this test-adding diff itself would have tripped the old pin — acceptance shown); bare CLI exit 1 over max by design, --advisory gate lane exit 0; grep confirms run-quality.sh:504 is the only gate caller.
- Test duplication pressure: check_dup_ratchet.py: OK, no new fixable-eligible families, fixable_ceiling=0; net +1 synthetic test (~23 LOC), -2 live asserts.
- Critique: Fresh-eye bounded reviewer: REVISE -> folded. Must-fix was a false proof record (bare --json exits 1, not 0 — advisory lives only at the run-quality gate); two comment-wording overstatements fixed; boundary-bypass token set verified unchanged; no other live ratio pin exists in repo.
- Off-goal findings: docs/handoff.md Discuss bullet ('pinned at ~1.0') goes stale — owned by closeout handoff refresh (critique F5-adjacent, recorded, not filed).
- Lessons carried forward: Do not pipe a proof command into head — the pipe hides the exit code; record the exact gate-lane invocation as proof, not a lookalike.
- Metrics: 1 impl subagent (sonnet) + 1 fresh-eye critique subagent; ~2 focused pytest runs + 1 pre-lock closeout.

### Slice 2: Slice V — validate_scenario_conditional_reads (blocking + seeded waivers)

- Objective: Machine-catch the 7/2 incident class: flag planner-forceable conditional required-reads no scenario engage-always forces; blocking with classTag DUP/INLINE + allowlist waiver channels; v1 handoff-only extractor.
- Why this approach: Decided slice; retro next-time checklist explicitly queued this validator; two real findings already known and waived-with-reason per the drafting decision.
- Commits: 6440b24d
- What changed: scripts/claim_fidelity_lib.py (+~145: extractor registry, allowlist loader, cross_check_conditional_reads, dup_inline_tags key, missing-planner guard); new scripts/validate_scenario_conditional_reads.py + .allowlist.txt (seeded adapter-contract waiver); run-quality.sh wiring after validate-claim-fidelity-specs; new tests/quality_gates/test_scenario_conditional_reads.py (10 tests); validator-timing-layers.md verdict row; plugins mirror resync.
- Alternatives rejected: Advisory-first posture (rejected at drafting: recorded ignored-precedent undeclared_on_disk); fixturing the two findings as new scenarios (rejected: widens v1, adapter-health hard to fixture healthy); importing the planner module (rejected: import runs adapter bootstrap — AST literal scan instead).
- Targeted verification: 10 focused tests green incl. directed no-extractor advisory branch (critique F3) + incident reconstruction (deleting pickup-ambiguous.spec.json flags continuation-sequence.md — User Acceptance line proven at test level); live validator exit 0 with exactly the two seeded waivers; validate_packaging green after mirror sync; full pre-lock run_slice_closeout PASS.
- Test duplication pressure: check_dup_ratchet at slice R boundary was clean; new thin script may grow a portable-boilerplate family — deferred to Slice D review-then-accept re-baseline per goal Boundaries (dup gate is broad-path only, cannot trip pre-D).
- Critique: Fresh-eye bounded reviewer: REVISE -> folded. Must-fix: plugins/ mirror not regenerated (mutate->sync barrier miss; validate-packaging exit 1) — synced. Hardening folded: missing-planner clean ValidationError. Named non-claims confirmed: extractor false-negative axis (computed/f-string paths escape both pin and cross-check); allowlist waiver is skill+ref-grained (a future differently-caused flag on a waived ref stays absorbed). check_test_repo_copy_invariants + check_timing_layer_completeness fired post-critique; fixed via REPO_COPY_IGNORE subtree idiom + timing-table row.
- Off-goal findings: none
- Lessons carried forward: The slice proof set must include the surface-matched closeout aggregate, not a hand-picked gate list — validate-packaging and the timing meta-gate only fired in the aggregate; run the aggregate earlier next slice.
- Metrics: 1 impl subagent (sonnet) + 1 fresh-eye critique subagent; 3 pre-lock closeout runs (2 gate-fix iterations).

### Slice 3: Slice B — #371 Tier 1 signal-safe gather-browser teardown

- Objective: SIGTERM/SIGINT/atexit best-effort teardown of a live agent-browser session in acquire_public_url.py via the existing _close_cleanup_error chain; correct the handoff item-3 self-contained mislabel; draft (not post) the #371 partial-resolution comment.
- Why this approach: Decided slice; charness-owned half of #371 (the raw tool-call path is upstream agent-browser#1334); handoff carried a wrong scope label.
- Commits: cf7e6f47 (+ 30e3dd11 Slice V debt fix surfaced by this slice's broad run)
- What changed: skills/support/web-fetch/scripts/acquire_public_url.py (+~89: registry, teardown, handlers) + plugins mirror; tests/test_web_fetch_cleanup.py (+2 tests); tests/test_web_fetch_route_and_classify.py (MF1 namespace fix); docs/handoff.md item 3; tests/quality_gates/support.py (V debt, separate commit).
- Alternatives rejected: A second reaper process (rejected: existing _close_cleanup_error chain + runtime-guard reaper suffice); handling SIGKILL (impossible; reaper is the backstop); posting the #371 comment now (rejected: operator confirm-before-post boundary).
- Targeted verification: Red run captured pre-fix (log open-without-close, exit 143) then green; directed no-session idempotent no-op fixture green; 9/9 cleanup tests; 64 tests across the three touched test files; aggregate pre-lock closeout completed; boundary-bypass classification unchanged (file already internally-spawning); runtime guard asserts no orphans after the SIGTERM test itself.
- Test duplication pressure: No scanned clone-member files touched; dup gate remains broad-path-only until Slice D.
- Critique: Fresh-eye bounded reviewer: REVISE -> folded. MF1 (real regression): _register_live_session reads args.repo_root, breaking a sibling SimpleNamespace test — fixed by adding repo_root (sibling test at :124 already had it). Reviewer confirmed red/green independently in a detached worktree. Answers: atexit is currently-unreachable-but-kept backstop; teardown delay bounded ~3x timeout; SIGTERM test flake risk <1%; handoff at 70/70 acceptable (zero headroom noted); no reentrancy hazard.
- Off-goal findings: Pre-existing red (predates goal, fails at cbfc8b8a in a clean worktree): tests/quality_gates/test_check_artifact_surface_preflight.py::test_changed_artifacts_passes_scaffold_roundtrip — critique-stub roundtrip blocked by validate_critique_artifacts (#408 disposition line). Must be repaired before the final verification lock; queued for the closeout phase.
- Lessons carried forward: The V lesson was under-applied: the pre-lock aggregate still skips broad pytest, and MF1 lived exactly there. For remaining slices, run the focused pytest of ALL modules importing the changed surface (grep the import), not only the slice's own test file.
- Metrics: 1 impl subagent (sonnet) + 1 fresh-eye critique subagent; red/green captured pre/post fix; 2 commits.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. `charness-artifacts/design-studies/2026-07-08-retro-informed-improvement-briefs.md`
   — the five condensed investigation briefs with decisions folded in (primary).
2. `docs/handoff.md` — `## Discuss` ratio item (two blocked sessions), item 3
   (#371, mislabeled self-contained), `## Next Session` backlog this goal
   deliberately does not pick up.
3. `charness-artifacts/retro/recent-lessons.md` +
   `charness-artifacts/retro/2026-07-02-session-retro.md` — the validator idea
   (next-time checklist) and the per-branch falsifiable-fixture discipline.
4. `charness-artifacts/quality/latest.md` — dup-ratchet residual sketch
   (transformation/proof-boundary/posture) this goal implements.
5. `charness-artifacts/quality/history/2026-07-03-pytest-suite-test-value-audit.md`
   — the lean-suite finding that reframed the ratio premise.
6. GitHub #371 (+ `charness-artifacts/debug/2026-06-15-issue-371-agent-browser-upstream-lifecycle.md`,
   upstream `vercel-labs/agent-browser#1334`), #408 (residual item 4),
   `docs/deferred-decisions.md` D30/S4-Defer-1/2/3.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Ratio posture after hard-assert removal** — family: {advisory-only, soft
  `no_increase` ratchet with deliberate baseline bump, advisory-now +
  data-driven ratchet later}. Chosen: advisory-only. Rejected: any ratchet
  re-creates a forcing function against test-writing (the observed Goodhart
  failure); the audit shows the suite is lean, so growth is not presumptively
  bad. `single-point: repo-local quality-gate policy, no host/provider axis.`
- **#371 closure scope** — family: {Tier 1 + issue open, Tier 1+1b + close,
  Tier 3 adapter design}. Chosen: Tier 1 + issue open. Rejected: closing would
  mislabel the ceal raw-tool-call scenario as fixed (prior disposition and both
  issue comments require proof across all exit paths); Tier 1b is
  capability-gated on the pinned CLI; Tier 3 needs host cooperation.
  `single-point: ownership boundary fact, not a config axis.` (Tier 1b's
  profile-dir override IS version-axis-dependent — recorded as the gate for
  any future 1b slice.)
- **dup-ratchet scope** — family: {B only + measure A, A+B combined migration,
  defer both}. Chosen: A+B combined. Rejected: B-only risks a second full
  re-baseline if A ships later (each migration rotates all 546 families);
  deferral leaves the dominant observed churn class active. Accepted cost: A's
  evidence is theoretical (0 observed comment-edit rotations) — shipped for
  migration-economy, not materiality. `single-point: repo-local baseline
  artifacts.`
- **Validator posture** — family: {blocking + seeded waivers, advisory-first
  then promote, blocking + fixture the two findings now}. Chosen: blocking +
  seeded waivers, findings get waiver+reason. Rejected: advisory output has a
  recorded ignored-precedent (`undeclared_on_disk`); fixturing the two findings
  now widens v1 scope (adapter-health is genuinely hard to fixture healthy).
  `single-point: repo eval-spec contract; extractor registry is the
  multi-planner axis and is explicitly extensible.`
- **Mode** — artifact-only drafting session; implementation next session.
  Settled by operator prose, not asked.
- **#408 carrier** — family: {tracked follow-up issue, direct slice in this
  goal}. Chosen: direct slice (S-size; an issue would be ceremony — the goal +
  handoff carry it). Rejected-alternative recorded for the case the goal is
  abandoned: file the drafted issue from the briefs artifact instead.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

Reviewer provenance: one bounded fresh-eye subagent (read-only, no drafting
context), 2026-07-08. Verdict: REVISE — no blockers; factual base fully
verified (every load-bearing file:line claim in the briefs checked true,
including both validator "real findings" and the handoff #371 mislabel).

Folded (all applied in this draft):

- F1 (should-fix): Slice D's single re-baseline split into survivor remap +
  explicit review-then-accept of goal-grown/added families — folded into
  `## Boundaries`. Root: V's new thin script likely grows a portable
  boilerplate family; membership change is not member-preserving, so a blind
  `--write-baseline` would silently absorb goal-introduced duplication.
- F2 (should-fix): Slice B proof-level non-claim (fake-CLI ceiling; SIGKILL /
  live-browser / raw-tool-call non-claims) added to
  `## Discuss Before Activation` — that trigger fires and was previously
  uncovered.
- F3 (should-fix-lite): two conditional branches got named same-slice fixtures
  (V's no-extractor advisory branch; B's no-session idempotent no-op branch) —
  folded into Low-Cost Checks.
- F4 (over-worry, folded anyway as one line): Slice G doc-arm trips resolve via
  dup-review classification, not D's code re-baseline — folded into
  `## Boundaries`.

Raised, not folded:

- F5 (over-worry): handoff `## Next Session` item 3 goes stale at closeout
  (Slice B corrects the label and queues Tier 1) — the closeout handoff
  refresh owns it; noted so it is not missed.

Verified-pass highlights a fresh session need not re-check: ratio hard bound
is unique to `test_test_production_ratio.py:25-26`; the in-process fixture
idioms compose (summarize-on-tmp-repo :97-111 + argv/capsys main() :50-55);
no V↔planner circularity (V reads `plan_handoff_run.py`, no slice edits it);
dup-ratchet gate runs broad-path only, so mid-goal slices cannot trip it
before D; both seeded waivers must land inside Slice V (already decided) or
the final run-quality self-blocks.

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
