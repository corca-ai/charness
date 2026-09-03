# Goal Run #784 session record, 2026-09-03

Planning and establishment session, the same operator day as the #775 close.
No child was started.

## What exists

- Goal Draft `charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md`
  (sha256 `878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151`),
  interview record beside it (`interview-complete`, four questions, all
  answered in this session), binding
  `2026-09-03-lesson-review-and-775-followups.binding.json`
  (sha256 `9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82`).
- Parent #784 with metadata block and cursor (revision 1, next
  `lane-changed-line-done` #785). Children: #785 lane-changed-line-done, #786
  timeout-bound-census, #783 lesson-review-783 (reused; body rewritten with its
  marker), #787 runtime-root-retention, #788 checkout-first-routing-and-8-0-3,
  #789 integrated-closeout. `list-sub-issues` against
  `expected-initial-graph.json`: 6 of 6, none missing or unexpected.
  `goal-run-read` verified-read; `/goal #784` pickup `selected` → #785.
- The first parent metadata block went through the direct `update` command;
  `goal-run-apply update-body` refused the blockless parent (`parent-unverified`),
  as the achieve SKILL.md said it did. Fixed in this session (`fe92c1ca1`): the
  bootstrap `update-body` with explicit operation identity is now the one
  operation a blockless parent accepts, so the next establishment runs on the
  file-backed surface alone. Proven by seeded tests and the changed-line gate
  (`status: clean` against `5eb3adc15`), not by a live re-bootstrap.

## Decided in this session (see the draft's Interview Decisions)

#783 reused as slice 3; 8.0.3 pre-approved and required for slice 5; the
runtime sweep deletes directly under the extended rule; the changed-line
definition of done is a `task run` mechanism plus the docs sentence.

## Done outside the goal, before establishment

