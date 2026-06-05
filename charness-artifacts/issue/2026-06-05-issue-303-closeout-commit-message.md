feat(setup): generate adapter-first subagent reviewer rule in AGENTS.md

Close #303.

Classification: feature.
Issue closeout carrier: direct-commit.
Issue: #303 setup should generate adapter-first subagent reviewer rules.
JTBD: a host whose AGENTS.md is generated/normalized by `setup` needs an
explicit rule that subagent reviews follow the active skill/repo adapter's
reviewer tier and concrete spawn fields, instead of silently inheriting the
parent turn's host defaults and spawning a reviewer at the wrong effort.
Boundary: host-facing rule only; preserve the existing standing-delegation
language and do not redesign the reviewer-tier policy. The rule must stay
adapter-first and must not assert every subagent is always medium — medium is
named only as the Codex-critique high-leverage default unless the adapter says
otherwise.
Resolution brief: feature-class issue with no open product decisions; add a
concise second bullet to the compact `## Subagent Delegation` template that
states the adapter-first rule, names the conditional Codex default, and stops
and reports when the adapter/tier cannot be applied — consistent with the
canonical reviewer-tier policy where concrete values live in the adapter.
Implementation: extended `COMPACT_SUBAGENT_DELEGATION` in
`scripts/setup_host_docs_lib.py` (and synced mirror) with the adapter-first
reviewer bullet. The bullet uses the canonical `high-leverage` tier name,
attributes concrete spawn fields to the adapter, frames medium as a per-adapter
Codex default ("unless it says otherwise") with an explicit "not a claim that
every subagent is medium" disclaimer, and keeps the existing standing-delegation
bullet untouched. The setup inspector stays clean (compact_contract_present
True, no weakening-caveat/drift findings).
Prevention: a new regression test
(`test_generated_agents_carries_adapter_first_reviewer_rule`) asserts the rule
phrases, the conditional-medium framing and disclaimer, intact standing
delegation, and inspector cleanliness, so future template edits cannot regress
to inherited subagent effort or a global medium.
Tests: `pytest -q tests/quality_gates/test_setup_inspect_policy.py
tests/quality_gates/test_setup_normalize_host_docs.py
tests/quality_gates/test_reviewer_tier_policy.py` (50 passed);
`run_slice_closeout.py` deterministic aggregate completed.
Critique: charness-artifacts/critique/2026-06-05-issue-303-adapter-first-reviewer-rule.md
