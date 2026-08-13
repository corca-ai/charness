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
use the one command that declares the frozen session, writes the deterministic
preview, and leaves a subordinate command receipt. Present that selected list
in the active conversation before affected work:

```bash
python3 scripts/open_lesson_session.py --repo-root . \
  --session-id <unique-session-id> --seed <deterministic-seed>
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
time. Its emission receipt proves only that the command's stdout write and
flush returned for the recorded bytes. A valid cited score proves only that its
lesson occurred in that declared list. Neither record proves that a person saw,
read, used, or benefited from it, and neither authorizes contract graduation.
The contemporaneous presentation is an agent-authored conversation action. If
it is absent or uncertain, append no score and use the exact `not-evaluated`
form below. Never backfill from retro-time inspection.

### Lesson Evaluation Disposition

Every eligible Charness retro has exactly one `## Lesson Evaluation` section and
one machine line. Use one applicable form, replacing the session ID and score
count:

```text
Lesson evaluation: {"score_event_count":1,"session_id":"2026-08-14-example","status":"effect-recorded"}
Lesson evaluation: {"score_event_count":0,"session_id":"2026-08-14-example","status":"no-effect"}
Lesson evaluation: {"reason":"missing-start","score_event_count":0,"session_id":"none","status":"not-evaluated"}
Lesson evaluation: {"reason":"emission-unproven","score_event_count":0,"session_id":"2026-08-14-example","status":"not-evaluated"}
Lesson evaluation: {"reason":"presentation-unproven","score_event_count":0,"session_id":"2026-08-14-example","status":"not-evaluated"}
```

`no-effect` is affirmative and is never inferred from zero scores.
`presentation-unproven` means a valid command receipt exists but actual
conversation presentation is absent or uncertain. `emission-unproven` means a
session was declared without a valid receipt.

After the retro disposition and any sparse scores are persisted, reconcile the
eligible durable-retro cohort:

```bash
python3 scripts/check_lesson_evaluation_continuity.py --repo-root .
```

This report measures disposition continuity, not all host sessions or lesson
usefulness.

### Lesson Lifecycle

The ledger keeps at most 50 active lessons. Archive and resurrection are explicit
reviewed events; scores never change lifecycle state automatically. Existing
schema-v3 state migrates deterministically, with a dry run by default:

```bash
python3 scripts/migrate_lesson_lifecycle.py --repo-root .
python3 scripts/migrate_lesson_lifecycle.py --repo-root . --execute
python3 scripts/record_lesson_lifecycle.py --repo-root . \
  --event-id <unique-event-id> --lesson-id <lesson-id> --action archive \
  --decision-ref <reviewed-markdown-path> --rationale '<why this state changed>'
python3 scripts/check_lesson_ledger.py --repo-root .
```

Use `--action resurrect` to return an archived lesson to the active cohort. The
selection preview draws its recent, value, and uncertainty slots only from active
lessons and its archive slot only from archived lessons. If no archived lesson
exists, that slot stays empty; it is not filled with a second active lesson.
[recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) remains the generated rolling digest and is not rewritten by
preview selection or lifecycle events.

### Contract Graduation and Retirement

The contract register freezes its original H2 inventory and unit budget, then
replays reviewed membership transitions. Migrate schema v1 before recording new
work:

```bash
python3 scripts/migrate_contract_register.py --repo-root .
python3 scripts/migrate_contract_register.py --repo-root . --execute
```

A graduation proposal must cite one seeded lesson and at least two distinct
declared sessions in which that lesson received a score. This is an evidence
floor, not a score threshold or automatic authorization:

```bash
python3 scripts/record_contract_graduation_proposal.py --repo-root . \
  --proposal-id <unique-proposal-id> --lesson-id <lesson-id> \
  --source-retro <seed-retro-path> \
  --evidence-session-id <session-1> --evidence-session-id <session-2> \
  --target-path AGENTS.md --target-heading '<new H2 heading>' \
  --rationale '<why review is warranted>' \
  --displacement-unit-id '<path#heading-slug>'
```

After a reviewer approves the exact membership change, edit the contract docs to
the proposed H2 inventory. Then preview the matching transition and repeat with
`--execute` only after inspecting the receipt:

```bash
python3 scripts/apply_contract_transition.py --repo-root . \
  --action apply-graduation --event-id <unique-event-id> \
  --approval-ref <reviewed-markdown-path> --proposal-id <proposal-id> \
  --rationale '<reviewed decision>'
python3 scripts/apply_contract_transition.py --repo-root . \
  --action apply-graduation --event-id <unique-event-id> \
  --approval-ref <reviewed-markdown-path> --proposal-id <proposal-id> \
  --rationale '<reviewed decision>' --execute
```

For standalone retirement, use `--action retire`, repeat
`--retired-unit-id`, and either name active `--successor-unit-id` values with
`--disposition successor-units` or explicitly use
`--disposition no-remaining-binding-behavior`. The command refuses unless the
replayed active units exactly match the current contract H2 inventory.

Record a retro citation without changing membership, and render the bounded
retention evidence separately:

```bash
python3 scripts/record_contract_citation.py --repo-root . \
  --event-id <unique-event-id> --source-retro <retro-path> \
  --unit-id '<path#heading-slug>' --anchor '<where it mattered>'
python3 scripts/render_contract_retention_review.py --repo-root .
python3 scripts/check_contract_register.py --repo-root .
```

The retention report is non-authorizing. It reports observed citations, preserves
retired-unit history, and labels catch mapping and staleness calibration honestly;
it cannot approve graduation or retirement.

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

## Local Mutation Report Retention

`reports/mutation` is ignored machine-local state, but its regular producer outputs
are still current proof inputs. Inspect its lifecycle before deleting anything:

```bash
python3 scripts/manage_mutation_reports.py --repo-root . --older-than-days 30
```

The command classifies adapter-declared and repo-owned fixed output paths as
`managed`; they are never prune candidates. Old top-level regular files outside
that set are reported as `prune_candidate` but remain untouched. After inspecting
the exact paths and byte total, repeat with `--execute` and the emitted
`--confirm-candidate-set-sha256 <digest>` to remove only that unchanged candidate
set. A missing/mismatched digest, a replaced report root, or a candidate whose size
or modification time changed at its pre-delete check refuses. The command anchors
deletion to the inventoried directory and rechecks each candidate immediately before
unlinking it. It is not a transaction across all files: do not run cleanup alongside
a mutation producer, and a late concurrent change may leave an earlier candidate
already removed before the later candidate is refused. Directories, symlinks, fresh
files, and managed outputs are always preserved. Normal quality and mutation runs
never invoke this cleanup implicitly.

The standing pytest runner separately retains the newest three runner-owned failed
basetemps. It skips live locked runs and never prunes a custom `--basetemp`. Set
`CHARNESS_PYTEST_FAILED_BASETEMP_KEEP` to a positive integer for a machine-local
inspection window override; invalid or non-positive values warn and fall back to
three. Successful `--keep-basetemp` roots and legacy unmarked roots are preserved
outside the failure-retention count, so enabling this policy never silently reclaims
an earlier explicit keep or an ambiguously owned pre-policy root.

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
