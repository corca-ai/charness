# Achieve Goal: Waste-retro disposition reviews must classify a structural-follow-up destination per transferable waste item (#337)

Status: draft
Created: 2026-06-08
Activation: `/goal @charness-artifacts/goals/2026-06-08-retro-disposition-structural-followup-classification.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: before activation.
- Next action: activate with `/goal @charness-artifacts/goals/2026-06-08-retro-disposition-structural-followup-classification.md`.
- Verification cadence: cheap deterministic checks at commit boundaries; the
  touched scripts' tests + fresh-eye critique at slice boundaries; the broad gate
  + #337 closeout at the bundle/closeout boundary. Carry this session's lessons:
  at a bundle boundary with mutation-pool commits run the changed-line coverage
  producer FIRST; cover any new input-normalization branch or defensive guard
  line IN the introducing slice (not happy-path only); check the critique enum
  legend before substituting.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Final Verification`, and `## Auto-Retro`.

## Goal

Make the waste-retro **disposition review** classify a structural-follow-up
*destination* for each transferable waste item it reviews, by construction —
a presence-only deterministic floor plus an explicit reviewer mandate — so that
"recorded in recent-lessons" can no longer be mistaken for "disposed" when the
real disposition is a missing structural fix.

The dogfood trigger is two-fold: (1) issue #337, filed from a `corca-ai/ceal`
identity-legacy-cleanup closeout where a waste item was recorded as retro memory
without classifying whether the structural fix belonged in a Charness skill, a
Charness adapter, a repo `AGENTS.md` rule, or nowhere; and (2) THIS session's own
disposition review (`charness-artifacts/critique/2026-06-08-issue-336-disposition-review.md`,
Finding 1), where an `applied: persisted to recent-lessons` disposition overstated
its teeth because the Repeat-Trap-vs-Next-Time-Checklist / memory-vs-gate
destination was never classified. The fix belongs upstream in Charness
retro/achieve guidance, NOT in consuming-repo `AGENTS.md` prose (which would
duplicate skill policy).

Each transferable waste item's disposition should resolve to one explicit
destination, mirroring the existing disposition forms but at the
structural-follow-up scope:

- `applied: <gate/hook/validator/test/contract change>` (teeth landed this run),
- `issue #N (recurs: <lineage> | novel: <reason>)` (filed, with lineage),
- `repo-local guard: <path>` (a consuming-repo guard, when genuinely repo-local),
- `none — <reason>` (no structural follow-up — a falsifiable claim).

## Non-Goals

- Do NOT make the floor a content classifier. The deterministic floor stays
  presence/binding-only (it proves a destination line exists and binds); the
  reviewer/operator makes the substantive destination call. Turning it into a
  prose word-list re-imports the exact over-fire trap the existing disposition
  floor was designed to avoid (#337 explicitly says the deterministic floor
  avoiding content classification is correct).
- Do NOT take on #338 (gather X/Twitter exact-source fallback) — a different
  theme (gather provider / source-identity proof), larger, tracked separately.
- Do NOT take on the deferred installed-vs-repo drift detector, the
  `run_slice_closeout.py` length-split, #335 (cron-closing), or #184 (product) —
  all different themes; keep this goal focused on #337 (the prior-goal focus
  lesson).
- Do NOT cut a real release/push by default — standard `achieve` no-push.

## Boundaries

- **Presence-only, grandfathered.** The new destination floor fires only when the
  retro/disposition-review names a transferable waste item (a waste-sibling-scan
  trigger), and is grandfathered by goal `Created` date so in-flight goals are
  unaffected. A missing/malformed `Created` fails closed. Clone-safe (in-file
  content, not mtime).
- **Behavior-preserving.** Existing disposition forms (`applied`/`issue #N`/
  `none — <reason>`) and the rung-1/rung-2 gate stay unchanged; the destination
  classification is an additive rung, no existing goal/retro verdict changes.
- **Public-skill + prompt-surface scope.** Touches the `achieve` disposition gate
  and the `retro` waste-sibling-scan + the shared retro-issue-destination-split
  reference → mirror-sync (`plugins/charness/...`), public-skill dogfood, and
  prompt-behavior-proof apply; deterministic gates own closeout.
- External side-effect scope: default no-push. Any approved publish/push/CI is
  scoped to the bundle that requested it and does not carry forward.
