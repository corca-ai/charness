# Prompt-Mutation Pilot: handoff / refresh scenario

Date: 2026-07-09
Goal: [2026-07-09-prompt-mutation-pilot.md](../goals/2026-07-09-prompt-mutation-pilot.md)
Policy: [prompt-mutation-policy.md](../../docs/prompt-mutation-policy.md)
Raw evidence:
[survival.json](./2026-07-09-handoff-refresh-survival.json) ·
[coverage.json](./2026-07-09-handoff-refresh-coverage.json) ·
[mutant manifest](./2026-07-09-handoff-refresh-mutants.json) ·
[A/B config](./2026-07-09-handoff-refresh-ab-config.json) ·
`charness-artifacts/efficiency/prompt-mutation-handoff-refresh-pilot/`

## TL;DR

Eight real captures (baseline N=2 + three section-removed mutants N=2, budget
8/12) produced one `DETECTED`, two `NO-OBSERVED-EFFECT`, and a live
confirmation of the design premise this pipeline was built on: the two
surviving sections are **mutually redundant for the observed floor** — each
survives alone because the other still spells the refresh tokens — which is
exactly the A+B interaction case the ship-configuration integrated rerun
exists to catch. Static coverage found **30 UNTESTED units** (scenario
coverage debt), the pipeline's primary product.

## Method

- Units: section-level mutation units over the installed-plugin tree
  (`plugins/charness/skills/handoff/**`, the tree captures resolve).
- Baseline: `f84eb223` (pre-S1) — chosen so no captured worktree contains the
  experiment's own blueprint (witness map, goal artifact, pipeline commit
  messages). Handoff surfaces are byte-identical to HEAD at that ref.
- Mutants: unit-removed commits built with git plumbing only, neutral
  `chore: snapshot` messages, digest-only ref leaves, baseline committer
  date; parent = baseline.
- Scenario: `refresh.spec.json` (chosen for maximal deterministic floors).
- Witnesses (pre-registered in
  [witness-map.json](../../evals/cautilus/handoff-claim-fidelity/witness-map.json),
  causal-path rationale required): RCF `spill-targets.md`, RSF
  `Refresh kept:` / `Refresh non-claims:`, trace marker
  `plan_handoff_run.py`.
- Scoring: deterministic only (`score_prompt_mutation_survival.py`);
  baseline-validity check passed (all witnesses fired in both baseline runs);
  no cautilus judge spend.

## Verdicts

| Unit (SKILL.md section) | Verdict | Survival | Witness fire pattern (per run) |
| --- | --- | --- | --- |
| `#handoff/bootstrap` | **DETECTED** | 0/2 | planner marker [T,F]; RCF spill-targets [F,F] |
| `#handoff/workflow` | **NO-OBSERVED-EFFECT** | 2/2 | RSF kept [T,T]; RSF non-claims [T,T] |
| `#handoff/closeout-vocabulary` | **NO-OBSERVED-EFFECT** | 2/2 | RSF kept [T,T]; RSF non-claims [T,T] |

The harness's own combined claim-matcher pass_rate independently agrees:
baseline 1.0, m-bootstrap 0.0, m-workflow 1.0, m-closeout 1.0.

## Findings

1. **Bootstrap is load-bearing, with a clean causal confirmation.** In
   mutant run 0 the agent still *found and ran* the planner (genuine
   discovery redundancy — the trace marker fired), and the planner output
   named `spill-targets.md`; but the "Open the listed reads" follow-through
   instruction lived in the removed section, and the read never happened.
   Removal also cost +95% total tokens and +117% wall-clock (mean) — the
   flailing is visible in process metrics too.
2. **workflow ↔ closeout-vocabulary are mutually redundant for the token
   floor.** Workflow step 7 spells `Refresh kept:` / `Refresh non-claims:`
   verbatim, and the Closeout Vocabulary section defines the same tokens;
   removing either alone leaves the tokens emitted in both runs. Removing
   both was **not tested** (single-unit arms only) and is presumed breaking:
   any demotion batch touching either section MUST prove the combined
   post-demotion state via the ship-configuration rerun.
3. **`NO-OBSERVED-EFFECT` on a broad unit means under-witnessed, not dead.**
   The workflow section owns steps 1–6 beyond the tokens; nothing
   deterministic witnesses them. Post-hoc (not pre-registered, observational
   only): mutant-workflow runs mention "critique" 3/14 times in the stream
   vs ~50 in a baseline run — consistent with step 6 (bounded
   misunderstanding critique) silently disappearing — and ran leaner
   (−23.5% tokens), a classic "leaner can mean did less" signal. The right
   response for `workflow` is **new witnesses, not demotion**.

## Ranked Demotion Candidate

- **`#handoff/closeout-vocabulary` (rank 1, the only proposal).** Narrow
  unit whose entire observable job (token definitions) is duplicated
  verbatim by Workflow step 7; survived 2/2 with all witnesses firing.
  Proposal per policy: demote to a reference file (never delete), in a batch
  of k≤2, gated by the ship-configuration integrated rerun (which must keep
  the tokens firing with the demotion applied) and a real-usage tripwire
  window. NOT applied in this goal (non-goal).
- `#handoff/workflow`: survived but **not proposed** — under-witnessed broad
  owner with observational evidence of undetected behavior change. Filed as
  coverage debt instead.

## Scenario Coverage Debt (primary product)

30 units are `UNTESTED` for the refresh scenario — see
[coverage.json](./2026-07-09-handoff-refresh-coverage.json) for the full
list with reasons. Structure of the debt:

- all 27 reference-body units (`references/*.md`): RCF floors prove
  file-open only; nothing observes content use.
- `#handoff/output-shape`: the only conceivable marker (artifact headings)
  pre-exists in the artifact — zero detection power.
- `#handoff/guardrails`: judge-channel candidate only (unspent).
- `#handoff/references`: link list, planner-driven opens.
- Plus the under-witnessing of `#handoff/workflow` steps 1–6 (finding 3),
  which the static counts record as "witnessed" — the witnessed/untested
  boundary is per-unit, and a witnessed unit can still be mostly unobserved.

## Non-Claims

- **N=2.** Survival rates over two runs rank candidates; they are not
  stability estimates. A witness that fails 1-in-5 runs would likely be
  missed.
- **One scenario, one host.** Verdicts hold for the refresh scenario battery
  on this machine (Claude host via `capture-skill-run.sh`); nothing is
  claimed about pickup/chunked-routing scenarios, Codex, or other repos.
- **Deterministic channels only.** Prose quality, guardrail compliance, and
  critique depth were not scored (judge channels unspent per the cautilus
  ask-before-run contract). The critique-collapse observation in finding 3
  is post-hoc and unregistered.
- **Known blinding residuals.** `refresh.spec.json` itself (in-tree at the
  baseline ref) names the tokens; a run reading the eval dir could recover
  them — pre-existing channel, observed in no transcript this pilot. The
  worktree shares the main repo's refs, so `refs/prompt-mutants/*`
  (digest-only) are enumerable in principle.
- **trace-digest truncation.** Trace markers were scored with the
  `stream.jsonl` fallback available at scoring time; a re-score with streams
  removed reproduced every verdict from `trace-digest.jsonl` alone, so the
  160-char truncation caveat did not bind and the streams (2.6M) are not
  committed with the preserved bundles.

## Budget

8 of ≤12 captures spent; 0 failures; no re-runs needed. Baseline mean
duration 337s/run; the whole matrix ran ~52 minutes wall-clock.
