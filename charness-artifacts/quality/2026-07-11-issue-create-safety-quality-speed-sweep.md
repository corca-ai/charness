# Quality Review
Date: 2026-07-11

## Scope

Target boundary: active-goal Slices 0–2 — issue #433's release carrier seam,
artifact fresh-record/prepare-packet siblings, and the measured standing pytest
cost that should shape the next speed slice.

Ambient repo findings: pytest has 389 files and 146 standing files with nested
CLI sites, but those counts do not prove which tests are waste. The reproduced
artifact pointer and packet/session mismatches are now resolved.

## Current Gates

- The issue direct-commit draft validator owns ledger, critique, behavior, source,
  and provenance form checks; the commit-msg hook owns the final carrier gate.
- The release helper now reuses those semantics before quality and reuses the
  validated paragraphs at commit; resume separately validates the existing
  tagged `HEAD` body it will push.
- Maintainer-Local Enforcement: healthy — `.githooks/pre-push` selects the
  repo-owned read-only quality gate and `charness worktree doctor --json`
  reported configured hooks and overall `status=pass`.

## Runtime Signals

- runtime source: structured metrics from `.charness/quality/runtime-signals.json`
  rendered by `render_runtime_summary.py`; profile `local-linux-x86_64-36cpu`.
- runtime hot spots: pytest 30.9s latest / 32.5s recent median vs 140s budget;
  three matched pre-change samples were 30.68s, 30.66s, and 30.32s (median
  30.66s, spread 0.36s), all 4,469 tests passing.
- coverage gate: focused release/issue boundary tests ran; broad coverage and
  changed-line mutation coverage are reserved for the final verification lock.
- evaluator depth: deterministic-gates-only — no prompt/agent behavior claim
  needs Cautilus, and Cautilus remains ask-before-run.

## Healthy

- Exact-carrier proof now crosses four distinct boundaries: behavior presence,
  issue-owned draft schema, actual commit-msg acceptance, and seeded release
  commit assembly. The current focused bundle passed 72 tests in 22.55s.
- Source and installed plugin layouts have direct import coverage; generated
  release mirrors are synchronized from the public source.
- Standing gate output has quiet pytest/spec execution, structured phase signal,
  actionable failure replay, and a verbose escape hatch.
- Debug fresh investigations now emit a non-conflicting dated record and an
  executable current-pointer refresh; critique/retro prepare packets retain
  their pre-review kind without weakening completed-record floors. The composed
  parent suite passed 95 tests in 4.56s, and all current critique/retro records
  validate.

## Weak

- The legacy seeded-publish helper auto-injects a synthetic full bug carrier for
  unrelated close-issue tests. Explicit missing, thin, extra-close, feature,
  normal publish, and resume tests keep the new contract visible, but new tests
  must not rely on the injection when carrier behavior is their subject.
- The current broad quality result is not yet locked; focused green evidence is
  sufficient for this slice, not final-goal completion.

## Missing

- Live release/provider/installed-machine proof was not run and is not claimed;
  it remains an operator-approved external lane rather than a local gate gap.

## Deferred

- Broad sibling repair stays evidence-ranked: keyword matches alone do not earn
  changes. Classification parser consolidation reopens only on vocabulary change
  or another drift instance.
- Worker-count tuning, broad subprocess redesign, and test pruning wait for
  release-only/node-level profiling. The 389/146 inventory is a selection prompt,
  not a performance verdict.
- Broad read-only quality, full pytest, mutation coverage, and matched after
  samples run at the bundle/final verification lock.

## Advisory

- structural review result — artifact: `charness-artifacts/debug/2026-07-11-issue-433-release-closeout-carrier.md`; capability needed is producer-to-final-consumer
  acceptance before expensive work; current centers are the issue validator and
  commit-msg gate, and the strengthened next center is release preflight/resume.
  Sequencing applies because validation now unlocks quality/mutation safely.
  Recommended #433 posture is existing-gate-reuse, sibling audit is
  describe-first/advisory, and timing thresholds are no-gate.
- prose review result — artifact: `skills/public/release/references/publication-boundary.md`; release renders/transports; issue owns ledger semantics;
  commit-msg is the final consumer. The public publication-boundary reference
  now teaches carrier/classification inputs, exact-number matching, and resume
  `HEAD` proof.
- fixture-economics inventory — command: `inventory_standing_test_economics.py --summary`; 389 test files, 146 standing nested-CLI files,
  one all-release-only nested-CLI file, 13 mixed files, and 174,481,045 bytes of
  pytest temp footprint. These fields identify profiling targets but do not
  measure coverage value.
- runtime interpretation — command: `render_runtime_summary.py --json` plus three matched `run_standing_pytest.py --mode read-only` samples; the stable three-sample baseline confirms pytest is a
  real standing cost on this profile; differences within the 0.36s observed
  spread remain inconclusive.

## Delegated Review

- Delegated Review: executed — parent-delegated high-leverage review found no
  quality blocker after the critique-driven fixes; requested fields were sent
  and application was not claimed.
- Slow-gate lenses: fixture-economics found distinct boundary value with one
  shared `bug_closeout_body` builder; parallel-critical-path ranked release-only
  seeded publishes for profiling before worker counts; duplicated-proof kept
  behavior, draft, commit-msg, and seeded publish layers because each proves a
  different consumer boundary.

## Commands Run

- Quality planner and required primers; runtime summary; standing-test economics
  summary (test counts, marker split, nested CLI buckets, temp footprint);
  standing-gate verbosity summary; structural-waste inventory.
- GitHub #433 read through the issue backend with `comments_read=true`; exact
  generated-body reproduction through `check_issue_closeout_commit_msg.evaluate`.
- Three standing pytest baseline samples; focused release/issue tests; ruff,
  py_compile, packaging validation, mirror sync, debug artifact validation,
  reviewer boundary snapshots/verifications, and standalone code critique.
- Composed debug scaffold/planner, quality resolver, critique packet, and retro
  packet roundtrips; whole-corpus critique/retro/debug validators; packet-kind
  escape tests; same-day record-collision and executable-refresh tests.

## Recommended Next Quality Moves

- passive sibling interface monitoring because the reproduced current-pointer and packet/session mismatches are fixed and remaining matches are preconditions/contracts rather than confirmed defects; capability_needed=prevent producer/carrier/consumer drift; next_center=deferred until a new composed roundtrip fails; transformation=none; proof_boundary=95-test composed suite plus whole-corpus validators; enforcement_posture=describe-first.
- active release test profile — capability_needed=reduce standing feedback time without losing delivery-boundary proof; next_center=release-only seeded publish and nested process hotspots; transformation=profile node/file durations then move repeated mechanical setup or contract proof below subprocess boundaries; proof_boundary=three matched standing samples and focused behavior parity; enforcement_posture=no-gate.
- passive worker-count or selector tuning until profiling identifies a dominant repeated family because file/process counts alone cannot distinguish valuable isolation from startup waste; capability_needed=faster safe selection; next_center=deferred; transformation=none yet; proof_boundary=missing profile; enforcement_posture=no-gate.

## History

- [Prior pytest value audit](history/2026-07-03-pytest-suite-test-value-audit.md)
