# Claude executor pilot evidence

2026-10-25; local commits only. No push or landing was performed.

The opt-in Claude executor uses `claude -p --model claude-haiku-5-5`, the lane
worktree, stream JSON, session-resume steering, mandatory whole-process bwrap,
authentication in a parent-side proxy, and private Git bundle import. Orchestration
preserves `muse,codex` as its default and accepts `LANE_EXECUTOR=claude`.

## Final real lane

- Task: `task/claude-haiku-isolated-20261025`. Result: **completed**, result kind `success`.
- Result JSON: `/tmp/charness/runtime/dfde85cabc08db6d/task-run/claude-haiku-isolated-20261025/result.json`.
- Task commit: `15b63f0da123236e3f94d5e8c328ec3b93eb2713`; base: `967b9a3b567e3b091e0f278a337a5740d141da2b`.
- Author: Hwidong Bae <bae.hwidong@gmail.com>. Task commit is not an ancestor of main.
- Exact committed byte comparison confirms only the seeded `boundded` → `bounded`
  replacement in `docs/agent-task-runs.md`; clean commit-only candidate.
- Full report exists; VERIFY line present. Native Bash: 7 calls, 0 tool failures.
  Both pre-commit and commit-msg hook output were observed; no hook bypass was used.
- The native outside-write probe was refused; its host sentinel stayed unchanged.
- Changed-line proof is `noop` because this is documentation only. Normal retention
  released the clean worktree and its private runtime after preserving the branch,
  result JSON and logs. Execution phase: 103,380 ms; not a throughput benchmark.
- The final preflight reviewer session was observed under private runtime before
  retention, with no matching session file in real `~/.codex`. Runtime retention
  removed that private home, including the auth-only copy. Raw messages and
  credentials are not reproduced here.

## Tests and safety

- Charness standing runner: **135 passed** (`/tmp/claude-review-isolation-rerun.log`).
- Charness core quality: **6 passed**, 4 opt-in checks not run
  (`/tmp/claude-core-quality-final.log`). Docs length, staged hook gates and the
  canonical debug validator passed. This is not a full release-lane claim. An earlier run hit the existing
  Muse live-poll timing assertion while its durable receipt was correct; the
  unchanged rerun passed. That test remains timing-sensitive in
  `tests/charness_cli/test_task_run_muse_stream_886.py`.
- Orchestration: `bin/check-script.sh bin/tool_policy.py bin/flow-times.py
  bin/tally.py bin/test_claude_executor.py` passed all **33 test modules**, plus
  real-state consumer smoke (`/tmp/claude-orch-check-final.log`).
- Real OS refusal, private-Git hooks/import, ancestor-rename protection, credential
  masks, auth substitution, resume construction, stream capture and reviewer-home
  masking have focused boundary tests. Native A/B probes disconfirmed two guessed
  permission fixes before the measured configuration repairs were accepted.

Exact standalone safety proof (`/tmp/charness-claude-safety-final/safety-proof.txt`):

```text
inside-write=allowed outside-write=refused outside-unchanged=true
policy-ancestor-rename=refused
credential-read=masked-or-refused credential-original-unchanged=true
```

The real final receipt also completed the orchestration review-writer → shared
comparison-reader roundtrip under a private proof-state root: four experimental
attempts, one explicitly reviewed final lane, first-pass GREEN 1/1, P1 0. Unreviewed
failed experiments remain visible and outside that denominator. This is not a
production quality-rate claim; production state was not populated with the demo.

## Earlier probes and remaining cleanup

Earlier experiments are retained, unlanded. One was blocked by an old-base
preflight; another exposed the native subprocess-scrub/socat side effect; another
exposed an overbroad native read guard. The final lane above includes both repairs.
The [debug record](../debug/2026-10-25-claude-native-empty-protected-files.md) and
[acceptance contract](../spec/2026-10-25-claude-native-sandbox-composition.md) preserve
cause, discriminator, critique, prevention and the live acceptance boundary.

Three early legacy Codex preflight sessions were created in real `~/.codex/sessions`
before reviewer isolation was fixed. Exact new job-owned files, absent from the
pre-probe snapshot, are listed privately in
`/tmp/claude-haiku-pilot-evidence/owned-review-session-cleanup.private.json`.
The required `workspace-trash` refused that protected location; no files were
moved and no shared index/database was edited. A request to move only those three
files into task cache and trash them is pending. This record does not claim the
entire concurrently active home tree stayed unchanged: one real `.claude.json`
metadata change was also observed and is not attributed to this lane.

## Files per repository

Charness (plus this evidence record):

- `.agents/temp-producers.yaml`
- `charness-artifacts/debug/2026-10-25-claude-native-empty-protected-files.md`
- `charness-artifacts/debug/latest.md`
- `charness-artifacts/debug/seam-risk-index.json`
- `charness-artifacts/metrics/rca-ledger.jsonl`
- `charness-artifacts/spec/2026-10-25-claude-native-sandbox-composition.md`
- `docs/agent-task-runs.md`
- `docs/claude-task-executor.md`
- `scripts/cli/cmd_task.py`
- `scripts/task_run/task_run_attempts.py`
- `scripts/task_run/task_run_brief_critique.py`
- `scripts/task_run/task_run_claude_auth.py`
- `scripts/task_run/task_run_claude_events.py`
- `scripts/task_run/task_run_claude_review.py`
- `scripts/task_run/task_run_claude_sandbox.py`
- `scripts/task_run/task_run_contract.py`
- `scripts/task_run/task_run_event_timing.py`
- `scripts/task_run/task_run_execution.py`
- `scripts/task_run/task_run_lane_options.py`
- `scripts/task_run/task_run_lane_runner.py`
- `scripts/task_run/task_run_progress_rule.py`
- `scripts/task_run/task_run_runtime.py`
- `scripts/task_run/task_run_steering.py`
- `scripts/task_run/task_run_support.py`
- `tests/charness_cli/test_task_run_claude_events.py`
- `tests/charness_cli/test_task_run_claude_review.py`
- `tests/charness_cli/test_task_run_claude_sandbox.py`
- `tests/charness_cli/test_task_run_executor_probe.py`
- `charness-artifacts/impl/2026-10-25-claude-executor-pilot.md`

Orchestration (`5864235`):

- `bin/flow-times.py`
- `bin/tally.py`
- `bin/test_claude_executor.py`
- `bin/tool_policy.py`
- `design/claude-executor.md`

## Local implementation commits

```text
06fa32efc feat(task-run): confine opt-in Claude Haiku lanes and preserve executor evidence
e05920911 fix(task-run): preserve the trusted repository identity in Claude Git storage
706ce166b fix(task-run): keep native Claude tools inside the existing outer sandbox
cd57f9b84 fix(task-run): keep Claude tooling and preflight inside private runtime boundaries
5864235 feat(lanes): allow opt-in Claude pilot and compare canonical executor receipts
```
