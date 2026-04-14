# Support Tool Follow-Up

This document captures the next `charness` workstream after the support-skill
materialization redesign and the `cautilus` integration tightening pass.

The goal is not to reopen the already-closed control-plane decision. The goal
is to apply the portable lessons from that work to public skills, dogfood those
skill changes inside `charness`, and keep issue triage explicit.

## Scope

- decision window: 2026-04-13 support-tool follow-up planning
- upstream context: `cautilus` consumer-integration issues were picked up and
  resolved upstream
- local prerequisite already landed: cache-backed user-cache materialization +
  repo-local support-skill symlink exposure

## Current Decisions

- Portable skill bodies should not depend on Claude-style `!` execution.
- Support skills stay locally consumable through cache-backed materialization
  plus repo-local symlinks.
- `external_skill` and `external_binary_with_skill` both materialize a local
  support-skill surface. The difference is binary lifecycle, not support-skill
  discoverability.
- Prefer upstream-provided support skills when their shape is usable as-is.
  Keep `local_wrapper` as an exception path for oversized, host-specific, or
  otherwise unsuitable upstream surfaces.
- Every `charness` change in this area should end in both:
  - source-of-truth skill updates
  - `charness` dogfood on the changed skill surface

## Context To Preserve

These points came from the full support-tool discussion and should not be lost
even if the next session only skims this document.

- The recent `cautilus` work was a trigger, not the product-specific center of
  gravity. The intended output is a portable `charness` pattern for support
  binaries and agent-facing command surfaces, not a one-off `cautilus`
  accommodation.
- The maintainer and the downstream `charness` user should see the same support
  skill surface. If `charness` says a binary is supported-with-skill, the skill
  must be locally readable and usable for both dogfood and downstream use.
- That requirement does **not** justify vendoring upstream skill clones into
  the tracked repo. The current answer is user-cache materialization plus
  repo-local symlink exposure.
- Prefer upstream-provided skill content when it is usable as-is. A
  `charness`-owned wrapper is an exception path, not the new default.
- The old `reference` support-sync model is intentionally gone from the active
  plan. Provenance still matters, but not as a substitute for a consumable
  local skill surface.
- `external_skill` versus `external_binary_with_skill` should now be read as a
  binary-lifecycle distinction:
  - both materialize support skills locally
  - only the latter adds install/update/detect/healthcheck/readiness contract
- The recommendation/install requirement is stronger than passive discovery.
  When a public skill genuinely depends on or materially benefits from an
  external tool, `charness` should proactively surface that route, explain why,
  and point to the exact install and verification path instead of leaving the
  operator to rediscover it.
- The rejected `!` plan is an intentional portability choice, not an accident
  to revisit casually. The session conclusion was:
  portable skill source should not depend on host-specific shell-execution
  semantics inside `SKILL.md`.
- The next slices should keep issue-driven work and dogfood tightly coupled.
  This workstream is not complete when the skill prose changes; it is complete
  when the changed skill has been run against `charness` itself and any exposed
  repo-surface honesty gap is either fixed or recorded durably.

## Issue Triage

### Close Now

- `corca-ai/cautilus#2`
  Resolved upstream. The `--help` and probe-contract gaps were the real product
  issue, and the old skill-discoverability concern is no longer a blocker on
  the `charness` side because support skills are now always materialized.

- `corca-ai/charness#9`
  Landed. `create-cli` now separates no-side-effect help, machine-readable
  command discovery, binary/runtime health, repo/install readiness, and local
  discoverability directly in the public skill contract.

- `corca-ai/charness#10`
  Landed. `quality` now inspects installable CLI probe layers explicitly,
  checks README / INSTALL / operator docs for probe-contract drift, and
  requires exact install/verify guidance when a missing external tool blocks
  deeper local proof.

- `corca-ai/charness#13`
  Landed as the second-wave `quality` follow-on. The quality adapter now has
  `specdown_smoke_patterns` and `coverage_fragile_margin_pp`, and the public
  skill now calls out executable-spec smoke-vs-behavior ratios, pytest/specdown
  overlap, and fragile coverage-floor tagging.

- `corca-ai/charness#11`
  Landed. `init-repo` now points installable-surface repos at an explicit probe
  surface, keeps that guidance narrow, and teaches `README.md` / `INSTALL.md`
  to name install, healthcheck, discovery, readiness, and local
  discoverability semantics without forcing boilerplate onto repos that do not
  ship installable surfaces.

- `corca-ai/charness#14`
  Landed. `quality` now treats prior artifacts as non-authoritative scope,
  adds a fresh-eye premortem step, carries adapter-owned blind-spot policy
  (`coverage_floor_policy`, `spec_pytest_reference_format`), and ships
  reference implementations for unfloored-file inventory and
  `Covered by pytest:` note validation. The second premortem refinements also
  shaped the reference posture: glob-based gate discovery, lefthook/CI
  meta-checks, contradiction detection, exemption-path existence checks, and
  an explicit honesty note that pytest-reference validation proves collection,
  not behavior binding.

