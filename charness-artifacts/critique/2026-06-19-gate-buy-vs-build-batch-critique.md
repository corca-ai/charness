# Critique Review
Date: 2026-06-19

- **Target:** `references/code-critique.md`
- **Execution:** parent-delegated bounded fresh-eye subagents (4 angles + 1
  separate counterweight), read-only in the shared parent worktree.
- **Packet Consumed:** `charness-artifacts/critique/2026-06-19-015230-packet.md`
  (sections: changed-files-and-owning-surfaces, non-goals).

## Decision Under Review

The unpushed batch `git log --oneline origin/main..HEAD`: gate buy-vs-build (#390
bootstrap-shim convergence A; B triage; B DROP #1/#2 demotions; ①
validate_critique_packet DELETE; ③ function-length -> ruff PLR0915; ④ doc
near-dup -> nose Markdown advisory + nose REQUIRED >=0.13.0) plus find-skills
repo-only regen. Operator held the push; this critique decides what must change
before that push.

## Failure Angles

- **Jackson (problem framing):** does each delete/demote let a class of wrong
  answer escape, or is "buy" honestly equivalent? Verdict: disciplined — every
  demotion targets a reversible in-session surface; none guards an irreversible
  boundary. PLR0915 swap and #390 convergence both survived direct scrutiny.
- **Weinberg (diagnostic):** are the swaps behaviorally equivalent? Verdict:
  PLR0915 vs old AST gate is faithful parity (current max 74 statements < 80;
  `charness` CLI per-file-ignore matches the prior unglobbed exemption); #390
  convergence preserves per-skill behavior; mirrors byte-identical; tests cleaned
  and new gates covered.
- **Gawande (operational):** new required dependency + silent-failure modes.
  Surfaced C1 + C2 (below).
- **Minto (structure/legibility):** decision trail reconstructable? Yes, except
  the stale handoff (C4).

## Counterweight Pass

Skeptical senior triage confirmed C1 as a real escape (not just a confusing
message): the counterweight found `doctor_lib.py:228` whitelists version status
`unknown` as a *pass*, so the unparseable constraint made `charness doctor
--tool-id nose` report `ok` for any nose — a wrong answer escaping the very gate
meant to give it. C2 downgraded to bundle (advisory surface). C3/C5 confirmed
genuinely out-of-scope/deferred; C6 over-worry.

## Structured Findings

<!-- bin: act-before-ship | bundle-anyway | over-worry | valid-but-defer; evidence: strong | moderate | weak | contested; action: fix | file-issue | document | defer -->
- F1 | bin: act-before-ship | evidence: strong | ref: integrations/tools/nose.json:58 | action: fix | note: version_expectation.constraint was prose not a PEP440 specifier -> InvalidSpecifier -> status unknown -> doctor reports ok for any nose incl 0.12.x, nullifying the batch's require->=0.13.0 intent. Fixed to ">=0.13.0"; verified 0.12.5->mismatched, 0.13.0->matched.
- F2 | bin: bundle-anyway | evidence: strong | ref: skills/public/quality/scripts/inventory_doc_duplicates.py:332 | action: fix | note: --require-nose failed closed only on missing/version-too-old; a present-but-broken nose (error status) returned exit 0, contradicting the degradation contract. Added "error" to the fail-closed set + help text + an error-path test.
- F3 | bin: bundle-anyway | evidence: strong | ref: docs/handoff.md | action: fix | note: stale hardcoded "6 commits" and an already-resolved find-skills Discuss item; refreshed to point at the live git command and mark the decision resolved.
- F4 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_integrations.py | action: defer | note: validator does not reject an unparseable constraint under a non-advisory policy, so it could not catch C1; recurrence-prevention follow-up, not a ship blocker.
- F5 | bin: valid-but-defer | evidence: moderate | ref: .githooks/pre-push:60 | action: defer | note: docs-only pre-push runs no doc-dup check (old removed, new advisory not added — intentional); a docs-only near-dup gets no signal until the next broad run. Folded into item 5.
- F6 | bin: over-worry | evidence: weak | ref: charness-artifacts/audit/2026-06-19-gate-buy-vs-build-decisions.md | action: defer | note: B DROP #1/#2 rationale lives in the triage doc + commit message, not the decisions companion; git-traceable and the docs are a designed pair.

## Deliberately Not Doing

- C3 validator hardening and C5 docs-only doc-dup re-add are deferred (C5 ->
  item 5). C6 split-brain left as-is (git-traceable).
- No `--read-only` find-skills routing change: the artifact write is idempotent
  on unchanged content, so repo-only canonical already ends the per-session drift.

## Reviewer Tier Evidence

<!-- Host exposure state: pending-parent-spawn | requested_fields_sent | metadata-hidden | host-defaulted | unsupported | applied -->
- Requested tier: high-leverage (`.agents/critique-adapter.yaml` reviewer_tiers.high-leverage)
- Requested spawn fields: model gpt-5.5, reasoning_effort medium, service_tier priority
- Host exposure state: unsupported
- Application state: this host's Agent-tool spawn surface exposes a model enum of sonnet/opus/haiku/fable only; gpt-5.5, reasoning_effort, and service_tier are not selectable, so the 5 reviewers ran as general-purpose subagents on the inherited host-default model (Opus). Tier fidelity not achievable on this host.

## Fresh-Eye Satisfaction

parent-delegated — 4 angle subagents + 1 separate counterweight subagent each
returned independent triage; the counterweight independently caught the
`doctor_lib.py:228` whitelist that escalated C1 from defer to act-before-ship.

## Next Move

Batch is push-ready post-fix (operator still holds the push decision). Proceed to
item 5 (boy-scout dup ratchet + advisory-review), which also owns the C5 re-add.
