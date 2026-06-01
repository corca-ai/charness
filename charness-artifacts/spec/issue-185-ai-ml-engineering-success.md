# Issue 185 AI/ML Engineering Success Conditions

Status: ready for final-carrier closeout of #185
Date: 2026-06-01

## Scope

This artifact resolves the engineering-pattern investigation requested by
[#185](https://github.com/corca-ai/charness/issues/185). It records the
necessary Charness engineering success conditions and follow-up disposition that
can be decided from the current repo state and issue bodies.

It does not resolve [#184](https://github.com/corca-ai/charness/issues/184).
Product success still needs maintainer synthesis and a refreshed read of the
originating Slack thread before numeric targets, product priorities, or
business/user outcome definitions are treated as final.

## Source Evidence

- #185 issue body, read on 2026-06-01: asks for AI/ML engineering pattern
  investigation across evaluation, experimentation, data/feedback,
  operations/observability, and quality engineering.
- #184 issue body, read on 2026-06-01: asks for product success criteria and
  metrics and says to re-read the same Slack source thread before resolving.
- [AI/ML engineering patterns](../../docs/ai-ml-engineering-patterns.md):
  current-state review, keep/missing pattern split, and three improvement
  candidates.
- [Product success metrics](../../docs/product-success-metrics.md): current
  measurable leading indicators and explicit product-success non-claims.
- [Usage episode report](../../scripts/report_usage_episodes.py): implemented
  #243 consumer for session grouping, T-signal rate, and capture gaps.

## Necessary Conditions

For Charness repo work, an AI/ML engineering success claim should require these
conditions:

1. **Evaluation is proof-scoped.** Deterministic gates own routine local
   correctness; Cautilus/evaluator-backed proof is used only through the
   repo-owned planner and supported eval surfaces when behavior evidence is
   actually needed; bounded fresh-eye/HITL review owns judgment that deterministic
   gates cannot encode.
2. **Experiments leave durable state.** Specs, issues, critiques, retros,
   release artifacts, and goal logs preserve the hypothesis, changed variable,
   rejected options, decision, proof, and residual risk instead of relying on
   session memory.
3. **Feedback becomes learning.** Bugs, repeated corrections, and weak proof
   findings convert into RCA events, tests, gates, issues, or retro lessons
   with a named detection gap and sibling pattern.
4. **Usage signals are privacy-bounded and denominator-honest.** Usage
   episodes never carry raw prompts, transcripts, or user identity; reports
   expose session grouping, T-signal rate, and capture gaps without pretending
   captured records are the full usage or outcome denominator.
5. **Operations stay observable.** Quality runtime signals, release proof,
   install/tool doctor surfaces, attention-state visibility, and usage reports
   make local state inspectable before publication; latency/cost claims stay
   non-claims unless the host or repo artifact actually exposes those metrics.
6. **Quality remains sustainable.** The local gate surface stays runnable and
   explainable; advisory signals become active gates only when the existing
   convention and noise profile justify the cost.
7. **Portability boundaries are explicit.** Public skills stay host-neutral;
   host/provider behavior belongs in adapters, hooks, manifests, and
   integration surfaces.

These are necessary conditions, not sufficient product-success criteria.

## Issue 185 Checklist Disposition

| #185 Area | Current disposition |
| --- | --- |
| Evaluation | Dispositioned through deterministic gates, public-skill dogfood, Cautilus planner policy, scenario registry validation, and bounded fresh-eye/HITL review for judgment-heavy claims. |
| Experimentation | Dispositioned for Charness workflow/prompt/adapter changes through specs, goal artifacts, issue closeout matrixing, critique, and retro loops. Charness does not currently run model/search/sampling grid experiments, so those variables must be named in the owning spec when they appear. |
| Data/feedback | Dispositioned for incidents and engineering learning through RCA/retro/debug; strengthened by #243 usage reporting for ordinary closeout episodes, with capture gaps still visible. Usage episodes are not a labeled training/eval dataset. |
| Operations/observability | Dispositioned through quality runtime signals, release/doctor surfaces, attention-state visibility, and run-quality report surfacing. Cost/latency are claimable only where host/runtime artifacts expose them. |
| Quality/engineering | Dispositioned through `run-quality`, local pre-commit/pre-push gates, packaging mirrors, closeout proof discipline, and explicit advisory-to-gate promotion rules. |

## Applied Improvements

- #188 implemented the first narrow privacy-bounded `slice_closeout` usage
  episode emitter.
- #243 added the usage episode report consumer and quality-visible capture-gap
  signal.
- Existing RCA ledger and retro/debug workflows provide the feedback-to-learning
  mechanism that #185 asked for.

## Remaining Non-Claims

- This does not define product success for #184.
- This does not set numeric product or business targets.
- This does not prove consumer-repo adoption, user satisfaction, or business
  value.
- This does not re-fetch the originating private Slack thread.

## Final-Carrier Note

#185 can close in the final carrier with this artifact, the AI/ML engineering
patterns doc, and the #188/#243 implementation evidence. The carrier should say
that the issue's investigation checklist is dispositioned for Charness's current
workflow product boundary, not that product success is solved. #184 should
remain open with a note that product-success synthesis and source-thread refresh
are still pending.
