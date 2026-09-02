# Goal Run #765 second session: #768/#774 integration

## Context

Second execution session of Goal Run #765 (north-star realignment). Under
review: the session-start procedure and the push of the `9ae34cf2b` boundary,
the integration of four #768 repair lanes plus four length-split lanes, the
#774 ledger-only-lessons lane, and the third fresh-eye pass on the #769 gate
classification. What matters next: the #768 and #774 closeout carriers, the
operator-authorised push, and the #769 lane, all listed in
`charness-artifacts/goal-runs/765/2026-09-02-session-record.md` under "Next
session, in order".

## Window

2026-09-02, from `git push origin a5002ffc9:main` to local `main` at the L4
integration (`800c6dbad`), 45 commits after the pushed boundary; nine Codex
lanes at xhigh; four bounded reviewers; roughly seven hours of parent time.

## Evidence Summary

- The session record (`2026-09-02-session-record.md`) and this checkout's
  commit log after `a5002ffc9`; every parent fix names the lane blocker it
  answers in its commit body.
- Full-lane logs kept in `/tmp/quality-768-{1..6,final}.log` (not durable);
  the standing runner's failure logs under the charness runtime cache.
- Lane receipts (`result.json`) for r0, r1, r2, ratchet, L1 to L4, and
  ledger-only-lessons-774; their Codex stdout tails.
- Reviewer reports for the #769 classification, applied as rows marked
  `third pass` in `charness-artifacts/quality/2026-09-02-gate-classification-769.md`.
- No adapter `metrics_commands`; this retro is narrative with the counts
  above taken from those logs. `probe_host_logs.py` was not run: the session
  crossed a `/goal clear`, so a turn or token count would not bound one unit
  of work.

## Waste

- **Two lanes ended uncommitted for one reason: the Codex sandbox holds
  `.agents/` read-only** (ratchet, #774). Each cost a parent round of reading
  the worktree, applying two edits, and committing there. Neither brief said
  the parent applies adapter or surfaces edits. (recurrence-class: lane-brief-omits-parent-owned-surfaces)
- **Three full-lane runs were spent on the untracked `plugins/` mirror.** Two
  standing tests byte-compare the generated export with source; every skill or
  script edit made the next lane red until `sync_root_plugin_manifests.py` ran.
  The record from the first session did not name this. (recurrence-class: derived-surface-batching)
- **The #768 migration's largest defect class was invisible under pytest.**
  39 files imported `scripts.subprocess_guard` as a package, which resolves only
  when the repo root is on `sys.path` (pytest) and not when the script runs as a
  CLI from its own directory. Nine gates went red at once; the lanes' own
  verification (focused pytest) could not see it, and my first detector ran
  with the root on the path and reported zero broken. Half a day of lane work
  shipped a tree that no gate but the full lane could refuse.
- **Order-dependent failures absorbed the longest single stretch.** The
  runtime-prefix bisect (pairwise, then whole prefix) found nothing in three
  rounds; the collection-set bisect found `test_batch6.py` in nine 20-second
  runs. The gather flake needed the same reasoning at production level (shared
  module table across in-process child runs).
- **Two cherry-picks ran inside a lane worktree** because the shell `cd`
  persisted across tool calls; each needed an abort and a re-run with `git -C`.
- **Serial verification gaps**: the parent waited on full lanes (2 to 3 min
  each) seven times. At least three of those would have been avoided by
  reading the length gate and regenerating the mirror before launching.

Not waste: the four #769 reviewers ran during lane wait time and their
findings changed ten rows; the wait was already committed.

## Critical Decisions

- **Fixing the boundary on top of `9ae34cf2b` rather than blocking on a
  re-authorisation.** The record's step 2 already licensed "fix the refusal in
  a new commit rather than skipping"; the same reading applied one step
  earlier. Pushed exactly one fix commit, from a fresh clone so the pre-push
  hook gated the pushed tree, not the mid-migration parent.
- **Candidate-first integration with the parent owning every out-of-scope
  blocker.** Each lane named exactly one; fixing them on main immediately
  after the pick kept the tree's failure count monotone (134 → 89 → 66 → 10 →
  3 → 1 → 0 on pytest).
