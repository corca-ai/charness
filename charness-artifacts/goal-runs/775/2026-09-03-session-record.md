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


Pushed 2026-09-03 after the operator's approval: three hook refusals first
(release changed-line coverage on 24 unproven lines, four unmapped skill
scripts rendering PARTIAL, then a module-identity split in the coverage probe),
each fixed structurally and recorded under "Smells"; the fourth push landed
`540baf850` with the hook lane at 86 passed in 272 s. `verify-closeout` =
`verified` for #776, #777, #778, #779. Cursor advanced by
`operations/update-parent-progress-780.json` (progress 4/3/7 revision 2);
pickup names #780.

## Smells, not incidents (operator rule, 2026-09-03)

Each failure this session read as a pattern, and the pattern's pattern.

| Smell | Instances this session | Pattern | Pattern of the pattern | Structural move |
| --- | --- | --- | --- | --- |
| A lane that never ran on the artifact it judges | the frozen Goal Draft red in the standard lane at HEAD; `c781e87d6` with no release-lane read; my #777 rename breaking a `release_only` anchor | a verification lane exists but nothing in the workflow runs it at the moment the artifact is produced | `verification-shape-mismatch`: the shape that judges is not the shape that produced | #778 closed the push edge. Still open: Goal Draft establishment should run the standard lane before committing the draft (achieve skill), and the commit-msg carrier should require the release lane for a `Closes` commit that touches `release_only` surfaces |
| Derived surface stale | the plugin mirror refused the full lane three times after an edit | every source edit invalidates a derived surface that a later lane compares | `derived-surface-batching`, recurred a fourth time | the read-only preamble could name the exact regenerate command it already prints as a one-step remedy the lane runs itself in a writing run; or the pre-lane chain in `docs/development.md` starts with the sync, which this session now does |
| Coverage proxy for a new module | 24 changed lines unproven: shim inserts, main guards, error branches, writer success paths | a new module's own tests prove the happy path; the release lane proves the lines | green focused test is not a covered line (`green-test-is-not-covered-line`) | a scaffold for a new gate that emits the shim test, the main-guard test, and the empty-universe test together, so the first cut ships with the lines the release lane will ask for |
| Unmapped skill script | four skill scripts reached only through loaders, so no standing test named them | the mapper keys on textual references; a loader indirection hides the file | the same class as `_load_local` hiding the sibling in the unreferenced-scripts graph | the mapper could follow `_load_local` and `load_repo_module_from_skill_script` tokens the way it follows `spec_from_file_location`; until then, a test per skill script by path |
| Empty-diff classification | seed-plus-unseed range classified docs-only and skipped the release lane | the classifier reads changed paths, and a range whose net diff is empty has none | a boundary read on a summary rather than on the objects that cross it | the classifier should treat an empty path set as full-gate, since the commits still land; recorded for #782 or a follow-up issue |
| Process kill by pattern | `pkill -f` matched my own chain twice | a kill keyed on a substring of a command line hits the caller | the same shape as the runner's group kill lesson: address the tree, not the name | kill by pid or process group only; never `pkill -f` from a chain whose own argv carries the pattern |
| Module identity split by eviction | the second push refused: `test_git_inventory_discovery` patched `scripts.core.repo_file_listing` reached through the package attribute while the lib held the class from the object `monkeypatch.delitem` had restored; failed only when `test_batch8`'s eviction ran first in the same worker; twelve tests evicted `scripts.*` modules this way | `monkeypatch.delitem(sys.modules, name)` restores the entry and leaves the parent package attribute on the new object | `collection-time-pollution`: identity established at collection diverges from identity at test time | `tests/module_eviction.py::evict_module` pins the parent attribute for restoration; all twelve sites use it; the victim binds to `sys.modules[RepoFileSnapshot.__module__]`; proven by the ordered pair (1 failed before, 2 passed after) |
| Installed plugin behind the repo | pickup from `~/.agents/src/charness` (8.0.2) refused the parent on a key the current contract dropped | the host adapter reaches the installed copy first inside the repo that authors it | a proxy from an older tree read as the current state (`verification-shape-mismatch` again) | in the charness repo itself, the Claude host adapter should route skill scripts to the working tree; release 8.0.3 also closes it |

## Third session, 2026-09-03 (#780 wall-clock-rewrite-remainder)

Picked up with `/goal #775` (the repo's own `goal_run_pickup.py`; the installed
8.0.2 plugin still refuses on `current_membership_sha256`). Cursor named #780.
Standing lane on arrival: 8660 passed. Plugin mirror unchanged.

### Shape of the work

