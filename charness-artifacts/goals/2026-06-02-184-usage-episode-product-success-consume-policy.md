# Achieve Goal: Issue 184 usage episode product success consume policy

Status: complete
Created: 2026-06-02
Activation: `/goal @charness-artifacts/goals/2026-06-02-184-usage-episode-product-success-consume-policy.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: After-phase closeout.
- Next action: run retro, final artifact check, then commit the policy/report
  slice while leaving #184 open.
- Verification cadence: cheap deterministic checks for schema/report changes;
  focused usage-episode fixtures for semantics; fresh-eye critique before
  treating the policy as a #184 closeout candidate.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files, expected invariants, usage-episode examples, tests/proof, non-claims,
  and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Shape and, if activated, implement a Charness self-dev product-success consume
policy for issue #184: define how usage episodes become evidence about
operator/agent task success and trust, which signals are required before the
evidence is quotable, which gaps veto success claims, and how the weekly/monthly
review loop should decide whether Charness is actually improving.

The goal should leave #184 with a defensible answer to the user's question:
"How exactly do we collect and measure the experience, and how do we know the
product-success story is not just plausible prose?"

## Non-Goals

- Do not close #184 merely by documenting metrics. Closure requires a maintainer
  decision after the policy and its evidence limitations are visible.
- Do not claim consumer-repo product success. Scope is Charness self-dev
  maintainer/operator dogfood unless the user explicitly widens it.
- Do not store raw prompts, transcripts, private source text, or user identity in
  usage episodes.
- Do not optimize one proxy in isolation. RCA-to-learning conversion can be the
  leading indicator, but usage-episode outcome and feedback gaps retain veto
  power.
- Do not require broad new telemetry before the first useful policy. Prefer a
  small, auditable record/report loop over a large capture surface.

## Boundaries

- In scope: `docs/product-success-metrics.md`,
  `docs/ai-ml-engineering-patterns.md`,
  `.agents/usage-episodes-adapter.yaml`,
  `integrations/usage-episodes/episode.schema.json`,
  `scripts/report_usage_episodes.py`,
  `scripts/validate_usage_episodes.py`,
  `scripts/slice_closeout_usage_episode.py`, and focused tests around those
  surfaces if implementation follows.
- In scope: policy for interpreting existing local records under
  `.charness/usage-episodes/` without committing generated runtime JSONL.
- In scope: self-dev workflow categories such as issue resolution, achieve
  slice closeout, handoff refresh/pickup, debug/RCA, gather, quality review, and
  release proof.
- Out of scope unless explicitly discussed: external user instrumentation,
  hosted analytics, private Slack refresh through `ceal`, and consumer-repo
  rollout requirements.
- Stop if the proposed metric cannot distinguish "the agent did work" from "the
  user got useful, trusted value."
- Stop if feedback capture would require raw transcript/prompt storage.

## User Acceptance

- The user can point at one document section that states the usage-episode
  consume policy: episode unit, collection points, required fields, review
  cadence, quotable metrics, and non-claims.
- The user can see exactly which current gaps block product-success claims
  today, especially missing feedback signals and incomplete denominator
  coverage.
- The user can inspect example good/bad usage episodes and understand how each
  would affect product-success review.
- The user can run one local report command and see capture coverage,
  first-value evidence, outcome/feedback distribution, and veto gaps without
  reading raw records manually.
- The user can decide whether #184 is ready to close, should remain open for a
  baseline window, or should split implementation follow-ups.

## Agent Verification Plan

### Low-Cost Checks

- `python3 scripts/validate_usage_episodes.py --repo-root .`
- `python3 scripts/report_usage_episodes.py --repo-root . --json`
- `python3 /home/hwidong/.codex/plugins/cache/local/charness/0.13.5/skills/achieve/scripts/check_goal_artifact.py --repo-root . --goal-path charness-artifacts/goals/2026-06-02-184-usage-episode-product-success-consume-policy.md`
- Focused `rg` checks that product-success docs do not claim usage episodes
  prove product success when feedback or denominator gaps remain.

### High-Confidence Checks

- Focused tests for any changed usage-episode report semantics.
- Fixture review with at least three synthetic episodes:
  `delivered+accepted`, `delivered+missing_feedback`, and `corrected` or
  `follow_up_requested`.
- Fresh-eye critique of the measurement policy before any #184 closeout claim.

### External Or Live Proof

- Live private Slack source refresh is unavailable in the current Codex runtime
  because `ceal` is not installed. If the user supplies access or runs the
  fetch, use `gather` before final #184 closure.
- No consumer-repo live proof is required for the self-dev scope; record this as
  a non-claim.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 0 | Discuss and lock the measurement posture | The user explicitly questioned whether usage episodes can really prove experience quality | Accepted decisions for scope, episode unit, artifact-value limit, feedback policy, and closeout threshold | completed |
| 1 | Specify the consume policy in the product-success doc | The current docs say usage episodes are not proof but do not yet say how they become review evidence | Updated policy text with metrics, veto gaps, review cadence, and non-claims | completed |
| 2 | Add or refine report semantics if needed | A policy without a runnable consumer repeats the current weakness | Report output or tests expose coverage, first-value, outcome, feedback, and gap summaries | completed |
| 3 | Review #184 closeout readiness | Closing #184 is a product decision, not an automatic implementation result | Critique, local checks, and a clear close / keep-open / split recommendation | completed |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — ask `find-skills` to recommend the skill for the current phase or
  boundary, and record the route it returns.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.

Gather: n/a for the draft — the originating Slack source is private and `ceal`
is unavailable in this runtime; before final #184 closure, refresh the Slack
source through `gather` if access is provided.

Release: n/a — this goal should not touch release surfaces.

## Discuss before activation

Confirm whether self-dev scope is enough for #184, whether missing feedback
should hard-block success claims, whether "first valuable artifact" should be
only a minimum evidence floor rather than a satisfaction proxy, and whether this
goal should implement report changes or only write the product-success consume
policy.

## Slice Log

### Slice 1: Define usage episode product evidence

- Objective: Separate artifact floor from satisfaction evidence and make the usage episode report expose product-success veto gaps
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: pytest -q tests/test_usage_episodes_report.py tests/test_usage_episodes_schema.py tests/quality_gates/test_slice_closeout_usage_episode.py; ruff check changed report/test files; validate_packaging.py; validate_packaging_committed.py; validate_integrations.py; check_doc_links.py; check_command_docs.py; check-markdown.sh; check-secrets.sh; validate_attention_state_visibility.py; report_usage_episodes.py shows first_value_floor=407/407, feedback_coverage=0.0%, satisfaction_signals=0, veto gaps
- Test duplication pressure: Expanded tests/test_usage_episodes_report.py to assert product_evidence floor, feedback coverage, satisfaction/friction counts, and veto gaps; check_python_lengths.py exit 0 with report_usage_episodes.py removed from warn band after helper extraction
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

### Slice 2: Review #184 closeout readiness

- Objective: Decide whether the product-success consume policy/report slice can ship and whether #184 can close
- Why this approach:
- Commits:
- What changed:
- Alternatives rejected:
- Targeted verification: Fresh-eye critique by Hooke, Turing, Bernoulli plus counterweight Hume: ship policy/report slice, keep #184 open; focused tests 58 passed; ruff passed; docs/packaging/integration/usage validation passed; live report shows feedback_coverage=0.0%, satisfaction_signals=0, veto gaps missing_feedback/no_satisfaction/single_emitter/single_trigger_type/single_entry_point
- Test duplication pressure: No new broad tests; added focused report tests for no-satisfaction, single-emitter, and unclassified-feedback vetoes
- Critique:
- Off-goal findings:
- Lessons carried forward:
- Metrics:

## Context Sources

- GitHub issue #184: `https://github.com/corca-ai/charness/issues/184`
- Baseline: `docs/product-success-metrics.md`
- Engineering boundary: `docs/ai-ml-engineering-patterns.md`
- Usage episode schema: `integrations/usage-episodes/episode.schema.json`
- Current report consumer: `scripts/report_usage_episodes.py`
- Current emitter: `scripts/slice_closeout_usage_episode.py`
- Usage adapter: `.agents/usage-episodes-adapter.yaml`
- Current blocker signal observed during shaping: `report_usage_episodes.py`
  reports 407 records, 60 sessions, 172 T signals, and 407 missing feedback
  signals. Treat this as a local engineering signal, not product-success proof.

