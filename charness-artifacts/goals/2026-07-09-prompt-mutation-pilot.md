# Achieve Goal: Prompt mutation testing: witness coverage + demote-ranking pilot

Status: complete
Created: 2026-07-09
Activation: `/goal @charness-artifacts/goals/2026-07-09-prompt-mutation-pilot.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: COMPLETE. All four slices + closeout honesty pass landed.
  Verdicts: bootstrap DETECTED (0/2), workflow NO-OBSERVED-EFFECT (2/2,
  under-witnessed — coverage debt, not demotion), closeout-vocabulary
  NO-OBSERVED-EFFECT (2/2, the single ranked demotion candidate — untainted
  by the disclosed unblinding). Report:
  `charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md`;
  policy: `docs/prompt-mutation-policy.md`. Closeout critique verdict
  CLOSE-AFTER-FIXES with all fixes applied; disposition review PASS after
  one FAIL-fix cycle (#427 relabeled recurs: #415).
- Next action: none — operator decisions queued (demotion proposal
  accept/reject; push) in `## Operator Decision Queue`.
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

Build a prompt-surface mutation pipeline for charness skill prose and prove it
on one pilot skill. The pipeline is a **ranking + scenario-coverage detector,
never a deletion prover**:

1. **Static witness-coverage analysis (zero capture cost).** Split a skill's
   prompt surface (SKILL.md + loaded references) into section-level mutation
   units and map each unit to the deterministic detection channels that could
   witness its removal (outcome assertions in the skill's claim-fidelity eval,
   plus deterministic behavior-trace markers over the captured run). Units with
   no witness are verdict `UNTESTED` — the primary product is this
   scenario-coverage debt list, not compaction.
2. **Live deletion-survival ranking (bounded capture cost).** For witnessed
   units only, generate mutant git refs (unit-removed commits on a throwaway
   ref namespace) and run them as arms through the existing
   `run_skill_efficiency_ab.py` capture harness against a baseline arm.
   Mutants remove the unit from the tree the capture actually resolves —
   **`plugins/charness/skills/<skill>/**` (the installed-plugin mirror)** —
   not only `skills/public/**` (plan-critique blocker F1). Per-unit verdict:
   `DETECTED` (a witness fired differently) or `NO-OBSERVED-EFFECT`
   (survival), reported as a survival rate over N runs, never a binary
   deadness claim.
3. **Demotion candidates, not deletions.** `NO-OBSERVED-EFFECT` output is a
   demote-to-reference proposal artifact. Physical deletion, batch ratchets,
   and the ship-configuration integrated rerun are designed in the policy doc
   but exercised only if the pilot actually yields an accepted demotion batch.

Success = the two offline tools exist with tests, the pilot skill has a checked
witness map, one bounded live pilot ran end-to-end, and a survival/coverage
report artifact exists under `charness-artifacts/prompt-mutation/` with honest
small-N caveats and non-claims.

## Non-Goals

- No physical deletion of any prompt prose in this goal — demotion proposals
  only; deletion stays gated behind real-usage tripwire silence (future work).
- No all-skills rollout; exactly one pilot skill this goal.
- No commit/CI gate: the pipeline is advisory tooling
  (floor-addition-restraint), like the efficiency A/B harness it reuses.
- No cautilus judge-kind grading in the pilot's survival scoring: detection
  channels are deterministic assertions + deterministic trace markers only.
  Judge-kind witnesses are recorded in the witness map schema as a future
  channel but not spent on (repo cautilus ask-before-run contract).
- No trap→tripwire compiler (separate idea from the same design conversation;
  out of scope here).
- No sentence/paragraph granularity in the pilot: section-level units only.

## Boundaries

- External side-effect scope: none approved — no push, no release, no remote
  CI, no issue closes planned by this goal. Commits stay local; the operator
  pushes. If a demotion batch were accepted (unlikely within pilot), applying
  it is a follow-up goal, not this one.
