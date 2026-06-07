# Resolution Critique — #329 retro disposition-form floor

Date: 2026-06-07
Issue: #329 (the retro/Auto-Retro disposition floor was presence/binding-only —
"a review ran" — and a standalone session retro had no disposition review at
all, so an invalid prose-only `Disposition: memory` could ship and only a human
reading it would catch it). Resolution: a narrow presence/enum **form** check
(mirroring `validate_proposal_fields.py`'s `Destination` enum) that rejects the
named-invalid bare `memory`/prose-only disposition and requires one of
`applied: <change>` / `issue #N` / `none — <reason>`, form-only (never a content
classifier), enforced from a date forward to grandfather frozen retros.
Reviewer provenance: bounded fresh-eye subagent review (independent agent
context, read-only in the shared parent worktree), run at the bundle boundary per
the goal's high-confidence verification plan. Verdict: SHIP-WITH-NITS.
Fresh-eye satisfaction: satisfied — parent-delegated bounded review returned
SHIP-WITH-NITS; both real findings were folded before ship (no deferral), and two
self-introduced gate regressions surfaced by the broad gate were folded too.

## Scope reviewed

- `scripts/disposition_form.py` — NEW shared single-source grammar:
  `evaluate_disposition_form` (markdown-tolerant leading-token enum),
  `scan_dispositions` (fence-masked marker scan), `invalid_dispositions`,
  `is_form_enforced` (`DISPOSITION_FORM_RULE_DATE = 2026-06-08`, fail-closed).
- `skills/public/achieve/scripts/goal_artifact_disposition.py` — rung 1c
  (`apply_disposition_form_floor`) loaded into `apply_disposition_rungs`;
  parent-walk loads the shared leaf; scoped to `## Auto-Retro`.
- `scripts/validate_retro_artifact.py` — `validate_disposition_forms` scoped to
  `## Next Improvements`, enforce-date off the retro `Date:` line + filename
  fallback.
- `tests/quality_gates/test_disposition_form_floor.py` — 21 cases; synced plugin
  mirrors.

## Findings

- **BLOCKERS: none.** The floor rejects every named-invalid form (bare `memory`,
  `memory -> …`, `memory.`, prose-only, unfiled `issue` without `#N`, bare
  `none`), accepts the three valid forms including real corpus phrasings
  (`applied: tweak`, `issues #295 and #296`, `**issue #307**`, `#328`,
  `none — <reason>`), and the cardinal "form not content" rule holds
  (`applied: tweak` passes). Corpus-wide proof: 0 completed goals and all 152
  retros validate clean — no frozen artifact is retroactively failed.
- **NIT (folded) — dateless historical retros were fail-closed into enforcement.**
  The reviewer empirically showed 93 of 152 frozen retros predate the `Date:`
  header convention; under `--all`, 4 would have been retroactively failed
  because a missing date fell through to fail-closed (in-scope), violating the
  Goodhart Non-Goal. **Acted before ship:** added a filename-date fallback
  (`YYYY-MM-DD-*.md`); only a retro with neither a `Date:` line nor a dated
  filename falls through to fail-closed (which still blocks dodging by stripping
  the date line of a current-dated file). `--all` now validates all 152 clean.
- **NIT (folded) — `none-actionable` compound word was a false-accept.** The
  `none` separator allowed a plain hyphen glued to `none`, so the compound word
  `none-actionable …` read as a valid `none — <reason>` disposition. **Acted
  before ship:** a plain hyphen now requires surrounding whitespace; em/en-dash
  and colon (not used inside compound words) still need no leading space.
- **Self-introduced regression (folded) — portable-package issue anchors.** My
  `(#329)` comments in the portable achieve leaf `goal_artifact_disposition.py`
  tripped `validate_skill_ergonomics`' `portable_package_issue_anchor` (a
  portable skill package must not carry concrete repo issue numbers). **Acted
  before ship:** generalized the wording; the `#329` provenance lives in the
  repo-level shared module + the goal artifact, the correct home.
- **Self-introduced regression (folded) — attention-state false trigger.** A
  docstring in `scripts/disposition_form.py` contained the bare term `skipped`,
  which `validate_attention_state_visibility` reads as an undeclared exit-zero
  attention state. **Acted before ship:** reworded to `not judged` (the module
  has no exit-zero skip state; the trigger was incidental).

