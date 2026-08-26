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
`.claude/achieve-adapter.yaml`, `<repo-root>/docs/achieve-adapter.yaml`, and
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
interview:
  max_questions: 15
  allow_provisional_local_fallback: false
discussion_deploy_vocab:
  - rollout
  - hotfix
release_surface_tokens:
  - ./ops/ship-it.sh
closeout_publication:
  default_mode: handoff-only
  issue_closeout_carrier: direct-commit
  require_draft_validation: true
  draft_validation_command_template: "python3 <plugin-dir>/skills/issue/scripts/issue_tool.py validate-closeout-draft --repo-root . --repo corca-ai/charness --number {issue_number} --classification {classification} --carrier direct-commit --commit-message-file {commit_message_file}"
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
    - "- Next action: after approval, resume the provider-backed run with `/goal #<parent>`."
  execution_efficiency_context_path: docs/execution-efficiency.md
```

`interview.max_questions` is the maximum number of operator questions in one
goal-shaping interview. It defaults to 15, accepts any positive integer, and is
a ceiling rather than a target. Zero, negatives, booleans, strings, and
fractions invalidate the adapter. Reaching the ceiling with consequential
decisions unresolved yields `interview-cap-reached` and blocks parent creation;
the skill never truncates unresolved decisions.

`interview.allow_provisional_local_fallback` defaults to `false`. When false,
missing parent-update or sub-issue backend capability blocks activation. `true`
permits an explicitly provisional local continuation for offline/non-GitHub
hosts; it does not create GitHub identity claims and must reconcile into a
verified parent before authority moves.

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

`scaffold.execution_efficiency_context_path` optionally adds one
repo-relative execution-efficiency context pointer after the default or custom
active-frame lines. The configured path must resolve to an existing regular file
within the repository. Missing paths, directories, absolute or escaping paths,
and symlinks whose targets escape the repository invalidate the adapter and
refuse new goal scaffolding. An in-repository symlink to a regular file is valid.
The pointer is guidance for Before-phase shaping and resumed-goal pickup; it is
not a new completion floor, and it does not replace `draft_active_frame_lines`.

`discussion_deploy_vocab` optionally provides the consumer-axis deploy /
irreversible-side-effect verbs the pre-activation discussion gate detects (for
example `rollout`, `hotfix`, `redeploy`). When set it **replaces** the portable
English default (`apply/restart`, `restart`, `deploy`); when omitted the English
default applies, so a repo that does not declare it keeps byte-identical
behavior. The charness-neutral concepts (`production`, `live proof`,
`irreversible`, `external side effect`, ...) always apply regardless. This keeps
charness from hardcoding one consumer's boundary vocabulary while never silently
dropping the guard for an unconfigured consumer.

`release_surface_tokens` optionally ADDS release surfaces the built-in list does
not name. The release coordination floor already recognises ecosystem-standard
version manifests and publish commands (`pyproject.toml`, `package.json`,
`Cargo.toml`, `npm publish`, `git tag`, ...), and a repo whose release runs
through something bespoke — an internal deploy script, a house manifest —
declares it here so the floor is armed for that repo too. Unlike
`discussion_deploy_vocab` this field EXTENDS rather than replaces, so declaring it
can only make the floor fire more often, never less. Omitting it keeps the
built-in list alone.

Why it exists at all: a floor that recognises only its authoring repo's surface
names is silently inert everywhere else, which is worse than no floor because it
reads as coverage. This field is the seam that lets a consumer re-arm it without
waiting for charness to learn their layout.

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
`/goal #N` pickup is the only point that does (see
`lifecycle-before.md` *Drafting does not consume the host goal slot*).
Deliberately, no `goal_slot.*` adapter field exists — a configurable knob here
would only be a no-op that fakes portability. A host that auto-activates the
slot on artifact creation is a host-runtime limitation to record as a
non-claim, not an adapter-configurable behavior.
