# Achieve Goal: Finish the sweeps this run left: pay the deferred residue, and one real miss

Status: active
Created: 2026-08-07
Activation: `/goal @charness-artifacts/goals/2026-08-07-finish-the-sweeps-this-run-left.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: A is DONE and committed; B next — #493, make the refill report
  reach a nested block.
- Current slice intent: `_mark_subkey_refills` compares TOP-LEVEL keys, so a
  nested block (`mutation_testing.report_paths`) whose own leaves were refilled
  is under-reported. #481 was whole-field, #489 sub-key, this sub-sub-key. TWO
  bounded rounds are owed: this changes a REPORT other surfaces read. This names
  the reviewable-intent unit in progress and the commits it spans; critique and
  broad proof do not re-fire within one unchanged intent — update it when the
  intent changes, not per commit (meaningful-slice-cadence).
- Next action: reproduce #493 from the issue (`mutation_testing.report_paths`
  minus `summary_md`) BEFORE designing, then check stop condition 2 — if the
  recursion names dozens of leaves, STOP and ask rather than shipping a report
  nobody reads.
- Slice A carry-forward: a guard belongs to the VALUE, not the transport that
  delivered it; and a masking primitive that FAILS OPEN turns any caller
  scanning its output into a verdict over a reading it never established.
- Verification cadence: cheap deterministic checks at commit boundaries;
  higher-cost or fresh-eye proof at slice boundaries; final broad/live proof at
  closeout.
- Gate cadence: pre-lock slices use `run_slice_closeout.py --skip-broad-pytest`;
  final/bundle proof records the verification lock and uses `--verification-lock`.
- Slice review packet: before fresh-eye slice critique, provide intent, changed
  files and owning/generated surfaces, expected invariants, tests/proof,
  non-claims, out-of-scope lines, and reviewer questions.
- History boundary: keep this frame current; move completed detail to
  `## Slice Log`, `## Operator Decision Queue`, `## Final Verification`,
  and `## Auto-Retro`.

## Goal

Three issues, one mechanism: **a repair that stopped at the surface the instance
named and did not reach the class.** All three are residue the 2026-08-06 goal
created, and its own delegated close-critique or bounded rounds surfaced each.