- Discuss before activation: RESOLVED at shaping. (a) **Floor design** —
  presence/binding-only destination floor + reviewer mandate; NOT a content
  classifier (the consequential design default, resolved per #337's own
  guidance). (b) **#337 closure** — close on the fix landing via a direct-commit
  close-keyword carrier (standard issue closeout); the issue is repo-owned.
  (c) **Scope** = #337 only (the focus lesson; #338 and the other candidates are
  tracked separately). No unresolved consequential default remains.

## User Acceptance

What the user can do to verify completion directly.

- Run an `achieve` closeout whose retro names a transferable workflow-failure
  waste item, and confirm the disposition review must record a per-item
  *destination* (`applied: <change>` / `issue #N (recurs|novel:)` /
  `repo-local guard: <path>` / `none — <reason>`) — a bare "recorded in
  recent-lessons" no longer satisfies the floor when a transferable waste item
  is named.
- Confirm an existing (pre-rule `Created`) goal still completes unchanged
  (grandfathered) and that a goal with no transferable waste item is not forced
  to add a destination line (the floor does not over-fire).
- Confirm #337 is CLOSED on GitHub via the close-keyword carrier.

## Agent Verification Plan

### Low-Cost Checks

- `py_compile`, `ruff`, `check_python_lengths` on touched scripts at each commit.
- The touched scripts' own pytest modules (`test_goal_disposition_gate.py` and
  the retro/disposition tests); a before/after verdict-equality check on existing
  goal/retro artifacts; `check_export_safe_imports` + mirror byte-sync.
- At a bundle boundary with mutation-pool commits, run
  `check_changed_line_mutation_coverage.py --write-fresh-marker` FIRST and cover
  any new normalization/guard branch in-slice (this session's carried lesson).

### High-Confidence Checks

- Dogfood: a synthetic retro+goal with a transferable waste item is refused
  without a destination line and accepted with one; a pre-rule goal and a
  no-transferable-waste goal are both unaffected; the touched gates stay green.
- Broad gate (`run-quality.sh --read-only`) at the bundle boundary. Fresh-eye
  `critique` at each slice boundary per the slice plan.

### External Or Live Proof

- **#337 closeout** via a direct-commit close-keyword carrier, verified with
  `gh issue view 337` and `issue_tool.py verify-closeout`.
- No real release by default; if a release-surface bump is warranted, record the
  `Release:` proof, else `Release: n/a — <reason>`.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| 1 | Add the per-waste-item destination classification to the disposition-review mandate + a presence-only floor (destination line present + bound; grandfathered by `Created`) | #337 + this session's own disposition overclaim (the dogfood) | a transferable-waste retro is refused without a destination line, accepted with one; pre-rule + no-waste goals unaffected; SHIP critique | planned |
| 2 | Align the `retro` waste-sibling-scan four-decision taxonomy + the shared retro-issue-destination-split reference with the destination shape, so retro and the disposition review agree | the destination vocabulary must be one source, not two drifting copies | retro scan + disposition review use one destination taxonomy; verdicts unchanged; SHIP critique | planned |
| 3 | bundle proof + closeout: broad gate; #337 closeout; retro | the operator-requested next-to-do closeout | broad gate PASS; #337 verified closed; retro + dispositions (dogfooding the new destination classification) | planned |

## Coordination Cues

Phase-appropriate routing for this run, deferred to `find-skills` (its
`--recommend-for-task` / `--recommendation-role --next-skill-id` recommendation
engine) — never a hard-coded phase-to-skill list here. `achieve` owns this slot
and the floors below; `find-skills` owns *which* skill answers a boundary. Fill
during the run:

- **Routing** — planned: Slice 1 → `impl` + `critique`; Slice 2 → `impl` +
  `critique` (+ `retro` for the taxonomy); Slice 3 → `quality` + `issue` +
  `retro`. Confirm via `find-skills` and record the returned route at completion
  (or `Routing: n/a — <reason>`).
- **Gather step** — likely n/a — #337 is a GitHub issue read via `gh` (its body
  cites a ceal retro path, not an external URL/Slack/Notion/Docs/Drive asset);
  confirm at completion (`Gather: n/a — <reason>`).
- **Release step** — likely n/a by default (no real release); record
  `Release: n/a — <reason>` at completion unless a release-surface bump is taken.
