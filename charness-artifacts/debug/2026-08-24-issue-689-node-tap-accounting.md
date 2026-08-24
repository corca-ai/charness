# Issue #689 Node Tap Accounting Debug
Date: 2026-08-24

## Problem

`mutate_and_restore.py` cannot earn baseline accounting for a green `node --test`
run when its pytest reader sees TAP (`# pass N`). Issue #689 is OPEN;
`gh issue view 689 --repo corca-ai/charness --comments --json
number,title,body,comments,state,author,labels,url` returned
`state: OPEN`, `comments: []`.

## Capability Failure

JTBD (verbatim issue body): “None of them can use this harness, so `ceal` grew a
repo-local equivalent (`scripts/prove-guard.ts` plus `config/guard-proofs.json`).”
Also verbatim: “The repo-local harness reimplements the same three properties this
one has — green-baseline check, exactly-one-site mutation, and snapshot-verified
restore with a durable journal — so the divergence is duplication rather than a
different idea.” The failed capability is portable mutation proof for a Node repo
without forking the accounting/restore contract.

## Correct Behavior

Given a green Node TAP run, when the plan selects a Node reporter, then the
harness must surface the reported baseline count, classify a named failing
mutation, restore bytes, and return structured YAML; a default/mismatched reader
must refuse without blaming the tree.

## Observed Facts

- `node --test` on the repository’s real fixture returned `0` and emitted `# tests
  2`, `# pass 2`, `# fail 0`, `# duration_ms ...`.
- Exact end-to-end fixture command: `python3 -m pytest -q
  tests/quality_gates/test_mutation_test_reporters.py -k
  'node_repository_gets_a_real_verdict or mutated_node_file_is_restored or
  default_reporter_still_refuses_a_node_tree or module_breaking_mutant_is_refused_not_killed'`
  -> `4 passed, 38 deselected`.
- The raw fixture readback (helper lines `190-243`) was: default reporter exit
  `2`, `baseline.earned: false`, `returncode: 0`, refusal “pytest reporter found
  no readable count report”; explicit `"reporter": "node-test"` exit `0`,
  `baseline: 2 passed`, `killed: 1`, and the restore/non-Python call-site
  non-claim. The baseline was green; only its reader was wrong.
- Current HEAD already contains prior #689 seam work (`ff0f5292`, `10f1a092`);
  this phase changed no source, issue, or Ceal file. Source/plugin reporter and
  harness copies have identical SHA-256 bytes.
- `python3 -m pytest -q tests/quality_gates/test_mutation_test_reporters.py` ->
  `42 passed`; `python3 -m pytest -q
  tests/quality_gates/test_mutate_and_restore.py` -> `58 passed`.
- In `/home/hwidong/codes/ceal`, `npm run test:prove-guard` -> exit `0`; its
  temporary fixture reported both `proved` and `mutation_survived`, with byte
  restore. `npm run lint:guard-proof-manifest` -> exit `1`: one real Ceal proof
  (`client-manifest-dependency-pin`) has `find` matching `0` sites. This is a
  separate Ceal manifest-drift finding, not evidence against #689.
- `rg -n 'mutate_and_restore|mutation_test_reporters' scripts package.json
  config docs` in Ceal found no runtime wiring; only documentation/comments.

## Reproduction

Source: `python3 -m pytest -q tests/quality_gates/test_mutation_test_reporters.py`
reproduces both default refusal and explicit Node success in temp repositories.
The Node producer and Charness consumer are therefore locally reproduced.
Ceal: `npm run test:prove-guard` reproduces its own final consumer contract in
temp repositories; `npm run lint:guard-proof-manifest` reproduces its current
source/manifest refusal without mutating the checkout.

Rejected diagnostic evidence: direct test-file import failed with Python’s
relative-import error; the corrected package import first reused the fixture
directory and failed `FileExistsError`; `npm run lint:guard-proof` was an
unsupported script. These failures exposed command/fixture ownership mistakes;
they were not counted as behavioral proof. The owned script name came from
Ceal `package.json` and was then run once.

## Candidate Causes

- Node/dependency/environment failure: disconfirmed; `node --test` exited `0`.
- TAP/spec/TTY variation: contributing compatibility risk; TAP is the observed
  output, while current code deliberately refuses `spec` because it lacks the
  file-level failure signal (`mutation_test_reporters.py:78-100,161-181`).
- Parser coupling/missing reporter contract: confirmed by the same bytes being
  unreadable to `PytestReporter` but readable to `NodeTestReporter`.
- Ceal-only test or restore defect: disconfirmed for the local fixture; its
  focused contract suite passes and restores bytes.

## Hypothesis

