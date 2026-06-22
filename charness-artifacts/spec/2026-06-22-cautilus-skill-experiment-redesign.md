# Spec draft — Cautilus skill-experiment A/B harness, redesigned

Status: draft (execute after compact)
Created: 2026-06-22
Supersedes the capture half of: `charness-artifacts/goals/2026-06-22-cautilus-skill-usage-validation-harness.md`
(complete) and its `charness-artifacts/cautilus/skill-experiment-2026-06-22/corrected-capture-plan.md`.

This file is self-contained on purpose: a post-compaction context that has lost the
conversation must be able to execute faithfully from here alone.

## Why this redesign (what the first attempt got wrong)

The first run shipped a working chain but a flawed design, found by operator review:

1. **Reinvented cautilus's A/B machinery.** I hand-rolled `git worktree add` and a
   bespoke stdout-capture runner, not knowing cautilus already provides the A/B
   host-side commands. Root cause: the prior goal's Boundaries banned
   `cautilus --help` ("read source, don't trust prose"), an over-correction that
   fused the repo's *"never bare `cautilus evaluate`"* run-safety rule with
   BLOCKER-1's *"prose was inverted, read source"* lesson. So I read ONE scorer
   file narrowly and never saw the command surface. Lesson: `--help` is the
   binary's own accurate index (no side effects, not a gated run) — survey the CLI
   surface first; verify *behavior* in source; never *run* gated evals unguarded.
2. **Leaked the answer into the capture task.** The capture prompt named the
   obligation concepts, whose names equal the reference filenames, so the agent
   reached refs by filename in BOTH arms → zero source-coverage delta → an
   uninformative `discard`.
3. **Used brittle transcript-grep as evidence.** `collectSourceRefs` greps
   `tool_use` file_paths from the parent stdout only. It misses the subagent log
   tree, cannot tell "opened" from "actually used", and counts exploration noise.
   cautilus's contract explicitly says raw-transcript parsing is NOT product
   evidence — the host should produce *structured* evidence.

## Ground truth verified this session (do not re-discover)

- **cautilus skill-experiment is a deterministic scorer only.** Contract:
  `/home/hwidong/codes/cautilus/docs/contracts/skill-clone-experiment.md` — "starts
  after a host-owned runner has already executed baseline and variant; does not
  install skills, call an LLM, or parse raw host logs." Scorer source:
  `internal/runtime/skill_clone_experiment.go` (181ebef7). Recommendation rules:
  promote iff variant adds declared source coverage OR newly-matched rubric phrases,
  AND baseline comparable, isolation proven (`productionSkillTouched:false`
  declared), no lost coverage, no still-missing required/rubric.