- **Issue closeout step** — #337 is the in-scope tracked issue: close on the fix
  landing via a direct-commit close-keyword carrier; record the `Issue closeout:`
  line (numbers + carrier + `issue_tool.py verify-closeout` proof) at completion.
  #338, #335, #184 are tracked context only.

## Slice Log

_No slices yet. Activation (`/goal`) flips status to `active` and begins Slice 1._

## Context Sources

Durable references this goal was shaped from. A fresh session can reconstruct
the originating context by following them in order.

1. **The fresh issue:** #337 "Require waste-retro disposition reviews to classify
   structural follow-ups" (`gh issue view 337`; filed from a `corca-ai/ceal`
   identity-legacy-cleanup closeout; cites `2026-06-08-identity-legacy-cleanup-session.md`
   in ceal).
2. **This session's dogfood:** the #336 disposition review
   `charness-artifacts/critique/2026-06-08-issue-336-disposition-review.md`
   (Finding 1 — the `applied: persisted to recent-lessons` overclaim whose
   structural destination was unclassified) and the goal retro
   `charness-artifacts/retro/2026-06-08-workflow-ergonomics-bundle-336-goal-slot.md`.
3. **Owning surfaces:** `skills/public/achieve/scripts/goal_artifact_disposition.py`
   (the rung-1/rung-2 disposition gate); `skills/public/retro/references/waste-sibling-scan.md`
   (the four-decision taxonomy); `skills/shared/references/retro-issue-destination-split.md`;
   the closeout contract `docs/prescribed-skill-closeout-contract.md`.
4. **Recent-lessons:** `charness-artifacts/retro/recent-lessons.md`.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason. Applies the anti-anchoring lesson to the artifact
itself so a fresh session sees the design space, not only the closed point.

- **Scope (assumed at shaping 2026-06-08).** Family: {#337 only; #337 + #338
  gather; #337 + the `run_slice_closeout` length-split}. Chosen: **#337 only**
  (focused; same workflow-ergonomics/retro theme; this session's disposition
  overclaim is its dogfood). Rejected: +#338 (different theme — gather provider /
  source-identity proof, larger; tracked separately); +slice-closeout-split
  (a length refactor, different theme; a recent-lessons Current Focus candidate
  but unrelated to #337). `axis: issue-theme` — the repo varies work by issue
  theme, so bundling across themes is the over-anchoring to avoid.
- **Floor design (resolved at shaping).** Family: {presence/binding-only
  destination floor + reviewer mandate; deterministic content classifier}.
  Chosen: **presence/binding-only** — #337 itself states the deterministic floor
  avoiding content classification is correct, and the existing disposition floor
  proves the prose word-list over-fires. `single-point: the gate-and-intelligence
  split is a fixed repo doctrine, not a host/provider axis`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

- **Over-tightening into a content classifier.** The biggest risk is the new
  floor scoring whether a destination is "good", re-importing the word-list
  over-fire trap. Folded: Non-Goals + Boundaries scope it presence/binding-only;
  the reviewer owns substance; Slice 1's tests assert presence/binding, not
  content.
- **Over-fire on goals with no transferable waste.** A blanket destination
  requirement would punish goals whose retro surfaced nothing transferable.
  Folded: the floor fires only on a named transferable/sibling-scan waste item,
  grandfathered by `Created`.
- **Taxonomy drift (two copies).** The retro waste-sibling-scan and the
  disposition review could grow divergent destination vocabularies. Folded into
  Slice 2 (one source via the shared retro-issue-destination-split reference).
- **Over-worry, not folded:** rebuilding the whole rung-1/rung-2 disposition gate
  — out of class; this is an additive destination rung on the existing gate.

## Off-Goal Findings

_None yet. File off-goal findings through `issue`; record only the reference and
reason here — and check the seam lineage before filing a fresh narrow issue._

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

After the run reports complete, the user can independently verify:

1. Run an `achieve` closeout whose retro names a transferable waste item and
   confirm the disposition review must record a per-item destination
   (`applied:` / `issue #N (recurs|novel:)` / `repo-local guard:` / `none —`).
2. Confirm a pre-rule (`Created` before the rule date) goal and a goal with no
   transferable waste both complete unchanged (grandfathered; no over-fire).
3. Confirm the retro waste-sibling-scan and the disposition review use one
   destination taxonomy.
4. Confirm #337 is CLOSED on GitHub via the close-keyword carrier.

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
