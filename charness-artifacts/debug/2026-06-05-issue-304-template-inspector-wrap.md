# Debug #304 — setup template ↔ inspector compact-delegation disagreement
Date: 2026-06-05
Issue: #304 (bug-class; confirm-the-hypothesis, mechanism already documented)
Surface: `scripts/setup_host_docs_lib.py` (`COMPACT_SUBAGENT_DELEGATION`),
`scripts/setup_agent_docs_fresh_eye_lib.py`,
`skills/public/setup/scripts/inspect_repo.py`.

## Problem

An `AGENTS.md` generated from the documented compact `## Subagent Delegation`
default is judged by the setup inspector to have *no* compact contract present.
It falls back to the long-form required-snippet check (which the compact form
does not satisfy) and emits `fresh_eye_delegation_rule_drift` — flagging a
verbatim copy of the documented default as drift.

## Correct Behavior

A `## Subagent Delegation` block generated from the documented compact default
must be accepted by the inspector with no drift finding, while the
same-agent-allowed variant must still be rejected.

## Observed Facts

End-to-end via `inspect_repo.py` against the documented compact default:

```
compact_contract_present: False
missing compact required snippets: ['standing delegation request', 'host block']
policy_gaps missing_required: ['explicit user delegation request', 'already
  delegated', 'second user message', 'host blocks', 'same-agent pass']
findings: ['fresh_eye_delegation_rule_drift']
```

The two "missing" phrases are present in the template; they are split across a
newline + indentation by the markdown line-length wrap:

- `standing delegation request` → `…standing delegation\n  request.`
- `host block` → `Report a host\n  block explicitly`

## Reproduction

`render_agents_template(...)` → `inspect_repo.py` / `detect_fresh_eye_normalization`
on the documented compact default reproduces the output above (pre-fix,
confirmed).

## Candidate Causes

- `fresh_eye_compact_contract_present()` matches compact-contract phrases against
  the section body with raw contiguous-substring `in` checks, so a phrase that
  line-wraps across a newline + indent reads as absent. (Confirmed cause.)
- The shipped compact template diverged from the inspector's required snippet
  list (template ↔ inspector contract skew). (Ruled out — the words are present.)
- Section extraction pulled text from outside the `## Subagent Delegation`
  section, corrupting the haystack. (Ruled out — extraction is correct; only the
  intra-section match is whitespace-sensitive.)

## Hypothesis

The only reason the phrases read as missing is the line wrap: the words are
present, just split across a newline + indentation. De-wrapping the haystack
before matching should make the documented default validate while leaving the
same-agent-allowed variant rejected.

## Verification

Hypothesis confirmed at unit level and end-to-end through `inspect_repo.py`.
Post-fix: `compact_contract_present: True`, `missing_required: []`, no drift
findings; the same-agent-allowed variant is still rejected
(`compact_contract_present: False`). Regression test:
`tests/quality_gates/test_setup_inspect_policy.py::test_setup_inspect_accepts_generated_compact_subagent_delegation_block`.

## Root Cause

Contract-snippet detection in `setup_agent_docs_fresh_eye_lib.py` matched
multi-word phrases against line-wrapped markdown prose with a literal `in`
check, so any documented phrase that wraps across a line break read as absent.

## Prevention

Route every contract-snippet substring match in the module through a new
`_normalize_whitespace()` (collapse whitespace runs — newlines + indentation —
to a single space) before matching: `_missing_snippets` (haystack + snippet),
the same-agent-forbidden check in `fresh_eye_compact_contract_present`, and the
`lowered`/`section_lower` haystacks in `fresh_eye_policy_gaps` and
`detect_fresh_eye_normalization`. Section extraction still runs on raw,
line-structured text, so the in-section weakening-caveat check cannot pull text
from outside the section. Per reviewer note RN1 this was chosen over de-wrapping
the template, because relaxing the inspector also fixes any consumer repo that
copied the documented (naturally wrapped) compact block.
