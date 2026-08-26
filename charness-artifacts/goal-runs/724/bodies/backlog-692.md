<!-- charness-work-item-key: backlog-692 -->
# Existing Work Item #692 — Adapter idempotence ownership

## JTBD

Make every shipped public-skill adapter initializer predictable: a fresh
destination initializes once, a valid existing destination is unchanged, and
invalid or unestablished state refuses before mutation unless the operator
explicitly requests force.

## Root cause

Idempotence was implemented only in the `impl` adapter while the other 15
entrypoints retained wrapper-specific output or writers, so the shipped
surface had no single lifecycle owner or uniform refusal receipt.

## Debug artifact

`charness-artifacts/debug/2026-08-27-issue-692-adapter-idempotence.md`

## Owned change and acceptance

Charness owns the common initializer, the 16 public source entrypoints, the
checked-in plugin export, the consumer-classification declarations, and their
local tests. Fresh, existing-valid, dry-run, invalid-version, force, path,
and symlink states are explicit in one typed receipt. Scheduler changes,
hosted enforcement, conditional-trigger execution, installed-host adoption,
and consumer-repository rollout are outside this issue.

## Siblings

Decision: the 16 initializer placements and `scripts/adapter_init_lib.py`
were bundled as the same bug and fixed now; `skills/public/issue/scripts/issue_tracker_cli.py`
is an adjacent direct consumer of adapter state, classified and checked but
not behaviorally changed because it is not an initializer. Proof: clean
named-worktree contract/standing tests and source/plugin parity; the adjacent
consumer has classification proof only.

## Prevention

Keep all public initializer wrappers on the common lifecycle and retain the
32-case contract matrix plus the consumer-classification gate. Do not make a
dirty-parent diff or universal changed-line proof a prerequisite for ordinary
implementation.

## Verification and evidence boundary

Base `55026bdb6b5423fdaadffff218f32bff3b0f5811`; target
`47f5ddc30179f9a3a20954d69678b01c47319ef1`; proof branch
`proof/issue-692-adapter-20260827`; proof path
`/tmp/charness-692-proof-20260827`.

## Executed verification

- `python3 -m pytest -q tests/quality_gates/test_adapter_bootstrap_contract.py` — `32 passed` across all 16 public adapter entrypoints, covering dry-run, initialization, idempotent repeat, and invalid-version refusal.
- `python3 -m pytest -q tests/test_impl_bootstrap.py tests/test_announcement_adapter_lib.py tests/quality_gates/test_hotl_adapter.py tests/quality_gates/test_setup_adapter_scaffold_policy.py tests/quality_gates/test_reviewer_tier_policy.py tests/quality_gates/test_create_skill_adapter.py tests/quality_gates/test_narrative_scenario_blocks.py` — `75 passed`.
- The related suite passed `76` tests; the standing consumer-classification target passed `37`, and the focused-plus-standing combined target passed `69`.
- The selected adapter eval subset passed `10/10` scenarios.
- `python3 scripts/check_staged_mirror_drift.py --repo-root .` — source/plugin mirror matched.
- Ruff, Python length checks, `git diff --check`, and the final clean proof-worktree postflight passed. The no-`--verify` pre-commit completed all 20 hook commands in the proof worktree with a temporary non-staged compatibility overlay for the stale critique contract; the overlay was removed and not committed.
- An exact-target `python3 scripts/run_evals.py --repo-root . --jobs 4` is not claimed: it exits at the pre-existing `representative-skill-contracts` checker, which still requires the two critique phrases already removed from the current `skills/public/critique/SKILL.md` (18 scenario lines passed before that failure). Restoring those stale constraints is outside #692.
- The common initializer now emits one typed `charness.adapter-bootstrap/v1` receipt, refuses invalid or unestablished state without explicit force, and leaves valid existing adapters unchanged.
- `Behavior #692: local-only-by-contract — the clean named proof covers source, tests, plugin export, and classification consumers only; no installed-host behavior or provider roundtrip is claimed.`
- This is local source/test/plugin verification only; no issue closure, push, release, tag, hosted enforcement, scheduler change, conditional-trigger execution, or consumer-repository adoption is claimed.
- `Critique: blocked explicit operator direction omits forced fresh-eye review and this host exposes no Agent/subagent capability; deterministic contract tests and mirror/readback checks are the retained evidence.`
