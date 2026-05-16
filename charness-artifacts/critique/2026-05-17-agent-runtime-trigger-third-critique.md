# Agent Runtime Trigger Third Critique

## Execution

- Fresh-Eye Satisfaction: `parent-delegated`
- Target: `code-critique`
- Change under review: `71119a6 Tighten agent runtime quality triggers`
- Packet Consumed:
  `charness-artifacts/critique/2026-05-17-agent-runtime-trigger-third-critique-packet.md`

## Change

The prior corrective commit narrowed the production LLM/agent runtime quality
lens so docs-only agent product descriptions would not trigger runtime review.
This critique checked whether that correction fixed the cause or only patched
the symptom.

## Angles

- Problem framing: did the correction solve trigger overbreadth without
  over-narrowing real runtime signs?
- Diagnostic cause: can docs or runbooks still self-certify runtime evidence?
- Operational checklist: are the critique packet and recurrence tests durable
  enough for future reviewers?
- Counterweight: separate blockers from dogfood-contract and export-sync worry.

## Findings

### Act Before Ship

- Trigger overbreadth was still partly open. The source reference said
  docs/runbooks could trigger when they merely identified a serving path,
  runtime configuration, telemetry surface, or incident procedure. That still
  allowed docs to self-certify production runtime evidence.

Resolution: tightened the source reference to require product docs/runbooks to
be paired with serving-path code, runtime configuration, telemetry, or concrete
incident/runtime evidence. Added explicit wording that docs/runbooks merely
naming a provider, serving path, or conceptual procedure do not trigger without
corroborating runtime evidence.

- The initial third critique packet used a symbolic `HEAD^..HEAD` changed ref
  and a stale label.

Resolution: regenerated the packet with explicit
`71119a6^..71119a6` changed-ref and a third-critique label.

### Bundle Anyway

- The test pinned docs-only exclusion but not the positive invariant that
  docs/runbooks require paired runtime evidence.

Resolution: added test assertions for the paired-runtime-evidence wording in
both `agent-production-runtime.md` and `inventory-dispatch.md`.

- The test did not guard against over-narrowing real runtime signs.

Resolution: added assertions that model/API clients in serving paths,
routing/fallback config, streaming endpoints, tool/action queues, and runtime
telemetry remain trigger evidence.

### Over-Worry

- Generated/export sync was not an independent concern. Source and plugin
  copies are synced by `sync_root_plugin_manifests.py` and packaging validation
  owns the export check.

### Valid But Defer

- A dedicated agent-runtime dogfood prompt remains useful but belongs to a
  dogfood-contract slice because the current registry validates one scaffolded
  case per public skill.

## Proof

- `pytest -q tests/quality_gates/test_quality_skill_docs.py`
- `python3 scripts/validate_skills.py --repo-root .`
- `python3 scripts/validate_packaging.py --repo-root .`
- `python3 scripts/validate_packaging_committed.py --repo-root .`

## Closeout Status

Closed by commit `0efa557 Require runtime evidence for agent docs triggers`
after full slice closeout passed.
