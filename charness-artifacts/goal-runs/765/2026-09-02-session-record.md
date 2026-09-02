# Goal Run #765 session record, 2026-09-02

Dated evidence for the first execution session. The provider parent and its
cursor remain the resume state (`/goal #765`); this record exists because the
child closes below are carried in UNPUSHED commits, so the cursor still names
#771 until the operator pushes and the closes land. Run pickup from THIS
checkout's copy (`python3 skills/public/achieve/scripts/goal_run_pickup.py`),
not the installed one under `~/.agents`, which predates #773.

## Session start (next session runs this before anything else)

Pickup (`/goal #765`) will still name #771 as the next child, because the
four closes below are unpushed. Do NOT re-implement #771; follow this order.

0. Authorization on record: the operator approved, in the 2026-09-02 session
   after reading the green boundary, pushing exactly `9ae34cf2b` to
   `origin/main` ("다음 세션에서 그 푸시부터 시작"). This approval covers that
   one ref only; the #768 commits after it stay local until the tree is green.
1. Prove the boundary is still green from a clean checkout of that ref:
   `git worktree add /tmp/wt-9ae34cf2b 9ae34cf2b && (cd /tmp/wt-9ae34cf2b && python3 scripts/sync_root_plugin_manifests.py --repo-root . && ./scripts/run-quality.sh --full --read-only)`;
   read the skip list, not only the summary; then remove the worktree.
2. `git push origin 9ae34cf2b:main` (the pre-push hook runs; if it refuses,
   fix the refusal in a new commit on top of `9ae34cf2b` rather than skipping).
