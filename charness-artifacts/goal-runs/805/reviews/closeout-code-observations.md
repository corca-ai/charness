# Closeout carrier code observations

Date: 2026-09-06

## Pending boundary

Issue #810's living contract owns exact packet/result/citation membership and
per-target classification. The integrated working-tree diff against `23a9eaa6`
implements that contract; it does not publish, close issues, or claim semantic
truth from schemas. Shared support returns already-verified evidence; only the
issue owner interprets issue identity. Existing singleton migration and delivery,
source, result and parent identity checks remain required.

Two isolated implementation attempts timed out and were not approval-eligible.
The parent recovered candidate `1d02e11a168bb7d480d86cdbbd0d9f395edd4258`
in a disposable checkout, inspected its production diff and composed tests, and
adopted the reviewed source changes explicitly. No timed-out task receipt is
promoted to successful implementation evidence.

## Parent reproduction and repair

The candidate's hook had a second targeted-classification parser. A dict
projection erased duplicate declarations before the issue owner could reject
them; a global declaration alongside targeted ones was also lost. The test
`test_artifact_classification_conflicts_cannot_be_erased_by_hook_projection`
reproduced four false greens: duplicate and mixed authority, each through
commit-msg and independent pre-push. All four failed their expected-refusal
assertions before repair (3.12s). In the duplicate case, overwriting bug with
feature even avoided the bug's required critique.

The repair deletes the hook parser and delegates the complete artifact body to
`resolve_classifications`, the existing issue-owned authority. Both hook callers
pass that owner explicitly; the legacy helper entry resolves it only when needed.
The parser rejects ambiguity before projection. The four negative cases then
passed alongside the relevant hooks: 129 tests in 5.07s. On the integrated parent,
the wider closeout/worker/semantic-producer selection passed 190 tests in 6.80s.
The valid composed fixture independently passed before and after this repair:
one delivered two-target review and one citation across mixed bug/feature groups,
through draft, commit-msg's staged-artifact input and pre-push. The initial test
did not execute the CLI or pause-to-close transition despite an earlier record
claiming that full list. Parent inspection caught the overclaim and added those
actual paths to the same fixture, plus removal of each group's distinct field
through the CLI, draft, hooks and pause transition. Initial CLI readback required
the assertion to account for serialized string dictionary keys; behavior passed.

The same detection-gap pattern is recorded in
`charness-artifacts/debug/2026-09-06-multi-issue-closeout-cardinality.md`:
isolated parser and singleton tests cannot prove a composed final consumer.

## Verification Scope Decision

Claim: exact source-bound bundled membership and each classification's existing
floor survive all closeout callers. Consumer closure: producer, shared carrier,
issue policy, grouped verifier, draft and both hook paths. Minimum proof:
composed passing delivery plus omitted/extra/duplicate/foreign/nonpassing target,
classification ambiguity and removed-floor refusals; focused old-singleton
regressions; independent code review and changed-line proof. Omitted here:
actual provider close, release, installed observation and four-arm comparison.
Those remain Goal #805 obligations. Failure classification for the reproduced
hook projection is subject-defect, not a test or infrastructure problem.

## Review questions

The integrity lens should test the three distinct scopes (invocation, full
citation, classification group), source/result/delivery binding and migration
refusals. The simplification lens should inspect duplicate ownership, repeat
parsing/verification, actual operator paths and the composed test's credibility.
Both should inspect changed verdict logic, not infer acceptance from these
observations. Do not widen into a global approval cache, new taxonomy or
semantic classification oracle. Code review is not final behavioral closeout.

## Parent counterweight before review

- Act Before Ship: fixed the reproduced lossy hook projection.
- Bundle Anyway: removed an unused normalizer argument and unreachable fallback.
- Over-Worry: no new registry, classifier, hash family or persistent review cache.
- Valid but Defer: publication/installed behavioral evidence and net-value pilot.

Fresh-Eye Satisfaction: pending code review.

## Strict-generation failure and bounded repair

The first code-review pair, `goal805-code-closeout-integrity` and
`goal805-code-closeout-simplicity`, stopped after 5.0s/5.2s with no model verdict.
The preserved backend error was `invalid_json_schema`: generation required
every property in `required`, but `target_observations` was optional. Both had
failure identity `2ba389a26d3ae33bb02bce7036c9843eb0156f2f4984dd85513ef3b459e0e5e2`.
They are invalid delivery evidence, not a blocking code opinion or approval.

