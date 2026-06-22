# Achieve Goal: Cautilus skill-experiment harness — real headless-run usage validation for skills

Status: complete
Created: 2026-06-22
Activation: `/goal @charness-artifacts/goals/2026-06-22-cautilus-skill-usage-validation-harness.md`
Timebox: 6h
Activation time: 2026-06-22T08:30:00+09:00
Closeout reserve: 45m
Done-early policy: continue_next_improvement

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: COMPLETE. All 8 slices landed; the chain is built, tested, plumbing-proven, and PROVEN END-TO-END by one real cautilus verdict (`discard`, honest zero-coverage-delta) from two real haiku captures; broad gate green; retro persisted + dispositioned.
- Current disposition: COMPLETE (under-budget early close ~2h into the 6h box; full scope met). `check_goal_artifact.py` ok=true. Deferred: the full sweep + reviewer_tiers (operator queue); the DRY nit + no-name-hint eval redesign (next session).
- Current slice intent: closed — final broad gate (verification lock + standing pytest) green, retro/handoff done, status flipped to complete with honest non-claims and an early-close report.
- Next action: none for this goal — handoff carries #396 + the deferred decisions to the next session.
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
| 4 | Wire the wrapper invocation: justification-log + full `-- --input/--output` | Two-file roles (BLOCKER-3) must be correct or the run fails | `run_cautilus_eval.py --dry-run ... -- --input --output` accepts both the gate and the schema | **done** (dry-run assembles two-file command + planner-override note; negative gate refuses raw jsonl/wrong-kind; see Slice Log S4) |
| 5 | Author quality-skill `sourceCoverageObligations` + `rubricPhrases` | The eval needs obligations/rubric (existing fixtures are routing sentinels on a different schema) | Obligations/rubric defined; validator-extend-vs-runtime-artifact decision recorded (install validator only knows `evaluation_input.v1`) | **done** (spec.json = runtime artifact, 7 routed obligations; surface declared; 10/10 tests; see Slice Log S5) |
| 6 | Baseline↔variant capture via isolated read-only worktrees | The A/B arms — proposal's proven method; avoids mutating the shared install clone (BLOCKER-2) | Two transcripts captured at baseline vs `5ded9f3a`; any clone/worktree restored/cleaned | **done** (two clean haiku captures; worktrees removed; install clone untouched at d2cf1b75; see Slice Log S7) |
| 7 | One real Cautilus proof run (gated, External/Live) | The empirical proof the whole chain emits a verdict | Recorded promote/revise/discard in `charness-artifacts/cautilus/latest.md` (labeled single-capture proof) + planner output verbatim | **done** (verdict `discard` = honest zero-coverage-delta; planner verbatim recorded; see Slice Log S7) |
| 8 | Closeout | Task-completing repo work: prove, reflect, hand off | `check_goal_artifact.py` complete + broad gate (or substitute) green + retro dispositions + handoff updated | **done** (check_goal_artifact ok=true; broad gate + standing pytest green; retro persisted; handoff updated) |

## Operator Decision Queue

Two operator-only decisions surfaced and were deferred at closeout; neither blocks
safe local progress (both are paid/adapter-write boundaries the goal scoped out).

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

Routing: find-skills (session start) recommended `impl` as the durable work skill and `quality` for validation posture + `cautilus` (eval-only) for the harness; `achieve` drove the goal lifecycle while `critique` (S3 fresh-eye) and `retro` (closeout) coordinated the slices.
Gather: n/a — no external URL/source was ingested; the cautilus contract came from the local read-only source tree, not a fetched asset.
Release: n/a — generated mirrors are synced, not versioned; no plugin version bump (per Non-Goals).
Issue closeout: n/a — this goal originated from handoff entry #2, not a tracked GitHub issue; no issue is being closed.

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

### Slice 4: S4: Wire the wrapper invocation (justification-log + -- --input/--output)

