# Issue 539 Create URL Shape Resolution Critique
Date: 2026-08-13

## Decision Under Review

Keep parsed issue numbers from alternate create backends, while exposing URL
identity only when its shape is a valid complete HTTP(S) URL.

## Failure Angles

- A bare number or diagnostic text can be wrongly reported as a URL.
- A malformed URL must not crash after the issue was already created.
- A URL fallback must preserve skipped-readback honesty and avoid host guessing.

## Counterweight Pass

- Normal readback requests structured `body,url`, so a missing create URL can
  be recovered without synthesizing one from repo and number.
- R1 tightened host/space controls. R2 found malformed bracket hosts, invalid
  ports, and backslash authority input; all now become null. This R2 repair is
  accepted-unreviewed under the two-round cap.
- URL-to-number identity matching and URL conventions remain out of scope.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: issue_create.py | action: fix | note: raw stdout no longer fills canonical URL fields.
- F2 | bin: act-before-ship | evidence: strong | ref: tests/quality_gates/test_issue_create.py | action: fix | note: malformed hosts, ports, whitespace, and backslashes become null.
- F3 | bin: over-worry | evidence: moderate | ref: issue_create.py | action: defer | note: URL host and issue number need not be revalidated as one identity in this shape-only fix.

## Reviewer Tier Evidence

- Requested tier: bounded fresh-eye reviewer.
- Requested spawn fields: read-only one-shot task with inherited model and effort.
- Host exposure state: metadata-hidden
- Application state: R1 and R2 reviewer tasks returned findings; boundary fingerprints showed no reviewer drift.
- Delivery state: findings-received

## Fresh-Eye Satisfaction

parent-delegated; R1 and R2 completed. R2 malformed URL repairs are
accepted-unreviewed under the verdict-logic two-round cap.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/2026-08-12-163952-packet.md
- Packet path: charness-artifacts/critique/2026-08-12-163952-packet.json
- Packet SHA256: 9e72a3e5bbf905287537b0b8c891e6f403d65940bfb764782a3ea0e1c8a122ed
- Identity SHA256: 19453fdc06356f8db06940bb1017b6d82eea305365c20671e59693860cfdc912

## Boundary Ownership

- Producer: issue-create backend output and structured readback.
- Consumer: create closeout payload readers.
- Owning surface: issue create identity shaping.
- Verdict: owned-correctly
