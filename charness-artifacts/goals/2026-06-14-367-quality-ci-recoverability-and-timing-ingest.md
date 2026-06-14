# Achieve Goal: Resolve #367 — quality CI-recoverability triage lens + command-timing-log ingest

Status: active
Created: 2026-06-14
Activation: `/goal @charness-artifacts/goals/2026-06-14-367-quality-ci-recoverability-and-timing-ingest.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Mode: implementation-continuation (execute slices once activated). The prose
"쭉 처리" (process straight through) settles the mode; this is not an
artifact-only draft.

## Active Operating Frame

- Current slice: Slices 1–3 complete (timing-log ingest, CI-recoverability lens,
  docs/surface/dogfood + slice-1 review follow-ups), all committed + locally
  proven. Next: Slice 4 (bundle closeout).
- Current slice intent: Slice 4 — refresh the stale handoff, run the bundle broad
  proof (verification-lock), final fresh-eye + disposition review, then push with
  `Close #367` and run `release`. This is the single approved external lane.
- Next action: commit slice 3, then run the bundle fresh-eye review + broad proof
  before the push/close/release lane.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Resolve open GitHub issue #367 by closing its two portable gaps in the `quality`
skill, end-to-end (implement → local proof → push + `Close #367` → release):

1. **CI-recoverability triage lens.** Add a lens that cross-references each costly
   local *standing gate* against the repo's CI workflow steps and flags
   "CI fully re-runs this proof → candidate to move off the local hot path,"
   ranked by measured local wall-clock. It is an explicit counterweight to the
   existing local-proof guardrail (`inventory_ci_local_gate_parity.py`), not a
   replacement: it must never recommend moving proof CI does *not* re-run.
2. **Command-timing-log ingest.** Let `render_runtime_summary` /
   `runtime_budget_profiles` ingest a repo-declared command-timing log via a new
   adapter key (a log path + a field/schema mapping) as a sample source, so a
   repo's existing structured timing log lights up gate hot spots without each
   repo hand-rolling a log→`runtime-signals.json` bridge.

