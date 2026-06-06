# Achieve Goal: Repo quality scan + closeout-discipline gates

Status: complete
Created: 2026-06-06
Activation: `/goal @charness-artifacts/goals/2026-06-06-quality-scan-closeout-discipline.md`
Timebox: 3h
Activation time: 2026-06-06T06:16:29Z (closeout reserve begins 2026-06-06T08:56:29Z)
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: **complete** — all 6 slices done, closeout finished well within
  the timebox (closeout reserve began 2026-06-06T08:56:29Z; finished ahead).
- Outcome: honest refreshed quality posture (71/0 read-only, 72/0 full); #2b +
  #2a closeout-discipline improvements committed; advisory-interpretation contract
  first cut landed with the rollout split to #322. Retro persisted; every
  improvement dispositioned. No release (per Non-Goals).
- Timebox: 3h from activation; protect the final 20m for broad gate + retro +
  disposition + commit + user closeout. If the macro outcome finishes early,
  continue to the next safe in-scope improvement (do not close on first item).
- Slice order: (1) quality posture scan → (2) #2b cross-file sibling-scan
  enforcement → (3) #2a advisory RCA-ledger nudge → (4) fold cheap scan wins /
  file the rest → (5) advisory epistemic-status + agent-interpretation contract
  (first cut, **splittable** to issue/spec) → (6) closeout. Run sequentially.
  Slice 5 is the natural cut point: if the clock or scope demands, split its
  remainder to an issue (+ optional spec) and proceed to closeout. #2a is the
  next-most deferrable.
- Verification cadence: cheap deterministic checks at commit boundaries
  (`run_slice_closeout.py --predict-commit` aggregate); higher-cost or fresh-eye
  proof at slice boundaries; final broad `./scripts/run-quality.sh` at closeout.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces (plugins/ + mutants/ mirrors for any
  `scripts/` edit), expected invariants, tests/proof, non-claims, out-of-scope
  lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Run a full repo quality posture pass on clean `main` (v0.24.1 shipped), then land
the concrete improvements it surfaces — folding in the #320-diagnosed
closeout-discipline gap:

1. **Quality posture scan** (`find-skills` → `quality`): detect and run the
   existing gates, walk the four lenses, run one bounded fresh-eye review, and
   refresh `charness-artifacts/quality/latest.md` with a prioritized list of
   improvement candidates (`nose` clone advisory — the optional binary is
   absent, so that inventory stays a deferred integration-manifest dependency,
   not a repo requirement).
2. **#2b — enforce the cross-file sibling scan.** Today `validate_debug_artifact.py`
   only checks `## Sibling Search` for shape + follow-up identifiers
   (`validate_sibling_followups`); a within-file-only scan still passes, so the
   sibling-search reference's cross-file requirement is unenforced. Add real
   enforcement with a justified escape hatch.
3. **#2a — advisory RCA-ledger nudge.** When a slice adds a new
   `charness-artifacts/debug/*.md` artifact but no `rca-ledger.jsonl` event
   `ref`s it, emit an advisory (exit-0) warning. Non-gated by design.
4. **Advisory epistemic-status + agent-interpretation contract (first cut,
   splittable).** Generalize the judgment-over-automation principle exercised in
   #2b: as deterministic heuristics improve, the agent risks deferring to them
   instead of interpreting. Land a *pilot* — a shared reference requiring an
   advisory/heuristic (inference-layer) output to self-declare what it measures,
   what it is a proxy *for*, its known blind spots, and the interpretation
   question it cannot answer; and require the consuming skill to answer that
   question before acting — applied to one pilot surface (the `quality` advisory
   output and/or the `nose` duplicate advisory). Split the cross-skill rollout to
   an `issue` (Structural pattern + Triggering instances), promoting to `spec` if
   it grows. This is positive-form (declare blind spots), NOT a blanket "distrust
   me" banner, and it does NOT attach to verifiable deterministic facts.

Outcome = an honest refreshed quality posture, the two closeout-discipline
improvements committed (or dispositioned to issues), and a landed first cut of
the advisory-interpretation contract (or its clean split to issue/spec) — with
the repo green on the broad gate.

## Non-Goals

- **No release.** No version bump, tag, publish, or push in this goal; v0.24.1 is
  the shipped surface. A release is a separate later goal.
- **Not reopening #320 / v0.24.1** — shipped and verified; do not relitigate the
  changed-line coverage work, only build on the closeout-discipline diagnosis it
  surfaced.
- **No gating of the RCA conversion rate and no forced RCA-event append.** The
  #2a nudge stays advisory-only (anti-gaming, per the rca-conversion-ledger spec
  Fixed Decision 5 + validator-posture Probe Question: schema validity is
  gated, the rate and the append are not).
- **Not #184** (product-success metric definition) — deferred-by-judgment,
  needs maintainer input, out of scope here.
- **No broad test-suite prune and no test-count ceiling.** Standing test
  economics is advisory-by-design; the durable lever is shrinking the
  release-only CLI lifecycle surface, which is out of scope unless a cheap,
  obviously-correct win falls out of the scan.
