# CLI Side-Effect Probe Closeout Premortem

Date: 2026-04-30

## Decision

Close issue #85 by turning the Ceal `apply --help` incident into reusable
Charness quality guidance and a repo-owned helper. The helper now validates a
`cli-side-effect-probes.json` contract, flags a missing contract, and can execute
explicitly safe fixtures with watched side-effect snapshots.

## Likely Misread

- The helper could be mistaken for proof that every Charness lifecycle command
  has an executable sandbox. Current Charness entries are declaration-level
  until a command marks `safe_to_execute`.
- A product could add probe strings that look complete but never run them.
  `--fail-on-findings` catches missing declarations; `--execute-probes` is the
  next bar when a safe fixture exists.
- Option-looking positional probes are only meaningful when the parser path is
  safe to execute. The contract keeps them explicit instead of guessing from
  source text.

## Counterweight

- The issue asked for a deterministic checklist/helper, not a universal parser
  fuzzer. Running arbitrary mutating commands by default would recreate the
  original safety failure.
- The repo now has a closeout surface for the Charness contract itself:
  `python3 skills/public/quality/scripts/inventory_cli_side_effect_probes.py --repo-root . --fail-on-findings`.
- The test fixture proves the Ceal-shaped failure mode: a `--help` probe that
  writes watched state produces `probe_changed_side_effect_watch`.

## Proof

- `python3 skills/public/quality/scripts/inventory_cli_side_effect_probes.py --repo-root . --fail-on-findings`
- `python3 -m pytest tests/quality_gates/test_quality_cli_side_effect_probes.py tests/quality_gates/test_quality_skill_docs.py tests/quality_gates/test_surface_obligations.py -q`
- `python3 -m pytest -q tests/quality_gates tests/control_plane tests/test_*.py tests/charness_cli/test_doctor_cache_selection.py tests/charness_cli/test_tool_lifecycle.py`
- `ruff check charness scripts tests skills/public/*/scripts skills/support/*/scripts`
- `python3 scripts/validate_surfaces.py --repo-root .`

## Closeout

Fresh-eye review initially blocked closure because the helper was declaration
only and silent on missing contracts. The implementation was revised before
commit to add missing-contract findings, `--fail-on-findings`, executable safe
fixtures, Charness dogfood contract coverage, and changed-surface obligations.
