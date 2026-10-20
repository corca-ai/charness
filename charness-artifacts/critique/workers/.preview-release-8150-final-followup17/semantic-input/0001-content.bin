# Lane progress rule: replace the wall-clock lane timeout

Status: current (2026-10-20). Revised after a two-reviewer design premortem; dispositions at the end.

## Source (verbatim)

Operator, 2026-10-20 18:5x KST: "한쪽은 시간이 짧아서 문제, 다른 쪽은 길어서 문제네. 이 시간 제한 자체를 없애고, 대신 시간 제한으로 이루려고 했던 걸 더 효율적/효과적으로 할 더 좋은 방법이 없나?"

Operator, 2026-10-20 19:0x KST, on a proposed separate generous backstop timer: "'넉넉한 안전판'을 따로 둘 필요가 있나? 어차피 계속 볼텐데? 레스 벗 베터로 할 수는 없나?" The primary's restatement: drop the separate backstop; keep a single no-progress rule. "No progress" means no new commit, no file change and no new command outcome since the last check. Its terminal action is charness itself stopping the lane after a checkpoint request goes unanswered. A dead or silent executor is the extreme case of the same rule, so there is no second timer. The stop must not depend on a human or the primary watching. Delete the wall-clock default.

Evidence from the consuming repo (ceal, 2026-10-20, reported by its primary, not re-verified here): lanes run with `--timeout-seconds 5400`; 24 of about 133 lanes timed out; one sweep timed out four times in a row, the last while fixing pre-commit findings just before its commit. Each timeout leaves a `task-run: WIP candidate — interrupted mid-edit — state unknown` commit that cannot be merged and must be continued. One lane ran its focused tests 39 times, another 56 times.

## What the timeout was for

(a) stop a lane that loops without progress; (b) free capacity; (c) give the orchestrator a judgment point. A wall clock does all three badly: it kills productive lanes mid-edit and lets a looping lane burn its whole budget.

## Current owners reused (baseline before this change)

- Before this change, `charness task run --timeout-seconds` (default 3600) was the only wall clock; `run_monitored_phase` kills the executor at it and the carrier commits a WIP candidate.
- `LaneProgressWatch` (`scripts/task_run/task_run_progress.py`) already polls lane logs and the worktree every 15 s beside a require-change lane, owns the kill of the executor's process group, records `NO-PROGRESS-STOP:` and `progress_stopped`, and enforces two narrower guards: the first-edit budget (CONTRACT-READ to first EDITING or scoped diff, `--no-progress-seconds`, default 300 s) and the BLOCKED linger grace (60 s).
- The steer queue (`charness task steer <id> --message`, `steer.queue.jsonl`) delivers typed messages only at an executor turn boundary: the carrier resumes the same session (`codex exec resume <thread>` / Muse `--session-id`) with the messages appended. A Codex lane is usually one long turn, so today a message reaches it only after it finishes.
- v8.15.0 stamps every executor event line as it arrives (`StampingPipe`), and `task_run_event_timing` already parses Codex `command_execution` and Muse `tool.bash` start/completion into commands and families (test, lint, typecheck).

## What is missing, and the one new mechanism

Mid-turn delivery. The carrier gains **preemption**: to deliver its own message now, it kills the executor's process group and resumes the same session with the message, through the existing steer delivery path (`codex exec resume <thread>`, Muse `--session-id`), falling back to the existing relaunch-in-place (fresh session, same worktree, prompt plus messages) when no session id is known or the resume fails. Probe on this machine (codex-cli 0.163.0): a `codex exec --json` session SIGKILLed during a running `sleep 40` resumed with `codex exec resume <thread>`, kept its context (it quoted the first instruction), and logged only a missing tool-call output. Muse resume after a kill is not probed; its fallback is relaunch-in-place.

Preemption is not free, so the rule limits where it happens:

- At a command completion (loop messages), no command is in flight, so only the model's in-progress reasoning is lost.
- At a window check, the carrier never kills a command younger than one window (one that started after the previous check). Such a command defers the request, or the stop, until it completes or the next check, whichever is first; only then is a command that has run for at least `W` killed, and the message names it as interrupted with possibly partial effects.
- One preemption per invocation: a second message raised before the executor dies is queued and rides the same resume. Once a stop has won (in the watch or already in the rule), a later message is suppressed and counted (`suppressed_actions`), never queued; a message queued earlier in the same invocation is nacked `superseded-by-stop` and its preemption uncounted.
- Each invocation has its own command state: a resumed Codex session reuses item ids (`item_1` again), so in-flight commands are keyed per invocation and a restarted command is young again.

Preemption leaves the worktree as it is, including any partial effect of a killed command; the carrier does not checkpoint, commit, or clean it. A preempted invocation has its own result: it is not a failure, not a retry attempt (attempts live outside the invocation loop), not a relaunch in the friction log, not a failed resume, and not a WIP candidate. `execution.preemptions` counts them; relaunch friction counts only real relaunches. If the executor exits on its own just before the kill, the queued message is delivered at that turn boundary exactly like an operator steer.

## The rule

One knob: the progress window `W` (env `CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS`, default 1200 s; `0` turns the rule off; a negative value falls back to the default). It applies to every lane run through `charness task run`, not only require-change lanes.

Progress since the last check is any of:

1. a new commit or file change: the worktree fingerprint (`HEAD`, the tracked diff, untracked files by size and mtime; ignored files do not count) differs from the last check;
2. a new outcome in the executor's own events: a completed file-change item (Codex `file_change`; Muse `tool.edit`, `tool.edit_file`, or `tool.write_file`; reads, searches, and todo lists are not outcomes), or a completed command whose pair (command text, worktree fingerprint at completion) has not completed before in this lane. Rerunning the same command on an unchanged tree is not a new outcome.

Signals are three-valued. An unobservable worktree contributes nothing, neither progress nor its absence: the executor's events are always observed, so a silent executor is still reclaimed, and an editing executor still shows file-change items. With the tree unreadable, a command completion is keyed to one "unobservable" state: a new command is still new, a rerun is not, and no loop message is sent. The watch runs the rule even when its other polls fail; if the rule itself fails 8 consecutive times (no completed check in between; quiet polls do not reset the count), the watch stops the lane with that reason rather than leave it unbounded.

Every `W` the watch checks:

- progress: nothing happens. An outstanding request is recorded as answered.
- no progress, no request outstanding: charness sends a **checkpoint request** ("No commit, file change, or new command result in the last W. If your work has a coherent state, commit it (hooks must pass; never --no-verify) and write your final report naming what remains; if you are blocked, reply BLOCKED: <reason>. If you are still progressing, continue; charness stops this lane if the next W also shows none."), by preemption when no command is in flight, deferred as above otherwise.
- no progress, request delivered and unanswered: charness **stops** the lane (`NO-PROGRESS-STOP:`, `progress_stopped`) through the existing guard kill. A request still deferred at this check is delivered now (preempting the long command) instead, and the stop waits one more window.