- `corca-ai/charness#12`
  Close as declined in its current form. `charness` should not recommend
  `git push` as the generic local verification primitive because push is an
  external side effect, not a safe repo-local check. If this problem is worth
  revisiting later, the portable shape is:
  detect repo-owned parallel hook runners or hook entrypoints, and run those
  directly without treating network mutation as the verification command.

  Preserve the underlying lesson, though:

  - verification-command selection is still too manual today
  - the real follow-up is not "prefer push"
  - the real follow-up is "prefer repo-owned verification bundles or explicit
    hook entrypoints when they already exist, and otherwise fall back to
    surface-based validator selection"

### Not In This Workstream

- `corca-ai/charness#8`
  Valid, but not the main support-tool follow-up slice.

- `corca-ai/charness#7`
  Valid, but separate from the probe-contract and recommendation/install work.

## Planned Application

### 1. `create-cli`: Split Probe Layers Explicitly

Apply `#9`, but tighten it into a portable contract rather than a
`cautilus`-specific anecdote.

Status:

- Landed on 2026-04-13 in `charness`.
- The public skill now explicitly separates help, command discovery, health,
  readiness, and local discoverability.
- `charness` CLI `--help` surfaces were re-checked against that stronger
  contract in the same slice.

Required shape:

- name the no-side-effect `subcommand --help` contract explicitly
- distinguish machine-readable command discovery from help text
- distinguish binary/runtime health from repo/install readiness
- distinguish local agent/plugin/materialized-surface discoverability from
  general binary health
- explain when `doctor` should stay readiness-focused instead of absorbing all
  probe semantics

Expected repo changes:

- update [skills/public/create-cli/SKILL.md](../skills/public/create-cli/SKILL.md)
- strengthen the relevant `create-cli` references, especially command-surface
  and quality-gate guidance
- add or tighten a repo-owned smoke/eval check if `charness` now expects this
  posture from installable CLIs

Dogfood requirement:

- re-read the root [charness](../charness) CLI and the `tool` subcommands
  through the updated `create-cli` contract
- if the strengthened skill exposes an honesty gap, fix the repo surface in the
  same slice instead of leaving the gap as theory

### 2. `quality`: Add Installable-CLI Probe-Contract Posture

Apply `#10`, but keep it bounded to repos that actually ship an installable CLI
or agent-facing command surface.

Required shape:

- inspect whether probe layers are separated honestly
- treat local support-skill/materialization readiness as distinct from binary
  health
- inspect README / INSTALL / operator docs for probe-contract drift
- recommend deterministic enforcement when the missing check is cheap enough to
  own locally
- if a missing binary or support tool materially weakens confidence, recommend
  installation with an exact route instead of vague prose

Expected repo changes:

- update [skills/public/quality/SKILL.md](../skills/public/quality/SKILL.md)
- strengthen or add `quality` references that encode this posture explicitly
- add a cheap repo-owned gate only when the next deterministic move is clear

Dogfood requirement:

- run `quality` against `charness` after the skill update
- update [skill-outputs/quality/quality.md](../skill-outputs/quality/quality.md)
  with the new findings or confirmation that the new lens passes cleanly

### 2a. `quality`: Executable-Spec And Coverage Fragility Follow-On

Treat `#13` as a second-wave `quality` slice after the probe-contract posture
work is stable.

Why it is valuable:

- it sharpens executable-spec economics beyond the current generic overlap
  guidance
- it gives adapter-owned configuration a clean place to describe repo-specific
  smoke patterns or fragile margins
- it turns a real review miss into a portable follow-up instead of one repo's
  private lore

Why it is not first:

- the immediate cross-repo lesson from the recent support-tool work is still
  probe-contract posture, not specdown heuristics
- the acceptance criteria in `#13` are more adapter-specific, so they should
  build on a stable first-wave `quality` contract instead of landing mixed into
  the first rewrite

Expected shape when picked up:

- extend `quality` behavior-lens guidance for executable-spec smoke vs
  behavior classification
- extend executable-spec references so explicit pytest/specdown delegation and
  duplicate assertion patterns are called out directly
- decide whether adapter schema should carry repo-specific smoke patterns and
  fragile coverage margin thresholds
- if those adapter knobs land, teach sample presets honest defaults instead of
  pretending one repo's threshold is universal

### 3. Recommendation And Install Flow

This is the direct product requirement from the recent discussion, not only an
issue-derived follow-up:

If a public skill depends on, strongly benefits from, or should honestly
recommend a support binary, `charness` should say so proactively, explain why,
and surface the install/verify path instead of hiding it behind operator
rediscovery.

