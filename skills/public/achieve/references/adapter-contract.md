# Achieve Adapter Contract

`achieve` can run without an adapter. Missing adapters resolve to conservative
audit-only publication defaults so a portable skill stays usable in a new repo.
A found adapter is authoritative: if it is malformed, closeout evidence fails
instead of silently falling back.

## Location

Preferred path:

```text
.agents/achieve-adapter.yaml
```

Compatibility fallbacks, in order: `.codex/achieve-adapter.yaml`,
`.claude/achieve-adapter.yaml`, `docs/achieve-adapter.yaml`, and
`achieve-adapter.yaml`.

Resolve it with:

```bash
python3 "$SKILL_DIR/scripts/resolve_adapter.py" --repo-root .
```

## Fields

```yaml
version: 1
repo: charness
language: en
artifact_dir: charness-artifacts/goals
discussion_deploy_vocab:
  - rollout
  - hotfix
closeout_publication:
  default_mode: handoff-only
  issue_closeout_carrier: direct-commit
  require_draft_validation: true
  draft_validation_command_template: "python3 skills/public/issue/scripts/issue_tool.py validate-closeout-draft --repo-root . --repo corca-ai/charness --number {issue_number} --classification {classification} --carrier direct-commit --commit-message-file {commit_message_file}"
  require_post_publication_verify: true
  publish_requires_user_confirmation: true
auto_retro:
  disposition_floor: review-required
  allow_host_blocked_disposition_review_skip: true
  valid_dispositions:
    - applied
    - issue
  allow_none_optout: true
scaffold:
  draft_active_frame_lines:
    - "- Current slice: real draft/backlog awaiting activation."
    - "- Current slice intent: real draft/backlog awaiting activation; reshape before"
    - "  activating if the acceptance boundary has changed. Once active, this names"
    - "  the reviewable-intent unit in progress and the commits it spans; critique"
    - "  and broad proof do not re-fire within one unchanged intent — update it when"
    - "  the intent changes, not per commit (meaningful-slice-cadence)."
    - "- Next action: activate with `/goal @{goal_rel}` after confirming the draft is"
    - "  still intended."
```

`closeout_publication.default_mode` is the default claim boundary. Supported
values are `audit-only`, `handoff-only`, `direct-commit`, `pull-request`,
`release`, and `manual`. `audit-only` means the goal can complete with evidence
but makes no publication claim. `handoff-only` means the closeout may refresh the
next-session baton but still does not imply push, issue closure, release, or live
delivery.

`closeout_publication.issue_closeout_carrier` chooses the carrier the goal should
stage when it resolves tracked issues. Supported values are `none`,
`direct-commit`, `pull-request`, `release`, and `manual`. When the carrier is
`direct-commit` and draft validation is required, the command template must
include `validate-closeout-draft`, `--carrier direct-commit`, and
`--commit-message-file`; this binds `achieve` closeout policy to the `issue`
skill's direct-commit rehearsal contract rather than hand-written memory.

`auto_retro.disposition_floor` controls the local floor before completion.
`review-required` is the normal setting: deterministic gates require evidence
that the disposition review ran or was host-blocked, and `## Auto-Retro` must
disposition surfaced improvements with `applied: <what>` or `issue #N`, unless a
valid `Retro dispositions: none — <reason>` line applies. `deterministic-only`
is for hosts that cannot support fresh-eye review, but it should be explicit in
the adapter because it weakens the normal floor.

`scaffold.draft_active_frame_lines` optionally replaces the default draft
`## Active Operating Frame` lines in newly scaffolded goal artifacts. The field
is a list of rendered markdown lines, including bullet prefixes when desired;
`{goal_rel}` is replaced with the generated
artifact path. Existing artifacts are still idempotent: `upsert_goal.py` updates
only `Status:` on later calls and never rewrites manual frame content.

`discussion_deploy_vocab` optionally provides the consumer-axis deploy /
irreversible-side-effect verbs the pre-activation discussion gate detects (for
example `rollout`, `hotfix`, `redeploy`). When set it **replaces** the portable
English default (`apply/restart`, `restart`, `deploy`); when omitted the English
default applies, so a repo that does not declare it keeps byte-identical
behavior. The charness-neutral concepts (`production`, `live proof`,
`irreversible`, `external side effect`, ...) always apply regardless. This keeps
charness from hardcoding one consumer's boundary vocabulary while never silently
dropping the guard for an unconfigured consumer.

## Closeout Report

`check_goal_artifact.py` attaches an `achieve_adapter_policy` block to the
complete-state evidence report. The block records the resolved publication
default, issue-closeout carrier, draft/post-publication verification flags, and
Auto-Retro disposition floor. Missing adapters are `valid: true`; found invalid
adapters set `valid: false` and block completion.

## Host Goal-Slot Boundary

The host active-goal slot is host-owned, not an `achieve` adapter setting: the
Claude `/goal` Stop-hook and the Codex thread-goal slot are host primitives
`achieve` coordinates but does not reimplement. The portable draft-vs-active
contract is uniform across every host and therefore needs no adapter knob: the
Before-phase is artifact-only and never consumes the host slot, and
`/goal @artifact` pursuit is the only point that does (see `lifecycle.md`
*Drafting does not consume the host goal slot*). Deliberately, no
`goal_slot.*` adapter field exists — a configurable knob here would only be a
no-op that fakes portability. A host that auto-activates the slot on artifact
creation is a host-runtime limitation to record as a non-claim, not an
adapter-configurable behavior.
