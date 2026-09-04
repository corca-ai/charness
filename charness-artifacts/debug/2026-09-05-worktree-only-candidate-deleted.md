# Debug Review: worktree-only candidate deleted
Date: 2026-09-05

## Problem

A `charness task run` lane marked `validated` / `useful: true` / `carrier_kind: worktree-only` with `keep_worktree: true` can have its worktree deleted, leaving `result.json` pointing at a path that does not exist and a branch whose `target_sha` equals `base_sha`.

## Correct Behavior

Given a terminal useful candidate whose HEAD does not carry the dirty tree, when completion or a later sweep runs, then a durable copy (lane-branch commit, or salvage named on the receipt) still exists, and `keep_worktree` / `next_step` / `worktree_path` do not claim a directory the same run removed.

## Observed Facts

- Issue #797 `result.json` (goal793-basis-host-scripts): `status=validated-partial-result`, `keep_worktree=true`, `carrier_kind=worktree-only`, `committed_paths=[]`, `target_sha==base_sha`, `worktree_path` gone, `next_step` still names the worktree. Claim type: absence of surviving copy. Cheapest falsifier: local sweep fixture (below). Result: receipt-named copy absent; salvage files can exist beside `result.json` but are unreferenced.
- `release_finished_lane` (`scripts/task_run/task_run_completion.py:200-210`) returns None unless `status=="completed"` and `commit-only`/`head_is_complete`; worktree-only is retained at completion. Default `keep_worktree` is True (`task_run.py:313`).
- `Sweep.sweep_lane` (`scripts/gates_support/runtime_root_retention.py:215-240`) deletes every terminal lane worktree after salvage, ignoring `keep_worktree` and `carrier_kind`. Standing pytest runs this before the suite (`run_standing_pytest.py:451`).
- Reproduction 2026-09-05: terminal useful worktree-only fixture → worktree gone, `keep_worktree` still True, `next_step` unchanged, `uncommitted.patch` + `uncommitted-untracked.tar` written. Existing test `test_the_sweep_removes_what_the_rule_names` encodes that deletion (`tests/test_runtime_root_retention.py:195-204`).
- Timeout path already commits dirty trees (`_commit_wip_candidate`); the successful useful path does not.
- Secondary: operator `git diff` omits untracked; salvage tar does not. Third: killed `status=running` is a sibling (read-time `liveness.alive` exists; `result.json` is not rewritten).

## Reproduction

- Fixture: terminal `validated-partial-result`, `keep_worktree=true`, dirty tracked + two untracked files; `sweep_runtime_root`. Worktree removed; receipt unchanged; salvage present but unnamed.

## Candidate Causes

- Completion deletes worktree-only (disconfirmed: `release_finished_lane` retains it).
- Sweep deletes every terminal worktree and does not update the receipt (confirmed).
- Salvage never runs (disconfirmed in the fixture; unproven for the live goal793 tree, which is gone).

## Hypothesis

- If sweep honors `keep_worktree` for a useful incomplete carrier, the worktree survives a later pytest. If completion commits that dirty tree onto the lane branch first, `target_sha` carries the candidate even after a later release. | disconfirmer: fixture with `keep_worktree=true` must keep the worktree today (it does not); timeout already commits, the useful path does not.

## Verification

- confirmed — fixture above; code at `runtime_root_retention.py:221-238` and `task_run_completion.py:199-210`.

## Root Cause

#787 split retention: completion keeps a worktree-only candidate, the sweep later treats every terminal `phase` as reclaimable after salvage. Salvage is not written onto `result.json`, so the producer signal `keep_worktree=true` never reaches the deleting consumer. The useful path has no analogue of `_commit_wip_candidate`, so the lane branch stays at `base_sha`.

Whys: worktree gone → sweep removes terminal lanes (`runtime_root_retention.py:221`) → #787 reclaim rule ignores `keep_worktree` → completion and sweep do not share an invariant that a useful incomplete carrier must outlive the directory.

## Invariant Proof

- Invariant: when completion emits `keep_worktree=true` (or `useful` and not `head_is_complete`), the operator-facing consumer (`task status` / parent integration) must still find the candidate bytes — worktree, named salvage, or lane commit — and must not be told to inspect a removed path.
- Producer Proof: `test_a_worktree_only_candidate_keeps_its_lane_worktree` and `release_finished_lane` retain at completion.
- Final-Consumer Proof: sweep fixture deletes the worktree and leaves the receipt lying; parent `next_step` names `resolved_target`.
- Interface-Shape Sibling Scan: timeout WIP commit (`task_run_git.py:137`); salvage files unreferenced on the receipt; `task status` liveness vs persisted `running`.
- Non-Claims: live goal793 salvage directory not inspected (runtime key gone). Hosts other than this repo's standing pytest hook not proven.

## Detection Gap

- `tests/charness_cli/test_task_run.py:424` asserts the worktree exists at process exit; it never runs the sweep. Smallest change: after that lane, call `sweep_runtime_root` and assert a durable carrier plus an honest receipt.
- `tests/test_runtime_root_retention.py:195` asserts the opposite of #797 (dirty terminal lane is removed). Smallest change: a `keep_worktree=true` useful fixture that must not drop the only named copy.
- Over-reach: not "no test in this corner"; the sweep test samples this shape and locks the defect in.

## Sibling Search

- Mental model: a later GC may ignore a keep/retain flag if salvage exists somewhere the receipt does not name.
- same layer: `sweep_lane` vs `release_finished_lane` — two deleters, one honors carrier_kind. decision: same bug, fix now | proof: local payload proof
- specialization down: `git diff HEAD` salvage omits untracked; tar path exists. decision: same class, diagnostic-only for this slice | proof: executable fixture (tar members in reproduction)
- mental-model: killed `running` + dead pid. decision: valid follow-up outside the slice | proof: static scan only | follow-up: deferred #797 third clause (result.json stays `running`; `task status` already adds `liveness.alive`)
- cross-file: `scripts/task_run/task_run_completion.py` (producer retain) vs `scripts/gates_support/runtime_root_retention.py` (consumer delete)

## Seam Risk

- Interrupt ID: none
- Risk Class: none
- Seam: standing-pytest → sweep → task-run records
- Disproving Observation: in-process fixture reproduces without a host
- What Local Reasoning Cannot Prove: whether the live goal793 dir lacked salvage files
- Generalization Pressure: monitor

## Interrupt Decision

- Resolution: resolved
- Critique Required: yes
- Next Step: impl
- Handoff Artifact: charness-artifacts/debug/2026-09-05-worktree-only-candidate-deleted.md

## Prevention

Honor `keep_worktree` in `sweep_lane` for a useful incomplete carrier. Persist a useful dirty candidate onto the lane branch at completion (timeout already does). Point `next_step` at that commit when the worktree is released. Extend the worktree-only task-run test across a sweep.
