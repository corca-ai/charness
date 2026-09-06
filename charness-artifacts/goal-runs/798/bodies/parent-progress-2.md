# Reduce consumer rework through coherent judgment, faithful evidence, and proven skill journeys

## Problem and impact

Current verification guidance differs across owner documents; release output
turns advisory evidence limitations into confirmed inaccuracies; generic skill
cases do not establish the complete spec-to-impl and existing-script CLI consumer
journeys. These seams can make agents repeat decisions and overstate proof.

## Approved outcome

Align verification ownership, preserve release advisory meaning, exercise and
improve both consumer journeys on fixed comparative inputs, and remove observed
duplicate work without losing capability. Integrate, independently review, push
and release the completed result. Repair encountered friction within these seams.

## Authority and planning

The operator requested this Goal on 2026-09-06 and explicitly delegated remaining
choices, friction repair, final push and release. Planning and both review rounds
are complete; the repaired whole received a separate file-backed worker pass.
No milestone was requested, so this Goal is unassigned.

- Frozen planning record: charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.md
- Framing review: charness-artifacts/critique/workers/consumer-plan-framing-live/worker-report.yaml
- Final pre-binding review: charness-artifacts/critique/workers/consumer-plan-whole/worker-report.yaml
- First operational findings: charness-artifacts/probe/2026-09-06-consumer-plan-proof-findings.json

## Work Items and execution order

1. contract-ownership — consistent ordinary, proof-surface and release verification.
2. evidence-meaning — faithful final report rendering with legacy compatibility.
3. spec-impl-journey — direct consumer handoff and implementation proof.
4. cli-journey — existing-script compatibility and coherent CLI behavior.
5. friction-reduction — demonstrated repeated-work removal with preserved acceptance.
6. publish-closeout — integrated proof, release, direct readback and guarded close.

Dependencies are local acceptance readiness, not premature provider closure.
A prerequisite is ready when implementation, focused proof and applicable
independent review identify the integrated revision and only publication remains.
The final publication child may then start while the other children stay OPEN.
After public carrier verification and behavioral evidence binding, close the
implementation children, publication child, then this parent.

## Current frontier

Contract ownership and evidence rendering are locally ready in integrated code
at 1479ab08a (behavior-bearing code reviewed at 42fd204e1; unchanged thereafter).
Focused release tests passed 56; review/path/seed tests passed 33 after the
nonblocking fake-backend marker repair. The separate code/contracts review is
charness-artifacts/critique/workers/goal798-code-contracts/worker-report.yaml.
The first integrated changed-line run covered all three mapped changed files.

Consumer protocol revision 3 is frozen and independently approved:
charness-artifacts/critique/workers/goal798-consumer-oracle-r3/worker-report.yaml.
The v8.4.3 alias-spec and CLI migration baseline contexts are now running.
No completed consumer acceptance or release is claimed yet.

Preview recovery is removed in a paired final-wrapper observation: both packet
modes require one renamed recovery invocation on v8.4.3 and none after repair,
while each starts exactly one backend. Source and commands are retained in
charness-artifacts/probe/2026-09-06-preview-recovery-comparison.json.

All six Work Items remain OPEN pending final published-carrier proof and
behavioral binding. Next local action: observe baseline handoffs and run the
identical candidate journeys; the parent owns integration and release.

## Completion evidence

Exact child graph, per-child acceptance/observer/revision evidence, integrated
verification, final release identity and separate provider readback. A green
gate, public tag page, or CLOSED state alone does not establish behavior.

<!-- charness-goal-run:v1
{
  "binding_schema": "charness.goal-binding/v1",
  "binding_path": "charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.binding.json",
  "binding_sha256": "88ec9430391af0d4843d57bcb12337fbe89f7e2f9c3861dd98b73fd55cf02ac1",
  "draft_path": "charness-artifacts/goals/2026-09-06-autonomous-consumer-improvement.md",
  "draft_sha256": "2d7db581aa37bcd88442a37282fe1f74ff0b544220637b3bf830d27a321e1bea",
  "initial_graph_sha256": "6e64a91ebe8949e168ca07853481d413b348f75d1ad19cc7ced974b164079514",
  "bootstrap_verification": "verified-target-roundtrip",
  "parent_identity": {
    "repo": "corca-ai/charness",
    "number": 798,
    "url": "https://github.com/corca-ai/charness/issues/798"
  },
  "progress": {
    "schema": "charness.goal-progress/v1",
    "revision": 2,
    "total": 6,
    "completed": 0,
    "open": 6,
    "next": {
      "key": "spec-impl-journey",
      "repo": "corca-ai/charness",
      "number": 801,
      "url": "https://github.com/corca-ai/charness/issues/801",
      "state": "OPEN"
    }
  }
}
-->
