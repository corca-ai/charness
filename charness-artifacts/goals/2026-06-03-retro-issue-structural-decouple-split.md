# Achieve Goal: Generalized, Destination-Split Retro Issue Proposals

Status: complete
Created: 2026-06-03
Activation: `/goal @charness-artifacts/goals/2026-06-03-retro-issue-structural-decouple-split.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Discuss before activation: RESOLVED in-thread on 2026-06-03 via AskUserQuestion.
(A) **A4-lite shared contract** — retro classifies the two axes, achieve
Auto-Retro dispositions the split, issue routes the target; each skill stays
standalone-useful. (B) **B1 adapter/manifest `harness_upstream` pointer** with a
current-repo==upstream collapse rule and a safe "unknown → keep local + state
ambiguity" fallback. (C) **C2 presence-only structured field** (separate
`Structural pattern` / `Triggering instance(s)`) plus prompt guidance; the
deterministic check verifies presence only, never quality. (D) **D1** — split
only when a finding has both a generalizable upstream fix and a distinct
current-repo-local adaptation (assumed default, unobjected). (E) **E1** — when
the current repo is charness, collapse "upstream" to this repo and split on
portable-skill-core vs repo-local operating surface (assumed default,
unobjected). (F) **F2** — capability **and** dogfood: also file the real split
backlog for this repo from recent waste retros, through normal `issue`
discipline. This authorizes a multi-skill workflow change plus real issue
creation. A present summary is not itself proof of resolution; the binding
resolution is the in-thread answers folded into Boundaries / Slice Plan below.

## Active Operating Frame

- Status: COMPLETE. Shipped in `6432d6c1` + a review-fix commit; dogfood issues
  #284 (upstream-harness) and #285 (repo-local) filed and verified OPEN.
- Next action: none — see `## Final Verification` and `## Auto-Retro`. Follow-up
  work lives in #284/#285, not this goal.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Make achieve's end-of-goal waste-retro issue proposals **structural instead of
incident-coupled**, and **split each actionable improvement by destination**:
upstream charness (portable harness / skill core) versus current-repo-local
(skill adapters, repo-local skills, AGENTS.md, folder structure, test fixtures,
code quality). The benefit primarily lands when achieve runs from a *consumer*
repo that installed charness as a plugin, but the behavior must also be coherent
when the current repo *is* charness itself.

Two orthogonal axes apply to every surfaced improvement:

- **Axis 1 — generalization (structural vs incident):** propose the structural
  pattern fix and cite the triggering incident as *evidence*, not as the fix
  scope. Do not couple the issue to "the one thing that happened this run."
- **Axis 2 — destination (upstream vs local):** route the generalizable harness
  fix to charness upstream, and the repo-specific adaptation to the current
  repo, as *separate* issues to the correct target — only when the finding
  genuinely has both.

## Non-Goals

- Do not turn the achieve disposition floor into a content classifier that
  judges whether an issue is "structural enough." The deterministic gate stays
  presence/binding-only per the existing guardrail; substance is judged by the
  reviewer/human.
- Do not auto-file issues without the normal `issue` discipline (observed
  problem before solution, target-repo resolution, backend verification).
- Do not double-count: a single finding must not be mechanically forked into an
  upstream+local pair when only one destination genuinely applies.
- Do not hardcode `gh` or a specific org as the upstream identity; portability
  flows through the adapter, not literals.
- Do not absorb retro/issue/critique responsibilities into achieve or add
  achieve-only branches that break their standalone use.
- Dogfood (F2) is bounded: only findings from *recent* waste retros in this
  repo, each filed through normal `issue` discipline (observed problem first,
  target resolution, backend verification). Do not bulk-file speculative issues
  or reopen unrelated closed concerns.

## Boundaries

- Repo-local and portable across hosts; host/repo-specific identity stays in
  adapters and manifests, not skill prose.
- The change spans the retro → achieve-Auto-Retro → issue seam; keep each skill
  independently useful (a standalone `retro` or `issue` must still work).
- Any new structured field is presence-checkable only; no quality classifier.
- When the current repo's identity cannot be distinguished from upstream
  charness, the safe default is to keep the finding local and say so, never to
  file into the wrong repo (B1 fallback).
- Folded resolutions: **A4-lite** — retro owns the two-axis classification,
  achieve Auto-Retro owns the split disposition, issue owns target routing; no
  skill loses standalone use. **B1** — upstream identity is an adapter/manifest
  `harness_upstream` pointer with a current-repo==upstream collapse. **C2** —
  any structural-vs-incident structure is a presence-only field; the gate never
  judges quality. **D1** — single destination by default; split only on a real
  dual finding. **E1** — in the charness repo, split becomes portable-skill-core
  vs repo-local operating surface.
