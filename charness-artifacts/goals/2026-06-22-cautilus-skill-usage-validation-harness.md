# Achieve Goal: Cautilus skill-experiment harness — real headless-run usage validation for skills

Status: draft
Created: 2026-06-22
Activation: `/goal @charness-artifacts/goals/2026-06-22-cautilus-skill-usage-validation-harness.md`
Timebox: 6h
Activation time: recorded at `/goal` activation (run start)
Closeout reserve: 45m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: Slice 4 — wire the wrapper invocation (justification-log + full `-- --input/--output`). S1+S2+S3 DONE; the keystone extractor passed a NO-blocker fresh-eye critique (two findings folded) + the full slice closeout.
- Current disposition: ACTIVE (pursued 2026-06-22). Capture→extract subsystem complete and critiqued. Next is the cautilus-wrapper plumbing (no scorer invocation yet — that is the single S7 run).
- Current slice intent: Slice 4 proves `run_cautilus_eval.py --mode skill-experiment --justification-log <transcript> -- --input <built.json> --output <report>` assembles correctly (dry-run): the transcript satisfies the `source-kind: transcript` gate and the forwarded command carries the two-file roles (BLOCKER-3).
- Next action: implement Slice 4 — author a transcript justification-log shape + build a sample input.v1, run the wrapper `--dry-run`, confirm gate + command assembly. Open nit carried: DRY findResultEvent/findClaudeResultEvent in a later slice.
- Verification cadence: cheap deterministic checks at commit boundaries; runner smoke + fresh-eye critique at slice boundaries; the one real Cautilus run at the External/Live boundary; broad gate at closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`; final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed files and owning/generated surfaces, expected invariants, tests/proof, non-claims, out-of-scope lines, and reviewer questions.
- Discuss before activation: Resolved — operator chose (2026-06-22) one real eval-only Cautilus paid run, dropping the forced-JSON default, and a 6h box; eval-only contract honored (consult + record `plan_cautilus_proof.py`, run only via `run_cautilus_eval.py`, exactly one single-scenario run). Full rationale in `## Interview Decisions`.
- History boundary: keep this frame current; move completed detail to `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Build the real headless-run usage-validation harness for charness skills so a skill change can be proven by a *real* `claude -p` run scored by Cautilus, not only by routing sentinels or blind-runner A/B substitutes.

Corrected data flow (plan-critique BLOCKER-1, verified against the cautilus source at `/home/hwidong/codes/cautilus`): Cautilus `evaluate skill-experiment` is a **deterministic scorer**, not a transcript analyzer. It reads a structured `--input` JSON (`cautilus.skill_clone_experiment_input.v1`) carrying `sourceCoverageObligations` + `rubricPhrases` + each arm's **host-captured `output.sourceRefs`**, and writes a `--output` report (`cautilus.skill_clone_experiment_report.v1`: `promotion_recommendation` / `source_coverage_delta` / `rubric_match` / `baseline_vs_variant_delta` / `variant_ran`). So the chain is:

1. Headless `claude -p` run → capture a **natural stream-json transcript** (drop forced-JSON).
2. Repo-owned **extractor** (the keystone deliverable) parses the transcript → emits `skill_clone_experiment_input.v1` JSON with `baseline.output.sourceRefs` / `variant.output.sourceRefs` / `text` / `status`.
3. `run_cautilus_eval.py --mode skill-experiment --justification-log <transcript.md> -- --input <input.v1.json> --output <report.json>` — **two files, two roles**: the transcript satisfies the charness wrapper's `- source-kind: transcript` gate; the extracted JSON is what Cautilus actually scores.
4. Baseline-vs-variant arms come from **two capture passes** at different skill refs (baseline = origin/main pre-disposition; variant = `5ded9f3a`).

Prove the whole chain with **one real single-scenario** run; defer the full multi-scenario sweep.

**Source handoff entry #2: START HERE — A: cautilus skill-experiment harness** (operator-requested). Detail + B-smoke evidence: [proposal § A design](../quality/2026-06-21-quality-reference-disposition-proposal.md) (lines 263–299).

## Non-Goals

- Not a release: no plugin version bump expected (generated mirrors are *synced*, not versioned).
- Not the full multi-scenario blind A/B sweep — this goal runs **one** single-scenario run. Because Cautilus scoring is deterministic, one run proves the chain emits a real verdict but is **not** a power-bearing A/B (variance lives in the stochastic upstream capture). Label it as such.
- Do not unlock broader Cautilus surfaces (claim discovery, optimize, review-learning, `evaluate live`, Agent orchestration) — they stay disabled by repo policy.
- Optional proposal item #5 (`reviewer_tiers.high-leverage` in the quality adapter) is out of scope unless the proof run concretely needs it.
- Do not absorb adjacent handoff entries (C/#387, D/#392, #396) beyond this chunk.

## Boundaries

- In scope: `scripts/agent-runtime/run-local-eval-test.mjs` (+ its claude runtime sibling), a **new repo-owned transcript→`skill_clone_experiment_input.v1` extractor**, the `scripts/run_cautilus_eval.py` justification-log + `--`-passthrough interplay, `scripts/plan_cautilus_proof.py` (read-only consult only), `evals/cautilus/` (the new quality-skill obligations/rubric input), `scripts/cautilus_scenarios_lib.py` / `validate_cautilus_scenarios.py` (only if extending the validator to the new schema), baseline/variant capture tooling, and the generated mirrors under `plugins/charness/scripts/` + `mutants/` (sync only).
- Ground truth for the Cautilus contract is the local source at `/home/hwidong/codes/cautilus` (read-only). Do NOT trust the proposal's prose where it conflicts; do NOT invoke bare `cautilus evaluate` (including `--help`) to discover the API — read the source.
- **The SKILL_DIR / skill-ref lever governs the RUNNER's two capture passes only, not Cautilus** (Cautilus receives two already-captured `output` objects). BLOCKER-2: prefer **two isolated read-only worktrees** (the proposal's own proven method, b01cee6b-baseline vs 5ded9f3a-variant) over mutating the shared install clone `~/.agents/src/charness` — that clone is what a live `/quality` resolves SKILL_DIR to, and an in-place checkout can silently make a concurrent session run the wrong skill (#258-class corruption). If the shared clone must be used: record its original ref, restore it in a `finally`/trap even on failure, and precondition that no live `/quality` is mid-resolution.
- Portable per implementation-discipline: host-specific behavior stays in adapters/presets; no hardcoded host assumption added to the runner.
- Phase barriers: mutate → sync → verify → publish; sync generated/plugin/mirror surfaces before running validators.
- Eval-only / ask-before-run honored: consult `plan_cautilus_proof.py` first, run through `run_cautilus_eval.py` (never bare `cautilus evaluate`), exactly one real single-scenario run.
- Stop conditions: if Slice 1 finds the Cautilus contract differs from the corrected data flow above, stop and surface before building the extractor; if dropping forced-JSON breaks a consumer that cannot be migrated inside the box, stop and surface rather than guess.

## User Acceptance

What the user can do to verify completion directly.

- Run `node scripts/agent-runtime/run-local-eval-test.mjs` (claude_code backend) and confirm it captures a **natural stream-json transcript** artifact (not a forced single-JSON envelope), while still writing the normalized result to `--output-file`.
- Confirm existing eval consumers (the routing-fixture scenario path) still pass after the default flip — repo validators green.
- Run the extractor on a captured transcript and confirm it emits a JSON that validates against `cautilus.skill_clone_experiment_input.v1` (baseline/variant `output.sourceRefs` populated).
- See one real `cautilus evaluate skill-experiment` baseline-vs-variant verdict (promote / revise / discard) recorded in `charness-artifacts/cautilus/latest.md`, produced via `run_cautilus_eval.py --justification-log <transcript> -- --input <json> --output <report>`.
- Confirm any worktree/clone used for capture is cleaned up / restored to its original ref (`~/.agents/src/charness` back at `d2cf1b75` if it was used).

## Agent Verification Plan

### Low-Cost Checks

- `node --check` on every changed `.mjs`; repo lint/format if configured.
- The extracted `--input` JSON validates against `cautilus.skill_clone_experiment_input.v1` (schemaVersion + required `experimentId`/`taskPacket`/`baseline`/`variant`); fixture/obligations validate against the schema actually used.
- `scripts/validate_skills.py`, `scripts/check_skill_contracts.py`, doc-links, and the generated-mirror sync check.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.

### High-Confidence Checks

- Runner smoke: a bounded real headless capture produces a stream-json transcript file AND the normalized `--output-file` result is preserved in shape (this smoke is also how the BLOCKER-2 over-worry is settled — if no external consumer breaks, no migration is needed).
- Extractor unit check: a known transcript → expected `output.sourceRefs` set (the keystone correctness check).
- `run_cautilus_eval.py --dry-run --mode skill-experiment --justification-log <transcript.md> -- --input <built.json> --output <report.json>` accepts the transcript as `source-kind: transcript` AND the built `--input` passes Cautilus's schema (full command, not just the wrapper gate — BLOCKER-3).
- Fresh-eye slice critique on the extractor + runner-change slices (bounded packet) — different agent context, not a same-agent pass.

### External Or Live Proof

- `plan_cautilus_proof.py --repo-root . --json` consulted (read-only) immediately before the run. BLOCKER-4 honesty: the planner is hardcoded to return `next_action: none` / `must_ask_before_running: true`, and `run_cautilus_eval.py` *proceeds anyway* once a real `--justification-log` is supplied — so authorization is the operator's explicit one-run approval (Interview Decisions) + a real transcript justification-log, NOT a planner green. Record the planner output verbatim alongside the operator-approval citation in `charness-artifacts/cautilus/latest.md`.
- Exactly ONE real `cautilus evaluate skill-experiment` baseline-vs-variant run via `run_cautilus_eval.py` (never bare). Any second run (e.g. a re-run after a failed first) re-enters the Operator Decision Queue. The full multi-scenario sweep is deferred.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | De-risk the Cautilus contract against `/home/hwidong/codes/cautilus` source | Slices 3–7 depend on the real shape; the proposal's transcript-is-input premise was wrong (BLOCKER-1) | Recorded: input schema `cautilus.skill_clone_experiment_input.v1`, `--input/--output` CLI, host-supplied `output.sourceRefs`, report schema + fields | **done** (181ebef7; contract matches corrected flow; see Slice Log S1) |
| 2 | Runner: stream-json default (drop forced-JSON) + persist transcript artifact; sync mirrors | Core capture step; flip is small (`claudeArgs`/`parseClaudeOutput` only) | `node --check` + runner smoke: transcript captured, normalized `--output-file` preserved, consumers green, mirrors synced | **done** (16/16 unit + real claude 2.1.179 stream-json smoke; mirror parity; see Slice Log S2) |
| 3 | Keystone: transcript → `skill_clone_experiment_input.v1` extractor (sourceRefs capture) | The chain's keystone the original plan omitted; fixture + run both need it | Extractor unit: known transcript → expected `output.sourceRefs`; emitted JSON validates against the schema | **done** (9/9 unit + real CLI + NO-blocker fresh-eye critique, 2 findings folded; see Slice Log S3) |
| 4 | Wire the wrapper invocation: justification-log + full `-- --input/--output` | Two-file roles (BLOCKER-3) must be correct or the run fails | `run_cautilus_eval.py --dry-run ... -- --input --output` accepts both the gate and the schema | planned |
| 5 | Author quality-skill `sourceCoverageObligations` + `rubricPhrases` | The eval needs obligations/rubric (existing fixtures are routing sentinels on a different schema) | Obligations/rubric defined; validator-extend-vs-runtime-artifact decision recorded (install validator only knows `evaluation_input.v1`) | planned |
| 6 | Baseline↔variant capture via isolated read-only worktrees | The A/B arms — proposal's proven method; avoids mutating the shared install clone (BLOCKER-2) | Two transcripts captured at baseline vs `5ded9f3a`; any clone/worktree restored/cleaned | planned |
| 7 | One real Cautilus proof run (gated, External/Live) | The empirical proof the whole chain emits a verdict | Recorded promote/revise/discard in `charness-artifacts/cautilus/latest.md` (labeled single-capture proof) + planner output verbatim | planned |
| 8 | Closeout | Task-completing repo work: prove, reflect, hand off | `check_goal_artifact.py` complete + broad gate (or substitute) green + retro dispositions + handoff updated | planned |

## Operator Decision Queue

Record decisions, confirmations, credential actions, manual proof steps, and
external-boundary approvals discovered during the run when they do not block
safe local progress. Use `none — <reason>` when the queue is empty at closeout.

- Decision: run the FULL multi-scenario baseline-vs-variant Cautilus A/B sweep (beyond the one authorized proof run)?
  - Owner: operator
  - Why deferred: operator chose one single-scenario proof run for this goal; the full sweep is a separate paid decision
  - Unblock action: operator says "run the full sweep" (new goal or follow-up slice)
  - Revisit trigger: after the one proof run demonstrates the chain emits a real verdict
- Decision: define `reviewer_tiers.high-leverage` in the quality adapter (optional proposal #5)?
  - Owner: operator
  - Why deferred: not required for the single proof run
  - Unblock action: operator requests it, or a run needs to assert the fresh-eye reviewer's tier
  - Revisit trigger: if asserting reviewer tier becomes load-bearing for the eval

## Coordination Cues

Phase routing defers to `find-skills` at the point of need — no inline phase→skill map is hardcoded here. Closeout coordination evidence (`Routing:` / `Gather:` / `Release:` / `Issue closeout:`) is recorded under `## Final Verification` / here at the After phase when the matching floor triggers.

