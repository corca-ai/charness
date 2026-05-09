# Critique — Issue #135 PR 3 (Leg 3): Engelbart anchor + applies_when scope

Date: 2026-05-09
Target: code-critique (per `skills/public/critique/references/code-critique.md`)
Spec: charness-artifacts/spec/issue-135-t-first-self-evolving-unit.md (Leg 3)

## Diff Scope

- `skills/public/critique/references/angle-selection.md` — new
  `## Anchor Lineup` section: 6 entries (`jackson`, `weinberg`, `gawande`,
  `raskin`, `minto` with `applies_when: lam-critique`; `engelbart` with
  `applies_when: system-improving-itself` + Falsifier line). Trigger wording
  matches the spec verbatim.
- `skills/public/retro/references/expert-lens.md` — Engelbart bullet added
  to `Examples` list, citing the lineup home and the same scope tag, with a
  "skip for ordinary lesson retros" guard.
- `scripts/check_premortem_rename.allowlist.txt` — two carry-over additions:
  `angle-selection.md` (new `decision premortem` trigger cite) and
  `charness-artifacts/skill-t-mechanism/inventory.json` (PR 2 baseline cleanup —
  validator was already failing fail-closed on main with 8 outside-allowlist
  cites from historical retro filenames).
- `plugins/charness/*` mirrors via `scripts/sync_root_plugin_manifests.py`.

## Acceptance

- A3.1 — every entry in the Anchor Lineup carries an `applies_when:` line
  (grep-verifiable, 6/6).
- A3.2 — Engelbart entry's `Falsifier:` line is grep-verifiable on the same
  reference.
- A3.3 — manual smoke deferred to first dogfood retro after land (the
  Falsifier itself is the contract for collecting that observation).
- S3.3 — Engelbart trigger cited in both `critique` reference
  (`angle-selection.md`) and `retro` reference (`expert-lens.md`).

## Angles + Counterweight

Bounded fresh-eye reviewer (general-purpose subagent) ran the code-critique
substrate with Minto + Jackson + Gawande angles and a separate counterweight
pass.

- **Act Before Ship**: none. All A3.x checks satisfied; validator green;
  scope vocabulary byte-consistent with `integrations/t-events/event.schema.json`
  enum (`lam-critique`, `system-improving-itself`); plugin mirrors byte-identical
  to root.
- **Bundle Anyway** (applied): the `inventory.json` allowlist line. The
  validator was failing fail-closed since PR 2 land (commit `77d87b7`) on the
  generated inventory's cite of historical premortem retro filenames. PR 3
  is the natural slice to add the line because it already touches this
  validator's allowlist for its own cite.
- **Over-Worry**: pushed back on three "while we're here" concerns —
  cross-citing the new `Anchor Lineup` by name from each of the 5 critique
  target references (existing `angle-selection.md` link from SKILL.md
  reaches it); adding a third guard against Engelbart over-pull on plain
  product retros (the bullet body already carries an explicit "skip for
  ordinary lesson retros" guard, on top of the surrounding rules section's
  "if the same action would emerge without the name, prefer the direct
  lens" line); touching AGENTS.md / CLAUDE.md / retro mode-guide /
  retro section-guide / t-events emit lib (none of them currently mention
  anchors and the spec does not require it).
- **Valid but Defer**: collecting Engelbart mis-fire evidence on
  `lam-critique` surfaces. By design — the Falsifier line *is* the contract
  for that future observation. The first post-land dogfood retro covers it.

## Defect Class Cross-Link

`charness-artifacts/retro/recent-lessons.md` repeat traps around generated
surfaces and validator scope drift apply to the inventory.json allowlist
line: a sync surface ideally lands with the slice that produced it. PR 2
should have shipped the line; PR 3 is the natural cleanup point now that
the same validator's allowlist is being touched anyway.

## Recurrence Prevention

- `applies_when:` scope vocabulary is a closed value set co-owned by
  `skills/public/critique/references/angle-selection.md` (lineup metadata)
  and `integrations/t-events/event.schema.json` (event enum). New values
  require both surface updates plus at least one positive dogfood case
  before landing — captured in the lineup section's closing paragraph.
- The `Falsifier` line names the concrete trigger (mis-fire on
  `lam-critique` surface, ≥1 dogfood observation) and the bounded
  escalation cost (lineup metadata format change inside critique
  references), so a future retro that observes a mis-fire knows what to do
  without a fresh design pass.

## Baseline (out of scope for PR 3)

`tests/quality_gates/test_critique_skill.py` carries 4 failing tests on
`main` *before* PR 3 — PR 1 (Leg 5 `premortem` → `critique` rename) shipped
the SKILL.md and validator content but did not update these tests. They
expect old wording (`Task-completing repo work always records critique
before closeout.` vs current `…records this critique pass before closeout.`)
and the old `charness-artifacts/critique/` artifact path (current location
is `charness-artifacts/premortem/`). Verified by stashing the PR 3 diff
and re-running — same 4 fails. Not introduced by PR 3, not fixed by PR 3.
Belongs in a Leg 5 follow-up slice that aligns the test expectations with
the post-rename SKILL.md and the historical-artifact-dir reality.

## Source

Internal — initiated from current repo state (handoff trigger). No external
originating context, so no Source identity block per
`closeout-discipline.md`.
