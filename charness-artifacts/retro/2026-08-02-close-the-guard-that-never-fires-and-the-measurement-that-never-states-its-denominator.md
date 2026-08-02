# Close the guard that never fires, and the measurement that never states its denominator
Date: 2026-08-02

## Context

Two proof surfaces whose wrong pass was silent by construction, both found by the
previous run's reviewers and deliberately left unfixed.

Lane A (#471): `validate_critique_artifacts.has_repo_delegation_contract`
substring-tested an unbolded marker against an `AGENTS.md` that writes
`**already delegated**`, so it returned `False` in the repo that wrote it and
`_check_forbidden_blocker_phrases` had never executed. Lane B:
`audit_disposition_corpus.py` reported `in_scope` — the fail-closed population
that silently absorbs every undatable artifact — without ever stating the dated
denominator.

Both shipped in one commit. The run's defining fact: **the bounded round that read
only the REPAIRS found the most serious defect of the run, and it was in Lane B's
own repair — a population statement that hid part of its own intake.** The thesis
failed on the slice implementing the thesis.

## Evidence Summary

- Lane A: `scripts/validate_critique_artifacts.py` — `has_repo_delegation_contract`
  now flattens inline markup and guards `OSError`; the refusal names the matched
  phrase. 4 new tests in `tests/test_critique_artifact_validation.py`, including
  the one that never existed: a test reading the REAL `AGENTS.md`.
- Lane B: `skills/public/achieve/scripts/audit_disposition_corpus.py` — `summarize`
  extracted from `main`, status normalized, intake split three ways, denominator
  stated. 5 new tests in `tests/quality_gates/test_goal_disposition_gate.py`.
- **Measurement with its denominator, taken BEFORE the repair and again after:**
  the woken gate refuses **0** candidate artifacts, at every point measured. The
  denominator moves because this run writes into the corpus it measures: **686**
  pre- and post-repair (986 `critique/*.md` minus 300 prepare-packet documents;
  587 with a readable `Fresh-eye satisfaction` value), **687** at closeout once
  this run's own resolution critique landed. Corroborated on a different channel
  by a round-1 reviewer's case-insensitive grep across all 986 files, which found
  no matches at that point — so the 0 does not depend on the denominator being
  right. The closeout-claims reviewer then found that this run's own resolution
  critique later introduced one PROSE occurrence while discussing the phrase; the
  conclusion holds on the narrower and stronger ground that no artifact's
  `Fresh-eye satisfaction` VALUE contains any of the six.
- **The 0 is honest but narrower than it reads.** It measures how narrowly
  `FORBIDDEN_SUBAGENT_BLOCKER_PHRASES` is spelled: 2 checked-in artifacts name a
  delegation policy as the canonical blocker in a real `Fresh-Eye Satisfaction`
  value and pass on spelling. A third cited artifact turned out to be a separate
  defect — it writes `Fresh-eye status:`, a field-name variant the reader never
  reaches, so widening the list would not catch it. Filed as #472 rather than
  widened, because widening refuses checked-in artifacts.
- **A completed goal was invisible to the audit.** Round 2 found `summarize`
  compared `status == "complete"` case-sensitively;
  `2026-06-08-preflight-gate-phase-coverage.md` writes `Status: COMPLETE
  (2026-06-07)` and so fell out of `completed_goals` AND out of
  `rows_without_status` — present in the corpus, absent from every reported
  bucket. `completed_goals` moved 121 → 122 on repair.
- **A second guard that cannot fire, found inside Lane B's own surface:**
  `--fail-on-pre-rule-refusal` is 0 by construction, because
  `apply_disposition_rungs` returns at `if not in_scope` before any
  `disposition_blank` is set. Annotated, filed as #473, not repaired.
- **Two** bounded review ROUNDS over the code (three `bounded-reviewer` spawns:
  one per lane in round 1, one over the repairs in round 2), plus a third round —
  the closeout-claims review — for four spawns total. Each round was
  fingerprinted and its `verify --before` returned `clean`: three verifies, one
  per round. The count matters because it is an integrity attestation; an earlier
  draft of this line said "three bounded rounds" and conflated spawns with rounds.

## What Created Waste

- **Running the duplicate ratchet at the closeout aggregate instead of at the
  first edit to a gated file.** The plan's own Low-Cost Checks said to run it at
  the first edit. Doing it at the end turned a two-line classification note into a
  hard block discovered after the commit message was written, and cost a full
  gate re-run cycle.
- **Re-serializing `dup-review.json` with `sort_keys=True`.** The minimal change
  was 14 inserted lines; the first attempt produced a 50/36 diff that reordered
  keys across 14 unrelated entries. Caught by reading the diff before committing,
  but only because the line count looked wrong for a two-entry insert.
- **Guessing an issue number before filing.** I wrote `#473` into `docs/handoff.md`
  for the near-miss issue before `gh issue create` returned `#472`, then had to
  correct it. Filing first and writing the number second costs nothing.
- **Writing handoff prose without checking its budget.** The handoff gate refused
  the commit at 78 content lines against a 58 limit, after the commit message was
  already composed. The right move was rewriting it for the next session — which
  it needed anyway, since the goal it pointed at was now complete — not patching.
- **Naming the wrong phrase in an assertion.** The new refusal-message test
  asserted `current developer instruction only permits` when the list matches
  `only permits spawning subagents when` first. One failed run to find it; the
  cheaper path was reading the tuple order before writing the string.

## What Mattered

- **Verifying the named remedy's premise before shaping the slice.** Both lanes
  arrived as reviewer assertions. Checking Lane A's first revealed the sibling
  `issue_critique_observer` ALREADY carried the exact repair, with a comment saying
  the two surfaces deliberately disagreed. That changed the work from "invent a
  matcher" to "restore parity", produced the parity test, and made a stale comment
  visible. None of that was in the plan.
- **Measuring before the fold, and again after.** Both measurements agreed, which
  is what made "ship with no grandfather" a defended decision rather than a hope.
- **The second bounded round.** It was mandatory by contract and it earned it: the
  case-sensitivity blocker was invisible to round 1 because round 1 reviewed code
  that did not yet contain the population statement. It also caught two sentences
  of MINE that asserted more than was established — an "and no other shape"
  closure claim, and a 0 described as "confirming" control flow when it is merely
  unable to be non-zero. Writing a correct explanation of why a number is 0 turned
  out to be as error-prone as the original defect.
- **Filing instead of fixing, twice.** #472 and #473 were both tempting one-line
  changes. Both would have armed or altered a verdict surface on a corpus that
  could not object.

## Next Improvements

- Run `check_dup_ratchet.py` at the first edit to a gated file, not at the
  closeout aggregate — the plan already said so and the run still did not.
- When editing a checked-in JSON policy file, preserve key order and diff the line
  count against the expected insert size before staging.
- File the issue first, then write its number into prose.
- Check `validate_handoff_artifact.py` before composing a commit message when the
  handoff was touched.
- Treat "explain why this number is 0" as a claim needing the same premise check
  as any other claim.

## Persisted

Persisted: yes: charness-artifacts/retro/2026-08-02-close-the-guard-that-never-fires-and-the-measurement-that-never-states-its-denominator.md

## Sibling Search

The transferable pattern is **a count whose value is determined by structure
rather than by the thing it purports to measure**. Three instances surfaced in one
run: #471's guard (0 refusals because the gate never ran), #473's flag (0 because
the predicates are mutually exclusive), and Lane B's `in_scope` (a number whose
population was never stated). The generalized trigger — a reported count that
cannot vary with the corpus — is what #473 records for the next session.