## Slice Log

### Slice 1: S1: De-risk Cautilus skill-experiment contract

- Objective: Record the real cautilus skill-experiment contract from source (181ebef7), confirm the corrected data flow, clear the Slice-1 stop condition.
- Why this approach: Goal mandates source-as-ground-truth (not the proposal prose); read the Go scorer directly rather than probing the binary.
- Commits: none (research/de-risk slice; no code mutation)
- What changed: No files changed. Findings recorded here + carried into S3 extractor design.
- Alternatives rejected:
- Targeted verification: Read internal/contracts/constants.go:69-70, internal/app/skill_experiment_command.go, internal/runtime/skill_clone_experiment.go (full), internal/app/app.go:200-201 (dispatch) + 2791-2818 (parseInputOutputArgs); cross-checked scripts/run_cautilus_eval.py passthrough.
- Test duplication pressure:
- Critique: n/a — pure research slice; no design lock yet. Fresh-eye critique reserved for the S2 runner-change and S3 extractor slices per the goal's verification plan.
- Off-goal findings:
- Lessons carried forward: CONTRACT CONFIRMED (matches corrected data flow; stop condition NOT triggered). (1) Input schema cautilus.skill_clone_experiment_input.v1 REQUIRED keys: schemaVersion, experimentId (non-empty), taskPacket (object w/ >=1 of path|sourceRef|schemaVersion|summary), baseline (object), variant (object). OPTIONAL: exemplar, sourceCoverageObligations (array of {id,ref,required?=true}), rubricPhrases (array of non-empty strings), isolation. (2) Run object: status one of passed|failed|blocked|degraded (default passed); sourceRefs merged from top-level sourceRefs + output.sourceRefs (unique-sorted); text = input.text||output.text||input.summary||output.summary. (3) CLI: cautilus evaluate skill-experiment --input <path> --output <path>; parseInputOutputArgs accepts ONLY --input/--output (else 'unknown argument'); --input required, --output optional->stdout. (4) GOTCHA isolationSafe = productionTouchDeclared && !productionTouched: a clean 'promote' REQUIRES input.isolation.productionSkillTouched:false explicitly; omitting isolation => isolationSafe=false => recommendation downgrades to 'revise'. (5) promotion_recommendation: discard if !variantRan; revise if !baselineComparable||!isolationSafe||lost>0||stillMissing>0||rubricMissing>0; promote if addedSourceCoverage>0||rubricGained>0; else discard. (6) Report schema cautilus.skill_clone_experiment_report.v1 fields: promotion_recommendation, source_coverage_delta, rubric_match, baseline_vs_variant_delta, variant_ran, baseline_comparable, findings, isolation_notes. (7) Wrapper: -- --input/--output forwarded verbatim; --justification-log wrapper-only; planner-none overridden by justification-log (printed note) = BLOCKER-4 confirmed.
- Metrics:

