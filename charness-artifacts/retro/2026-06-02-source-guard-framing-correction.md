# Source Guard Framing Correction Retro
Date: 2026-06-02

## Context

The workflow-review sibling-pattern audit described the user's source-guard
concern using the phrase "expression difference". The user challenged that as
likely over-coupling or source-guard risk.

## Evidence Summary

- `charness-artifacts/quality/2026-06-02-workflow-review-sibling-pattern-audit.md`
  already identified `script.brittle_review_phrase_detector` for setup policy
  scripts and advisory recommendation consumers.
- `python3 skills/public/setup/scripts/inspect_repo.py --repo-root .` exited 0
  and reported `normalization.status: ok`, `recommendations: []`, and
  `prose_wrap.source_guard_count: 0`.
- `skills/public/quality/references/adapter-gate-review.md` classifies brittle
  phrase matching as `brittle_hard_gate_smell` unless a sharper invariant
  exists.

## Waste

The audit compressed two different facts into a weak phrase: prose-shape
matching is real coupling, while the current consumer path is advisory rather
than a hard gate. That wording made the no-code-change disposition look like a
dismissal of the user's concern instead of a consumer-boundary finding.

## Critical Decisions

- Keep F1/F8 as no-code-change dispositions only because no hard final consumer
  was found.
- Tighten the audit language so future readers see that prose-shape matching is
  coupling and that `needs_normalization`, `review_required`, or
  `brittle_hard_gate_smell` becoming pass/fail is the reopen trigger.

## Expert Counterfactuals

- Michael Feathers lens: characterize the consumer boundary first. If a test or
  command fails solely from prose shape, treat it as a source guard; otherwise
  keep it as a visible smell with an owner.
- Gary Klein premortem lens: ask how the disposition would be misread by the
  maintainer. The likely failure was exactly this one: "expression difference"
  reads like minimizing the risk.

## Next Improvements

- workflow: when reviewing source-guard candidates, write the decision as
  `coupling present?` and `hard consumer present?` rather than using wording
  like "expression difference".
- memory: keep this correction in the active goal Auto-Retro and the sibling
  audit artifact so final closeout cannot collapse the distinction again.

## Sibling Search

- same layer: sibling-pattern audit F1/F8 | decision: same waste, fix now | proof: audit language patched to separate prose-shape coupling from hard consumer evidence
- abstraction up: `skills/public/quality/references/adapter-gate-review.md` | decision: intentional boundary | proof: reference already names `brittle_hard_gate_smell` and `NON_AUTOMATABLE`
- specialization down: setup inspection consumer | decision: diagnostic-only | proof: `inspect_repo.py --repo-root .` exited 0 and emitted no recommendations on the current repo
- mental-model siblings: final goal closeout wording | decision: same waste, fix now | proof: active goal Auto-Retro records the corrected distinction

## Persisted

Persisted: yes `charness-artifacts/retro/2026-06-02-source-guard-framing-correction.md`