- Dogfood issues must clear the same bar this goal builds (generalized framing,
  presence fields, correct destination) before filing — the feature and its
  first real outputs share one standard.

## User Acceptance

What the user can do to verify completion directly:

- Read the updated `retro` / `achieve` / `issue` skill surfaces and confirm the
  two axes (generalize; destination-split) are expressed where a future agent
  will actually read them, with each skill still standalone-useful.
- Run achieve's Auto-Retro on a sample finding (or read a worked example in the
  goal/retro artifact) and confirm it proposes a generalized issue and, when
  warranted, a separated upstream-vs-local pair routed to the correct target.
- Confirm any deterministic check added is presence-only by reading its test
  fixtures (a vague-but-present issue passes; a missing structured field fails).
- Confirm portability: a consumer-repo adapter example shows how "upstream
  charness" is identified, and the charness-as-current-repo case is handled.

## Agent Verification Plan

### Low-Cost Checks

- Existing skill-ergonomics / goal-artifact / skill-validation gates still pass
  after the prose + structure edits.
- New presence-only test fixtures (if C resolves to a structured field): a
  present-but-vague field passes; a missing field fails. No content assertions.
- `find-skills` inventory + adapter validators stay green; plugin/export mirror
  surfaces stay in sync (mutate → sync → verify).

### High-Confidence Checks

- A worked dry-run example: feed a realistic incident-coupled retro finding
  through the updated disposition guidance and show (a) the generalized restate
  and (b) the destination-split decision, including the "single destination"
  and "current repo is charness" branches.
- Fresh-eye bounded review of the seam change (different agent context).

### External Or Live Proof

- Not planned unless F (dogfood) is chosen: filing real split issues through the
  resolved backend and verifying them upstream + locally would be the live
  proof. Otherwise explicitly recorded as not run.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Resolve the design forks with the user | Forks change architecture; cannot shape boundaries without them | Answered AskUserQuestion (A4-lite/B1/C2/D1/E1/F2) + folded Boundaries | done |
| 1 | Two-axis contract across retro/achieve/issue (A4-lite) | Anchors every later edit; keeps each skill standalone | Updated retro `Next Improvements` (destination axis), achieve Auto-Retro split disposition, issue target routing | pending |
| 2 | Portable upstream-identity mechanism (B1) | Split is meaningless without correct target | Adapter `harness_upstream` field + example + charness-as-current-repo collapse (E1) | pending |
| 3 | Presence-only generalization field (C2) | Make decoupling auditable without a content classifier | `Structural pattern` / `Triggering instance(s)` fields + presence-only test fixtures (present-vague passes, missing fails) | pending |
| 4 | Over-split / volume rule (D1) | Prevent issue spam / double-count | Documented rule + worked single-vs-split examples | pending |
| 5 | Dogfood: file the split backlog for this repo (F2) | Prove the feature on real recent waste-retro findings | Generalized, destination-split issues filed + backend-verified through `issue` | pending |
| 6 | Sync mirrors, run gates, fresh-eye review, closeout | Phase barrier discipline | Green gates, bounded review notes, commit | pending |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — Gather: n/a — this goal is shaped from in-repo skill
  surfaces and artifacts, no external URL/Slack/Notion/Docs/Drive source.
- **Release step** — Release: n/a — workflow/skill-surface change, no version
  bump or install-manifest edit planned.
- **Issue closeout step** — this goal *creates* issues (dogfood F2 output) more
  than it closes them. The dogfood slice files generalized, destination-split
  issues via `issue` and verifies each through the selected backend (creation
  verification, not closeout). If the run also opens a tracking issue for the
  capability work and closes it on completion, record the close carrier and
  `verify-closeout` proof here. No pre-existing tracked issue is being resolved.

## Slice Log

### Slice 1: Two-axis contract (A4-lite)

- Objective: Create the shared retro-issue-destination-split contract (generalization fields + destination axis + D1/B1/E1) and point retro, achieve, issue at it without breaking standalone use
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: check_skill_contracts/check_references_link_inventory/check_doc_links pass; test_skill_surfaces_reference_the_shared_contract pins all three skills cite the shared ref
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Portable upstream identity (B1+E1)

