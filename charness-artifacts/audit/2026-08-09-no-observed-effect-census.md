# NO-OBSERVED-EFFECT Census — the checks `run-quality.sh` queues
Date: 2026-08-09
Instrument: dynamic workflow, 11 Sonnet agents, 6 classify chunks + 4 adversarial
refuters + 1 synthesis. 744K subagent tokens, 213 tool calls, ~5m wall clock.
Run: `wf_75898014-5f8`

## Why this exists

The operator asked one check — `check-title-slug-drift` — why it existed, and the
answer was that it could not fail, had never been observed catching anything, and
was not worth repairing. The obvious next question was whether that was one
instance or a population. `#521` has been open on exactly this question
("프롬프트 표면이 단조증가한다 — NO-OBSERVED-EFFECT에 삭제 실험 경로를 열 것인가")
without the evidence that would settle it.

## Result

| | count |
| --- | --- |
| Unique checks queued by `scripts/run-quality.sh` | 90 |
| Classified `no-observed-effect-candidate` on the first pass | 6 |
| **Refuted by adversarial verification** | **4** |
| **Survived** | **2** |

**The suspicion that "many such checks exist" is not supported. Two of ninety.**

### Survivors

- **`check-title-slug-drift`** (`scripts/check_title_slug_drift.py`) —
  advisory-only; `return 1 if drift and args.strict else 0` and no caller passes
  `--strict`. Already decided for deletion by the operator; the census is
  corroboration, not an independent second source.
- **`check-public-doc-coupling`** (`scripts/check_public_doc_coupling.py`) — NEW
  finding. `main()` has exactly two return paths and both `return 0`; the
  docstring says "Always exits 0" and that is accurate. No downstream script
  consumes its JSON as a decision input. Two commits in its entire history, and
  it was created to guard a one-time 2026-06-11 manual cleanup. **9 live reference lines**, all internal (`run-quality.sh`, two docs, its own test) — no
  public-skill prose ships it, so removal cost is close to the grep count.
  Counter-argument on record: it is the only detector for that drift class, and
  no-recorded-catch is not proof no human ever acted on its `ADVISORY:` line.

### Refuted — the four the adversarial pass saved

This is the most important number in the file. **A single-pass census would have
recommended deleting four working surfaces.** 4 of 6 first-pass candidates were
wrong, a 67% false-positive rate on exactly the verdict class this repo keeps
repairing.

- **`inventory-quality-handoff`** — a measurement surface whose product is a
  number other work consumes, not a pass/fail. Function, not teeth.
- **`check-test-production-ratio`** — `run-quality.sh:458` matches
  `^(WARNING|WARN|WEAK|ADVISORY)(:|[[:space:]])` and forces the full phase log to
  print. The advisory line is wired to a real consumer; it is not inert.
- **`inventory-sloc`** — `inventory_sloc.py:73` calls `json.loads()` inside
  `_run_tokei()` guarded only by `except RuntimeError`, so a `JSONDecodeError`
  propagates and the process exits nonzero. It CAN fail; the first pass read
  `main()`'s returns and missed the raise.
- **`inventory-cli-ergonomics`** — same shape.

## What this census did NOT establish

- It tested "can this exit nonzero AS CURRENTLY INVOKED", not whether an advisory
  line ever prompted a human fix that went unrecorded. Absence from the artifact
  trail is being read as absence of value, and nothing obliges a reader of a
  `WARN:` line to log that they acted on it. That gap is real.
- It did not re-derive the repair/re-scope alternatives as seriously as deletion.
  For `check-title-slug-drift` it inherited the operator's decision rather than
  re-testing it.
- The reference counts are static grep hits today, not a measured cost of
  executing a removal correctly.
- No consumer-repo dependency was checked: whether any installation outside this
  repo relies on either script existing is unmeasured.
- Neither survivor's "no evidence of a catch" was checked against CI logs, only
  against committed artifacts and git history. Silence is suggestive, not
  conclusive.

## Correction to the run's own framing

The synthesis prompt asserted that `check-title-slug-drift` had "already been
deleted on exactly this reasoning". That was wrong and the agent caught it: both
the script and its `skills/shared/scripts/` shim still exist and are still wired
into `run-quality.sh`, `.githooks/pre-push`, and `staged_commit_gate_plan.py`.
The correct status is DECIDED, NOT DONE — recorded as slice 3 of a `draft` goal
with an empty `## Slice Log`. Recorded here because a census that overstates its
own baseline is the defect the census is looking for.

## Non-claims

- No check was deleted, disarmed, or modified by this census.
- The 90 classifications were produced by Sonnet agents reading source; only the
  6 candidates were adversarially attacked. **The 84 `earns-its-place` verdicts
  were NOT independently verified**, so a check wrongly cleared would not have
  been caught. The census is biased toward false negatives by construction, which
  is the safe direction for a deletion question.
- `check-runtime-budget` was classified `earns-its-place` because it CAN fail on
  `violations` and `profile_config_errors`. That does not contradict `#546`,
  whose narrower claim is that the `missing_samples` SUBSET can never fail. The
  census did not measure that subset.
