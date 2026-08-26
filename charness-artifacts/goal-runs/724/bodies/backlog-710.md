<!-- charness-work-item-key: backlog-710 -->
# Existing Work Item #710 — Normalize advisory scope paths

## Purpose and premise

Normalize adapter `scope_paths` before edit-advisory matching while preserving
the existing ratchet policy. Re-read root and nested scope semantics first.

## Owned change and acceptance

Prove `.` and nested roots against changed files with exact advisory output;
invalid or ambiguous scope input receives a typed result and cannot silently
silence the advisory.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_dup_ratchet_edit_advisory.py`, then changed-line proof. No ratchet-policy expansion is in scope.

## 2026-08-27 follow-up — normalize scope membership at the advisory boundary

The edit-time advisory now consumes the canonical `dup_ratchet_scope.resolve_scope_prefixes` resolver in both source and exported layouts. `.` and `./src/` normalize to the same literal prefixes used by the ratchet gate; an unresolvable glob stays conservative and never widens the advisory to the whole tree, while a known literal sibling remains actionable. Resolver lookup failures also return an explicit conservative no-scope result rather than reviving the raw string-prefix comparison.

The advisory passes the actual `repo_root` through both decision call sites, and the source/plugin mirrors are byte-identical. Regression coverage includes whole-tree and nested normalization, mixed literal/glob scope, missing resolver metadata, and resolver import failure. The focused gate reports `33 passed`.

## Follow-up verification

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_dup_ratchet_edit_advisory.py` — `33 passed`.
- Isolated proof commit `bb44001c533031305b9d9f730d89f984f282eeac` ran `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` on a named proof branch — `status: clean`, `consumer_returncode: 0`, one changed mutation-pool file analyzed (`scripts/dup_ratchet_edit_advisory.py`), `blocking: []`, and `unmapped_changed_pool_files: []`.
- Targeted mutant: replacing the normalized membership predicate with `return False` made `test_scope_membership_uses_the_canonical_normalized_prefixes` fail; the mutation was restored and the proof tree is clean.
- Proof-tree pre-commit checks passed, including mirror drift, Python lint/compile, standalone imports, and boundary ratchet.

## Remaining acceptance boundary

This child remains open by policy. The change preserves the existing advisory-only ratchet policy; it does not claim a new hard gate, hosted or installed-host behavior, release, tag, push, or issue closure. The user-authorized implementation path omits forced fresh-eye execution, handoff updates, and micro-slice rituals; no such evidence is claimed.