- Objective: Add issue adapter harness_upstream field + pure resolve_destination_target helper (consumer/collapse/unknown) + resolve-destination CLI + .agents/issue-adapter.yaml for this repo; document in issue-backend.md
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: resolve-destination smoke (collapse for corca-ai/charness); bare resolve_adapter still valid; 3 resolve-destination tests green
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 3: Presence-only generalization check (C2)

- Objective: Add validate_proposal_fields.py (presence + Destination enum only) and test fixtures proving present-vague passes and missing field fails
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: test_issue_proposal_fields.py: 8 passed (present-vague pass, missing-field fail, bad-enum fail, bullet-style pass)
- Test duplication pressure: new test file test_issue_proposal_fields.py (8 cases); no overlap with existing issue tests — different script under test
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 4: Sync, broad gate, conciseness/markdown fixes (D1 folded)

- Objective: Sync mirrors and run the broad read-only gate; fix real failures it surfaced (adapter repo field, SKILL conciseness ceilings, wrapped inline code spans, reference depth). D1 over-split rule + worked examples are folded into the shared reference rather than a separate slice
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: validate_skills/validate_adapters/validate_skill_ergonomics/check-markdown/check_doc_links/check_references_link_inventory all exit 0; 70 targeted pytest pass incl. previously-failing test_validate_adapters; only env-residual fails are validate-maintainer-setup (worktree inherits absolute core.hooksPath) and check-runtime-budget (check-duplicates timing under parallel load)
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 5: Dogfood: persist retro + file generalized split issues (F2)

- Objective: Run the After-phase session retro, persist it, and dogfood the new contract by filing the generalized, destination-split proposals as real issues (collapse mode: this repo IS charness)
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: retro persisted to charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md (+recent-lessons/index refresh); both proposals pass validate_proposal_fields.py (ok, correct destination); resolve-destination=collapse; filed #284 (upstream-harness) + #285 (repo-local), both verified OPEN with Structural pattern + Destination fields in body
- Test duplication pressure:
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 6: Fresh-eye bounded review + fix

- Objective: Run a different-context bounded reviewer over commit 6432d6c1 + closeout; fold its findings
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Reviewer verdict ship-with-nits. Real bug fixed: validate_proposal_fields regex used \s (matched newline) so an empty field value stole the next line — now horizontal-whitespace only; added regression test (empty value -> missing); fixed two docstring ref-depths. 9/9 proposal tests pass; empty-value smoke now ok=False; dogfood proposals still pass; py_compile/ruff/check-markdown green. Invariants confirmed OK by reviewer: B1/E1 resolver, mirror fidelity, issue SKILL unbloated (byte-identical to base), presence-only not a classifier
- Test duplication pressure: added test_empty_value_treated_as_missing; closes the present-but-empty gap the reviewer flagged; no duplication with existing cases
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- `skills/public/retro/SKILL.md` — current `Next Improvements` taxonomy
  (`workflow` / `capability` / `memory`) and the broad-durable vs narrowly-local
  split; today it has no destination axis and no generalize-the-pattern field.
- `skills/public/achieve/SKILL.md` — Auto-Retro disposition floor
  (`applied: <what>` or `issue #N`, presence/binding-only, never a content
  classifier).
- `skills/public/issue/SKILL.md` + `references/issue-backend.md` — target-repo
  resolution (`default_org` corca-ai, git-remote inference) and observed-problem
  -before-solution discipline; the routing exists but is not retro-driven.
- `charness-artifacts/goals/2026-06-03-281-automatic-waste-retro-closeout.md` —
  adjacent goal (retro-trigger context preservation); confirms this is a
  distinct concern (issue *content/destination*, not trigger plumbing).
- `docs/handoff.md`, `charness-artifacts/retro/recent-lessons.md` — current
  pickup + repeat traps (anti-anchoring lesson is directly relevant to Axis 1).

## Interview Decisions

Option families for the six forks. Resolved in-thread on 2026-06-03; this
section records the design space so a fresh session sees more than the closed
point.

- **A — Owning layer for split + generalization.**
  - A1 retro is the classifier (adds destination + pattern/instance axes);
    achieve & issue consume.
  - A2 achieve Auto-Retro disposition owns the split; retro stays generic.
  - A3 issue owns target routing; retro/achieve feed candidate findings.
  - A4 shared contract across all three (retro classifies, achieve dispositions
    split, issue routes), each kept standalone-useful.
  - **Chosen: A4-lite.** Rejected A1/A2/A3 because each leaves a gap: A1 forces
    retro to learn harness-identity concepts and over-centralizes; A2 only helps
    achieve-driven retros (standalone retro gets nothing); A3 makes issue carry
    generalization, which is not its job. A4-lite distributes each axis to the
    skill that already owns the nearest concern while keeping all three usable
    alone.
