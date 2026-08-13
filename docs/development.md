# charness Development Paths

This document collects development-only and proof-only `charness` flows.

These paths are useful when you are changing this repo itself, validating a
packaging change before push, or exercising a host-specific edge case without
mutating the installed CLI source of truth.

They are not the operator install contract. For supported installation and
refresh guidance, use the Quick Start in [README.md](../README.md).

## Repo-Local Dogfood

If you changed this checkout locally and want the installed host surface to
exercise those unpushed edits, update from this repo without pulling:

```bash
charness update --repo-root . --no-pull --skip-cli-install
```

Use this when the managed checkout already contains the exact source you want
to dogfood and an implicit `git pull --ff-only` would be wrong. This is a
proof-only path: it updates the host-visible plugin surface from the working
tree, but keeps the installed CLI pinned to the managed checkout.

If you need to refresh the installed CLI itself, run the managed checkout
entrypoint directly:

```bash
~/.agents/src/charness/charness update
```

After a release or normal operator cycle, go back to the default managed flow:

```bash
charness update
```

## Stable Goal Helper Commands

Use the repo-owned CLI surface for common goal helper checks instead of copying
versioned plugin-cache paths:

```bash
charness goal check --repo-root . --goal-path charness-artifacts/goals/<goal>.md --pursue-ready
```

`--charness-checkout /path/to/charness` points at an explicit source checkout
when proving local edits. Paths under
`~/.codex/plugins/cache/local/charness/<version>/...` are host cache internals
and may rotate after plugin updates.

## Closeout Bundle and Handoff Validation

The closeout bundle is an opt-in repo-local direct script, not a top-level
`charness` command. Run its no-write plan first with the manifest, bundle id,
critique path, and behavior channel that belong to the frozen slice:

```bash
python3 scripts/closeout_bundle.py --help
python3 scripts/closeout_bundle.py \
  --manifest <slice-manifest.json> \
  --bundle-id <bundle-id> \
  --critique-path <critique.md> \
  --behavior-channel 'behavior=<operator proof command>'
```

Add `--execute` only after inspecting the plan. A completed run writes a
repository-relative receipt intended for check-in at
`charness-artifacts/goals/<bundle-id>.json` by default, or at the explicit
`--receipt-path`. Behavior channels are recorded rather than run; the result is
local deterministic evidence only.

To check that retro follow-ups are wired into the next-session handoff, run:

```bash
python3 scripts/validate_retro_handoff_wiring.py --help
python3 scripts/validate_retro_handoff_wiring.py --repo-root . \
  --goal-path <goal.md> --retro-path <retro.md> --handoff-path docs/handoff.md
```

This validator checks path identity, the handoff's retro citation, and exact
recurrence markers. It does not judge prose disposition quality or establish
fresh-eye, provider, installed-consumer, remote-CI, push, or release proof.

## Local Lesson-Ledger Authoring

The lesson ledger has a deliberately local eligibility path. At session start,
render the deterministic preview, present that selected list in the active
conversation, and then record its frozen declaration before affected work:

```bash
python3 scripts/render_lesson_selection_preview.py --repo-root . \
  --seed <deterministic-seed>
python3 scripts/record_lesson_session.py --repo-root . \
  --session-id <unique-session-id> --seed <same-deterministic-seed>
```

At retro, add only sparse cited scores for effects observed after that
presentation, then validate the replayed state:

```bash
python3 scripts/record_lesson_score.py --repo-root . \
  --event-id <unique-event-id> --session-id <unique-session-id> \
  --lesson-id <listed-lesson-id> --source-retro <cited-retro-path> --score <integer>
python3 scripts/check_lesson_ledger.py --repo-root .
```

The session is a local declaration of the deterministic snapshot at record
time. A valid cited score proves only that its lesson occurred in that declared
list; it does not prove that a person saw, read, used, or benefited from it, and
does not authorize contract graduation. The contemporaneous presentation is an
agent-authored conversation action, not a ledger receipt. If it is absent or
uncertain, append no score; record
`not evaluated — presentation not established` in the retro and schedule
declaration plus presentation before the next work slice in the handoff. Never
backfill from retro-time inspection.

## Proof-Only Non-Managed Checkout

If you deliberately want to prove install behavior from a non-managed checkout,
keep it explicitly read-only with respect to the installed CLI source:

```bash
./charness init --repo-root /absolute/path/to/charness --skip-cli-install
```

This is for development or packaging proof only. The installed CLI should still
resolve back to `~/.agents/src/charness`.

## Host-Specific Proof Paths

- Claude fallback proof may still use `claude --plugin-dir /absolute/path/to/charness/plugins/charness`,
  but that is not the primary install path once `charness init` manages the
  host install.
- Codex local development may point the checked-in marketplace file at
  [`./plugins/charness`](../plugins/charness/) when proving packaging behavior inside this repo.

Keep any proof-only host route out of operator docs unless it becomes a
maintained, first-class install contract.

## Mutation Phase Barriers

When validating this repo, keep state-changing work and verification in
separate phases:

1. mutate
2. sync generated surfaces
3. verify
4. publish

Do not run generated-surface sync, version bumps, install/update flows, or git
mutations in parallel with validators or closeout commands. `multi_tool_use`
parallelism is only safe for read-only inventory such as `sed`, `rg`, `ls`,
and similar inspection commands.