- Objective: Prove the two-file roles (BLOCKER-3): run_cautilus_eval.py forwards -- --input/--output verbatim to cautilus evaluate skill-experiment while the markdown transcript justification-log satisfies the wrapper's source-kind gate; document the harness flow durably.
- Why this approach: The wrapper plumbing must be correct before the single S7 run or the run fails on plumbing. Dry-run proves assembly without invoking cautilus (respects the one-scorer-run scope). A concise harness README makes S6/S7 + operator acceptance reproducible.
- Commits: (this commit)
- What changed: NEW evals/cautilus/skill-experiment/README.md (three-role data flow: capture->extract->score + eval-only contract); NEW evals/cautilus/skill-experiment/justification-log.template.md (source-kind: transcript shape). No code/mirror change (evals/ is not a plugin-exported surface).
- Alternatives rejected:
- Targeted verification: POSITIVE: run_cautilus_eval.py --mode skill-experiment --justification-log <461B transcript md> --dry-run -- --input <built input.v1> --output <report> => exit 0, prints 'would run: cautilus evaluate skill-experiment --input ... --output ...' (BLOCKER-3 two-file roles confirmed) + the planner-none-overridden-by-justification note (BLOCKER-4 confirmed live). NEGATIVE: raw transcript.jsonl (no source-kind line) REFUSED; source-kind: made-up-kind REFUSED listing supported kinds => the gate has teeth, a markdown justification-log is required. check_doc_links + check-markdown green.
- Test duplication pressure:
- Critique: n/a — small plumbing-proof + doc slice; the load-bearing capture->extract subsystem already passed the S3 fresh-eye critique. No new design surface introduced.
- Off-goal findings:
- Lessons carried forward: The raw stream-json transcript does NOT satisfy the wrapper gate (no - source-kind line) — S6/S7 must author a separate markdown justification-log (template provided). --dry-run only assembles/forwards; it does NOT validate the input schema against cautilus, so schema validity rests on the extractor's source-faithful structural checks (S3) until the one real S7 scorer run.
- Metrics:

### Slice 5: S5: Author sourceCoverageObligations + rubricPhrases spec

