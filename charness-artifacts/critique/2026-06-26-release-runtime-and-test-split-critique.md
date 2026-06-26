# Release Runtime And Test Split Critique

Date: 2026-06-26

## Scope

- Split `publish_release_artifact.py` into a thin writer plus section renderer helpers.
- Share release runtime recording between execute and resume flows.
- Surface timed failure-path payloads without dumping the full release plan.
- Split Codex runtime/home tests out of `tests/test_cautilus_scenarios.py`.

## Fresh-Eye Review

Reviewer: bounded read-only subagent `019f032c-a4b2-7ad1-b733-a5428b62e7a8`.

Result: no blockers.

Residual risk found: the first shared runtime change recorded failure-path timings only in memory. That would not prove operator-visible failure runtime.

Disposition: fixed before commit. `publish_release_runtime.print_failure_payload()` now emits a compact stderr JSON payload on execute/resume `SystemExit`, and `test_resume_aborts_before_push_when_revalidation_fails` asserts `quality_command` runtime is present while publish runtime is absent.

Follow-up risk found during local verification: dumping the whole payload leaked fresh-checkout probe details into stderr and violated the existing local-only-path non-disclosure test.

Disposition: fixed before commit. Failure payload output now uses a whitelist centered on release identity and `release_runtime`.

Pre-push quality finding: `dup-ratchet` blocked on newly rotated code family ids after the release helper split and plugin mirror sync.

Disposition: refreshed `charness-artifacts/quality/dup-ratchet-baseline.json` with `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --write-baseline`; rerun status was clean. This accepts the current intentional/generated mirror state rather than classifying it as fixable duplication.

## Verification

- `python3 -m pytest -q tests/quality_gates/test_release_publish.py tests/quality_gates/test_release_publish_resilience.py tests/quality_gates/test_current_pointer_writes.py tests/test_cautilus_scenarios.py tests/test_instruction_surface_codex_runtime.py tests/test_cautilus_eval_commands.py` -> 78 passed
- `python3 -m ruff check skills/public/release/scripts tests/quality_gates/test_release_publish_resilience.py tests/test_cautilus_scenarios.py tests/test_instruction_surface_codex_runtime.py`
- `python3 scripts/check_boundary_bypass_ratchet.py --repo-root .`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/check_staged_mirror_drift.py --repo-root .`
- `python3 scripts/check_doc_links.py --repo-root .`
- `bash scripts/check-markdown.sh`
- `python3 scripts/check_python_lengths.py --headroom --paths skills/public/release/scripts/publish_release_artifact.py skills/public/release/scripts/publish_release_artifact_sections.py skills/public/release/scripts/publish_release_cli.py skills/public/release/scripts/publish_release_runtime.py tests/test_cautilus_scenarios.py tests/test_instruction_surface_codex_runtime.py`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