- **cautilus DOES provide the A/B host-side commands** (all confirmed via source +
  `--help`):
  - `cautilus evaluate comparison prepare --repo-root . --baseline-ref <X>
    [--candidate-ref <Y> | --use-current-candidate] --output-dir <dir>` →
    `internal/app/remaining_commands.go:39`; creates `baseline/` + `candidate/`
    **detached git worktrees** (`createDetachedWorktree` = `git worktree add
    --detach`) and prints both paths + next-step command hints. No LLM, no scoring.
  - `cautilus evaluate review variants --repo-root . --workspace <dir>
    [--prompt-file --schema-file] --output-dir <dir>` →
    `remaining_commands.go:341`; **runs configured variants (tool/model/backend)
    against a workspace and captures each output** → `cautilus.review_variant_result.v1`
    + a `review_summary.v1`. cautilus's own `docs/guides/evaluation-process.md:174`
    says a repo runner wrapper "should delegate to `cautilus evaluate review
    variants` and stay a thin fanout shim."
- **Claude Code always logs every tool call, incl. subagents.** Parent:
  `~/.claude/projects/<proj>/<session>.jsonl` (all main-agent tool_use). Each
  subagent: `<proj>/<session>/subagents/agent-*.jsonl` (`isSidechain:true`, full
  tool_use incl. nested spawns). Verified: 212 local sessions have a `subagents/`
  dir; a sample subagent file carried `Read/Bash/Agent` tool_use with file paths.
  → the full evidence is on disk regardless of stdout.
- **`/charness:quality` resolves SKILL_DIR to the INSTALLED plugin clone**
  (`~/.agents/src/charness`, currently `d2cf1b75`), NOT a repo worktree (prior
  B-smoke gotcha). This is the central capture-isolation problem (see Decision D3).
- charness currently DISABLES review-learning / `evaluate live` / Agent
  orchestration; the wrapper `scripts/run_cautilus_eval.py` allows only
  fixture/observation/skill-experiment. `comparison prepare` is NOT in the disabled
  list (it is LLM-free worktree infra).

## Operator decisions (locked this session)

- **D1 — lift the `review variants` seal.** Operator: cautilus is mature enough.
  `evaluate review variants` becomes the native runner; charness's
  `run-local-eval-test.mjs` becomes a thin delegating shim.
- **D2 — evidence is agent-produced, not grep.** The tool-call → "sources used"
  analysis is done by an agent (the coding-agent runner self-reporting, and/or a
  cheap analysis agent over the session-log tree), NOT by a deterministic
  transcript grep. The brittle `collectSourceRefs` extractor is retired.
- **D3 — capture as a real user: literally `/charness:quality`, nothing else.** No
  hand-written scaffolding prompt. The arm-under-test is the *installed* skill
  version, so each arm must install its own version in isolation (see Open Q1).

## Redesigned pipeline

1. **Prepare arms** — `cautilus evaluate comparison prepare --baseline-ref
   5ded9f3a^ --candidate-ref 5ded9f3a` → `baseline/` + `candidate/` worktrees.
   (Replaces hand-rolled `git worktree add`.)
2. **Make each arm's skill the installed one (Open Q1).** Per arm, build/install
   that worktree's plugin export into an ISOLATED `CLAUDE_CONFIG_DIR` so
   `/charness:quality` resolves to that arm's version without mutating the shared
   `~/.agents/src/charness`. (Avoids the #258-class corruption BLOCKER-2 warned of.)
3. **Run as a real user** — `claude -p "/charness:quality"` (bare) per arm, with the
   arm's isolated config. Broad permissions (the real skill needs Bash/Agent/etc.);
   it WILL spawn subagents and run gates.
4. **Produce structured evidence with an agent (D2).** Either the runner
   self-reports "sources consulted + used-for", or an analysis agent reads the full
   session-log tree (parent + `subagents/*.jsonl`) and emits structured
   `output.sourceRefs` + a used-vs-opened judgment per arm. This is the host's
   evidence; cautilus does not parse logs.
5. **Score** — build `skill_clone_experiment_input.v1` from the two arms' structured
   outputs (the `buildSkillCloneExperimentInput` builder + spec obligations can be
   reused) → `cautilus evaluate skill-experiment` via the wrapper → verdict.

## Concrete charness changes (file-level)

- `scripts/run_cautilus_eval.py`: add `review-variants` to allowed `--mode`
  (and decide `comparison-prepare` is LLM-free infra → may bypass the planner gate).
- `skills/public/quality/references/cautilus-on-demand.md`: replace the
  "review-learning disabled" stance for `review variants`; define its planner /
  justification rules. (quality-contract change → route through `quality`.)
- `scripts/agent-runtime/run-local-eval-test.mjs`: reduce to a thin shim that
  delegates to `cautilus evaluate review variants` (drop bespoke runtime semantics).
  KEEP the S2 stream-json capability only if still needed after the shim.
- Retire `scripts/agent-runtime/extract-skill-experiment-input.mjs`'s grep core
  (D2). Keep `buildSkillCloneExperimentInput` (the scorer-shaped builder + its
  validation) — that part is still correct and reusable. Replace `collectSourceRefs`
  with the agent-produced evidence ingestion. Update its tests + the JS mutation
  pool baselines accordingly.
- `evals/cautilus/skill-experiment/`: regenerate `capture-prompt.md` to be literally
  `/charness:quality` (or remove it — there is no scaffolding prompt anymore);
  keep `spec.json` obligations but make `taskPacket.summary` generic.
- Update `charness-artifacts/cautilus/latest.md` after the corrected run; note the
  first run's `discard` was a design artifact, superseded.

## Open questions — RESOLVED this session (empirical + source-grounded)

All three open questions are settled. Operator also confirmed: Q1 = isolated (yes).

- **Q1 — isolated per-arm install — RESOLVED (approach (a), empirically proven).**
  `corca-charness` is a **directory-source** marketplace
  (`~/.claude/plugins/known_marketplaces.json` → `source.path:
  ~/.agents/src/charness`); for directory sources Claude loads the plugin
  **directly from the source dir** (`plugins/charness`), which is exactly why
  editing the shared clone is the #258 hazard. Isolation recipe (verified):
  per-arm `CLAUDE_CONFIG_DIR` containing copied `~/.claude/.credentials.json`
  (OAuth; `apiKeySource:none`) + `plugins/known_marketplaces.json` pointing
  `corca-charness` `source.path`/`installLocation` at the arm's worktree +
  `plugins/installed_plugins.json` listing `charness@corca-charness`. PROOF: a
  trivial `claude -p` with such a config reported
  `init.plugins == [{name:charness, path:<worktree>/plugins/charness,
  source:charness@corca-charness}]` and exposed `charness:quality` — resolved to
  the worktree, NOT the shared clone; shared clone stayed `d2cf1b75`/clean.
  **A/B design:** vary ONLY the installed skill version per arm; fix `cwd` to ONE
  shared review workspace so the only difference is the SKILL (the first attempt's
  confound was the opposite: same installed skill, differing repo cwd). The
  quality skill reads its references via `$SKILL_DIR/references/*` = the per-arm
  installed plugin, so the measured `sourceRefs` track the skill version, not cwd.
- **Q2 — does `claude -p "/charness:quality"` invoke the skill headless? — YES
  (empirically proven).** A bounded probe showed `charness:quality` is a
  registered slash command and the run drove `Skill`→`Bash`→`Agent`→
  `AskUserQuestion` tool calls (the skill loaded and started its real flow; the
  first `Skill` call is `find-skills`, correct per CLAUDE.md). Runner shape =
  cautilus `executor_variants` + `cautilus evaluate review variants`:
  `handleReviewVariants` merely renders the variant `command_template`
  (placeholders `{candidate_repo} {prompt_file} {schema_file} {output_file}
  {variant_id} {output_under_test}`) and runs it via `runShellCommand` with a
  timeout + a `{output_file}.stderr` companion + runDir. The `--tools ""`/verdict
  convention in `examples/adapter.example.yaml` is only the review-judge example,
  NOT enforced — the template can run a tools-on capture. Model the charness
  wrapper on cautilus's checked-in `scripts/agent-runtime/run-review-variant.sh`.
- **Q3 — review-variants vs bare `/charness:quality` — RESOLVED.** Because
  `command_template` is arbitrary, `evaluate review variants` CAN carry the bare
  capture: `{prompt_file}` holds literally `/charness:quality` (D3), and the
  template runs `claude -p ... < {prompt_file}` with the arm's isolated
  `CLAUDE_CONFIG_DIR` + full tools. The two arms are two `executor_variants`
  differing only by which arm config dir they bind.

## NEW execution constraints discovered (from the probe — must honor)

- **Capture needs FULL tools + a permissive mode.** The probe used
  `--allowedTools "Read"` under `permissionMode:dontAsk`, which DENIED the skill's
  Bash → the quality flow never bootstrapped/routed (it asked how to proceed). A
  real-user capture must let Bash/Agent/gates run (representative permissive
  setup, e.g. bypass-permissions), so the routing-to-references actually happens.
- **Capture MUST persist sessions.** `--no-session-persistence` left only a
  subagent `*.meta.json` (no `*.jsonl`). D2's evidence (analysis agent over the
  session-log tree: parent + `subagents/*.jsonl`) requires those jsonl trees on
  disk — so persist the session and VERIFY subagent `*.jsonl` were written before
  trusting the evidence step.
- **Contain side effects.** Under a permissive capture, set `cwd` to a throwaway
  worktree + isolated config so any gate writes stay contained; never the shared
  install clone.
- **D2 evidence path = analysis agent over the session-log tree (path b).**
  Self-report (path a) is rejected: it would require appending instructions to the
  prompt, violating D3 ("literally `/charness:quality`, nothing else"). The bare
  capture stays pure; a SEPARATE Read-only analysis agent reads parent +
  `subagents/*.jsonl`, emits structured `output.sourceRefs` + an opened-vs-used
  judgment per arm.

## Build order (deferred LLM spend; reproducible before the expensive run)

1. (done) Record resolutions in this spec; commit.
2. Build checked-in harness, deterministic, no LLM spend: per-arm setup
   (`comparison prepare` + isolated config) + capture wrapper (full tools, session
   persistence, throwaway worktree cwd) + the named cautilus adapter
   (`.agents/cautilus-adapters/skill-experiment.yaml`, two arm `executor_variants`)
   + `run_cautilus_eval.py` `review-variants` mode + eval `capture-prompt.md` =
   `/charness:quality` + generic `spec.json` summary + extractor refactor (retire
   grep `collectSourceRefs`, keep `buildSkillCloneExperimentInput`, ingest
   agent-produced evidence) + tests/mutation-baseline re-base + `cautilus-on-demand.md`
   (route through `quality`). Sync → deterministic gates → commit.
3. Run the corrected capture via the harness (the expensive real runs); inspect
   the baseline-vs-candidate `sourceRefs` delta BEFORE any scorer run.
4. Gate the one `skill-experiment` scorer run (`plan_cautilus_proof.py`; operator GO).
5. Record verdict, update `charness-artifacts/cautilus/latest.md`, retro, closeout.

## Verification plan

- Cheap: `--help` survey recorded; Open Q1/Q2 empirically settled (1 bounded run
  each) before building.
- The corrected capture shows a REAL baseline-vs-variant source-coverage delta
  (variant reaches a pointer-routed ref the baseline cannot) — the signal the first
  run lacked.
- One operator-gated `skill-experiment` scorer run on the corrected arms; record
  the honest verdict.
- Repo gates green (the quality-contract changes route through `quality`; the JS
  mutation baselines re-based for any agent-runtime edits).

## Out of scope / non-claims

- Not the full multi-scenario sweep (still an operator decision).
- This is a redesign of the *capture/evidence* half; the scorer contract is
  unchanged and correct.
