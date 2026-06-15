# Critique Review
Date: 2026-06-15

## Decision Under Review

Resolution of issue #368 (class: bug) — shift the inference-interpretation
surface-registration *leak scan* left from the ~4-min broad gate into the
commit-time structural sweep, plus the bundled general-leak audit and the
operator's separate test speed/quality ask. JTBD: a new advisory `INTERPRETATION`
declaration's missing registration must fail at the cheap commit boundary, not
after a full broad-pytest run. Recurrence-conversion of the #314/#319/#332/#366
class ("a cheap, deterministic, offline structural check enforced only at the
broad gate").

Implemented: `_leak_scan_gates` in `scripts/staged_commit_gate_plan.py` pulls
`validate-inference-interpretation` (trigger = any staged `*.py` outside the
registry exclude prefixes), `check-bootstrap-shim-consistency`, and
`check-inventory-declaration-coverage` to the commit boundary + STRUCTURAL_SWEEP_LABELS;
a new `check-timing-layer-completeness` meta-gate makes the timing-doc table the
enforced single source of truth; `docs/conventions/validator-timing-layers.md`
corrected + expanded to exact labels; an authoring checklist in
`automation-promotion.md`; and 4 always-skipped tokei degraded-path tests fixed
to actually exercise the fallback.

## Failure Angles

- **Gate mechanics (correctness):** does the gate fire, fail closed, and degrade
  correctly? Found a real trigger-scope hole — the inference validator scans every
  tracked `*.py` outside `plugins/|mutants/|tests/`, but the original trigger was
  only `scripts/|skills/`, so a declaration in a root module (`runtime_bootstrap.py`)
  would escape the commit gate. Worktree-vs-staged content read is a pre-existing
  shared nit, not new.
- **Recurrence / completeness:** what is the next recurrence after 5 instances?
  Found `check-bootstrap-shim-consistency` still broad-only (genuine cheap sibling)
  and the timing table incomplete; recommended a completeness meta-gate as the
  mechanism-level class fix (the instance-by-instance hand-pull does not stop the
  class).
- **Cost economics + test fix:** is the ~0.9s pull honest, and is the empty-PATH
  tokei fix portable? Confirmed the "no cheaper changed-scoped subset" claim is
  TRUE (the whole-tree scan is load-bearing for orphan detection via staged
  registry/consumer edits), but the budget prose framed cost in isolation; the
  tokei fix is robust (both scripts check `which` before any subprocess).

## Counterweight Pass

- The trigger-scope hole is low-probability (all 8 current declarations live in
  `scripts/|skills/`) and the broad gate stays the floor — but the fix is ~2 lines
  and restores the trigger==scan-domain invariant the whole issue is about, so
  bundle it rather than leave a smaller instance of the same class.
- `check-public-doc-coupling` is NOT a real sibling: it always exits 0 (advisory),
  so there is no blocking verdict to shift left.
- `test_t_events_emit.py:145` is NOT dead coverage: the reviewer's claim was
  inverted — `recent-lessons.md` is present, so the test runs.
- ~2s of combined full-tree scans at commit does not tempt `--no-verify` vs. the
  ~4-min alternative; pre-commit is bypassable anyway.
- The leak-scan staged-subset redesign is correctly rejected for this slice
  (full-tree scan load-bearing; reporter mandated established #314 wiring).

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: bundle-anyway | evidence: moderate | ref: scripts/staged_commit_gate_plan.py:_leak_scan_gates | action: fix | note: trigger-scope hole — widened inference trigger to the validator's full scan domain (any staged .py outside plugins/|mutants/|tests/), closing the runtime_bootstrap.py silent-disarm
- F2 | bin: bundle-anyway | evidence: strong | ref: scripts/run-quality.sh:check-bootstrap-shim-consistency | action: fix | note: genuine general-leak sibling (cheap, offline, blocking, broad-only) — pulled to the commit boundary + STRUCTURAL_SWEEP_LABELS + timing-doc row
- F3 | bin: bundle-anyway | evidence: strong | ref: scripts/check_timing_layer_completeness.py | action: fix | note: completeness meta-gate — asserts every run-quality.sh validator carries a timing verdict; the mechanism-level class fix (built per operator decision) so a 6th recurrence cannot sit unclassified
- F4 | bin: bundle-anyway | evidence: moderate | ref: docs/conventions/validator-timing-layers.md:budget | action: document | note: budget prose framed ~0.9s in isolation — now states the honest combined ~2.0s full-tree-scan cost on a scripts/|skills/ .py commit and names these the revisit-first items
- F5 | bin: over-worry | evidence: strong | ref: scripts/check_public_doc_coupling.py | action: document | note: not a real sibling — always exits 0 (advisory); classified as stays-advisory in the timing doc so the table is complete
- F6 | bin: over-worry | evidence: strong | ref: tests/test_t_events_emit.py:145 | action: defer | note: reviewer claim inverted — recent-lessons.md is present so the test runs, not skips; no fix
- F7 | bin: valid-but-defer | evidence: contested | ref: scripts/validate_inference_interpretation.py:scan_repo_declarations | action: defer | note: staged-subset scan redesign rejected — full-tree scan is load-bearing for orphan detection (staged registry/consumer edit against an unchanged declaration); reporter mandated established #314 wiring. Deliberately not doing.
- F8 | bin: over-worry | evidence: weak | ref: docs/conventions/validator-timing-layers.md:budget | action: defer | note: ~2s combined commit-path scans do not tempt --no-verify vs the ~4-min broad gate; documented as the revisit-first line item
- F9 | bin: over-worry | evidence: strong | ref: tests/quality_gates/test_quality_sloc_inventory.py | action: defer | note: empty-PATH tokei fix is portable/safe (both scripts check shutil.which before any subprocess); dogfooded — 4 tests now run, not skip
- F10 | bin: valid-but-defer | evidence: moderate | ref: scripts/staged_commit_gate_plan.py | action: defer | note: file at 475/480 code-line warn band (cohesive, passes); extract the gate-helper functions to a submodule when the NEXT gate is added — recorded in the close comment

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: high-leverage (issue-resolution critique class).
- Requested spawn fields: model=opus (this Claude Code host's mapping of the
  `high-leverage` tier; the critique-adapter's `gpt-5.5 / reasoning_effort=medium /
  service_tier=priority` is the Codex-host mapping, not applicable here).
- Host exposure state: host-defaulted
- Application state: 4 bounded fresh-eye reviewers (3 angles + 1 counterweight)
  plus the prior causal-review + test-audit reviewers spawned via the Agent tool on
  the requested model; the host does not echo applied reasoning-effort/service-tier,
  so the model override is the only host-confirmed spawn field.

## Fresh-Eye Satisfaction

parent-delegated — the parent `issue resolve` workflow spawned all bounded
reviewers (causal review, test audit, and the 4-reviewer code critique); each
completed its assigned lens directly and returned triage. Packet consumed:
`charness-artifacts/critique/2026-06-14-233441-packet.md`.
