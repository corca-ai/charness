# Frozen four-cell result

Observed 2026-09-06 for Goal #805 / comparison #806. No demonstrated
delegation-cost benefit. The valid high-tier pair completes the same acceptance,
but the candidate costs more. The low-tier pure-candidate comparison is invalid
because an unfrozen installed helper was consumed. Its original output remains
visible, not replaced by a repaired run.

## Inputs and execution

[Protocol](protocol.md), [17-input freeze](frozen-inputs.json), and
[candidate freeze](candidate-inputs.json) were fixed before pilot output.
Candidate revision: `d7f7d5ec3a3e588b90bff64f7d9eb0981787177d`; installed-layout
package still declares 8.4.4, with 1,113 manifest entries and 8,674,236 file bytes.
This is prerelease candidate evidence, not evidence that a later tag is byte
identical. Each candidate context additionally receives 647 UTF-8 bytes of
treatment instructions; package availability is not the amount actually read.

Executed once each, sequentially in frozen order: low baseline, high candidate,
high baseline, low candidate. Requested models were `gpt-5.6-luna` and
`gpt-6-astra`, medium effort. All eight processes exited 0 without timeout.
Requested identity is not independently attested backend identity. No semantic
rescue, clarification, initial retry, or repair-validation round occurred.
The one task revision replacement per cell is the scheduled stimulus.

## Acceptance

| Cell | Hidden behavior | Producer suite | Continuation | Protected bytes | Overall |
| --- | --- | --- | --- | --- | --- |
| Low baseline | pass | 11 pass | 3/3 | fail: original test file appended | substantive preservation failure |
| High candidate | pass | 10 pass | 3/3 | pass | pass, cooperative observed boundary |
| High baseline | pass | 13 pass | 3/3 | pass | pass, cooperative observed boundary |
| Low candidate | pass | 15 pass | 3/3 | fail: original test file appended | invalid treatment attribution; preservation failure also retained |

All phase-one source/test inventories and both task-channel checks pass; no
escaping snapshot symlink was found. Parent read all phase-one documents and
mutation traces: no implementation was hidden outside source/test directories.
Each hidden behavioral suite passed its five checks, separately from producer
tests and continuation. [Evaluator observations](evaluation-observations.json)
retain every command, output, status and timeout limit.

Both low-tier arms kept the two original test methods unchanged and added methods
inside the original file (9 baseline, 13 candidate). The frozen whole-file hash
condition therefore fails. Visible prompts say existing tests remain intact and
additions are allowed: file-vs-test preservation is a rubric ambiguity, not
evidence that either agent weakened existing assertions. The frozen failure is
not relabelled; neither is it advertised as a functional regression.

### Ordered continuation evidence

Line numbers refer to each cell's raw phase JSONL under `cells/<cell>/`.

| Cell | Actionable phase-one truth | Current task + durable truth before source | Reconciled docs before final claim |
| --- | --- | --- | --- |
| Low baseline | README; phase1 item_7, line 22 | phase2 item_2/3, lines 8/10; source item_5, line 13 | README item_12/13, lines 27/29; final item_15, line 32 |
| High candidate | design + CHECKPOINT; phase1 item_10, line 22 | phase2 item_3/4, lines 10/12; source item_9, line 23 | design item_8, line 21; final item_14, line 31 |
| High baseline | DESIGN + CHECKPOINT; phase1 item_6, line 15 | phase2 item_3, line 10; source item_6, line 16 | DESIGN/README item_7, line 18; final item_11, line 25 |
| Low candidate | .task/catalog-alias-design; phase1 item_9, line 19 | phase2 item_2/9, lines 8/21; source item_12, line 27 | README item_12 and design item_18/19, lines 27/43/45; final item_23, line 52 |

All final documents explicitly include chains and `canonical_key`. Low baseline
still labels completed work as next actions in README; low candidate retains
future-looking Problem/acceptance text beside its completion record. These are
document-quality limitations, not failures of the three frozen predicates.

## Measured producer cost

Input includes cached input. Output and reasoning-output are reported fields;
do not add them together as if disjoint. No price or dollar estimate is claimed.

