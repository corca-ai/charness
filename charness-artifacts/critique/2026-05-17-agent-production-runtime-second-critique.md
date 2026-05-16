# Agent Production Runtime Second Critique

## Execution

- Fresh-Eye Satisfaction: `parent-delegated`
- Target: `code-critique`
- Change under review: `7c6fcef Add agent runtime quality lens`
- Packet Consumed:
  `charness-artifacts/critique/2026-05-17-agent-production-runtime-second-critique-packet.md`
- Non-authoritative packet:
  `charness-artifacts/critique/2026-05-16-225907-packet.md` was generated
  without a committed-diff `changed_ref` and was removed from the working set.

## Change

The prior commit added a provider-neutral production LLM/agent runtime lens to
`quality`, synced plugin exports, updated dogfood evidence, and added tests.
This critique checked whether the lens overtriggers, whether proof vocabulary
drifts, and whether the reviewed packet represented the committed diff.

## Angles

- Problem framing: check whether the lens solves production runtime risk rather
  than adjacent docs/concept review.
- Diagnostic cause: check whether the implementation fixes the quality contract
  gap or only records symptoms.
- Counterweight: separate actual pre-ship fixes from optional stronger proof.

## Findings

### Act Before Ship

- Trigger overbreadth was real. `agent-production-runtime.md` and
  `inventory-dispatch.md` allowed user-facing agent product docs or operator
  runbooks as standalone trigger evidence, which contradicted the intended
  serving-path/runtime boundary.

Resolution: tightened the trigger so product docs/runbooks must identify a
concrete serving path, runtime configuration, telemetry surface, or incident
procedure. Added docs-only non-trigger assertions to
`tests/quality_gates/test_quality_skill_docs.py`.

### Bundle Anyway

- `skill-experiment` was too broad as a default Cautilus proof mode for
  cheap-first model routing in ordinary consumer agent apps.

Resolution: narrowed default proof wording to `fixture` or `observation`, with
`skill-experiment` reserved for Charness skill or prompt variants.

- A separate agent-runtime dogfood prompt would exercise the new problem frame
  more directly.

Resolution: deferred. The dogfood registry currently enforces one scaffolded
case per public skill, and adding a second `quality` case would change the
dogfood contract rather than only this lens. Existing observed evidence keeps
the new lens visible until a broader dogfood-contract slice exists.

### Over-Worry

- Generated/export sync was not a real concern. The authoritative packet showed
  both source and plugin export surfaces, and packaging validation remained the
  owning gate.

### Valid But Defer

- The first clean-tree packet was a process issue, not a commit blocker after
  regenerating the authoritative packet with `changed_ref`.
- A realistic consumer fixture can wait until there is a concrete agent-app
  repo shape to test undertrigger and overtrigger behavior.

## Proof

- `pytest -q tests/quality_gates/test_quality_skill_docs.py`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`

## Next Move

Close this as a corrective follow-up commit after full slice closeout passes.
