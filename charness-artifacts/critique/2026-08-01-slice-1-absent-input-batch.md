# Slice 1 critique — S24/S28/S35, "an absent input is not a matching input"

Date: 2026-08-01
Goal: [close-the-sweeps-remaining-high-rows-by-class](../goals/2026-08-01-close-the-sweeps-remaining-high-rows-by-class.md)
Slice: batch A — sweep rows S24, S28, S35.

## Reviewer Tier Evidence

- Requested tier: bounded read-only reviewer (`bounded-reviewer` typed agent)
- Requested spawn fields: agent_type=bounded-reviewer, unnamed spawn, session-model
  inheritance. Per the repo's per-host subagent split this is a Claude Code host, so the
  Codex `gpt-5.6-terra` / `fork_turns` request does not apply and its absence is
  contract-conformant rather than a degradation.
- Host exposure state: requested_fields_sent
- Application state: all five spawns were accepted with the requested agent type and
  returned their findings inline; the host does not separately expose applied model
  metadata.
- Delivery state: findings-received

## Reviewer Provenance

Fresh-eye satisfaction: parent-delegated

Five bounded read-only `bounded-reviewer` subagents across two rounds, all spawned
unnamed in the shared parent worktree with Read/Grep/Glob only. Every one reported
`parent-delegated` and confirmed it ran no git or write operations.

- Round 1 (three concurrent): correctness of the repaired surfaces; blast radius and
  contract compatibility; claim fidelity against the owning records.
- Round 2 (two concurrent, reading the REPAIRED surface): does this fix reproduce the
  class it fixes; is every claim the slice now makes true.

Worktree integrity: `reviewer_boundary_fingerprint.py snapshot` opened window
`slice1-round1` (`/tmp/rbf-slice1-r1.json`) and `slice1-round2` (`/tmp/rbf-slice1-r2.json`),
both at HEAD `7de074c1`. **Non-claim:** the matching `verify` was not run for either
window — the parent kept editing in-tree between the rounds by design, which is what the
`--parent-path` argument exists to declare, and it was not used. Integrity rests on
`git status --porcelain` showing only this slice's own intended paths.

## Round 1 — findings that changed the work

Six blockers and nine nits across three reviewers. The ones that changed the plan rather
than polishing it:

1. **The arming violated the goal's own stop condition.** The first cut made an
   uninterpreted adapter line an ERROR, so `valid: false` and every issue subcommand
   exits 1. The goal's Boundaries route a repair on a consumer-authored file to
   legible-plus-deferred. Downgraded to warnings; arming filed as
   [D46](../../docs/deferred-decisions.md).
2. **The measurement did not cover the governed population.** 0 uninterpreted lines over
   this repo's corpus says arming costs *this repo* nothing and says nothing about
   consumer-authored adapters. The script's docstring and D46 now say so.
3. **The instrumentation was blind to a fourth drop site** — the `index += 1` fallthrough
   in `_parse_list_items`. Re-measuring with it instrumented still returned 0, so the
   arming decision survived, but it had been resting on an undercount.
4. **The S24 defect produces the S35 defect.** `required_release_surfaces`, the field that
   arms the S35 absence check, was read through the un-repaired parse channel: a missing
   colon disarmed the teeth silently. The shared nine-skill `load_adapter_contract` now
   reports too.
5. **`expected is None` suppressed the entire drift verdict** — a deleted packaging
   manifest rendered `drift: []`, the batch's own rule broken at the top of its chain.
6. **`---` became a false refusal on legal YAML.**
7. The contract doc and `adapter.example.yaml` never learned the new field, so a consumer
   authoring from the published contract could not discover the one field that arms it.

## Round 2 — the fixes that carried the class they fixed

Five blockers, all on round 1's own repairs:

1. **`_is_ignorable` changed `load_yaml`'s result.** Skipping `---` in the LIST loop
   merged a second document's items into the first document's list, with no sink entry —
   the exact "the file did not say this" class the sink exists to close, introduced by the
   fix. The marker test moved to the mapping loop's call site.
2. **The list call site passed the wrong indent to `_mapping_value`**, so a block scalar
   under `- key: |` swallowed its sibling line and a nested mapping was dropped, both
   silently. Pre-existing (HEAD passed the same value), but it means a `0` from the
   measurement could not mean "nothing was dropped" while it stood.
3. **`absent_surfaces` was still built from the `None` test** `_state()` was introduced to
   replace, so a file present on disk with an unusable version was reported absent — in
   the one field named for that distinction.
4. **`_version_at` tracebacked on unreadable JSON** while the new comment claimed
   unreadable was handled. A half-written `plugin.json` is exactly what a failed sync
   leaves.
5. **The typed-refusal guard landed on one loader.** The other, serving nine skills
   including the release drift check this slice hardens, still died on a traceback.

Plus: the measurement was itself a **zero-denominator green** (0 files scanned printed a
clean 0 and exited 0 — the class this same session closed as S1/S26/S30/S32), `--roots`
did not actually bound the scan, this repo declared three of its four generated release
surfaces, and D46 said seven skills where there are nine.

## Round-2 repairs — ACCEPTED-UNREVIEWED

Under the two-round cap, everything in the round-2 list above ships without a third
review. The residual is visible rather than implied.

## What was raised and NOT folded

- Round 1 proposed arming the S24 refusal with a narrowed false-positive set. Declined:
  separating "attempted assignment with a missing colon" from "legal YAML this parser does
  not support" is the actual hard problem, and D46 records it as the reopen trigger.
- Round 2 proposed striking the "74 files" verification claim from the dup-review note.
  Declined: the number is real and came from a detached-HEAD worktree comparison over
  `git ls-files '*.yaml' '*.yml'`. The note now names the command and scope instead.

## Boundary Ownership

- Verdict: owned-correctly

The producer/consumer question this slice raised is real and was answered rather than
routed around. `adapter_lib` PRODUCES the parse result; every skill's `resolve_adapter`
CONSUMES it. The dropped-line fact was invisible because the producer discarded it, so the
report belongs in the producer — and it is observation-only there, leaving `load_yaml`'s
contract with its ~16 existing consumers untouched. The verdict about what a dropped line
MEANS stays with each consumer, which is why the issue adapter and the shared nine-skill
loader each decide warning-versus-error for themselves rather than inheriting a policy
from the parser. The one boundary this slice declined to move is S35's
`required_release_surfaces`: it sits in the adapter (a consumer-authored channel outside
the audited file) rather than being derived by the producer, and that is recorded as the
row's residual, not as a solved ownership question.

## Non-claims

No push, no CI dispatch, no live `cautilus` run. S24 and S35 close as NARROWED with the
residuals written into the sweep row, not as CLOSED. No claim is made about consumer-repo
behavior beyond what a local run establishes.
