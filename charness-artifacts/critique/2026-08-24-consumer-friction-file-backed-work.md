# Consumer Friction And File-Backed Work Decision Critique

Date: 2026-08-24

## Decision Under Review

Whether to retire every currently evidenced consumer-friction issue while making
Ceal's file-backed external-worker pattern portable through Charness, without
copying Ceal scripts or introducing a duplicate lifecycle/configuration owner.

- Target premortem: six months after shipping, unrelated issue closeout waits on a
  broad lane platform, a second task store drifts from `.charness/tasks`, and the
  candidate reviewer approves its own broken verdict path.
- Decision: proceed to spec only with two independent contracts, `charness task` as
  the sole durable owner, one host process/configuration boundary, and an independent
  proof channel.
- Klein reference: n/a; the concrete Ceal episodes and current repository owners were
  stronger evidence than a named expert simulation.

## Failure Angles

- Problem framing: the original selected cohort was not auditable against all 46 open
  issues, and it made a heterogeneous issue program appear causally unified.
- Operator first use: a command name without durable launch/status/collect/cancel/
  retry behavior would not survive parent loss, timeout, or repeated collection.
- Implementation integrity: a new lane store would duplicate `charness task`; a new
  runner could become a third argv/env/auth normalizer; candidate dogfood could create
  a circular approval claim.

## Counterweight Pass

- Act before spec: full 46-row accounting, independent program closeout, existing
  task ownership, one process/config owner, lifecycle recovery, reproduction-gated
  path repair, and independent proof-surface review.
- Bundle in the first read-only slice: deterministic backend/authority precedence,
  timeout recovery, installed clean-room proof, and executable input-drift checks.
- Valid defer: tracked opt-in `AGENTS.local.md` composition and write-worktree recovery.
- Over-worry: one angle reviewer hashed the Markdown packet rendering even though the
  assigned identity belonged to the canonical JSON packet. The counterweight verified
  the JSON identity and retained that review's independently valid semantic concerns.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/ideation/2026-08-24-open-issue-consumer-friction-matrix.md | action: fix | note: fixed by accounting for all 46 open rows as 13 include, 1 dependency, and 32 exclude with non-close semantics
- F2 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md | action: fix | note: fixed by giving issue retirement and external-worker capability independent terminal criteria and causal-edge-only dependencies
- F3 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md | action: fix | note: fixed by selecting `charness task` as the sole durable lifecycle owner and defining the minimum recoverable attempt journey
- F4 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md | action: fix | note: fixed by selecting one Python executable argv/env/auth boundary and assigning tracked adapter, ignored capability, runtime grant, invocation, and receipt fields
- F5 | bin: act-before-ship | evidence: strong | ref: charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md | action: fix | note: fixed by reproduction-gating the path hypothesis and reserving a pre-existing independent channel plus the conditional second round for verdict-logic repairs
- F6 | bin: over-worry | evidence: strong | ref: charness-artifacts/critique/workers/2026-08-24-counterweight-result.json | action: document | note: the packet mismatch concern hashed the Markdown rendering instead of the canonical JSON packet and was not carried forward
- F7 | bin: valid-but-defer | evidence: strong | ref: charness-artifacts/ideation/2026-08-24-consumer-friction-and-file-backed-lanes.md | action: defer | note: local-instruction composition and write-capable recovery remain outside the first read-only slice with explicit later proof obligations

## Reviewer Tier Evidence

- Requested tier: high-leverage from the critique adapter; the current file-backed
  runner does not apply or report its model/effort fields.
- Requested spawn fields: n/a; this was a file-backed `codex_exec` worker, not a host
  spawn surface.
- Host exposure state: unsupported
- Application state: n/a; backend `codex_exec` and adapter timeout were applied, but
  the runner exposed no tier application signal.
- Delivery state: findings-received
- Worker report: charness-artifacts/critique/workers/2026-08-24-post-repair-report.yaml
- Worker report identity: a0aca15b718449ad6836cc2b7abc0ea8b9db926f0f4e003bf271ae2dd313bc15
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: 731472bb457cc52a489ba253ab7ce72a6f66ba7bd633c9ee058d562a7eadfc13
- Worker report input identity: 66d881bff7fa784f9a76610e7c382bce37e82054275f58e2b2c98667a9ddceb6
- Worker report parent receipt identity: 2026-08-24-consumer-friction-parent
- Worker report findings identity: 5c43379b161fc43461e576415e13f3c95142118111df1358261edd028e6c8b34

## Fresh-Eye Satisfaction

worker-delivered. The final serial worker returned `pass` with no findings, and the
combined report is approval-eligible. Boundary verification found no unexplained
drift; only the declared ledger/result/receipt/report/stdout/stderr files were
parent-attributed. Earlier parallel angle reviews are concern sources, not approval
carriers, because their expected artifact writes appeared in each other's shared-tree
windows.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.json
- Packet path: charness-artifacts/critique/2026-08-24-consumer-friction-post-repair-packet.json
- Packet SHA256: 731472bb457cc52a489ba253ab7ce72a6f66ba7bd633c9ee058d562a7eadfc13
- Identity SHA256: 66d881bff7fa784f9a76610e7c382bce37e82054275f58e2b2c98667a9ddceb6

## Boundary Ownership

- Producer: the issue inventory produces routing facts; the host process boundary
  produces execution facts; task-specific validators produce semantic verdicts.
- Consumer: the issue-retirement ledger, external-worker spec, parent integration,
  and eventual GitHub closeout.
- Owning surface: the complete issue matrix for cohort truth, `.charness/tasks` for
  durable lifecycle, one CLI-backed process adapter for argv/env/auth, and bounded
  review reports for approval.
- Verdict: moved-to-owner
