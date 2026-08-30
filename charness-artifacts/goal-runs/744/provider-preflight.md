# Goal Run #744 Provider Preflight

Observed: `2026-08-30T05:46:05Z`

Command:

`python3 skills/public/issue/scripts/issue_tool.py goal-run-preflight --repo-root . --repo corca-ai/charness --number 744 --plan-file charness-artifacts/goal-runs/744/provider-plan.json`

Result: `ok: true`, `status: ready`, `outcome: verified-read`, `mutation_invoked: false`.

- Selected backend `gh`; binary found; active GitHub authentication probe returned exit 0.
- Adapter is valid and repository target is exact.
- All seven planned operations are ready: `read-body`, `read-state`, `update-body`, `list-children`, `add-child`, `record-observation`, and `close-goal-run`.
- Parent readback: `corca-ai/charness#744`, `OPEN`, canonical URL `https://github.com/corca-ai/charness/issues/744`, updated at `2026-08-28T09:41:24Z`.
- Provider-plan SHA-256: `76b0c45e485e6feb66956004fc53974229c07cd39000cca1aacd5b9f96c6f440`.
- Provider main: `ab4b2d8b72d9450dbab32da89e4934acdf6724e8`.
- Exact-SHA Quality Core: `success`,
  `https://github.com/corca-ai/charness/actions/runs/33295371954`.

This receipt proves readiness only at the observation time. Re-run before binding and before the first provider mutation; a later unavailable result blocks activation.
