<!-- charness-work-item-key: goal-binding-v1 -->
# Freeze A Full Goal Draft And Validate Goal Binding V1

## Purpose

Own the immutable `charness.goal-binding/v1` sidecar that binds the approved
Goal Draft to one exact Goal Run parent and one canonical initial work-item
manifest.

## Bounded contract

- Consume only the approved frozen draft and briefing identity recorded in the
  local planning artifacts.
- Serialize canonical UTF-8 JSON and compute complete-byte SHA-256 values.
- Refuse unknown schema, state/progress fields, path escape or symlink traversal,
  draft drift, parent mismatch, graph mismatch, policy mismatch, dependency
  cycles/rank errors, and duplicate reused issue identities.
- Create the deterministic `.binding.json` sibling once with an exclusive,
  durable atomic write. A later change requires new approval and a new binding.

## Acceptance and verification

The validator distinguishes structural-only validation from parent-bound
authority. A create/reuse/preserve matrix, malformed-input negatives, clean
process readback, and source/plugin parity are covered by:

```bash
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_goal_binding_v1.py
python3 scripts/check_python_lengths.py --repo-root . --paths skills/public/achieve/scripts/goal_binding.py skills/public/achieve/scripts/goal_binding_support.py plugins/charness/skills/achieve/scripts/goal_binding.py plugins/charness/skills/achieve/scripts/goal_binding_support.py
python3 scripts/sync_root_plugin_manifests.py --repo-root .
```

## Evidence boundary

This child proves the local schema and freeze/readback surface. It does not
claim GitHub mutation, installed-host adoption, `/goal` pickup, issue closure,
release, tag, or push.
