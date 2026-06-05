fix(setup): agree compact subagent-delegation contract across line wraps

Close #304.

Classification: bug.
Issue closeout carrier: direct-commit.
Issue: #304 setup host-doc default and inspector disagree on the minimal valid
`## Subagent Delegation` contract.
JTBD: an agent or operator who copies the documented compact
`COMPACT_SUBAGENT_DELEGATION` default into AGENTS.md must not be immediately
flagged as delegated-review drift by `inspect_repo.py`.
Root cause: `fresh_eye_compact_contract_present()` matched the compact-contract
phrases against the section body with raw contiguous-substring `in` checks, but
the shipped default line-wraps `standing delegation request` and `host block` to
satisfy the markdown line-length gate, so the phrases read as missing and the
inspector fell back to the long-form check, emitting
`fresh_eye_delegation_rule_drift`.
Debug artifact: charness-artifacts/debug/2026-06-05-issue-304-template-inspector-wrap.md
Siblings: sibling search covered every contract-snippet matcher in
`setup_agent_docs_fresh_eye_lib.py` (the same-agent-forbidden check, the compact
and long-form required-snippet checks, the task-scope/stale-marker/weakening-caveat
haystacks). Decision: fix the whole class in this module by routing all of them
through whitespace-normalized matching rather than patching only the two wrapped
phrases. Proof: every matcher now calls `_normalize_whitespace`; the full
`test_setup_inspect_policy.py` (32 tests) and the related fresh-eye-touching
suites (107 tests) pass, and the same-agent-allowed variant is still rejected.
Prevention: contract phrases are matched whitespace-insensitively, and the new
regression test asserts the raw generated phrases are not contiguous, so a future
template de-wrap that would silently stop exercising the wrap hazard fails the
test.
Tests: `pytest -q tests/quality_gates/test_setup_inspect_policy.py` (32 passed),
plus `test_setup_normalize_host_docs.py test_reviewer_tier_policy.py
test_quality_skill_docs.py test_docs_and_misc.py test_spec_critique.py`
(75 passed); `run_slice_closeout.py` deterministic aggregate completed.
Critique: charness-artifacts/critique/2026-06-05-issue-304-template-inspector-agreement.md