- **Launching #774 and the four length lanes in parallel with #768's tail**
  instead of after it. The order dependency was cursor-only; the tree cost was
  one mirror regeneration.
- **Bisecting collection instead of runtime once the runtime prefix came back
  clean.** This is the decision that ended the longest stretch.
- **Isolating `sys.modules` around gather's in-process child** rather than
  reverting gather to a real spawn: the migration's rule (in-process unless the
  boundary is the claim) held, at the price of emulating the child interpreter.

## North Star Alignment

Read from `docs/design-north-star.md` (2026-09-02).

- **P4 held at the push boundary.** The first-session record called
  `9ae34cf2b` green; a distinct channel (fresh clone, full lane, skip list
  read) refuted it with four red gates before the push. The session then
  applied the same discipline to lane candidates: every lane's own "green" was
  re-read on main, and each was wrong about one thing.
- **P5 mis-applied once, then corrected.** The pre-push hook is a terminal
  green over the wrong subject (the parent working tree); pushing from a clone
  of the ref treated the hook as a question about the pushed tree, which is
  what it is for. The lesson is recorded; the hook itself is unchanged (the
  #769 declarative-runner work owns it).
- **P2 inverted by the migration, then restored.** Twelve files crossed the
  length cap because the guard migration added lines; the splits are cohesive
  modules, not `_lib` spill, and the gate stayed armed.
- **Named failure signature walked into: terminal trust in a lane's green.**
  Nine lane reports said "passing" under a verification that could not observe
  the CLI import shape. The refutation channel (full lane on main) existed and
  was used; the miss was not running it before the next launch.
- **Consumer subject:** the #769 third pass moved the classification toward
  what a consumer repo owns (seven `tools` rows became `ship`, three `ship`
  rows that probe charness source became `tools`), which is the north star's
  own question.

## Trends vs Last Retro

The 2026-08-31 session retro asked for: (1) never quote a derived metric
before one adversarial pass, (2) spend a subagent only after the target
survives its own check, (3) verification instruments need a negative control.
This session: (1) held (the "0 broken" detector was distrusted and re-run the
way the gate runs); (2) partly held (reviewers were launched during idle time;
the four length lanes were launched before I had measured which files
exceeded from #774, so L4 was a second launch); (3) held once (the poisoned-
order repro for gather was run before and after the fix). New this session and
absent last time: sandbox-boundary waste in lanes, and generated-surface waste.

## Expert Counterfactuals

- **Engelbart (system-improving-itself), applied to the lane harness.** The
  tool (T) is `charness task run`; the method (LAM) is the brief. This session
  changed the method by hand nine times (add `.agents` note, add mirror
  regeneration, add "verify as the gate runs") and never the tool. The
  counterfactual: after the first uncommitted lane, add to the lane receipt a
  `parent_owned_paths` list computed from the sandbox's read-only set, and
  have `task run` refuse a scope that names one of them unless the brief
  declares the parent applies it. The second uncommitted lane (#774) would
  then have been a refused launch, not a 90-minute WIP.
- **Charity Majors (observe the production shape, not the test shape).** The
  39-file defect was invisible because every verification ran under pytest's
  `sys.path`. Her move: before integrating any migration that changes how a
  module is reached, run one probe in the shape production uses (here:
  `python3 <script> --help` from the repo root for every touched CLI). That is
  a 60-second loop and it would have made the lanes' own verification honest;
  it is now the `check-documented-command-flags` gate's job only for documented
  commands, which is why six gates found it and no lane did.

## Next Improvements

- **workflow — `recurs:` verify a migration in the shape production uses
  before the next launch.** Add to every lane brief that touches imports: "run
  `python3 <file> --help` for each touched CLI from the repo root; paste the
  failures". Parent side: run the full read-only lane before launching a
  dependent lane, not after. Structural pattern: verification bound to one
  loader shape misses the other. Triggering instance(s): 39 `scripts.subprocess_guard`
  package imports; `load_script_module` under bare names in `test_batch6.py`.
  (recurrence-class: verification-shape-mismatch)
- **capability — `novel:` make `charness task run` know the sandbox's
  read-only set.** Receipt field plus a launch refusal when the scope names a
  path the lane cannot write (today: `.agents/**`), unless the brief carries a
  `parent-applies:` line. Destination: repo-local guard in `charness task run`
  (`scripts/task_run_execution.py`). Structural pattern: a scope the executor
  cannot honour is accepted silently. Triggering instance(s): ratchet lane,
  #774 lane. (recurrence-class: lane-brief-omits-parent-owned-surfaces)
- **capability — `recurs:` regenerate the plugin mirror inside the lane
  runner.** `run-quality.sh` (or the two mirror tests' fixture) should call
  `sync_root_plugin_manifests.py` before the standing pytest when `plugins/`
  exists, since the mirror is generated and untracked. Destination: issue
  under #769's declarative runner, `recurs:` lineage to the first-session
  "derived-surface-batching" lesson. Structural pattern: a derived surface
  compared byte-for-byte but regenerated by hand. (recurrence-class: derived-surface-batching)
- **workflow — when a failure passes alone, bisect the collection set first.**
  Under xdist every test module imports in every worker, so a module-level
  rebind pollutes regardless of runtime order. The nine-run bisect script is in
  the session record's lesson list; it belongs in
  `skills/public/debug/references/sibling-search.md` beside the runtime
  prefix method. (recurrence-class: collection-time-pollution)
- **memory — an in-process migration must emulate the child interpreter.**
  Empty module table (evict bare names that shadow a sibling file, restore
  after), argv swapped before import, the script's directory first on
  `sys.path`, import-time exits captured. Three production fixes this session
  were this one rule (`inventory_empty_scope_honesty.py`, `gather_public_url.py`,
  `check_staged_worktree_consistency.py`). Written into the session record;
  belongs in `docs/development.md` beside the in-process loader guidance.
- **workflow — use `git -C <worktree>` for every lane-worktree command.** The
  shell cwd persists across tool calls; two cherry-picks landed in the wrong
  repository. Trivial, but it recurred within one session.

## Sibling Search

- same layer: other portable skill scripts that import a root `scripts/`
  module by package name | decision: same waste, fix now | proof: `grep -rn
  "^from scripts" skills` after the fix names only files with the dual-path
  `try/except`, and `python3 <file> --help` over all 65 guard importers reports
  zero `No module named 'scripts'` beyond the nine libraries that failed the
  same way at `a5002ffc9`.
- abstraction up: any generated-but-untracked surface a standing test compares
  (`plugins/`, `native/repograph` fixtures, the runtime-budget profile) |
  decision: valid follow-up outside the slice | proof: the repograph captured-
  reader fixture bit this session at the boundary commit (`a5002ffc9`), same
  shape; follow-up: deferred `2026-09-02-session-record.md#next-session-in-order`
  item 7 (#769 declarative runner owns regeneration).
- specialization down: `check_docs_graph.py` prints `FAIL [docs-graph-awiki]`
  for awiki's advisory exit 1 while the gate passes | decision: diagnostic-only
  | proof: gate exit 0 and `status: pass` in three lanes; the line is the phase
  monitor echoing the child's code, misleading but not a verdict.
- mental-model siblings: any lane brief that scopes a path the executor cannot
  write (`.agents/**` today; `.githooks/**` untested) | decision: valid
  follow-up outside the slice | proof: two of nine lanes hit it, both on
  `.agents`; follow-up: deferred `2026-09-02-session-record.md#next-session-in-order`
  (lane-runner guard, capability bullet above).

## Portable Candidate

- abstract pattern: a delegated executor accepts a scope it cannot honour and
  reports the gap only at the end.
- triggering evidence: two of nine Codex lanes ended uncommitted over
  read-only `.agents/`.
- intended consumer/repo shape: any repo that runs sandboxed agent lanes with
  a declared write set.
- destination: not portable — the read-only set is a property of this repo's
  lane runner and host sandbox; the fix is repo-local (`charness task run`).
- first-prompt acceptance claim: n/a.

## Packet Consumed

n/a (no adapter sections)

## Persisted

Persisted: yes: charness-artifacts/retro/2026-09-02-session-retro.md