First implementation slice:

- add one shared helper that combines manifest metadata with current
  detect/healthcheck/readiness/support-sync state
- return a structured recommendation payload rather than prose-only advice
- consume that helper first from `find-skills`
- then reuse it from `quality` when a missing tool blocks stronger local proof

Status:

- The first code seam landed on 2026-04-13.
- `find-skills` now has a structured recommendation payload through
  `list_capabilities.py --recommend-for-skill <skill-id>`.
- `quality` now reuses the same shared payload through
  `skills/public/quality/scripts/list_tool_recommendations.py` when a missing
  validation tool blocks stronger local proof.
- Integration manifests may now declare:
  - `supports_public_skills`
  - `recommendation_role` (`runtime` or `validation`)
- Current dogfood proof in `charness`:
  - `gather` surfaces `gws-cli` as `runtime` and `cautilus` as `validation`
  - `spec` surfaces `cautilus` as `validation`
- the `quality` dogfood path now surfaces `cautilus` as a blocking validation
  tool with exact install docs and a repo-owned verify command.
- What still remains:
  - route this payload through more public-skill flows beyond `find-skills` and
    `quality` only when there is a concrete next consumer

Required payload fields:

- why this tool is recommended
- current detect/healthcheck/readiness/support-sync status
- supported install route or explicit manual path
- post-install verification command
- next public skill or workflow to continue with

Likely touch points:

- [skills/public/find-skills/SKILL.md](../skills/public/find-skills/SKILL.md)
- [skills/public/find-skills/scripts/list_capabilities.py](../skills/public/find-skills/scripts/list_capabilities.py)
- shared control-plane helpers under `scripts/`
- possibly [docs/control-plane.md](control-plane.md) if the operator-facing
  contract needs one small addition

Dogfood requirement:

- run the recommendation flow on `charness` for at least:
  - one tool that is already installed
  - one tool that is manual-only or currently missing
- verify that the structured output and any persisted machine state stay honest

### 4. `init-repo`: Follow-On, Not Next

Transform `#11` into a follow-on that only lands after the first three slices.

The intended shape is small:

- when a repo actually ships an installable CLI or local agent/plugin surface,
  `init-repo` may recommend a small probe-surface doc section
- do not add boilerplate before the probe-contract language stabilizes in
  `create-cli` and `quality`

## Explicit Non-Goals For The Next Slice

- do not reopen support-skill materialization unless a concrete regression
  appears
- do not reintroduce `reference` as an operator-facing support-sync mode
- do not depend on `!` execution in portable skill bodies
- do not treat `git push` as the generic local verification command
- do not vendor upstream support-skill clones into the tracked repo

## Verification Selection Note

This session also surfaced a narrower verification problem that should stay
attached to the support-tool follow-up context.

Current honest state:

- validation choice still depends partly on operator judgment plus `AGENTS.md`
  conventions
- this is better than ad hoc guessing, but it is not yet a strongly
  repo-owned verifier-selection seam
- the closed `git push` issue was really pointing at wasted manual verifier
  selection, not at push itself

Status:

- landed on 2026-04-14 as `scripts/select_verifiers.py`
- the helper now maps changed paths through `.agents/surfaces.json`, returns
  the smallest repo-owned sync/verify bundle, and names uncovered paths as a
  real missing-bundle gap instead of silently re-deciding verification in chat

What to preserve:

- the next improvement should prefer repo-owned local verification bundles when
  they already exist
- examples:
  - a checked-in `run-quality.sh`
  - a checked-in hook runner entrypoint
  - a repo-owned script that maps changed surfaces to the canonical validator
    set
- if the repo exposes only hook config, call the hook runner or hook entrypoint
  directly; do not upgrade network mutation into the verification primitive
- if no bundle exists yet, keep using surface-based validator choice, but name
  the missing verifier bundle as a real repo-quality gap instead of silently
  re-deciding it every session

Not the next slice, but worth preserving as a probable later follow-on:

- a repo-owned helper that maps changed files or declared surfaces to the
  smallest honest validation bundle
- optional reuse of existing hook-runner parallelism without equating that to
  `git push`

## Suggested Order

1. land `create-cli` probe-contract changes
2. land `quality` posture changes and dogfood them
3. land the shared recommendation/install helper and first consumers
4. land `quality` executable-spec / fragile-margin follow-on only after the
   first-wave `quality` rewrite settles
5. revisit `init-repo` only if the earlier slices settled cleanly

## Acceptance For The Next Session

- update the source-of-truth skill files first
- add or tighten repo-owned helpers or validators when the next deterministic
  move is obvious
- dogfood each changed public skill inside `charness`
- record durable findings in the appropriate artifact instead of leaving them
  only in chat
- update [docs/handoff.md](handoff.md) again if the next first move changes
- commit after each meaningful slice instead of batching the whole workstream
