# Issue #398 closeout ledger

## Target

- Repo: `corca-ai/charness`
- Issue: `#398`
- State before closeout: `OPEN`
- URL: `https://github.com/corca-ai/charness/issues/398`

## Classification

- Classification: `feature`
- JTBD: preserve and validate diagnostic/negative Cautilus verdicts without
  weakening passing-proof closeout.

## Carrier

- Preferred carrier: direct commit with `Close #398`
- Draft closeout body:
  `charness-artifacts/issue-398-closeout/closeout-comment.md`
- Resolution critique:
  `charness-artifacts/critique/2026-06-23-issue-398-cautilus-diagnostics.md`

## Behavior Evidence

- `python3 scripts/validate_cautilus_diagnostics.py --repo-root . --all`
- `CHARNESS_QUALITY_LABELS=validate-cautilus-diagnostics ./scripts/run-quality.sh --read-only`
- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only`
- `python3 skills/public/quality/scripts/check_dup_ratchet.py --repo-root . --json`
  after refreshing the gate baseline for the local nose 0.15.0 family-id set.