## Structured Findings

- dateless-retro-grandfather | bin: act-before-ship | evidence: strong | ref: scripts/validate_retro_artifact.py _retro_observed_date | action: fix | note: filename-date fallback so frozen retros predating the `Date:` header stay grandfathered; fail-closed reserved for genuinely undatable files; `--all` validates all 152 retros clean. Regression tests added.
- none-actionable-false-accept | bin: act-before-ship | evidence: moderate | ref: scripts/disposition_form.py _NONE | action: fix | note: plain hyphen now requires surrounding whitespace so the compound word `none-actionable` is not read as `none` + separator + reason; em/en-dash/colon unaffected. Regression test added.
- portable-package-issue-anchor | bin: act-before-ship | evidence: strong | ref: skills/public/achieve/scripts/goal_artifact_disposition.py | action: fix | note: removed concrete `(#329)` anchors from the portable achieve leaf (caught by validate_skill_ergonomics); provenance kept in the repo-level module + goal artifact.
- attention-state-skipped-term | bin: act-before-ship | evidence: strong | ref: scripts/disposition_form.py evaluate_disposition_form docstring | action: fix | note: reworded the incidental `skipped` term to `not judged`; the grammar library has no exit-zero attention state, so this clears a false validate_attention_state_visibility trigger rather than hiding a real one.
- line-wrap-issue-fail-closed | bin: over-worry | evidence: weak | ref: scripts/disposition_form.py scan_dispositions | action: document | note: a line-wrapped `issue\n#N` scans as invalid (fail-closed false-reject), explicitly a stated non-claim; fail-closed is the safe direction for a gate and the canonical form keeps `issue #N` on one line.
- applied-vague-accepted | bin: over-worry | evidence: strong | ref: scripts/disposition_form.py evaluate_disposition_form | action: document | note: `applied: tweak` and bare-prefix forms pass by design — substance is the reviewer's job (the cardinal form-not-content rule); not a hole.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent review (independent agent context, read-only in the shared parent worktree).
- Requested spawn fields: review packet — intent, changed files, expected invariants (7), the named-invalid/valid form cases, grandfather/Goodhart date semantics, scope tightness, non-claims, out-of-scope, and five adversarial reviewer questions (closure escapes, over-reach, date off-by-one, cardinal rule, portability).
- Host exposure state: applied
- Application state: host-confirmed: subagent completed and returned a SHIP-WITH-NITS verdict with two real findings (both folded above) plus over-worry items; the two self-introduced gate regressions were caught by the broad quality run and also folded.

## Verification proof

- Targeted floor tests after folding: 21 passed (`test_disposition_form_floor.py`).
- Existing disposition/retro/goal-artifact/ergonomics/preflight suites: 117 passed
  (incl. the previously-red `test_run_checks_reports_all_portable_package_gates_on_real_repo`,
  now green after the two regression folds).
- Corpus safety: 0 completed goals retroactively form-failed; `validate_retro_artifact --all`
  validated all 152 retros clean (Goodhart Non-Goal honored — everything Created/Dated ≤ 2026-06-07 grandfathered).
- `ruff`, `check_python_lengths` (3 touched files), `validate_skill_ergonomics`,
  `validate_attention_state_visibility` (76 files), `check_export_safe_imports`,
  `check_plugin_import_smoke` (parent-walk loader resolves in the export): all green.

## Counterweight pass

- Folding both NITs was not scope creep: the dateless-retro fix is the difference
  between honoring and violating the goal's own Goodhart Non-Goal, and the
  `none-actionable` fix closes a (small) false-accept in a fail-closed gate; each
  is a few lines plus a regression test.
- The two self-introduced regressions prove the value of running the broad gate
  before close — both are portability/visibility disciplines this repo enforces on
  exactly this kind of change, and both were folded at the source with the mirror
  re-synced.
- The deliberate non-claims (form-only, never substance; inline-backtick examples
  judged like the existing fence-only gates; same-line `issue #N` assumed) are
  honest and match the disposition-floor discipline: prove the form is canonical;
  a human/reviewer judges whether the generalization is good. Pushing further would
  make the floor a content classifier (#329 Non-Goal).