- **B — Portable identity of "upstream charness."**
  - B1 adapter/manifest pointer (`harness_upstream` repo slug) with a
    current-repo == upstream collapse rule.
  - B2 prompt-only inference from plugin-install + org, no new config.
  - **Chosen: B1** with safe "unknown → keep local + state ambiguity" fallback.
    Rejected B2 because zero-config inference is fragile and risks filing harness
    issues into the wrong repo; portability must be explicit config, not a guess.
- **C — Generalization mechanism.**
  - C1 prompt-only guidance (generalize the pattern, cite incident as evidence).
  - C2 presence-only structured field (separate "Structural pattern" and
    "Triggering instance(s)"), deterministic check verifies presence only.
  - **Chosen: C2 layered on C1.** Rejected C1-only because prose drifts and is
    not auditable; rejected any quality-judging check because the achieve
    disposition-floor guardrail forbids a content classifier. Presence-only is
    the maximum enforcement allowed.
- **D — Over-split / volume rule.**
  - D1 split only when a finding has both a generalizable upstream fix and a
    distinct current-repo-local adaptation; else single destination.
  - D2 always propose both buckets and let the human prune.
  - **Chosen: D1** (assumed default, unobjected). Rejected D2 because mechanical
    dual-filing doubles backlog noise and double-counts one root cause.
