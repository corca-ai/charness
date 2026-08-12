# Issue 607 Subprocess Settlement Inventory Resolution Critique

Date: 2026-08-13

## Decision Under Review

Extend the existing standing-test economics detail payload with conservative,
callsite-attributed static settlement signals without claiming runtime child
lifecycle or process-tree behavior.

## Failure Angles

- Synchronous calls without a deadline can block forever and must not imply a
  finite lifecycle.
- Captured output on either stream can grow without bound even when the other
  stream is discarded.
- Dynamic timeout expressions, aliases, and JS formatting can exceed what this
  narrow static scan can prove.

## Counterweight Pass

- R1 found two false-green classifications: timeout-free synchronous calls were
  marked `finite`, and mixed `DEVNULL` plus `PIPE` output was marked `bounded`.
  The repair makes both `unknown` or `unbounded` as appropriate and documents
  that direct static fields are syntax-only.
- R2 found the same lifecycle class through dynamic timeout expressions. The
  accepted-unreviewed final repair emits `present` and `finite` only for literal
  numeric deadlines; dynamic expressions become `unknown`, in Python and JS.
- Process-tree termination remains `unknown`; runtime ownership and a full JS
  data-flow parser are deliberately deferred.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: R1 fresh-eye and counterweight | action: fix | note: no-timeout synchronous calls are not finite.
- F2 | bin: act-before-ship | evidence: strong | ref: R1 fresh-eye and counterweight | action: fix | note: any captured Python stream prevents a bounded-output claim.
- F3 | bin: act-before-ship | evidence: strong | ref: R2 fresh-eye | action: fix | note: only literal numeric deadlines can yield a finite static lifecycle; this second-round repair is accepted-unreviewed under the two-round cap.
- F4 | bin: bundle-anyway | evidence: moderate | ref: R1 compatibility review | action: document | note: summary now directs callsite attribution readers to `--detail`.
- F5 | bin: valid-but-defer | evidence: strong | ref: R1/R2 | action: defer | note: tree ownership, alias/data-flow analysis, and multiline JS options require a separate runtime/parser contract.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: read-only one-shot task with inherited model and effort.
- Host exposure state: metadata-hidden
- Application state: R1 repair was read by R2; R2 repair is recorded as accepted-unreviewed under the two-round cap.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; R1, separate counterweight, and R2 completed.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-175707-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-175707-packet.json
- Packet SHA256: 32e68e08ab130cf627917f5dedb2366a588844d93f932c1cef13e7dcc2074772
- Identity SHA256: a86020bf00e93d6df4f802df3a8ef235f9dd45474e87ef21184f309c888ce928
- Earlier R1 packet: charness-artifacts/critique/2026-08-12-174749-packet.json (SHA256 5d88329f7da97019b5b5bab1e218cf93b316215e569ae3a0bff2ce07a2fdc0e4; identity 7654a2e029e9f56f6533ca286754373b12b595a87181eaace963d9fe0b99c60f).

## Boundary Ownership

- Producer: `surface_marker_lib.py` static callsite scanner.
- Consumer: `inventory_standing_test_economics.py --detail` reader reviewing
  attributed subprocess seams.
- Owning surface: standing-test economics advisory inventory.
- Verdict: owned-correctly.
