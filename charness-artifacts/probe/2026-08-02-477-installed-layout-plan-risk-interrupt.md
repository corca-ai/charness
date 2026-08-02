# Probe: #477 in a real exported plugin, outside the authoring tree

Date: 2026-08-02
Issue: #477
Purpose: the behavioural verdict for #477's closeout, produced through a channel
DISTINCT from the fix and from its own tests. Every prior check ran inside
`/home/hwidong/codes/charness`, where `plugins/charness/` is a subdirectory of a
tree that also contains the authoring `scripts/`. That cannot distinguish "the
shipped package carries what it needs" from "the authoring tree was in reach".

## Method

1. `python3 scripts/export_plugin.py --repo-root . --host claude --output-root <tmp>`
   → `/tmp/charness-export-8W66/plugins/charness` (charness 3.0.1), outside the repo.
2. A consumer repo at `/tmp/consumer2-*` containing only `.agents/` — no charness
   `scripts/`, no `skills/`, not a charness checkout.
3. `SKILL_DIR` set to `<plugin>/skills/impl`, exactly as an installed skill resolves it,
   and the documented command run verbatim.

## Result

| invocation | outcome | exit |
| --- | --- | --- |
| OLD `$SKILL_DIR/../../../scripts/plan_risk_interrupt.py` | `python3: can't open file … No such file or directory` | non-zero |
| OLD, with the shipped `2>/dev/null \|\| true` | **no output at all** | 0 |
| NEW `$SKILL_DIR/../../shared/scripts/plan_risk_interrupt.py` | `status: not-applicable` / `no current debug artifact` | 0 |

Both halves of #477 reproduce in the installed layout — the path does not resolve,
and the swallow makes that indistinguishable from success — and the repaired path
runs and degrades gracefully where no debug artifact exists.

Dependency presence verified in the exported package before running:
`shared/scripts/plan_risk_interrupt.py`, `scripts/plan_risk_interrupt.py`,
`scripts/risk_interrupt_lib.py`, `scripts/yaml_output.py`,
`scripts/runtime_bootstrap.py`, `scripts/artifact_validator.py` — all present.

## Non-claims

- This is an EXPORT, not a `charness install`. It proves the exported package is
  self-sufficient for this command; it does not exercise a host's installer,
  marketplace resolution, or plugin discovery.
- It does not prove the planner's VERDICT logic is correct — only that the
  documented command resolves, runs, and degrades gracefully where it ships.
- Temp directories are not retained; re-run the method above to reproduce.