- Live capture spend: real `claude -p` captures via `capture-skill-run.sh`
  on this machine, bounded to **≤ 12 captures total, ≤ 1200s timeout each**.
  Planned shape: **one pilot scenario** (chosen in S2 to maximize causally
  witnessed units), baseline N=2 + up to **4** mutant units × N=2 = 10
  captures, keeping 2 as flake headroom. Failed/timed-out captures consume
  the budget; an arm left at N=1 is reported `INVALID-FOR-VERDICT`, never a
  survival rate. Exceeding the bound requires new operator approval.
- Cautilus contract: no bare `cautilus evaluate`; any evaluator-backed judging
  (excluded from pilot scoring anyway) would go through
  `plan_cautilus_proof.py` + `run_cautilus_eval.py`.
- Mutant refs live in a throwaway namespace (`refs/prompt-mutants/…`); they
  never touch `main` history or the shared install. Construction uses
  **object-database plumbing only** (`git hash-object` / `mktree` /
  `commit-tree` / `update-ref`) — never `checkout`/`add`/`commit` in the
  shared worktree (#258 hygiene; plan-critique F4). The manifest records each
  mutant's **commit SHA**, and cleanup is a separate explicit subcommand run
  only after S3 captures complete, so commits stay reachable during the
  experiment.
- Mutant commits carry a **neutral, uniform commit message** and share the
  baseline commit as parent, so a captured run inspecting `git log` cannot
  read which unit was removed or that it is in an experiment (#423-class
  leak; plan-critique F5).
- Generated-surface sync: if new scripts are plugin-shipped they must follow
  the `scripts/` ↔ `plugins/charness/scripts/` mirror contract
  (implementation-discipline owns sync-before-verify order). Default posture:
  maintainer-side eval tooling, mirrored the same way
  `run_skill_efficiency_ab.py` is.
- Coding slices run in lower-power-model subagents per the repo standing
  request; main loop keeps design, review, synthesis.

## User Acceptance

- Read `charness-artifacts/prompt-mutation/2026-07-09-<pilot>-pilot.md`: it
  names every mutation unit of the pilot skill with a verdict
  (`UNTESTED` / `DETECTED` / `NO-OBSERVED-EFFECT` + survival rate), the
  scenario-coverage debt list, and explicit non-claims.
- Re-run the offline half with zero spend:
  `python3 scripts/generate_prompt_mutants.py --help` and
  `python3 scripts/witness_coverage.py --help` work, and
  `pytest -q <their test files>` passes.
- Confirm no prompt prose was deleted or demoted in this goal
  (`git log --stat` shows tooling + artifacts + tests only, no
  `skills/public/**` prose removal).

## Agent Verification Plan

### Low-Cost Checks

- Unit tests for the splitter (stable unit ids, lossless reassembly, section
  granularity), the mutant generator (ref created, **unit absent from
  `plugins/charness/skills/<skill>/**` in the mutant tree** — the tree the
  capture resolves, F1; SHA recorded in manifest; neutral commit message;
  explicit cleanup subcommand), and witness-coverage verdict logic
  (unwitnessed → `UNTESTED` without any capture).
- Witness map entries require a **causal-path rationale** (the unit owns the
  instruction that produces the witnessed fragment). Run-level sanity
  assertions that fire on any packet (e.g. handoff's `ran-handoff`
  `summary_contains`, which the observation builder emits unconditionally) do
  **not** count as witnesses; units witnessed only by such assertions are
  `UNTESTED` (F2). Sections inside reference bodies whose only deterministic
  signal is file-open (RCF) are `UNTESTED` and land in the debt list.
- A selftest-style refusal mirror: the survival scorer must rank a fixture run
  with a fired witness as `DETECTED` and refuse to score when the baseline
  arm's witnesses did not fire **in both baseline runs** (a baseline whose
  witness never fires cannot detect anything — invalid experiment, not
  survival).
- `run_slice_closeout.py --skip-broad-pytest` at slice boundaries.

### High-Confidence Checks

