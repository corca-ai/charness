# Goal #844 WI-12 guarded-close proof (2026-09-24)

Parent operator: Muse Code. All provider mutations via the `issue` skill;
exact backend readback below. No `scripts/`, `tests/`, or `docs/` edits in
WI-12; no `gh` writes outside the skill; no release, version, or push.

## Child graph readback (goal-run-read, 2026-09-24)

- #844 OPEN (parent); children #845-#857 CLOSED; #858 OPEN (this slice).

## Guarded closes (close-with-comment + verify-closeout, all `verified`)

| Issue | Mapped slice | Child readback | Verdict |
| --- | --- | --- | --- |
| #837 steer | WI-3 | #847 CLOSED | closed + verified |
| #838 executor probe | WI-2 | #846 CLOSED | closed + verified |
| #839 self-review | WI-7 | #851 CLOSED | closed + verified |
| #840 exit codes | WI-1 | #845 CLOSED | closed + verified |
| #841 merge train | WI-8a | #852 CLOSED | closed + verified |
| #842 lesson injection | WI-6 | #850 CLOSED | closed + verified |

Beyond the mapped children, also read back CLOSED: #848 (WI-4), #849
(WI-5), #853 (WI-8b), #854 (WI-9), #855 (WI-10a), #856 (WI-10b), #857
(WI-11).

## #843 stays OPEN (recorded reason)

Items 1-7 (WI-4/WI-5), 10-11 (WI-9), 12 (WI-7), 13-14 (WI-10a/b), 15-18
(WI-11) all landed and their children read back CLOSED. Items 8-9 (WI-8b
DAG) are functionally present (read-only lane PASS, DAG tests green), but
the delivering module violates a pre-existing repo quality gate:
`scripts/task_run/task_run_dag.py:540` writes JSON to stdout, failing
`test_public_skill_yaml_output_contract.py::test_no_repo_owned_command_writes_json_to_stdout`
(gate added 2026-07-18; line introduced by goal-session lane persist
4fa8247b1, which created the module). The print path is currently
unreachable from any CLI surface (no command wiring, no CLI-reference
entry), but the tree is red on that gate regardless.

Fixing it (YAML migration or contract exemption plus consumer check) is a
code change outside WI-12 scope, so #843 stays OPEN pending a follow-up
migration lane. No other issue is blocked by this finding.

## Verification evidence

- Read-only lane `wi-12-readonly-verify` (report-only): verdict success;
  12/13 slice PASS, pytest 8 passed; 1 FAIL (WI-10b clause wording, see
  adjudication below).
- Full standing suite: 10288 passed, 1 failed (the dag.py:540 gate above).
- `check-docs.sh` PASS; CLI reference renders clean; plugin mirror export
  clean (1162 unchanged); code-length gate exit 0; `git diff --check` clean.
- Resume-guard suites (831/834/835): 12 passed — no slice reintroduced
  relaunch-where-resume-applies.
- `skills/public/` untouched (no edits since 2026-09-23, none this session).

## Adjudications

- WI-10b non-authority clause: behaviorally present. Skips replay only
  outcomes satisfying the frozen success envelope (`_green_envelope`:
  SUCCESS kind + frozen exit code + PASS + exit 0 + no failures) with both
  hashes matching; tampered/failed records force re-execution (pinned by
  `test_skip_requires_frozen_success_envelope` and
  `test_failed_verify_outcome_is_never_cached`). A skip therefore never
  asserts completion beyond the frozen prior green it replays.
- Changed-line proof no-verdict (WI-11): focused producer fails only on the
  dag.py:540 offender above; parent coverage instead (friction module 100%
  under 159 topical+sibling tests).

## Goal completion status

13 of 14 slices closed and verified. #843 remains open per the recorded
reason above; closing it is a follow-up migration lane, not WI-12 work.
