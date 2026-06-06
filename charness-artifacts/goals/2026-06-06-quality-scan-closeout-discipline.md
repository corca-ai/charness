# Achieve Goal: Repo quality scan + closeout-discipline gates

Status: draft
Created: 2026-06-06
Activation: `/goal @charness-artifacts/goals/2026-06-06-quality-scan-closeout-discipline.md`
Timebox: 3h
Activation time: set at /goal activation (record the ISO start timestamp then)
Closeout reserve: 20m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation (draft).
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-06-quality-scan-closeout-discipline.md`.
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
| 1 | Quality posture scan (`find-skills` → `quality`) | Handoff Next Session #1 planned focus; surfaces the improvement candidates that scope slices 2–4 | Refreshed `quality/latest.md`; `run-quality.sh --read-only` PASS; bounded fresh-eye review; prioritized candidate list (incl. `nose` advisory) | planned |
| 2 | #2b sibling-scan marker enforcement in the `validate_debug_artifact.py` `latest.md` branch (+ reference doc) | Diagnosed in the #320 slice; the reference's cross-file requirement is unenforced (shape-only) | Marker check added to the `latest.md` branch only; fails a `latest.md`-form `## Sibling Search` missing the `cross-file:` / `no cross-file sibling:` marker, passes one with it; 59 dated artifacts stay green; `sibling-search.md` updated; mirrors synced; fresh-eye critique CLEAR | planned |
| 3 | #2a advisory RCA-ledger nudge (exit-0, in the slice-closeout aggregate) | Diagnosed in the #320 slice; prompt-only append is deliberately non-gated, so add advisory detection of unlinked debug artifacts | Nudge warns at exit 0 for a new debug artifact with no matching ledger `ref`, silent when a `ref` exists; wired into `run_slice_closeout.py --predict-commit` as an advisory line (not a standalone promotable gate); no fail path | planned |
| 4 | Fold cheap scan wins / file the rest | Keep the goal honest: apply only obviously-correct cheap improvements, route the rest to issues | Applied diffs or `issue #N` references for each candidate; watch-item carry-forward recorded | planned |
| 5 | Advisory epistemic-status + agent-interpretation contract (first cut, **splittable**) | Generalizes the #2b judgment-over-automation principle; the goal already touches advisory surfaces (scan, nose, RCA nudge) so it is the natural pilot home | Shared reference written (inference-layer self-declaration + required consumer interpretation; explicit "not verifiable facts", no blanket banner); applied to one pilot surface (`quality` advisory and/or `nose`); fresh-eye critique CLEAR; rollout `issue #N` filed (+ `spec` if it grows); split/cut point recorded in Off-Goal Findings | planned |
| 6 | Closeout | Bundle proof + reflection within the closeout reserve | Full `./scripts/run-quality.sh` PASS; `retro`; every improvement dispositioned; Final Verification + non-claims written | planned |

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

## Slice Log

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

_(None yet — record issue references and reasons here during the run.)_

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

_(Filled at closeout — see User Acceptance for the planned shape: read the
refreshed quality posture, run the read-only gate, exercise the #2b fixture and
#2a nudge, and confirm each improvement is dispositioned.)_

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
