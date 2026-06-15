# Achieve Goal: Nose findings, issues 371-373, and test runtime reduction

Status: active
Created: 2026-06-15
Activation: `/goal @charness-artifacts/goals/2026-06-15-nose-issues-371-373-test-runtime.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

Discuss before activation: resolved by goal contract — tracked issues #371,
#372, and #373 are close-intended, but #371 may only close with teardown proof
for the browser process tree/profile lifecycle; an age-based reaper or advisory
alone is a mitigation, not closure. If direct teardown is outside this repo's
control, split/file the upstream/host gap and record the non-closure honestly.

## Active Operating Frame

- Current slice: 5 - fix selected nose 0.10.0 clone findings.
- Current slice intent: reduce the highest-value clone families that are
  genuinely extractable without weakening portability or broadening unrelated
  behavior.
- Next action: refresh the nose 0.10.0 inventory, pick the smallest
  high-confidence family, and record before/after duplicate evidence.
- Verification cadence: cheap deterministic checks at commit boundaries;
  focused tests and fresh-eye critique at slice boundaries; broad pytest and
  closeout gates only at bundle/final proof unless a slice changes shared test
  infrastructure.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Finish the three requested workstreams in the order that lowers total run cost:

1. aggressively measure and reduce local test/validation runtime;
2. resolve GitHub issues #373, #372, and #371 with issue-grade proof;
3. fix the newly surfaced nose 0.10.0 clone findings that are genuinely
   extractable and worth the blast radius.

The goal is successful only if it leaves measurable before/after runtime
evidence, closes or honestly dispositions #371-#373, and records which nose
families were fixed versus deliberately left as boilerplate or separate design
work.

## Non-Goals

- Do not chase every nose family. Bootstrap/import shim and per-skill portability
  boilerplate remains out of scope unless a small shared helper clearly reduces
  real maintenance cost without weakening portability.
- Do not weaken local proof by moving gates off local unless the quality
  CI-recoverability lens proves CI fully reruns that gate.
- Do not close #371 with only a periodic orphan reaper, stale-dir cleanup, or a
  doctor warning. Those may be supporting mitigations, but closure requires
  lifecycle teardown proof or an explicit split to the owning layer.
- Do not publish, push, or close GitHub issues through remote side effects until
  the relevant slice has local proof and the issue closeout draft validates.
- Do not claim broad runtime improvement from anecdotal elapsed time. Use
  structured command timing, quality runtime summaries, or repeated comparable
  before/after command runs.

## Boundaries

- External side-effect scope: GitHub issue closure is planned for #371, #372,
  and #373 only after local implementation proof plus issue closeout validation.
  Any push/PR/remote-CI approval is phase-scoped and does not carry forward.
- Runtime-speed work may delete, merge, demote, or reclassify stale tests/gates
  only when the deleted coverage is provably redundant, stale, or CI-backed; it
  must not silently lower the quality bar.
- Bug-class issue work (#371, #372, #373 if classified bug) starts with a debug
  root-cause note or a compact causal review before implementation.
- Charness source and checked-in plugin/export mirrors must stay synchronized
  before verification.
- Historical artifacts may keep old `gws-cli` or prior timing mentions; current
  operator/source surfaces must not be updated unless the slice touches them.

## User Acceptance

The user can verify completion by checking:

- `gh issue view 371/372/373` shows closed or, for #371 only if needed, a
  recorded split/follow-up with an explicit reason why this repo cannot own the
  final teardown.
- `charness-artifacts/quality/latest.md` or a goal-linked runtime artifact shows
  before/after wall-clock data and the chosen reductions.
- `python3 skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`
  shows the targeted clone families removed, reduced, or explicitly dispositioned.
- Final closeout lists commands run, broad proof/non-claims, and residual risks.

## Agent Verification Plan

### Low-Cost Checks

- `git status --short --branch`
- `python3 scripts/check_changed_surfaces.py --repo-root .`
- `python3 scripts/validate_integrations.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- focused pytest for the touched slice
- `python3 scripts/check_staged_reversion.py --repo-root .`
- `python3 scripts/check_staged_mirror_drift.py --repo-root .`

### High-Confidence Checks

- Quality timing: run or ingest `command_timing_log`, then run
  `render_runtime_summary.py`, `check_runtime_budget.py`, and
  `inventory_ci_recoverable_gates.py`.
