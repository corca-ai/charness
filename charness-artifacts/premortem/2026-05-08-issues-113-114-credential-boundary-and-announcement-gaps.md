# Premortem — Issues 113 & 114

Date: 2026-05-08
Decisions under review:

- **#113** — Charness skills/manifests must not advertise raw credential env
  fallback (`SLACK_BOT_TOKEN`, `GOOGLE_WORKSPACE_CLI_*`,
  `GH_TOKEN`/`GITHUB_TOKEN`) as agent-consumable paths. Capability resolution
  redesigned from XDG machine-local config (`~/.config/charness/...`) to
  repo-local (`<repo-root>/.charness/local/capability.json` gitignored,
  `.charness/capability.example.json` committed). XDG paths and
  `--home-root` flag on capability subcommands retired with no compat shim
  per explicit user direction.
- **#114** — `announcement` skill gains audience-tone enforcement, inline
  draft-body guardrail, dual-output (`outputs` adapter field with
  `delivery_role: single|parent|thread_reply`), in-progress source hint
  (`in_progress_sources`), Slack mrkdwn rules in `delivery-seams.md` plus
  adapter-declared `format_rules_path`, and per-backend size-limit splitting
  (`message_size_limit`).

## Success Criteria

- Charness skills/manifests no longer present raw env fallback as the
  agent-consumable path. `gather-slack`, `gws-cli`, `create-cli`, and
  `create-skill` references re-state operator-only env paths.
- Repo-local capability config replaces XDG layout end-to-end across CLI,
  tests, docs, plugin export.
- `announcement` adapter validates legacy inputs unchanged while accepting the
  new fields with safe defaults.
- Quality gates pass; checked-in plugin export sync clean.

## Out of Scope

- A `charness capability migrate` subcommand (user explicitly declined).
- Compatibility shim that reads the retired XDG layout.
- Forcing `gather-slack` `vendor/slack-api.mjs` to refuse `SLACK_BOT_TOKEN`
  when present in the operator-local CLI shell — operator paths remain
  honored, contracts re-stated.
- A doctor warning for stale `~/.config/charness/capability-*.json` (deferred).

## Angles

Four bounded fresh-eye subagents reviewed independently:

1. **Breaking-change risk** on already-onboarded charness users.
2. **Contract regression** across changed surfaces (CLI, scripts, references,
   plugin export, tests).
3. **Adapter forward-compatibility** for the `announcement` skill.
4. **Counterweight** — separate real blockers from over-worry.

## Triage

### Act Before Ship

- None. All four reviewers returned no blockers. Plugin export `diff -q`
  clean; no leftover references to `MATCHED_REPO_KEY`,
  `capability-profiles.json`, `repo-bindings.json`, `repo_binding_keys`,
  `canonical_repo_remote_id`, or `--home-root` on capability subcommands.
- Breaking-change reviewer flagged one cheap addition: name the retired XDG
  layout in `capability_setup_guidance` so old runbooks have a grep-back.
  **Bundled into this PR.**
- Contract-regression reviewer flagged one cheap addition: a back-compat unit
  test exercising a legacy adapter through `validate_announcement_adapter_data`.
  **Bundled into this PR** as `tests/test_announcement_adapter_lib.py`.

### Bundle Anyway

- (Bundled, see Act Before Ship.)

### Over-Worry

- "Operators will lose bindings on the upgrade with no migration." Rejected:
  the user explicitly accepted the breaking change for the small user count
  and declined a migration helper.
- "`gather-slack/scripts/export-thread.sh` may degrade silently when the new
  capability config is absent." Rejected: the script already exits 1 with an
  explicit message naming the new path before any Slack call.
- "Mass `--home-root` and `default_home_root()` matches across charness." Top
  level CLI commands (`init`, `update`, `doctor`, `version`, `uninstall`,
  `reset`, `tool ...`) intentionally keep `--home-root`; only capability
  subcommands lost it. No regression.
- "Adapter validator may reject legacy adapters that lack the new fields."
  Rejected: `infer_announcement_defaults` seeds the new fields and
  `_validate_outputs` / `_validate_in_progress_sources` early-return on `None`.

### Valid but Defer

- Tighten `docs/control-plane.md` and `docs/runtime-capability-contract.md`
  XDG mentions to clarify that the cache/install/state layers stay XDG-based
  (only capability resolution moved repo-local). Documentation polish, no
  behavior bug.
- A `charness doctor` check that warns when stale
  `~/.config/charness/capability-profiles.json` is still present. Nice-to-have
  for the few existing users; not blocking.
- A warning in `_validate_outputs` when `delivery_role: thread_reply` appears
  without a prior `parent`. Adapter-shape polish; not blocking.
- A warning when an `outputs[]` entry has empty `audience_tags` (orphan
  output). Adapter-shape polish; not blocking.

## Closeout

- Premortem path: subagent-delegated (3 angles + 1 counterweight, parallel).
- Fresh-eye satisfaction: parent-delegated.
- Decision: ship. Two cheap improvements bundled (XDG-retirement guidance,
  adapter back-compat test).