The structural hypothesis is: the accounting invariant was runner-independent,
but the reader was hardcoded to pytest’s `N passed in Ns` line
(`mutation_test_reporters.py:70-158`), so Node’s separate TAP block became an
unreadable green baseline (`mutate_and_restore.py:188-214`). Cheapest
disconfirmer: run one identical Node fixture through the default and selected
reporters. Result: confirmed; only the selected reporter earns the baseline.

## Verification

The hypothesis is confirmed, not merely inferred from source: the real fixture
produced exit `0` with TAP, default Charness returned exit `2` with
`returncode: 0`, and `node-test` returned exit `0` with `2 passed / 1 killed`.
The module-breaking mutant is refused, not killed, by the current Node tests
(`test_mutation_test_reporters.py:409-426`).

## Root Cause

Five whys: (1) baseline accounting was `None` because the pytest reader found no
summary (`mutate_and_restore.py:192-211`); (2) that reader requires a duration-
and-count line (`mutation_test_reporters.py:72-76,126-158`); (3) Node emits a
trailing TAP block instead (`mutation_test_reporters.py:9-20`); (4) the original
contract had no runner-reporting adapter, so a healthy Node tree looked like an
unreadable tree; (5) Ceal had to duplicate the proof loop, documented at
`/home/hwidong/codes/ceal/docs/implementation/quality-gates.md:476-485`.
Structural bottom: missing reporter-format contract at the accounting boundary,
not a Node test failure or human error.

## Invariant Proof

- Invariant: when the Node test producer emits TAP counts, the reporter -> plan
  transport -> Charness YAML consumer must preserve count, mutation verdict, and
  restore evidence before claiming success.
- Producer: real `node --test` emitted the TAP block above.
- Signal/transport: `reporter: node-test` selects `NodeTestReporter`; `run_sweep`
  emits the baseline and structured YAML (`mutate_and_restore.py:389-412,433-459`).
- Final consumer: the raw Charness payload read `earned: true`, `passed: 2`,
  `killed: 1`; Ceal’s separate final consumer read its own proof outcomes in
  `test:prove-guard`.
- Non-claims: Ceal is not wired to consume Charness output; Ceal-cli/agent,
  installed caches, real host TTY/spec selection, and provider roundtrips were
  not proven.

## Detection Gap

- Existing pytest-only harness tests did not fire on Node output. Smallest
  firing change: one real `node --test` fixture asserting `# pass` accounting and
  exit/restore (`test_mutation_test_reporters.py:190-285`).
- Count-only Node tests would miss module-breaking false kills. Smallest change:
  assert file-level `exitCode` becomes `errors`, yielding refusal
  (`test_mutation_test_reporters.py:409-426`).
- No adoption gate detects a consumer fork. Smallest outside-slice change: a
  Node consumer portability/adoption probe that reads the selected reporter and
  final payload. Ceal’s manifest drift is separately detected by its existing
  `lint:guard-proof-manifest`.

## Sibling Search

Mental model: a proof surface treats one runner’s human-readable output as the
universal accounting interface, forcing consumers to fork when formats differ.

- same layer: `scripts/mutate_and_restore.py:389-412` and its Node fixtures |
  decision: same bug, fix now | proof: local payload proof.
- specialization down: `scripts/mutation_test_reporters.py:161-252` and
  `tests/quality_gates/test_mutation_test_reporters.py:469-491` (TAP vs `spec`)
  | decision: same class, diagnostic-only for this slice | proof: local payload proof.
- abstraction up: `scripts/check_js_mutation_score.py:51-89,205-229` reads
  structured Stryker JSON, not runner text | decision: intentional plain-text or
  non-rendering boundary | proof: static scan only.
- mental-model sibling, cross-file: `/home/hwidong/codes/ceal/scripts/prove-guard.ts:40-52,209-259`
  and `config/guard-proofs.json:1-11` duplicate the mutation/restore contract |
  decision: valid follow-up outside the slice | proof: local payload proof |
  follow-up: deferred `docs/handoff.md` Current State.

## Seam Risk

- Interrupt ID: issue-689-node-tap-accounting-2026-08-24
- Risk Class: external-seam, repeated-symptom
- Seam: runner output -> reporter -> structured payload -> consumer/adoption fork
- Disproving observation: same Node fixture accepted by explicit `node-test` and
  refused by default; this rules out “Node is red,” not the seam defect.
- Local reasoning cannot prove the two sibling repos, installed-host behavior,
  or a real TTY-selected reporter.
- Generalization Pressure: factor-now

## Interrupt Decision

- Resolution: open
- Critique Required: yes — separate causal reviewer before repair
- Next Step: spec
- Handoff Artifact: `charness-artifacts/debug/2026-08-24-issue-689-node-tap-accounting.md`

## Prevention

Keep runner-independent accounting in one shared classifier, but make report
formats explicit adapters with producer fixtures and final structured-payload
assertions. Add a consumer adoption probe before claiming fork retirement. Do not
close/comment/push #689; the source repair in HEAD still needs causal review and
consumer proof.
