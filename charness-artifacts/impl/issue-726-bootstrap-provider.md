# Issue #726 Minimum Bootstrap Provider Slice

Status: implementation in progress
Contract: `charness-artifacts/specs/adversarial-priority-backlog-closeout/phase-00-issue-native-achieve-tracking/children/goal-run-provider.md`

## Slice Boundary

Implement and prove only the create/read/update/list/add/remove provider
mechanics needed to establish the existing #724 Goal Run graph. Full target
`goal-run-*` orchestration, guarded close, `/goal` pickup, and concurrent-human
editing remain later slices.

## Observed Failure And Structural Repair

During read-only live proof, the operator command manually repeated 29 expected
child numbers and used a stale, unrelated set. The provider correctly returned
`graph-mismatch`; GitHub had not drifted. The immediate typo exposed a broader
pattern: a durable approved manifest existed, but the verification boundary
made the caller transcribe it into another representation.

The repair is source-bound input, not a corrected hand-written command:

- `list-sub-issues --expect-child-file` consumes one strict, target-bound JSON
  set and reports its complete-byte SHA-256;
- manual repeated flags and the file are mutually exclusive;
- duplicates, unknown fields, malformed JSON, and repo/parent mismatch refuse;
- the current approved pre-mutation graph lives at
  `charness-artifacts/goal-runs/724/bootstrap-existing-graph.json`;
- future reconciliation generates the next set from the same binding/plan owner
  instead of reconstructing it in shell arguments.

Pattern of pattern: whenever an external mutation or verdict already has a
durable source record, the executing command consumes that record or a
hash-bound projection owned by the same producer. Human re-encoding is not an
acceptable integration seam.

## Evidence So Far

- Focused provider/skill suite: 115 passed before the source-bound repair.
- Focused provider/skill suite after the repair: 116 passed.
- Live provider preflight: ready, exact `corca-ai/charness#724`, eight required
  templates rendered, no mutation.
- Live graph read: exact approved 29-child current graph after correcting the
  input, then exact equality through the source-bound file with input SHA-256
  `4be278a5f2bad6325f64e8ee968e0906fc7f1f6d4a8f38e2a3f69ce780978f2d`;
  the earlier mismatch is retained above as design evidence.

No GitHub write has occurred in this slice yet.

## Review-Rail Failure And Structural Repair

The first file-backed review attempts produced valid terminal worker receipts,
but their run directory was Git-visible. The boundary fingerprint therefore
reported the worker's own required result/log files as worktree drift. Both
reviews were quarantined before their findings were read and their delivery
ledgers were terminated as `collection-failed`.

This is the same higher-order class as the manifest transcription failure: a
proof mechanism must not require callers to duplicate or accidentally pollute
the state that mechanism judges. The repo already owns the ignored
`.charness/critique/` runtime surface, so retries use that canonical path while
durable findings alone belong under `charness-artifacts/critique/`. The failed
attempt bytes are preserved under the ignored runtime tree; they are evidence
of the setup failure, not approval evidence.

The first ignored-path retry exposed a second rail defect. The low-level
`reviewer_delivery.py start` example in the operating reference did not bind
the worker output path, receipt path, or producer run id even though
`reviewer_worker_report.py` requires all three. The workers and boundary checks
succeeded, but collection correctly refused approval. This was not repaired by
editing the ledgers. The canonical `run_reviewer_worker.py` already owns the
complete launch/collection transaction, so the reference now names that one
runner and explicitly forbids assembling the three low-level commands as a
shell workflow. Canonical retries produced provenance-valid, schema-valid,
`collection_ready: true` findings.

Pattern of pattern: when several low-level proof primitives exist, operator
documentation names the transaction owner, not a plausible-looking subset of
the primitives. A state machine that can only be completed by hidden library
arguments is not a valid shell protocol.

## Round 1 Critique Disposition

Two independent angles and one separately delivered counterweight all remained
read-only and passed clean reviewer-boundary verification. The counterweight
retained these before-ship repairs:

- a prior ambiguous create needed an enforceable cross-attempt interlock;
- an explicitly empty expected child set was conflated with no expectation;
- malformed, duplicate, or foreign-version Goal Run metadata could bypass the
  already-current path;
- malformed alternate-backend format grammar could escape typed preflight;
- the packet omitted contract inputs used by reviewers and had to be rebuilt
  from stable repaired bytes;
- closeout must retain exact operator commands and observation/readback paths.

The implementation now uses immutable provider observations as the create
interlock key `(repo, parent, Work Item key)`. Submitted body SHA remains
comparison evidence but cannot change the logical Work Item identity. A later
attempt may perform exhaustive discovery and reuse the exact issue, but it
cannot invoke create again while a matching started-only or unverified-write
receipt remains unresolved. Exact-set presence is tracked independently from
cardinality. Goal Run metadata is parsed before idempotent success. Backend
templates are parsed with Python's format grammar and normalized into typed
preflight errors. The provider's open-child next action now returns state to the
lifecycle policy owner instead of prescribing transfer policy.

Guarded close, `/goal` pickup, concurrent editing, and complete `goal-run-*`
orchestration remain outside this slice.

## Repaired Evidence

Focused command (154 passed after compatibility and architecture repairs):

