# AI/ML Engineering Patterns For Charness

This document addresses the autonomously researchable investigation portion of
[#185](https://github.com/corca-ai/charness/issues/185) and complements
[product-success-metrics.md](./product-success-metrics.md).

Source note: the originating Slack thread was not re-fetched in this session;
see the source note in [product-success-metrics.md](./product-success-metrics.md).

## Summary

Charness already carries several mature ML-engineering patterns under agentic
workflow names: deterministic gates, evaluator routing, metadata-rich artifacts,
debug RCA, release proof, and feedback-through-retro. The main missing pattern
is not another evaluation framework. It is product usage telemetry that connects
workflow outputs to repeated user value without storing raw prompts or private
source text.

The highest-leverage proposed next improvement is to implement privacy-bounded
`usage_episode` emission for one narrow Charness-owned workflow, using the
vocabulary in [product-success-metrics.md](./product-success-metrics.md) while
keeping the
[usage-episodes adapter](../.agents/usage-episodes-adapter.yaml) disabled until
the emitter exists.

## Current-State Review

| Pattern area | Current Charness state | Posture |
| --- | --- | --- |
| Evaluation | Deterministic gates are strong; Cautilus is eval-only and adapter-disabled unless planner proof asks for it. Public-skill dogfood and quality artifacts preserve behavior-review state. | Strong for local proof; weak for product outcome measurement. |
| Experimentation | Specs, issues, critiques, retros, and release artifacts record changes and decisions. Runtime metrics exist for quality gates. | Strong for repo changes; weak for comparing product hypotheses over usage. |
| Data and feedback | Debug artifacts preserve RCA, detection gaps, and sibling scans. Retros turn corrections into lessons. Usage episodes are configured but disabled. | Strong for incidents; missing for ordinary successful usage. |
| Operations and observability | Quality runtime signals, release proof, tool doctor, integration manifests, and handoff docs make operator state visible. | Strong for maintainer-local operations; release real-host proof remains deferred. |
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

1. Product outcome telemetry is disabled.
   The [usage-episodes adapter](../.agents/usage-episodes-adapter.yaml) exists
   with `enabled: false`, so the current quality posture can report readiness
   but not product usage.
2. First value is not measured across sessions.
   Commits, artifacts, and issue closeouts exist, but no runtime record says
   which one was the first useful output for a user job.
3. Feedback signals are fragmented.
   Corrections appear in debug/retro/issue history, but ordinary acceptance,
   edits, and follow-up requests are not captured in a common envelope.
4. Docs ergonomics has weak signal quality.
   The latest quality artifact flags README and generated CLI reference noise;
   the next move is ownership cleanup, not a broad docs gate.

## Improvement Candidates

1. Implement one usage-episode emitter path.
   Start with a narrow workflow such as issue resolution or handoff closeout,
   write privacy-safe JSONL under .charness/usage-episodes/, validate it with
   the [usage episode validator](../scripts/validate_usage_episodes.py), and
   only then enable the adapter.
2. Add a usage-episode summary to quality review.
   Once records exist, report counts by `selected_job`, `core_action`,
   `outcome_status`, `feedback_signal`, and `t_status`; do not include raw
   prompts, identities, or source text.
3. Trim README route/procedure duplication after separating generated docs.
   This addresses the quality artifact's docs ergonomics finding without adding
   a noisy gate before ownership is clear.

The first candidate is the highest effect-to-effort move under current repo
evidence because it directly connects product success metrics to observable
usage and narrows the handoff item that currently blocks `usage-episodes`
activation. Maintainers still own the final product-priority decision.

## Follow-Up Issue

Concrete follow-up issue for candidate 1:

- [#188: Emit one privacy-bounded Charness usage episode workflow](https://github.com/corca-ai/charness/issues/188)

```text
Title: Emit one privacy-bounded Charness usage episode workflow
Problem: Charness has a validated usage_episode schema and a product vocabulary,
but the adapter remains disabled because no runtime emitter writes
.charness/usage-episodes/usage_episode.jsonl.
Outcome: one narrow workflow emits a privacy-safe usage_episode record, local
validation passes, and the adapter can be enabled only for that proven path.
Acceptance: emitter chooses one workflow; record uses the vocabulary in
docs/product-success-metrics.md; no raw prompt/transcript/user identity is
written; tests cover valid and malformed emitted records; quality closeout
reports enabled or explicitly still disabled.
```

The issue should stay separate from #184/#185 because it changes runtime
behavior, tests, and possibly quality summaries, while this slice defines the
product contract and investigation result.