3. For each of #771, #773, #766, #767: `python3 skills/public/issue/scripts/issue_tool.py verify-closeout --repo corca-ai/charness --number <n> --classification feature --carrier direct-commit --commit-ref <commit> --expect-state CLOSED`
   (commits: #771 6673ad6d9, #773 b8a6c7421, #766 d27274cf7, #767 7f4bcf835).
4. Advance the parent cursor through the issue-owned goal-run operations
   (`issue_tool.py goal-run-read`, then an `update-body` operation file under
   `charness-artifacts/goal-runs/765/operations/` with the new `progress`;
   `#773`'s amendment set the precedent at `update-parent-amended-773.json`),
   and re-run pickup until it names #768 (`subprocess-retroactive-removal`).
5. Continue with the #768 steps under "Next session, in order".

## Session start executed (second session, 2026-09-02)

Steps 0 to 4 above are done; the cursor names #768 (`cursor_revision: 4`).

- Step 1 was NOT green at `9ae34cf2b`. A real clone (worktrees lie: a detached
  HEAD trips `plan_release_run.py`, a linked worktree on a branch trips
  `head_oid_from_files`) passed pytest 8554 but failed four later gates that no
  earlier lane had read: bootstrap-shim drift in `goal_run_pickup.py`, "#773"
  anchors in two portable-package docstrings, the repograph captured-reader
  fixture missing `check-unreferenced-scripts`, and the boundary-bypass
  ratchet (one convertible spawn in `test_unreferenced_scripts.py` plus three
  rebound keys from #766/#767 edits). Fixed in `a5002ffc9` on top of
  `9ae34cf2b`, following step 2's "fix in a new commit rather than skipping";
  the fresh-clone lane then read `79 passed, 0 failed`, skip list empty.
- Step 2: the pre-push hook runs the lane against the PARENT working tree, so
  a push from this checkout (on the #768 commits, 131 red) refused. Pushed
  `a5002ffc9` from the fresh clone with the GitHub remote added; the hook ran
  there on the exact tree and passed. `origin/main` = `a5002ffc9`.
- Step 3: `verify-closeout` = `verified` for #771, #773, #766, #767.
- Step 4: `operations/update-parent-progress-768.json` (verified-write,
  identity fields resolved from live metadata, no `binding_sha256` needed
  after #773); body `bodies/parent-progress-768.md`; progress 4/5/9 rev 4.
- Local `main` was rebased onto `a5002ffc9`: the twelve #768 commits have new
  SHAs (tip `0485c7db9` before this record commit). The temporary worktree and
  branch `tmp/wt-9ae34cf2b` were removed.

Lesson: the push hook is a parent-tree gate, not a pushed-ref gate. Prove and
push a boundary from a clone of the ref when the parent tree is mid-migration.

## Integrated locally (closeout carrier in the commit body, `verify-closeout` = carrier_verified)

| Child | Commit subject | Proof that mattered |
| --- | --- | --- |
| #771 rework-instrument | issue/retro: observe consumer rework through the rework label and Causing skill line | packet `charness-artifacts/retro/2026-09-02-771-rework-instrument-packet.md` renders achieve 1, issue 1; `rework` label created and applied to #773 |
| #773 goal-run-binding-simplification | achieve/issue: finish identity-not-content binding for Goal Runs | live `list-children` without identity fields read 8 children; a foreign `binding_sha256` refused by identity (`operations/list-children-773-identity-*.out.yaml`) |
| #766 docs-as-code | docs: retire completed records, verify every page, and make README the user guide | `check-docs.sh` PASS with the new `check-last-verified` component; seeded page turned it red |
| #767 gate-scope-repair | quality: make gate universes recursive, cover shell, and detect unreferenced scripts | `charness-artifacts/quality/2026-09-02-gate-universe-diff.md`; `check_unreferenced_scripts.py --strict` verdict ok; length gate green after splitting two #773 modules |

Each of those four trees passed the full standing pytest (last green: 8554).

## #768 subprocess-retroactive-removal: production done, tests mid-repair

Integrated commits (six lane candidates plus parent fixes, all after #767):

- production: every `subprocess.*` call in `scripts/` and `skills/` now goes
  through `scripts/subprocess_guard.py`; `scripts/check_subprocess_form.py`
  refuses a direct spawn and is green on the live tree (757 files); eval
  runners keep their spawns on `sys.executable`; the guard decodes child
  output with `surrogateescape`.
- tests: lanes T1, T2, T3 migrated most of the 150 spawning test files
  in-process. Three of the six lane commits carry the wrapper's WIP subject
  (`task-run: WIP candidate`); their content was assessed and integrated
  (P2: zero direct spawns left, lint and compile clean; T2 and T3: collect
  parity held). Rewrite those subjects at the #768 closeout.

State of the integrated tree at session end: full standing pytest
`134 failed, 8420 passed`. The failures are the test seam, not production:
tests still patch `module.subprocess.run` on modules that now bind
`run_process`; fakes return bytes; a few assert `CalledProcessError`, which
the guard never raises. `check_subprocess_form.py` is NOT yet queued in
`run-quality.sh` because the runner fixture list (`tests/quality_gates/support.py`)
was inside a repair lane's scope.

## #768 subprocess-retroactive-removal: integrated and green (second session)

Lanes r0, r1, r2 (`briefs/brief-768-repair.md` with `repair-batch-r{0,1,2}.txt`)
and the ratchet lane (`briefs/brief-768-ratchet.md`) ran in parallel at xhigh;
all four returned candidates. The ratchet lane could not write `.agents/` in
its sandbox, so the parent applied the two adapter and surfaces edits in its
worktree and committed there before cherry-picking. Each lane named exactly one
production blocker outside its scope, and the parent fixed each on main:

- `check_staged_worktree_consistency.py` decoded guard text as bytes.
- `inventory_empty_scope_honesty.py` called a loader the bootstrap does not
  export, loaded detectors before swapping argv, and left the detector's
  directory off `sys.path`.
- `test_batch6.py` loaded three modules by path under their bare names, which
  rebinds `sys.modules` at collection time in every xdist worker: three
  order-dependent failures found by bisecting the 563-file collection set.
- `gather_public_url.py` ran its record writer in-process with a shared module
  table; fifteen skills ship a `resolve_adapter.py`, so the wrong skill's
  adapter picked the output directory: an intermittent gather failure.

Full read-only quality lane green with the skip list empty; docs check PASS.
The three WIP lane subjects were rewritten at closeout (P2, T2, T3).

Lessons this paid for: an in-process migration must emulate what a child
interpreter gave for free (empty module table, argv before import, script dir
first on `sys.path`); `load_script_module` under a bare name is a collection-
time rebind, never use it for a module the code under test imports lazily;
bisect the COLLECTION set, not the runtime prefix, when a failure passes alone.

## #774 ledger-only-lessons: integrated (second session)

One Codex lane (`briefs/` not needed; prompt in the commit body) produced every
change except `.agents/retro-adapter.yaml` and `.agents/surfaces.json`, which
the lane sandbox holds read-only; the parent applied those two edits in the
lane worktree and committed there (`93cf83600`, cherry-picked to main).
Proof on main: `recent-lessons.md` absent, `/goal #765` pickup `ok: true` with
`lessons.selection: bounded-ledger-preview`, 164 focused tests, docs check
PASS. Closeout carrier follows #768's.

Lesson: a Codex lane cannot write `.agents/`; a brief that needs an adapter
or surfaces edit must say the parent applies it, or the lane ends uncommitted.

## Next session, in order (written at the end of the second session)

State: local `main` is 40+ commits ahead of `origin/main` (`a5002ffc9`), all
unpushed. #768 is integrated and every gate but one was green at the last full
lane; #774 is integrated and verified. Nothing is closed on GitHub yet.

1. Read "#768 ... integrated and green" and "#774 ... integrated" below, then
   confirm the tree: `python3 scripts/sync_root_plugin_manifests.py --repo-root .`
   (the generated mirror MUST be regenerated after any skill or script edit or
   two mirror tests go red), then `./scripts/run-quality.sh --full --read-only`.
   The only expected red is `check-python-lengths` naming the L4 files if the
   L4 lane (`length-768-L4`, scope: goal_run_pickup.py,
   publish_release_helpers.py, check_artifact_surface_preflight.py,
   recent_lessons_lib.py) did not land; see the "L4" note below for its state.
2. Reword the three WIP lane subjects with `/tmp/reword-768.sh` if it still
   exists, else by hand (`git rebase -i a5002ffc9`): b646c21f6 is the P2
   production lane (skill and worktree spawns through the guard), 697975921 is
   T2 (quality-gate tests in-process), f72baa7b6 is T3 (CLI and coverage-debt
   tests in-process). SHAs are the post-rebase ones on this main.
3. #768 closeout carrier: one commit with `Closes #768`, the template of the
   four earlier closeout commits (`git show 7f4bcf835 -s`), feature
   classification. Acceptance figures measured on this tree: subprocess form
   gate 762 production files, zero direct spawns; test files naming
   `sys.executable` or `"python3"`: 103, files carrying `boundary_contract`:
   85, A minus B 36 (the 36 are helpers and in-process CLI loaders, not
   spawns), B minus A 18; collection 8504 selected of 8635.
4. #774 closeout carrier the same way (`Closes #774`, classification feature,
   rework label already on the issue).
5. Ask the operator for the push of everything after `a5002ffc9` (NOT covered
   by the step-0 authorization). Push from a fresh clone of the ref with the
   GitHub remote added; the pre-push hook gates the PARENT working tree, and
   the runner's basetemp is machine-local.
6. `verify-closeout` for #768 and #774, advance the cursor (`update-body`
   operation like `operations/update-parent-progress-768.json`, progress
   6/3/9 revision 5, next = #769 quality-boundary-and-run-quality), re-run
   pickup until it names #769.
7. #769: the classification now has a third fresh-eye pass applied
   (`charness-artifacts/quality/2026-09-02-gate-classification-769.md`); the
   lane brief should cite rows and treat the 22 conditional `ship` rows as
   the design's centre. Then #770, #772.

## Lessons this session paid for

- The default `run-quality.sh` lane ran five gates and the full lane ran only
  pytest, so the length gate that flagged two #773 modules was not read until
  #767's lane ran it. Read the skip list before calling a tree green.
- A lane whose brief has five heavy items times out at 60 minutes with a WIP
  candidate; the WIP was salvageable every time. Prefer six small lanes to
  one big one, and launch them in parallel.
- `charness task run` refuses a scope glob that matches nothing; seed the
  directory first. It also refuses a dirty parent, so commit before the next
  launch and do not write files while a launch is sleeping.
- Bounded-reviewer reports are truncated by the host around 4k characters;
  ask for under 60 lines and run two passes with disjoint angles.
- A Codex lane cannot write `.agents/`. Two lanes (ratchet, #774) ended
  uncommitted for that reason alone; say in the brief that the parent applies
  adapter and surfaces edits.
- The generated `plugins/` mirror is not tracked but two standing tests
  compare it byte for byte; regenerate it before every full lane.
- The pre-push hook runs the quality lane on the parent working tree, so a
  mid-migration parent cannot push a green ref; push from a clone of the ref.
- A shell `cd` into a lane worktree persists across tool calls; two
  cherry-picks ran inside the lane worktree instead of main. Use `git -C`.
- Bisect the collection set (all test modules import in every xdist worker),
  not the runtime prefix, when a failure passes alone; it found the polluter
  in nine runs of 20 seconds where the runtime bisect found nothing.
- An in-process migration must emulate the child interpreter: empty module
  table, argv swapped before import, script directory first on `sys.path`.