- **Not the carry-forward real-host / second-machine `nose` proof** — separate
  standing item, not this goal.
- **Not the full cross-skill rollout of the advisory-interpretation contract.**
  Slice 5 lands a pilot + the shared reference only; the broad rollout across
  every advisory surface is split to an issue (+ optional spec), by design.

## Boundaries

- **Appetite (operator-chosen):** new deterministic gates / validators / tests /
  hooks are in-scope when they close a real recurrence class. Carve-out: the
  RCA-ledger nudge stays advisory-only.
- **#2b signal must be authorable, not parsed from prose (plan-critique
  blocker, folded).** Do NOT enforce "a sibling location in a file other than
  the subject": the real debug corpus (41 of 60 artifacts carry `## Sibling
  Search`) uses prose-axis bullets, not the reference's `file:line` token, and
  there is no `Subject:`/source-file field in the schema — so a deterministic
  foreign-`file:line` parser would either mass-regress correct artifacts or
  collapse to a gameable "any `*.py` mention" check (the reference's own
  over-reach guard). Instead enforce an **explicit author-added marker** —
  `cross-file: <path-or-axis note>` OR `no cross-file sibling: <reason>` —
  modeled on how `validate_sibling_followups` already requires `follow-up:`.
  This is a new shape contract, so the slice must also update
  `skills/public/debug/references/sibling-search.md` to document the marker.
- **#2b enforcement scope = `latest.md` / forward-only (decided at shaping).**
  Add the cross-file marker check inside the `path.name == "latest.md"` branch
  of `validate_debug_artifact.py:214` (where the other current-form checks
  already live), NOT in the shared `validate_sibling_followups` (which runs on
  all 60 artifacts and would mass-regress the 41 token-less historical ones). A
  new debug artifact is the current pointer (`latest.md`) at closeout, so this
  enforces the marker on every new closeout exactly when it is authored — no
  corpus migration, no grandfather list, history stays immutable. Rejected
  all-dated enforcement: it edits immutable records (retroactively asserting a
  scan that may not map) or adds a maintained date-cutoff exemption, for the low
  marginal value of re-validating closed artifacts. Non-claim to record in the
  slice: if two debug artifacts are created in one slice, only the last is
  `latest.md` and gets the strict check that cycle (dominant flow is
  one-at-a-time).
- **Phase barriers:** treat `mutate -> sync -> verify -> publish` as hard. Any
  `scripts/*.py` edit is mirrored to `plugins/charness/scripts/` (and the
  `mutants/` mirror); run the sync before the verify gate, not after.
- **External side-effect scope:** name which phase or bundle any approved
  publish / push / remote-CI / apply applies to. That approval is phase-scoped
  and does not carry forward — after an approved publish/CI/apply lane
  completes, done-early test-only quality continuation is local by default
  (batch remote proof, run CI once over the final bundled state). Per-slice
  remote publication is assumed only when the operator explicitly asks or a
  runtime-affecting slice requires earlier publication. (This goal plans no
  external side effects — see Non-Goals.)
- **Advisory-interpretation contract = inference layer only (slice 5).** The
  self-declaration + agent-interpretation requirement attaches ONLY to
  heuristic/proxy/ranking outputs (nose duplicate %, ergonomics heuristics,
  test-economics trend, recommendation rankings). It must NOT attach to
  verifiable deterministic facts (green gates, counts, AST results): inducing
  distrust there reintroduces the manual-ritual waste validators exist to
  remove, contradicting "validator over prose ritual."
- **No blanket distrust banner (slice 5).** The contract is positive-form — the
  output declares its blind spots and the interpretation question it cannot
  answer, and the consumer must answer it — not a generic "don't trust me"
  string repeated on every output (which habituates the reader into ignoring it
  and adds noise). It generalizes `automation-promotion`'s "do not repeat
  without repository-level interpretation" from a passive prohibition into an
  active requirement; the existing fresh-eye subagent review is the real
  independent-intelligence backstop.
- **Slice 5 is splittable by design.** If the pilot + reference exceed the
  remaining timebox or grow beyond a clean low-noise change (per the
  `automation-promotion` AUTO_CANDIDATE checklist), split the remainder to an
  `issue` (Structural pattern + Triggering instances) and optionally a `spec`,
  record the cut point in `## Off-Goal Findings`, and proceed to closeout. A
  partial landing is safe because the change is advisory; a clean split is a
  success, not an early-stop failure.
- Discuss before activation: Approved at shaping — operator selected scope =
  full quality scan + fold-in #2 + a fourth advisory-interpretation slice
  (sequential, splittable), a 3h timebox, and appetite = new gates/validators
  allowed with the RCA-ledger nudge held advisory-only (anti-gaming). No
  release/push/tag in this goal; #320 and #184 appear as context only and are
  neither reopened nor closed here. The two behavior-affecting prompt/validator
  changes (#2b debug-closeout validator; the slice-5 advisory-interpretation
  contract) are each bounded above (the #2b brittleness escape; the slice-5
  inference-layer-only + no-blanket-banner + splittable guards) and each get a
  fresh-eye slice critique before commit.

## User Acceptance

What the user can do to verify completion directly:

- Read the refreshed `charness-artifacts/quality/latest.md` — posture, gates run,
  and the prioritized improvement list with each item dispositioned.
- Run `./scripts/run-quality.sh --read-only` and see it green on the final state.
- See #2b enforced: a debug artifact whose `## Sibling Search` never leaves its
  own subject file (and records no `no cross-file sibling:` reason) now FAILS
  `validate_debug_artifact.py`; a real cross-file artifact still passes — proven
  by a committed fixture test.
- See #2a advisory: a new debug artifact with no matching `rca-ledger.jsonl`
  `ref` prints an advisory warning at exit 0 (no fail); adding the ref silences
  it.
- See every surfaced improvement dispositioned in `## Auto-Retro` as
  `applied: <what>` or `issue #N` — no prose-only memory.

## Agent Verification Plan

### Low-Cost Checks

- `run_slice_closeout.py --predict-commit` aggregate (runs
  `validate_skill_ergonomics` + `check-markdown` + changed-surface checks) at
  each commit boundary.
- For #2b: targeted `pytest` over the new debug-validator fixture (within-file
  scan fails; cross-file passes; `no cross-file sibling:` escape passes).
- For #2a: run the nudge script against a fixture debug artifact with and
  without a ledger `ref`; assert warn-exit-0 vs silent.
- After any `scripts/` edit: run the mirror sync, then `validate_rca_ledger.py`
  / `validate_debug_artifact.py` on a sample.

### High-Confidence Checks

- One bounded fresh-eye slice critique before commit on EACH behavior-affecting
  prompt/validator slice — the #2b debug-closeout validator and the slice-5
  advisory-interpretation contract — each with its own slice packet.
- `quality` skill's four-lens walk + one bounded fresh-eye review for slice 1.
- Regression floor (scope = `latest.md`/forward-only): the marker check lives in
  the `latest.md` branch only, so the 59 dated artifacts are untouched — prove
  it by re-running `validate_debug_artifact.py` over the real corpus and
  confirming all dated artifacts still pass unchanged (no historical
  regression). Prove the new rule with fixtures: a `latest.md`-form artifact
  whose `## Sibling Search` lacks the marker FAILS; one carrying `cross-file:`
  or `no cross-file sibling: <reason>` PASSES. Either way the assertion is explicit
  code/test, not prose.

### External Or Live Proof

- None planned (no release, push, or live host contact this goal). Final broad
  proof is the local `./scripts/run-quality.sh` full run over the bundled state;
  name it explicitly as deterministic-local, not provider/live. Real-host
  `nose` proof stays a separate carry-forward item and is a stated non-claim
  here.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Quality posture scan (`find-skills` → `quality`) | Handoff Next Session #1 planned focus; surfaces the improvement candidates that scope slices 2–4 | Refreshed `quality/latest.md` (140 lines, validators green); `run-quality.sh --read-only` 71/0; bounded fresh-eye review REVISE→folded; prioritized candidate list + nose-now-active delta | **done** |
| 2 | #2b sibling-scan marker enforcement in the `validate_debug_artifact.py` `latest.md` branch (+ reference doc) | Diagnosed in the #320 slice; the reference's cross-file requirement is unenforced (shape-only) | Marker check added to the `latest.md` branch only; fails a `latest.md`-form `## Sibling Search` missing the `cross-file:` / `no cross-file sibling:` marker, passes one with it; 60 dated artifacts stay green; `sibling-search.md` + scaffold updated; mirrors synced; 35 tests pass; fresh-eye critique CLEAR; 71/0 | **done** |
| 3 | #2a advisory RCA-ledger nudge (exit-0, in the slice-closeout aggregate) | Diagnosed in the #320 slice; prompt-only append is deliberately non-gated, so add advisory detection of unlinked debug artifacts | `scripts/rca_link_advisory.py` warns at exit 0 for an added debug artifact with no matching ledger `ref`, silent when a `ref` exists; wired into `run_slice_closeout.py --predict-commit` via an `advisory_provider` hook (not a standalone promotable gate); no fail path; 9 in-process tests + wiring test + real-repo smoke; 71/0 | **done** |
| 4 | Fold cheap scan wins / file the rest | Keep the goal honest: apply only obviously-correct cheap improvements, route the rest to issues | One cheap fold applied (refactor pulling `run_slice_closeout.py` back under the python-lengths advisory band, a slice-3 length-creep); all other candidates dispositioned as gate-tracked watch or maintainer-deferred (#184) in Off-Goal Findings; no new issues; 71/0 | **done** |
| 5 | Advisory epistemic-status + agent-interpretation contract (first cut, **splittable**) | Generalizes the #2b judgment-over-automation principle; the goal already touches advisory surfaces (scan, nose, RCA nudge) so it is the natural pilot home | Shared reference `advisory-interpretation-contract.md` written (inference-layer self-declaration + consumer-must-answer; explicit "not verified facts"; no blanket banner); applied to the `nose` pilot; consumer requirement in `automation-promotion.md`; 4 tests; rollout split to **issue #322**; cut point in Off-Goal Findings; 71/0; fresh-eye critique folded below | **done** |
| 6 | Closeout | Bundle proof + reflection within the closeout reserve | Full `./scripts/run-quality.sh` 72/0; session `retro` persisted + RCA event; every improvement dispositioned; Final Verification + User Verification + Auto-Retro written; handoff updated | **done** |

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
  applies. (Expected `n/a` here: all context is repo-local.)
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`. (Expected `n/a` — Non-Goals bar a
  release.)
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`. (#320/#184 are context-only; any new issues
  filed for deferred candidates are off-goal findings, not closeouts.)

**Resolved at closeout:**

- **Routing:** slice 1 → `quality` (find-skills `--recommend-for-task`, matched
  trigger `quality`); slices 2–5 → `impl`-class (find-skills task-text returned no
  public-skill match for the validator/advisory/reference implementation verbs —
  durable code/test/reference work).
- **Gather:** n/a — all context is repo-local (no external URL/Slack/Notion/Docs).
- **Release:** n/a — Non-Goals bar any version bump, tag, publish, or push.
- **Issue closeout:** n/a — this goal closes no tracked issue. New issue **#322**
  (advisory-interpretation rollout) is an off-goal finding, not a closeout; #321
  (mutation regression) and #184 (product metrics) are out of scope / deferred.

## Slice Log

### Slice 1 — Quality posture scan (done, 2026-06-06)

- **Routing:** `find-skills --recommend-for-task` → `quality` (public skill),
  matched trigger `quality`; adapter local-first defaults (no trusted roots).
- **Result:** refreshed `charness-artifacts/quality/latest.md` (was stale at
  v0.20.0; now v0.24.1, 140 lines, passes `validate-quality-artifact` +
  `validate-inventory-consumption` + `validate-quality-closeout-contract`).
  Archived prior pass to `history/2026-06-05-quality-review.md`.
- **Gates:** `run-quality.sh --read-only` = 71 passed, 0 failed (~43s, profile
  `local-linux-x86_64-36cpu`). `plan_cautilus_proof.py` next_action=none → no
  eval. `validate_usage_episodes` 596 / `validate_attention_state_visibility` 72.
- **Key delta:** `inventory-nose-clones` is now ACTIVE — the `nose` binary
  (0.5.0) is present locally, where the goal premise assumed absent. 20 families
  / 1951 dup-lines, dominated by intentional per-package `resolve_adapter.py`
  boilerplate. This becomes slice 5's pilot surface (proxy-needs-interpretation),
  not a new gate. The goal's "nose absent" framing is corrected as a non-claim.
- **Fresh-eye review:** one bounded reviewer (read-only, shared parent worktree,
  `high-leverage`) → **REVISE → folded**. Critical catch: my first comprehensive
  draft was 230 lines and tripped `validate-quality-artifact`'s 140-line cap
  (flipping the gate to 70/1); trimmed to 140 to restore 71/0. Also corrected the
  coverage bullet (`check-coverage` is changed-path-gated, did not run this turn;
  44.x s is a recorded sample). Verdict after fold: no new repo-owned gate
  missing — tier is "extend existing gates", #2b/#2a targeted correctly.
- **Candidate list → slice scoping:** #2b (cross-file sibling marker, slice 2,
  AUTO_CANDIDATE) and #2a (RCA-ledger nudge, slice 3, advisory-by-design)
  confirmed as the only real enforcement holes; nose-interpretation → slice 5;
  test-economics + coverage-brush + python-lengths WARN = watch items (slice 4
  carry-forward, no cheap obviously-correct fold surfaced).
- **Non-claims:** the 44.x s coverage timing is a recorded prior-run sample, not
  this `--read-only` invocation; the `nose` proof is local-profile only (real-host
  second-machine proof remains a separate carry-forward).

### Slice 2 — #2b cross-file sibling marker enforcement (2026-06-06)

- **Routing:** `find-skills --recommend-for-task` returned no public-skill match
  for the validator-implementation task text (verbs add/check/validator match no
  trigger noun); this is durable `impl`-class work (the owner of code/validator/
  test changes). Recorded as `Routing: impl (find-skills task-text empty)`.
- **Change:** new `validate_cross_file_sibling_marker(lines)` in
  `scripts/validate_debug_artifact.py`, called in the `path.name == "latest.md"`
  branch only (after `validate_sibling_followups`). Requires `## Sibling Search`
  to carry `cross-file: <path-or-axis>` OR `no cross-file sibling: <reason>`
  (trivial-fix short-circuit also satisfies). Authored marker, not a prose parser
  — the brittleness-escape decision from the plan critique. Documented in
  `sibling-search.md` ("## Declare cross-file scope"); scaffold template gains a
  `cross-file:` prompt line so new artifacts are born compliant.
- **Forward-only scope:** the check lives in the latest.md branch only; the 60
  dated artifacts route through the else-branch and are untouched (goal said 59;
  actual corpus is 60 dated + latest.md — count corrected as a non-claim).
  Truthful `cross-file:` marker added to the current `debug/latest.md` (#320) so
  the gate stays green — the #320 selection-budget axis genuinely names the two
  `setup_*_lib` files outside the subject `staged_commit_gate_plan.py`. Not
  reopening #320 (no coverage relitigation).
- **Proof:** `pytest tests/test_debug_artifact.py tests/test_debug_scaffold.py`
  = 35 passed (5 new: missing-marker FAILS, escape PASSES, empty-marker FAILS,
  dated-not-required PASSES, trivial-short-circuit satisfies).
  `validate_debug_artifact.py` exit 0 over the real 61-file corpus.
  `run-quality.sh --read-only` = 71/0. Mirror synced (`sync_root_plugin_manifests`).
  Caught + fixed one inline-code-span wrap in the ref doc (the recurring
  `check-markdown` trap from recent-lessons).
- **Fresh-eye critique:** bounded reviewer (read-only, shared parent worktree) →
  **CLEAR**. Independently verified: (A) the marker check is reached ONLY in the
  `latest.md` branch — traced the code + re-ran the 61-file corpus, dated artifacts
  bypass it; (B) marker logic sound, `cross-file:` does not substring-collide with
  `no cross-file sibling:`, empty markers fail, case-insensitive; (C) the #320
  `cross-file:` marker is truthful — confirmed `setup_agent_docs_fresh_eye_lib.py`
  / `setup_commit_discipline_lib.py` exist outside the subject; (D) no gap /
  regression / over-reach, test coverage comprehensive, scaffold round-trips. No
  blocking corrections.

### Slice 3 — #2a advisory RCA-ledger nudge (2026-06-06)

- **Routing:** `impl`-class (no find-skills public-skill match for the
  advisory-helper task text). Advisory-only slice → no fresh-eye critique
  required by the goal (High-Confidence Checks scope critique to #2b + slice 5).
- **Change:** new `scripts/rca_link_advisory.py` (export-safe, standalone
  `main()` per the verification plan) detects dated `debug/*.md` additions with no
  matching `rca-ledger.jsonl` `ref` and emits exit-0 `ADVISORY:` lines (silent
  when linked, `latest.md` pointer excluded). Wired into the predict-commit
  aggregate via a generic `advisory_provider` hook added to
  `staged_commit_gate_plan.run_predict_commit` (kept RCA-free) — the provider in
  `run_slice_closeout.py` re-derives added-only staged paths. Never blocks; not a
  promotable gate (no failure path).
- **Proof:** `tests/test_rca_link_advisory.py` (9 in-process tests:
  classification, linked→silent, unlinked→warn, pointer/non-debug ignored,
  ledger-absent→warn, `main()` exit-0 both ways) + a `run_predict_commit`
  advisory-wiring test in `test_staged_commit_gate_plan.py`. Real-repo smoke:
  a ledger-linked path is silent, an unlinked path warns at exit 0; a staged
  temp debug artifact surfaced the advisory through the full predict-commit
  aggregate then `pre-commit: ok`. `run-quality.sh --read-only` = 71/0.
- **Caught + fixed:** the first test subprocessed the CLI, which tripped
  `check-boundary-bypass-ratchet` (a *new* convertible boundary). Rewrote the
  test fully in-process (the ratchet's intended direction) — ratchet green, no
  exemption needed. Mirror synced.

### Slice 5 — advisory-interpretation contract pilot (2026-06-06)

- **Routing:** `impl`-class (reference + script change). Behavior-affecting →
  fresh-eye critique required (verdict folded below).
- **Change:** new shared reference
  `skills/shared/references/advisory-interpretation-contract.md` — an
  inference-layer output self-declares measures / proxy-for / blind-spots /
  interpretation-question, and the consumer must answer the question before
  acting. Inference-layer ONLY (explicitly excludes verified facts: green gates,
  counts, AST results); positive-form, no blanket distrust banner. Generalizes
  `automation-promotion.md` + `agent-assessment-invariant.md` from passive
  prohibition to active requirement. **Pilot:** `inventory_nose_clones.py` emits
  an `interpretation` self-declaration (payload + a `print_human` INTERPRETATION
  line) — measures lexical clone families, proxies refactorable debt, blind to
  intentional per-package boilerplate, asks "intentional vs extractable?".
  `automation-promotion.md` gains the consumer-must-answer requirement.
- **Split / cut point (by design):** the cross-skill rollout to the other
  inference-layer surfaces (ergonomics heuristics, test-economics trend,
  lint-suppression pressure, length smell, recommendation rankings, runtime
  trend) is split to **issue #322** (Structural pattern + Triggering instances +
  proposed rollout; promote to `spec` if it grows). The pilot + reference + one
  consumer requirement is the clean low-noise first cut; the rest is the issue.
- **Proof:** `pytest tests/quality_gates/test_quality_nose_advisory.py` = 4 passed
  (asserts the 4-field self-declaration + the human INTERPRETATION line). Real
  output prints the INTERPRETATION line. Mirror synced; doc-links fixed
  (`../../../shared/...`). `run-quality.sh --read-only` = 71/0.
- **Fresh-eye critique:** bounded reviewer (read-only, shared parent worktree) →
  **CLEAR**. Verified all five design boundaries: (A) the contract explicitly
  protects verified facts (inference-layer only, quotes "validator over prose
  ritual"); (B) positive-form per-measure declaration, not a habituating distrust
  banner; (C) the `nose` self-declaration is truthful — independently confirmed
  16 near-identical `resolve_adapter.py` files across skill packages match the
  declared blind spot — and the consumer requirement is actionable; (D) faithful
  passive→active generalization of `automation-promotion.md` +
  `agent-assessment-invariant.md` (a tightening, not a contradiction); (E) clean
  low-noise, exit-0, no scope creep, rollout correctly split to #322. No blocking
  corrections.

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order:

1. [docs/handoff.md](../../docs/handoff.md) — Next Session #1 (full quality scan
   + improvements) and #2 (closeout-discipline gap, with the "run critique +
   read recent-lessons first, do NOT rush" instruction).
2. [charness-artifacts/quality/latest.md](../quality/latest.md) — last posture
   pass (all 71 gates green; watch items: coverage brush, standing test
   economics; `nose` clone skipped).
3. [charness-artifacts/retro/recent-lessons.md](../retro/recent-lessons.md) —
   repeat traps (mutate→sync→verify rhythm, `scripts/` mirrors to
   `plugins/charness/scripts/`).
4. [#320 debug artifact](../debug/2026-06-06-issue-320-mutation-changed-line-coverage.md)
   — where the closeout-discipline gap was diagnosed.
5. [rca-conversion-ledger spec](../spec/rca-conversion-ledger.md) — Fixed
   Decision 5 + validator-posture Probe Question fix the advisory-only / anti-
   gaming posture for #2a.
6. [sibling-search reference](../../skills/public/debug/references/sibling-search.md)
   — the four-axis cross-file scan requirement #2b must enforce.
7. `scripts/validate_debug_artifact.py` + `scripts/artifact_validator.py`
   (`validate_sibling_followups`) — the shape-only validator surface #2b
   extends; `scripts/record_rca_event.py` / `validate_rca_ledger.py` /
   `aggregate_rca_ledger.py` + `charness-artifacts/metrics/rca-ledger.jsonl` —
   the ledger surface #2a nudges toward.
8. [prior 318-319 goal](2026-06-06-318-319-achieve-closeout-and-quality-headroom.md)
   — the most recent completed quality-headroom goal, for format and cadence.
9. [agent-assessment-invariant](../../skills/shared/references/agent-assessment-invariant.md)
   and [automation-promotion](../../skills/public/quality/references/automation-promotion.md)
   — the two existing contracts slice 5 generalizes (agent judgment before human
   handoff; "do not repeat an automated finding without repository-level
   interpretation", heuristics stay advisory until a low-noise invariant exists).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Scope** — family {full scan + fold-in #2, #2-only, scan-only/defer-#2}.
  Chosen: **full scan + fold-in #2** (handoff's planned focus). Rejected:
  #2-only strands the planned full posture pass; scan-only re-defers a gap that
  is already diagnosed and cheap to close now. `single-point` — a one-time scope
  decision, not a system axis.
- **Timebox** — family {none, 2h, 3h}. Chosen: **3h** (matches recent goal
  cadence). Rejected: none → no enforceable closeout reserve; 2h → too tight for
  a scan plus two prompt/validator slices each needing critique. `single-point`.
- **Appetite** — family {new gates/validators allowed, advisory/docs-only}.
  Chosen: **gates/validators allowed**, with the RCA nudge held advisory.
  Rejected: advisory-only would re-defer the sibling-scan gap (it needs real
  enforcement to actually close). `axis: gate-posture` — the repo already varies
  here (e.g. `validate_rca_ledger` gates schema while the conversion rate stays
  advisory; standing test economics is advisory-by-design). The RCA-nudge
  carve-out is anchored to that existing axis, not a global "everything must
  gate" default.
- **#2b enforcement scope** (resolved at shaping after the plan critique) —
  family {`latest.md`/forward-only, all-dated + migrate/grandfather}. Chosen:
  **`latest.md`/forward-only**. Rationale: a new debug artifact is `latest.md`
  at closeout, so forward-only enforcement catches every new closeout without
  editing the 41 immutable historical artifacts. Rejected all-dated: history
  churn or a maintained cutoff exemption for the low value of re-validating
  closed records. `axis: artifact-lifecycle` — the validator already varies
  current-form strictness by `latest.md` vs dated, so this anchors to an
  existing axis rather than inventing one.
- **Advisory-interpretation concern → slice or issue** (raised mid-shaping:
  "as deterministic heuristics/nose improve, the agent may over-defer instead of
  using its own intelligence; should advisory output carry a 'read critically'
  prompt?"). Family {fold as a goal slice, file as an issue, defer to ideation}.
  Chosen: **fold as a sequential, splittable slice 5**. Rejected: issue-only
  loses the chance to pilot it on the advisory surfaces this goal already
  touches; defer-to-ideation drops the momentum. The mechanism was refined away
  from the literal proposal (a blanket "distrust" banner) to a positive-form
  self-declaration + required consumer interpretation, scoped to the inference
  layer only — because the repo already trusts verifiable deterministic facts by
  design (`agent-assessment-invariant.md`, `automation-promotion.md`).
  `axis: gate-posture` — same automation-vs-judgment axis as the appetite
  decision; this targets the *advisory* end of it without touching the verified
  end.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

**Reviewer provenance:** one bounded fresh-eye plan critic (read-only, shared
parent worktree), Before-phase. It read `validate_debug_artifact.py`,
`artifact_validator.py` (`validate_sibling_followups`), the rca-conversion-ledger
spec, the sibling-search reference, the handoff, and 4 real debug artifacts.
Verdict: **REVISE** → two blockers folded; #2a scoping, slice ordering, and the
anti-anchoring tags confirmed SOUND.

**Blockers folded:**

1. *#2b "cross-file location" is not derivable from real artifact text.* The
   corpus uses prose-axis bullets, not the reference's `file:line` token, and
   there is no `Subject:` schema field, so a deterministic foreign-`file:line`
   parser would mass-regress correct artifacts or be trivially gamed. Folded
   into Boundaries as an **explicit author-added marker** (`cross-file:` /
   `no cross-file sibling:`) modeled on `follow-up:`, with a required
   `sibling-search.md` doc update.
2. *Regression floor was hollow.* The validator only runs the current-form
   `## Sibling Search` checks for `debug/latest.md`; dated artifacts skip that
   section. Folded into Boundaries (declare enforcement scope explicitly) and
   the High-Confidence regression floor (hard-assert PASS on the 41 existing
   `## Sibling Search` artifacts if extended to dated artifacts, else state
   latest.md/forward-only and drop the across-corpus claim).

**Over-worries raised, not folded as blockers:**

- *#2a advisory scoping is correct* per spec Fixed Decision 5 + the
  validator-posture Probe Question (schema gated, rate/append advisory); the
  spec's slice-2 residual-risk text even pre-describes this advisory nudge.
  Recorded refinement (now in Slice 3): pin the nudge to the slice-closeout
  aggregate as an exit-0 advisory line, not a standalone gate that could later
  be promoted.
- *`nose` advisory* correctly carried as a deferred integration-manifest
  dependency; *slice ordering* (scan → #2b → #2a → fold → closeout) is right —
  the scan must precede the fold-the-rest slice.

**Anti-anchoring verdict:** honest. `appetite axis: gate-posture` is real (the
repo varies — `validate_rca_ledger` gates schema while the rate stays advisory;
test-economics is advisory-by-design), and `scope`/`timebox` as `single-point`
is accurate. Soft note carried into Boundaries: the brittleness-escape signal
was over-anchored to a parser that does not exist — which is exactly Blocker 1,
now resolved by the author-marker design.

## Off-Goal Findings

**Slice-1 candidate dispositions (slice 4):**

- **#2b cross-file sibling marker** → `applied` (slice 2, committed `69c2df9b`).
- **#2a RCA-ledger nudge** → `applied` (slice 3, committed `238fad72`).
- **`nose` 1951-dup-line interpretation** → slice 5 pilot + rollout issue
  (filed in slice 5, not here).
- **Standing test economics** (`test_file_count`=258, `nested_cli_file_count`=118,
  rising) → `watch, gate-tracked` by `inventory_standing_test_economics`
  (advisory-by-design, no fail path). Durable lever = shrink the release-only CLI
  lifecycle surface, an explicit Non-Goal here. No new issue: the advisory
  inventory IS the durable tracking (validator over prose ritual).
- **Coverage brush** (`check-coverage` 44.5s/44.8s vs 45.0s) → `watch,
  gate-tracked` by `check-runtime-budget` (PASS). No new issue.
- **`goal_artifact_closeout_evidence.py` python-lengths WARN** (348 in band
  `[330,360]`) → `watch, gate-tracked`. Pre-existing, exit-0 advisory, an
  `achieve`-skill script outside this goal's debug/quality-closeout scope; the
  `check-python-lengths` WARN self-tracks every run. No new issue.

**Cheap fold applied (slice 4):** my slice-3 change crossed `run_slice_closeout.py`
into the `[432,480]` python-lengths advisory warn band (433 code lines). Folded a
clean refactor — moved the `_rca_link_advisory_provider` wrapper into
`rca_link_advisory.provider` (better cohesion; the provider lives with the
advisory module) — pulling the file back under the band. 71/0 holds.

**Non-claim / goal-premise correction:** the goal's shaping text assumed the
`nose` binary is absent (a deferred integration-manifest dependency). The slice-1
scan found `nose` 0.5.0 present locally, so `inventory-nose-clones` is ACTIVE.
The shaped Goal/Non-Goals text is left as the historical contract; this is the
authoritative correction (also in `quality/latest.md` and the slice-1 log).

**No new GitHub issues filed in slice 4:** every remaining candidate is either
gate-tracked (existing advisory inventory/gate owns the memory) or
deferred-by-maintainer-judgment (#184). The advisory-interpretation rollout issue
belongs to slice 5.

**Slice 5 split → issue [#322](https://github.com/corca-ai/charness/issues/322):**
the cross-skill rollout of the advisory-interpretation contract to the remaining
inference-layer surfaces (ergonomics heuristics, test-economics trend,
lint-suppression pressure, length smell, recommendation rankings, runtime trend)
is split to #322 by design. Slice 5 landed the shared reference + the `nose`
pilot + one consumer requirement; #322 carries the rollout (promote to `spec` if
it grows). This is a clean split, not an early-stop.

**New open issue observed (out of scope, for the next session):**
[#321](https://github.com/corca-ai/charness/issues/321) "Mutation test regression
on main" (opened 2026-06-06, after the handoff). Not touched here — out of this
goal's scope; flagged for handoff at closeout.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-06-06-quality-scan-closeout-discipline.md
(session retro; recent-lessons + lesson-selection-index refreshed; one RCA event
appended — `capped-artifact-drafted-before-reading-limit`, source=retro,
converted, caught_by=gate).
Host log probe: skipped: not-applicable: cost/turn-count was not this goal's
question. Evidence is deterministic gate pass/fail (full `run-quality.sh` 72/0)
and three bounded fresh-eye review verdicts, not host-log efficiency metrics; no
`Host metric window:` line was set for this goal.
Disposition review: charness-artifacts/goals/2026-06-06-quality-scan-closeout-discipline.md
`## Off-Goal Findings` — every slice-1 scan candidate dispositioned (applied /
gate-tracked watch / split to #322 / maintainer-deferred #184); the slice-5
fresh-eye critique independently reviewed the splittable cut point.

## User Verification Instructions

1. **Quality posture:** read `charness-artifacts/quality/latest.md` — v0.24.1
   posture, 71/0 gates, the `nose`-now-active delta, and the prioritized candidate
   list. Archived prior pass at `history/2026-06-05-quality-review.md`.
2. **Green on the final state:** `./scripts/run-quality.sh --read-only` → 71/0
   (full `./scripts/run-quality.sh` → 72/0).
3. **#2b enforced:** in a scratch copy, delete the `cross-file:` line from
   `charness-artifacts/debug/latest.md`'s `## Sibling Search` and run
   `python3 scripts/validate_debug_artifact.py --repo-root .` — it FAILS with a
   `cross-file` error; restore it (or add `no cross-file sibling: <reason>`) and it
   PASSES. Or run `python3 -m pytest tests/test_debug_artifact.py -k cross_file`.
4. **#2a advisory:** `python3 scripts/rca_link_advisory.py --repo-root . --paths
   charness-artifacts/debug/2026-06-06-not-in-ledger.md` prints an `ADVISORY:` at
   exit 0; a path already `ref`'d in `rca-ledger.jsonl` is silent. Or
   `python3 -m pytest tests/test_rca_link_advisory.py`.
5. **Slice-5 pilot:** `python3 skills/public/quality/scripts/inventory_nose_clones.py
   --repo-root .` prints an `INTERPRETATION (...)` self-declaration line.
6. **Dispositions:** `## Off-Goal Findings` (above) and `## Auto-Retro` (below)
   show every surfaced improvement as `applied`, `issue #N`, or `gate-tracked
   watch` — no prose-only memory.

## Auto-Retro

Retro dispositions (every surfaced improvement has a disposition):

- #2b cross-file sibling marker → `applied` (slice 2, `69c2df9b`).
- #2a RCA-ledger nudge → `applied` (slice 3, `238fad72`).
- `nose` 1951-dup interpretation → `applied` as the slice-5 pilot (`78da39d7`);
  cross-skill rollout → `issue #322`.
- Standing test economics → `gate-tracked watch` (`inventory_standing_test_economics`,
  advisory-by-design; lever out of scope).
- Coverage brush → `gate-tracked watch` (`check-runtime-budget` PASS).
- `goal_artifact_closeout_evidence.py` python-lengths WARN → `gate-tracked watch`
  (pre-existing, out of scope; `check-python-lengths` self-tracks).
- `run_slice_closeout.py` length creep (introduced in slice 3) → `applied` fold
  (slice 4 refactor, `c97bde77`).
- Retro lesson (capped-artifact-drafted-before-reading-limit) → `applied` to
  `recent-lessons.md` + one RCA event; no new issue (habit + validators enforce).
- #321 (mutation regression, newly open) → `out of scope`, flagged for handoff.
- #184 (product metrics) → `deferred, maintainer judgment` (Non-Goal).

No prose-only memory: each item is a commit, an issue, or a gate that self-tracks.
