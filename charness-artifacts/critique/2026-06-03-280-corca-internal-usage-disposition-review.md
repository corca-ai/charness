# Disposition Review: #280 Corca-internal last-seen product review

Fresh-Eye Satisfaction: parent-delegated

## Verdict

pass

## Scope

Reviewed whether the goal artifact's Auto-Retro and retro dispositions are
concrete and bound to actual changes rather than prose-only memory.

## Initial Finding

The first review found one Act Before Ship gap: the goal claimed execute posts
one combined comment and records packet count separately, but the test suite
only exercised `--execute` with one actionable packet.

## Disposition

Applied. `tests/test_usage_episodes_report.py` now includes
`test_product_review_execute_combines_multiple_threshold_packets`, which creates
one record crossing both friction and missed-detection thresholds, executes with
fake `gh`, and asserts:

- `comment_count == 1`
- `packet_count == 2`
- the posted body contains two product-review packet sections
- both `friction_threshold` and `missed_detection_candidate` are present

Focused proof passed: `pytest -q tests/test_usage_episodes_report.py
tests/test_usage_episodes_schema.py` — 64 tests.

Other reviewed dispositions were already concrete:

- empty-window, `classification_skipped`, invalid-window, target-ref
  gating/redaction, and missing-`gh` edge fixtures bind to
  `tests/test_usage_episodes_report.py`
- the attention-state/dogfood disposition binds to
  `docs/public-skill-dogfood.json`
- the goal slice log records the fresh-eye findings and their applied fixes

## Residual Risk

No remaining disposition gap found. Live GitHub posting was not performed; the
mutating path is covered with fake `gh` and remains gated by explicit
`--execute`.
