runtime: keys are siblings, finished lanes keep only their record, and the runtime root has a retention rule (#787)

Closes #787

The per-repo runtime tree had one retention rule (pytest-tmp) and measured
340 GB on 2026-09-03: 266 GB of finished lane records that kept their
worktrees, 41 GB of other repos' runtime keys nested inside this repo's own
xdg-cache, and 1,867 keys whose repo was gone. Three changes: the bootstrap
hoists a child's base out of a parent's exported xdg-cache so every key is a
sibling; `task run` releases a completed commit-only lane's worktree and
runtime at completion, naming the branch that carries the candidate; and a
sweep beside the pytest-tmp rule removes finished lanes' worktree and runtime
(salvaging uncommitted edits as a verified patch first), nested keys, idle
rebuilt-on-demand subtrees, and dead or legacy-idle sibling keys, logging
every removal and skip with bytes and reason, never reaching outside
charness/runtime/ and never touching a lane's result.json or logs.

Classification: feature
Jtbd: a session does not stop for lack of disk, and a finished lane's record stays readable after its 2.5 GB of worktree and runtime are gone.
Boundary: scripts/runtime_bootstrap.py (the hoist and the repo-root marker), scripts/gates_support/runtime_root_retention.py (new), scripts/gates_support/run_standing_pytest.py (the hook), scripts/task_run/task_run_completion.py (release at completion), tests/test_runtime_root_retention.py (new), tests/charness_cli/test_task_run.py (the lane-runtime test rewritten for release semantics plus the retained worktree-only case), docs/development.md (cache table rows), docs/agent-task-runs.md (the receipt's retention field), .agents/claude-host.md (integrate from the branch), charness-artifacts/goal-runs/784/runtime-root-sweep.md and the session record. TMPDIR placement, the pytest basetemp contract, and the seed and support-skill caches' rules are unchanged.
Resolution Brief: charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md slice 4 and the #787 Work Item body.
Implementation: the live-tree assumption the body asked to name surfaced in the first test run: pytest's tmp_path sits under this run's own key, so a cache home a test points there is inside a charness/runtime tree by construction; the hoist is therefore limited to a base that is a bootstrap's own xdg-cache export, and a plain cache home is used as given. The dry run over the live tree took 0.6 s and planned 598 removals; the first real run, from the standing-runner hook, removed those 598 finished fixture-lane runtimes (4 MiB) and skipped 1,287 nested keys touched within the one-day active window; the by-hand run recorded for the slice removed nothing because everything left had been touched today. The tree reads 16 GB before and after; the hand sweep the same morning had already taken it from 340 GB to 25 GB.
Prevention: tests/test_runtime_root_retention.py seeds every shape the rule names in one idle tree (clean and dirty finished lanes, a running lane, a nested key, idle and fresh subtrees, dead, live, legacy-idle and legacy-fresh sibling keys, a directory outside the tree) and asserts each disposition, the verified patch and tar, the skip reasons, the log, the dry run's zero effect, an unverifiable salvage keeping the worktree, a live pytest run lock, read-only files, an explicit runtime root, the bounded logs, and the three inherited-environment shapes landing as siblings; test_task_run.py proves a commit-only lane keeps only result.json and logs with its commit on the branch, and a worktree-only lane is retained.
Behavior: verified — 13 retention tests and 43 task-run tests green; ./scripts/check-docs.sh PASS; the standing runner and ./scripts/run-quality.sh --full --read-only green on the finished tree (counts in the session record); the changed-line gate on this slice's own diff clean; the sweep's first live run logged under the key with du before and after in runtime-root-sweep.md.
Review disposition: critique not required; a deletion rule proven against a seeded tree for every class it names, with the live run logged and bounded to charness/runtime/.
AI-provenance: implemented, probed on the live tree, and verified by an AI agent (Claude Code) in the Goal Run #784 session; the direct-deletion policy is the operator's 2026-09-03 decision.
Goal lineage: Goal Run corca-ai/charness#784; draft sha256 878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151; binding sha256 9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82; Work Item runtime-root-retention (#787).