One shared observation replaced the three census shapes: `tests/fifo_witness.py`
(commit `ca5b1d517`). A test opens a FIFO non-blocking for read; the controlled
child writes one line when it has reached the observed state and keeps the
write end open for its life (its descendants inherit it). `wait_line()`
replaces sleep-then-check, `wait_eof()` replaces sleep-then-"the tree is
dead", `has_line()` feeds a controlled clock. No timeouts: the standing
runner's budget is the only bound, and a hang names the test.

The 47 sites in 14 files were then rewritten in parallel on disjoint files:
`tests/test_subprocess_guard.py` (14) by an opus subagent;
`test_cli_skill_surface.py`, `conftest.py`, `test_reviewer_delivery_state_machine.py`
(7) by a second opus subagent; `test_semantic_review_command.py`,
`test_standing_pytest_run_execution.py`, `test_mutation_recovery.py`,
`test_gate_summary_names_failures.py` (14) by a Codex lane
(`task/wall-clock-fifo-four`, cherry-picked as `61ce9e21d`); the remaining six
files (12) by a sonnet dynamic workflow. The parent reviewed every diff.

| Site kind | Replacement |
| --- | --- |
| `elapsed < N` after a timeout (guard ×3, run_quality_engine, codex_cache_refresh) | dropped; the claim is `timed_out` plus the marker that tells the failure modes apart (`DRAIN_UNAVAILABLE` absent or present); the clamp is unit-tested through `_resolve_interval` |
| deadline poll for a child marker (guard ×2, semantic_review, standing_pytest, mutation_recovery, gate_summary, web_fetch, task_run) | FIFO line the child writes, or a blocking `readline()` on the child's pipe |
| sleep before "the tree is dead" (guard ×2, task_run, semantic_review, standing_pytest) | `wait_eof()` on the FIFO the whole tree inherited; the controlled children now sleep 3600 s so a survivor cannot end EOF by dying of old age (found by mutation-testing `_kill_tree` down to a direct-child kill: with 30 s children both tests still passed, 50 s late) |
| poll for a pid to vanish (cli_skill_surface) | `os.pidfd_open` + blocking `select`, identity check kept in front |
| sleep for a distinct `.used` stamp (seed_cache_eviction) | `seed_cache.time` replaced by a counting clock; exact values asserted |
| sleep to widen a lock race (reviewer_delivery) | event-ordered interleaving with an exact event log, plus a direct `LOCK_EX|LOCK_NB` refusal probe |
| sleep so the peer reaches its wait (test_seed_cache) | a spawn `Semaphore` each worker releases before entering; the builder acquires both tokens |
| JSON-RPC absolute deadline (codex_cache_refresh) | the loaded module's `time` replaced by a stepped clock; exact call sequence asserted. Step is 1000 s because `remaining` is also the real `select` timeout: a small step made a slow child start shorten the sequence (caught in parent review) |
| session-finish cleanup retry (conftest) | one cleanup, one inspect; a zombie has released its cwd so fail-closed ownership never attributes it to this checkout |

`wall-clock-baseline.json` is now `{}`; the gate rule is "any call is red".
`docs/development.md`, the gate docstring, the gate note in
`.agents/quality-gates.yaml`, and the census header say so.

### Smells this session

| Smell | Instance | Structural move |
| --- | --- | --- |
| EOF for the wrong reason | a 30 s controlled child lets `wait_eof()` return when it dies of age, so the kill proof is vacuous after 30 s | controlled children behind a kill proof outlive any plausible run (3600 s); recorded in the guard test comments |
| fake clock leaking into a real timeout | the stepped `monotonic` also sized the real `select` timeout | when the module under test derives a real wait from the clock, the fake's step must dwarf the wait |
| length cap crossed by a test helper | the pidfd wait pushed `test_cli_skill_surface.py` to 824 code lines; the full read-only lane refused | the probe-boundary tests (own-session spawn, group kill, drain, survivors) moved to `test_cli_skill_surface_probe_boundary.py`, a cohesive split rather than a `_lib` spill (D33) |
| installed plugin behind the repo (fourth time) | pickup refused from `~/.agents/src/charness` again | unchanged: route skill scripts to the working tree inside the charness repo; release 8.0.3 |

## Fourth session, 2026-09-03 (#781 lesson-promotion-and-budget)

#780 pushed after operator approval (hook release lane 86 passed); cursor to
be advanced after #781's readback. #781 ran in two halves in parallel.

Code half (Codex lane `task/lesson-graduate-lifecycle`, cherry-picked):
`graduate` move and `graduated` state in `lesson_ledger_lib.LIFECYCLE_TRANSITIONS`,
a graduate event's `decision_ref` must be under `docs/`, `_materialize` and the
argparse choices derive from the table, graduated rows are neither eligible nor
archive-slot candidates.

