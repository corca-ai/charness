# Critique: Issue 299 Release-Only Sentinel Inventory

Execution: executed via bounded fresh-eye subagents plus separate counterweight.

Fresh-Eye Satisfaction: parent-delegated.

Packet Consumed:
`charness-artifacts/critique/2026-06-04-225531-packet.md`.

Target: code critique / issue-resolution critique.

## Change

Resolve #299 by adding an advisory quality inventory,
`skills/public/quality/scripts/inventory_release_only_sentinels.py`, plus
focused tests, inventory-dispatch discoverability, plugin mirror sync, and
quality dogfood evidence.

Success means selected expensive pytest files can report release-only test
counts, standing test counts, standing sentinel names, and advisory warnings
when release-only tests lack obvious standing sentinel coverage. This slice is
advisory-only and does not promote a new blocking gate.

## Angles

- Behavior / contract correctness: reviewed AST parsing, output shape, sentinel
  heuristic risk, and public quality contract drift.
- Issue-resolution fit: reviewed #299 desired outcome, advisory posture,
  Cautilus/dogfood handling, and closeout carrier risk.
- Counterweight: pushed back on over-hardening the advisory into a gate and
  triaged what must be bundled before commit.

## Findings

### Act Before Ship

None.

### Bundle Anyway

- Cite the selected-file inventory output in closeout:
  `tests/quality_gates/test_release_publish.py` plus
  `tests/quality_gates/test_release_publish_real_host_delta.py` report
  `release_only=19`, `standing=8`, `standing sentinels=8`, and no findings.
  Applied in the goal slice evidence.
- Record Cautilus planner output: `required=false`, `next_action=none`,
  `must_ask_before_running=true`; deterministic validation owns this slice and
  no live Cautilus proof is claimed. Applied in the goal slice evidence.
- Clarify inventory dispatch wording: use `--path` for selected slow /
  release-only files because default all-tests scanning is broad and
  advisory-noisy. Applied in `inventory-dispatch.md`.

### Over-Worry

- Do not run Cautilus; the planner explicitly says no action is required.
- Do not treat default broad-scan advisory findings as release blockers.
- Do not harden the new inventory into a standing gate in this slice.

### Valid But Defer

- Initial substring marker detection could overcount non-marker mentions if the
  inventory were promoted to a gate. Applied instead of deferred by switching to
  structural `pytest.mark.release_only` marker parsing.
- Initial AST walk ignored `async def test_*`. Applied instead of deferred by
  counting `ast.AsyncFunctionDef` tests.

## Counterweight Triage

Structured Findings:

- `selected-output-closeout`: Bundle Anyway — required closeout evidence, not a
  code change.
- `cautilus-non-run-closeout`: Bundle Anyway — required proof honesty, not a
  live eval.
- `dispatch-path-warning`: Bundle Anyway — cheap documentation that prevents
  broad-scan advisory output from being misread as a blocker.
- `substring-marker-risk`: Valid but Defer in review, applied cheaply before
  commit.
- `async-test-risk`: Valid but Defer in review, applied cheaply before commit.

## Deliberately Not Doing

- No live Cautilus run; planner returned `next_action: none`.
- No default broad-scan gate promotion; default output is advisory and may be
  noisy outside selected slow files.
- No issue push/verification claim before a maintainer publishes the local
  commit.

## Next Move

Commit the #299 fix with `Close #299` in the commit body after focused and
surface validation passes. Final issue verification remains a post-push step.