- Test/runtime proof: comparable before/after broad pytest or run-quality timing
  over the same machine/profile; include repeated samples when feasible.
- Nose proof: inventory nose clone families before and after targeted refactors.
- Issue proof: issue closeout draft/verify tooling for #371-#373.
- Final repo proof: broad pytest plus repo closeout gates named by
  `check_changed_surfaces.py`.

### External Or Live Proof

- #371 needs a live or controlled local process-lifecycle proof: invoke the
  agent-browser path, end/abort the invocation or equivalent session, then prove
  the process tree and `agent-browser-chrome-*` profile dir are torn down or
  explicitly bounded. If only a mitigation is possible, do not call it full
  closure.
- GitHub issue closeout is external proof and must be phase-scoped.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Activation inventory and baselines | Establish exact starting state before optimizing or closing issues | current issue snapshots; nose 0.10.0 inventory; timing baseline; changed-surface map | completed |
| 1 | Reduce validation/test runtime first | Every later slice pays verification cost; speed wins compound | runtime summary; CI-recoverable triage; removed/merged/demoted stale tests or justified no-op; before/after timing | completed |
| 2 | Resolve #373 producer-before-validator regressions | It affects `achieve` itself and prevents repeated scaffold/validator waste during this goal | producer-first invariant; tests scanning scaffold/check order; issue closeout proof | completed |
| 3 | Resolve #372 disconfirmer-first debug rule | This improves the causal discipline needed before #371's runtime bug work | debug reference update; tests/dogfood/gate if appropriate; issue closeout proof | completed |
| 4 | Resolve #371 agent-browser orphan lifecycle | Highest operational-risk issue, but benefits from #372's diagnosis rule and faster gates | root-cause note; teardown implementation or honest split; live/local lifecycle proof; issue closeout proof | completed |
| 5 | Fix selected nose 0.10.0 clone findings | Broadest refactor blast radius; safer after speed and issue-critical work | before/after nose inventory; targeted helper extraction; focused + broad proof; disposition of left-behind families | pending |
| 6 | Bundle closeout | Prove the whole goal and record non-claims | broad pytest; closeout gates; critique; retro; issue states; final verification | pending |

## Coordination Cues

Phase-appropriate routing for this run is deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine), not hard-coded here.

- Routing: initial recommendation probe selected `quality` for runtime/nose
  work, `issue` via `github-gh` for #371-#373, and `achieve` as the goal
  operator.
- Gather: n/a — GitHub issues were read through `gh issue view`; no separate
  external document needs local gather before activation.
- Release: n/a — no version bump or release surface is planned.
- Issue closeout: close-intended #371, #372, #373; carrier to be chosen during
  implementation (`direct-commit`, PR body, or manual fallback) and verified via
  issue closeout tooling before final completion.

## Slice Log

### Slice 1: Activation inventory and runtime hot-spot reduction

