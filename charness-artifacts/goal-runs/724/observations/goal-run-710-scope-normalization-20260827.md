# Goal Run `backlog-710` scope normalization

## Scope

- Work item: `backlog-710` / issue `#710`
- Contract source: `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/existing-work-item-readiness.md`
- Owned source: `scripts/dup_ratchet_edit_advisory.py` and its generated plugin mirror
- Owned tests: `tests/quality_gates/test_dup_ratchet_edit_advisory.py`

## Implemented contract

The edit-time advisory now delegates scope normalization to the canonical `dup_ratchet_scope.resolve_scope_prefixes` helper. Whole-tree and nested literal forms match the ratchet's semantics; ambiguous glob entries do not widen scope; known literal entries remain actionable; and resolver loading failures stay conservative. Both decision call sites pass the target repository root. The source and plugin mirror compare byte-identically.

## Executed verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_dup_ratchet_edit_advisory.py` — `33 passed`.
- Isolated proof commit `bb44001c533031305b9d9f730d89f984f282eeac`: `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` — `status: clean`, `consumer_returncode: 0`, one changed mutation-pool file analyzed, `blocking: []`, and `unmapped_changed_pool_files: []`.
- Targeted membership mutant failed the normalization regression test and was restored.
- Proof-tree pre-commit and source/plugin mirror checks passed.

## Boundary and non-claims

This is local deterministic verification only. It preserves advisory-only behavior and does not claim a ratchet-policy expansion, issue closure, hosted or installed-host behavior, release, tag, or push. The user-authorized path omits forced fresh-eye, handoff, and micro-slice rituals; no fresh-eye result is claimed. Issue `#710` remains open.
