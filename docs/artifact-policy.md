# Artifact Policy

> Status: current
> Source of truth: this page and its linked executable surfaces
> Last verified: 2026-09-04

This document explains where `charness` should keep different kinds of
knowledge. The goal is not one perfect file pattern. The goal is a stable
default plus explicit exceptions.

## Goal lineage

Goal Draft/Binding identity, the `goal_lineage` record, and the parent cursor are owned by [goal-lifecycle.md](./goal-lifecycle.md); evidence dispositions (`goal-bound`, `planning-only`, `not-goal-bound`) are held by [goal_lineage.py](../scripts/issue/goal_lineage.py).

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

- [deferred-decisions.md](./deferred-decisions.md) — how to defer a product-boundary choice.
- [runtime-capability-contract.md](./runtime-capability-contract.md) — how host capability grants replace raw env-secret fallbacks.
- [external-integrations.md](./external-integrations.md) — what upstream tools own versus what charness owns.
- `skills/public/<skill-id>/SKILL.md`
- [`.agents/quality-adapter.yaml`](../.agents/quality-adapter.yaml) — this repo's quality preset, coverage floor policy, and gate globs.

Do not use fixed surfaces for:

- high-churn runtime signals
- one-run evidence
- machine-local queues

### Semi-Fixed Knowledge

Use semi-fixed knowledge when the repo already keeps dated visible records and
also needs one short current pointer that refreshes in place as the current
state changes.

Put it in:

- `charness-artifacts/<skill>/latest.md`
- a rolling canonical doc when that is the clearer operator surface

Examples:

- [goal-lifecycle.md](./goal-lifecycle.md) — the parent Goal Run cursor and execution identity.
- [../charness-artifacts/gather/latest.md](../charness-artifacts/gather/latest.md) — the current gathered source, route family, and acquisition trace.
- [../charness-artifacts/quality/latest.md](../charness-artifacts/quality/latest.md) — the current quality review's scope, surface contract, and findings.
- [release artifacts](../charness-artifacts/release/) — dated release notes and the operator update path.

Use semi-fixed surfaces when later sessions should see the current best summary
without re-reading every historical record, but the exact past records still
matter enough to keep as separate dated artifacts.

Do not use semi-fixed surfaces for:

- immutable policy
- long archives that should move to dated history
- machine-only state

### Variable Visible Knowledge

Use variable visible knowledge when the value changes per run, per review, or
per incident, and future readers may still need the specific record. This is
the default visible artifact class for skill work unless the repo can justify a
rolling pointer as the clearer operator surface.

Put it in:

- `charness-artifacts/<skill>/YYYY-MM-DD-<slug>.md`
- explicit history archives such as `history/*.md`

Examples:

- [`charness-artifacts/gather/2026-04-16-agent-harness-guide-v1-0.md`](../charness-artifacts/gather/2026-04-16-agent-harness-guide-v1-0.md) — a dated gather of a public agent-harness article.
- [`charness-artifacts/retro/2026-04-16-issue-closeout-premortem.md`](../charness-artifacts/retro/2026-04-16-issue-closeout-premortem.md) — a dated retro on failures surfaced by external dogfooding.
- [`charness-artifacts/quality/history/2026-04-09-through-2026-04-10.md`](../charness-artifacts/quality/history/2026-04-09-through-2026-04-10.md) — archived quality reviews with the commands run then.

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

- `.charness/quality/runtime-signals.json`
- `.artifacts/markdown-preview/*.txt`
- `.artifacts/markdown-preview/manifest.json`
- install/update/support-sync state captured under `.charness/`

Use hidden runtime state when:

- the state helps resume work on one machine
- the state is too noisy to commit usefully
- the state should not be mistaken for portable policy
- runtime timings should feed human summaries from structured state instead of
  becoming hand-edited markdown numbers

JSON state under `.charness/`, `.artifacts/`, or `charness-artifacts/` must
still keep canonical path fields portable when it may be committed, copied into
a report, or used by a later clone. Store repo-root-relative paths for repo
files. If a diagnostic truly points outside the repo, store a logical label and
non-secret provenance such as a basename instead of the absolute host path.