- Objective: Capture live baseline evidence, restore inherited baseline failures to green, and reduce one standing validation hot spot without weakening source-owned proof.
- Why this approach: Runtime reduction first lowers every later slice's proof cost; current-pointer scanning was a measured 15.2s hot spot caused by duplicate parsing of generated plugin mirrors.
- Commits: `e7912196 quality: reduce current-pointer scan runtime`.
- What changed: Recorded issue states #371/#372/#373 as open; captured nose 0.10.0 inventory at 20 shown families / 2036 duplicated lines / 559 total ranked families; updated the current-pointer scanner to scan source-owned roots only; added a generated-plugin mirror skip regression; restored specdown and coverage baseline failures; synced plugin mirrors; recorded attention-state declaration for skipped healthcheck coverage.
- Alternatives rejected: Rejected moving coverage, pytest, duplicates, or test-completeness off local because the CI-recoverability lens kept those gates local; rejected broad current-pointer taint analysis as an existing deferred design question, not needed for this runtime slice.
- Targeted verification: Before: run-quality-read-only failed in 73.6s with check-coverage and specdown failures; check-current-pointer-writes latest sample was 15.2s. After: final ./scripts/run-quality.sh --read-only passed 78 phases in 65.7s; check-current-pointer-writes passed in 7.826s standalone and 7.8s in the final gate; python3 scripts/check_coverage.py --repo-root . --json passed; specdown run -quiet -no-report passed; pytest focused checks passed (17 current-pointer tests, 2 tool lifecycle/update tests, 3 prior failure nodes); validate_attention_state_visibility passed for 82 files.
- Test duplication pressure: Added one current-pointer scanner regression test; nose inventory remained 20 shown families / 2036 duplicated lines in reported families; no broad duplicate-pressure gate claim beyond the final read-only quality run.
- Critique: Fresh-eye critique recorded at charness-artifacts/critique/2026-06-15-slice-0-runtime-baseline-and-current-pointer-scanner-reduction.md; Act Before Ship was artifact honesty only and is folded here; no blocking code defect found. Public-skill review decision: `python3 scripts/suggest_public_skill_dogfood.py --repo-root . --skill-id quality --json` returned the existing quality dogfood case as `hitl-recommended`; this slice did not change quality routing semantics, only the attention-state declaration for an already-visible skipped healthcheck state. The one-shot skill-surface preflight advisory was attempted, but `check_skill_surface_preflight.py` rejected `skills/public/quality/references/attention-state-visibility.json` because it only accepts `SKILL.md` or `references/*.md`, so the applicable deterministic checks are the attention-state validator, dogfood validator, and slice closeout acknowledgment.
- Off-goal findings: Specdown lock historical healthcheck data may be stale but is deferred unless a validator treats it as live truth; full issue #371-#373 closure remains planned for later slices.
- Lessons carried forward: For runtime claims, cite explicit samples when rolling medians still include pre-change data; generated mirrors should usually be protected by source scan plus packaging/mirror validation rather than duplicate semantic scans.
- Metrics: runtime profile local-linux-x86_64-36cpu; aggregate read-only quality 73.6s failed -> 65.7s passed; current-pointer scanner 15.2s -> 7.8s.

### Slice 2: Issue #373 producer-before-validator ordering

- Objective: Resolve #373 by ensuring public artifact-producing skill bootstraps show producers/scaffolds before validators/readiness checks, and by adding a regression gate over that instruction surface.
- Why this approach: The issue was an operator-instruction regression, not a runtime helper bug; the smallest durable prevention is a source-skill wording fix plus a quality-gate test over the public bootstrap examples.
- Commits: this slice commit (`fix(achieve): enforce scaffold before goal validation`).
- What changed: `achieve` now runs `upsert_goal.py` before `check_goal_artifact.py` in Bootstrap and explicitly describes `check_goal_artifact.py` as a post-scaffold gate; plugin mirror synced; added `tests/quality_gates/test_artifact_producer_order.py`; recorded debug, seam-risk index, critique, and issue closeout artifacts.
- Alternatives rejected: Deferred deriving producer/validator pairs from `scripts/check_artifact_surface_preflight.py` because an explicit table covers the #373 close boundary; rejected scaffold-output roundtrip testing for every producer because the reported failure is command ordering in public instructions.
- Targeted verification: `pytest -q tests/quality_gates/test_artifact_producer_order.py tests/quality_gates/test_goal_artifact_producers.py` passed; `validate_skills`, packaging, docs/markdown/secrets, deterministic prompt-proof validation, public-skill validation/dogfood, debug artifact/index validation, critique artifact validation, integration validation, ruff, Python lengths, attention visibility, test-repo-copy invariants, and boundary-bypass ratchet passed locally.
- Test duplication pressure: Added one table-driven quality-gate test covering known public producer/validator pairs, including the `hitl` same-script sync-vs-`--check` mode pair found by fresh-eye critique.
- Critique: Causal review accepted the bug classification and invariant proof; resolution critique initially found a blocking `hitl` coverage hole, which was fixed before commit. Artifact: `charness-artifacts/critique/2026-06-15-issue-373-producer-before-validator-resolution.md`. Public-skill dogfood decision: `suggest_public_skill_dogfood.py --skill-id achieve --json` and slice closeout both returned the existing `achieve` case as `hitl-recommended`; the fresh-eye review and unchanged dogfood registry are the scenario review for this slice.
- Off-goal findings: Auto-deriving the ordering table from an owning registry could reduce future drift, but is deferred outside this slice.
- Lessons carried forward: Same-script producer/check modes need command-token coverage, not filename-only checks; validator commands belong in post-scaffold/post-shape language unless they explicitly advertise a non-mutating discovery mode.

### Slice 3: Issue #372 disconfirmer-first debug rule

