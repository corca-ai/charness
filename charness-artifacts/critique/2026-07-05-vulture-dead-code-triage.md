# Vulture Dead-Code Advisory Triage Closeout
Date: 2026-07-05

## Decision Under Review

Handoff Next-Session item 1: triage the 33 `review_candidate` findings the newly-wired
(default-off, never-blocks) vulture dead-code advisory flags on a real run — delete genuine
dead code, or confirm/leave false positives. Shipped: 15 dead module-level symbols deleted,
2 orphaned-by-cascade symbols deleted (`ISSUE_392_SID`, `WHOLE_REPO_ROUTING_FIXTURE_PATH`),
1 dead duplicate function at a P4 boundary deleted (`has_ai_provenance_marker`), 1 vestigial
0-test file deleted (`tests/test_handoff_skill_md_budget.py`), and 7 test-local protocol/mock
params fixed idiomatically (drop unused pytest-hook param, collapse subprocess-mock kwargs to
`**_kwargs`, `_`-prefix `wt`/`exc_type`). Net ≈ −135 lines across 31 files. The advisory's
high-signal PRIMARY pass (confidence 80) is now CLEAN (0); the noisy SWEEP pass (confidence 60)
dropped 33→10, all 10 confirmed benign.

Scope discipline: the fix followed a repo-wide usage scout (`git grep -w` across all `.py` +
`.md`/`.json`, excluding the plugin mirror and mutants), so every "delete" is a zero-live-reference
symbol, not a guess. ONE correction: two symbols (`ATTENTION_STATES`, `ATTENTION_EVIDENCE_TERMS`
in `report_usage_product_review.py`) were initially deleted as zero-reference, but the
`validate_attention_state_visibility` pre-commit gate correctly BLOCKED the commit — they are not
dead, they are the in-file string-literal markers that gate detects to prove the module's exit-0
attention states (`no_adapter`/`disabled`/`no_records`, actually emitted via imported payload
builders). Both were restored with a `do-not-delete` comment. Lesson: a zero-*code*-reference
symbol can still be a required *gate* marker; the usage-scout and the fresh-eye deadness-grep both
looked only for code references and missed it — the attention-state gate is what caught it.

## Failure Angles

- A "dead" symbol could be live via dynamic dispatch / wildcard re-export the grep missed.
  Checked: no `import *` re-exports of any affected module; the fresh-eye reviewer independently
  re-ran `git grep -w` for every deleted symbol and found zero live references (only historical
  `charness-artifacts/` markdown mentions, not code).
- A boundary floor could be silently removed. `has_ai_provenance_marker` lives in the north-star
  P4 issue-closeout file and its docstring claims "enforced by the closeout floor." Checked: the
  LIVE floor is `evaluate_ai_provenance` (wired at `issue_verify_closeout.py:222`, feeds the verdict
  `ok`) using the same `_PROVENANCE_ALIASES` field check; `has_ai_provenance_marker` was a dead
  DUPLICATE of that logic with zero callers. Deleting it left `evaluate_ai_provenance` and all its
  helpers (`_PROVENANCE_ALIASES`/`_first_field`/`_body_fields`/`_has_substantive_value`) intact —
  the floor is still enforced (reviewer confirmed).
- Deleting a function could orphan its private helpers/constants/imports. Checked: cascades handled
  in the same edit (`WHOLE_REPO_ROUTING_FIXTURE_PATH`, `ISSUE_392_SID`); `ruff check` passes on all
  deletion files (no orphaned imports); shared helpers still used elsewhere were kept.
- A test-local "fix" could change test behavior. Checked against real call sites: the `**_kwargs`
  mocks still receive the keyword args the code-under-test passes (`subprocess.run(..., capture_output=True,
  text=True)`), bodies still assert on `command`/`cmd`; dropping `exitstatus` is a valid partial pytest
  hook signature (body never used it); underscore renames are cosmetic. 132 + 257 tests pass.
- Deleting a whole file could lose coverage. Checked: `git show HEAD:tests/test_handoff_skill_md_budget.py`
  had NO `def test_`/class/assert — a vestigial docstring + unused `REPO_ROOT` after its fixtures were
  removed earlier; the ≤161-line intent is still covered by the general 200-line MAX_SKILL_MD_LINES gate.

## Counterweight Pass

