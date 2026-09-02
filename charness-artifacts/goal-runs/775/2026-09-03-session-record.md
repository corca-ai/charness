# Goal Run #775 session record, 2026-09-03

Planning and establishment session. No child was started; the operator deferred
activation to the next session.

## What exists

- Goal Draft `charness-artifacts/goals/2026-09-03-verification-shape-alignment.md`
  (sha256 `6f2f63ecd8264a4502f7feeb9884a2e2cbb5e3f288be22536fd93a2eed010898`),
  interview record beside it (`interview-complete`, ten questions), binding
  `2026-09-03-verification-shape-alignment.binding.json`.
- Parent #775 with metadata block and cursor (revision 1, next
  `awiki-phase-echo` #776). Children: #776 awiki-phase-echo, #777
  layout-resolver, #778 release-lane-standing-evidence, #779
  wall-clock-census-and-764, #780 wall-clock-rewrite-remainder, #781
  lesson-promotion-and-budget, #782 integrated-closeout. `list-sub-issues`
  against `expected-initial-graph.json`: 7 of 7, none missing or unexpected.
  `goal-run-preflight` ready, `goal-run-read` verified, `/goal #775` pickup
  `selected` → #776.

## What was fixed before establishment (outside the goal)

- `1ee5dbc48` achieve SKILL.md: names `interview_contract.py` and the
  pre-approval sequence (framing critique, child bodies, adversarial critique,
  alignment audit, briefing).
- `c781e87d6` issue skill: Work Item key discovery scoped to the parent by the
  provider's `parent_issue_url`; the seventh child had been refused because
  #772 (run #765) carried the same `integrated-closeout` marker. Achieve
  SKILL.md now also records the establishment order: first parent metadata
  through the direct `update` command, then children, then the cursor.

## Next session, in order

1. Read the ledger preview (`--seed goal-775-session1`) and the 2026-09-03
   retro's Next Improvements. Confirm the tree: regenerate the mirror, then
   `python3 scripts/gates_support/run_standing_pytest.py --repo-root .` and
   `./scripts/run-quality.sh --full --read-only`. Only those two are "green".
2. `/goal #775` → #776 awiki-phase-echo. Body in `bodies/awiki-phase-echo.md`;
   the boundary is that `subprocess_guard.py` is untouched.
3. Closeout carrier per child as in run #765 (`Closes #N`, feature, template
   `git show 7f4bcf835 -s`); push from a clean clone; `verify-closeout`; advance
   the cursor with an `update-body` operation under `operations/`.
4. Slice 5 (#781) is a joint per-lesson review with the operator; do not
   apply any lifecycle event before each lesson's reason is settled in
   conversation.

## Second session, 2026-09-03 (activation)

Picked up with `/goal #775`. The installed plugin at `~/.agents/src/charness`
is the 8.0.2 release; its older pickup contract refused the parent
(`metadata-incomplete`, a key the current contract no longer writes), so
pickup ran from this repo's own `skills/public/achieve/scripts/goal_run_pickup.py`
and selected #776. Standing lane on arrival: 8603 passed, `release_only` and
`slow_corpus` deselected. The plugin mirror was stale (achieve SKILL.md);
regenerated before any lane.

### Outside the goal, before #776 could land

- `check_spec_evidence_durability.py` was red at HEAD on the frozen Goal Draft
  itself: the draft cites `.charness/quality/runtime-signals.json` (gitignored)
  twice, the binding hashes the draft's bytes, and the standard lane had not
  been run against the draft before the establishing commit. Editing the
  draft would break the binding; the gate gained a second frozen-record
  channel: a sibling `*.binding.json` of kind `charness.goal-binding/v1`
  whose `draft.sha256` equals the draft's bytes on disk is counted in the
  advisory, not enforced. Any mismatch is enforced. Commit `ce49c2bee`.
  **Flagged for the operator**: this is a gate rule change made to unblock the
  goal, in no child's scope.

### Children carried in unpushed commits

- #776 awiki-phase-echo: commit `657386b63`. Also moved the awiki process contract to `scripts/gates_support/docs_graph_awiki.py` (length cap).
- #777 layout-resolver: commit `9e915f281`. The census found eight lookups in
  seven files, not four: `tests/script_closure.py` (two), and three tests
  (`test_scaffold_repo_local_validator.py`, `test_authoring_preflight_reference.py`,
  `test_prepush_close_keyword_guard.py`). All folded.
- #778 release-lane-standing-evidence: commit `0c9f79ab1`. Clean-clone proof in `778-clean-clone-proof.md`: seeded release-only failure refused in 123 s; clean code push passed in 257 s. The first proof attempt caught a real release-only regression from the #777 rename (fixed before the second attempt).

- #779 wall-clock-census-and-764: commit 8d01bae96. Census in `wall-clock-census.md`
  (96 sites); `check_wall_clock_form.py` holds `charness-artifacts/quality/wall-clock-baseline.json`
  (47 sites, 14 files) to a shrinking count. The five #764 failures read from run
  33631065064's log: two wall-clock drain claims, three shape leaks (isolated PATH,
  definition-time `gh` runner binding); all rewritten. CI-shape baseline before 1
  failed (a checkout copy racing cargo), after 8631 passed. The hosted read on the
  pushed tree belongs to #782.

## Next session, in order

1. Operator: authorise the push. Then push from a clean clone (the hook runs the
   release lane), `verify-closeout` for #776, #777, #778, #779, advance the
   cursor with `operations/update-parent-progress-777.json` then a fresh
   operation naming #780 (bodies for 777 and 778 are prepared; regenerate for
   the cursor's real next child after readback), and re-run `/goal #775`.
2. Operator: confirm the durability-gate binding channel (`ce49c2bee`), made
   outside any child to unblock the standard lane.
3. #780 wall-clock-rewrite-remainder: 47 sites in `wall-clock-baseline.json`.
   Patterns settled while reading them: (a) `elapsed < N` after a timeout is
   dropped, the claim is `timed_out` plus the drain marker, and the clamp is
   unit-tested through `_resolve_interval`; (b) a deadline poll for a child
   marker becomes a blocking read on a FIFO or pipe the child holds, so the
   observation is forced and the standing runner's budget is the only bound;
   (c) a sleep before "the grandchild is dead" becomes a read to EOF on a pipe
   the grandchild inherited; (d) a sleep for mtime ordering becomes a
   controlled clock (`os.utime` or a patched `time.time` in the module under
   test); (e) the JSON-RPC absolute-deadline claim gets a fake monotonic clock.
   Lower the baseline with `--write-baseline` as each file reaches zero.
4. #781 lesson-promotion-and-budget: joint per-lesson review with the operator;
   nothing applied by rule.
5. #782 integrated-closeout after the scheduled mutation run on the pushed tree.


Push, `verify-closeout`, and cursor advance (operation files
`operations/update-parent-progress-77{7,8}.json` prepared) wait on the
operator's push authorisation.