- Objective: Resolve #372 by adding a debug workflow rung that requires absence, attribution, liveness, and frequency claims to run their cheapest falsifier before being treated as confirmed.
- Why this approach: The issue names a diagnosis-contract gap, so the durable home is a debug reference plus the issue causal-review substrate that consumes debug during bug-class issue resolution.
- Commits: this slice commit (`fix(debug): require disconfirmers before diagnosis claims`).
- What changed: Added `skills/public/debug/references/disconfirmer-first.md`; linked it from `skills/public/debug/SKILL.md`; added the same substrate to `skills/public/issue/references/causal-review.md`; synced plugin mirrors; expanded `tests/quality_gates/test_debug_rca_reference_cite_chain.py`; recorded debug, critique, seam-risk index, and issue closeout artifacts.
- Alternatives rejected: Rejected broad public-skill adoption in this slice because issue causal review already consumes debug substrate for bug-class RCA; rejected evaluator work for falsifier quality because the rule is now explicit and auditable, while live choice quality is broader future work.
- Targeted verification: `pytest -q tests/quality_gates/test_debug_rca_reference_cite_chain.py` passed; debug artifact/index and critique artifact validators passed; skill/package/docs/markdown/secrets/deterministic prompt-proof/public-skill validation gates passed locally; public-skill dogfood registry validates after scenario-review notes for `debug` and `issue`.
- Test duplication pressure: Added focused assertions to an existing debug-reference suite rather than a new parallel test file.
- Critique: Causal review accepted the bug classification and invariant proof; resolution critique found an Act Before Ship gap in issue causal-review substrate cites, fixed before commit. Artifact: `charness-artifacts/critique/2026-06-15-issue-372-disconfirmer-first-resolution.md`. Public-skill dogfood decision: `suggest_public_skill_dogfood.py --skill-id debug --json` and `--skill-id issue --json` returned `evaluator-required`; scenario-registry review inspected `evals/cautilus/scenarios.json` and kept existing `debug-adapter-bootstrap`, `issue-sibling-search-concept-fixtures`, and `representative-skill-contracts` unchanged because routing/bootstrap behavior did not change. The scenario review is recorded in `docs/public-skill-dogfood.json`; `validate_cautilus_proof.py` reported deterministic validation owns this closeout because no live proof artifact changed and no log-backed behavior proof was requested.
- Off-goal findings: Stronger evaluator coverage for the quality of selected falsifiers is valid future work but outside this slice.
- Lessons carried forward: If a rule is placed in debug substrate, bug-class issue causal review must cite it explicitly or recurrence can bypass the new diagnosis guard.

### Slice 4: Issue #371 agent-browser lifecycle split

- Objective: Resolve or honestly disposition #371 without treating post-hoc runtime cleanup as invocation-bound process/profile teardown.
- Why this approach: #371 requires proof that normal completion, cancellation, provider failure, and timeout tear down both the browser process tree and `agent-browser-chrome-*` profile directory. Charness owns only downstream runtime drift detection and owned orphan daemon-tree cleanup after residue already exists; the upstream `agent-browser` daemon/profile lifecycle is not locally owned.
- Commits: this slice commit (`issue: record agent-browser lifecycle upstream split`).
- What changed: Added a debug artifact and issue split draft documenting the non-closure; updated the agent-browser integration manifest and checked-in plugin mirror to state that invocation-bound Chrome process/profile teardown is upstream lifecycle ownership and Charness' guard is downstream drift detection/owned orphan daemon-tree cleanup; refreshed the debug seam-risk index; recorded fresh-eye critique.
- Alternatives rejected: Rejected expanding the local runtime guard into a broader reaper because it would still run after residue exists and would not prove invocation-end profile/process teardown. Rejected closing #371 because no controlled teardown proof exists.
- Targeted verification: `gh issue view 371 --repo corca-ai/charness` confirmed the local issue is open and asks for lifecycle teardown; `gh issue view 1334/1401/1371 --repo vercel-labs/agent-browser` confirmed open upstream coverage for the same or adjacent external lifecycle class; `validate_debug_artifact`, debug seam-risk index check, `validate_critique_artifacts`, `validate_integrations`, packaging validators, markdown/link/secret checks, `sync_support`, and `update_tools` passed locally.
- Test duplication pressure: No runtime tests added; this slice intentionally records a split/non-closure rather than changing behavior or adding post-hoc cleanup that could be mistaken for teardown proof.
- Critique: Fresh-eye causal review classified #371 as a bug but not locally fixed, accepted the upstream split, and found one Act Before Ship wording loophole that allowed closure without teardown proof. The wording was tightened before commit. Artifact: `charness-artifacts/critique/2026-06-15-issue-371-agent-browser-lifecycle-split.md`.
- Off-goal findings: Upstream `vercel-labs/agent-browser#1334` is the closest tracker for interrupted/killed/timed-out Chrome helper and temp-profile leaks; `#1401` covers Linux launch zombies; `#1371` covers high-CPU helpers under temp profiles. This token has read-only permission on the upstream repo, so no new upstream issue was filed.
- Lessons carried forward: For external binaries, healthcheck/reaper surfaces must be named as drift mitigation unless the repo holds an invocation lifecycle handle and can prove process/profile teardown at the final boundary.