### Slice 2: S2: Runner stream-json default + transcript artifact

- Objective: Flip the claude_code eval runner from forced --output-format json to a natural stream-json transcript while preserving the normalized --output-file; persist transcript.jsonl; sync the plugin mirror.
- Why this approach: stream-json's newline-delimited event stream preserves the agent's real tool calls (file Reads = sourceRefs) that the S3 extractor needs; the single JSON envelope hid them. findClaudeResultEvent unifies stream-json + the legacy single envelope, so existing consumers stay green (default-flip, not opt-in, per Interview Decision).
- Commits: (this commit)
- What changed: scripts/agent-runtime/run-local-eval-test.mjs (claudeArgs -> stream-json --verbose; new findClaudeResultEvent; parseClaudeOutput + telemetry use it; persist transcript.jsonl + artifactRef('transcript')); tests/agent-runtime/native.test.mjs (+stream-json seam test); plugins/charness/scripts/agent-runtime/run-local-eval-test.mjs (mirror synced).
- Alternatives rejected: Opt-in additive stream-json mode keeping JSON default — rejected per Interview Decision (operator wants stream-json as the real default). Dropping renderClaudePrompt's schema framing — rejected: the normalized --output-file (routing consumers) depends on the final answer being routing JSON.
- Targeted verification: node --check OK; node --test tests/agent-runtime/native.test.mjs = 16/16 pass (incl. new stream-json transcript test asserting transport flags, parsed observed result, persisted transcript.jsonl, telemetry from result event); REAL claude 2.1.179 CLI smoke: -p --output-format stream-json --verbose emitted 63-line JSONL with terminal type:result (subtype success, result text, usage+total_cost_usd present) = matches findClaudeResultEvent; mirror diff: plugins copy == source.
- Test duplication pressure: Added ONE seam test reusing the existing recordingSpawn/observedFixture helpers (no new harness); covers the new stream-json branch + transcript persistence not covered by the legacy single-envelope test. No duplicate of existing assertions.
- Critique: Deferred to a combined fresh-eye critique over the coupled capture->extract intent after S3 (extractor): the extractor's correctness depends on this transcript format, so critiquing the runner alone would be incomplete. Matches the goal's 'extractor + runner-change slices' bounded packet.
- Off-goal findings:
- Lessons carried forward: Real stream-json carries system/assistant/user/result + rate_limit_event lines; tool calls live in assistant 'tool_use' content blocks and tool_result in user events — the S3 extractor scans assistant tool_use (Read/Glob/Grep) for file paths = output.sourceRefs. BLOCKER-2 over-worry SETTLED: normalized output-file shape unchanged, zero consumer migration.
- Metrics:

