# Impl debug route and waste classes critique

Date: 2026-09-04

## Decision Under Review

Two prompt-affecting additions to `skills/public/impl/SKILL.md`: a debug entry
rule in `## Verify` (the same failure returning after a fix aimed at it, or a
result contradicting the contract, is routed on whether a falsifiable cause can
be stated; if not, `impl` stops patching and enters `debug`), and a six-signal
waste scan in `## Change` with a defined seam and a follow-up stopping rule.
`debug/SKILL.md` is unchanged: its Pattern Ladder already owns "pattern of
patterns". The README rewrite in the same release is a truth-surface change
reviewed separately by a bounded read-only reviewer.

## Verification Scope Decision

- Claim under test: an agent reading `impl` once will route a repeated
  unexplained failure to `debug` instead of a second guess, and will read its
  diff against the six signals before closing, without the rule firing on
  ordinary compile/test loops.
- Changed surfaces: `skills/public/impl/SKILL.md`; final consumers are the
  installed `impl` skill in Claude Code and Codex and the generated
  `plugins/charness` mirror.
- Minimum sufficient proof: `validate_skill_ergonomics.py`,
  `check_skill_surface_preflight.py --changed-skill-md` (core headroom 65/160,
  not regressed), `check-docs.sh`, and three file-backed fresh-eye reviews.
- Deliberately omitted checks: no behavioral evaluator; per
  `docs/public-skill-validation.md` a prompt-affecting diff alone does not
  justify one, and the scenario review is the three reviews recorded here.
- Verifier contract: `scripts/review/validate_critique_artifacts.py`,
  unchanged in this slice.
- Failure classification: none
- Negative control: none with rationale: the reviewers' `block` verdicts on the first draft are the evidence that the review channel discriminates; no refusal path is claimed.
- Subject identity: sha256:cb076af724e11db86e573c174976f715268c207358b86cf966ebedc93ecace0c
- Verifier identity: sha256:fdae081f53f503cfc7eb37bd0790ab07ad0ee04855e2af9f0bf6d47f11c5ae08
- Input identity: sha256:c173dd153b9b410283a5c2d6afc77790f656da74bb292fce9fd92420431ed2ee
- Failure identity: stable:none
- Evidence identity: none
- Retry disposition: first-attempt
- Retry key: sha256:688d992c299b9635b91f89a82f991c5ebd7d04fdcc5c319ec52165a507db64f7

## Failure Angles

- Trigger noise: a debug route that fires on every unpredicted command result
  becomes background text the reader learns to ignore, and debug's bootstrap
  (adapter, planner, scaffold, validator) is disproportionate for a reversible
  contract correction (north star P1).
- Recall: one long bullet with seven packed concerns and no retrieval cue is
  not read at the moment it matters (P2), and a self-justifying clause in the
  body argues against P3 inside the contract it is meant to serve.
- Ownership: the waste scan could duplicate `quality` or the north star's
  purpose section, and "fix the class" could widen every slice against
  "smallest coherent change".
- Loophole: a seam defined for code only leaves config, test, and artifact
  slices with no seam and no stopping rule.

## Counterweight Pass

- Real blockers, fixed before ship: the trigger width and the missing
  observable (now: same failure after a fix aimed at it, or a contradicted
  contract claim; test is a cause that predicts a disproving observation; a
  narrower new failure is excluded); the paragraph shape (now one-line
  principle, six-item sub-list, seam, stopping rule); the code-only seam (now
  every edited surface with consumers, readers, and generated derivatives).
- Bundled: "classes" became "signals; they overlap, and every match is
  repaired"; the self-justifying clause was removed from the body.
- Over-worry: "the enumeration duplicates quality and reverses P3". Quality is
  an on-demand inspection; impl is the moment of change. The operator's
  observed evidence is that the principle alone did not produce recall, which
  is the P3 exception the north star names. Recorded, not folded.
- Valid but deferred: debug has no narrow fast path that skips its bootstrap
  for a small reversible incident. That is a `debug` change, not this slice.

## Structured Findings

