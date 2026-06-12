# Product Success Criteria And Metrics

This document defines the current Charness success baseline that informed
issues [#184](https://github.com/corca-ai/charness/issues/184) and
[#185](https://github.com/corca-ai/charness/issues/185). The #184 baseline
review closed on 2026-06-13: the maintainer confirmed the numeric target for
the instrumented objective (see Decisions 2026-06-13 below), so #184 is now a
closed decision record rather than an open synthesis item.

Source note: both issues came from the 2026-05-20 Daily Scrum Slack thread
`slack://C05J5LTFSCU/1778805288.184149`. Neither the 2026-05-24 session nor
the 2026-06-13 baseline review could re-fetch that private source (`ceal`
unavailable on the deciding hosts; no Slack web URL usable by the checked-in
gather-slack wrapper). At the baseline review the maintainer explicitly
accepted the ceal-captured GitHub issue body as the working source for this
decision. Non-claim: the original Slack thread was never re-read; if a future
re-read surfaces intent the GitHub capture missed, the numeric-target decision
is the surface to revisit. Runtime capture activation for consumer repos
remains a separate deferred decision.

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

The current baseline product north-star is **operator/agent task success and
trust**: an operator or agent in an installed repo can start from a normal task
and trust the harness to make the next right workflow move, leaving durable
evidence instead of false confidence. That is the success definition the
[One-Page Summary](#one-page-summary) and
[Core Success Criteria](#core-success-criteria) describe. It remains provisional
for #184 and is not yet directly measurable, because Charness does not yet
capture operator-side task outcomes (consumer-repo measurement depends on the
deferred usage-episode capture surface).

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
usage-episode feedback, correction/follow-up rate, or closeout proof strength
stay flat or decline — in that case the proxy is wrong and the north-star
instrument must be revisited.

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

Decisions (2026-06-13, issue #184 baseline review — maintainer-confirmed):

- Numeric target, in force now: **conversion rate ≥ 70% on the rolling 28-day
  seed-excluded window, judged only when the window holds ≥ 10 live events,
  AND zero falsified conversions in the window.** A *falsified conversion* is
  an exact `class_key` recurrence after a `converted=true` event — the
  recorded durable artifact demonstrably did not prevent the class. Both
  halves are reported by
  [aggregate_rca_ledger.py](../scripts/aggregate_rca_ledger.py) (`target`
  block, computed in `rca_ledger_lib.py`); the verdict anchors on the latest
  live event timestamp so it is reproducible from the committed ledger alone.
  When the window holds fewer than 10 live events the verdict reads
  `insufficient-n` even if a falsified conversion sits in the window — the
  tripwire-response contract below fires on *detection*, regardless of the
  verdict string, and the all-time falsified list always renders.
- Baseline at decision time: 76.9% (20/26 live events, 2026-05-24 → 06-11).
  The floor sits below the baseline deliberately: the rubric's conservative
  tie-break ("ambiguous → `converted=false`") and the quality-sustainability
  criterion mean some non-conversions are correct judgment, so 100% — or even
  holding the observed 77% — is **not** the goal. Pushing the rate up by
  shipping ceremony gates is the failure mode the tripwire half guards.
- Tripwire response contract: each falsified conversion requires redesigning
  that conversion's durable artifact (tracked as an issue), not waiting for
  the recurrence to age out of the window. First instance at decision time:
  `mutation-dispatch-no-base-sha-false-proof`
  ([#358](https://github.com/corca-ai/charness/issues/358)).
- Recording the redesign: append a `conversion_upgrade=true` re-record of the
  same `class_key` via `record_rca_event.py` with `--conversion-upgrade`,
  `--converted`, `--durable-kind <kind>`, and `--ref <response-issue>`
  (the ref is required). An upgrade event records
  artifact work, not a new occurrence of the mistake: it is excluded from
  conversion-rate denominators, it does not count as a recurrence, it refreshes
  the conversion stamp so a *later* recurrence falsifies the upgraded artifact,
  and it does **not** clear an in-window tripwire — the recurrence still ages
  out on its own ts, per this contract. The aggregator annotates the falsified
  entry with `upgraded_ts`/`upgraded_ref` so the response is visible in the
  report. Operational rule: an actual recurrence is always recorded as a
  plain event **first**; the upgrade never substitutes for the recurrence
  record. Recording a recurrence as an "upgrade" hides it from the rate, the
  recurrence list, and the tripwire — the exact self-reporting corruption the
  tripwire exists to catch.
- Per-`event_kind` and per-`source` rates stay a monitored decomposition, not
  targets: at the observed inflow (~1.4 events/day) the per-kind samples
  (n=5–9 in the baseline window) are too small to target without rewarding
  reclassification games.
- The target stays advisory (reported, reviewed in the weekly loop), not a
  blocking quality gate, per the spec's gate-posture probe answer.

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
| First-value evidence floor | First durable output that changes repo state or operator understanding, such as a spec, issue, commit, gathered record, quality artifact, or handoff update. This is a minimum evidence floor, not satisfaction proof. | Separates "the agent produced something inspectable" from raw activity, while preventing artifact existence from being counted as user satisfaction. | Capturable for `slice_closeout` when usage episodes are enabled; summarized by `python3 scripts/report_usage_episodes.py --repo-root .`. |
| Satisfaction and friction signals | Observable follow-through after the first-value floor: acceptance, human confirmation, issue closure, release, correction, retry, ignored output, or follow-up request. | Measures whether the artifact was useful enough to accept or reuse, or whether it created more work. | Partly measurable when `feedback_signal` is present; missing feedback remains a veto gap in `report_usage_episodes.py`. |
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

## Usage-Episode Consume Policy

Usage episodes become product-success evidence only through a review layer, not
by raw record count.

The review unit is one privacy-safe episode that approximates a user intent
moving toward first inspectable value. For current self-dev dogfood, the
implemented `slice_closeout` emitter records that approximation at workflow
closeout. Future emitters may cover issue closeout, handoff refresh/pickup,
debug/RCA, gather, quality review, or release proof, but each must keep the same
privacy boundary: no raw prompt, no transcript, no private source body, and no
user identity.

Interpret records in four tiers:

1. **Capture coverage**: a session or workflow produced a valid usage episode.
   Missing capture is a denominator gap, not a success or failure.
2. **First-value floor**: `first_value_ref` names an inspectable output. This
   admits the episode into product review, but it does not prove satisfaction;
   Charness often leaves artifacts even when the user is unhappy or the direction
   is wrong.
3. **Satisfaction evidence**: `feedback_signal` values such as `accepted`,
   `human_confirmed`, `closed_issue`, or `released` show observable acceptance or
   reuse. These are the first signals that can support a product-value claim.
4. **Friction evidence**: `feedback_signal` values such as `corrected`,
   `retried`, `ignored`, or `follow_up_requested`, plus non-delivered
   `outcome_status` values, show that the artifact floor was not enough.
   Feedback values outside the documented satisfaction/friction buckets are
   counted as feedback coverage but remain unclassified and cannot support a
   strong product-success claim.

Strong product-success claims are vetoed when feedback is missing, when records
come from only one emitter, entry point, or trigger type, when first-value refs
are present but satisfaction evidence is absent, when feedback values are
unclassified, or when correction/follow-up signals rise with the RCA conversion
rate. In those cases the correct conclusion is "capture exists but user value is
not proven."

## Corca-Internal Last-Seen Product Review

Issue [#280](https://github.com/corca-ai/charness/issues/280) adds a narrower
review loop for Corca-internal usage evidence. The review layer may show when a
Corca repo/user was last observed using Charness, but it must not classify
silence as churn, dissatisfaction, or a `stopped_using_candidate`.

The local reporter is
[report_usage_product_review.py](../scripts/report_usage_product_review.py). It
reads the same privacy-bounded usage episode records as
`report_usage_episodes.py` and emits reporter-only packets with:

- `first_seen_at`, `last_seen_at`, `usage_count`, product counts, trigger counts,
  outcome counts, and feedback counts for the review window
- release/version context plus `update_prompt_state`, with the explicit
  non-claim that update prompts are not satisfaction evidence
- optional Corca-internal `repo_ref` and `user_ref` fields supplied at report
  time, not stored in public episode records
- thresholded `friction_threshold` and `missed_detection_candidate` packets only
  when the operator supplies the corresponding threshold flags
- triage questions and non-claims instead of root-cause diagnosis or suggested
  fixes

Example dry-run:

```bash
python3 scripts/report_usage_product_review.py \
  --repo-root . \
  --release-version 0.14.0 \
  --update-prompt-state prompted \
  --corca-internal \
  --repo-ref corca-ai/charness \
  --user-ref <corca-user-ref> \
  --friction-threshold 2 \
  --missed-detection-threshold 1
```

The command is report-only by default. `--execute` can post thresholded
issue-comment packets through GitHub only when `--github-repo` and
`--issue-number` are provided. Mutating comments redact `repo_ref` and
`user_ref` by default; pass `--include-target-refs-in-comments` only for an
approved Corca-internal destination. The command refuses to post a comment when
no friction or missed-detection threshold crossed. Usage observed, raw episode
count growth, first-value artifacts, last-seen staleness, and update prompts
alone remain dashboard/review context rather than auto-filed findings.

## Measurement State And Next Actions

Currently measurable:

- local gate health through [run-quality](../scripts/run-quality.sh)
- usage-episode adapter state through the
  [usage episode validator](../scripts/validate_usage_episodes.py)
- usage-episode counts, session grouping, T-signal rate, and capture gaps
  through the [usage episode report](../scripts/report_usage_episodes.py)
- usage-episode first-value floor, feedback coverage, satisfaction signals, and
  friction/follow-up signals through the same report
- Corca-internal review-window `first_seen_at` / `last_seen_at` summaries and
  dry-run reporter packets through
  [report_usage_product_review.py](../scripts/report_usage_product_review.py)
- `slice_closeout` emission path when the usage-episodes adapter is enabled in
  a fixture or consumer repo
- release and quality proof through current artifacts
- public-skill validation tiers and dogfood records
- issue and commit closeout evidence through GitHub and git history

Needs implementation before product-success measurement:

- a maintainer-owned product-success frame for #184
- a broader denominator for uncaptured sessions, disabled hooks, and non-closeout
  workflows
- broader emitter coverage beyond `slice_closeout`
- stronger feedback capture so satisfaction and friction signals are not mostly
  missing

## Review Loops

Weekly:

- Review open issues, recent handoff, latest quality artifact, and any new
  debug/retro artifacts.
- Check whether repeated corrections became a deterministic gate, spec, issue,
  or deliberate non-goal.
- Report `usage-episodes` validator and report status. Treat `disabled`,
  `no_adapter`, and `no_records` as visible capture/readiness states, not as
  product-success conclusions.
- In the report, separate first-value floor from satisfaction evidence; do not
  count artifact existence as user satisfaction.

Monthly:

- Review top Charness workflows against the success criteria above.
- Compare AI-quality proof depth with product outcomes: fewer repeated
  corrections, stronger closeout proof, faster resume, and clearer user-facing
  docs.
- Check whether feedback coverage is high enough to quote any product-success
  trend. If feedback is missing for most records, keep #184-style claims
  provisional.
- Decide whether any passive quality recommendation should become an active
  gate, using the existing-convention check required by recent retros.
