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

### Getting a Lesson Into the Ledger

A repo creates its ledger once with `python3 scripts/init_lesson_ledger.py
--repo-root .`, which deliberately seeds nothing. A lesson becomes eligible only
when an author tags a retro bullet `recurrence-class: <slug>`; the ledger then
needs one append-only seed transition citing that retro. Rehearse and apply it:

```bash
python3 scripts/seed_lesson_transitions.py --repo-root . --dry-run
python3 scripts/seed_lesson_transitions.py --repo-root .
```

Appending a newly tagged class later is the same command, not a separate
operation. Use `--lesson-id <slug>` (repeatable) to seed a subset. The command
never invents a class, never edits a retro tag, and refuses a class that is
already seeded.

Inspect the cited retros before committing. Validation rebuilds each citation
live from `charness-artifacts/retro/*.md`, and transitions are append-only with
archive as the only withdrawal, so a committed transition breaks unrepairably if
its cited retro is renamed or its tag is removed.

### Declaring a Session

At session start,
use the one command that declares the frozen session, writes the deterministic
Markdown bundle, emits those same bytes, and leaves a subordinate receipt:

```bash
python3 scripts/open_lesson_session.py --repo-root . \
  --session-id <unique-session-id> --seed <deterministic-seed>
```

Record the session ID and derived bundle path
`charness-artifacts/retro/lesson-session-receipts/<session-id>.md` in the affected
work's durable artifact. After context loss, read that exact bundle before
evaluating lesson effects; do not reconstruct it from mutable lesson sources or
search a host transcript.

At retro, add only sparse cited encounters for effects observed after that
presentation, then validate the replayed state:

```bash
python3 scripts/record_lesson_score.py --repo-root . \
  --event-id <unique-event-id> --session-id <unique-session-id> \
  --lesson-id <listed-lesson-id> --source-retro <this-retro-path> \
  --outcome <changed-an-action|read-but-not-applied|not-consulted|pushed-a-wrong-action> \
  --anchor <what you observed>
python3 scripts/check_lesson_ledger.py --repo-root .
```

An encounter records a **typed outcome**, not a signed number. Each value
answers a question about your own behaviour and routes to one disposition
without anyone re-deriving which: `changed-an-action` (did it change a specific
action you took?) to `graduate`; `read-but-not-applied` (was it in view AT the
decision and still did not land?) and `pushed-a-wrong-action` (did it move the
work toward something wrong, or cost a read that returned nothing?) to
`rewrite-in-place`; `not-consulted` (did you never revisit it when the class
came up?) to `strengthen-binding`.

Three rules the vocabulary is built on, all three refused when you author the
encounter rather than later. `not-consulted` is the one with an ordering
consequence: it asserts the class recurred, so its `recurrence-class:` bullet
must already be in the recording retro before you score it. Write that bullet
first; the rest of the disposition still comes after the scores.

- **Every outcome needs an anchor.** There is no unanchored tier, because there
  is no magnitude left to carry one. A commit hash is permitted evidence and
  never required — a lesson usually fails at a judgement, not at an edit.
- **`changed-an-action` anchors must name the counterfactual**, not only the
  action: where the work would have gone otherwise. It is the easiest and most
  flattering claim available to an agent scoring its own session.
- **`not-consulted` requires the session to have committed the class**, proven by
  a `recurrence-class: <lesson-id>` bullet in the retro doing the recording.
  Without that guard it is trivially true of every lesson a session had no
  occasion to use.

`--source-retro` names the retro **recording the encounter** — the one being
written now — not the lesson's origin retro. Scoring cites evidence that an
encounter happened; seeding a lesson cites evidence that the class exists. One
rule used to serve both, which made a working lesson uncreditable (crediting it
meant declaring that its class recurred) and made a session drawing lessons from
two origin retros unclearable by any disposition.

The session is a local declaration of the deterministic snapshot at record
time. Its receipt proves the bundle matches the completed stdout bytes; the
bundle makes the selected content recoverable. A valid cited score proves only
that its lesson occurred in that declared list. Neither record proves that a
person saw, used, or benefited from it, and neither authorizes contract
graduation. If contemporaneous presentation is absent or uncertain, append no
score and use the exact `not-evaluated` form below. Never backfill from
retro-time inspection.

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
reviewed events; scores never change lifecycle state automatically:

```bash
python3 scripts/record_lesson_lifecycle.py --repo-root . \
  --event-id <unique-event-id> --lesson-id <lesson-id> --action archive \
  --decision-ref <reviewed-markdown-path> --rationale '<why this state changed>'
python3 scripts/check_lesson_ledger.py --repo-root .
```

`record_lesson_lifecycle.py` has no preview mode: after validating the complete
candidate it appends the event immediately. Commit or otherwise preserve the
current repo-local ledger before recording a reviewed archive or resurrection.

`quality` owns the lifecycle judgment, not `retro`: a retro sees one session, and
promoting a lesson is a multi-session claim about an always-loaded surface. Read
the evidence with:

```bash
python3 scripts/render_lesson_lifecycle_review.py --repo-root .
```

The review is read-only and proposes nothing. It exits zero over any ledger it
can validate, including one with nothing to propose, so a nonzero exit is always
a refusal to render — an unreadable or unreplayable ledger at 1, a
helper-provenance refusal at 2 — and never a finding about a lesson. It orders
lessons by ANCHORED evidence and reports recurrence only as context, because a
high-recurrence lesson may need graduation, a rewrite in place, or a stronger
binding to a step, and recurrence count cannot tell those apart — ranking by it
selects the loudest lesson rather than the one whose prose is the problem. Its
`by_disposition` grouping answers "which lessons have a `read-but-not-applied`
encounter" as a lookup rather than an inference, because the outcome an author
recorded already carries the routing. A lesson with no anchored evidence is
undetermined, not a candidate, and legacy-scalar encounters route nowhere: they
were recorded when `changed-an-action` was not expressible, so reading a
disposition out of them would manufacture evidence nobody gave.

Each reviewed lesson also carries `lifecycle_command_templates` — the archive or
resurrect move that is legal in its CURRENT state, with its arguments filled in.
The review emits the command and never runs it: threshold calibration is
deferred, and every lifecycle event still requires a reviewed `decision_ref` and
rationale. What was missing was never automation, only the operator ever being
handed the command.

Use `--action resurrect` to return an archived lesson to the active cohort. The
selection preview draws its recent, value, and uncertainty slots only from active
lessons and its archive slot only from archived lessons. When no archived lesson
exists, the slot falls back to the next lesson in the uncertainty ordering and
reports that under `archive_fallback_uncertainty` rather than folding it into
`uncertainty` — so "the archive is empty" stays visible while the presentation
still carries its full ten lessons. Selection policy v2 had hardcoded that
fallback to `0`, so every session recorded under it presented nine rather than
ten; policy v1 sessions did fill the slot, and policy v3 restores it.
[recent-lessons.md](../charness-artifacts/retro/recent-lessons.md) remains the generated rolling digest and is not rewritten by
preview selection or lifecycle events.

### Contract Graduation and Retirement

The contract register freezes its original H2 inventory and unit budget, then
replays reviewed membership transitions.

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

The proposal recorder also appends immediately after full validation; it does not
apply a contract membership change. Inspect the resulting proposal before editing
contract docs or running the separate transition command.

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
