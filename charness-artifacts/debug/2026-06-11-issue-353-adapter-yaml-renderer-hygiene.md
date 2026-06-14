# Issue #353 Adapter YAML Renderer Hygiene Debug
Date: 2026-06-11

## Problem

`scripts/adapter_lib.py` silently corrupts YAML-adjacent adapter data at rewrite
time: newline-bearing strings render with literal newlines inside quotes,
unsupported YAML constructs are parsed as ordinary scalars and normalized, and
`quality_bootstrap_lib.py` reports falsy explicit fields as preserved while the
renderer omits them.

## Correct Behavior

- Given a string value containing `\n`, rendering then loading it returns the
  original string.
- Given limited block scalars (`|`, `|-`, `>`, `>-`), the small adapter parser
  preserves the body instead of dropping it; given aliases, tags, or unsupported
  block-scalar modifiers, it refuses loudly instead of guessing semantics.
- Given explicit falsy known quality-adapter fields (`preset_version: null`,
  `spec_pytest_reference_format: ""`), rewrite output preserves them when
  `field_statuses` says `preserved`.

## Observed Facts

- Repro before fix: `render_yaml_mapping([("body", "line1\nline2")])` emitted
  `body: "line1\nline2"` and `load_yaml()` returned `{"body": "\"line1"}`.
- Before fix, `load_yaml("body: |\n  line1\n")` returned `{"body": "|"}` and
  ignored the block body.
- Before fix, the quality bootstrap render path only appended `preset_version`
  and `spec_pytest_reference_format` when truthy, despite earlier status code
  marking explicit fields as `preserved`.

## Reproduction

- `python3 -m pytest -q tests/quality_gates/test_adapter_lib_yaml.py`
  with the new regression cases failed on newline rendering and unsupported
  construct refusal before the production patch.
- `python3 -m pytest -q tests/quality_gates/test_quality_bootstrap.py::test_quality_bootstrap_rewrite_preserves_explicit_falsy_fields`
  pinned the consumer mismatch after a fixture setup correction.

## Candidate Causes

- Missing scalar escaping: `_yaml_scalar()` escaped quotes/backslashes but not
  newline or carriage-return characters.
- Parser over-acceptance: `_coerce_scalar()` accepted every unquoted scalar,
  including YAML syntax this hand-rolled subset cannot represent.
- Consumer truthiness gate: `render_bootstrap_adapter()` used `data.get(...)`
  rather than preservation status for optional falsy fields.

## Hypothesis

If the renderer escapes newline/carriage-return characters, the loader decodes
only supported double-quoted escapes, the parser preserves limited block-scalar
bodies while rejecting unsupported aliases/tags/modifiers, and
quality-bootstrap renders fields when their status is `preserved`, then the
three #353 failure modes are fixed without making `adapter_lib` a general YAML
engine.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_adapter_lib_yaml.py tests/quality_gates/test_quality_bootstrap.py::test_quality_bootstrap_rewrite_preserves_explicit_falsy_fields tests/quality_gates/test_quality_bootstrap.py::test_quality_bootstrap_adapter_preserves_existing_explicit_commands`
  passed after the fix.
- Compatibility correction: the first decoder patch collapsed unknown regex
  escapes such as `\s`; the existing explicit-commands test caught it, and the
  decoder now preserves unknown escapes as literal backslash+character.

## Root Cause

The repo-owned YAML seam was a deliberately small parser/renderer, but it had no
clear refusal boundary. It accepted input that exceeded its subset, then rewrote
it through the subset renderer. Separately, quality-bootstrap status reporting
tracked explicitness correctly but rendering used truthiness, creating a
status/output mismatch for falsy explicit values.

## Invariant Proof

- Invariant: adapter rewrite either preserves a supported value exactly across
  render/load or refuses an unsupported construct before normalization.
- Producer Proof: focused parser/renderer tests cover newline escaping, limited
  block-scalar body preservation, unsupported alias/tag/modifier refusal, and
  existing regex escape compatibility.
- Final-Consumer Proof: quality-bootstrap rewrite test proves explicit falsy
  known fields are present in output when reported as preserved.
- Interface-Shape Sibling Scan: `quality_bootstrap_lib.py` was the concrete
  consumer sibling where renderer truthiness leaked into operator status.
- Non-Claims: not a general YAML implementation; only plain and strip-chomped
  literal/folded block scalar headers are supported.

## Detection Gap

- adapter renderer tests | did not cover richer-than-subset YAML input or
  falsy explicit fields in a real consumer rewrite | added focused tests for
  newline round-trip, limited block-scalar body preservation, unsupported
  alias/tag/modifier refusal, regex escape compatibility, and
  quality-bootstrap falsy preservation.

## Sibling Search

- Mental model: "the adapter parser only sees values it created itself."
- same-file: `scripts/adapter_lib.py` scalar rendering/loading | fixed now |
  proof: `test_adapter_lib_yaml.py`.
- consumer sibling: `scripts/quality_bootstrap_lib.py` optional falsy fields |
  fixed now | proof: `test_quality_bootstrap_rewrite_preserves_explicit_falsy_fields`.
- cross-file: other adapter helpers that call `render_yaml_mapping()` | decision:
  no direct change; the shared renderer now refuses unsupported constructs and
  preserves newline scalars for all callers | proof: focused shared tests.

## Seam Risk

- Interrupt ID: issue-353-adapter-yaml-renderer-hygiene
- Risk Class: none
- Seam: repo-owned adapter parser/renderer subset
- Disproving Observation: local focused tests reproduced and then retired the
  three named failure modes.
- What Local Reasoning Cannot Prove: arbitrary YAML compatibility outside the
  declared subset.
- Generalization Pressure: none

## Interrupt Decision

- Critique Required: yes
- Next Step: impl
- Handoff Artifact: none

## Prevention

Keep the adapter seam subset explicit in tests: any future construct either gets
a supported round-trip test or a refusal test before a consumer rewrite path can
claim preservation.