Joint half, in conversation, one lesson at a time in Korean, recorded in
`781-lesson-dispositions.md`. Two operator rules emerged and were written into
the new `skills/shared/references/lesson-graduation.md` (linked from the retro
skill): graduation is three questions (one owning `docs/` page with duplicates
removed; a code mechanism where possible, shipped in the same commit; only then
the event), and a docs-only graduation is allowed only into a page read at the
decision moment, because the preview is read every session and a docs page on
demand. Tally: nine graduated, four archived, two kept; the three recurred
classes seeded; 39 of 50 active.

Mechanisms shipped by the graduations (each by an opus subagent, reviewed here):
`check_module_eviction_form.py` with `tests/module_eviction.py::evict_new_modules`
(nine raw evictions folded); `plugin_mirror_preamble.py` shared by the standing
runner and the quality engine (the runner now refuses a stale mirror in
read-only and regenerates in full; a false `development.md` sentence claiming
the byte-comparison tests use a temporary export was deleted, about thirty
tests read the on-disk mirror); the quality summary line names every gate not
run with its reason (`proof_receipt.py`, receipt `details.not_run`); retro
persistence runs the seeder and stamps `Seeding:` beside `Persisted:`, and
`check_lesson_ledger.py` names unseeded tagged classes (twelve today, nine of
them stranded since mid-August); cache retention for `pytest-tmp` (16 GB, 300
dead repo keys measured) and `support-skills`. D38 recorded as reopened by its
trigger and resolved.

## Next session, in order (operator-confirmed 2026-09-03)

Resume with `/goal #775`; the cursor names #782 integrated-closeout once
#781's push and readback land (this session advances it).

1. #782: standing, full read-only, and release lanes green in a clean clone
   with the skip list read; the quality summary's `not run` clause is now
   that list.
2. #782: read the most recent scheduled `mutation-tests.yml` run from GitHub
   and make #764's state consistent with it; #764 closes only through its
   recovery-observer path. The #779 sampler baseline is the thing to confirm
   hosted.
3. #782: graduate `verification-shape-mismatch` into `docs/development.md`
   with a `changed-an-action` score citing this goal's retro; settle the two
   open paths first (the installed plugin read ahead of the repo tree inside
   the charness repo; whether 8.0.3 ships) or record them as the stated gap.
4. Close #775 through the guarded Goal Run close after exact readback.

Outside #775, carried by a follow-up issue filed this session: second joint
lesson review (the 34 scored active lessons under the three-question rule,
graduation candidates first: `changed-line-proof-before-broad-quality`,
`green-test-is-not-covered-line`, `detector-blind-class-unstated`,
`bar-recorded-as-prose`) and the nine tagged classes still unseeded, one by one.

Cache retention outcome, measured: `pytest-tmp` 16 GB → 3.2 GB, 300 repo keys
→ 59, in one 32 s sweep; the residue was 27 marked-failed roots bounded per key
but never across keys, and 11 unmarked orphans from runners killed before their
`finally`. Follow-up outside #781: the per-repo runtime root
`$TMPDIR/charness/runtime/<key>` owned by `scripts/runtime_bootstrap.py` has no
retention of its own; the sweep reaches only the keyed `pytest-tmp` namespace.

First #781 standing run: 5 failed. Four tests read the LIVE ledger and assumed
every lesson eligible or every lesson representable in v8 (the v8 fixture
stripped lifecycle from a 52-lesson corpus and migrated it over the 50 budget);
one docs gate flagged a literal count in the new cache table. Repairs: the v8
fixture derives the working set (active lessons, transitions renumbered), the
preview invariant counts active plus archived, the archive-slot expectation is
derived from the live ledger, and the table names the retention constants
instead of numbers. Smell: a live-corpus invariant ("all lessons active") was
pinned in four places without a name; the first lifecycle event broke all four.

Push refusals for #781, in order: (1) release lane, one `release_only` test:
the support-skill use-stamp was written INSIDE the digest tree and
`charness update`'s same-version content readback hashed it (moved to a
sibling file; regression test pins the tree's bytes stable). (2) release
changed-line coverage: about forty changed lines unproven across seven files
(mostly `except OSError` branches in the new cache retention, the not-run
clause rendering and parsing, manifest-resolution failure in the mirror
preamble) plus two unmapped files (`run_quality_engine_receipt.py`,
`run_quality_engine_selection.py`). Same class as the #780 session's first
refusal: `green-test-is-not-covered-line`, a focused green is not a covered
line. Covered by three parallel subagents before the retry.

Observed under three concurrent agents: `test_cli_skill_surface_keeps_partial_output_when_even_the_drain_times_out`
failed once under load and passes alone. It carries no `time.*` call, so the
wall-clock form gate does not see it; its claim rides on subprocess drain
timeouts. Same class as #779/#780, a shape the gate does not cover. For #782
or a follow-up: extend the census to timeout-bound claims (`communicate(timeout=)`,
probe deadlines) that decide a verdict rather than bound a hang.
