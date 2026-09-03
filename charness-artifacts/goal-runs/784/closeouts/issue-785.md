task run: lane completion runs the changed-line gate and the receipt carries its verdict (#785)

Closes #785

A `charness task run` lane can no longer report done past a line the pre-push
hook would refuse. At completion, for a validated candidate, the runner
regenerates the lane tree's plugin mirror and runs that tree's
release_changed_line_coverage.py over the lane's own base with
--refuse-unestablished; the receipt's new `changed_line_gate` field carries the
gate's status, exit code, the consumer's blocking_detail and blocking_targets
verbatim, a one-line summary, the runtime, and the log paths. Any exit the hook
refuses on demotes the result to validated-partial-result, marks it ineligible,
and names the unproven line in next_step. A tree without the gate script records
not-applicable; a lane with no validated candidate records skipped; neither is
clean.

Classification: feature
Jtbd: the parent reads at the lane receipt what it used to learn at the fourth refused push: which changed line nobody proved.
Boundary: scripts/task_run/task_run_changed_line.py (new), scripts/task_run/task_run_completion.py, scripts/task_run/task_run.py, tests/charness_cli/test_task_run_changed_line.py (new), tests/charness_cli/test_task_run_completion.py, docs/agent-task-runs.md (the receipt field), docs/parallel-execution.md "Disjoint Writers" (the definition-of-done sentence with the measured runtime), .agents/claude-host.md (the same for in-process subagent briefs), and the #784 session record. What the gate proves and the pre-push hook are unchanged; no gate over brief text.
Resolution Brief: charness-artifacts/goals/2026-09-03-lesson-review-and-775-followups.md slice 1 and the #785 Work Item body.
Implementation: implemented in the parent session and probed with a real lane against this repo (fake Codex committing an uncovered two-branch function into a pool file). The first probe refused on the wrong ground, `focused producer failed`, because a lane worktree has no generated plugins/ mirror and the instrumented standing runner refuses a missing one; the runner now regenerates the mirror in the lane tree first (0.4 s). The second probe returned validated-partial-result with blocking_detail naming lines 239-241, gate 23.6 s; the hand-run gate on the same worktree returned the same detail. A hand run against the pre-amend base exposed the untested mirror-sync path in the new module itself, covered before the slice diff passed the gate.
Prevention: tests/charness_cli/test_task_run_changed_line.py drives the gate runner through every exit shape (clean, blocked, unestablished, partial, unreadable, malformed, timed out, mirror failure, tree without the exporter, tree without the gate) and runs three real lanes through the runner with a seeded gate script in the lane tree: a refusing tree ends validated-partial-result with the detail persisted, a passing tree completes as before, a tree without the script records not-applicable. test_task_run_completion.py proves the demotion, the skip, and the not-run branches.
Behavior: verified — standing runner 8773 passed in 69 s, ./scripts/run-quality.sh --full --read-only green, ./scripts/check-docs.sh PASS, the changed-line gate on this slice's own diff `status: clean` against 553f79c7, and the seeded probe lane refused with the line named.
Review disposition: critique not required; reversible runner change proven by seeded refusals and a live probe lane against the real repository.
AI-provenance: implemented, probed, and verified by an AI agent (Claude Code) in the Goal Run #784 session.
Goal lineage: Goal Run corca-ai/charness#784; draft sha256 878f74409e4c271d07a87c4bb34108376d10878cfdc476249311ec3671a8a151; binding sha256 9e4650f0f731add79de7a0b68cc3b918ed087e71d7e28f43cb74c0973ddafd82; Work Item lane-changed-line-done (#785).