- F1 | bin: act-before-ship | evidence: strong | ref: skills/public/impl/SKILL.md#Verify | action: fix | note: trigger fired on any unpredicted result and did not separate a recurring unexplained failure from a narrowed new one; repaired with the falsifiable-cause test and the narrower-failure exclusion (reviewers 1 and 2; reviewer 3 confirms resolved).
- F2 | bin: act-before-ship | evidence: strong | ref: skills/public/impl/SKILL.md#Change | action: fix | note: seven concerns in one bullet with no retrieval cue and a clause arguing against north-star P3 in the body; repaired to a principle plus six-item sub-list (reviewers 1 and 2; reviewer 3 confirms resolved).
- F3 | bin: bundle-anyway | evidence: strong | ref: skills/public/impl/SKILL.md#Change | action: fix | note: "what the slice touches" undefined, then defined for code only while impl also edits config, tests, and artifacts; repaired to every edited surface with its consumers, readers, and generated derivatives (reviewer 1; reviewer 3 narrowed it; fixed after).
- F4 | bin: bundle-anyway | evidence: moderate | ref: skills/public/impl/SKILL.md#Change | action: fix | note: the six entries overlap while the text called them classes; now named as overlapping signals with every match repaired (reviewer 3).
- F5 | bin: bundle-anyway | evidence: moderate | ref: skills/public/impl/SKILL.md#Verify | action: fix | note: "falsifiable" needed its observable; now "one that predicts an observation able to disprove it" (reviewer 3).
- F6 | bin: over-worry | evidence: contested | ref: skills/public/quality/SKILL.md | action: document | note: the waste scan duplicates quality and reverses P3; quality inspects on demand while impl is the moment of change, and the operator's observed non-recall is the P3 exception. Recorded here, not folded (reviewer 1).
- F7 | bin: valid-but-defer | evidence: moderate | ref: skills/public/debug/SKILL.md#Bootstrap | action: defer | note: debug offers no narrow fast path around its bootstrap for a small reversible incident; a debug-skill slice, outside this change (reviewer 1).

## Reviewer Tier Evidence

- Requested tier: n/a (run_review.py default; adapter `reviewer_runner` is `file-backed-worker`, backend `codex_exec`, boundary `read-only-worker`).
- Requested spawn fields: file-backed Codex worker through `run_review.py`; no host subagent spawn.
- Host exposure state: host-defaulted
- Application state: unverified-by-packet; the packet records the request, not the model the host chose.
- Delivery state: findings-received
- Execution mode: file-backed-worker
- Worker report: .charness/reviewer-round-impl-debug-route-final-1/worker-report.yaml
- Earlier rounds: `.charness/reviewer-round-impl-debug-route-weinberg-1/`, `-raskin-2/`, `-repair-verify-1/` (run state, not tracked).
- Worker report identity: 2c5bcb8e647bf00259494b1306893d1202c90e713cda2c21bb52753778375818
- Worker report approval: approval_eligible: true
- Worker report delivery: findings-received
- Worker report packet identity: b3d8083fb9433fd5c41f02a127335ebec28db0837367e2dba9efe9687bc62bc1
- Worker report input identity: c173dd153b9b410283a5c2d6afc77790f656da74bb292fce9fd92420431ed2ee
- Worker report parent receipt identity: parent-7e5ed93e44da821706046c28b2c0dec8bb471e9972a21e79
- Worker report findings identity: 7f3e5f4c16dc19b510e14b9e4c69c92c29f7cec6e905d63aa0f386422227fd7b

## Fresh-Eye Satisfaction

worker-delivered; four file-backed Codex workers ran through `run_review.py`. Reviewers 1 and 2 (Weinberg/Ousterhout ownership, Raskin first-reader) delivered `block` on the first draft; reviewer 3 (repair verification) delivered `block` with three wording gaps; reviewer 4 (final bytes) delivered `pass`, `approval_eligible: true`, on the exact subject identity above. No same-context substitute was used.

## Reviewed Input Identity

- Packet consumed: charness-artifacts/critique/impl-debug-route-final-1-packet.json
- Packet path: charness-artifacts/critique/impl-debug-route-final-1-packet.json
- Packet SHA256: b3d8083fb9433fd5c41f02a127335ebec28db0837367e2dba9efe9687bc62bc1
- Identity SHA256: c173dd153b9b410283a5c2d6afc77790f656da74bb292fce9fd92420431ed2ee
- Reviewer 3 packet: charness-artifacts/critique/impl-debug-route-repair-verify-1-packet.json, SHA256 659fc911267111bf17bfa4cc6da76354efa6bc56e597cadf990a08d15283450e, identity 7ae92ecbdae1723ebff33dcfba92f5db4fb8cecb847fe20b8fd4efa827e558df, verdict block, three wording gaps.
- Reviewer 1 packet: charness-artifacts/critique/impl-debug-route-weinberg-1-packet.json, SHA256 4bca88c074ec041de97af5b0acf73faaae98066757e87181720f1935996b45a7, identity 028c40b32436808e24e97b113cd46c73fa5d36b08fdc07b26b2bded0c5844b72, verdict block, three findings.
- Reviewer 2 packet: charness-artifacts/critique/impl-debug-route-raskin-2-packet.json, SHA256 04d6fc96016090314c1886068333c396b06043554d7dc14525c9d494448d7eee, identity 15b1eb5dd241267cb72388feee43ab09a3ce06dcb722157409d8420a70114759, verdict block, three findings.
- Reviewer 4 read the final tree; the subject identity above is that tree.

## Boundary Ownership

- Producer: `skills/public/impl/SKILL.md` states the debug entry rule and the waste signals.
- Consumer: the agent executing an implementation slice; `debug` receives the handoff and already hands back to `impl`.
- Owning surface: public skill `impl` (repair discipline itself stays owned by `debug`).
- Verdict: owned-correctly