- The live pilot itself (S3): baseline + witnessed mutant arms through
  `run_skill_efficiency_ab.py`, deterministic grading only, within the capture
  bound. Baseline witness-fire validity check must pass before any mutant
  verdict is read.
- Full broad gate at closeout with the verification lock.

### External Or Live Proof

- None planned (no push/release/live-provider claims). Non-claim: pilot
  verdicts hold for the captured scenario battery on this machine and say
  nothing about other hosts, other scenarios, or judge-witnessed behavior.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| S1 | `generate_prompt_mutants.py`: section-level splitter + manifest + plumbing-built mutant refs (plugin-mirror tree, neutral messages, SHA-recorded, explicit cleanup) | Everything downstream consumes its unit ids and refs | pytest unit tests green; manifest JSON for pilot skill; mutant-tree proof against `plugins/charness/…` path; low test-duplication pressure (new module, own test file) | pending |
| S2 | Witness map schema (causal-path rationale required) + `witness_coverage.py` static verdicts + seeded pilot witness map + **pilot scenario selection** (single scenario maximizing causally witnessed units) | Zero-cost half of the value; decides which mutants are worth capture spend | pytest green; `UNTESTED` debt list for pilot skill checked in; chosen scenario + per-scenario baseline arithmetic recorded; moderate duplication pressure (fixture JSONs — keep small) | pending |
| S3 | Bounded live pilot: one scenario, baseline N=2 + ≤4 witnessed mutant arms × N=2, deterministic scoring; survival report data | The empirical claim of the whole design | results.json + per-unit survival verdicts within ≤12 captures (2 flake headroom); baseline validity (witness fired in both baseline runs) passed before any mutant verdict; N=1 arms marked INVALID-FOR-VERDICT; no new tests (harness reuse) | pending |
| S4 | Report artifact + demotion-policy doc (ratchet, ship-config rerun, tripwire-gated deletion) + closeout | Turns data into the operator-facing deliverable and durable policy | `charness-artifacts/prompt-mutation/` report; policy reference doc; goal closeout gates green | pending |

## Operator Decision Queue

- Decision: accept or reject the ranked demotion proposal
  (`#handoff/closeout-vocabulary` → reference file, per
  `docs/prompt-mutation-policy.md`: ship-config rerun + ratchet + tripwire
  window before any physical change)
  - Owner: operator
  - Why deferred: applying demotions is an explicit non-goal of this pilot
  - Unblock action: say "accept the demotion proposal" to open a follow-up
    goal, or reject and the candidate stays recorded in the report
  - Revisit trigger: next prompt-mutation or handoff-skill work
- Decision: push the local commits (this goal is 6 commits ahead of
  origin/main; no push approved in-goal)
  - Owner: operator
  - Why deferred: external side-effect scope was none-approved by design
  - Unblock action: `git push`, or ask for a pre-push review
  - Revisit trigger: next session pickup

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

- Routing: find-skills -> impl — implementation slices S1/S2/S4 (list_capabilities.py --recommend-for-skill impl also surfaced cautilus as a validation-role tool; deliberately unspent this goal per Boundaries)
- Routing: find-skills -> issue — off-goal findings #426/#427 filed with observed-problem-first bodies (list_capabilities.py --recommend-for-task returned issue)
- Routing: find-skills -> quality — gate cadence and verification lock at closeout (list_capabilities.py --recommend-for-task returned quality)
- Gather: n/a — all context sources are repo-local (no external URL/doc consumed).
- Release: n/a — no version bump or install-manifest edit in this goal.
- Issue closeout: n/a — no issue closed by this goal; #426 was FILED as an off-goal follow-up, not resolved.

## Discuss Before Activation

- Discuss before activation: resolved — **live capture spend**: the operator
  explicitly delegated the full design-and-execute process this session
  ("전체 과정 설계해서 진행해보세요. 당신을 믿습니다") after approving the
  demote-not-delete / witness-scenario / ship-config design in conversation;
  spend is bounded to ≤ 12 real `claude -p` captures (Boundaries) and any
  overage re-asks.