- Real work folded now: −148 lines of genuinely-dead code removed; a confusing dead DUPLICATE of a live
  P4 floor eliminated; a vestigial 0-test file removed; `issue_verify_closeout_body.py` incidentally
  dropped 333→322, exiting its own length warn band. PRIMARY advisory now clean.
- Deliberately LEFT (confirmed benign, not deleted — deleting would be the worse error): the 10 residual
  SWEEP review_candidates. Five are genuine vulture false positives with live references — dataclass
  fields (`has_package_json`, `current_artifact_path`, `write_artifact_role`, `current_pointer_is_symlink`)
  and used functions (`reconcile_find_skills_hooks`, `sibling_loader`). Two are documented-intentional
  vocabulary constants tied to disclosed residuals: `AI_PROVENANCE_MARKER` (canonical P4 marker text) and
  `DISTINCT_CHANNEL_STATUSES` (release distinct-channel verdicts, declined D35). Two are the restored
  attention-state-visibility markers (`ATTENTION_STATES`, `ATTENTION_EVIDENCE_TERMS`) — gate-required, not
  dead. (One more, `structured_output_field`/`rss_kib`, was already auto-bucketed as non-review.) The SWEEP
  pass is explicitly documented to "include ... dynamic-use false positives," so these are the expected floor.
- Deliberately NOT done: extending the classifier with a per-name allowlist to suppress the 8 residuals.
  Rejected as disproportionate — it is a quality-gate contract change (with its own pinning test) for
  marginal benefit on a default-off advisory whose sweep is designed to be noisy. Left as a clean
  follow-up if a future maintainer wants a silent sweep.

## Structured Findings

- F1 | bin: bundle-anyway | evidence: strong | ref: scripts/cautilus_scenarios_lib.py:46 | action: fix | note: 17 zero-reference dead symbols + 2 cascade orphans deleted; every one confirmed by repo-wide grep and re-verified by the fresh-eye reviewer
- F2 | bin: over-worry | evidence: strong | ref: skills/public/issue/scripts/issue_verify_closeout_body.py:374 | action: document | note: P4 provenance floor stays enforced via evaluate_ai_provenance; only the dead duplicate has_ai_provenance_marker removed, no orphaned helper
- F3 | bin: bundle-anyway | evidence: strong | ref: tests/conftest.py:42 | action: fix | note: 7 test-local protocol/mock params fixed idiomatically (drop/`**_kwargs`/`_`-prefix), not suppressed; primary advisory pass now clean
- F4 | bin: bundle-anyway | evidence: strong | ref: tests/test_handoff_skill_md_budget.py | action: fix | note: vestigial 0-test file deleted; intent covered by the 200-line SKILL.md gate; zero coverage lost
- F5 | bin: valid-but-defer | evidence: moderate | ref: skills/public/quality/scripts/run_dead_code_advisory.py | action: defer | note: 10 residual SWEEP review_candidates are confirmed benign (used FPs + documented-intentional + gate markers); a classifier allowlist to silence them is a disproportionate default-off-gate contract change, left as optional follow-up
- F6 | bin: act-before-ship | evidence: strong | ref: scripts/report_usage_product_review.py:37 | action: fix | note: two "dead" constants were the in-file markers the attention-state-visibility gate detects; the pre-commit gate BLOCKED the over-deletion; restored with a do-not-delete comment. The usage-scout + fresh-eye grep only checked CODE references — a zero-code-reference symbol can still be a required gate marker

Fresh-eye satisfaction: parent-delegated — a bounded fresh-eye subagent (general-purpose,
id a9fdb052c3b0e8aea) adversarially reviewed the staged diff across all six requested angles and
returned SHIP with no defects, each angle CONFIRMED by execution (independent `git grep -w` for every
deleted symbol, verifying evaluate_ai_provenance still wired, `ruff check`, checking the mock call sites,
`git show HEAD` on the deleted file, and byte-diffing mirror copies).

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent in a different agent context, adversarial, read-only in the shared parent worktree
- Requested spawn fields: the full staged diff, the deadness/boundary/orphan/test-fidelity/vestigial/mirror angles, and the specific claim that has_ai_provenance_marker is a dead duplicate of the live evaluate_ai_provenance floor
- Host exposure state: applied
- Application state: host-confirmed: subagent a9fdb052c3b0e8aea ran to completion and returned verdict SHIP with per-angle commands and observations
