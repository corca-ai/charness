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

## Next session, in order

1. Relaunch the three repair lanes from `briefs/brief-768-repair.md` with the
   batches `briefs/repair-batch-r{0,1,2}.txt` (replace `__SCOPE__` with the
   batch as a bulleted list). They were stopped at wrap-up with almost no
   edits; the worktrees `task-run/subprocess-768-r{0,1,2}` under the charness
   runtime cache may still exist and can be removed. Integrate candidate-first.
2. Launch `briefs/brief-768-ratchet.md` (retires the boundary-bypass ratchet,
   wires `check-subprocess-form` into the runner, fixture list, and
   timing-layers doc, and runs the issue's acceptance greps).
3. Full standing pytest green, then the #768 closeout carrier (feature
   classification; template in the four earlier closeout commits), rewriting
   the three WIP subjects into it or into a squash.
4. #774 ledger-only-lessons (added by amendment on 2026-09-02, `rework`,
   causing skills retro and achieve): apply `summary_path: null` to this
   repo's retro adapter, delete `recent-lessons.md`, make `goal_run_pickup.py`
   read the ledger preview, and drop the digest comparison from this lane.
   Body: `bodies/ledger-only-lessons.md`; operation
   `operations/amend-add-ledger-only-lessons.json` (verified-write). Small;
   one lane or the parent directly.
5. #769 quality-boundary-and-run-quality: the parent's design is
   `charness-artifacts/quality/2026-09-02-gate-classification-769.md`,
   reviewed twice by bounded reviewers; both reports were truncated by the
   host, so angles 2 to 4 beyond the recorded rows are unreviewed. The real
   finding: eight `ship` gates need adapter-declared inputs or they are a
   vacuous green in a consumer repo. Then #770, #772.
6. Once the #768 tree is green and its closeout carrier is verified, ask the
   operator for the push of the remaining commits (that push is NOT covered
   by the step-0 authorization), then verify #768 CLOSED and advance the
   cursor the same way as step 4 of "Session start".

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