Do not let hidden runtime state become the only copy of:

- a user-visible decision
- the next-session pickup path
- a durable explanation another maintainer will need

## Default Placement Rules

When choosing a surface, ask these questions in order:

1. Is this a rule or invariant that should stay true until intentionally edited?
   - use a fixed surface
2. Is this a point-in-time record that future readers may need?
   - use a variable visible surface
3. Does the repo also need one short current pointer over those records?
   - add a semi-fixed surface
4. Is this machine-local state that should not be treated as repo truth?
   - use a variable hidden surface

## Default Naming Rules

For visible skill artifacts, the default naming pattern is:

- durable record: `YYYY-MM-DD-<slug>.md`
- optional current pointer: `latest.md`

Before editing an artifact, resolve the edit target instead of opening
`latest.md` from memory:

```bash
python3 scripts/artifacts/resolve_artifact_path.py --repo-root . --skill-id <skill-id> --slug <slug> --intent record
python3 scripts/artifacts/resolve_artifact_path.py --repo-root . --skill-id <skill-id> --slug <slug> --intent current
```

`--intent` and `artifact_class` identity live in
[`artifact_naming_lib.py`](../scripts/artifacts/artifact_naming_lib.py) and
`resolve_artifact_path.py --help`. Do not recopy the enum here. After writing a
dated record, refresh the current pointer through the helper instead of editing
`latest.md` directly:

```bash
python3 scripts/artifacts/refresh_current_pointer.py --repo-root . --skill-id <skill-id> --record-artifact-path <record-path> --execute
```

Do not add skill-id exception lists for artifact behavior. Declare the class in
the owning adapter resolver or policy document.

To audit the current repo layout instead of relying on memory, run:

```bash
python3 scripts/artifacts/inventory_current_pointer_layouts.py --repo-root .
```

The inventory reports the adapter class, `artifact_path`, `write_artifact_path`,
symlink target metadata, and whether the checked-in current pointer is a regular
file, symlink, rolling file, missing pointer, or adapter-unmanaged workflow.

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

## Derived-Artifact Validation Posture

An artifact is **purely derived** when this repo's own code reproduces its exact
bytes from repo state. Those get a recompute-and-compare gate — a `--check` mode
that re-derives the artifact and byte-compares, plus a repo-local-helper guard at
the write site — so drift is caught whatever caused it: a foreign or stale
harness copy, a partial edit, a bad merge, a hand-edit of a generated surface.
The gated ones today are the
[retro lesson-selection index](../charness-artifacts/retro/lesson-selection-index.json)
and the ledger-backed preview that reads it, and the
[debug seam-risk index](../charness-artifacts/debug/seam-risk-index.json).

Across the artifact families a foreign or stale harness copy can write —
`charness-artifacts/{critique,probe,release,retro}/` — every other machine-written
artifact embeds agent prose, a generation timestamp, producer subprocess output,
a live release URL, or absolute host paths, so recompute-and-compare has no
defined meaning for it. **Shape-only validation is the deliberate contract for
those families, not a missing gate** — the per-family evidence is in the
[derived-artifact recompute inventory](../charness-artifacts/audit/2026-07-27-derived-artifact-recompute-inventory.md).
Families outside those four directories were not surveyed, and at least one
(`capability-catalog`) is byte-stable by design, so read this as a scoped finding
rather than a repo-wide claim.

When adding a machine-written artifact, classify it first. Purely derived: add
the recompute gate at write time and a `--check` verify command on its
[surface](../.agents/surfaces.json). Not purely derived: say so in the surface
entry, so a later reader sees a decision rather than an omission.

## Related Contracts

- [harness-composition.md](./harness-composition.md) — which repo surface owns which kind of rule.
- [goal-lifecycle.md](./goal-lifecycle.md) — provider-backed parent/cursor continuation state.
- [runtime-capability-contract.md](./runtime-capability-contract.md) — capability grants, access modes, and repo-local capability config.
- [external-integrations.md](./external-integrations.md) — the integration-over-vendoring principle and upstream ownership model.
- `skills/public/*/references/adapter-contract.md`
