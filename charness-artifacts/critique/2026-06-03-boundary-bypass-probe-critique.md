# Code Critique: Boundary-Bypass Advisory Probe

Date: 2026-06-03

Fresh-Eye Satisfaction: parent-delegated (3 bounded fresh-eye general-purpose subagents — 2 angle: Weinberg/Jackson + 1 counterweight; read-only in the shared parent worktree)

Packet Consumed: n/a (additive slice; changed-files surface inspected directly, no per-slice packet render)

Target: skills/public/critique/references/code-critique.md

## Scope

- Change: a repo-owned advisory probe inventorying "boundary-bypass" tests
  (tests spawning an import-safe script entrypoint via subprocess when the logic
  is in-process reachable). Files: `scripts/inventory_boundary_bypass_lib.py`,
  `scripts/inventory_boundary_bypass.py`, `tests/test_boundary_bypass_inventory.py`
  (+ synced `plugins/charness/scripts/` mirror).
- Advisory only — no gate wiring, no ratchet, no committed baseline. Reports 134
  candidates (121 convertible, 13 likely keep-boundary) / 235 test files.
- Verified: ruff, lengths, attention-state, packaging (+committed mirror),
  repo-python subset 2098 passed / 4 skipped.

## Verdict

SHIP — two one-line note additions folded; framing items routed to
[testability-dsl-initiative.md](../../docs/testability-dsl-initiative.md). No
logic change required.

## Angles

- Weinberg (heuristic correctness), Jackson (problem-framing/portability), + a
  separate counterweight triage.
- Agreed strength (keep): the payload shape is genuinely stack-neutral and the
  probe's own test is in-process (imports the `_lib`, builds synthetic repos via
  the DSL's `build()`), so it dogfoods the principle it advocates — non-circular.

## Folded Before Ship (notes added to inventory_boundary_bypass_lib.py)

- **W2 — `convertible_count` over-claims.** ~30% of import-safe targets spawn
  subprocesses/git internally, so converting their tests moves the boundary
  inward rather than removing it. Added a payload note: the count is candidates,
  not guaranteed boundary elimination.
- **J3 — schema ownership.** `charness.quality.*` straddles repo-owned probe vs
  quality-owned contract. Added a comment by `SCHEMA_VERSION`: the payload
  contract is quality-skill-owned; this probe is one stack-specific emitter (no
  rename, intent disclosed).
- **J1 — placement rationale.** Added a docstring "Relation" line: this refines
  the already-portable `nested_cli_fanout` spawn-smell in
  `standing_test_economics_lib.py`; the genuine stack-specific delta is
  `is_import_safe` + in-repo target resolution.

## Deferred (recorded in testability-dsl-initiative.md)

- **J2 — the ratchet.** This slice is a sensor with no teeth: it advances
  repo-improvement + skillification, NOT yet "bad patterns can't take root." The
  no-increase ratchet on a committed baseline is the **named next obligation**,
  recorded in the initiative doc and handoff (this satisfies J2's condition that
  deferral is honest only if the ratchet is explicitly named).
- **W3** (`.read_text(` over-match in `behavior_assert`), **J5** ("candidate"
  naming; ratchet must not inherit false positives as permitted debt), and
  `convertible_count` jitter — all ratchet-correctness concerns, fixed when the
  ratchet lands, not now.

## Over-Worry Dismissed (counterweight)

- **W1** (~7–9% literal-scan over-report): already disclosed in the payload
  notes; an advisory over-reporter that admits it has discharged its duty.

## Next Move

Ships as-is. Next obligation is the ratchet (goal 2), per the initiative doc.
