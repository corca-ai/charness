# north-star P1-P3 sweep (branch north-star-p123)
Date: 2026-07-04

## Decision Under Review

One PR implementing 24 counterweight-verified north-star findings (one more, the
test-production-ratio deletion, was cancelled by the operator mid-run): P4/P5 floors at
issue-close/release/critique/announcement/deletion boundaries, P1 teeth removal on
reversible surfaces, and P2/P3 concept separation across skill bodies — 93 tracked files
±1900 lines plus 14 new files, built by 14 parallel bounded implementation subagents.

## Failure Angles

- Boundary floors that look closed but are bypassable (the #386 class re-created inside
  the fix): probed adversarially by a dedicated reviewer per floor.
- Pinned-string / eval / claim-fidelity / generated-mirror couplings broken by the prose
  moves: probed by a coupling reviewer with live test runs (~4,100 executions).
- North-star misapplication by the sweep itself (displaced overflow, deleted protection,
  count-as-metric claims) and operator-input violations (test/prod ratio, length caps):
  probed by a fidelity reviewer against the gathered operator reference.

## Counterweight Pass

- Real blockers (all fixed in-branch before commit): scaffold default `parent-delegated
  (TODO …)` satisfied the new fresh-eye floor by prefix match; `Closes: #N` colon form
  escaped both close-keyword regexes; announcement `--delivery-kind` was self-attested
  with no choices/adapter cross-check; `question` classification exempted every floor on
  caller say-so; reviewer-brief doc-link failure; fail-open-vs-fail-closed design mismatch
  in the undatable-artifact tests; release CLI hard-crashed when the issue skill is absent;
  audit artifact carried a false "B-side still advisory" claim with fake confidence.
- Over-worry (accepted, not folded): same-proxy probe evasion via wrapper scripts (form
  check by design; rung-2 reviewer still sees the literal command); bidirectional
  delivery-kind equality (would break legitimate draft-only finalization); nested-delegated
  downstream evidence-linking (acknowledged in-code as an accepted gap, its own
  floor-addition call).
- Deflation recorded honestly: the "mutation_testing block duplicated across quality
  references" finding was overclaimed — only the standing_doc_provenance pair was truly
  circular; the sibling block was already one-directional and was left in place.

## Structured Findings

<!-- allowed enums (substitute only these) — bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer. action: file-issue also needs a follow-up: (issue URL or 'deferred ' plus a handoff anchor). -->
- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/critique/scripts/scaffold_critique_artifact.py | action: fix | note: unedited scaffold stub passed the new fresh-eye typed-presence floor by prefix match; fixed (TODO-remainder rejection + non-typed stub + fail-closed undatable with 2-name legacy allowlist) and proven by test_critique_scaffold_default_stub_fails_validation_post_cutoff.
- F2 | bin: act-before-ship | evidence: strong | ref: scripts/check_issue_closeout_commit_msg.py | action: fix | note: GitHub-documented `Closes: #N` colon form and single-keyword comma lists escaped the bare-close floor; fixed by a single deduplicated scanner (iter_close_keyword_refs) used by both the hook gate and the closeout verifier.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/announcement/scripts/record_announcement.py | action: fix | note: --delivery-kind was free text so any non-"human-backend" string skipped delivery verification; fixed with choices+normalization, adapter cross-check (human-backend mismatch refuses), and reason-required non-confirmed statuses.
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_close.py | action: fix | note: question/decision-needed classification exempted all floors on caller say-so; bare-close path now honors only an explicit Classification: line (defaults to bug) and close-with-comment emits a REVIEW advisory naming the exemption.
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/release/scripts/release_issue_closeout.py | action: fix | note: module-scope cross-skill import crashed the whole release CLI on installs without the issue skill; fixed with the plan_handoff_run try/except degrade — non-closing commands work, --close-issue refuses with a typed missing-capability message.
- F6 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/audit/2026-07-04-gate-reclassification.md | action: fix | note: audit carried a false high-confidence "check_python_lengths B-side still --advisory" claim (transient sibling-wave state read as settled); corrected with git-diff/git-log evidence inline and the miss named explicitly.
- F7 | bin: act-before-ship | evidence: strong | ref: skills/shared/references/disposition-reviewer-brief.md | action: fix | note: backticked doc path failed check_doc_links; converted to a markdown link, whole-repo doc links green.
- F8 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_critique_artifacts.py | action: document | note: nested-delegated has no downstream evidence-linking check; recorded in-code as an accepted gap — promoting it is a separate floor-addition-restraint decision.
- F9 | bin: valid-but-defer | evidence: moderate | ref: charness-artifacts/audit/2026-07-04-gate-reclassification.md | action: defer | note: combination gaps vs the operator-endorsed toolset (vulture configured but never wired as a gate; 81-site argparse-help debt across 24 files) are recorded in the audit Follow-ups for their own slices.
- F10 | bin: over-worry | evidence: weak | ref: skills/public/release/scripts/publish_release_post_create.py | action: defer | note: same-proxy probe detection is a token-prefix form check and evadable via wrapper indirection; by design — it forces the question, and the rung-2 reviewer sees the recorded command string.

## Reviewer Tier Evidence

<!-- allowed Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied. Use applied only with Application state: host-confirmed: plus a concrete signal. -->
- Requested tier: three parallel bounded fresh-eye reviewers (boundary-adversarial, regression/coupling with live pytest, north-star/operator fidelity), distinct contexts from the implementing agents.
- Requested spawn fields: subagent_type=general-purpose, model=sonnet, read-only mandate (no edits, no worktree-mutating git), per-angle briefs with file evidence.
- Host exposure state: applied
- Application state: host-confirmed: three reviewer completion reports returned with independently-run test evidence (2542-passed broad run, defeat proofs with regex reproductions, git-log falsification of the audit claim); fixes from those reports landed and re-verified before commit.

## Fresh-Eye Satisfaction

parent-delegated — three angle reviewers plus per-fix re-verification ran as separate subagent contexts spawned by the orchestrating parent; no same-agent pass was counted as review.
