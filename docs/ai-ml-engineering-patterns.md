# AI/ML Engineering Patterns For Charness

This document addresses the autonomously researchable investigation portion of
[#185](https://github.com/corca-ai/charness/issues/185) and complements
[product-success-metrics.md](./product-success-metrics.md). It dispositions the
engineering checklist for Charness's current workflow-product boundary; it does
not close product-success issue #184.
The closeout-ready necessary-condition summary is recorded in
[issue-185-ai-ml-engineering-success.md](../charness-artifacts/spec/issue-185-ai-ml-engineering-success.md).

Source note: the originating Slack thread was not re-fetched in this session;
see the source note in [product-success-metrics.md](./product-success-metrics.md).

## Summary

Charness already carries several mature ML-engineering patterns under agentic
workflow names: deterministic gates, evaluator routing, metadata-rich artifacts,
debug RCA, release proof, and feedback-through-retro. The main missing pattern
is not another evaluation framework. It is product usage telemetry that connects
workflow outputs to repeated user value without storing raw prompts or private
source text.

The highest-leverage proposed next improvement was to implement
privacy-bounded `usage_episode` emission for one narrow Charness-owned
workflow, using the vocabulary in
[product-success-metrics.md](./product-success-metrics.md). That path now
exists for `slice_closeout`, and the repo-owned usage report summarizes counts,
session grouping, T-signal rate, and capture gaps. This is still an engineering
usage signal, not product-success proof.

## Current-State Review

| Pattern area | Current Charness state | Posture |
| --- | --- | --- |
| Evaluation | Deterministic gates are strong; Cautilus is eval-only and adapter-disabled unless planner proof asks for it. Public-skill dogfood, quality artifacts, bounded fresh-eye review, and HITL surfaces preserve behavior-review state. | Strong for local proof and judgment-heavy closeout; weak for product outcome measurement. |
| Experimentation | Specs, issues, critiques, retros, and release artifacts record workflow, prompt, adapter, and policy changes. Runtime metrics exist for quality gates. | Strong for repo experiments; model/search/sampling experiments must be named in an owning spec when Charness gains that runtime surface. |
| Data and feedback | Debug artifacts preserve RCA, detection gaps, and sibling scans. Retros turn corrections into lessons. Usage episodes now have validator and report consumers, with capture gaps made visible. | Strong for incidents and local usage episodes; not a labeled training or eval dataset. |
| Operations and observability | Quality runtime signals, release proof, tool doctor, integration manifests, and handoff docs make operator state visible. | Strong for maintainer-local operations; release real-host proof and cost/latency claims remain deferred unless captured by host/runtime artifacts. |
| Quality engineering | `run-quality`, coverage, ruff, link checks, supply-chain checks, issue closeout rules, and critique discipline form a mature local gate surface. | Strong, with known risks around docs ergonomics and test fanout. |

## Patterns To Keep

- Treat evals as one proof class, not the whole product metric. OpenAI's eval
  guide describes task criteria, data, runs, and iteration; Charness should keep
  using Cautilus only when the repo-owned proof planner says behavior evidence
  is needed.
- Keep validation and metadata together. Google Cloud's MLOps guidance stresses
  validation, comparisons, metadata, rollback pointers, and triggers; Charness
  already mirrors this through quality/release artifacts and current pointers.
- Measure many health signals, but do not overfit one objective. Google Rules
  of ML distinguishes metrics from the directly optimized objective; Charness
  should keep success criteria broader than a single eval pass rate.
- Include risk and post-deployment monitoring. NIST AI RMF frames measurement
  and management as ongoing monitoring, user input, incident response, and
  continual improvement; Charness maps this to debug, retro, issue, quality,
  and handoff loops.

## Missing Or Weak Patterns

1. Product outcome telemetry is opt-in and incomplete.
   The [usage-episodes adapter](../.agents/usage-episodes-adapter.yaml) exists
   so the current quality posture can report readiness. `slice_closeout`
   emission and report aggregation exist, but the denominator is still only
   captured local records.
2. First value is not measured across sessions.
   Commits, artifacts, and issue closeouts exist, but no runtime record says
   which one was the first useful output for a user job.
3. Feedback signals are fragmented.
   Corrections appear in debug/retro/issue history, but ordinary acceptance,
   edits, and follow-up requests are not captured in a common envelope.
4. Model-runtime experiment tracking is not a shipped Charness surface.
   Charness currently tracks workflow/product experiments, not model/search/
   sampling grids. If those variables become first-class, the owning spec should
   name the variable set, comparison method, and rollback/selection criteria.
5. Docs ergonomics has weak signal quality.
   The latest quality artifact flags README and generated CLI reference noise;
   the next move is ownership cleanup, not a broad docs gate.

## Improvement Candidates

1. Keep the `slice_closeout` usage-episode emitter narrow.
   It writes privacy-safe JSONL under .charness/usage-episodes/ only when the
   adapter is enabled. Validate it with the
   [usage episode validator](../scripts/validate_usage_episodes.py) before any
   maintainer opts this repo into capture.
2. Keep the usage-episode summary in quality review.
   Report counts by `selected_job`, `core_action`, `outcome_status`,
   `feedback_signal`, and `t_status`, plus session grouping and capture gaps;
   do not include raw prompts, identities, or source text, and do not treat the
   report as product-success proof.
3. Trim README route/procedure duplication after separating generated docs.
   This addresses the quality artifact's docs ergonomics finding without adding
   a noisy gate before ownership is clear.

The first candidate was implemented through #188, and the summary consumer was
added later for #243. Maintainers still own the final product-priority and
product-success decisions. That boundary is intentional: #185 can close on
engineering success conditions, while #184 remains open for product-success
synthesis.

## Implementation Issue

Concrete follow-up issue for candidate 1:

- [#188: Emit one privacy-bounded Charness usage episode workflow](https://github.com/corca-ai/charness/issues/188)

```text
Title: Emit one privacy-bounded Charness usage episode workflow
Problem: Charness has a validated usage_episode schema and a product vocabulary,
but the adapter remains disabled by default until maintainers intentionally
enable local runtime capture.
Outcome: one narrow workflow emits a privacy-safe usage_episode record, local
validation passes, and the adapter can be enabled only for that proven path.
Acceptance: emitter chooses one workflow; record uses the vocabulary in
docs/product-success-metrics.md; no raw prompt/transcript/user identity is
written; tests cover valid and malformed records; quality closeout reports
enabled or explicitly still disabled.
```

The issue stayed separate from #184/#185 because it changed runtime behavior,
tests, and quality closeout behavior, while the earlier slice defined the
product contract and investigation result.
