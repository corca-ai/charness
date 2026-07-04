# Dup-Ratchet Module Split Closeout
Date: 2026-07-04

## Decision Under Review

Handoff Next-Session item 2: the two dup-ratchet skill helpers sat in the SKILL_HELPER
file-length advisory WARN band (`check_dup_ratchet.py`=357, `dup_ratchet_lib.py`=340;
band `[330,360]`, hard limit 360). Triage of the *scope* — the handoff had planned to
batch this with the D30 residuals S4-Defer-1/-3 ("open the ratchet engine once,
re-baseline once") — found the residual reopen triggers had NOT materialized: post-Slice-4
baseline rotations track real code edits (e.g. the "suspicious" cautilus bugfix `9d4c2882`
actually reworked `run_skill_efficiency_ab.py` by 101 lines), not phantom in-place-comment
edits, and the membership-shrink re-baseline friction is mild/arguably-correct. The
operator confirmed **module split only**, keeping S4-Defer-1/-3 deferred with triggers intact.

Shipped: extracted the fingerprint/drift-signature collection cluster into a new leaf
`dup_ratchet_scan.py` (check 357→250) and the git stagnation seams into a new leaf
`dup_ratchet_git.py` (lib 340→309). Both original files now sit well under the 330 warn
threshold; the two new leaves are 137 and 47 code lines. Behavior-preserving move only.

## Failure Angles

- The extraction could silently change behavior (dropped function, changed default/return).
  Checked: a fresh-eye reviewer byte-compared every moved body against `HEAD` — all bodies
  identical, only the mechanical call-site renames (`_load_json`→`_scan.load_json`,
  `_code_fingerprints`→`_scan.code_fingerprints`, `_ratchet.<gitfn>`→`_ratchet_git.<gitfn>`)
  differ; git-seam defaults (`head="HEAD"`) preserved. 69/69 dup-ratchet tests pass.
- A moved reference could dangle (removed name still called, or a needed import missing).
  Checked: no residual `_inventory`/`_code_fingerprints`/`_doc_drift_signatures`/`_load_json`/
  `DOC_INVENTORY`/`FULL_SCAN_*`/`_ratchet.<gitfn>` references remain in the checker; removed
  imports (`subprocess`,`sys` in check; `subprocess`,`Path` in lib) are genuinely unused;
  new leaves carry every import they use. Reviewer confirmed by grep + compile.
- The split could rotate accepted clone fingerprints and mask authored duplication.
  Checked: the 2 rotated families (`bf2540d3`, `ccb81bdf`) are INTERNAL self-clones within
  `check_dup_ratchet.py` (`_evaluate_config`/`_write_baseline`/`_scoped_rebaseline` boilerplate
  + paired error-return dicts) — pre-existing accepted duplication whose shared span text was
  edited by the mechanical rename, so the content fingerprint legitimately rotated (the exact
  Slice-4 "real span-content change rotates" behavior). Scoped `--accept-family` gives a +2/-0
  baseline diff; the split authored zero NEW duplication. Verified by fingerprint set-diff and
  independently by the reviewer running the collector.
- Test monkeypatches could target the wrong module and silently no-op. Checked: patches now
  target `scan._inventory`/`scan._nose_report`, the same objects `scan.scan_code_fingerprints`
  resolves at call time; reviewer confirmed the patches take effect (tests still exercise the
  degrade/skip arms).
- Moving attention-state-emitting code could leave the declared visibility surface stale
  (the caught regression). Checked: the `skipped` state moved from check to scan; the
  `attention-state-visibility.json` declaration was updated (drop `skipped` from check, add a
  `dup_ratchet_scan.py` entry) and `validate_attention_state_visibility.py` passes (89 files).

## Counterweight Pass

- Real work folded now: two WARN-band files given real headroom (check 107 lines, lib 21) via
  cohesive leaf modules (`dup_ratchet_scan` = "world → identity sets"; `dup_ratchet_git` =
  "git stagnation seams"), a one-way dependency direction, and a stale-declaration regression
  found-and-fixed. Net a cleaner engine, not reactive churn.
- Deliberately NOT pursued (kept deferred, evidence-backed): S4-Defer-1 (token/comment-aware
  normalization) and S4-Defer-3 (subset-aware reduction diff) — the triage found their reopen
  triggers unmaterialized, so building them "because the engine is open" is the over-build the
  Slice-4 critique explicitly rejected. Also not pursued: lever D (accepted-corpus shrink) and
  pruning the pre-existing baseline slack (25 removed-but-still-baselined fingerprints) — a full
  `--write-baseline` prune would conflate 23 unrelated stale entries into this commit and
  re-accept unreviewed families; the additive scoped `--accept-family` (+2, attributable) is the
  honest minimal path the docstring prefers for routine rotation churn.
- Pre-existing failure disclosed, not fixed here: `test_standing_test_economics_summary_omits_
  full_nested_cli_list` fails on clean `HEAD` too (proven via `git archive HEAD`) — the machine's
  pytest temp-dir footprint emits an extra `pytest_temp_footprint` finding. Environmental,
  independent of this change, out of scope.

## Structured Findings

- F1 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/dup_ratchet_scan.py:1 | action: document | note: pure move — every extracted body byte-identical to HEAD; only mechanical call-site renames differ; 69/69 tests pass
- F2 | bin: over-worry | evidence: strong | ref: skills/public/quality/scripts/check_dup_ratchet.py:56 | action: document | note: wiring complete — `_scan`/`_ratchet_git` loaded, no dangling removed-name references, dead imports dropped
- F3 | bin: bundle-anyway | evidence: strong | ref: charness-artifacts/quality/dup-ratchet-baseline.json | action: fix | note: 2 internal-boilerplate fingerprints rotated by the rename touching accepted cloned spans; scoped --accept-family (+2/-0), zero authored new duplication
- F4 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/references/attention-state-visibility.json:53 | action: fix | note: caught + fixed the moved-code stale-declaration regression (skipped state relocated to dup_ratchet_scan.py); validator passes
- F5 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/spec/boy-scout-dup-ratchet.md | action: defer | note: S4-Defer-1/-3 kept deferred — reopen triggers unmaterialized per triage; batching them would be the rejected over-build
- F6 | bin: valid-but-defer | evidence: moderate | ref: tests/quality_gates/test_standing_test_economics.py:104 | action: defer | note: pre-existing env failure (pytest_temp_footprint), reproduces on clean HEAD, out of scope

Fresh-eye satisfaction: parent-delegated — a bounded fresh-eye subagent (general-purpose,
id ada069eb2537d2392) adversarially reviewed the STAGED diff across all five requested angles
and returned SHIP with only one cosmetic nit (a stale `dup_ratchet_lib.py` docstring TITLE
still listing "git seams"), which was then fixed and re-synced. Each angle was CONFIRMED by
execution (byte-compare vs HEAD, grep for dangling refs, running the fingerprint collector,
running the attention-state validator). The shipped change is what it reviewed plus the nit fix.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye subagent in a different agent context, adversarial, read-only in the shared parent worktree
- Requested spawn fields: the full staged diff scope, the module-split claim, and five adversarial angles (behavior preservation, wiring completeness, test fidelity, attention-state declaration, mirror byte-identity)
- Host exposure state: applied
- Application state: host-confirmed: subagent ada069eb2537d2392 ran to completion and returned verdict SHIP with per-angle commands and observations