- Objective: Author evals/cautilus/skill-experiment/spec.json grounded in the 5ded9f3a disposition (7 routed refs), decide validator-extend-vs-runtime-artifact, and declare the new surface in the manifest.
- Why this approach: The eval needs real obligations: the disposition routes 7 quality references via SKILL.md/inventory-dispatch.md pointers, so the variant should reach refs the baseline cannot. Source-coverage GAIN is the robust discriminating signal; obligations are required:false (a single stochastic capture is not expected to cover all 7) and rubricPhrases are kept neutral to avoid spurious revise. Verified all 7 refs exist + the 2 merge-retired are absent.
- Commits: (this commit)
- What changed: NEW evals/cautilus/skill-experiment/spec.json (experimentId/taskPacket/7 obligations/rubric/isolation.productionSkillTouched:false/skillId); tests/agent-runtime/extract-skill-experiment-input.test.mjs (+spec.json well-formed + coverage-gain test); .agents/surfaces.json (+evals/cautilus/skill-experiment/** under prompt-behavior-proof surface).
- Alternatives rejected: required:true obligations — rejected: a single capture rarely exercises every routed ref -> would force a spurious stillMissing/revise. rubricPhrases = routed concept tokens — rejected: substring-miss on one stochastic final answer forces revise; chose robust near-certain phrases (quality, reference) so rubric stays neutral and the verdict rides on source coverage. Extending validate_cautilus_scenarios.py — rejected: it validates evaluation_input.v1 routing scenarios, a different schema.
- Targeted verification: 10/10 extractor tests (incl. new spec test asserting 7 obligations + isolation.productionSkillTouched=false + a real variant coverage gain over baseline); spec.json valid JSON; validate_cautilus_scenarios.py still green (only validates scenarios.json); run_slice_closeout.py --skip-broad-pytest COMPLETED (validate_surfaces + validate_cautilus_proof + agent-runtime tests + mutation dry-run all PASS).
- Test duplication pressure: One new test reads the COMMITTED spec.json (makes it a tested artifact, guards drift) + asserts the coverage-gain mechanic. No duplication with existing extractor tests.
- Critique: n/a — data/spec authoring slice; no new code logic. The load-bearing extractor already passed the S3 fresh-eye critique; this slice only feeds it real obligations.
- Off-goal findings:
- Lessons carried forward: DECISION: spec.json is a RUNTIME ARTIFACT (validated by the extractor's build-time checks + the new JS test), not a cautilus-schema fixture — no validator extension. New files under evals/cautilus/ need a .agents/surfaces.json source_paths entry or run_slice_closeout blocks on unmatched-surface (pre-commit does NOT catch this; the closeout does). Added evals/cautilus/skill-experiment/** to the prompt-behavior-proof surface.
- Metrics:

### Slice 6: S7: One real cautilus skill-experiment proof run (External/Live)

- Objective: Capture two real claude -p quality transcripts (baseline b01cee6b vs variant 5ded9f3a) in isolated worktrees, extract to input.v1, and run the single authorized cautilus evaluate skill-experiment scorer; record the verdict + planner output in latest.md.
- Why this approach: The empirical proof the whole chain emits a real verdict. Captures via direct claude -p in read-only worktrees (cwd=worktree, reads worktree skill refs) avoided the BLOCKER-2 install-clone mutation hazard.
- Commits: (this commit)
- What changed: NEW charness-artifacts/cautilus/skill-experiment-2026-06-22/{baseline,variant}.transcript.jsonl + input.v1.json + report.json + justification.md; REWROTE charness-artifacts/cautilus/latest.md (skill-experiment verdict, goal: preserve); .agents/surfaces.json (+skill-experiment-*/ derived_path).
- Alternatives rejected:
- Targeted verification: PLANNER (verbatim, read-only): next_action=none, must_ask_before_running=true, run_mode=ask, goal=preserve (hardcoded; authorization = operator one-run approval + transcript justification-log per BLOCKER-4). Both captures clean (is_error=False, haiku-4.5, ~$0.15 total). Extractor cwd-relativized refs. SCORER VERDICT: promotion_recommendation=DISCARD; variant_ran=true, baseline_comparable=true, rubric=pass; source_coverage_delta.gained=[] lost=[] (both covered 6/7); finding severity=note. validate_cautilus_proof + validate_surfaces + check-secrets green; 37 cautilus artifact tests pass.
- Test duplication pressure:
- Critique: n/a within this slice — the load-bearing extractor/runner already passed the S3 fresh-eye critique; S7 executes the proven chain. The honest verdict (discard, not a gamed promote) is itself north-star-aligned.
- Off-goal findings: none
- Lessons carried forward: HONEST RESULT: verdict=discard reflects ZERO source-coverage delta — both arms read the SAME 6 refs. Two capture designs tested: (v1) naming the concept refs lets a capable agent reach them by FILENAME in both arms (no delta); (v2) Read-only pointer-following produced runaway broad exploration. Insight: this disposition improves pointer-DIRECTNESS (reach-via-pointer, prior routing A/B 7/7), which source-coverage (which-files-read) cannot measure. The chain works end-to-end; the lens is orthogonal to this disposition class. API 529 overload made sonnet captures fail; haiku captured cleanly. Install clone ~/.agents/src/charness untouched (d2cf1b75); worktrees removed.
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

Self-verification (what was proven):

- The full chain is built, tested, and proven end-to-end: a real `claude -p`
  stream-json capture → repo-owned extractor → `skill_clone_experiment_input.v1`
  → `run_cautilus_eval.py` wrapper → a real cautilus `evaluate skill-experiment`
  verdict.
- Broad gate GREEN: `run_slice_closeout.py --verification-lock
  --refresh-broad-pytest-proof --base` — 26 verify gates + `run_standing_pytest
  --mode read-only` all PASS; broad-pytest proof recorded.
- The one authorized scorer run returned `promotion_recommendation: discard`
  (variant_ran + baseline_comparable true, rubric pass, source_coverage_delta
  gained=[] lost=[]); recorded verbatim in `charness-artifacts/cautilus/latest.md`.
- Captures used isolated read-only worktrees; install clone
  `~/.agents/src/charness` untouched at `d2cf1b75`; worktrees removed.

Non-claims (honest limits):

- NOT a power-bearing A/B: one single-scenario capture per arm; stochastic
  upstream capture variance is uncontrolled.
- The `discard` reflects ZERO source-coverage delta (both arms read the same six
  refs), NOT that the disposition is bad — source-coverage measures which files
  were read, not pointer-directness (the disposition's actual improvement,
  measured 7/7 by the prior routing blind A/B).
