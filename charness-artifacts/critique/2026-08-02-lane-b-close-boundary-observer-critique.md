# Lane B — the close boundary reads who reviewed the resolution
Date: 2026-08-02

## Decision Under Review

Make the issue-close resolution-critique floor read the cited artifact's own
`Fresh-eye satisfaction:` value, and refuse a record that positively states no
distinct observer read the resolution — gated on an adopted repo delegation
contract and on the artifact predating the typed contract, with
`blocked <host-signal>` kept as a passing degradation valve.

Two bounded rounds, because this changes verdict logic on a proof surface. Both
rounds are recorded here, in one artifact per slice.

## Failure Angles

- The refusal is inert: its activation condition is never itself tested.
- The refusal is defeatable: a spelling of the field the reader does not know, or
  an escape hatch cheaper than telling the truth.
- The refusal over-blocks: honest historical records refused by a rule that did
  not exist when they were written.
- The rationale for what does NOT refuse rests on a floor that never runs in time.
- Portability: a consuming repo held to a convention it never adopted.

## Counterweight Pass

- The strongest argument against blocking at all: the field is a SELF-REPORT, and
  this repo already learned that a caller-supplied self-report earns an advisory
  rather than teeth, because the agent that would lie in the field is the one that
  writes it. A blocking floor over a self-report cannot stop a dishonest closer;
  it stops the honest one who wrote plain English.
- That argument is decisive UNTIL the cheap escapes are closed. With a bare
  `blocked` accepted and a bolded key unreadable, the blocking arm had strictly
  negative expected value — all cost on honest authors, none on the failure mode.
  It becomes defensible only with the signal floor, the markup-tolerant reader,
  the contract gate and the date grandfather all in place, which is why all four
  shipped together.
- The #467 motivation did NOT survive: reading this field would not have
  prevented that closure. The hole is real independently; the worked example is
  synthetic and is now labelled as such.

## Structured Findings

Round 1 (five blockers, all parent-verified before folding):

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_critique_observer.py:296 | action: fix | note: the refusal was INERT in this repo. The contract marker substring-tested an unbolded literal against an AGENTS.md that writes `**already delegated**`; measured False. Markup is now flattened before matching, and a test pins the contract LIVE against the real checked-in file — the one test whose deletion restores the whole defect.
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_critique_observer.py:103-115 | action: fix | note: the reader missed the corpus's bold-bullet form (`- **Fresh-Eye Satisfaction**:`, nine checked-in artifacts), so a delegated artifact read as absent AND bolding the key was a two-asterisk bypass. Reading now splits on the first colon and normalizes the key.
- F3 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_critique_observer.py:229-233 | action: fix | note: `blocked` was a magic word with no substance floor; the seven-character value passed. Now `blocked-unsubstantiated` and refused, with the minimum read live from the sibling valve's own floor.
- F4 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_resolution_critique.py:219 | action: fix | note: the rationale for letting `absent` pass was false — `validate_critique_artifacts.py` runs at the COMMIT boundary and `close-with-comment` performs no commit, so "delete the line" was a live bypass guarded by a floor on the wrong side of the boundary. `absent` now refuses under the contract.
- F5 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_critique_observer.py:198-201 | action: fix | note: prefix matching would have refused ten checked-in artifacts recording `satisfied — parent-delegated bounded review returned ...`. Delegated tokens are now matched by containment.

