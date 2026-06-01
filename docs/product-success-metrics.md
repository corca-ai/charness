# Product Success Criteria And Metrics

This document defines the current Charness success baseline for issues
[#184](https://github.com/corca-ai/charness/issues/184) and
[#185](https://github.com/corca-ai/charness/issues/185).

Source note: both issues came from the 2026-05-20 Daily Scrum Slack thread
`slack://C05J5LTFSCU/1778805288.184149`. This session could not re-fetch that
private source because the local `ceal` binary was unavailable and the issue
record did not include a Slack web URL usable by the checked-in gather-slack
wrapper. The GitHub issue bodies and current repo docs are the available
working evidence for this baseline. Human agreement is still required before
treating numeric targets, product prioritization, or runtime capture activation
as final.

## One-Page Summary

Charness succeeds when a Claude Code or Codex operator can start from a normal
repo task and get a repeatable product-development workflow: the right skill is
selected, relevant durable context is loaded, code or docs are changed in the
right phase order, validation is honest, review state is preserved, and the next
session can continue without rediscovering the same facts.

The primary users are:

- maintainers evolving Charness itself
- agents operating inside repos that have installed Charness
- humans reviewing agent-produced plans, diffs, issues, releases, and handoffs
- consumer product teams that reuse Charness skills, support capabilities, and
  adapters in their own repos

The most important usage contexts are:

- repo setup and normalization
- implementation, debug, and issue-resolution work
- durable context gathering from GitHub, Slack, Notion, Google Workspace, or
  public web sources
- quality, release, retro, handoff, and human-review loops
- external capability discovery and tool readiness checks

Qualitative success means an operator can trust the harness to make the next
right workflow move, name what it cannot prove, leave durable evidence, and
avoid turning missing context into false confidence.

## North-Star And First Instrumented Objective

The product north-star is **operator/agent task success and trust**: an operator
or agent in an installed repo can start from a normal task and trust the harness
to make the next right workflow move, leaving durable evidence instead of false
confidence. That is the success definition the [One-Page Summary](#one-page-summary)
and [Core Success Criteria](#core-success-criteria) describe. It is named here
but not yet directly measurable, because Charness does not yet capture
operator-side task outcomes (consumer-repo measurement depends on the deferred
usage-episode capture surface).

The **first instrumented objective** — the one number Charness optimizes today —
is the **repeated-mistake-to-learning conversion rate**: the share of RCA events
(bugs, repeated corrections, weak-proof findings) converted into a
recurrence-preventing durable artifact (a deterministic gate, spec, test, tracked
issue, or a retro lesson naming the detection gap and sibling pattern). It is an
engineering-health *leading indicator* that sharpens the `Follow-up conversion`
row in [Metric Definitions](#metric-definitions), not the product north-star
itself.

This objective rests on a **falsifiable assumption**: that the conversion rate
correlates with operator-observed value (a harness that stops repeating mistakes
serves its users better). What would disprove it: a rising conversion rate while
`First valuable artifact` or `Closeout proof strength` stay flat or decline — in
that case the proxy is wrong and the north-star instrument must be revisited.

The remaining metrics in [Metric Definitions](#metric-definitions) are a
*monitored* dashboard, not optimization targets, following Google Rules of ML:
many monitored metrics, one optimized objective. They retain **veto power**: a
high conversion rate during a period of degrading routing, evidence honesty, or
operator continuity is a failed period, not a success.

Decisions (2026-05-24, issue #184):

- First instrument: a symptom-to-root-cause shift counter recorded in a
  fixed-schema RCA ledger under charness-artifacts/metrics/, appended at debug,
  issue, and retro closeout. Conversion rate = converted events / total RCA
  events, decomposable by source and event kind. Build contract:
  [rca-conversion-ledger spec](../charness-artifacts/spec/rca-conversion-ledger.md).
- Numeric target: baseline-first. Observe 2-4 weeks of ledger data before
  committing a target; do not set a guessed number now.
- Scope: Charness self-development dogfood first. Consumer-repo measurement
  depends on usage-episode capture, which stays a separate deferred decision.

The ledger schema, append discipline, aggregation script, and review-loop wiring
are specced separately (issue #185).

## RCA-To-Learning Classification Rubric

This rubric makes the conversion rate reproducible across recorders. The closed
enums (`source`, `event_kind`, `durable_kind`, `caught_by`) are owned by
[scripts/rca_event.schema.json](../scripts/rca_event.schema.json); this section
summarizes the judgment calls and must not extend the enums inline.

`converted=true` requires a named durable artifact that prevents *this class* of
mistake from recurring. The quality bar applies to **every** `durable_kind`, not
only `retro_lesson`: each converted event must name the class it prevents and
cite a concrete detection point —

- `gate`: the gate name that will now catch the class,
- `spec` / `test`: the spec or test path,
- `issue`: the tracked issue number,
- `retro_lesson`: the lesson's detection-gap and sibling-pattern lines.

A throwaway issue or a one-line lesson with no named detection point does **not**
count as converted. This closes the numerator-gaming path of padding cheap
conversions to inflate the rate.

`event_kind` rules:

- `bug`: a defect in shipped behavior.
- `repeated_correction`: the same class of correction the operator already gave.
- `weak_proof`: a closeout that reached only an explicitly weak proof level.

**Tie-break default**: when it is unclear whether an event qualifies, log it with
`converted=false` rather than omitting it. Ambiguity should inflate the
denominator (conservative), never silently suppress the event (flattering).

**Auto-append wiring (slice 2) is live**: the `debug`, `issue`, and `retro`
closeout prompts append RCA events through
[skills/shared/references/rca-ledger-append.md](../skills/shared/references/rca-ledger-append.md),
so [aggregate_rca_ledger.py](../scripts/aggregate_rca_ledger.py) prints an
`auto_append: ON` banner. The baseline honesty guards still hold: it emits `n/a`
(not `0%`) for an empty seed-excluded window and refuses to print a non-seed
baseline rate while zero non-seed events exist. Seed events are excluded from the
baseline figure so a hand-picked starting set cannot anchor the eventual numeric
target, and the baseline window opens only as live (non-seed) events accrue.

## Core Success Criteria

1. Routing correctness: task language maps to the intended public skill,
   support skill, or integration without requiring the user to name internals.
2. Contract fidelity: work follows the current handoff, issue body, spec,
   quality artifact, and repo operating contract instead of stale session
   memory.
3. Evidence honesty: claims are tied to executed commands, gathered sources,
   durable artifacts, or explicit weak/missing proof labels.
4. Operator continuity: the next session can resume from
   [handoff](./handoff.md) and current `charness-artifacts/**` without
   re-solving the previous slice.
5. Quality sustainability: local deterministic gates remain runnable and
   explainable without turning every advisory signal into another broad gate.
6. External capability honesty: private-source and tool-dependent workflows name
   missing access, readiness level, and next action instead of pretending a
   weaker path proved the same thing.

## Metric Definitions

| Metric | Definition | Why it matters | Current measurability |
| --- | --- | --- | --- |
| Skill routing success | Task-oriented sessions start with the expected skill or explicit capability discovery when required. | Proves Charness is reducing workflow ambiguity. | Partly measurable through Cautilus fixtures, public-skill dogfood artifacts, issue closeout notes, and manual review. |
| First valuable artifact | First durable output that changes repo state or operator understanding, such as a spec, issue, commit, gathered record, quality artifact, or handoff update. | Connects agent activity to user-visible value instead of raw tool count. | Capturable for `slice_closeout` when usage episodes are enabled; summarized by `python3 scripts/report_usage_episodes.py --repo-root .`. |
| Closeout proof strength | Highest proof level reached before commit or handoff: deterministic local gate, release gate, provider roundtrip, bounded fresh-eye review, or explicit weak proof. | Prevents green-looking but under-proven work. | Measurable from artifacts and command logs; not summarized automatically. |
| Resume clarity | Whether [handoff](./handoff.md) points to the correct next move and stale completed work is removed. | Measures long-running agent continuity. | Manually reviewable; handoff validators cover structure but not semantic sufficiency. |
| Quality gate health | [run-quality](../scripts/run-quality.sh) phase count, pass/fail state, runtime hot spots, and warnings. | Keeps the product maintainable as skills and validators grow. | Measured in [quality latest](../charness-artifacts/quality/latest.md) and .charness/quality/runtime-signals.json. |
| Usage-episode readiness | Adapter state for privacy-bounded product usage capture: absent, disabled, invalid, no records, or valid. | Connects product success metrics to actual use without raw transcript capture. | Measured by `python3 scripts/validate_usage_episodes.py --repo-root .`; summarized by `python3 scripts/report_usage_episodes.py --repo-root .`. |
| Follow-up conversion | Repeated corrections, bug RCAs, or weak proof findings become specs, issues, tests, gates, or retro lessons. | Proves the system gets smarter with use. | Partly measurable through issue links, debug artifacts, retro artifacts, and commits. |

## AI Quality To User Value

AI-specific quality metrics are useful only when they explain user or operator
value. Charness should map them this way:

| AI quality signal | User-value metric it supports | Notes |
| --- | --- | --- |
| Routing eval pass rate | Skill routing success and resume clarity | Maintained evaluator fixtures should test high-value routing boundaries, not broad prompt trivia. |
| Regression or behavior eval result | Closeout proof strength | Run only through the repo-owned Cautilus planner/wrapper when the adapter allows it. |
| Human review outcome | Evidence honesty and operator continuity | Bounded fresh-eye review catches overclaim and stale-surface risk that deterministic gates cannot. |
| Failure/RCA artifact count and recurrence | Follow-up conversion | A bug is not fully learned from until the detection gap and sibling pattern are named. |
| Runtime/cost hot spots | Quality gate health | Runtime signals should drive deletion, routing, or ownership fixes before additive budget gates. |

External references that informed the mapping:

- Google Cloud MLOps guidance ties production ML to automated validation,
  metadata, model comparison, rollback, and triggers:
  <https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning>
- Google Rules of ML separates many monitored metrics from the single objective
  being optimized and warns not to confuse the objective with system health:
  <https://developers.google.com/machine-learning/guides/rules-of-ml/>
- OpenAI eval guidance frames evals as task criteria plus test data, run
  results, and iteration:
  <https://developers.openai.com/api/docs/guides/evals>
- NIST AI RMF emphasizes measurement, monitoring, risk response, user input,
  incidents, and continual improvement:
  <https://airc.nist.gov/airmf-resources/airmf/5-sec-core/>

## Usage-Episode Vocabulary

The proposed Charness-owned vocabulary for the fields called out in
[handoff](./handoff.md) is:

| Field | Charness baseline values | Rule |
| --- | --- | --- |
| `selected_job` | `initialize_repo`, `resolve_issue`, `implement_slice`, `debug_failure`, `gather_context`, `review_quality`, `prepare_release`, `prepare_handoff`, `update_workflow_memory`, `answer_operator_question` | Use the human job, not the raw prompt. |
| `core_action` | `normalized_repo_surface`, `landed_verified_change`, `preserved_debug_learning`, `captured_source_context`, `produced_quality_posture`, `published_release_surface`, `refreshed_handoff`, `persisted_retro_lesson`, `explained_current_state` | Use the valuable product behavior, not the tool call. |
| `agent_action.surface` | `public_skill_workflow`, `support_capability`, `github_issue`, `git_commit`, `quality_gate`, `release_helper`, `gather_record`, `handoff_artifact`, `critique_review`, `operator_reply` | Use the surface that delivered value. |
| `first_value_ref.kind` | `commit`, `issue`, `artifact`, `doc`, `test_result`, `release`, `comment`, `answer` | Keep `ref` opaque and non-PII; use `path` for repo-root-relative artifacts. |
| `feedback_signal` | `accepted`, `edited`, `corrected`, `ignored`, `retried`, `follow_up_requested`, `human_confirmed`, `closed_issue`, `released` | Use observable feedback when available; omit when unknown. |
| `outcome_status` | `delivered`, `abandoned`, `corrected`, `escalated`, `failed` | Closed enum owned by the schema; summarize it, do not extend it in docs. |
| `t_status` | `none`, `candidate`, `promoted`, `rejected` | Closed enum owned by the schema; use it to connect episodes to durable learning. |

This is a product vocabulary baseline only. It does not prove product success.
The first implemented workflow is `slice_closeout`: when the adapter is
enabled, [run_slice_closeout](../scripts/run_slice_closeout.py) appends a
privacy-safe record to .charness/usage-episodes/usage_episode.jsonl after
successful closeout. The repo-owned
[usage episode report](../scripts/report_usage_episodes.py) summarizes counts,
session grouping, T-signal rate, and capture gaps; it deliberately reports
non-claims because records are only the captured denominator, not the full usage
or outcome denominator.

## Measurement State And Next Actions

Currently measurable:

- local gate health through [run-quality](../scripts/run-quality.sh)
- usage-episode adapter state through the
  [usage episode validator](../scripts/validate_usage_episodes.py)
- usage-episode counts, session grouping, T-signal rate, and capture gaps
  through the [usage episode report](../scripts/report_usage_episodes.py)
- `slice_closeout` emission path when the usage-episodes adapter is enabled in
  a fixture or consumer repo
- release and quality proof through current artifacts
- public-skill validation tiers and dogfood records
- issue and commit closeout evidence through GitHub and git history

Needs implementation before product-success measurement:

- a maintainer-owned product-success frame for #184
- a broader denominator for uncaptured sessions, disabled hooks, and non-closeout
  workflows
- a review summary that connects usage episodes to user outcomes rather than
  only quality, retro, issue, and release artifacts

## Review Loops

Weekly:

- Review open issues, recent handoff, latest quality artifact, and any new
  debug/retro artifacts.
- Check whether repeated corrections became a deterministic gate, spec, issue,
  or deliberate non-goal.
- Report `usage-episodes` validator and report status. Treat `disabled`,
  `no_adapter`, and `no_records` as visible capture/readiness states, not as
  product-success conclusions.

Monthly:

- Review top Charness workflows against the success criteria above.
- Compare AI-quality proof depth with product outcomes: fewer repeated
  corrections, stronger closeout proof, faster resume, and clearer user-facing
  docs.
- Decide whether any passive quality recommendation should become an active
  gate, using the existing-convention check required by recent retros.