### Slice 3: S3: Keystone transcript->skill_clone_experiment_input.v1 extractor

- Objective: Build the repo-owned extractor that parses a stream-json transcript into a cautilus.skill_clone_experiment_input.v1 JSON, recovering each arm's output.sourceRefs from the agent's Read/Edit/Write tool calls + text/status from the terminal result event.
- Why this approach: The chain's keystone (omitted by the original plan, surfaced by BLOCKER-1): cautilus is a deterministic scorer over host-captured output.sourceRefs, so something must bridge transcript->input.v1. Built as an .mjs sibling of the runner (same dir, auto-mirrored) with pure testable cores + a thin CLI.
- Commits: (this commit)
- What changed: NEW scripts/agent-runtime/extract-skill-experiment-input.mjs (parseTranscriptEvents/collectSourceRefs/findResultEvent/transcriptCwd/extractRunFromTranscript/buildSkillCloneExperimentInput + CLI); scripts/agent-runtime/contract-versions.mjs (+SKILL_CLONE_EXPERIMENT_INPUT_SCHEMA); NEW tests/agent-runtime/extract-skill-experiment-input.test.mjs (9 tests); scripts/run_js_mutation.py (+weight 369 for new module); tests/quality_gates/test_js_mutation_tooling.py (pool list + generalize import gate to all *.test.mjs); plugin mirrors synced.
- Alternatives rejected: Python extractor — rejected: transcript is JS-object-shaped, runner is .mjs, keep capture+extract in one language/dir. Re-implementing a cautilus schema validator in-repo — rejected: the Go scorer is the authority; buildSkillCloneExperimentInput faithfully enforces its required-field + status-enum + non-empty-string rules so a malformed build throws before cautilus.
- Targeted verification: node --check OK; 9/9 extractor tests + 16/16 native = 25/25 via npm run test:agent-runtime; real CLI end-to-end on the captured smoke transcript -> valid input.v1; run_slice_closeout.py --skip-broad-pytest ALL GREEN (sync+packaging+agent-runtime tests+mutation dry-run+ruff+validators); stryker dry-run = 369 mutants for the new module.
- Test duplication pressure: 9 extractor tests target distinct branches (sourceRefs extraction+exclusions, cwd-relativization symlink safety, status mapping, builder required-field+enum+non-empty guards, full CLI two-arm). No overlap with native.test.mjs. The mutation-tooling gate now covers the new module (weight 369, imported by the new test).
- Critique: Fresh-eye bounded reviewer (separate general-purpose context), checked against cautilus source 181ebef7. Verdict: NO blockers. Folded: (1) CONCERN worktree symlink/realpath relativization silently zeroes coverage -> FIXED by preferring the transcript's own init cwd as the relativization root (form-consistent with claude's tool paths) + a regression test; (2) Q4 residual -> hardened assertRun with status-enum + non-empty-string checks so the builder rejects exactly what the Go scorer rejects, with tests. DEFERRED (reviewer: no action this slice): findResultEvent/findClaudeResultEvent duplication (~10 lines) -> tracked nit, consolidate in a later slice to avoid re-touching the committed runner. Confirmed safe: emitting only output.sourceRefs (scorer merges top-level+output); unification keeps single-envelope consumers green.
- Off-goal findings:
- Lessons carried forward: Adding a scripts/agent-runtime/*.mjs file rotates the JS mutation baseline (analogous to the dup-ratchet family_id trap): expect to (a) add it to the pool-list gate, (b) add an accurate weight via a scoped stryker dry-run, (c) ensure a native test imports it. The import-coverage gate was hardcoded to native.test.mjs; generalized to all *.test.mjs. transcript cwd from the init event is the safe relativization root across worktrees.
- Metrics:

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

- Source: handoff entry #2 (START HERE — A: cautilus skill-experiment harness) — see [docs/handoff.md](../../docs/handoff.md).
- Design + B-smoke evidence: [quality proposal § A design](../quality/2026-06-21-quality-reference-disposition-proposal.md) (lines 263–299) — note its "transcript is Cautilus's input" framing is corrected by BLOCKER-1.
- **Cautilus contract ground truth (read-only):** `/home/hwidong/codes/cautilus` — `internal/app/skill_experiment_command.go` (`--input/--output` CLI), `internal/runtime/skill_clone_experiment.go` (scorer over `output.sourceRefs`), `internal/contracts/constants.go:69-70` (schema names).
- Runner under change: `scripts/agent-runtime/run-local-eval-test.mjs` (forces `--output-format json` at line 445; normalized result written via `normalizeObservedResult`, raw envelope kept only as `result.raw`).
- Gate + planner: `scripts/run_cautilus_eval.py` (`--justification-log` is wrapper-only, not forwarded; `--` passthrough to cautilus), `scripts/plan_cautilus_proof.py`; contract `skills/public/quality/references/cautilus-on-demand.md`.
- Install clone (capture lever only): `~/.agents/src/charness` (currently at `d2cf1b75`; baseline = origin/main pre-disposition, variant = `5ded9f3a`).

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

- Scope / definition of done — options: {build+gate-the-paid-run, +one-real-proof-run, +full-multi-scenario-sweep}. Chosen: **+ one real single-scenario proof run**. Rejected gated-only (operator wants empirical proof the chain emits a verdict, not just plumbing); rejected full sweep (token cost — deferred to a follow-up once the chain is proven).
- Forced-JSON handling — options: {opt-in additive stream-json mode keeping JSON default, default-flip dropping forced-JSON}. Chosen: **default-flip / drop forced-JSON**. Rejected opt-in additive (operator accepts the wider blast radius and wants stream-json to be the real default). Plan-critique BLOCKER-2 over-worry: the runner's `--output-file` is a *normalized* packet, so the actual consumer blast radius is likely near-zero (settled by the Slice 2 runner smoke), not the broad migration first assumed.
- Timebox — options: {2h, 4h, 6h}. Chosen: **6h** with 45m closeout reserve; done-early policy `continue_next_improvement` toward the ranked backlog (#396 next). Re-weight effort toward Slices 1/3/7 (the hard 60%), not the runner flip.
- Discuss before activation: Resolved — the three consequential defaults (one real eval-only Cautilus *paid* run; dropping the forced-JSON default; the 6h box) were each explicitly chosen by the operator on 2026-06-22. The eval-only contract is honored in the plan: consult `plan_cautilus_proof.py` (output recorded verbatim), run only via `run_cautilus_eval.py`, exactly one single-scenario run; a second run re-enters the operator queue.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance.

Reviewer: bounded fresh-eye plan reviewer (separate `general-purpose` agent context, 2026-06-22), which verified claims against the local cautilus source `/home/hwidong/codes/cautilus` (181ebef7). Load-bearing finding independently re-confirmed by the parent before folding.

- **BLOCKER-1 (folded — Goal rewrite):** the central premise was inverted. `cautilus evaluate skill-experiment` does NOT consume a transcript; it scores a structured `skill_clone_experiment_input.v1` JSON with host-supplied `output.sourceRefs`. Fold: added the transcript→input.v1 **extractor** as the keystone (Slice 3) and corrected the Goal data flow + schema names. *Confirmed by parent:* `constants.go:69`, `skill_experiment_command.go:14-24`, `skill_clone_experiment.go:61/65/124`.
- **BLOCKER-2 (folded — Boundaries + Slice 6):** the "checkout the shared install clone per arm" lever is a runner-capture concern (not Cautilus) and risks silently corrupting a live `/quality`. Fold: prefer isolated read-only worktrees; if the shared clone is used, record + restore the original ref + precondition no live `/quality`.
- **BLOCKER-3 (folded — Verification + Slice 4):** `--justification-log` (wrapper-only gate) ≠ `--input` (what Cautilus reads). Fold: the dry-run check uses the full `... --justification-log <transcript> -- --input <json> --output <report>`, and the built input validates against the schema; transcript carries a literal `- source-kind: transcript` line ≥32 bytes.
- **BLOCKER-4 (folded — Verification):** "operator chose +one run" is not a planner green; the planner is hardcoded to `none` and the wrapper proceeds on the justification-log. Fold: record planner output verbatim + operator-approval citation; any second run re-enters the queue.
- **Over-worry (raised, not folded):** (a) forced-JSON consumer migration is likely near-zero (normalized output-file) — verify via the Slice 2 smoke rather than pre-budgeting a big migration; (b) generated-mirror sync is mechanical/cheap, just keep it behind the mutate→sync barrier; (c) "one run too few" is acceptable because Cautilus scoring is deterministic — label the verdict a single-capture proof, not a power-bearing A/B.

## Off-Goal Findings

## Final Verification

## User Verification Instructions

## Auto-Retro