## Interview Decisions

- Scope options considered: Charness self-dev only, consumer repo product
  success, or both. Draft choice: self-dev first; consumer proof is a later
  milestone because capture and feedback denominators are not ready.
- Measurement options considered: optimize RCA conversion only, optimize usage
  episodes only, or use RCA conversion as leading indicator with usage episodes
  as product-value veto. Draft choice: use both; either can disqualify a success
  claim.
- Episode-unit options considered: session, tool call, workflow closeout, or
  user-intent-to-first-value. Draft choice: user-intent-to-first-value is the
  conceptual unit, but the artifact itself is only a minimum evidence floor; it
  does not prove satisfaction without acceptance, reuse, correction, or
  follow-up signals. Initial emitters may approximate the unit at workflow
  closeout.
- Feedback options considered: omit feedback until available, require feedback
  for all claims, or distinguish missing feedback as a veto gap. Draft choice:
  missing feedback remains visible and prevents strong product-success claims.
- Closeout options considered: close #184 after policy, keep open until 2-4 week
  baseline review, or split implementation follow-ups. Draft choice: decide
  after Slice 0 discussion; do not assume closure.

## Plan Critique Findings

- Risk: current usage episodes can overcount activity because `slice_closeout`
  emits a delivered workflow record even when user-visible acceptance is unknown.
  Folded into User Acceptance and Slice Plan through feedback and denominator
  veto checks.