- **E — Current repo *is* charness.**
  - E1 collapse: "upstream" == this repo; split becomes portable-skill-core vs
    repo-local operating surface (this repo's adapters, AGENTS.md, fixtures).
  - E2 suppress the destination split entirely in the charness repo.
  - **Chosen: E1** (assumed default, unobjected). Rejected E2 because the split
    is still meaningful in-repo (portable skill core vs this repo's operating
    surface) and suppressing it would make the dogfood (F2) vacuous here.
- **F — Scope of this goal.**
  - F1 capability/behavior only (teach the skills to propose generalized, split
    issues); no real backlog filed now.
  - F2 capability + dogfood: also file the split backlog for this repo from
    recent waste retros.
  - **Chosen: F2.** The user opted into dogfooding; the feature and its first
    real outputs share one standard (Boundaries), which is the charness way and
    gives live proof. This authorizes real issue creation as a consequential
    side effect.

## Plan Critique Findings

Anticipated blockers (to fold into Boundaries after discussion) and over-worry,
recorded before activation so a fresh session re-verifies rather than re-derives:

- **Blocker risk — classifier creep.** Axis 1 invites a deterministic "is this
  structural?" check, which directly violates the achieve disposition-floor
  guardrail. Mitigation: keep any check presence-only (C2), never quality.
- **Blocker risk — wrong-repo filing.** A portable upstream pointer that is
  absent or misconfigured in a consumer repo could file harness issues into the
  wrong place. Mitigation: safe default = keep local + state the ambiguity (B1
  fallback), never guess the target.
- **Blocker risk — issue spam / double-count.** Mechanical split doubles volume
  and pollutes backlogs. Mitigation: D1 rule, single destination by default.
- **Blocker risk — dogfood premature/noisy issues (F2).** Filing real issues
  before the feature is settled could create low-quality backlog. Mitigation:
  the dogfood slice runs last (slice 5), after the contract + presence field +
  split rule exist, and every dogfood issue must clear the same bar through
  normal `issue` discipline and backend verification.
- **Over-worry (not folding) — multi-skill surface area.** A4-lite touches three
  skills plus mirrors; feels heavy. But each axis is small prose + one presence
  field; the standalone-usefulness boundary is the real constraint, not raw
  surface count.
- **Provenance:** self-critique during Before-phase shaping; a fresh-eye bounded
  review is planned at slice 6, not yet run.

## Off-Goal Findings

(none yet)

## Final Verification

- Implementation commit: `6432d6c1 Add generalized, destination-split retro issue proposals`
  plus a follow-up review-fix commit (regex presence bug + regression test +
  docstring depths).
- Self-verification (high-confidence, ran):
  - Targeted gates green: `validate_skills`, `validate_adapters`,
    `validate_skill_ergonomics`, `check-markdown`, `check_doc_links`,
    `check_references_link_inventory`, `check_skill_contracts` all exit 0.
  - Pytest: `test_issue_proposal_fields.py` 9/9 (present-vague pass, bullet pass,
    missing-field fail, **empty-value-treated-as-missing** fail, bad-enum fail,
    resolve-destination collapse/consumer/unknown); plus
    `test_issue_skill`/`test_retro_skill`/`test_achieve_before_activation`/
    `test_goal_disposition_gate` and the previously-failing
    `test_validate_adapters_accepts_checked_in_charness_quality_coverage_floor`.
  - Broad read-only gate `run-quality.sh --read-only`: after fixes, the only
    residual fails are environmental (see Non-claims), not feature defects.
  - Backward compat: bare `resolve_adapter.py` still dumps the adapter; new
    `resolve-destination` subcommand returns collapse for this repo.
- Fresh-eye review: a different-context bounded reviewer (verdict
  `ship-with-nits`) confirmed B1/E1 resolver correctness, mirror fidelity,
  unbloated `issue/SKILL.md`, and presence-only (non-classifier) semantics; it
  caught one real presence bug, which was fixed + regression-tested before
  closeout. Recorded in
  `charness-artifacts/critique/2026-06-03-retro-issue-structural-decouple-split-disposition-review.md`.
- Live proof (dogfood, ran): filed #284 (upstream-harness) and #285 (repo-local)
  to `corca-ai/charness`; both verified `OPEN` with the presence fields in body.
- Retro: `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`.
- Host log probe: `charness-artifacts/probe/2026-06-03-retro-issue-structural-decouple-split.json`.
- Non-claims (not proven):
  - The **consumer-repo** path (current repo ≠ `harness_upstream`) is unit-tested
    only; it was not exercised live, because this run is in the charness repo
    itself (E1 collapse). The first non-charness adopter should exercise it.
  - `validate_proposal_fields.py` is an **advisory** presence check; it is not
    wired into a blocking gate, so it informs proposal authoring but does not
    enforce it at commit time.
  - Deep per-session token/turn counts are not asserted; the host probe is
    thread/session-level (no `Host metric window:` line existed before work).
  - No release was cut; no existing tracked issue was closed (this run *creates*
    follow-up issues).

## User Verification Instructions

- Read `skills/shared/references/retro-issue-destination-split.md` for the two
  axes and the D1/B1/E1 rules.
- Confirm presence-only behavior:
  `printf 'Structural pattern:\nTriggering instance(s): x\nDestination: repo-local\n' | python3 skills/public/issue/scripts/validate_proposal_fields.py`
  returns `ok:false` (empty value treated as missing), while a vague-but-present
  value returns `ok:true`.
- Confirm collapse routing for this repo:
  `python3 skills/public/issue/scripts/resolve_adapter.py --repo-root . resolve-destination --current corca-ai/charness`
  → `mode: collapse`, both targets `corca-ai/charness`.
- Run `python3 -m pytest tests/quality_gates/test_issue_proposal_fields.py -q`.
- Inspect the filed issues: `gh issue view 284 --json state,title`;
  `gh issue view 285 --json state,title`.

## Auto-Retro

Cited retro: `charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md`
(substantive findings inline below; the file carries the full Waste / Critical
Decisions / Expert Counterfactuals / Sibling Search).

- Waste this run: edited skill surfaces at the conciseness/ergonomics ceiling
  with no pre-edit headroom signal, forcing a revert (issue body) + trims +
  re-syncs after the broad gate; reference-depth and wrapped-span fixes added two
  more gate cycles.
- Critical decisions: A4-lite distribution (each skill standalone), presence-only
  validator (respect the disposition-floor guardrail), B1 adapter pointer + E1
  collapse over prompt inference.

Dispositions (each surfaced improvement is `applied` or `issue #N`):

- applied: the feature itself — shared contract + retro/achieve/issue wiring +
  `harness_upstream` resolver + presence-only validator + tests (commit `6432d6c1`).
- applied: fixed the validator presence bug the fresh-eye review caught and added
  `test_empty_value_treated_as_missing` (this run).
- issue #284: pre-edit preflight for skill-surface edits (headroom / known
  couplings / markdown spans) — Destination: upstream-harness.
- issue #285: stop hard-pinning live issue numbers in repo test fixtures —
  Destination: repo-local.
- Retro: charness-artifacts/retro/2026-06-03-retro-issue-destination-split.md
- Host log probe: charness-artifacts/probe/2026-06-03-retro-issue-structural-decouple-split.json
- Disposition review: charness-artifacts/critique/2026-06-03-retro-issue-structural-decouple-split-disposition-review.md
