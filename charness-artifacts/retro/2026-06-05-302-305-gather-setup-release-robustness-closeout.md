# Retro: Issues #302–#305 gather / setup / release robustness (goal closeout)

Date: 2026-06-05
Mode: session

## Context

Closeout of the `2026-06-05-302-305-gather-setup-release-robustness` achieve
goal: four independent robustness fixes (setup template↔inspector agreement,
setup adapter-first reviewer rule, gather agent-browser close + clean-runtime
proof, release publish resilience), each with regression tests and a
`Close #N` direct-commit closeout. Final broad pytest gate: 2192 passed, 4
skipped, 25 deselected in 171s. Issues stay OPEN until the maintainer pushes.

## Evidence Summary

Five fix/closeout commits (db66a30b #304, cb909eda #303, 5318a9a7 #302, 4b76196f
#305, 0c593e23 test-fixture follow-up). Four bounded fresh-eye subagent reviews
(one per slice). Host probe (claude session, thread-wide, not goal-scoped): 54
function calls, 17 custom tool calls, 13 patch applications, 0 compactions,
git-status x3. Probe `subagent spawn=0` is a known undercount — the Agent-tool
fresh-eye spawns (4 this run) are not counted by the probe's event key; the
honest count is four bounded reviewers.

## Waste

- Test-fixture drift (`shutil.ignore_patterns` inline in the #302 cleanup test)
  was caught only by the final broad pytest gate (~172s) instead of the
  per-slice deterministic aggregate, forcing a late fix commit after the slice
  was already closed. Transferable pattern → issue #307.
- **Self-inflicted detour (#302 attention-state):** the gate blocked the closeout
  because a new support module's docstring used "silently-skipped". I first took
  the WRONG, heavyweight path — declaring the new module's state in
  `skills/public/quality/references/attention-state-visibility.json` (which then
  pulled in the public-skill-validation gate) — then reverted that and reworded
  the docstring (the scoped fix). Not a one-pass reword: a real
  declare-then-revert detour. Root cause: authored support-module prose before
  knowing the gate's banned vocabulary.
- **Iteration (#305 staleness check):** first written as a general semver-scan
  regex, then rewritten to previous-vs-target substring containment after the
  fresh-eye review flagged date/`v`-prefix edges — one wasted iteration a
  regex-edge premortem would have skipped.
- **Unplanned refactor (#302 length gate):** `acquire_public_url.py` was near the
  skill-helper Python-length limit, forcing a mid-slice extraction of
  `agent_browser_session.py` — churn driven by adding to a near-limit file
  without checking headroom first.
- Smaller gate-caught frictions, each one edit, NOT itemized further (recording
  bar stated): the bug-class `Siblings:` field parse (`Decision:`/`Proof:` at line
  start read as new ledger fields) and the phase-routing `Routing:` regex
  capturing only the first physical line. Both validators gave precise errors at
  the right boundary — working as intended.

## Critical Decisions

- #304 RN1: relax the inspector (whitespace-normalize contract-snippet matching)
  rather than de-wrap the template — also fixes any consumer repo that copied the
  documented wrapped block.
- #305: explicit opt-in `--resume` over automatic idempotency — closes the B3
  double-publish hazard surfaced at shaping.
- Folded both fresh-eye edge findings in-slice rather than deferring: the #302
  chrome/chromium markers were tightened to require a headless/automation context
  (a desktop Chrome reparented to PID 1 would otherwise have false-positived the
  unconditional, waiver-stripped `--assert-no-orphans` closeout gate on other dev
  machines), and the #305 staleness check moved from a general semver scan to
  precise previous-vs-target containment (no date false positive, no v-prefix
  false negative).

## Expert Counterfactuals

- Jef Raskin (make system state/contracts discoverable): the repo-copy invariant
  and the attention-state vocabulary are "hidden rules" that only surface at gate
  time. A Raskin lens argues the cheap structural invariant should fail at the
  commit boundary where the change is made (issue #307), and that authoring a new
  support module should surface the gated vocabulary up front.
- Gary Klein (premortem): the shaping plan critique already premortem'd the #305
  double-publish hazard (B3) and the #302 over-claim (B2), which is why both were
  handled cleanly. Applying the same premortem to the #305 staleness regex before
  the fresh-eye pass would have caught the date/v-prefix edges one iteration
  earlier.

## Next Improvements

- workflow/capability: run cheap standalone structural checkers
  (`check_test_repo_copy_invariants.py` and peers) in the per-slice / pre-commit
  aggregate so test-fixture drift fails at the commit boundary, not the final
  broad gate. Disposition: issue #307 (quality-contract change; routes through
  `quality`).
- workflow: know a constrained surface's rule before authoring into it
  (attention-state banned vocabulary, `check_python_lengths` headroom, regex
  edge cases), so the #302 docstring detour, the #302 length-gate refactor, and
  the #305 regex→containment rewrite are avoided up front rather than caught
  late. Disposition: issue #308 (authoring-preflight discoverability; sibling to
  #307).
- test: the #305 `--resume` path lacked a negative test proving it aborts before
  push when re-validation fails (the RN2 "never push a stale commit unchecked"
  guarantee was code-traced only). Disposition: applied —
  `test_resume_aborts_before_push_when_revalidation_fails` added to
  `tests/quality_gates/test_release_publish_resilience.py` (surfaced by the
  follow-up goal critique, committed this run).

## Sibling Search

Transferable pattern: a cheap deterministic `scripts/check_*.py` invariant
enforced only via a broad-suite pytest test. Scan axis = "fast checker gated only
in broad pytest." Rather than enumerate peers here, issue #307 owns the
generalized sweep (it names the class and the `run_slice_closeout` + surfaces-
manifest destination); the in-goal instance (#302 cleanup test) is fixed and
guarded by the now-green invariant.

## Persisted

Persisted: yes (this artifact under charness-artifacts/retro/).