Also refresh the stale `docs/handoff.md` (it still names v0.45.0 and closed
#362/#361 while live state is v0.49.0).

## Non-Goals

- Not weakening or replacing the existing `inventory_ci_local_gate_parity.py`
  local-proof guardrail. The new lens is additive and explicitly gated to the
  opposite direction (CI-recoverable local gates), so the "required proof must be
  reachable locally" discipline stays intact.
- Not auto-moving any gate off the local hot path. Both surfaces are advisory
  inventory / summary output — the operator decides; no gate edits are applied.
- Not recommending that any proof CI does *not* fully re-run be moved. That gate
  is the whole safety point of the lens.
- Not building a stack-specific timing-log parser. The ingest is schema-mapped
  through adapter keys (portable) and **inert when the key is absent**, mirroring
  the inert-by-default pattern of `standing_doc_provenance` /
  `changed_line_mutation_gate`.
- Not adding any new blocking gate or floor (Floor-Addition Restraint). Both
  surfaces are advisory; no pass/fail gate is introduced.
- Release scope is a version bump that ships these `quality`-skill changes only —
  not a bundle of unrelated work.

## Boundaries

- External side-effect scope: the single approved external lane is the **final
  bundle** — push to `main` with `Close #367` and then a `release` version bump.
  That approval (operator-selected: push + close + release) is scoped to the
  closeout bundle; per-slice work before it is **local by default** (commit
  locally, run cheap gates, defer the single push + remote CI to the bundle
  boundary).
- Work directly on `main`, one commit per coherent slice (the repo's established
  direct-to-main pattern); push once at the bundle boundary, not per slice.
- Both new surfaces are advisory/inventory (no blocking floor), per
  Floor-Addition Restraint.
- The timing-log ingest is **inert when its adapter key is absent** (stack-neutral
  opt-in); a misconfigured key fails loud as a config error, never silently.
- The CI-recoverability lens only flags a local gate when a CI step **fully
  re-runs that gate's proof**; partial / non-matching CI coverage never produces a
  "move off local" recommendation.
- Generated/plugin mirror discipline: repo-root `scripts/*.py` and
  `skills/public/quality/**` changes must be mirrored into `plugins/charness/**`
  via `sync_root_plugin_manifests.py` *before* the commit gate
  (`staged-plugin-mirror-drift` is a hard pre-commit gate).

Discuss before activation: RESOLVED — the consequential outward boundary
(push to `main` + close #367 + cut a consumer release) was raised to the operator
and explicitly chosen as "Push + close + release" (fullest end-to-end). No split,
standalone goal, direct-commit carrier. No remaining unresolved consequential
decision blocks activation.

## User Acceptance

What the user can do to verify completion directly:

- Run the new CI-recoverability triage (the documented command) on this repo and
  see it either flag local standing gates whose proof CI fully re-runs (ranked by
  wall-clock) or correctly report none — and confirm it never flags a gate CI does
  not re-run.
- Point a `command_timing_log` adapter key at a JSONL timing log (a fixture or a
  real one) and run `render_runtime_summary.py`; confirm it reports hot spots from
  that log instead of "no samples," and that omitting the key leaves behavior
  unchanged.
- `gh issue view 367` shows `CLOSED`.
- The release surface (`charness-artifacts/release/latest.md` + tag) shows the new
  version shipping these changes, and the maintainer install refreshed.

## Agent Verification Plan

### Low-Cost Checks

- `ruff` + `check_python_lengths` on changed Python.
- Targeted `pytest` for the new libs/scripts (timing-log ingest + CI-recoverability
  lens) — TDD where practical.
- `sync_root_plugin_manifests.py` before each commit that touches exported
  `scripts/*.py` or `skills/public/quality/**`.
- `run_slice_closeout.py --skip-broad-pytest` at commit boundaries (the pre-commit
  gate aggregate, not the unit suite alone).

### High-Confidence Checks

- Full broad proof at the bundle boundary: `scripts/run-quality.sh` (or
  `run_slice_closeout.py --verification-lock`) — broad pytest + coverage + skill
  validation + markdown/doc-link gates.
- Dogfood: run the new lens and the timing-log ingest on this repo and record the
  observed output.
- Fresh-eye subagent critique per substantial slice (mandatory cadence): hand a
  bounded slice packet (intent, changed files, invariants, proof, non-claims,
  out-of-scope, questions).

### External Or Live Proof

- Push to `main` → CI (`.github/workflows/quality-core.yml`) green on the pushed
  SHA.
- `gh issue view 367` verified `CLOSED` after the `Close #367` carrier lands.
- `release` skill: version bump committed, tag published, release verification
  recorded, install refresh confirmed.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Command-timing-log ingest (adapter key) | Foundation: produces the real per-gate wall-clock the lens ranks by; most self-contained | New `command_timing_log` adapter field parsed into the runtime `commands` shape; `render_runtime_summary` reads it as a sample source; unit tests; inert when unconfigured; mirror synced | planned |
| 2 | CI-recoverability triage lens | The core #367 ask; consumes the ranking + CI-step matching | New inventory script + lib cross-referencing standing gates vs CI steps, flagging CI-fully-rerun gates ranked by wall-clock, gated against non-recoverable proof; unit tests; mirror synced | planned |
| 3 | Surface + docs + dogfood | Make both default `quality` output and document them; dogfood on this repo | SKILL.md + adapter-contract + references updated; this repo's adapter optionally wired; quality run shows the lens; skill validation green | planned |
| 4 | Closeout: handoff refresh + push + close + release | Full end-to-end per operator choice | Handoff refreshed to live state; broad proof green; `Close #367` pushed; #367 `CLOSED`; release cut + verified; retro + disposition review | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary.

- **Routing** — session-start `find-skills` `--recommend-for-task` returned
  `issue` (via the `github-gh` external binary) for #367 and `achieve` as the
  goal operator. Per-phase: `impl` for slices 1–2 (code), `quality` for the
  verification posture and the closeout broad gate, `issue` for the #367
  direct-commit closeout, `release` for the version bump, `handoff` for the
  handoff refresh. Each route confirmed against `find-skills` during the run and
  recorded here.
- **Gather step** — `Gather: n/a — issue #367 is read through the gh GitHub
  backend (gh issue view), not an external web/Slack/Notion/Docs/Drive source, so
  no gather asset applies.`
- **Release step** — Release: (filled at closeout — the `release` skill proof:
  version bump commit, tag, `charness-artifacts/release/latest.md`).
- **Issue closeout step** — Issue closeout: #367 via `direct-commit` carrier
  (`Close #367` on the fix/closeout commit), validated with
  `issue_tool.py validate-closeout-draft --carrier direct-commit
  --commit-message-file`, and verified `CLOSED` with `verify-closeout` after the
  push.

## Slice Log

### Slice 1: Command-timing-log ingest (adapter key)

- Objective: Let render_runtime_summary / check_runtime_budget ingest a repo-declared command-timing log via a new portable command_timing_log adapter key (path + field/schema mapping), as a sample source when runtime-signals.json has no samples; inert when unconfigured, fail-loud on misconfig. Files: NEW skills/public/quality/scripts/runtime_timing_log_lib.py; edited runtime_budget_lib.py (timing-log fallback + commands_source/timing_log report fields), render_runtime_summary.py (source line + json fields), adapter_validators.py (command_timing_log passthrough validator), scripts/quality_adapter_lib.py (default {} + _apply_runtime_fields helper). Mirror synced to plugins/charness.
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 16 new unit+integration tests pass (tests/quality_gates/test_runtime_timing_log_ingest.py); existing runtime-budget tests green after one intentional message-wording update; ruff + check_python_lengths clean; adapter resolves command_timing_log:{} valid:true.
- Test duplication pressure: added 1 new test file (16 cases); nose-clone inventory sample: 0 findings; no broad duplicate-pressure gate pushed toward threshold.
- Critique: Skill-review decision (public-skill change): additive + inert-by-default (behavior unchanged when key absent; only altered user string is the 'not configured' hint, now naming the new key); existing docs/public-skill-dogfood.json quality case acceptance evidence stays satisfied; richer acceptance-evidence update deferred to slice 3 (docs). Cautilus run_mode=ask, next_action=none -> no evaluator run per repo policy; --ack-cautilus-skill-review used for the slice-boundary aggregate.
- Off-goal findings:
- Lessons carried forward: Slice 2 will consume render_runtime_summary's commands_source/hot-spot ranking for the CI-recoverability lens; reuse evaluate_timing_log output as the wall-clock source. Keep _apply_policy_fields complexity in mind when wiring further adapter keys.
- Metrics:

### Slice 2: CI-recoverability triage lens

- Objective: Add the explicit counterweight to the local-proof guardrail: a lens that cross-references each cost-ranked local standing gate (wall-clock from slice-1 runtime ranking) against CI run-step commands, flags CI-fully-rerun gates as candidates to move off the local hot path (ranked by wall-clock), and never flags a gate CI does not re-run (keep-local). Files: NEW ci_recoverable_gates_lib.py (pure classify + word-boundary label/CI token match, gate-policy aware, advisory-interpretation contract) and inventory_ci_recoverable_gates.py (CLI, advisory-only, reuses ci_local_gate_parity_lib workflow discovery + runtime_budget_lib ranking).
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: 11 new tests pass (tests/quality_gates/test_ci_recoverable_gates.py); ruff + check_python_lengths clean. Dogfood on this repo: 21 cost-ranked gates -> check-markdown (4.6s) flagged candidate (re-run by quality-core.yml local-gate-subset-mirror); check-coverage (46s)/pytest (22s)/specdown (3.6s) correctly keep-local. False-negatives (unmeasured gates absent) are the safe direction.
- Test duplication pressure: added 1 new test file (11 cases); pure-function unit tests + 2 CLI integration tests; no broad duplicate-pressure gate pushed toward threshold.
- Critique: Same public-skill-change skill-review decision as slice 1 (additive advisory lens, no blocking floor, Floor-Addition Restraint honored). Matching heuristic is token-identity with declared blind spots (cannot prove proof equivalence / if-gated CI steps); advisory-only, operator confirms. Gate against false positives: word boundaries + >=4-char stems + generic-word stoplist; verified node!=node-version.
- Off-goal findings:
- Lessons carried forward: Lens scope is the cost-ranked (measured) gate set by design ('costly standing gate'); gates without cost signals are out of scope and absent, which is the safe under-flagging direction. Slice 3 documents both surfaces in SKILL.md + adapter-contract and updates the dogfood acceptance evidence.
- Metrics:

### Slice 3: Surface + docs + dogfood + slice-1 review follow-ups

- Objective: Document both surfaces and fold the slice-1 fresh-eye review follow-ups. SKILL.md (200/200 lines): render bullet + runtime-review bullet name command_timing_log and inventory_ci_recoverable_gates.py; local-proof guardrail names the bounded counterweight. NEW references/ci-recoverable-gate-triage.md. adapter-contract.md + adapter.example.yaml document command_timing_log fields. public-skill-dogfood: EVIDENCE_OVERRIDES[quality] (scaffold source) + json get 2 new acceptance lines naming the gate-speed behaviors; observed_evidence records the change; reviewed_on bumped. Slice-1 follow-ups: recent_window surfaced in report; soft/loud docstring boundary clarified (dropped, not 'skipped'); +3 tests (json malformed soft, field_map non-mapping, recent_window).
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Full slice closeout aggregate (--skip-broad-pytest --ack-cautilus-skill-review): Closeout status completed, all structural-sweep + verify gates PASS (validate_skills, validate_public_skill_dogfood, attention-state, check-markdown, doc-links). 55 targeted tests pass. SKILL.md exactly 200 lines (validate_skills concise gate).
- Test duplication pressure: added 3 tests to existing timing-log test file (now 19 cases); no new test file; no broad duplicate-pressure gate pushed toward threshold.
- Critique: Public-skill validation review done as the dogfood-contract freeze: acceptance_evidence is scaffold-pinned, so the new expected behaviors were added to the canonical EVIDENCE_OVERRIDES source (not just the json) and regenerated to match — the validator confirms no drift. Cautilus skill-review acked (run_mode ask, next_action none). Two attention-state false-positives resolved: declared the lens advisory-only state; reworded 'skipped'->'dropped' for internal record-filtering (not a closeout state).
- Off-goal findings:
- Lessons carried forward: Slice 4: refresh stale handoff, run the bundle broad proof (run-quality / verification-lock), final fresh-eye + disposition review, then push with Close #367 and run release. Watch the 200-line SKILL.md ceiling: append to existing soft-wrapped bullets (0 physical lines) rather than adding new bullets.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- GitHub issue #367 (read via `gh issue view 367`) — the originating request:
  the two portable gaps in `quality`.
- `docs/handoff.md` — stale (names v0.45.0 / closed #362/#361); the handoff-hygiene
  sub-task.
- `charness-artifacts/retro/recent-lessons.md` — repeat traps: mirror-drift gate,
  in-process gate cross-checks, premature-close process cost.
- `skills/public/quality/SKILL.md` and references (`adapter-contract.md`,
  `inventory-dispatch.md`, `automation-promotion.md`) — the skill contract.
- `skills/public/quality/scripts/`: `ci_local_gate_parity_lib.py` (the existing
  local-proof guardrail to counterweight), `standing_gate_discovery_lib.py` /
  `standing_gate_verbosity_lib.py` (local standing-gate discovery),
  `runtime_budget_lib.py` / `runtime_profile_lib.py` / `render_runtime_summary.py`
  (runtime cost ranking + the fixed `runtime-signals.json` source).
- `.agents/quality-adapter.yaml` — this repo's adapter (where a `command_timing_log`
  key would land).
- `.github/workflows/quality-core.yml`, `.github/workflows/mutation-tests.yml` —
  the CI steps the lens cross-references.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- **Run mode** — family {artifact-only draft, implementation-continuation}.
  Chosen: implementation-continuation. Rejected artifact-only because the prose
  "쭉 처리" (process straight through) is an explicit execution directive.
  `axis: single-point` — run mode is a per-invocation operator intent, not a
  system axis the harness varies on.
- **Closeout boundary** — family {local-only (maintainer pushes),
  push + close #367, push + close + release}. Chosen: push + close + release
  (operator-selected). Rejected the narrower options because the operator
  explicitly asked for the fullest end-to-end. `axis: single-point` — this repo
  direct-commits to `main` and its plugin install mirrors from `main`; the close
  carrier and release flow are fixed for this repo, not a multi-host axis for this
  goal.
- **Slice ordering (timing-ingest before triage-lens)** — family {lens first,
  ingest first}. Chosen: ingest first. Rejected lens-first because the lens ranks
  by measured wall-clock that the ingest provides; building the data source first
  de-risks the lens. `single-point: ordering is a within-goal sequencing decision,
  not a system axis.`

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance.

- **Blocker folded → Non-Goals + the lens gate:** a CI-recoverability lens could
  erode the local-proof guardrail if it recommended moving proof CI does not
  re-run. Folded: the lens only fires when a CI step *fully* re-runs the gate's
  proof; it is additive and never edits gates.
- **Blocker folded → Boundaries:** a timing-log ingest could become a
  stack-specific parser. Folded: schema-mapped adapter key, inert when absent,
  config-error-loud when misconfigured.
- **Blocker folded → Boundaries:** exported `scripts/*.py` /
  `skills/public/quality/**` must be mirrored to `plugins/charness/**` before the
  commit gate (recent-lessons repeat trap). Folded into the per-commit cadence.
- **Over-worry raised, not folded:** "should the lens auto-apply the move?" — no;
  advisory only keeps the operator in the loop and avoids a risky autonomous gate
  edit. Recorded in Non-Goals.
- **Reviewer provenance:** Before-phase inline self-critique (this session). The
  mandatory fresh-eye subagent critique runs per substantial slice during the
  During phase (cadence owned by `meaningful-slice-cadence`), and a final
  cross-slice + disposition review at closeout.

## Off-Goal Findings

(none yet)

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

(filled at closeout)

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