## Context Sources

- User request on 2026-06-15: solve new nose findings, issues #371-#373, and
  actively reduce slow tests, using quality timing surfaces where available.
- `docs/handoff.md` current state: #367 shipped quality gate-speed surfaces:
  `inventory_ci_recoverable_gates.py` and `command_timing_log` ingest.
- `gh issue view 371`: agent-browser orphaned chromium/profile-dir lifecycle bug.
- `gh issue view 372`: debug skill needs disconfirmer-first rung for
  absence/attribution/liveness/frequency claims.
- `gh issue view 373`: template-producing skills must scaffold before
  validators/readiness checks.
- `skills/public/quality/scripts/inventory_nose_clones.py --repo-root . --json`:
  nose 0.10.0 reports top clone families including adapter resolver/bootstrap
  boilerplate and init/validation candidates.
- `charness-artifacts/quality/latest.md`: prior nose 0.7.0 quality pass and
  already-shipped timing-surface context.

## Interview Decisions

- Mode: implementation-continuation after explicit `/goal` activation; rejected
  artifact-only because the user asked to solve the items, not only outline them.
- Order: runtime reduction first, then #373, #372, #371, then selected nose
  refactors. Rejected doing nose first because clone refactors are broad and
  would force repeated slow proof before the speed work pays off.
- #371 closure standard: require lifecycle teardown proof or honest split.
  Rejected closing with periodic cleanup alone because the issue body explicitly
  calls that downstream mitigation, not the durable fix.
- Timing standard: use structured timing or comparable before/after samples.
  Rejected anecdotal "felt faster" claims.
- Nose standard: fix selected extractable families, not all reported families.
  Rejected treating all clone families as debt because some are intentional
  portable skill boilerplate.

## Plan Critique Findings

- Folded blocker: issue #373 means this very goal must not validate a missing or
  unfilled artifact before producer scaffolding; this draft was scaffolded with
  `upsert_goal.py` before pursue-readiness validation.
- Folded blocker: #371 has external/runtime proof risk; the slice plan requires
  controlled lifecycle proof and forbids closure by reaper-only mitigation.
- Over-worry not folded: requiring a fixed percentage speedup before activation.
  The goal instead requires aggressive measured reduction attempts and honest
  no-safe-reduction evidence because the exact removable stale-test surface is
  unknown before slice 1 inventory.
- Reviewer provenance: Before-phase same-agent shaping only; fresh-eye critique
  required before the first broad implementation bundle or any issue closeout.

## Off-Goal Findings

None yet.

## Final Verification

Pending until the goal is active and slices are complete.

Retro: skipped: host-blocked-subagent: not run during draft shaping; required at final closeout.
Host log probe: skipped: host-log-not-exposed: draft shaping has no active goal window yet.
Disposition review: skipped: host-blocked-subagent: not applicable until final auto-retro has findings to disposition.

## User Verification Instructions

After activation and completion, verify:

1. Run `gh issue view 371 --json state,title,url`, and the same for #372/#373.
2. Read the final runtime before/after block in the goal or linked quality
   artifact.
3. Run the final nose inventory command and compare the recorded targeted
   family dispositions.
4. Review final non-claims for any issue not closed or any runtime proof skipped.

## Auto-Retro

Retro dispositions: pending final retro; no improvements surfaced during draft shaping.
Structural follow-up: none — draft shaping has not produced transferable waste beyond the in-scope #373 ordering issue.
