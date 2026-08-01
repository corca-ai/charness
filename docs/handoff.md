# Charness Handoff

## Workflow Trigger

- **No open work.** The three-unarmed-refusals goal is COMPLETE — D46, D48, D47
  each answered and recorded, though **all three remain open deferrals**; only the
  goal's slices closed. See
  [the goal](../charness-artifacts/goals/2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md).
  With no explicit task, run `charness:handoff` chunked routing over the live
  backlog. No open irreversible boundary.

## Continuation Capability

Two operating rules were promoted OUT of this handoff into the contracts that own
them; read them there rather than re-deriving from the retro:

- **A remedy a durable record names is a hypothesis, not a plan** — verify its
  premise before shaping a slice around it
  ([implementation-discipline](./conventions/implementation-discipline.md),
  Change Discipline). This is the single highest-value change to the next
  session's first hour.
- **Claim fidelity: the assertion is a surface too** — verify a scripted replace
  landed, grep the repo for a superseded number, state the unit before the value
  ([operating-contract](./conventions/operating-contract.md), Critique
  Discipline).

Arming posture: measure, then decide. **None of the three refusals AS POSED was
armed — but slice 2 did arm new teeth**, and the next release is the first to
carry them: `release_surface_blocker` refuses a publish on an uncorroborated
absence, and a present-but-corrupt surface is now drift with no declaration. That
refusal has never fired against a real publish. Budget for it; a refusal there is
the new gate working, not a regression.

## Current State

- **The armed changed-line gate needs an explicit `--base-sha`.** `run-quality.sh`
  hardcodes `merge-base origin/main HEAD` with no flag, so on a branch far ahead of
  `origin/main` it judges every unpushed commit and inherits other sessions'
  blocks. There is no knob on the broad lane — call the script directly:
  `python3 scripts/check_changed_line_mutation_coverage.py --repo-root . --base-sha <sha>`
  (~12 min). Scoped to a session's own base it comes back clean.
- D48's teeth sit at the publish boundary only, and it has never run against a
  real publish. `publish_release_resume.py` still reaches `create_release` with no
  surface check at all.

## Next Session

1. **`charness:handoff` chunked routing** over the live backlog, then apply the
   premise rule to what it SELECTS (not to every candidate it surfaces). Live
   lanes: sweep high rows S15 (PARTIAL), S31 (OPEN), S36/S37 (LEAD — never
   reproduced), S111; the untouched E-cluster (E1/E3/E6/E7 + E2's residual), the
   most expensive lane; #467; #468.
2. **A precondition on step 1, not a lane inside it: D45 carries #468's shape.**
   It names "moving the exemption to the adapter" as S31's correct repair — the
   same self-declaration channel D48 just found insufficient. Its premise is a
   FILE READ, not a command: check whether an adapter-declared exemption seam
   exists at all in `ci_local_gate_parity_lib.py`, which today sources the
   exemption only from the `# charness:gate-policy` marker inside the audited
   workflow. Do NOT "verify" it by running
   `inventory_ci_local_gate_parity.py --detail` — that reproduces the symptom D45
   already records and says nothing about the remedy's channel. Settle this if
   routing selects S31.
3. **`goal_artifact_floor_grammar.parse_created_date` is consumed by FIVE achieve
   floors with no corroboration** — carried untouched across two handoffs. NOT a
   drive-by: the helper takes only `text`, so corroborating from the filename the
   way `critique_enforcement_scope.observed_date(path, text)` does means threading
   a `path` through all five consumers plus their `plugins/charness/` mirrors.
   Size it as a slice, not an edit.

## Discuss

- **A read-only check and an irreversible boundary deserve different teeth.** D48
  resolved by leaving `drift` untouched and refusing at publish. Whether other
  gates should adopt that split is an operator call.

## References

- [goal](../charness-artifacts/goals/2026-08-01-get-the-operator-call-on-the-three-unarmed-refusals-d46-adap.md) · [retro](../charness-artifacts/retro/2026-08-01-three-unarmed-refusals-retro.md) · [marker-rule probe](../charness-artifacts/probe/2026-08-01-inventory-marker-rule.json)
- [deferred decisions](./deferred-decisions.md) (D45–D48) · [the sweep](../charness-artifacts/audit/2026-07-28-evidence-surface-triage-sweep.md) · [2026-07 hunt](../charness-artifacts/audit/2026-07-27-evidence-surface-bug-hunt.md)
- [recent lessons](../charness-artifacts/retro/recent-lessons.md) · [quality review](../charness-artifacts/quality/latest.md) · [release state](../charness-artifacts/release/latest.md)
