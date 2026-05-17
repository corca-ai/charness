# Gather Extracted Content Persistence Critique

- Date: 2026-05-17
- Target: opt-in extracted content persistence for public URL gather
- Fresh-Eye Satisfaction: same-agent scoped critique; subagent not invoked because this turn requested critique but not delegation
- Packet Consumed: n/a (bounded source/diff review)

## Change

Add opt-in persistence for readable extracted content in public URL gather. The
default artifact still records provenance, route, selected attempt, confidence,
open gaps, and trace JSON with `Content Persistence: none`. Passing
`--persist-extracted-content` asks `support/web-fetch` to return the selected
successful attempt's extracted text or markdown, and `gather_public_url.py`
stores it in a separate `Extracted Content` section.

## Design Critique

### Act Before Ship

- Do not store raw response bodies by default.
- Do not embed selected content inside `Trace JSON`; otherwise a reader cannot
  skim provenance without pulling bulk source text into logs or diffs.
- Do not print the selected content in the public command's result payload after
  writing the artifact.
- Preserve the existing rule that blocked, degraded, and error acquisitions do
  not refresh the durable gather pointer.
- Truncate opt-in content and record both stored and original character counts.
- Use a dynamic Markdown fence so extracted content containing backticks cannot
  corrupt the rest of the artifact.

### Bundle Anyway

- Record `Content Persistence: none | extracted | unavailable` in every public
  URL gather record.
- Update the public gather capability contract and the support web-fetch
  runtime contract so this remains an extracted-content feature, not raw
  response persistence.
- Keep deterministic tests for default omission, opt-in persistence, raw HTML
  tag removal, trace JSON omission, and no-write behavior for non-success
  acquisitions.

### Over-Worry

- Requiring a separate storage backend before adding an opt-in extracted-text
  section.
- Blocking on provider-private raw JSON policy; this slice only covers public
  URL gather.

### Valid But Defer

- A raw-response debug mode with redaction and retention policy.
- Provider-specific raw API response capture for Slack, Notion, or Google
  Workspace.
- A separate artifact size policy beyond the current truncation flag.

## Implementation Critique

The implementation follows the safe shape: content is absent by default,
included only behind explicit flags, converted to extracted text/markdown,
omitted from trace JSON, omitted from the public command result payload, and
not written for blocked/degraded/error acquisitions. The dynamic fence closes a
markdown corruption hole that would otherwise be easy to miss.

Residual risk: direct public fetch extraction uses the existing HTML tag
stripper. It is adequate for provenance-grade readable text, but not a high
quality reader. For article-quality content, `defuddle` remains the better
selected attempt when available.

## Proof

- `pytest -q tests/test_web_fetch_support.py`: 31 passed.
- `python3 scripts/check_python_lengths.py --repo-root .`: passed.
- `ruff check skills/public/gather/scripts/gather_public_url.py skills/support/web-fetch/scripts/acquire_public_url.py skills/support/web-fetch/scripts/acquisition_trace_lib.py tests/test_web_fetch_support.py`: passed.
- `python3 scripts/validate_skills.py --repo-root .`: passed.
- `python3 scripts/validate_public_skill_dogfood.py --repo-root .`: passed.
- `python3 scripts/run_slice_closeout.py --repo-root . --ack-cautilus-skill-review`: passed.

## Next Move

Run full quality, commit the source changes, synced plugin export, dogfood
evidence, tests, and this critique artifact together, then release if the
operator wants the installed plugin surface updated immediately.
