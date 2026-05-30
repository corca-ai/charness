# Critique — Codex Find-Skills Hook Cleanup

**Target:** pending diff for Codex/find-skills SessionStart hook cleanup.
**Packet consumed:** `charness-artifacts/critique/2026-05-30-231612-packet.md`.
**Fresh-Eye Satisfaction:** parent-delegated.

## Change

Make `charness update`/hook reconcile converge the Codex user-level find-skills
SessionStart hook to one representation:

- keep the intended `usage-episodes` hook separate;
- preserve foreign hooks;
- migrate the legacy `# charness:find-skills session-start routing trigger (#240)`
  TOML block to the canonical `# charness:find-skills-routing` block;
- add `matcher = "startup|resume|clear"` to the canonical Codex TOML block;
- remove charness-owned find-skills TOML blocks when Codex target selection moves
  to `hooks.json`.

Usage-episodes cross-representation cleanup remains out of scope and documented
as deferred in `docs/deferred-decisions.md`.

## Angles

- Correctness/idempotency fresh-eye review: `019e7b2c-c6d3-7553-9a89-4ff4df1dc71a`.
- Operator/install-surface fresh-eye review: `019e7b2c-e833-72c2-b4e8-26e5ec77abd4`.
- Counterweight review: `019e7b2d-03ec-7c83-b65c-a769f901173c`.

## Findings

### Act Before Ship

1. `find_charness_toml_block` originally treated a following unmarked
   `[[hooks.SessionStart]]` parent table as part of the current charness block,
   so matcher canonicalization or uninstall could remove a foreign SessionStart
   hook. Fixed by stopping the scanner at the next parent table while still
   allowing the `[[hooks.SessionStart.hooks]]` child table. Added
   `test_find_skills_codex_update_preserves_following_foreign_sessionstart`.

### Bundle Anyway

1. Disabled/status paths could leave the legacy find-skills TOML block firing
   while reporting disabled/in-sync. Fixed by reusing legacy cleanup in
   `uninstall_find_skills_codex_hook` and making status report legacy markers as
   drift. Added `test_find_skills_codex_disabled_removes_legacy_only_block`.
2. The most likely real migration shape is legacy-only TOML, not only
   legacy-plus-canonical. Added
   `test_find_skills_codex_reconcile_migrates_legacy_only_block`.
3. JSON-target cleanup should prove it preserves foreign hooks. Added a
   `PreToolUse` preservation assertion.

### Over-Worry

- Expanding this patch to usage-episodes cross-representation cleanup would be
  scope creep; D23 continues to defer that case.

### Valid But Defer

- `install_codex_toml_block` can canonicalize matching charness-owned TOML
  blocks. Hand-edited usage-episodes recovery stays deferred under D23.
- A JSON install can return `action: noop` while `legacy_cleanup` removed TOML
  blocks. That reporting shape is acceptable for this slice because the cleanup
  detail is explicit and status converges.

## Verification

- `pytest -q tests/test_find_skills_host_hook_reconcile.py tests/test_usage_episodes_host_hooks.py`
  passed after critique fixes (`41 passed`).
- Live reconcile against this machine removed the duplicate legacy Codex
  find-skills TOML block: `find_skills_routing.codex.result.action=updated`,
  `legacy_cleanup[0].action=removed`, then status reported `in_sync: true`.
