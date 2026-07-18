# Quality Inventory YAML Session Retro
Date: 2026-07-18

## Mode

session

## Context

The autonomous quality slice converted nine agent-facing inventory first reads
from JSON to compact YAML, centralized output selection, synchronized the plugin
mirror, and added live source/plugin contract proof. The work also exposed two
process misses: a partial migration was initially described too broadly, and the
first live-command test used the entire repository as its fixture.

## Evidence Summary

- `charness-artifacts/critique/2026-07-18-inventory-yaml-critique.md` records two
  angle reviews and a counterweight; the interface reviewer found the
  `--summary --detail` ambiguity and catalog overclaim.
- The dispatch contract test measured 57.29s against the full repo and 10.06s
  against `tmp_path`; both exercised the same 18 source/plugin command surfaces.
- Focused verification passed 99 tests; the skill-ergonomics first read shrank
  from 12,195 to 9,424 bytes and test-economics from 7,173 to 6,364 bytes.
- Packet Consumed: `charness-artifacts/retro/inventory-yaml-packet.md`.

## Waste

Exploration breadth was intentional, but triage should have locked the capability
as “nine dispatch-marked inventories” before implementation. The avoidable waste
was in verification: using the production repo as test data made a small interface
contract scan every real skill twice. The test needed a real subprocess boundary,
not production-sized content.

## Critical Decisions

- Make summary/detail mutually exclusive in the shared helper while keeping
  `--summary --json` as hidden compact-payload compatibility.
- State partial migration explicitly rather than forcing unrelated legacy tools
  into cosmetic flag symmetry.
- Derive tests from the dispatch, execute source and generated plugin copies, and
  use the smallest repository fixture that still crosses the true CLI boundary.
- Reuse the existing YAML contract gate; no new blocking floor was needed.

## Expert Counterfactuals

- Engelbart's system-improving lens would have designed method, language, and tool
  together at the triage lock: the dispatch declares capability, the shared helper
  implements it, and a dispatch-derived test proves exactly that declaration.
- A direct interface-design lens would ask whether every flag combination has one
  unsurprising meaning before rollout; that would have caught `--summary --detail`
  before fresh-eye review rather than after implementation.

## Sibling Search

- same layer: other YAML contract commands in `DETAIL_COMMANDS` | decision: diagnostic-only | proof: focused runtime stayed within the standing budget and these commands do not multiply broad domain scans through both layouts
- abstraction up: dispatch-derived source/plugin contract | decision: same waste, fix now | proof: `tmp_path` kept subprocess and YAML parsing real while reducing 57.29s to 10.06s
- specialization down: per-inventory unit tests | decision: intentional boundary | proof: they already use purpose-built fixtures to prove domain findings rather than repository scale
- mental-model siblings: unmarked inventory-dispatch entries | decision: intentional boundary | proof: catalog and dispatch now explicitly distinguish migrated YAML-capable commands from legacy output instead of asserting false universality

## Next Improvements

- workflow: lock the exact capability population before editing, then reconcile
  docs, implementation, generated mirror, and executable tests against that set.
- capability: for CLI contract tests, default to the smallest truthful fixture and
  measure the focused test before admitting it to a standing gate.
- memory: preserve the partial-migration qualifier and minimal-fixture lesson in
  this retro plus the durable critique/quality artifacts.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-07-18-inventory-yaml-session-retro.md