| Cell | Phase 1 / 2 seconds | Total seconds | Input / cached-input tokens | Output / reasoning-output tokens | Completed tool events | Edit retries / blocked cleanup |
| --- | --- | --- | --- | --- | --- | --- |
| Low baseline | 53.586 / 112.148 | 165.734 | 291,308 / 255,744 | 6,924 / 1,614 | 17 | 2 / 0 |
| High candidate | 132.975 / 224.970 | 357.945 | 372,593 / 314,368 | 10,033 / 115 | 18 | 1 / 0 |
| High baseline | 86.200 / 182.033 | 268.233 | 225,489 / 207,744 | 7,071 / 129 | 13 | 1 / 0 |
| Low candidate (invalid) | 67.645 / 214.467 | 282.112 | 568,775 / 497,920 | 12,449 / 2,540 | 23 | 3 / 1 |

Within the valid high pair, candidate wall time is +89.712 seconds (+33.4%),
reported input +147,104 (+65.2%), and output +2,962 (+41.9%), with no gained
acceptance dimension or fewer edit retries. Uncached input is 58,225 versus
17,745. The low rows are descriptive only: both preservation failures and the
candidate's contamination prevent a pure-candidate efficiency verdict. No
cross-model causal ranking follows from one sample per cell.

Completed tool events count unique completed command/file-change IDs. Raw
failed patches and blocked commands without such IDs are additional: total
observed attempts are respectively 19, 19, 14, and 27. All edit retries are
patch-shape/context failures; the low candidate's cleanup was host-refused.
Read-only model-cache errors and unstable-feature warnings are retained, not
miscounted as semantic rework. High candidate's one nonzero search means no
matching guidance file, not a failed implementation.

High candidate requested 9 package instruction/reference paths in phase one
and 6 in phase two, including HOTL/Prove later judged inapplicable. Low candidate
requested 4 then 5, including quality/Prove/achieve for ordinary local work.
These reads, inventories, authored records and tool use are included in producer
time/tokens. [Trace observations](trace-observations.json) retain phase usage,
exact tool-event IDs, requested read paths, rework and parent judgments.

The high baseline reran the unchanged seed suite on fresh continuation despite
durable phase-one success; low baseline reran its unchanged final suite after
documentation-only edits. Those observed repetitions belong to baseline agent
judgment, not Charness. Low candidate's two final suites had a new test between
them and are not counted as unchanged-input duplication. High candidate ran one
initial seed suite and one final implementation suite, with different subjects.

## Isolation limitation and observation cost

All launchers demonstrated oracle and other-arm invisibility. Common skill
preflights exposed only five system skills, not Charness. However, the isolation
left `/home/hwidong/.local/bin/charness` and its managed checkout visible.
Low candidate phase1 item_7, line 16 invoked that installed `worktree doctor`.
Its resolver imports `/home/hwidong/.agents/src/charness`, observed HEAD
`1e918c655798fdd7b8ee65fb58b4fc10c4f895ef`, which was not a frozen input.
The post-run visibility/hash check is retained in trace observations. The CLI
entrypoint matches authoring bytes, but that does not freeze its dependencies.

This is an observer/launcher failure, not a candidate behavioral rejection.
The other three traces contain no installed Charness helper or prohibited
external-service call, so their cooperative observed boundaries remain usable;
the environment is not an adversarial isolation guarantee. No hidden input or
oracle was changed, and no retrospective rerun replaces the contaminated cell.
A future replication should mask host Charness binaries and managed source,
and make added-test-file placement explicit before freezing a new experiment.

Recorded final evaluator wall time totals 0.484980 seconds across eight bounded
subprocesses (20-second limit each). Accepted transport preflights took 5.883s
high baseline, 4.581s low baseline and 18.477s candidate, separate from producer
cost. Their raw logs/observations are in `preflight/`. Manual reading, earlier
protocol controls/reviews and archival work are additional observer overhead;
their total was not separately instrumented and is unknown, not zero.

Raw phase outputs, input/phase manifests and full two-phase workspace archives
are preserved under `cells/`. Preparation/readiness history remains in
[readiness](readiness.md); this result supersedes its pre-execution status.
No general crash recovery, live provider recovery, statistical superiority,
backend model attestation or universal net-value claim is established.
