# Quality Review
Date: 2026-08-05
Title: Issue 504 Retro Persistence Closeout

## Scope

Target boundary: `retro` goal-aware persistence, its achieve caller contract,
source/plugin parity, and the #504 closeout proof. No new quality gate or
semantic lesson-quality policy is proposed.

Ambient repo findings: the existing quality gate warnings and #511 quality
record are prior-slice context, not repairs in this closeout.

## Current Gates

Focused persistence/goal/disposition proof passed 115 tests. Source and plugin
copies for the six affected runtime/instruction surfaces are byte-identical.
The critique artifact validated; the issue closeout draft returned
`draft_verified`; local pre-push passed 14 checks; remote Quality Core run
30999412722 passed both core deterministic and changed-line mutation jobs; and
the GitHub adapter returned #504 `CLOSED` through `verify-closeout`.

## Runtime Signals

- runtime source: timing capture is missing; no production timing capture was required for this local file-identity slice. <!-- reproduction-source -->
- runtime hot spots: not measured; focused proof is deterministic pytest and adapter readback.
- coverage gate: focused proof, pre-push docs/artifact subset, and remote changed-line mutation coverage passed.
- evaluator depth: deterministic-gates-only; Cautilus was not invoked under its ask-before-run contract.

## Healthy

- The shared writer validates exact goal identity before artifact, summary/index,
  event, or output-directory writes and canonicalizes accepted slug input.
- Goal-aware mode is explicit; ordinary session/release mode remains goal-free.
- Achieve/retro instructions name the canonical `--goal-path` contract, while
  the final achieve consumer remains defense in depth.
- Direct-library, CLI-success, malformed/mismatch, full-tree no-write,
  canonicalization, and legacy behavior are covered by the focused suite.
- Source/plugin mirrors, the delegated resolution critique, carrier, and
  adapter state readback are synchronized and independently recorded.

## Weak

- `--goal-path` remains opt-in, so live-agent argument propagation is not
  mechanically proven; the carrier correctly renders this as
  `local-only-by-contract` rather than host-verified behavior.
- Expected identity errors currently expose a Python nonzero failure rather
  than a custom concise CLI diagnostic; this does not weaken pre-write refusal.

## Missing

- Installed-host, provider, and live-agent invocation behavior remain
  unobservable in this repository and are not claimed.
- No Cautilus or production runtime proof was requested.

## Deferred

- A cleaner subprocess-level CLI refusal diagnostic/test is deferred until a
  concrete recurrence or operator request justifies widening #504.
- Host-level proof of prompt-to-CLI `--goal-path` propagation is a separate
  integration concern, not a new local closeout floor.

## Advisory

- structural review result: the `plan_quality_run.py --target-skill retro`
  packet identifies the shared writer plus explicit caller contract as the
  current owner; no new gate is needed.
- prose review result: `skills/public/retro/SKILL.md` and
  `references/trigger-and-persistence.md` provide progressive disclosure for
  goal-aware versus session persistence; the critique records the host-boundary
  non-claim.
- inventory advisory: no new inventory was needed; the exact focused command,
  115-test result, source/plugin `cmp`, and remote run are recorded above and
  in the issue carrier.

## Delegated Review

- Delegated Review: not_applicable — the required fresh-eye judgment ran as the
  issue-resolution critique in `charness-artifacts/critique/2026-08-05-issue-504-resolution-closeout-critique.md`.
- Slow-gate lenses (fixture-economics, parallel-critical-path, duplicated-proof): not_applicable — no standing slow-gate scope changed.

## Commands Run

- `python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_retro_persistence.py --pytest-target tests/quality_gates/test_goal_artifact_lib.py --pytest-target tests/quality_gates/test_goal_disposition_gate.py` — 115 passed.
- Six source/plugin `cmp` checks — passed; `validate_critique_artifacts.py` — passed.
- `issue_tool.py validate-closeout-draft` — `draft_verified`; local pre-push — 14 passed, 0 failed.
- `gh run watch 30999412722 --repo corca-ai/charness --exit-status` — both remote jobs passed.
- `issue_tool.py verify-closeout --expect-state CLOSED --commit-ref 5372631a1279993753bb7efe605ace19eb27f18d` — `status: verified`, #504 CLOSED.

## Recommended Next Quality Moves

- passive — capability_needed=live-agent invocation telemetry; next_center=retro/achieve caller boundary; transformation=measure a real host roundtrip if that capability becomes available; proof_boundary=agent-to-helper argument propagation; enforcement_posture=no-gate because the local contract is already explicit and the host channel is unavailable.
- passive — capability_needed=concise CLI validation diagnostics; next_center=retro persistence operator surface; transformation=add stable stderr and subprocess negative coverage after recurrence; proof_boundary=CLI process behavior; enforcement_posture=existing-gate-reuse because current pre-write tests already protect the issue JTBD.

## History

- [Previous quality review](history/2026-07-19-portable-proof-path-learning-review.md)
