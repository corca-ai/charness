# Session Retro

Date: 2026-08-21
Goal: charness-artifacts/goals/2026-08-20-repairs-that-carry-their-class.md

## Context

This retro closes the work unit that repaired the release fresh-checkout timeout,
changed-line consumer coverage, duplicated child-process setup, and the parallel
coverage-runtime collision exposed by the broad quality gate. It also closes the
lesson session that the gate correctly surfaced as unclaimed on the next day.
The next boundary is semantic-candidate critique; version mutation and public
release remain unclaimed.

## Evidence Summary

- `345ec2a7b`, `e00898cf9`, `69c1a3ec7`, `2ff21b39e`, `b44d6df16`,
  `e29735316`, `d6381e3d5`, and `933ac9f32` are the source, test, mirror, disposition, and
  evidence commits in this window.
- The fresh-checkout default proof passed all five probes with return code 0;
  the RCA artifact is resolved and the RCA ledger records its converted class.
- The immutable changed-line rerun at `d6bef6a948fe740991a251c67758ed077da08510`
  passed 10,766 tests, analyzed 20/20 changed pool files, and had `blocking: []`.
- The first broad quality run found 94 passes and two failures. Its changed-line
  red was reproduced as a race: broad and focused coverage producers shared the
  same hidden database/config/sitecustomize paths. After `d6381e3d5`, focused
  namespace tests, mirror smoke, py_compile, ruff, and retention tests passed;
  after `933ac9f32` fixed canonical test-to-source binding, the focused proof
  passed and is recorded at `/tmp/charness-s5-prepush-changed-line-current.log`.
- The other broad failure was `unclaimed-emission` for session
  `2026-08-20-01a01e8e-3ede-7053-8d51-0f9afd502234`; existing issue #639 owns
  the recurring session-start/disposition boundary.

## Waste

- recurrence-class: parallel-coverage-runtime-collision — broad quality
  parallelized two producers with overlapping hidden writer paths. The symptom
  was a nondeterministic changed-line verdict; the structural repair namespaces
  runtime files by report stem and tests disjointness.
- recurrence-class: unclaimed-session-disposition — the session declaration
  was emitted and receipted, but no same-session retro disposition was written
  before the next-day broad gate. The gate caught the state, but only after the
  originating session had ended; this recurs against the open #639 boundary.
- A short SHA was supplied once to the real-host checker and an obsolete option
  once to spec-evidence validation. Both were corrected by reading the command
  surface, but they show that copyable proof commands should bind their input
  grammar near the caller.

## Critical Decisions

- Treat the broad changed-line red as a shared-writer race, not as missing tests:
  the same source/test tree passed when the consumer ran alone, while the broad
  and focused coverage producers wrote `.mutation-*` siblings concurrently.
- Namespace the coverage runtime files by report stem and extend retention
  ownership, preserving parallel execution with disjoint write surfaces.
- Close the lesson receipt with sparse, anchored scores only for observed
  changed actions; do not backfill scores for lessons whose presentation or
  encounter is not evidenced.
- Keep #639 open as the owner of the recurring session lifecycle boundary; this
  retro is a reproduction and disposition, not an issue-close claim.

## North Star Alignment

The design north star requires a capable judge and a different observer at
irreversible boundaries. The changed-line failure initially escaped because the
parallel runner treated shared coverage state as if it were independent; the
quality gate became the different observer that exposed the mismatch. The repair
now makes the write ownership explicit and preserves the gate's teeth. The
lesson-continuity failure likewise remained blocking rather than being converted
to a green “in progress” state. No public release or external readback is
claimed, because local evidence cannot observe those boundaries.

## Expert Counterfactuals

- Engelbart's system-improving lens would have modeled the coverage producer,
  quality batch scheduler, and report-retention reader as one H+LAM+T system at
  the start. That would have exposed the shared hidden filenames before the
  first broad run; the next improvement is to name runtime files from the
  public report identity at creation time.
- A direct concurrency counterfactual asks, “Which files can these two supposedly
  parallel checks both create, truncate, or combine?” Applying it to every
  coverage-producing gate before batching would have prevented the race without
  giving up useful parallelism.

## Sibling Search

- cross-file: `scripts/mutation_sampling_lib.py` → `scripts/run-quality.sh` and
  `scripts/manage_mutation_reports.py` | decision: repaired the shared hidden
  runtime namespace and its retention reader together | proof: focused namespace
  test plus post-fix changed-line producer | follow-up: deferred sibling audit
  for other report-producing tools
- cross-file: `scripts/session_start_lesson_context.py` →
  `skills/public/retro/scripts/plan_retro_run.py` | decision: valid follow-up
  remains in existing issue #639 | proof: continuity gate's unclaimed-emission
  report and the session-start routing contract | follow-up: #639

## Lesson Evaluation

Lesson evaluation: {"score_event_count": 3, "session_id": "2026-08-20-01a01e8e-3ede-7053-8d51-0f9afd502234", "status": "effect-recorded"}

The harmful question first: no selected lesson pushed this work unit toward a
wrong technical action or caused a useless read. Three lessons changed concrete
actions and are scored; the remaining selected lessons have no honest encounter
anchor in this window and remain unscored rather than being treated as failures.

## Next Improvements

- workflow: before a quality batch is formed, inventory hidden files created by
  every concurrent check and require disjoint paths or an explicit serialization
  edge. recurrence-class: parallel-coverage-runtime-collision is now carried
  by the namespace regression and the closeout record.
- capability: make the session-start workflow surface any outstanding declared
  session before opening another one, while preserving the no-auto-write rule;
  `Structural pattern: state opened by one actor and enforceable only against a
  later stranger. Triggering instance(s): 2026-08-20 session receipt and prior
  2026-08-18 recurrence. Destination: issue #639.`
- memory: keep the handoff rule “commit, then changed-line proof, then broad
  quality,” and add “parallel checks must not share hidden runtime files” beside
  it. recurrence-class: unclaimed-session-disposition remains an explicit
  open lifecycle risk until #639's acceptance is independently closed.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-21-session-retro.md