The one-off runtime tree sweep (`runtime-sweep-2026-09-03.md`): 340 GB to
about 25 GB; 111 lane worktrees with uncommitted edits salvaged as verified
patches beside their `result.json`. Slice 4 (#787) owns the mechanism and uses
those numbers as its "before".

## Next session, in order

1. Read the ledger preview (`--seed goal-784-session1`) and the #775 closeout
   retro's Next Improvements. Confirm the tree: regenerate the mirror, then
   `python3 scripts/gates_support/run_standing_pytest.py --repo-root .` and
   `./scripts/run-quality.sh --full --read-only`.
2. `/goal #784` → #785 lane-changed-line-done. Body in
   `bodies/lane-changed-line-done.md`. The brief for any lane in this slice
   names `release_changed_line_coverage.py --base-sha <base>` as a
   verification step (the draft's Boundaries).
3. Closeout carrier per child as in run #775 (`Closes #N`, feature); push from
   a clean clone; `verify-closeout`; advance the cursor with an `update-body`
   operation under `operations/`.
4. Slice 3 (#783) is one lesson at a time in Korean; the four top candidates
   wait for their mechanism (slices 1 and 2); the other thirty do not.

## Second session, 2026-09-03 (#785 lane-changed-line-done)

Tree confirmed first: standing runner 8756 passed in 70 s on `8c3bf3769`;
`/goal #784` pickup from the checkout's own `goal_run_pickup.py` returned
`verified-read` naming #785 (the installed 8.0.2 plugin was not used).

Mechanism: `scripts/task_run/task_run_changed_line.py` runs the lane tree's
`release_changed_line_coverage.py --base-sha <lane base> --refuse-unestablished`
once at completion for a validated candidate; `complete_task` writes the verdict
as `changed_line_gate` (status, exit code, consumer `blocking_detail` and
`blocking_targets` verbatim, summary, runtime, logs) and demotes a blocking
verdict to `validated-partial-result` with the line named in `next_step`.

Disconfirming probe, a real lane against this repo with a fake Codex that
commits an uncovered two-branch function into a pool file:

| Probe | Result |
| --- | --- |
| first run | refused, but on the wrong ground: `no-verdict (exit 2): focused producer failed`. The lane worktree is a fresh checkout with no generated `plugins/` mirror, and the standing runner the gate instruments refuses a missing mirror. |
| fix | the gate runner regenerates the mirror in the lane tree first (`sync_root_plugin_manifests.py`, 0.4 s), the same step the push recipe does by hand; a failed regeneration is `no-verdict`, blocking. |
| second run | `validated-partial-result`, `changed_line_gate.status: blocked`, `blocking_detail: {scripts/task_run/task_run_changed_line.py: {changed_and_missing: [239, 240, 241]}}`, gate 23.6 s, lane wall 12 s before the gate. The hand-run gate on the same worktree returned the same detail for the same base. |
| hand run against the pre-amend base | also named lines 89–98 and 137 of the new module: the mirror-sync path had no test. Covered before the slice's own diff passed the gate (`status: clean` against `553f79c7`). |

The consumer's `blocking_targets` is a mapping of path to `[{line, source}]`;
the first cut flattened it to keys. It is carried verbatim now.

Standing runner on the finished slice: 8773 passed in 69 s.

Docs: `docs/agent-task-runs.md` owns the receipt field;
`docs/parallel-execution.md` "Disjoint Writers" carries the definition-of-done
sentence with the measured runtime; `.agents/claude-host.md` carries the same
for in-process subagent briefs, which have no receipt.

## Second session, continued (#786 timeout-bound-census)

#785 pushed from a clean clone as `4057fcb09` (hook lane 87 passed in 162 s),
`verify-closeout` = `verified` (CLOSED), cursor advanced by
`operations/update-parent-progress-786.json` (progress 1/5/6, revision 2);
`/goal #784` pickup names #786.

Two full-lane refusals on the way to that push, both on the new module and
both fixed structurally: the bootstrap-shim consistency gate wanted the
canonical preamble in `task_run_changed_line.py` (the rewriter added it), and
the attention-state visibility gate wanted the receipt's `skipped` state
declared (`attention-state-visibility.json` now carries it with its rationale).

Slice 2: the predicate was written into `timeout-census.md` before the gate,
then extended by one closed rule because the pinned form was blind to the
hosted shape itself (an assert on a name two assignments away from
`result.stdout`). `scripts/gates/check_timeout_bound_form.py` is the sibling
of the wall-clock check, wired as `check-timeout-bound-form` in the standing
lane; its record `timeout-bound-baseline.json` carries four kept sites, each
with its reason. The census read: 4 knob-bound sites the gate sees (all
certain-to-fire, kept), 2 controlled-clock tests exempt, 3 blind sites named,
and one real-process boundary test deleted because its two claims (holder
spawned and line printed before a 0.5 s kill) race the wall clock in the
unsafe direction, cannot be forced on a real check process, and are owned by
the controlled-clock siblings.

## Second session, continued (#786 closed; #787 runtime-root-retention)

#786 pushed as `ede3ac7a9` (hook lane 88 passed; standing runner 8804 passed,
full read-only quality 83 passed on the slice tree), `verify-closeout` =
`verified` (CLOSED), cursor advanced by `operations/update-parent-progress-787.json`
(progress 2/4/6, revision 3). The cursor was moved past #783 deliberately: the
lesson review is a joint per-lesson conversation with the operator, slices 4
and 5 declare no dependency on it, and the planning record says a session may
take them first. #783 and #789 remain for a session with the operator.

Slice 4 landed in three parts: the bootstrap hoists a base that is a
bootstrap's own `xdg-cache` export out of the `charness/runtime` tree so keys
are siblings; `task run` releases a `completed` commit-only lane's worktree and
runtime at completion; `runtime_root_retention.py` sweeps finished lanes (with
verified salvage of uncommitted edits), nested keys, idle rebuilt-on-demand
subtrees, and dead or legacy-idle sibling keys, logs every removal and skip
with bytes and reason under `<key>/retention/` (bounded to the newest 20), and
runs from the standing runner hook and by hand. Details and the first run's
numbers: `runtime-root-sweep.md`.

## Second session, continued (#787 closed; #788 routing half)

#787 pushed from a clean clone (hook lane green; standing runner 8818 passed
and the full read-only quality lane green on the slice tree, after two more
structural fixes the lanes named: the canonical bootstrap shim in
`task_run_completion.py`, and the sweep's `skipped` state declared in
`attention-state-visibility.json`).

Slice 5, routing half: `goal_run_pickup.py` judges its own copy against
`--repo-root` through the provenance guard the write sites already use
(`scripts/core/helper_provenance_lib.py`, tree scan), reports it as
`script_origin`, and refuses a `drifted` installed copy inside the authoring
repo as `stale-installed-copy` naming the checkout's script, before any
provider read. `plan_release_run.py` reports the same field (read-only, so it
reports rather than refuses; the publish helper's entrypoint guard is the
refusal). Read back from the checkout: `same-tree`; from this repo's generated
mirror under `plugins/charness`: `in-sync`. The rule and its reason are in
`bootstrap-resolution.md`, the Claude host adapter, and `docs/development.md`,
which no longer names the installed plugin as an open path.

## Second session, continued (#788 release half, before the cut)

Routing commit `d820d7e21` (standing 8838 passed; full read-only quality green
after the exported reference dropped its issue anchors for the public-doc
coupling gate). Release critique through the `critique` skill's file-backed
Codex workers: two lenses before the repairs (block, five findings; defer,
two), one repair-verification pass after (five confirmed, one minor, two
evidence-binding majors, one wording contradiction), all dispositioned in
`charness-artifacts/critique/release-8-0-3-critique.md`. Acted on before the
bump (`e487d14b1`, `90ba234c7`): the runtime sweep's salvage reads NUL paths
and reads its archive back; the update instruction says what `charness update`
does; the Goal lifecycle page is current; the host adapter and
`docs/development.md` say who refuses and who reports; README names the host
restart; the install/update rehearsal (37 passed) is a tracked receipt. Notes
`charness-artifacts/release/v8.0.3-notes.md`: derived block clean, narrative
lint clean. Final tree: standing 8842 passed; full read-only quality 83
passed, 0 failed. Publish dry run: `bump-and-publish` 8.0.2 -> 8.0.3, no
blockers. The cut runs next through `publish_release.py --execute` with the
#788 carrier; the operator pre-approved the decision on 2026-09-03.

## Second session, closing (#788 closed; 8.0.3 shipped)

The cut ran through the release skill with every step: planner, two fresh-eye
critique reviewers plus a repair-verification pass, `publish_release.py
--execute` to the prepared stop (release lane exit 0 in 164.7 s on the
candidate), four claims-review rounds by a file-backed Codex reviewer, the
claims record committed as the prepared commit's child, and `--resume
--publish-current --execute`. Read back: GitHub release
`https://github.com/corca-ai/charness/releases/tag/v8.0.3` (published
2026-09-03T10:33:33Z), rung-2 https channel `confirmed`, post-publish install
refresh `refreshed` (9.1 s), `charness version` from the managed checkout
`~/.agents/src/charness` reports `8.0.3`, and #788 `verify-closeout` =
`verified` (CLOSED) through the helper's carrier commit `ebfd777ed`.

What the claims rounds taught, recorded for the next release: round 1 and
round 2 each found a real record sentence (the planner does not refuse; a
file add/delete count is not a set comparison; "nothing needs migration" was
unqualified), each repair meant a reset before the prepared record and a new
prepare; round 3 reviewed a stale tree because a chained command had changed
directory into the push clone before running the prepare, so the prepared
commit lived there and not in the checkout; round 4 found no false sentence
and three evidence-boundary gaps, recorded as advisory findings. A prepare
must run in the checkout the reviewer reads.

Cursor advanced by `operations/update-parent-progress-783.json` (progress
4/2/6, revision 5); `/goal #784` pickup names #783.

## Remaining for a session with the operator

- #783 lesson-review-783: the 34 scored active lessons, one at a time in
  Korean, with the operator settling each; the four top candidates now have
  their mechanisms (changed-line done-gate in the lane receipt, timeout-bound
  form check, retention sweep, checkout-first routing) to graduate onto.
- #789 integrated-closeout: standing, full read-only, and release lanes in a
  clean clone; the scheduled mutation run read from GitHub with #764; every
  child `verify-closeout`; the guarded parent close after exact readback.
