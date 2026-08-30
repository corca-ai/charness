## Situation

`skills/shared/scripts/reviewer_worker_runtime.py` is the portable reviewer worker's
runtime. While fixing #755 it went from 346 to 357 tokei code lines against a hard
limit of 360, and `check_code_lengths` reported it inside the advisory warn band
`[330, 360]`.

## Observed problem

The file owns five separable concepts at once:

- worker path preflight and artifact-collision refusal (`preflight`);
- per-backend CLI command construction (`_command`);
- backend raw-output normalization (`_normalize_claude`);
- process execution, timeout, and process-group cleanup (`_execute_backend`);
- result validation, provenance joining, and receipt assembly (`_validate_result`, `run`).

The length gate's own message prescribes the response: *"Split the file into a
cohesive new module or delete code; do not mechanically spill into an
`_extra_lib`/`_lib` companion to dodge the cap (docs/deferred-decisions.md D33)."*
The advisory adds the question a consumer must answer — is this an honest cohesive
unit near its limit, or genuine over-accumulation? The answer here is
over-accumulation: nothing about backend CLI shapes belongs in the same module as
receipt assembly.

## Evidence

- `python3 scripts/check_code_lengths.py --repo-root . --paths skills/shared/scripts/reviewer_worker_runtime.py`
  reports `357` within `[330, 360]`.
- The #755 slice already took the cheap moves and stopped: `write_model_authored_schema`
  moved to `skills/shared/scripts/reviewer_result_contract.py` (a concept move, not a
  spill), and the two bootstrap import-fallback blocks merged into one. Those bought
  4 lines, not headroom.
- The residual margin is 3 lines. The immediately preceding session pushed
  `test_release_distinct_channel.py` from 798 to 824 over an 800 cap and found it only
  by accident while renaming the gate, which is what a 3-line margin invites next.

## Why it was not done in the #755 slice

The natural extraction is the backend boundary — `_command`, `_normalize_claude`, and
arguably `_execute_backend` — into a `reviewer_worker_backend` module. That extraction
requires `WorkerError` (defined at `reviewer_worker_runtime.py:79` and raised
throughout the runtime) to move as well, or the new module imports it back circularly.
Moving the worker's typed failure vocabulary is a production-surface change to the
consumer-facing review path, and riding it on a consumer-facing bug fix would have
made one commit answer for two unrelated risks.

## Expected behavior

One cohesive module owns how each backend is invoked and how its raw output is
normalized; the runtime owns lifecycle, validation, and the receipt. The move is
behavior-preserving, so the existing `tests/quality_gates/test_reviewer_worker.py`
end-to-end suite is the proof surface — including the two #755 cases that drive the
real entrypoint through a fake `codex`.

## Non-claims

- No defect in current behavior is claimed. Both lanes are green: standing 8573
  passed including `release_only`, broad 79 passed / 0 failed.
- This is not a request to raise the cap.
- `WorkerError`'s eventual home is not decided here; whether the failure vocabulary
  belongs with the backend boundary or in a module of its own is part of the work.

---

<!-- charness-work-item-key: issue-756-reviewer-backend -->
# Work Item #756 — Give reviewer backend invocation one owner

## Purpose and premise

Extract the backend invocation and normalization boundary from reviewer worker lifecycle code before #731 changes broader lifecycle semantics.

## Acceptance and proof

Every supported backend normalizes through one owner; backend-specific failure and timeout remain typed; a deliberately duplicated path fixture fails owner checks.

## Non-claims

No lifecycle redesign, new backend, or approval inference from normalized process status.
