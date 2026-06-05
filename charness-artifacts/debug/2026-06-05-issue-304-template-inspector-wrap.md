# Debug #304 — setup template ↔ inspector compact-delegation disagreement

Date: 2026-06-05
Issue: #304 (bug-class; confirm-the-hypothesis, mechanism already documented)
Surface: `scripts/setup_host_docs_lib.py` (`COMPACT_SUBAGENT_DELEGATION`),
`scripts/setup_agent_docs_fresh_eye_lib.py`,
`skills/public/setup/scripts/inspect_repo.py`.

## Falsifiable hypothesis

`fresh_eye_compact_contract_present()` matches the compact-contract phrases
against the `## Subagent Delegation` section body with raw contiguous-substring
`in` checks. The shipped `COMPACT_SUBAGENT_DELEGATION` default line-wraps two of
those phrases to satisfy the markdown line-length gate:

- `standing delegation request` → `…standing delegation\n  request.`
- `host block` → `Report a host\n  block explicitly`

Predicted consequence: an `AGENTS.md` generated from the documented compact
default is judged to have *no* compact contract present, falls back to the
long-form required-snippet check (which the compact form does not satisfy), and
emits `fresh_eye_delegation_rule_drift` — flagging a copy of the documented
default as drift.

## Reproduction (pre-fix, confirmed)

`render_agents_template(...)` → `inspect_repo.py` / `detect_fresh_eye_normalization`:

```
compact_contract_present: False
missing compact required snippets: ['standing delegation request', 'host block']
policy_gaps missing_required: ['explicit user delegation request', 'already
  delegated', 'second user message', 'host blocks', 'same-agent pass']
findings: ['fresh_eye_delegation_rule_drift']   # end-to-end via inspect_repo.py
```

Hypothesis confirmed: the only reason the phrases read as missing is the line
wrap; the words are present, just split across a newline + indentation.

## Root cause

Contract-snippet detection in `setup_agent_docs_fresh_eye_lib.py` matched
multi-word phrases against line-wrapped markdown prose with a literal `in`
check, so any documented phrase that wraps across a line break read as absent.

## Fix

Route every contract-snippet substring match in the module through a new
`_normalize_whitespace()` (collapse all whitespace runs — newlines + indentation
— to a single space) before matching: `_missing_snippets` (haystack + snippet),
the same-agent-forbidden check in `fresh_eye_compact_contract_present`, and the
`lowered`/`section_lower` haystacks in `fresh_eye_policy_gaps` and
`detect_fresh_eye_normalization`. Section extraction still runs on raw,
line-structured text, so the in-section weakening-caveat check cannot pull text
from outside the section. This was chosen over de-wrapping the template
(reviewer note RN1): relaxing the inspector also fixes any consumer repo that
copied the documented (naturally wrapped) compact block.

## Post-fix proof

`compact_contract_present: True`, `missing_required: []`, no drift findings —
both at unit level and end-to-end through `inspect_repo.py`. The
same-agent-allowed variant is still rejected (`compact_contract_present: False`).
Regression test:
`tests/quality_gates/test_setup_inspect_policy.py::test_setup_inspect_accepts_generated_compact_subagent_delegation_block`.