The existing model-schema projection now marks semantic properties required;
the optional canonical field is nullable. Legacy omission/null remains absent,
while structured packets refuse either. All observations remain model-authored.
This follows the observed rejection and the
[strict Structured Outputs contract](https://developers.openai.com/api/docs/guides/structured-outputs#all-fields-must-be-required),
checked on this date. A regression walks the actual generation schema's object
properties/required equality, and final-consumer tests distinguish legacy null
from missing structured observations. The subject schema and projection changed;
the next review pair is a corrected-delivery run, not a third verdict round.

## Delivered code findings and repair boundary

The corrected pair delivered `block`, not runner failures. Both packets passed
the current-input verifier before edits: packet
`fa34224328206e2b8cced0e37cb55b5823d73af3bb31ab203fca58cadaa7154c`, input
`e937cfb093a8818346502aa8aea125b994b6fbd8ccfa2ab6dea1020c48d7f8f4`.
Carriers are `.charness/reviewer-round-goal805-code-closeout-{integrity,simplicity}-strict/worker-report.yaml`;
the delivered `result.json` siblings preserve the full findings.

- Act Before Ship: integrity I1 found artifact maps suppressing independently
  conflicting message authority; I2 and simplicity S2 found artifact partition
  narrowing the citation invocation. Simplicity S1 found each mixed group's
  singleton size granting unqualified Behavior to both issues. Integrity I3
  found foreign repository citation labels reduced to local issue numbers.
- Bundle Anyway: fake generation now emits only model-authored fields,
  including null observations, and checks exact required schema keys. Pre-push
  should retain critique refusal details. Two file-length failures require
  cohesive owner extraction, not waived limits.
- Over-Worry: preserve legacy null/omission and existing delivery/source joins;
  neither strict generation nor exact membership needs a semantic truth oracle.
- Valid but Defer: publication, installed observation and net-value pilot are
  still separate obligations, not closed by this code review.

Parent tests first reproduced S1 and I3 as three false greens (3 failed in
2.51s). The repair retains full invocation cardinality for Behavior/HOTL and
validates bare citation grammar before projection. Exact issue membership moved
to `issue_worker_targets.py`; artifact section parsing moved to the existing
observer support owner. Carrier-input validation moved to the existing carrier
owner, and classification authority to its ledger owner. These are local
ownership changes, not another generic helper framework. The initial repaired
bundle/worker/semantic selection passed 61 tests in 4.80s before the remaining
invocation repair and additional HOTL control were finalized.

The material verdict branches warrant one bounded follow-up after repair.
Neither initial block is approval, and the follow-up does not replace final
behavioral closeout or authorize publication by itself.

The invocation repair now joins active artifact and bare targets once in both
hooks, preserving per-target artifact sources and full verifier diagnostics.
The issue owner reconciles carrier declarations with artifact authority rather
than trusting a projected map. Independent implementation added 25 passing
partition/authority cases (3.08s); parent integration passed 202 existing and
bundled tests (5.18s), including genuine singleton migration, both hooks,
draft, strict-schema and worker evidence paths. Rung-1 HOTL preserves its existing
plural shorthand behavior and separately refuses an explicitly targeted untyped
entry. Ruff and all touched production length checks passed; remaining length
warnings concern cohesive observer composition and pre-push channel ownership,
not an unowned policy split.

## Follow-up disposition

The single bounded follow-up `goal805-code-closeout-repair` delivered pass with
no findings. Parent read the complete typed result and verified current packet
binding before integration. It independently exercised decisive counterexamples
and retained the original findings as repaired, not erased. Fresh-Eye
Satisfaction: worker-delivered, code review only.

- Report: `charness-artifacts/critique/workers/goal805-code-closeout-repair/worker-report.yaml`
- Packet: `5a3d04fee40579dcd13f39070c5b15a8995fb468b29f882b7f5672f7bb99fb06`
- Input: `91a61433bf4412a3b4839501d0850c4a05ec834c2cb2e7a4575158f6c1f8e0c9`
- Findings: `690e0e9281f700685230afac7ee5f8813185d60ff0ea37b11fa345051819235c`

An additional parent singleton/classification/floor/observer selection passed
96 tests in 2.94s. Public packet and issue references now expose the bundled
operator path without changing the release helper's separate scalar interface.
Targeted Markdown passed for five edited documents. An accidental Markdown CLI
invocation expanded to the repository-wide configured glob and was terminated;
that run is not a pass. Integrated changed-line and broad verification follow
the local code commit; publication and actual behavioral closeout remain open.

## Integrated changed-line tripwire

At `cff88adf6`, the coverage producer and standing suite passed in 127.0s and
121.9s, but the gate correctly blocked: nine changed lines across the hook,
classification owner and citation owner were unmeasured. Three additional
owners (CLI parser, carrier input and extracted worker targets) lacked direct
standing-test references and were explicitly unanalyzed. Neither population is
covered by those passing test processes.

Nine focused authority controls then passed in 2.17s. Before mutation, the
parent displayed the gate's exact blocking target
`skills/public/issue/scripts/issue_resolution_critique.py:67` (`return []` for
duplicate targets). Temporarily replacing that line with `return target_numbers`
made the duplicate-target control fail with `[42, 42] != []` (one failed, one
passed, 2.16s). The parent restored the exact line, verified an empty production
diff, and restored the generated export. This is target-bound mutant proof,
not a claim about every mutation or the still-pending coverage rerun.

An independent test-only supplement directly loads the three previously
unmapped owners. It exercises the real CLI composition, carrier validation,
and exact worker-target membership including legacy compatibility. Parent read
the complete test file and independently ran it with the nine authority
controls: 93 passed in 2.95s; Ruff passed. Production bytes remain unchanged.