- [#494](https://github.com/corca-ai/charness/issues/494) — `#487` closed the
  prose-through-argv channel for `append_slice_log.py`. `upsert_goal.py --goal-body`
  has the identical channel, **was named in that goal's own `## Boundaries`**, and
  was never swept. `--goal-body` writes the `## Goal` section of a goal artifact at
  creation, so a hole there is worse than a hole in one slice-log line. The shipped
  `references/goal-artifact.md` now carries the rule directly above an example that
  demonstrates the forbidden form for this helper.
- [#493](https://github.com/corca-ai/charness/issues/493) — `#489` made a
  partially-refilled policy block report `augmented` and name its refilled sub-keys.
  `_mark_subkey_refills` compares TOP-LEVEL keys, so a nested block
  (`mutation_testing.report_paths`) whose own leaves were refilled is under-reported.
  #481 was whole-field, #489 was sub-key, this is sub-sub-key.
- [#492](https://github.com/corca-ai/charness/issues/492) — slice C's extraction
  created a real import cycle that **4979 passing tests could not see**, because
  every existing importer reached the other module first. A subprocess guard was
  shipped for that ONE module pair; the class is every module in the package.

**Honest shape of this goal: two of the three were DELIBERATE deferrals, correctly
recorded at the time.** #493's coarseness is commented at its call site with its
direction stated (under-reports, never over-reports); #492's guard was scoped to
the measured pair on purpose. Only #494 is an actual miss — a sibling named in
scope, not swept, not recorded. So this is a goal that CASHES IN deferred work,
not one that repairs a mistake, and the closeouts should say which is which rather
than letting all three read as bug fixes.

The outcome is that each of the three reaches the class its instance came from, or
records — with a measurement, not a hunch — why the class boundary sits where it
does.

## Non-Goals

- **Not [#491](https://github.com/corca-ai/charness/issues/491)** (a reference
  disagreeing with the code). It needs a design decision FIRST — gate versus a
  reviewer-packet question — and this repo has measured that a gate which cries
  wolf gets walked past. Deliberately excluded so it gets its own shaping.
- **Not the dotted `deliberately_absent` vocabulary.** #493 changes the REPORT's
  granularity, not the DECLARATION's. The operator deferred the dotted declaration
  vocabulary on 2026-08-05 and that still stands. These two look alike and are not;
  keeping them apart is a boundary this goal must not blur.
- **Not the unreachable-file cluster** (#482/#483/#484). No ruler yet, and a count
  that moves with the ruler is evidence about the ruler.
- **Not D40's blocking half**, not #468/#480/#475.
- **Not a general import-graph refactor.** #492 adds a CHECK, not a restructure.

## Boundaries

- **External side-effect scope.** Issue CREATION is standing per `AGENTS.md`.
  `git push` is standing CONDITIONAL ON THE GATES — a refusing gate withdraws it,
  and nothing gets weakened to reach green. Closing #492/#493/#494 is standing
  CONDITIONAL ON THE CLOSEOUT FLOOR. PR, release, tag, version bump and
  `cautilus evaluate` are NOT covered and are not requested.
- **The closeout ledger goes in the COMMIT MESSAGE for a direct-commit carrier**,
  not the comment body — `validate-closeout-draft` reads it from there. Two rounds
  were lost to that on 2026-08-06.
- In scope: `skills/public/achieve/scripts/upsert_goal.py` and
  `references/goal-artifact.md`; `scripts/quality_policy_merge.py`'s
  `refilled_policy_subkeys` and `scripts/quality_bootstrap_lib.py`'s
  `_mark_subkey_refills`; a repo-wide standalone-import check; the `plugins/` mirror
  of anything touched.
- Stop conditions:
  1. **If #492's repo-wide check is slow enough to hurt the pre-push lane**, scope
     it to CHANGED modules there and run the full sweep in CI — and say so in the
     check's own output, so a partial run never reads as a whole-package verdict.
     (That is this repo's own `partial` lesson from #488.)
  2. **If #493's recursion makes the report name dozens of leaves**, STOP and ask.
     A report nobody reads is the failure mode this repo has already measured; a
     nested block refilled WHOLE probably wants its block name, not every leaf.
  3. **If `upsert_goal.py` needs a different input shape than
     `append_slice_log.py`'s** (different field set, `--title` is required and
     short), do not force symmetry for its own sake.
- **Cut order if short: #492, then #493.** #494 is the only real miss and the only
  one where the shipped reference currently contradicts itself.

## User Acceptance

- **#494: a backtick-bearing goal body survives a real shell**, proven by driving
  `sh` — the same technique #487 used — and the reference no longer demonstrates a
  form it forbids for a helper with no alternative.
- **#493: a nested block with a deleted leaf is NAMED in the report**, proven by
  the reproduction pasted on the issue (`mutation_testing.report_paths` minus
  `summary_md`), with a false-positive control proving a fully-specified nested
  block still reports nothing.
- **#492: the check CATCHES the original cycle**, proven by feeding it the
  pre-fix `quality_policy_merge.py` from git — not merely by passing on a clean
  tree, which proves nothing.
- **Every new or changed rule is proven to BITE** by reintroducing the real defect.
- **Each close states whether it was a deferred deferral or a miss**, because two
  of three were correctly recorded decisions and calling all three bug fixes would
  misdescribe the record.
- **Every figure carries `<value> — <source>`** with its denominator and date, and
  is MEASURED before it is asserted. On 2026-08-06 a retro claimed comments pushed
  files over the length cap; one `tokei -f` run would have shown comments are
  already excluded. Run the command.

## Agent Verification Plan

### Low-Cost Checks

- **Reproduce each before designing.** All three issues carry a reproduction; two
  carry a measured instance. None needs investigation first.
- **For #492, the check must be proven against the REAL cycle**, recovered with
  `git show <sha>^:scripts/quality_policy_merge.py`. A guard that only passes on a
  healthy tree is the empty-scope green this repo refuses.
- Sync `plugins/` mirrors before validators; obey the dup-ratchet edit advisory.
- `run_slice_closeout.py --skip-broad-pytest` at pre-lock slice boundaries.

### High-Confidence Checks

- **TWO bounded rounds for #492 and #493** — #492 IS a new gate and #493 changes a
  report other surfaces read. #494 is an input channel and takes ONE round.
- `reviewer_boundary_fingerprint.py snapshot` around each review, and **`verify`
  the MOMENT the reviewer returns, before any parent write** — missed once on
  2026-08-06, costing that window its integrity proof.
- A closeout-claims review by a distinct observer before the completion flip.

### External Or Live Proof

- `git push` to `main` and its CI — standing, conditional on the gates. Remote CI
  confirmed by a different observer AND channel than the push exit code, read
  through the check-runs API. Note: an intermediate SHA's mutation mirror may read
  `cancelled` when a later push supersedes it; that is the CI system cancelling its
  own run, not a failure — confirm on the HEAD that carries the work.

## Slice Plan

| Slice | Objective | Why Now | Expected Evidence | Status |
| --- | --- | --- | --- | --- |
| A | #494 — close `upsert_goal.py`'s argv channel and stop the reference contradicting itself | The only real MISS of the three, and the shipped reference currently forbids a form and then demonstrates it | A backtick-bearing `--goal-body` through a real shell arrives whole or fails loudly; the reference example matches the rule | done — see Slice 1; two bounded rounds, 6 blockers found and repaired, 5 guards mutation-checked |
| B | #493 — make the refill report reach a nested block | #481 whole-field, #489 sub-key, this sub-sub-key; the class has moved down one level twice already | The issue's reproduction names the refilled leaf; a fully-specified nested block still reports nothing | pending |
| C | #492 — a standalone-import check for every module in the package | A real cycle passed 4979 tests; the guard exists for one pair only | The check FAILS on the pre-fix module recovered from git, and passes on the current tree | pending |
| D | Closeout: bundle gate, claims review, retro, the three issue closeouts, commit | Repo contract treats critique, closeout and commit as task-completing work | `--verification-lock` green with an explicit pytest number; each close through its floor, stating deferral-versus-miss | pending |

## Operator Decision Queue

- Queued: none — the scope decision was made by the operator on 2026-08-06 and is
  folded into `## Interview Decisions`. Nothing is waiting on the operator to start.

## Coordination Cues

Phase-appropriate routing for this run, chosen from installed skill metadata and
model judgment — never a hard-coded phase-to-skill list here. Use the catalog
only for hidden availability facts. `achieve` owns this slot and the floors
below. Fill during the run:

- **Routing** — choose the skill for the current phase or boundary from installed
  metadata/model judgment, and record the route. At completion, recorded
  boundary, and record the route it returns. At completion, recorded
  implementation / debug / quality / issue work needs this `Routing:` evidence
  or a `Routing: n/a — <reason>` opt-out.
- **Gather step** — when `## Context Sources` names an external source
  (URL / Slack / Notion / Docs / Drive), add a `Gather:` line here pointing at the
  gathered asset, or write `Gather: n/a — <reason>` when no external context
  applies.
- **Release step** — when this run touches a release surface (a version bump or
  install-manifest edit), add a `Release:` line here pointing at the release
  proof, or write `Release: n/a — <reason>`.
- **Issue closeout step** — when this goal resolves tracked GitHub issues, add
  an `Issue closeout:` line naming the close-intended issue numbers, carrier
  (`direct-commit`, PR body, release commit, or manual fallback), and
  `issue_tool.py validate-closeout-draft` / `verify-closeout` proof. If a
  tracked issue appears in `## Context Sources` as context only, use
  `Issue closeout: n/a — <reason>`.

Routing step line — record it on ONE physical line so the floor reads the whole
value (a soft-wrapped value is tolerated now, but one line is clearest). Copy the
form below and replace `<skill>` with the selected installed skill; the
placeholder is intentionally non-satisfying (the Gather / Release / Issue
closeout floors are presence-only, so no stub is seeded for them — add their line
per the bullets above when that boundary is crossed):

- `Routing: <skill> — <why this phase needs it>`

## Discuss Before Activation

- Discuss before activation: RESOLVED at design time. No release surface, no
  live/prod proof, no broad bundled scope, no irreversible side effect beyond the
  three standing approvals (`AGENTS.md`: issue creation; push conditional on the
  gates; issue close conditional on the closeout floor).
- The one proof-level non-claim is folded into `## User Acceptance` and stop
  condition 1: **#492's check can only establish what it enumerates.** A module the
  enumeration misses is unchecked, and the check must say what it covered rather
  than reading as a whole-package verdict — the `partial` lesson from #488, applied
  to the gate this goal builds.
- **This goal is ready to run.**

## Slice Log

### Slice 1: Close upsert_goal.py's prose-through-argv channel (#494)

- Objective: Give `upsert_goal.py` an input channel with no shell in front of it, and stop `references/goal-artifact.md` demonstrating the form it forbids. #494 is the only real MISS of this goal's three: a sibling helper named in #487's own `## Boundaries` and then never swept.
- Why this approach: `--goal-body` writes the `## Goal` section, so a hole there is worse than a hole in one slice-log line. The reference carried the rule directly above an example calling the forbidden form for a helper with no alternative. The channel is unfixable from inside the process, so this adds a CHANNEL, not a validator - the same shape #487 shipped.
- Commits: pending (this slice's commit)
- What changed: NEW `--fields-file` on `upsert_goal.py` taking `title`/`goal-body`; the JSON parse and its six refusals extracted to `goal_cli_args.load_fields_file` and now SHARED with `append_slice_log.py` (whose 8 pre-existing tests are the parity evidence). `_DATE` anchored with `\Z` in `goal_artifact_lib.py`. SKILL.md, `references/goal-artifact.md` and `references/lifecycle-during.md` repaired. NEW `tests/quality_gates/test_upsert_goal_input_channel.py` (17 tests). One `intentional` dup classification (c71405ac5e920fb0). `plugins/` mirror synced.
- Alternatives rejected: Rejected mirroring `append_slice_log.py`'s WHOLE field set for symmetry (goal stop condition 3): only `title` and `goal-body` are free prose. Rejected leaving `--slug` on argv on the old rationale - it was FALSE, so the slug now refuses a value `slugify` would rewrite instead. Rejected forcing `goal-body` single-line like a slice field: a goal body is a SECTION, and forcing one line would push callers straight back to the shell.
- Targeted verification: 17 + 8 channel tests through a REAL shell (`shell=True`), because the loss happens in the shell and an argv-list test cannot reproduce it; 4234-test broad run pending. Each of the 5 new guards MUTATION-CHECKED to be load-bearing: reverting `_merge_field`'s empty-override refusal, `fences_balanced`, `_normalize_newlines`, and `$`-vs-`\Z` each made its own test FAIL. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`: completed.
- Test duplication pressure: dup ratchet clean after one `intentional` classification: the extraction SHRANK four existing families and surfaced one new one that is a pre-existing CLI-boilerplate parallel (`try: <lib call> / except: print; return 2`) across three unrelated commands - verified pre-existing by stashing and re-running, ratchet clean on the base tree. Same span-shift class this repo measured four times on 2026-08-06.
- Critique: TWO bounded rounds, each with a verified `reviewer_boundary_fingerprint` window (both `clean`). Round 1 found 3 blockers: guards attached to the TRANSPORT not the value, so the documented list-argv channel walked past them and wrote a forged heading at exit 0; a lone CR forging a heading via universal-newline read-back; and a FALSE shipped claim that `--slug` fails loudly. Round 2 - the round that read the REPAIRS - found 3 more: an empty `--goal-body` flag overriding a non-empty file value (this helper's own total-loss shape, on the field the channel exists to protect); the fence mask rendering a verdict over a reading `mask_fences` documents as unestablished; and the `_DATE` repair shipped with no biting test. All repaired.
- Off-goal findings: Filed #495 - `docs/handoff-chunked-routing.md` says `draft_goal_from_chunk.py` writes through `upsert_goal`; it renders and writes directly, so a reader would wrongly conclude the new guards cover both goal-artifact writers.
- Lessons carried forward: The round that reads the REPAIRS earned its keep again: round 2's blockers were all the class being repaired. Two are worth carrying: a guard belongs to the VALUE, not to the transport that delivered it - round 1's blocker was that the new checks only policed the new channel while the documented-safe one bypassed them; and a masking primitive that FAILS OPEN turns any caller scanning its output into a verdict over a reading it never established, which is why `mask_fences` ships `fences_balanced` beside it.
- Metrics:

## Context Sources

Durable references this goal was shaped from, in reading order.

1. [issue #494](https://github.com/corca-ai/charness/issues/494),
   [#493](https://github.com/corca-ai/charness/issues/493),
   [#492](https://github.com/corca-ai/charness/issues/492) — each carries its own
   reproduction or measured instance. Read these first; no investigation is owed.
2. [the completed 2026-08-06 goal](2026-08-06-make-a-verdict-state-the-scope-it-measured.md)
   — five slice-log entries with the reviews that surfaced all three residues.
3. [its resolution critique](../critique/2026-08-06-issue-487-488-489-490-resolution-critique.md)
   — the delegated close-critique that REFUSED two of four closes and produced #493
   and #494.
4. [its retro](../retro/2026-08-06-make-a-verdict-state-the-scope-it-measured-retro.md)
   — including a corrected Waste bullet: a claim asserted without measurement.
5. [design-north-star.md](../../docs/design-north-star.md) — P4 governs the #492
   check: a guard that passes on a clean tree has established nothing.

## Interview Decisions

For each Before-phase question: family of options considered, chosen value, and
rejected-alternatives reason.

1. **What is the unit?** Family considered: {this run's residue (#492/#493/#494);
   the missing gates (#491+#492); the unreachable-file cluster (#482/#483/#484);
   the stored-remedy family (#468/#480)}. **Chosen by the operator 2026-08-06:
   this run's residue.** All three carry finished reproductions and measurements,
   so no investigation slice is owed, and each closes a debt this session created.
   Anti-anchoring: `axis: three issues are one class only if the MECHANISMS match`
   — checked before unifying, and they do: each is a repair that stopped at the
   surface its instance named. The unreachable-file cluster was rejected because it
   has NO ruler and a count that moves with the ruler is evidence about the ruler;
   #491 was rejected because it needs a design decision before any code.
2. **Order within the unit.** Family considered: {largest first; smallest first;
   the real miss first}. **Chosen: the real miss (#494) first.** Two of the three
   were deliberate, recorded deferrals; #494 is the one where a sibling was named
   in scope and silently not swept, and where a shipped reference currently
   contradicts itself. Paying the dishonest debt before the honest ones is the
   order that matters if the goal is cut short. Anti-anchoring: `axis: "smallest
   first" optimises for momentum, which is the wrong axis when one item is a
   correctness debt and the others are scheduled work`.
3. **Is this a bug-fix goal?** Family considered: {treat all three as bugs; treat
   all three as scheduled work; distinguish per issue}. **Chosen: distinguish, and
   say so in each close.** #493 and #492 were recorded decisions with their
   direction stated; calling them bugs at close time would misdescribe the record
   and quietly devalue the practice of recording a deferral. Anti-anchoring:
   `axis: an issue's existence says work remains, not that a mistake was made`.

## Plan Critique Findings

Blockers folded into Boundaries/Verification/Slice Plan, over-worry raised but
not folded, and reviewer provenance. Preserves reasoning so a fresh session
re-verifies the folded revisions without re-running critique.

## Off-Goal Findings

Issues or deferred findings discovered during the run.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: TODO — create or explicitly skip with an allowed reason before complete
Host log probe: TODO — create or explicitly skip with an allowed reason before complete
Disposition review: TODO — create or explicitly skip only when policy allows before complete

## User Verification Instructions

## Auto-Retro

Retro dispositions: TODO — disposition every surfaced improvement, or record the explicit no-improvement opt-out
Structural follow-up: TODO — when the retro names a transferable waste item (a `## Sibling Search` trigger), classify its structural destination (`applied: <gate/hook/validator/test/contract change>` / `issue #N (recurs:|novel: <reason>)` / `repo-local guard: <path>` / `none — <reason>`); delete this line when no transferable waste was named