- Risk: RCA conversion can become an internal hygiene score disconnected from
  user value. Folded into Goal and Non-Goals by making usage episode outcome
  signals veto product-success claims.
- Risk: first-value artifacts can be produced almost every run, so counting them
  as satisfaction would inflate success. Folded into Interview Decisions and
  Discuss before activation: artifact existence is a necessary floor, while
  satisfaction needs acceptance, reuse, correction, follow-up, or issue outcome
  evidence.
- Risk: expanding emitters too broadly could create privacy or maintenance
  burden before the review policy is proven. Folded into Boundaries: small,
  privacy-safe, self-dev scope first.
- Risk: closing #184 could hide the remaining source-thread freshness gap.
  Folded into Coordination Cues and External Proof: Slack refresh is required
  only for final closure, not for this draft discussion.
- Fresh-eye critique: Hooke, Turing, and Bernoulli reviewed product-measurement
  validity, report/test semantics, and privacy/boundary readiness. Acted on
  concrete findings by adding `single_emitter`, `no_satisfaction_signal`, and
  `unclassified_feedback` report coverage/tests. Counterweight Hume concluded
  the policy/report slice can ship but must not close #184.

## Off-Goal Findings

- #184 remains open: current local evidence proves capture exists, but not
  product satisfaction. Required follow-up is maintainer/source-thread synthesis,
  feedback capture, and/or a baseline window before product-success trend claims.

## Final Verification

- `pytest -q tests/test_usage_episodes_report.py tests/test_usage_episodes_schema.py tests/quality_gates/test_slice_closeout_usage_episode.py` passed: 58 passed.
- `ruff check scripts/report_usage_episodes.py scripts/usage_episode_product_evidence.py tests/test_usage_episodes_report.py plugins/charness/scripts/report_usage_episodes.py plugins/charness/scripts/usage_episode_product_evidence.py` passed.
- `python3 scripts/report_usage_episodes.py --repo-root .` reports
  `first_value_floor=407/407`, `feedback_coverage=0.0%`,
  `satisfaction_signals=0`, and veto gaps
  `missing_feedback`, `no_satisfaction_signal`, `single_emitter`,
  `single_trigger_type`, `single_entry_point`.
- `python3 scripts/validate_usage_episodes.py --repo-root .` validated 407
  usage episode records.
- Packaging/integration/docs/security checks passed:
  `validate_packaging.py`, `validate_packaging_committed.py`,
  `validate_integrations.py`, `check_doc_links.py`, `check_command_docs.py`,
  `check-markdown.sh`, `check-secrets.sh`.
- `check_python_lengths.py --require-git-file-listing` passed with advisory
  warnings in unrelated existing files; `report_usage_episodes.py` was removed
  from the warning band by extracting `usage_episode_product_evidence.py`.
- `validate_attention_state_visibility.py` passed.
- Fresh-eye review executed with parent-delegated reviewers and counterweight.

## User Verification Instructions

- Run `python3 scripts/report_usage_episodes.py --repo-root .` and confirm that
  artifact floor is shown separately from feedback coverage, satisfaction
  signals, friction/follow-up signals, and product-success veto gaps.
- Read `docs/product-success-metrics.md` section `Usage-Episode Consume Policy`
  and confirm it does not treat artifacts as satisfaction proof.
- Confirm #184 remains open unless the maintainer explicitly accepts closing it
  despite missing Slack-source refresh and missing feedback/baseline evidence.

## Auto-Retro

Retro: charness-artifacts/retro/2026-06-03-184-usage-episode-product-success-consume-policy.md

Host log probe: charness-artifacts/probe/2026-06-03-184-usage-episode-product-success-consume-policy.json

Disposition review: charness-artifacts/critique/2026-06-03-184-usage-episode-product-success-disposition.md

- Finding: artifact existence is only system output, not user satisfaction.
  Disposition: applied — product-success docs and report now separate
  first-value floor from satisfaction/friction evidence and expose veto gaps.
- Finding: `upsert_goal.py` without explicit `--date` can create a duplicate
  artifact when continuing a historical goal. Disposition: applied for this run
  by deleting the accidental 2026-06-03 duplicate and continuing on the
  user-provided 2026-06-02 artifact; no code change filed unless this recurs.
- Finding: policy wording can outpace implementation; the first pass named one
  emitter but did not check it. Disposition: applied — `single_emitter` and
  `unclassified_feedback` vetoes are implemented and tested.

Retro dispositions: applied changes above cover all retro improvements for this
goal; #184 remains open by design for maintainer/source-thread synthesis and
feedback/baseline evidence.
