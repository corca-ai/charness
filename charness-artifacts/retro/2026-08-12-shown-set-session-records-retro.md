# Goal Closeout Retro: Shown-Set Session Records

Goal: charness-artifacts/goals/2026-08-12-shown-set-session-records.md
Date: 2026-08-12

## Context

This goal made cited lesson scoring locally eligible only after an operator has
recorded a deterministic session snapshot that contains the lesson. It adds no
claim that a person received, read, used, or benefited from the list.

## Window

- Baseline: the completed schema-v2 cited-score ledger, flat deterministic
  preview, and zero-score ledger state.
- Completed work: schema-v3 session events, immutable v2 migration cutoff,
  shared local writer lock, session-bound score authoring, root/plugin sync,
  two review rounds, and final quality proof.

## Evidence Summary

- `scripts/check_lesson_ledger.py --repo-root .` validated 16 lessons and 16
  transitions; `check_contract_register.py` validated 26 units with no
  citations or proposals; the rebuilt selection index and a 10/16 preview also
  passed.
- `pytest -q tests/test_contract_register.py tests/test_lesson_ledger.py
  tests/test_lesson_ledger_refusals.py tests/test_lesson_selection_preview.py`
  and `./scripts/run-quality.sh --read-only` passed. The retained broad-quality
  receipt records that its changed-line gate passed; it does not retain focused
  mutation file-count detail.
- Delegated repaired-surface review reported strict-type, migration, and
  containment gaps after preparation packet `2026-08-12-025103-packet.md`.
  The packet itself preserves preparation inputs, not the reviewer result; the
  repairs remain operationally accepted-unreviewed under the two-round cap.
- Packet Consumed: disposable JSON preparation for `58e48ea5..662b632c`,
  prepared as `shown-set session records closeout`; no Markdown packet was
  placed in the retro corpus for this closeout.

## Waste

- The final changed-line proof initially left the renderer entrypoint unmapped.
  Adding a real `__main__` test exposed one uncovered exit line; the exact
  mutation failed the new test and was restored before closeout. The resulting
  test module exceeded the repository length cap, so refusal-path coverage was
  split into a cohesive dedicated test module rather than mechanically spilling
  it into a helper file.

## Critical Decisions

- Freeze the record-time preview snapshot and its canonical SHA-256 rather
  than re-render historical sessions from mutable scores or source artifacts.
- Preserve a committed v2 score prefix only through an immutable migration
  cutoff; all newly appended v3 scores require a known containing session.
- Keep score budgets, presentation receipts, archive state, calibration, and
  graduation outside the local eligibility claim because the current cohort has
  no score evidence.

## Trends vs Last Retro

The completed ledger goal deferred presentation and budget policy. This goal
adds the narrower structural eligibility seam without converting a local
declaration into human-observation evidence; the same non-claim remains intact.

## North Star Alignment

The gate now decides the observable escape: a cited new score cannot name an
unknown session or a lesson absent from that session, and committed event
prefixes cannot be silently rewritten. Distinct reviewers and the broad quality
lane checked the verdict surface. Git history, delivery, usefulness, and
contract mutation remain outside what this local state can observe.

## Expert Counterfactuals

- Ousterhout's design lens favors the frozen session event over a second
  presentation subsystem: one replayable ownership boundary keeps current
  selection policy changes from invalidating old declarations.
- Klein's decision-quality lens would ask what the record actually observes.
  That question rejects synthetic historic sessions, score budgets, and
  human-receipt language despite their apparent operational convenience.

## Sibling Search

- test organization: `tests/test_contract_register.py` and focused ledger
  modules | decision: applied in this slice | proof: the repository length gate
  refused the 862-line ledger test module | follow-up: none — the dedicated
  refusal module is now the bounded owner.
- proof mapping: `scripts/suggest_mutation_coverage_command.py` | decision:
  diagnostic-only | proof: the renderer became mapped when its actual script
  entrypoint was exercised | follow-up: deferred docs/handoff.md#next-session.

## Portable Candidate

Not portable — session-to-score containment is coupled to this repository's
retro citations, recurrence classes, and local ledger schema.

## Next Improvements

- workflow: run changed-line coverage before the final broad quality lane so a
  missing script entrypoint proof is found while the relevant test context is
  still local (recurrence-class: changed-line-proof-before-broad-quality).
- capability: defer any presentation receipt or score-budget design until a
  separately authorized workflow supplies real observations.
- memory: retain the local-declaration non-claim in the ledger specification,
  goal, and this retro rather than inferring user exposure from a stored seed.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-12-shown-set-session-records-retro.md