A request is answered by any progress before the next check (`answered_by: progress`), or by the executor ending cleanly with exit 0 (`answered_by: lane-ended`; a timeout, interruption, or failure records `answered: false, answered_by: lane-failed`) (a final report or a `BLOCKED:` line ends the executor's turn; the existing BLOCKED grace covers a lane that lingers after one). A silent model or dead executor is reclaimed within `2W` plus one poll; a hung command within `3W` (one window of youth, one for the request, one for the stop). Each check also spends up to 180 s on its worktree probes (three git commands, each limited to 60 s), so in the worst case a silent lane is reclaimed within `2W` plus one poll plus 360 s, and a hung command within `3W` plus 540 s. No human or orchestrator needs to watch. Set `W` above the longest single command a lane legitimately runs.

### Loops

Evaluated at each command completion, for commands in the test, lint, or typecheck families, keyed by (exact command text, worktree fingerprint at completion):

- 3rd completion of the same key (no file change between runs): preempt with "switch to the debug skill: read the failure, state one falsifiable hypothesis, change code, test, or approach before rerunning".
- 4th: preempt with the checkpoint request ("commit the coherent part, write your final report naming what is unresolved, and stop; a further identical run stops this lane").
- 5th: stop (the request went unanswered).

Exact text is deliberate: it catches the reported case (the same focused command rerun dozens of times) with no false alarm across distinct commands. A loop that varies the command text each time evades this check; it still produces outcomes, so the window does not stop it either. That gap is a recorded non-claim.

## Wall-clock default

`--timeout-seconds` loses its default (none: the executor runs until it ends, preempted or stopped only by the rule). The flag stays as an explicit hard cap for callers that want one; it is no longer recommended for lanes, and its stop still produces the WIP candidate. `task run --detach` stops forwarding a default. Internal reviewer and self-review carriers keep their own explicit bounds.

## Receipt and live view

`progress_guard.progress_rule` records the window, its source, every check (progress or not), each checkpoint or loop message, whether each request was answered, and the stop reason; `execution.preemptions` counts carrier preemptions. The `live` snapshot shows the window state (seconds since last progress, request outstanding) so `task status` readers see it without tailing logs.

## Launcher contract

A launcher stops passing `--timeout-seconds`. It may set `CHARNESS_TASK_RUN_PROGRESS_WINDOW_SECONDS` (per invocation or globally); otherwise the default applies. A launcher that keeps passing `--timeout-seconds 5400` keeps a 90-minute hard cap until it drops the flag. Nothing needs to watch the lane for the stop to happen.

## Non-goals and deferred

- The first-edit budget and BLOCKED grace stay as they are (they bound analysis-before-edit and a declared block, not progress).
- No periodic checkpoint request for a lane that is progressing; it continues until it ends.
- Relabeling the WIP commit a progress stop leaves (the tree has been static for at least W, so "interrupted mid-edit" overstates it) is deferred.
- Muse resume after a SIGKILL is not probed on this machine; Muse falls back to relaunch-in-place if its resume fails.

## Design critique disposition (2026-10-20)

Two file-backed read-only reviewers (`design-premortem-a`, operational; `design-premortem-b`, interface and minimality) both returned `block` on the first draft.

- Act before implementing: preemption could kill a productive long command (A LP-2, B 1) — now deferred while a command is in flight and only after `W`, with partial effects named. Preemption was not distinguished from a failed resume, attempts, or relaunch friction (A LP-3, B 3) — now its own result and counter. An unobservable worktree either blocked reclamation or risked false stops (A LP-4) — now three-valued, with file-change events as an always-observed signal. The request had no defined answer (B 2) — now defined.
- Valid but defer: loop keys by exact command text can be evaded by varying the text (A LP-1) — recorded as a non-claim; normalization risks false alarms across distinct commands.
- Over-worry: keeping `--timeout-seconds` as an explicit opt-in; keeping the first-edit budget and BLOCKED grace (both reviewers dismissed these).
- Outside this repository: the consuming launcher's `--timeout-seconds 5400` must be removed there.

## Implementation review disposition (2026-10-20)

A follow-up reviewer (`impl-followup-a`) over the first wiring returned `block`: a stop could kill a command started just after the request (LP-2), reruns on an unreadable tree counted as progress (LP-4a), a failing watch poll could leave a lane unbounded (LP-4b), preemption and stop were not serialized (LP-3), and a lane ending did not answer its request (B-2). All five are repaired as described above, each with a test.

A second follow-up (`impl-followup-b`) confirmed LP-2, LP-4a and the poll half of LP-4b resolved, and blocked on three narrower points, now repaired with tests: the failure counter was reset by quiet polls between failing due checks; a message could still be queued after the rule (not yet the watch) had decided to stop, or queued and then superseded by a stop without a disposition; and a timeout or failure counted as answering the request. A live probe on this machine (real codex-cli 0.163.0 lane, 20-second window) also showed a resumed session reusing `item_1`, which hid a restarted command from the young-command rule; commands are now keyed per invocation.

## Live probes (2026-10-20, this machine, codex-cli 0.163.0)

- Loop: a report-only lane told to run a failing `pytest` five times was preempted after the third run with the debug request and after the fourth with the checkpoint request; both resumes kept the same thread, the lane quoted both messages and ended with its report (`preemptions: 2`, exit 0, 35 s).
- Window: a lane told to wait on `sleep 300` with a 20 s window had the request deferred while the sleep was young, delivered (killing it) one window later, and was stopped after the request went unanswered.