- The built input was validated structurally against the source-read scorer
  contract; the single scorer run is the only end-to-end schema confirmation.
- The runner's claude_code stream-json capture is proven by 25/25 unit tests + a
  real CLI flag smoke; the cautilus A/B used direct `claude -p` quality-task
  captures (not the routing-eval prompt).

Residual risks:

- The eval obligations (7 routed concept refs) did not discriminate this
  disposition class; a future eval needs a no-name-hint task (recorded in
  `latest.md` Follow-ups).
- Carried nit: `findResultEvent`/`findClaudeResultEvent` duplication
  (test-covered; consolidate when next touching the runner).

Early close rationale: all 8 slices landed and the empirical proof (one real cautilus verdict) is recorded ~2h into the 6h box; the goal's defined scope is fully met, and continuing would mean absorbing out-of-scope backlog (#396 / the full sweep) that the Non-Goals forbid.
Early-close report: charness-artifacts/goals/2026-06-22-cautilus-skill-usage-validation-harness-early-close-report.md
Next slice candidate: full multi-scenario Cautilus A/B sweep | decision: user-decision | reason: a separate paid decision beyond the one authorized proof run; deferred to the operator queue until the operator approves the sweep.
Next slice candidate: consolidate findResultEvent/findClaudeResultEvent | decision: defer | reason: carried S3 nit; ~10 duplicated scanner lines, both test-covered, consolidate when the runner is next touched to avoid re-churn.
Next slice candidate: no-name-hint eval task redesign | decision: defer | reason: lets source-coverage discriminate a pointer-directness disposition; recorded in latest.md Follow-ups and not needed for this single proof.
Outcome sufficiency check: sufficient: the chain is proven end-to-end with one real verdict and the broad gate passed; named non-claims explicitly bound what was not proven (no power-bearing A/B; source-coverage orthogonal to this disposition class).

Retro: charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md
Host log probe: skipped: host-log-not-exposed: the retro host-log probe reads codex sqlite/session logs; this Claude Code session's turn and token timing are not exposed to it.
Disposition review: charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md

## User Verification Instructions

- `node --test tests/agent-runtime/extract-skill-experiment-input.test.mjs
  tests/agent-runtime/native.test.mjs` → 25 pass (runner stream-json capture +
  keystone extractor).
- Inspect `charness-artifacts/cautilus/latest.md` (goal: preserve) and
  `charness-artifacts/cautilus/skill-experiment-2026-06-22/report.json` →
  `promotion_recommendation: discard` with the honest zero-coverage-delta reading.
- Re-score deterministically: `python3 scripts/run_cautilus_eval.py --mode
  skill-experiment --justification-log
  charness-artifacts/cautilus/skill-experiment-2026-06-22/justification.md --
  --input charness-artifacts/cautilus/skill-experiment-2026-06-22/input.v1.json
  --output /tmp/recheck.json` → same verdict (deterministic scorer).
- `git -C ~/.agents/src/charness rev-parse --short HEAD` → `d2cf1b75` (install
  clone untouched); `git worktree list` → only the main worktree.

## Auto-Retro

Retro: charness-artifacts/retro/2026-06-22-cautilus-skill-usage-validation-harness-retro.md (session; persisted; recent-lessons refreshed).

Retro dispositions: applied: eval-design rule (source-coverage measures file-set, not pointer-directness; a name-hinted task defeats the pointer mechanism) recorded in `charness-artifacts/cautilus/latest.md` `## Follow-ups` and the bound retro.
Retro dispositions: none — the 529-overload "switch model tier early" lesson is recorded in the bound retro; a transient-API mitigation does not warrant a durable gate change this run.
Retro dispositions: none — the DRY nit (`findResultEvent`/`findClaudeResultEvent`, ~10 lines) is deferred per the S3 reviewer's own "no action this slice" guidance; both copies are test-covered with no drift risk.

Structural follow-up: none — the pre-commit-vs-closeout surface-coverage gap is already enforced by `run_slice_closeout.py` (a convenience pre-commit guard, not a correctness fix); single S5/S7 recurrence, deferred as low-priority.