Round 2, reading the repairs (two blockers, both INTRODUCED by round 1's folds):

- F6 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_critique_observer.py:222-234 | action: fix | note: containment was evaluated BEFORE the `blocked` test, so the valve's most natural phrasing — naming the spawn that failed — classified as a completed delegation, dropping its advisory and making the new signal floor bypassable in 24 characters, cheaper than the bare word F3 had just closed. `blocked` is now tested first, pinned by a test.
- F7 | bin: act-before-ship | evidence: strong | ref: skills/public/issue/scripts/issue_critique_observer.py:136-152 | action: fix | note: the section branch read only the first non-empty line, still refusing six checked-in artifacts that open the section with a prose verdict. The whole section body is now scanned; artifacts with no typed token at all are handled by the date grandfather instead.

Folding F6 introduced a THIRD over-block, caught by re-measuring the corpus rather
than by a further round: value-wide negation markers demoted eleven honest
post-cutoff artifacts on the words "no blockers". Narrowed to a negation window
immediately before the token, and re-measured to 0 refused.

- F8 | bin: bundle-anyway | evidence: moderate | ref: skills/public/issue/scripts/issue_resolution_critique.py:151-158 | action: fix | note: a non-UTF-8 cited artifact would traceback out of the close command instead of producing the `unreadable` disposition designed for it, because the binding library reads the same file with errors ignored. Now `errors="replace"`.
- F9 | bin: bundle-anyway | evidence: moderate | ref: skills/public/issue/scripts/issue_markdown_lib.py:8 | action: fix | note: `~~~` was an unhandled CommonMark fence, so a quoted example inside one was read as real content by every caller of the shared stripper.
- F10 | bin: valid-but-defer | evidence: moderate | ref: scripts/validate_critique_artifacts.py:167-172 | action: file-issue | follow-up: https://github.com/corca-ai/charness/issues/471 | note: the repo-side `has_repo_delegation_contract` carries the same F1 defect and is still inert here. Not fixed in lane: repairing it makes a dormant authoring gate live across 400+ checked-in artifacts and needs its own before/after measurement.
- F11 | bin: over-worry | evidence: weak | ref: skills/public/issue/scripts/issue_resolution_critique.py:229-259 | action: defer | note: round 2 flagged the `_refusal_reason` else-branch as a latent wrong-branch trap for a future disposition. Recorded as accepted-unreviewed under the two-round cap; the subsequent dup-ratchet refactor collapsed the branch chain into a data table, which incidentally narrows it.

## Reviewer Tier Evidence

- Requested tier: `bounded-reviewer` (this repo's typed read-only reviewer agent), twice.
- Requested spawn fields: `subagent_type: bounded-reviewer`, `run_in_background: false`, no host addressing/team `name` (an addressed spawn routes onto a teammate protocol whose retrieval tool is not exposed here). No model/effort override: on a Claude Code host the per-host contract uses session-model inheritance.
- Host exposure state: host-defaulted
- Application state: host-confirmed: both spawns returned findings inline in this session, and each reviewer reported its own envelope as Read/Grep/Glob only.
- Delivery state: findings-received

Parent-side boundary integrity: `.charness/reviewer-boundary/lane-b-round1.json`
and `lane-b-round2.json`. Both verified `parent-attributed` with empty drift AFTER
declaring the parent's own repair paths — recorded honestly rather than as
`clean`, because both verifies ran after the parent had begun folding findings, so
each rests on parent testimony about which paths moved rather than on a no-write
window. The ordering rule that prevents this is now in
`docs/conventions/operating-contract.md`.

## Fresh-Eye Satisfaction

parent-delegated

## Reviewed Input Identity

<!-- No prepare_packet.py packet was consumed; each round received an inline slice packet naming intent, changed files, the refusal decision and its defence, proof runs, non-claims, and eight/nine questions. Round 2's packet additionally named all five round-1 blockers and the fold applied to each. The binding floor is therefore off by design, and this critique does not claim packet-bound identity. -->

## Boundary Ownership

- Producer: `skills/public/issue/scripts/issue_critique_observer.py` (the disposition) and `issue_resolution_critique.py` (the refusal and the report).
- Consumer: `issue_close.py` / `issue_close_comment_floor.py` at the GitHub write boundary, `issue_verify_closeout.py`, `scripts/check_issue_closeout_commit_msg.py`, and the operator reading either.
- Owning surface: the issue skill owns the close-boundary floor; the achieve coordination reference owns the ordering rule; the tests own the proof, including the corpus measurement.
- Verdict: single-surface
