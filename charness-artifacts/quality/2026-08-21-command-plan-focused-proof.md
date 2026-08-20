# Command-Plan Focused Proof

Date: 2026-08-21

## Receipt

- Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q tests/quality_gates/test_command_plan_preflight.py`
- Resolved source/test HEAD: `19e62aea829e4d40b1ede2d1e2273ea067963dd1`
- Status: `passed`
- Result: `25 passed in 2.01s`
- Raw operator log: `/tmp/charness-final-head-command-plan-focused-19e62aea.log`
- Raw log SHA-256: `7f9d2ecd409e3385f77b15ba55bc4fad2e689455be43610c3f7c46c9928aa0a4`

## Coverage Boundary

This is the focused command-plan regression receipt for the semantic candidate
endpoint. It covers target/ref/owner/flag refusal, fail-fast behavior,
malformed command shapes, embedded and nested target-token refusal, and
non-string expansion failures. The owner-binding implementation applies the
same standalone-token validator to `argv` and `help_argv`; the focused suite
explicitly covers embedded refusal on both surfaces, while the nested-marker
case exercises the shared guard. This receipt is local evidence only: it does
not prove runtime, installed, hosted, publication, issue-closeout, or Cautilus
truth.
