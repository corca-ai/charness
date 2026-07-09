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
surviving sections are **mutually redundant for the observed floor** —
cleanly proven in the closeout-vocabulary direction, confounded by
unblinding in the workflow direction (finding 2) — which is exactly the A+B
interaction case the ship-configuration integrated rerun exists to catch.
Static coverage found **30 UNTESTED units** (scenario coverage debt), the
pipeline's primary product.

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
| `#handoff/bootstrap` | **DETECTED** | 0/2 | planner marker [F,F]; RCF spill-targets [F,F] |
| `#handoff/workflow` | **NO-OBSERVED-EFFECT** | 2/2 | RSF kept [T,T]; RSF non-claims [T,T] |
| `#handoff/closeout-vocabulary` | **NO-OBSERVED-EFFECT** | 2/2 | RSF kept [T,T]; RSF non-claims [T,T] |

The table is regenerated from the committed bundles (trace-digest only). At
scoring time, with streams still on disk, the bootstrap planner marker read
[T,F]: the run-0 "fire" existed only in the since-dropped `stream.jsonl` and
does not correspond to any planner *execution* in the committed trace-digest
(every genuine planner run in this pilot appears untruncated as a step-1 Bash
call) — it was most plausibly a mention, not a run. The DETECTED verdict is
unaffected either way (RCF [F,F] is fully backed by committed packets).

The harness's own combined claim-matcher pass_rate independently agrees:
baseline 1.0, m-bootstrap 0.0, m-workflow 1.0, m-closeout 1.0.

## Findings

1. **Bootstrap is load-bearing.** With the section removed, the committed
   trace-digests show no planner execution in either mutant run and
   `spill-targets.md` was never opened (RCF failed both runs), while both
   baseline runs open it via the planner chain. Removal also cost +95% total
   tokens and +117% wall-clock (mean) — the flailing is visible in process
   metrics too. An earlier draft claimed run 0 "found and ran the planner";
   that claim was stream-sourced, is contradicted by the committed
   trace-digest, and is withdrawn (see Verdicts note).
2. **workflow ↔ closeout-vocabulary are mutually redundant for the token
   floor — cleanly proven in one direction, confounded in the other.**
   Workflow step 7 spells `Refresh kept:` / `Refresh non-claims:` verbatim,
   and the Closeout Vocabulary section defines the same tokens. The
   m-closeout direction is clean: neither m-closeout run inspected the
   mutant diff (run 0 ran `git show --stat` only, run 1 never looked), so
   its 2/2 survival is genuinely explained by the still-loaded step 7. The
   m-workflow direction is **confounded by unblinding**: both m-workflow
   runs diffed the snapshot commit and read the full removed section —
   including step 7's verbatim token lines — before closing, so their token
   emission may be diff-readback rather than Closeout Vocabulary redundancy.
   Removing both units was **not tested** (single-unit arms only) and is
   presumed breaking: any demotion batch touching either section MUST prove
   the combined post-demotion state via the ship-configuration rerun.
3. **`NO-OBSERVED-EFFECT` on a broad unit means under-witnessed, not dead.**
   The workflow section owns steps 1–6 beyond the tokens; nothing
   deterministic witnesses them. Post-hoc (not pre-registered, observational
   only): mutant-workflow runs mention "critique" 3/14 times in the stream
   vs ~50 in a baseline run — consistent with step 6 (bounded
   misunderstanding critique) silently disappearing — and ran leaner
   (−23.5% tokens), a classic "leaner can mean did less" signal. The
   3/14-vs-50 magnitudes were stream-sourced and dropped with the streams;
   the committed digests and transcripts still support the direction
   (baseline runs mention "critique" 4 and 2 times, m-workflow runs 0 and
   0). The right response for `workflow` is **new witnesses, not demotion**.

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
- **Unblinding occurred and is disclosed.** Neutral commit messages were not
  enough: 4 of 6 mutant runs diffed the `chore: snapshot` commit and
  identified the removed section by name (both m-bootstrap runs, both
  m-workflow runs — the m-workflow runs read the removed diff including the
  verbatim token lines, confounding that arm's survival attribution; see
  finding 2). The ranked demotion candidate is untainted: m-closeout run 0
  saw file names only (`--stat`), run 1 never inspected the commit. Every
  future run needs a stronger blind — e.g. symmetric parentless snapshot
  commits for all arms (baseline included) so no arm has a diffable history;
  filed as a follow-up issue.
- **Other blinding residuals.** `refresh.spec.json` itself (in-tree at the
  baseline ref) names the tokens; a run reading the eval dir could recover
  them — pre-existing channel, not observed in any transcript this pilot.
  The worktree shares the main repo's refs, so `refs/prompt-mutants/*`
  (digest-only) are enumerable in principle.
- **trace-digest truncation.** The committed `survival.json` is regenerated
  from the committed bundles (trace-digest only) and reproduces every
  verdict; the bootstrap trace-marker rows carry the honest truncation
  caveat because the stream fallback is no longer on disk. The
  scoring-time stream-based fire pattern differed on one row (see Verdicts
  note) and that difference is withdrawn rather than relied on.

## Budget

8 of ≤12 captures spent; 0 failures; no re-runs needed. Baseline mean
duration 337s/run; the whole matrix ran ~52 minutes wall-clock.