- Discuss before activation: resolved — **cautilus judge spend**: excluded
  from pilot scoring entirely (deterministic assertions + trace markers only),
  honoring the repo's cautilus ask-before-run contract without needing a new
  ask; the witness schema still models judge channels for future use.
- Discuss before activation: resolved — **irreversibility posture**: no prose
  deletion, no demotion application, no push, no issue close in this goal;
  all outputs are additive tooling, tests, and artifacts, so every side effect
  is a local reversible commit.

## Slice Log

### Slice 1: S1 mutant generator

- Objective: Offline splitter + plumbing-built mutant refs against the plugin-mirror tree, with manifest and explicit cleanup
- Why this approach: Everything downstream consumes unit ids and refs; plumbing-only construction and plugin-tree targeting fold plan-critique F1/F4/F5 before any capture spend
- Commits: 213f8986
- What changed: scripts/prompt_mutant_lib.py, scripts/generate_prompt_mutants.py, tests/test_generate_prompt_mutants.py, plugin mirrors, goal artifact
- Alternatives rejected: Rejected checkout-based mutant branches (violates #258 shared-worktree hygiene); rejected skills/public-only mutation (F1: captures resolve the plugin mirror); rejected flat-partition splitting in favor of nested document-outline units with lossless top-level reassembly
- Targeted verification: 26 new tests green (pytest -q tests/test_generate_prompt_mutants.py); ruff clean; run_slice_closeout.py --skip-broad-pytest all PASS; length headroom 78/375/530; no mutant refs in real repo
- Test duplication pressure: New standalone test file for a new module; no sibling-file overlap expected; broad-gate sample deferred to closeout lock
- Critique: Plan-critique F1/F4/F5 folded into implementation and asserted by tests; fresh-eye implementation critique deferred to the S1+S2 offline-tooling bundle boundary (risk boundary = before S3 capture spend)
- Off-goal findings: none
- Lessons carried forward: Coding subagent flagged CRLF round-trip as a latent non-claim (repo markdown is all-LF); nested units overlap parents — S3 arm selection must avoid overlapping unit picks
- Metrics: subagent ~179k tokens, 51 tool uses, ~16m

### Slice 2: S2 witness coverage

- Objective: Static witness-coverage verdict tool + causally-rationalized handoff refresh witness map; pilot scenario decision
- Why this approach: Zero-cost half of the value; decides which mutants earn capture spend. Refresh scenario chosen: 3 deterministic floors vs 1 elsewhere
- Commits: d1c815c5
- What changed: scripts/witness_coverage{,_lib}.py, tests/test_witness_coverage.py, evals/cautilus/handoff-claim-fidelity/witness-map.json, plugin mirrors, goal frame
- Alternatives rejected: Rejected auto-deriving witnesses from spec floors alone (F2: channel existence is not causal sensitivity); rejected full-hash map keys (stale on any edit) for hash-less prefixes with fatal stale/ambiguous resolution; rejected judge-channel scoring (cautilus ask-before-run; modeled but unspent)
- Targeted verification: 39 tests green (13 new + 26 S1 regression); real-repo smoke witnessed=3/untested=30/excluded=2 with all 27 reference-body units UNTESTED unmapped; run_slice_closeout.py --skip-broad-pytest all PASS
- Test duplication pressure: New standalone test file; validate_claim_fidelity_specs/validate_outcome_assertions pass on the new eval-dir file; broad-gate sample deferred to closeout lock
- Critique: Main loop authored the causal analysis; S1+S2 bundle fresh-eye critique is the next action before S3 capture spend (risk boundary)
- Off-goal findings: none
- Lessons carried forward: Witness map schema hard-requires reason on untested/excluded — keeps the debt list honest; S3 budget improves to 8 captures + 4 headroom with only 3 witnessed units
- Metrics: subagent ~143k tokens, 66 tool uses, ~8m

### Slice 3: S3 live pilot

- Objective: 8-capture matrix (baseline f84eb223 N=2 + 3 unit-removed mutant arms N=2) through run_skill_efficiency_ab.py, deterministic survival scoring
- Why this approach: The empirical claim of the whole design; ran only after the S1+S2 bundle critique fixes (baseline decontamination, scorer, identity hardening) landed
- Commits: capture artifacts committed with S4
- What changed: charness-artifacts/efficiency/prompt-mutation-handoff-refresh-pilot/ (preserved bundles, results, report), charness-artifacts/prompt-mutation/ (mutant manifest, ab config, survival+coverage json)
- Alternatives rejected: Rejected HEAD baseline (blueprint contamination); rejected scoring from harness pass_rate alone (combined verdict, no per-witness attribution); streams dropped from committed evidence after verifying trace-digest-only re-score reproduces all verdicts
- Targeted verification: Selftest passed pre-run; baseline validity: all witnesses fired in both baseline runs; verdicts bootstrap=DETECTED(0/2), workflow=NOE(2/2), closeout-vocabulary=NOE(2/2); harness matcher pass_rate independently agrees (0.0/1.0/1.0); budget 8/12, 0 failures, ~52min wall
- Test duplication pressure: No new tests this slice (harness reuse)
- Critique: Bundle critique fixes verified in-run: mutant trees diffed (11-line removals both trees), neutral msg + baseline date confirmed, digest-only refs; refs cleaned post-capture per policy
- Off-goal findings: none
- Lessons carried forward: Mutual redundancy workflow<->closeout-vocabulary confirmed live (the A+B case); NO-OBSERVED-EFFECT on a broad unit reads as under-witnessed, not dead — post-hoc critique-collapse signal on m-workflow
- Metrics: 8 captures, baseline mean 337s/run; m-bootstrap +95% tokens +117% duration

### Slice 4: S4 report and policy

- Objective: Operator-facing pilot report + durable prompt-mutation policy doc; artifact cleanup
- Why this approach: Turns data into the deliverable and locks the demote-never-delete / ship-config / ratchet rules into a repo-owned surface
- Commits: this closeout commit
- What changed: charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md, docs/prompt-mutation-policy.md
- Alternatives rejected: Rejected proposing workflow for demotion despite 2/2 survival (under-witnessed broad owner; filed as coverage debt instead) — only closeout-vocabulary ranked
- Targeted verification: check_doc_links + check-markdown green on both docs; scorer re-run reproducibility check (streams removed) green
- Test duplication pressure: No new tests
- Critique: Final closeout fresh-eye critique next, before status flip
- Off-goal findings: none
- Lessons carried forward: The primary product framing held: 30-unit UNTESTED debt list is the bigger deliverable than the 1 demotion candidate
- Metrics: offline

## Context Sources

- This session's design conversation (2026-07-09): operator approved the
  false-negative posture (UNTESTED vs NO-OBSERVED-EFFECT, demote-not-delete,
  ship-config integrated rerun, batch ratchet) and delegated execution.
- Issue #423 (CLOSED by `7c09a8ce`): capture blinding fix — the pilot's
  representative-run premise depends on it; already landed on main.
- `scripts/agent-runtime/capture-skill-run.sh` and
  `scripts/run_skill_efficiency_ab.py`: the ref-armed capture/compare harness
  this goal reuses instead of rebuilding.
- `evals/cautilus/*/outcome-assertions.json` (achieve/debug/gather/handoff/
  hitl/impl have assertions today): the deterministic witness inventory.
- `charness-artifacts/reference-compaction/slice7-census-reconciliation.md`:
  the capture-proven KEEP/MOVE methodology this generalizes.
- `docs/retro-self-improvement-spec.md`: honesty pattern (available vs
  unavailable, no fabricated metrics) applied here as survival-rate honesty.
- `charness-artifacts/retro/recent-lessons.md`: producer-blind-spot and
  changed-path-surface-map lessons folded into the verification plan.

## Interview Decisions

- Mode — family: artifact-only draft vs implementation-continuation; chosen:
  **implementation-continuation** (operator prose names it: "전체 과정
  설계해서 진행해보세요"); rejected artifact-only because the delegation was
  explicit. single-point: operator instruction this session.
- Pilot skill — family: any skill with a claim-fidelity eval; chosen:
  **handoff** (capture path proven live in #410 Slice 9; has
  outcome-assertions.json; small prompt surface). Rejected: debug (needs a
  planted-bug fixture — costlier per capture), setup-greenfield (needs
  `--run-cwd` sandbox orchestration — more moving parts for a pilot).
  axis: skill-family — the tooling must stay skill-generic; only the pilot
  target is fixed, and selection criteria are recorded so the next skill is a
  config change, not a redesign.
- Mutation granularity — family: sentence / paragraph / section / whole-file;
  chosen: **section** (matches how meaning clusters and how consumers load
  prose; keeps interaction effects inside units; keeps arm count affordable).
  axis: granularity is a real design axis; the splitter takes it as a
  parameter with only `section` implemented in the pilot.
- Runs per arm — family: N=1 anecdote / N=2 / N≥4; chosen: **N=2** with
  survival reported as rate + explicit small-N caveat (never binary deadness).
  Rejected N≥4 for spend; rejected N=1 because stochastic runs make single
  observations uninterpretable. single-point: pilot cost bound.
- Detection channels — family: outcome assertions only / + trace markers /
  + judge; chosen: **deterministic assertions + deterministic trace markers**
  (handoff has 1 deterministic assertion; trace markers over stream.jsonl and
  the observed packet widen free coverage). Judge channel schema-modeled but
  unspent. axis: detection-channel is a declared schema axis.
- Host — captures run the Claude host (`claude -p`) because that is what
  `capture-skill-run.sh` drives today. axis: host — Codex capture parity is a
  known repo axis and an explicit non-claim here, not a hidden default.

## Plan Critique Findings

Bounded fresh-eye plan critique executed 2026-07-09 (delegated read-only
subagent `aab2735bdd5780cec`, shared parent worktree, per repo standing
delegation). Verdict: ACTIVATE-AFTER-FIXES; all fixes folded before
activation:

- **F1 BLOCKER (folded → Goal, Boundaries, Low-Cost Checks, S1):** captures
  resolve the skill from the installed-plugin mirror
  (`capture-skill-run.sh` sets `installPath = <worktree>/plugins/charness`),
  so mutants that only touch `skills/public/**` silently test the unmutated
  skill and every unit reports a false `NO-OBSERVED-EFFECT`. Mutants now
  target `plugins/charness/skills/<skill>/**` and S1's round-trip test
  asserts absence from that path.
- **F2 SHOULD-FIX (folded → Low-Cost Checks):** handoff's single
  deterministic assertion (`ran-handoff` `summary_contains`) is emitted
  unconditionally by the observation builder — zero detection power. Witness
  map entries now require a causal-path rationale; sanity-only-witnessed
  units are `UNTESTED`; RCF file-open floors do not witness sections inside
  reference bodies.
- **F3 SHOULD-FIX (folded → Boundaries, S2/S3):** witnessed units span
  scenarios and a mutant arm is only interpretable against a same-scenario
  baseline; pilot pinned to one scenario chosen in S2, baseline arithmetic
  recorded before S3.
- **F4 SHOULD-FIX (folded → Boundaries, S1):** naive mutant construction in
  the shared worktree violates #258 hygiene; plumbing-only construction,
  SHA-recorded manifest, cleanup as a separate post-S3 subcommand.
- **F5 SHOULD-FIX (folded → Boundaries):** a descriptive mutant commit
  message is a #423-class identity leak readable via `git log` inside the
  capture; neutral uniform messages, baseline commit as parent.
- **F6 SHOULD-FIX (folded → Boundaries, S3):** the ≤12 bound had zero flake
  headroom while the harness silently degrades to n-1; plan now 10 planned +
  2 headroom, failures consume budget, N=1 arms `INVALID-FOR-VERDICT`.
- **Over-worry (raised, not folded):** mutant-ref arms mechanically work
  through the existing harness (worktree add accepts any commit-ish; arms are
  `{name, ref}`; witness definitions resolve baseline-side from the main repo
  at HEAD; judge-kind assertions auto-SKIP without `--judge-cmd`), and the
  mirror contract for new scripts matches how `run_skill_efficiency_ab.py`
  ships today — no contract violation beyond the folded items.

## Off-Goal Findings

- #426 filed (commit-diff unblinding: 4/6 mutant captures identified the
  removed section via `git show` on the snapshot commit; fix direction =
  symmetric parentless snapshot commits for all arms). Surfaced by the final
  closeout fresh-eye critique; report + policy doc already disclose it.

## Final Verification

- Self-verification: 4 slices + honesty pass landed as 6 local commits; 58
  pipeline tests green; verification lock recorded at closeout
  (`run_slice_closeout.py --verification-lock`, broad pytest included);
  survival.json regenerates byte-consistently from the committed bundles;
  witness-coverage counts (3/30/2) reproduce live; no `skills/public/**`
  prose deleted (checked across all goal commits); no leftover
  `refs/prompt-mutants` refs or mktemp run bases.
- Residual risks / non-claims: N=2 survival rates rank, not estimate;
  verdicts hold for the refresh scenario on this Claude host only;
  m-workflow's survival attribution is unblinding-confounded (disclosed in
  the report; #426); prose quality and guardrail compliance unscored (judge
  channels unspent); trace-marker fires carry the trace-digest truncation
  caveat now that streams are dropped.
