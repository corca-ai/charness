<!-- charness-work-item-key: backlog-722 -->
# Existing Work Item #722 — Ownership-shaped setup plan

## Purpose and premise

Define an ownership-map output that tells an operator who owns which operating
surface. Re-read the current setup/quality producers and keep this child bounded
to structure, not a broad documentation rewrite.

## Owned change and acceptance

Specify fields for surface, owner, source, consumer, action, and confidence;
provide a dry-run fixture and exact command; refuse when only path existence is
known. Output and refusal reason must be deterministic.

## Verification and evidence boundary

Run `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_setup_inspect_policy.py`, then changed-line proof. This is local behavior only and does not claim installation or release adoption.

## 2026-08-27 addendum — emit a bounded ownership plan at the setup boundary

The setup inspector now uses a dedicated `setup_operating_surface_lib.py`
producer, mirrored under `plugins/charness/scripts/`, and exposes the same
plan through both `setup.inspect_repo` and `quality_setup_snapshot`. The
ownership surface remains plan-only: it does not rewrite, move, delete, or
approve documentation.

Every reported surface and proposed move carries the requested fields:
`surface`, `owner`, `source`, `consumer`, `action`, and `confidence`. The
source is the observed operating-surface path; consumers are the two local
readers; `medium` confidence means the plan is inferred from readable lexical
structure, not semantic ownership proof. A missing or empty source is marked
`path-existence-only`, leaves `owner` unset, uses `confidence: none`, and emits
the deterministic refusal reason `readable structure is required; path
existence alone is insufficient`.

The dry-run fixture is
`tests/quality_gates/test_setup_operating_surface_plan.py`. The exact local
command is:

```text
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_setup_inspect_policy.py --pytest-target tests/quality_gates/test_setup_operating_surface_plan.py
```

## Follow-up verification

- The issue-specified target alone — `tests/quality_gates/test_setup_inspect_policy.py` — reports `44 passed`.
- The combined exact command above reports `47 passed`.
- Isolated proof commit `e250565f9` ran all proof pre-commit checks and `python3 scripts/prepush_focused_changed_line_coverage.py --repo-root . --base-sha HEAD^ --refuse-unestablished` on a named proof branch: `status: clean`, `consumer_returncode: 0`, 3/3 changed mutation-pool files analyzed, `blocking: []`, and `unmapped_changed_pool_files: []`.
- A targeted mutant replacing the overloaded classification with `within-observed-shape` made `test_setup_inspect_emits_ownership_plan_for_overloaded_operating_surfaces` fail; the mutant was restored and the proof tree is clean.

## Boundary and non-claims

This is local deterministic setup/quality planning only. It does not claim
that an owner approved a documentation move, that a rewrite was executed, or
that hosted, installed-host, release, tag, push, or issue-closure behavior
changed. The user-authorized implementation path omits forced fresh-eye,
handoff, and micro-slice rituals; no such evidence is claimed. Issue `#722`
remains open.
