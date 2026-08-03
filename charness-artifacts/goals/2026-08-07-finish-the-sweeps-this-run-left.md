# Achieve Goal: Finish the sweeps this run left: pay the deferred residue, and one real miss

Status: active
Created: 2026-08-07
Activation: `/goal @charness-artifacts/goals/2026-08-07-finish-the-sweeps-this-run-left.md`

This file is the living goal scratchpad. It becomes active only when the user
runs the activation command.

## Active Operating Frame

- Current slice: D — closeout. All three code slices are committed
  (`25a8e265`, `86be2df5`, `70e32238`); retro, disposition review and the closeout
  sections are written. Remaining: push, CI confirmation by a different observer
  and channel, and the three issue closes through their floor.
- Current slice intent: prove and close. Each close states whether it was a
  deferred deferral (#493, #492) or a real miss (#494) — two of three were
  correctly recorded decisions and calling all three bug fixes would misdescribe
  the record.
- Next action: run the closeout commit (ledger IN THE COMMIT MESSAGE for a
  direct-commit carrier), push, then read CI through the check-runs API — a
  different observer AND channel than the push exit code.
- Carry-forward, the run's most transferable lesson: **a guard belongs at the
  boundary that breaks the invariant, not the one that is easy to test.** It went
  wrong five times across three surfaces this run (tracked as #499), and it was
  the round-2 blocker on every slice. Second: an inversion test beats a family
  pin, because a pin cannot fail for a family nobody thought of.
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
| B | #493 — make the refill report reach a nested block | #481 whole-field, #489 sub-key, this sub-sub-key; the class has moved down one level twice already | The issue's reproduction names the refilled leaf; a fully-specified nested block still reports nothing | done — see Slice 2; two bounded rounds, 6 findings, report size measured at 17 names |
| C | #492 — a standalone-import check for every module in the package | A real cycle passed 4979 tests; the guard exists for one pair only | The check FAILS on the pre-fix module recovered from git, and passes on the current tree | done — see Slice 3; two bounded rounds, 7 findings, enumeration wrong 3× and found by inversion |
| D | Closeout: bundle gate, claims review, retro, the three issue closeouts, commit | Repo contract treats critique, closeout and commit as task-completing work | `--verification-lock` green with an explicit pytest number; each close through its floor, stating deferral-versus-miss | pending |

## Operator Decision Queue

- none — every decision this run fell inside the three standing approvals recorded in
  `AGENTS.md` (issue creation; push conditional on the gates; issue close conditional
  on the closeout floor), and the scope decision was already made by the operator on
  2026-08-06 and folded into `## Interview Decisions`. Nothing was deferred to the
  operator and nothing is waiting on one.

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

- Routing: impl — selected from installed skill metadata and model judgment: all three slices were code/test/reference changes against tracked issues, so impl owned the build and prove owned each slice stop gate; quality owned the validation-posture calls (dup-ratchet classifications, the Floor-Addition Restraint call on the new blocking gate, and the two public-skill scenario-review records); issue owned the three closeouts and the five off-goal filings; critique owned the six bounded rounds plus the closeout claims review; retro owned the after-action review.
- Gather: n/a — every source this goal was shaped from is repo-local. The three GitHub issues were read through the gh issue adapter, and the prior goal, its resolution critique and its retro are checked-in artifacts; the GitHub URLs in Context Sources are issue references resolved through that adapter, not external web pages needing a durable gathered asset.
- Issue closeout: #494, #493, #492 — carrier direct-commit; each ledger rehearsed with issue_tool.py validate-closeout-draft --commit-message-file before the close commit and read back with verify-closeout --expect-state CLOSED after, with the proof recorded in Final Verification. Off-goal filings #495/#496/#497/#498/#499 are creations, not closes, and stay open.

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
- Commits: `25a8e265`
- What changed: NEW `--fields-file` on `upsert_goal.py` taking `title`/`goal-body`; the JSON parse and its six refusals extracted to `goal_cli_args.load_fields_file` and now SHARED with `append_slice_log.py` (whose 8 pre-existing tests are the parity evidence). `_DATE` anchored with `\Z` in `goal_artifact_lib.py`. SKILL.md, `references/goal-artifact.md` and `references/lifecycle-during.md` repaired. NEW `tests/quality_gates/test_upsert_goal_input_channel.py` (17 tests). One `intentional` dup classification (c71405ac5e920fb0). `plugins/` mirror synced.
- Alternatives rejected: Rejected mirroring `append_slice_log.py`'s WHOLE field set for symmetry (goal stop condition 3): only `title` and `goal-body` are free prose. Rejected leaving `--slug` on argv on the old rationale - it was FALSE, so the slug now refuses a value `slugify` would rewrite instead. Rejected forcing `goal-body` single-line like a slice field: a goal body is a SECTION, and forcing one line would push callers straight back to the shell.
- Targeted verification: 17 + 8 channel tests through a REAL shell (`shell=True`), because the loss happens in the shell and an argv-list test cannot reproduce it. BROAD SUITE 7060 passed / 0 failed (623.8s), recorded here at closeout - it was left as `pending` when this entry was first written, which the closeout claims review correctly called out. Each of the 5 new guards MUTATION-CHECKED to be load-bearing: reverting `_merge_field`'s empty-override refusal, `fences_balanced`, `_normalize_newlines`, and `$`-vs-`\Z` each made its own test FAIL. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`: completed.
- Test duplication pressure: dup ratchet clean after one `intentional` classification: the extraction SHRANK four existing families and surfaced one new one that is a pre-existing CLI-boilerplate parallel (`try: <lib call> / except: print; return 2`) across three unrelated commands - verified pre-existing by stashing and re-running, ratchet clean on the base tree. Same span-shift class this repo measured four times on 2026-08-06.
- Critique: TWO bounded rounds, each with a verified `reviewer_boundary_fingerprint` window (both `clean`). Round 1 found 3 blockers: guards attached to the TRANSPORT not the value, so the documented list-argv channel walked past them and wrote a forged heading at exit 0; a lone CR forging a heading via universal-newline read-back; and a FALSE shipped claim that `--slug` fails loudly. Round 2 - the round that read the REPAIRS - found 3 more: an empty `--goal-body` flag overriding a non-empty file value (this helper's own total-loss shape, on the field the channel exists to protect); the fence mask rendering a verdict over a reading `mask_fences` documents as unestablished; and the `_DATE` repair shipped with no biting test. All repaired.
- Off-goal findings: Filed #495 - `docs/handoff-chunked-routing.md` says `draft_goal_from_chunk.py` writes through `upsert_goal`; it renders and writes directly, so a reader would wrongly conclude the new guards cover both goal-artifact writers.
- Lessons carried forward: The round that reads the REPAIRS earned its keep again: round 2's blockers were all the class being repaired. Two are worth carrying: a guard belongs to the VALUE, not to the transport that delivered it - round 1's blocker was that the new checks only policed the new channel while the documented-safe one bypassed them; and a masking primitive that FAILS OPEN turns any caller scanning its output into a verdict over a reading it never established, which is why `mask_fences` ships `fences_balanced` beside it.
- Metrics:

### Slice 2: Make the refill report reach a nested block (#493)

- Objective: `refilled_policy_subkeys` compared TOP-LEVEL keys only, so a nested block (`mutation_testing.report_paths`) whose own leaves were refilled was under-reported. Make the report reach the class its instance came from.
- Why this approach: Third instance in one family - #481 whole-field, #489 sub-key, this sub-sub-key: a checker written against the granularity of the reported instance stopping exactly one level above the next instance. This was a DELIBERATE recorded deferral with its direction stated at the call site, so the slice CASHES IN scheduled work rather than repairing a mistake, and the close says so.
- Commits: `86be2df5`
- What changed: `refilled_policy_subkeys` recurses into a block the operator wrote something into, reporting dotted leaves; a block refilled WHOLE keeps its single block name. The stale call-site comment in `quality_bootstrap_lib.py` and three false or misplaced claims in `skills/public/quality/references/bootstrap-posture.md` were corrected. 6 new unit tests plus 2 end-to-end tests through the real bootstrap. `plugins/` mirrors synced.
- Alternatives rejected: Rejected reporting every leaf of a wholly-refilled block: the goal's stop condition 2 names a report nobody reads as the measured failure mode, and a block name says it better. Rejected touching the dotted `deliberately_absent` DECLARATION vocabulary - explicitly out of scope per Non-Goals, and grep confirms nothing parses these report names back into a key path. Rejected fixing the hollow-refill noise the recursion surfaced; filed as #496 because the predicate choice is a policy decision this slice should not settle by fiat.
- Targeted verification: Both arms of the defect reproduced against the pre-fix function BEFORE designing, plus a false-positive control (fully-specified nested block reports nothing) and the whole-block case. 63 tests green across the two files; broad suite pending. Every new guard mutation-checked: reverting the recursion, and reverting the round-2 outcome-based guard to the round-1 type-based one, each makes its own test FAIL. `run_slice_closeout.py --skip-broad-pytest --ack-cautilus-skill-review`: completed. BROAD SUITE 7068 green - and it caught a regression BOTH bounded rounds and the slice gate passed: the round-2 fallback predicate `merged_sub != default` MIS-named a fully-specified but CUSTOMISED block as refilled, flipping `mutation_testing` from `preserved` to `augmented` in `test_quality_bootstrap_adapter_preserves_existing_explicit_commands`. The predicate is now structural (did the merge produce a block carrying every default key), and both the pre-existing broad test and a new unit test refute the old form. Report size MEASURED at 17 names worst case - under the goal's `dozens` stop condition, and independently re-derived by the reviewer.
- Test duplication pressure: dup ratchet clean, no new family; 8 tests added across two existing files rather than a new one, so no new pool file for the changed-line lane.
- Critique: TWO bounded rounds, both windows verified `clean`. Round 1: the recursion's `else {}` arm reported a partially refilled block as NOTHING - silence, the worse arm of this very defect, written into the repair; a test fixture modelling a merge the bootstrap cannot produce; NO end-to-end proof for the nested case at all; and three false or misplaced claims in the shipped reference. Round 2, reading the REPAIRS: the silence fix stopped at the TYPE boundary, and `{}` is a dict, so it recursed, found nothing and went silent anyway - and my doc correction was ITSELF false, since `mutation_testing` errors on blank scalars and blank nested LEAVES but accepts a blank nested BLOCK header silently.
- Off-goal findings: Filed #496 - the recursion newly reports hollow refills for inert empty-string defaults (`commands.dry_run`), where the attached warning then advises dropping a whole block of real config to silence a claim about nothing.
- Lessons carried forward: Twice now a guard has been placed at the boundary that was easy to test rather than the one that breaks the invariant: slice A attached shape checks to the TRANSPORT instead of the value, and this slice guarded a TYPE (`isinstance(merged_sub, dict)`) when the real question was whether the merge produced the block at all. Deciding on the OUTCOME covered every shape at once. And a doc correction is a claim like any other - mine shipped false, and the fix was to pin it with a test rather than to word it more carefully. The sharpest lesson is the THIRD wrong predicate: two bounded rounds and the slice gate all passed a fallback that MIS-named a fully-specified block, because every control test in the file used DEFAULT values, so `merged == default` masked it. A false-positive control is only a control against the inputs it varies - mine varied presence and not value. The broad suite was the observer that caught it, which is the argument for running it per slice rather than only at closeout.
- Metrics: Host log exposes no per-slice token or tool-call totals; not claimed.

### Slice 3: A standalone-import check for every module in the package (#492)

- Objective: Generalize the one-pair subprocess guard into a repo-wide gate: every module must import FIRST, in a fresh interpreter. A full test suite structurally CANNOT see this class - it imports everything once, in one order, at collection.
- Why this approach: The measured instance passed 4979 tests while being unimportable on its own, and was found by a person reading two import statements. `ruff` does not check import cycles and `check_python_lengths` cannot. Exposure grows with every length-cap extraction, which this repo forces routinely - three in one goal, two of which introduced a defect the suite could not see.
- Commits: `70e32238`
- What changed: NEW `scripts/check_standalone_imports.py`, wired into `staged_commit_gate_plan.py` as a structural-sweep gate scoped to CHANGED modules. NEW `tests/quality_gates/test_standalone_imports.py` (14 tests). `plugins/` mirror synced. Floor-Addition Restraint call recorded at the site: BLOCKING deliberately, with the recurrence measured rather than assumed.
- Alternatives rejected: Rejected scoping the pre-push run for COST: the full sweep is 2.0s for 649 modules at 16 workers (measured), so goal stop condition 1 did not trigger. It is still scoped to changed modules on the different ground that a commit-boundary gate should answer for what the commit touched - and the check prints `PARTIAL: checked N of M` with its verdict so that can never read as a whole-package clean bill. Rejected probing a single import shape: this repo has two legitimate shapes and one-shape probing reported 35 healthy modules as broken.
- Targeted verification: The acceptance that matters: the check FAILS on the real cycle, recovered by reconstruction. The pre-fix module was never committed - the cycle was found and fixed inside the same commit - so the test hoists the function-level sibling imports back to module scope and FIRST proves that reproduction emits the issue's exact `partially initialized module` text before asserting anything about the gate. Every new guard mutation-checked: reverting any of the three inversion-found SCAN_PATTERN entries (of eight total), the `ok` predicate, or the fallback predicate each fails its own test. BROAD SUITE 7083 passed / 0 failed (623.4s) - and it caught the WIRING, which the slice gate and both rounds passed: the gate was registered from the whole touched scope, which includes DELETED files, and this repo has an explicit invariant that a scope path never reaches a per-file validator as an argument. It now takes the existing-file list like its two sibling gates.
- Test duplication pressure: 14 tests in one new file; the mini-repo helper builds throwaway packages for cycle shapes this repo does not contain, and the repo-copy fixture keeps every sweep off the live checkout after `check_test_repo_copy_invariants` correctly refused the first cut for mutating it.
- Critique: TWO bounded rounds, both windows verified `clean`, and the gate's own defects outnumbered anything else this slice. Round 1: `skills/shared/scripts/` (10 modules, the extraction-PAIR family this gate exists for) was unenumerated; the exported mirror matched ZERO skill modules while printing `checked all N`; the shape fallback MASKED cycles; `other_failures` did not block; unmatched paths were named only when the scope collapsed to zero. Round 2, reading the repairs: the mirror repair was PARTIAL because the export flattens twice, and the `plugins/` exclusion in the new inversion test re-hid exactly the tree whose enumeration had just been found broken.
- Off-goal findings: Filed #497 - `scripts/validate_adapters.py` cannot be imported in the exported plugin at all: it hardcodes `skills.public.retro.scripts.resolve_adapter` and the export flattens that path away. Found by this gate on its first run against the mirror, which is the class it was built for.
- Lessons carried forward: The enumeration was wrong THREE times and an inversion test found all three - the repo-root bootstrap shims imported by 135 scripts, then `support/`, then `shared/`. A test that names the families a pattern already matches is a pin against removal, not a completeness check: it cannot fail for a family nobody thought of, which is precisely how each of these escaped. The other lesson is the same one slices A and B taught in different words: the fallback predicate was wrong twice in OPPOSITE directions - too narrow, then too wide - because both cuts asked about the error's spelling rather than about what the fallback was for.
- Metrics: 649 modules discovered in both trees; full sweep 2.0s wall at 16 workers; scoped commit-gate run 0.2s. Host log exposes no per-slice token or tool-call totals; not claimed.

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

- The plan was shaped on 2026-08-06 and its critique is recorded in that goal's
  resolution critique (`../critique/2026-08-06-issue-487-488-489-490-resolution-critique.md`),
  which REFUSED two of four closes and produced #493 and #494. No separate plan-critique
  round ran at activation: the operator had already chosen the unit, all three issues
  carried finished reproductions, and `## Discuss Before Activation` recorded the one
  proof-level non-claim as resolved. Stated here rather than left blank so a fresh
  session knows this section is empty by decision, not by omission.
- The three stop conditions were the plan's own teeth and all three were EXERCISED:
  #492's cost was measured (2.0s, so condition 1 did not fire), #493's report size was
  measured at 17 names (condition 2 did not fire), and #494's field set was deliberately
  NOT made symmetric with its sibling's (condition 3 fired and was honoured).

## Off-Goal Findings

Issues or deferred findings discovered during the run.

- [#495](https://github.com/corca-ai/charness/issues/495) — `docs/handoff-chunked-routing.md`
  says `draft_goal_from_chunk.py` writes through `upsert_goal`; it renders and writes
  directly. Found by slice A's round 2 while checking whether the new input guards'
  blast radius was correctly scoped. The doc currently prevents anyone noticing that
  there are TWO goal-artifact writers and the guards reach only one.
- [#496](https://github.com/corca-ai/charness/issues/496) — slice B's recursion newly
  reports hollow refills for inert empty-string defaults (`commands.dry_run`), where the
  attached warning then advises dropping a whole block of real config. Residue this goal
  CREATED, filed rather than fixed because the predicate choice is a policy decision a
  slice scoped to something else should not settle by fiat.
- [#497](https://github.com/corca-ai/charness/issues/497) — `scripts/validate_adapters.py`
  cannot be imported in the exported plugin at all: it hardcodes
  `skills.public.retro.scripts.resolve_adapter` and the export flattens that path away.
  Found by slice C's own new gate on its first run against the mirror — the class it was
  built for, on day one.
- [#498](https://github.com/corca-ai/charness/issues/498) — the shipped `achieve` goal
  template's `Routing` bullet is garbled by a bad splice and reproduces into every goal
  artifact, including this one. Found by the closeout claims review.

## Final Verification

Closeout evidence — replace each `TODO` with a bound `<path>` (a checked-in
retro / host-log probe / disposition-review artifact) or an explicit
`skipped: <allowed-reason>: <detail>`. The complete gate rejects a literal
`TODO` / `<path>` / `TBD` until you do.

Retro: charness-artifacts/retro/2026-08-07-finish-the-sweeps-this-run-left-retro.md
Host log probe: skipped: host-log-not-exposed: this run executed on a Claude Code host, which exposes no per-session token or tool-call log to the agent. `probe_host_logs.py` did find Codex sqlite logs on this machine, but they belong to a different host and an unrelated session, so citing them would attribute another run's numbers to this one.
Disposition review: charness-artifacts/critique/2026-08-07-finish-the-sweeps-this-run-left-disposition-review.md

**Self-verification.** 3 slices, 3 commits (`25a8e265`, `86be2df5`, `70e32238`),
3 issues repaired. Broad suite 7060 / 7068 / 7083 passed, 0 failed — one full run
per slice (source: `pytest tests/ -q`, 2026-08-07). `run_slice_closeout.py
--skip-broad-pytest --ack-cautilus-skill-review` reported `completed` at every
slice boundary. 6 bounded review rounds, every fingerprint window `clean`, plus a
delegated closeout claims review before the completion flip. 0 gates weakened,
0 `--no-verify`.

**Residual risk.**

1. **The new `check-standalone-imports` gate is BLOCKING and has never refused a
   real push.** It refused the reconstructed cycle and three synthetic ones, and it
   passes 649 modules in both trees — but a gate's false-fire behaviour is only
   learned in traffic. Its new precondition is real: a hard third-party import now
   gates the commit boundary, so an environment missing `jsonschema` or `yaml`
   refuses a commit that previously passed.
2. **Slice B's 17-name worst case is unpinned.** It is a measurement of a report's
   size under a pathological adapter, not an invariant, and a test asserting a count
   would fail on every legitimate defaults change. If `DEFAULT_MUTATION_TESTING`
   grows, nothing notices that the report got longer.
3. **The mirrored gate reports BLOCKED today** on a real pre-existing defect
   (#497). Nothing in the commit path runs it, so this does not refuse anything —
   but a consuming repo that runs it will see a failure this goal did not fix.
4. **The three code slices' round-2 repairs are accepted-unreviewed**, per the
   two-round cap. Two of the three were subsequently exercised by the broad suite;
   slice A's were not.
5. **The delegated resolution critique found instance SIX of this run's own class**
   and it is repaired, not carried: the commit-gate TRIGGER for the new check
   excluded repo-root modules, so a changed `runtime_bootstrap.py` — the exact
   family `SCAN_PATTERNS`'s first entry was added for — would have skipped the gate.
   The enumeration had been repaired and the trigger one layer up still carried the
   original blind spot. Fixed and pinned; recorded here because it is the sharpest
   evidence for #499 that this run produced.

**Non-claims.**

- **No CI, no remote proof, no push at the time the closeout review ran.** Any CI
  statement below this line is recorded separately and by its own channel.
- **The check can only establish what it enumerated.** A module outside its eight
  patterns is unchecked, not clean. Four blind spots are recorded in its own
  docstring, including one (a cycle a module swallows itself) that is undecidable
  from outside the process rather than merely unimplemented.
- **The fingerprint-verify TIMING is practice followed, not artifact-proven.** The
  slice logs record each window's `clean` verdict; they do not record when the
  verify ran relative to the parent's next write.
- **No claim that either deferral was wrong to make.** #493 and #492 were correctly
  recorded decisions; this goal cashed them in, and only #494 was a miss.

## User Verification Instructions

## Auto-Retro

Retro dispositions: applied: two of the three surfaced improvements became committed tests this run, and the third is issue #499 (see the per-improvement lines below).

- applied: tests/quality_gates/test_quality_policy_merge.py::test_a_fully_specified_nested_block_with_CUSTOM_values_reports_nothing plus test_a_wrong_shape_sibling_error_still_falls_through — the improvement "a false-positive control must vary the axis the predicate reads", turned into controls that vary VALUE rather than presence.
- applied: tests/quality_gates/test_standalone_imports.py::test_every_tracked_module_is_either_discovered_or_deliberately_excluded and ::test_the_exported_mirror_enumerates_its_own_modules — the improvement "prefer an inversion test to a family pin", one inversion per tree that ships; between them they found three module families a pin could not have.
- issue #499 — the improvement "when a fix is a guard, name the invariant before writing the predicate". Filed rather than applied because the remedy is a gate-versus-reviewer-question decision on the same axis as #491, and this repo has measured that a gate which cries wolf gets walked past.

Structural follow-up: issue #499 (recurs: the guard-at-the-wrong-boundary class fired 5× across 3 surfaces in one goal — transport-instead-of-value, type-instead-of-outcome, equality-instead-of-structure, and a fallback predicate wrong in both directions; each cost a review round or a broad run)