- Live/high-cost proof: the 8-capture matrix itself (S3); no push, release,
  or provider claim made.

Retro: charness-artifacts/retro/2026-07-09-session-retro-prompt-mutation-pilot-goal.md
Host log probe: charness-artifacts/goals/2026-07-09-prompt-mutation-pilot-host-log-probe.json
Disposition review: charness-artifacts/critique/2026-07-09-prompt-mutation-pilot-disposition-review.md

## User Verification Instructions

- Read the pilot report:
  `charness-artifacts/prompt-mutation/2026-07-09-handoff-refresh-pilot.md`
  (verdict table, findings, unblinding disclosure, coverage debt,
  non-claims).
- Zero-spend reproduction: `python3 scripts/witness_coverage.py --repo-root .
  --skill handoff --scenario refresh --markdown` (expect 3 witnessed / 30
  untested / 2 excluded) and the scorer command in the report's Method
  section against the committed bundles (expect identical verdicts).
- Tests: `pytest -q tests/test_generate_prompt_mutants.py
  tests/test_witness_coverage.py tests/test_score_prompt_mutation_survival.py`
  (expect 58 passed).
- Confirm no skill prose changed: `git log origin/main..HEAD --stat --
  skills/public plugins/charness/skills` shows no deletions.

## Auto-Retro

Retro dispositions: applied: docs/prompt-mutation-policy.md stream-drop re-score rule + commit-diff blinding caveat (commit 5ce78e9d); applied: docs/prompt-mutation-policy.md "red-team the observer once, up front" floor (channel enumeration at design time — the lesson behind the three blinding iterations, committed with this closeout); issue #426 (novel: mutant snapshot commits are diffable against their baseline parent — symmetric parentless snapshots for all arms); issue #427 (recurs: #415 — textual mention counted as genuine action, the same matcher-honesty class as the closed doc-open-floor instance; lineage noted on the issue)
Structural follow-up: issue #427 (recurs: #415 — mention-vs-execution matching is a transcript-scorer class defect; the applied re-score rule is scoped to this pipeline, and the efficiency-A/B sibling named in the retro is dispositioned none-for-now because its committed reports derive from committed results.json, so the trap binds only if a future claim cites pruned evidence)