```text
python3 scripts/run_standing_pytest.py --repo-root . --mode read-only --pytest-target tests/quality_gates/test_issue_tracker.py --pytest-target tests/quality_gates/test_issue_tracker_observation.py --pytest-target tests/quality_gates/test_issue_tool_runners.py --pytest-target tests/quality_gates/test_issue_preflight.py --pytest-target tests/quality_gates/test_issue_create.py --pytest-target tests/quality_gates/test_issue_skill.py --pytest-target tests/quality_gates/test_reviewer_delivery_integration.py --pytest-target tests/quality_gates/test_reviewer_worker_report.py
```

Live read-only preflight command (ready, exact OPEN parent, all eight operations,
no template errors):

```text
python3 skills/public/issue/scripts/issue_tool.py tracker-preflight --repo corca-ai/charness --number 724 --repo-root .
```

Live source-bound graph read command (verified-read, 29 exact children, 3
closed, 26 open, no missing or unexpected identities):

```text
python3 skills/public/issue/scripts/issue_tool.py list-sub-issues --repo corca-ai/charness --number 724 --expect-child-file charness-artifacts/goal-runs/724/bootstrap-existing-graph.json --repo-root .
```

The graph source SHA-256 remains
`4be278a5f2bad6325f64e8ee968e0906fc7f1f6d4a8f38e2a3f69ce780978f2d`.
These two reads are transcript-carried evidence and perform no mutation;
immutable started/terminal receipt paths will be recorded beside each later
bootstrap write rather than fabricated for read-only commands.

Round-1 delivered runtime carriers are retained under ignored paths:

- `.charness/critique/issue-726-r1-canonical/{recovery,integration}-{delivery.json,result.json,receipt.json,report.yaml}`;
- `.charness/critique/issue-726-r1-counterweight/{delivery.json,result.json,receipt.json,report.yaml}`.

Their findings identities are respectively
`e503df7e4cbb2f47dc91880be60d1502ce8927099b0a9706d58f5631d2371c5f`,
`8dafd7788220e2cd4e6df6664e001def06db7446c7b540bd443a5711efc99dfe`,
and `ec33af55450cb93b582ce1ed651736d264a846293de4d87d873ce518eaa394fa`.

## Round 2 Cap

The first round-2 delivery failed schema collection because the prompt asked
for ordinary non-claims without assigning the similarly named
`capability_non_claims` field to the launch envelope. The worker synthesized a
capability non-claim even though no external read capability had been requested.
The result was not read. A single retry fixed the prompt contract by reserving
ordinary limits for `non_claims` and copying the envelope-owned empty capability
list and hash exactly. The retry passed receipt, provenance, schema, collection,
and reviewer-boundary checks.

Pattern of pattern: semantically adjacent fields owned by different producers
must be assigned explicitly in the prompt. Schema validity alone cannot tell a
reviewer which producer owns a value.

The delivered round-2 review found one remaining before-ship escape: using the
submitted body SHA as part of the unresolved-create lookup allowed a later body
edit to hide the first ambiguous write and invoke create again for the same
stable Work Item key. The final capped repair keys the interlock on repository,
parent, and Work Item key only, retains both body hashes as evidence, and adds a
two-attempt regression proving changed body bytes cannot increase the create
invocation count above one. Exact discovery recovery remains allowed.

Per the two-round cap, this repair is accepted-unreviewed and does not trigger a
third bounded round. The provenance-valid round-2 carrier remains under
`.charness/critique/issue-726-r2-retry/`; findings identity
`04e076bfb989930e7211ce77aa708a16a8edd17b7a0c4a644e89d15fa2699c78`.

## Closeout-Gate Friction And Structural Repair

The first pre-commit pass exposed three provider files beyond the repository's
360-code-line hard limit. Extracting only the reported long function would have
left each entrypoint at the advisory boundary and preserved the same accretion
pattern. The repair instead assigns one question to each module: provider
identity, command rendering, JSON pagination, capability closure, Work Item
discovery, relationship mutation, unresolved outcomes, Goal Run domain rules,
tracker orchestration, tracker argument grammar, milestone policy, and top-level
command composition. Every resulting module is below the advisory band, and
the established `issue_tool`/`issue_tracker` names remain compatibility facades.

The refactor also exposed tests patching facade globals while the behavior lived
in a newly extracted owner module. Those tests accidentally reached the live
provider instead of their fake and returned the real 29-child graph. Tests now
patch the owning relationship module, making the observation boundary explicit.
The source-capture consumer also revealed that `PLACEHOLDER_RE` was a consumed
backend export; it remains a compatibility export while command parsing stays
owned by `issue_backend`.

Separately, the first final-packet refresh passed a literal `\\n` between paths,
so all reviewed paths became one invalid path. The prepare runner refused before
writing. The successful retry enumerated the packet's JSON array directly. This
is the third instance of a valid manifest being manually translated into repeat
CLI flags; a source-bound repeated-argument wrapper belongs in the later
orchestration slice rather than another remembered shell recipe.

Test execution also creates plugin `__pycache__` files that the manifest sync
then removes. That generated-surface pollution is not part of provider behavior,
so it is retained as a later Goal Run hygiene Work Item rather than hidden or
mixed into this slice.
