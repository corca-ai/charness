# Artifact Policy

This document explains where `charness` should keep different kinds of
knowledge. The goal is not one perfect file pattern. The goal is a stable
default plus explicit exceptions.

## Durability Classes

### Fixed Knowledge

Use fixed knowledge when the content is supposed to stay true until a maintainer
intentionally edits the contract.

Put it in:

- committed docs under `docs/`
- checked-in skill packages under `skills/`
- checked-in manifests, profiles, presets, and schemas
- checked-in adapters when they define shared repo defaults

Examples:

- [deferred-decisions.md](deferred-decisions.md)
- [runtime-capability-contract.md](runtime-capability-contract.md)
- [external-integrations.md](external-integrations.md)
- `skills/public/<skill-id>/SKILL.md`
- `.agents/quality-adapter.yaml`

Do not use fixed surfaces for:

- high-churn runtime signals
- one-run evidence
- machine-local queues

### Semi-Fixed Knowledge

Use semi-fixed knowledge when the surface should stay visible and canonical, but
its contents are expected to refresh in place as the current state changes.

Put it in:

- `charness-artifacts/<skill>/latest.md`
- a rolling canonical doc when that is the clearer operator surface

Examples:

- [handoff.md](handoff.md)
- [../charness-artifacts/gather/latest.md](../charness-artifacts/gather/latest.md)
- [../charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
- [../charness-artifacts/release/latest.md](../charness-artifacts/release/latest.md)

Use semi-fixed surfaces when later sessions should see the current best summary
without re-reading every historical record.

Do not use semi-fixed surfaces for:

- immutable policy
- long archives that should move to dated history
- machine-only state

### Variable Visible Knowledge

Use variable visible knowledge when the value changes per run, per review, or
per incident, but future readers may still need the specific record.

Put it in:

- `charness-artifacts/<skill>/YYYY-MM-DD-<slug>.md`
- explicit history archives such as `history/*.md`

Examples:

- `charness-artifacts/gather/2026-04-16-agent-harness-guide-v1-0.md`
- `charness-artifacts/retro/2026-04-16-issue-closeout-premortem.md`
- `charness-artifacts/quality/history/2026-04-09-through-2026-04-10.md`

Use dated visible records when:

- the exact point-in-time observation matters
- you may need to audit what was believed at that time
- a rolling `latest.md` would hide important context

Do not create a dated record when the real change is a stable rule that belongs
in a fixed doc.

### Variable Hidden Knowledge

Use variable hidden knowledge when the state is machine-local, resumable,
high-churn, or not useful as checked-in repo truth.

Put it in:

- `.charness/**`
- `.artifacts/**`

Examples:

- `.charness/tasks/*.json`
- `.charness/quality/runtime-signals.json`
- `.artifacts/markdown-preview/*.txt`
- `.artifacts/markdown-preview/manifest.json`
- install/update/support-sync state captured under `.charness/`

Use hidden runtime state when:

- the state helps resume work on one machine
- the state is too noisy to commit usefully
- the state should not be mistaken for portable policy

Do not let hidden runtime state become the only copy of:

- a user-visible decision
- the next-session pickup path
- a durable explanation another maintainer will need

## Default Placement Rules

When choosing a surface, ask these questions in order:

1. Is this a rule or invariant that should stay true until intentionally edited?
   - use a fixed surface
2. Is this the current visible summary that should refresh in place?
   - use a semi-fixed surface
3. Is this a point-in-time record that future readers may need?
   - use a variable visible surface
4. Is this machine-local state that should not be treated as repo truth?
   - use a variable hidden surface

## Default Naming Rules

For visible skill artifacts, the default naming pattern is:

- current pointer: `latest.md`
- durable record: `YYYY-MM-DD-<slug>.md`

Current repo examples:

- `charness-artifacts/debug/latest.md`
- `charness-artifacts/debug/YYYY-MM-DD-<slug>.md`
- `charness-artifacts/gather/latest.md`
- `charness-artifacts/release/latest.md`

## Current Exceptions

These are intentional exceptions to the simple defaults:

- [handoff.md](handoff.md) is a rolling canonical artifact under `docs/`, not
  under `charness-artifacts/`, because the next-session pickup path is a repo
  entry surface.
- `spec` work can live in checked-in spec artifacts such as
  `charness-artifacts/spec/*.md` without a dedicated adapter-managed `latest.md`
  flow when the repo is keeping a design contract rather than a rolling skill
  artifact.
- `quality` keeps both [../charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md)
  and dated history archives because the current posture must stay short while
  older reviews still matter.
- `announcement` and `hitl` split visible artifact and hidden runtime state:
  the human-facing current artifact stays visible, while delivery/runtime state
  stays under `.charness/`.

If a new skill or workflow needs a different shape, document the exception in
the owning adapter contract or repo policy doc instead of silently drifting.

## Visibility Rule

Prefer visible artifacts when a future maintainer needs to understand:

- what was decided
- what was gathered
- what the current posture is
- why the next step exists

Prefer hidden runtime state when the data is mainly for:

- resuming a machine-local workflow
- storing runtime measurements
- carrying queue or task metadata
- holding noisy intermediate state
- keeping rendered or generated proof artifacts that help the current machine
  inspect a surface without becoming checked-in repo truth

## Anti-Patterns

Avoid these mistakes:

- storing secrets or copied credentials in any artifact
- letting `latest.md` turn into a long archive instead of a current pointer
- using a dated artifact when a fixed doc should have been edited
- relying on hidden runtime state as the only explanation of a human-visible
  decision
- duplicating the same current summary in both `docs/` and `charness-artifacts/`
  without naming which one is canonical

## Related Contracts

- [harness-composition.md](harness-composition.md)
- [handoff.md](handoff.md)
- [runtime-capability-contract.md](runtime-capability-contract.md)
- [external-integrations.md](external-integrations.md)
- `skills/public/*/references/adapter-contract.md`
